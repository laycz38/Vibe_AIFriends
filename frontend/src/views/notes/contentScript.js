// Content script injected into the NLP iframe.
// Handles: text selection detection, image click detection, highlight rendering, tooltips.
// Communicates with parent via postMessage.

export const CONTENT_SCRIPT = `
(function() {
  'use strict';

  // --- Collect text nodes from the main content area ---
  function getTextNodes() {
    var root = document.querySelector('article, main, .md-content, [role="main"]') || document.body;
    var walker = document.createTreeWalker(
      root,
      NodeFilter.SHOW_TEXT,
      { acceptNode: function(n) {
        var tag = (n.parentNode.nodeName || '').toLowerCase();
        if (tag === 'script' || tag === 'style' || tag === 'noscript') return NodeFilter.FILTER_REJECT;
        return n.textContent.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
      }}
    );
    var nodes = [];
    var node;
    while (node = walker.nextNode()) { nodes.push(node); }
    return nodes;
  }

  function getFullText() {
    return getTextNodes().map(function(n) { return n.textContent; }).join('');
  }

  // --- Tooltip ---
  var tooltip = null;
  function ensureTooltip() {
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.className = 'aifriends-tooltip';
      tooltip.style.cssText = 'position:fixed;z-index:99999;max-width:320px;padding:8px 12px;background:#1d232a;color:#e2e8f0;border-radius:8px;font-size:13px;line-height:1.5;pointer-events:none;opacity:0;transition:opacity 0.15s;box-shadow:0 4px 12px rgba(0,0,0,0.3);word-break:break-word;';
      document.body.appendChild(tooltip);
    }
    return tooltip;
  }

  function showTooltip(e, content) {
    if (!content) return;
    var tip = ensureTooltip();
    tip.textContent = content;
    tip.style.left = Math.min(e.clientX + 12, window.innerWidth - 340) + 'px';
    tip.style.top = Math.max(e.clientY - 40, 8) + 'px';
    tip.style.opacity = '1';
  }

  function hideTooltip() {
    if (tooltip) tooltip.style.opacity = '0';
  }

  // --- Inline image action bar (appears below clicked image) ---
  var imageActionBar = null;
  var imageActionTarget = null;

  function showImageActionBar(img) {
    hideImageActionBar();
    var bar = document.createElement('div');
    bar.className = 'aifriends-img-action';
    bar.style.cssText =
      'position:absolute;z-index:9999;' +
      'display:flex;align-items:center;gap:6px;' +
      'padding:5px 10px;' +
      'background:#1d232a;color:#e2e8f0;' +
      'border-radius:8px;font-size:12px;' +
      'box-shadow:0 4px 16px rgba(0,0,0,0.35);' +
      'white-space:nowrap;' +
      'animation:aifriends-fadein 0.15s ease-out;';

    var label = document.createElement('span');
    label.textContent = '为此图片添加批注？';

    var yesBtn = document.createElement('button');
    yesBtn.textContent = '添加';
    yesBtn.style.cssText = 'background:#6366f1;color:#fff;border:0;border-radius:5px;padding:3px 10px;cursor:pointer;font-size:12px;font-weight:500;';

    var noBtn = document.createElement('button');
    noBtn.textContent = '✕';
    noBtn.style.cssText = 'background:transparent;color:#94a3b8;border:0;cursor:pointer;font-size:14px;padding:2px 4px;line-height:1;';

    yesBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      hideImageActionBar();
      window.parent.postMessage({ type: 'image-clicked', src: img.src, alt: img.alt || '' }, '*');
    });

    noBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      hideImageActionBar();
    });

    bar.appendChild(label);
    bar.appendChild(yesBtn);
    bar.appendChild(noBtn);
    document.body.appendChild(bar);

    // Position below the image
    var rect = img.getBoundingClientRect();
    var left = Math.min(Math.max(rect.left + window.scrollX, 8), window.innerWidth - 240);
    var top = rect.bottom + window.scrollY + 4;
    // If would go off-screen, show above the image instead
    if (rect.bottom + 40 > window.innerHeight) {
      top = rect.top + window.scrollY - 36;
    }
    bar.style.left = left + 'px';
    bar.style.top = top + 'px';

    imageActionBar = bar;
    imageActionTarget = img;
  }

  function hideImageActionBar() {
    if (imageActionBar) {
      imageActionBar.remove();
      imageActionBar = null;
      imageActionTarget = null;
    }
  }

  // --- Remove existing highlights + image labels ---
  function removeHighlights() {
    document.querySelectorAll('.aifriends-anno').forEach(function(el) {
      var p = el.parentNode;
      if (p) { p.replaceChild(document.createTextNode(el.textContent), el); p.normalize(); }
    });
    document.querySelectorAll('.aifriends-img-label').forEach(function(el) { el.remove(); });
  }

  // --- Color map ---
  function annoStyle(c) {
    var bg, fg;
    switch (c) {
      case 'green':  bg = '#bbf7d0'; fg = '#14532d'; break;
      case 'blue':   bg = '#bfdbfe'; fg = '#1e3a5f'; break;
      case 'pink':   bg = '#fecdd3'; fg = '#881337'; break;
      case 'yellow': bg = '#fef08a'; fg = '#713f12'; break;
      default:       bg = '#fecaca'; fg = '#7f1d1d'; break;
    }
    return { bg: bg, fg: fg };
  }

  // --- Render text annotations as highlights ---
  function renderAnnotations(annotations) {
    removeHighlights();
    if (!annotations || !annotations.length) return;

    var textNodes = getTextNodes();
    if (!textNodes.length) return;

    var fullText = textNodes.map(function(n) { return n.textContent; }).join('');

    annotations.forEach(function(ann) {
      if (ann.annotation_type === 'image') {
        renderImageLabel(ann);
        return;
      }

      // Try exact match with context first, then fall back to selected_text only
      var search = (ann.context_before || '') + ann.selected_text + (ann.context_after || '');
      var idx = fullText.indexOf(search);
      var selStart, selEnd;

      if (idx >= 0) {
        selStart = idx + (ann.context_before || '').length;
        selEnd = selStart + ann.selected_text.length;
      } else {
        idx = fullText.indexOf(ann.selected_text);
        if (idx < 0) return;
        selStart = idx;
        selEnd = idx + ann.selected_text.length;
      }

      var off = 0;
      var nodeInfos = textNodes.map(function(n) {
        var len = n.textContent.length;
        var info = { node: n, start: off, len: len };
        off += len;
        return info;
      });

      var foundNode = false;
      nodeInfos.forEach(function(info) {
        if (!info.node || !info.node.parentNode) return;
        var ns = info.start, ne = ns + info.len;
        if (ne <= selStart || ns >= selEnd) return;

        var cutStart = Math.max(0, selStart - ns);
        var cutEnd = Math.min(info.len, selEnd - ns);
        if (cutStart >= cutEnd) return;

        var txt = info.node.textContent;
        var before = txt.slice(0, cutStart);
        var match = txt.slice(cutStart, cutEnd);
        var after = txt.slice(cutEnd);

        var style = annoStyle(ann.color);
        var mark = document.createElement('mark');
        mark.className = 'aifriends-anno';
        mark.dataset.id = ann.id;
        mark.textContent = match;
        mark.style.cssText =
          'background:' + style.bg + ' !important;' +
          'color:' + style.fg + ' !important;' +
          'cursor:pointer;' +
          'border-radius:3px;' +
          'padding:1px 2px;' +
          'font-weight:500;';

        mark.addEventListener('mouseenter', function(e) { showTooltip(e, ann.content); });
        mark.addEventListener('mouseleave', hideTooltip);
        mark.addEventListener('click', function(e) {
          e.stopPropagation();
          e.preventDefault();
          window.parent.postMessage({ type: 'annotation-click', id: ann.id }, '*');
        });

        var frag = document.createDocumentFragment();
        if (before) frag.appendChild(document.createTextNode(before));
        frag.appendChild(mark);
        if (after) frag.appendChild(document.createTextNode(after));
        info.node.parentNode.replaceChild(frag, info.node);
        info.node = null;
        foundNode = true;
      });
    });
  }

  // --- Render image annotation label (below the image) ---
  function renderImageLabel(ann) {
    var imgs = document.querySelectorAll('img[src="' + ann.selected_text + '"]');
    if (!imgs.length) {
      var basename = ann.selected_text.split('/').pop();
      imgs = document.querySelectorAll('img[src$="' + basename + '"]');
    }
    var style = annoStyle(ann.color);

    imgs.forEach(function(img) {
      // Check if label already exists for this annotation
      var existing = img.parentNode.querySelector('.aifriends-img-label[data-id="' + ann.id + '"]');
      if (existing) return;

      // If the image is inside a figure, place the label after the figure
      var figure = img.closest('figure');
      var anchor = figure || img;

      var label = document.createElement('div');
      label.className = 'aifriends-img-label';
      label.dataset.id = ann.id;
      label.style.cssText =
        'display:inline-flex;align-items:center;gap:4px;' +
        'margin:4px 0 8px 0;padding:3px 12px;' +
        'background:' + style.bg + ' !important;' +
        'color:' + style.fg + ' !important;' +
        'border-radius:12px;font-size:12px;font-weight:500;' +
        'cursor:pointer;' +
        'border:1px solid ' + style.fg + '44;' +
        'width:fit-content;' +
        'transition:filter 0.15s;';

      // Use textContent with actual emoji (avoid template-literal escape issues)
      label.appendChild(document.createTextNode('📝'));
      label.appendChild(document.createTextNode(' 已批注'));

      label.addEventListener('mouseenter', function(e) { showTooltip(e, ann.content); });
      label.addEventListener('mouseleave', hideTooltip);
      label.addEventListener('click', function(e) {
        e.stopPropagation();
        e.preventDefault();
        window.parent.postMessage({ type: 'annotation-click', id: ann.id }, '*');
      });

      // Insert label right after the anchor element
      anchor.parentNode.insertBefore(label, anchor.nextSibling);
    });
  }

  // --- Inject styles ---
  function injectStyles() {
    if (document.getElementById('aifriends-styles')) return;
    var s = document.createElement('style');
    s.id = 'aifriends-styles';
    s.textContent = [
      '.aifriends-anno:hover{filter:brightness(0.82);}',
      '.aifriends-anno.active{outline:3px solid #6366f1 !important;outline-offset:2px;animation:aifriends-pulse 0.6s ease-in-out 3;}',
      '.aifriends-img-label:hover{filter:brightness(0.88);}',
      '.aifriends-img-label.active{outline:3px solid #6366f1 !important;outline-offset:2px;animation:aifriends-pulse 0.6s ease-in-out 3;}',
      '@keyframes aifriends-pulse{0%,100%{outline-color:#6366f1}50%{outline-color:#a5b4fc}}',
      '@keyframes aifriends-fadein{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}'
    ].join('');
    document.head.appendChild(s);
  }

  // --- Text selection detection ---
  function onMouseUp() {
    setTimeout(function() {
      var sel = window.getSelection();
      if (!sel || sel.isCollapsed) {
        window.parent.postMessage({ type: 'selection-cleared' }, '*');
        return;
      }
      var text = sel.toString().trim();
      if (!text || text.length < 2) return;

      var fullBody = getFullText();
      var idx = fullBody.indexOf(text);
      var ctxBefore = idx >= 0 ? fullBody.slice(Math.max(0, idx - 60), idx) : '';
      var ctxAfter = idx >= 0 ? fullBody.slice(idx + text.length, idx + text.length + 60) : '';

      window.parent.postMessage({
        type: 'text-selected',
        text: text.slice(0, 500),
        contextBefore: ctxBefore,
        contextAfter: ctxAfter,
      }, '*');
    }, 10);
  }

  // --- Image click detection (shows inline action bar, not immediate) ---
  function onImageClick(e) {
    var img = e.target.closest('img');
    if (!img) { hideImageActionBar(); return; }
    // Don't intercept clicks on our own UI
    if (e.target.closest('.aifriends-img-label') || e.target.closest('.aifriends-img-action')) return;
    e.stopPropagation();
    showImageActionBar(img);
  }

  // --- Listen for commands from parent ---
  window.addEventListener('message', function(e) {
    if (!e.data || !e.data.type) return;
    if (e.data.type === 'render-annotations') {
      injectStyles();
      renderAnnotations(e.data.annotations);
    }
    if (e.data.type === 'focus-annotation') {
      var el = document.querySelector(
        '.aifriends-anno[data-id="' + e.data.id + '"], ' +
        '.aifriends-img-label[data-id="' + e.data.id + '"]'
      );
      if (el) {
        el.classList.add('active');
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(function() { el.classList.remove('active'); }, 2500);
      }
    }
  });

  // --- Init ---
  document.addEventListener('mouseup', onMouseUp);
  document.addEventListener('click', onImageClick, true);
  injectStyles();
})();
`;

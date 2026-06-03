// Content script injected into the NLP iframe.
// Handles: text selection detection, image click detection, highlight rendering, tooltips.
// Communicates with parent via postMessage.

export const CONTENT_SCRIPT = `
(function() {
  'use strict';

  // --- Debug: notify parent that script loaded ---
  window.parent.postMessage({ type: 'cs-debug', msg: 'content-script-loaded', url: window.location.href }, '*');

  // --- Debug banner in iframe ---
  try {
    var debugBanner = document.createElement('div');
    debugBanner.id = 'aifriends-debug';
    debugBanner.style.cssText = 'position:fixed;top:0;left:0;z-index:99999;background:#10b981;color:#fff;padding:2px 8px;font-size:11px;font-family:monospace;border-radius:0 0 4px 0;pointer-events:none;';
    debugBanner.textContent = 'CS loaded';
    document.body.appendChild(debugBanner);
  } catch(_) {}

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

  // --- Remove existing highlights ---
  function removeHighlights() {
    document.querySelectorAll('.aifriends-anno').forEach(function(el) {
      var p = el.parentNode;
      if (p) { p.replaceChild(document.createTextNode(el.textContent), el); p.normalize(); }
    });
    document.querySelectorAll('.aifriends-img-badge').forEach(function(el) { el.remove(); });
  }

  // --- Color map ---
  function annoStyle(c) {
    var bg, fg;
    switch (c) {
      case 'green':  bg = '#86efac'; fg = '#14532d'; break;
      case 'blue':   bg = '#93c5fd'; fg = '#1e3a5f'; break;
      case 'pink':   bg = '#fda4af'; fg = '#881337'; break;
      case 'yellow': bg = '#fde047'; fg = '#713f12'; break;
      default:       bg = '#f87171'; fg = '#7f1d1d'; break;
    }
    return { bg: bg, fg: fg };
  }

  // --- Render text annotations as highlights ---
  function renderAnnotations(annotations) {
    removeHighlights();
    if (!annotations || !annotations.length) {
      window.parent.postMessage({ type: 'cs-debug', msg: 'render-skip: no annotations' }, '*');
      return;
    }

    var textNodes = getTextNodes();
    if (!textNodes.length) {
      window.parent.postMessage({ type: 'cs-debug', msg: 'render-skip: no textNodes' }, '*');
      return;
    }

    var fullText = textNodes.map(function(n) { return n.textContent; }).join('');
    var renderedCount = 0;

    annotations.forEach(function(ann) {
      if (ann.annotation_type === 'image') {
        renderImageBadge(ann);
        renderedCount++;
        return;
      }

      // Try exact match with context first, then fall back to selected_text only
      var search = (ann.context_before || '') + ann.selected_text + (ann.context_after || '');
      var idx = fullText.indexOf(search);
      var selStart, selEnd, matchType;

      if (idx >= 0) {
        selStart = idx + (ann.context_before || '').length;
        selEnd = selStart + ann.selected_text.length;
        matchType = 'context';
      } else {
        // Fallback: match just the selected_text
        idx = fullText.indexOf(ann.selected_text);
        if (idx < 0) {
          window.parent.postMessage({
            type: 'cs-debug',
            msg: 'render-fail: text not found',
            selected_text: ann.selected_text.slice(0, 60),
            context_before_len: (ann.context_before || '').length,
            fullText_len: fullText.length
          }, '*');
          return;
        }
        selStart = idx;
        selEnd = idx + ann.selected_text.length;
        matchType = 'fallback';
      }

      // Build offset map
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

      if (foundNode) {
        renderedCount++;
      } else {
        window.parent.postMessage({ type: 'cs-debug', msg: 'render-fail: no node matched offset', selStart: selStart, selEnd: selEnd }, '*');
      }
    });

    window.parent.postMessage({ type: 'cs-debug', msg: 'render-done', count: renderedCount, total: annotations.length }, '*');

    // Update debug banner
    var banner = document.getElementById('aifriends-debug');
    if (banner) {
      banner.textContent = 'CS: ' + renderedCount + '/' + annotations.length + ' rendered, ' + textNodes.length + ' textNodes';
      banner.style.background = renderedCount > 0 ? '#10b981' : '#f59e0b';
    }
  }

  // --- Render image badge ---
  function renderImageBadge(ann) {
    var imgs = document.querySelectorAll('img[src="' + ann.selected_text + '"]');
    if (!imgs.length) {
      var basename = ann.selected_text.split('/').pop();
      imgs = document.querySelectorAll('img[src$="' + basename + '"]');
    }
    var style = annoStyle(ann.color);
    imgs.forEach(function(img) {
      if (img.parentNode.querySelector('.aifriends-img-badge[data-id="' + ann.id + '"]')) return;

      var parent = img.parentNode;
      var parentStyle = window.getComputedStyle(parent);
      if (parentStyle.position === 'static') { parent.style.position = 'relative'; }

      var badge = document.createElement('span');
      badge.className = 'aifriends-img-badge';
      badge.dataset.id = ann.id;
      badge.textContent = '\\uD83D\\uDCAC';
      badge.style.cssText =
        'position:absolute;top:4px;right:4px;' +
        'background:' + style.bg + ' !important;' +
        'border-radius:50%;width:24px;height:24px;' +
        'display:flex;align-items:center;justify-content:center;' +
        'font-size:13px;cursor:pointer;' +
        'box-shadow:0 1px 4px rgba(0,0,0,0.3);z-index:10;';

      badge.addEventListener('mouseenter', function(e) { showTooltip(e, ann.content); });
      badge.addEventListener('mouseleave', hideTooltip);
      badge.addEventListener('click', function(e) {
        e.stopPropagation();
        e.preventDefault();
        window.parent.postMessage({ type: 'annotation-click', id: ann.id }, '*');
      });

      parent.appendChild(badge);
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
      '@keyframes aifriends-pulse{0%,100%{outline-color:#6366f1}50%{outline-color:#a5b4fc}}'
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

  // --- Image click detection ---
  function onImageClick(e) {
    var img = e.target.closest('img');
    if (!img) return;
    if (e.target.closest('.aifriends-img-badge')) return;
    e.stopPropagation();
    window.parent.postMessage({
      type: 'image-clicked',
      src: img.src,
      alt: img.alt || '',
    }, '*');
  }

  // --- Listen for commands from parent ---
  window.addEventListener('message', function(e) {
    if (!e.data || !e.data.type) return;
    if (e.data.type === 'render-annotations') {
      injectStyles();
      renderAnnotations(e.data.annotations);
    }
    if (e.data.type === 'focus-annotation') {
      var el = document.querySelector('.aifriends-anno[data-id="' + e.data.id + '"], .aifriends-img-badge[data-id="' + e.data.id + '"]');
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

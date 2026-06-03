// Content script injected into the NLP iframe.
// Handles: text selection detection, highlight rendering, tooltips.
// Communicates with parent via postMessage.

export const CONTENT_SCRIPT = `
(function() {
  'use strict';

  // --- Tooltip element ---
  let tooltip = null;
  function ensureTooltip() {
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.className = 'aifriends-tooltip';
      tooltip.style.cssText = [
        'position:fixed; z-index:99999; max-width:320px; padding:8px 12px;',
        'background:#1d232a; color:#e2e8f0; border-radius:8px; font-size:13px;',
        'line-height:1.5; pointer-events:none; opacity:0; transition:opacity 0.15s;',
        'box-shadow:0 4px 12px rgba(0,0,0,0.3); word-break:break-word;',
      ].join('');
      document.body.appendChild(tooltip);
    }
    return tooltip;
  }

  function showTooltip(e, content) {
    if (!content) return;
    const tip = ensureTooltip();
    tip.textContent = content;
    const x = e.clientX + 12;
    const y = e.clientY - 40;
    tip.style.left = Math.min(x, window.innerWidth - 340) + 'px';
    tip.style.top = Math.max(y, 8) + 'px';
    tip.style.opacity = '1';
  }

  function hideTooltip() {
    if (tooltip) tooltip.style.opacity = '0';
  }

  // --- Remove all existing highlights ---
  function removeHighlights() {
    document.querySelectorAll('.aifriends-anno').forEach(function(el) {
      var parent = el.parentNode;
      if (parent) {
        parent.replaceChild(document.createTextNode(el.textContent), el);
        parent.normalize();
      }
    });
  }

  // --- Render annotations as highlights ---
  function renderAnnotations(annotations) {
    removeHighlights();
    if (!annotations || !annotations.length) return;

    // Collect text nodes
    var walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      { acceptNode: function(n) { return n.textContent.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP; } }
    );
    var textNodes = [];
    var node;
    while (node = walker.nextNode()) { textNodes.push(node); }
    if (!textNodes.length) return;

    // Build offset map
    var offset = 0;
    var nodeInfo = textNodes.map(function(n) {
      var len = n.textContent.length;
      var info = { node: n, start: offset, len: len };
      offset += len;
      return info;
    });
    var fullText = textNodes.map(function(n) { return n.textContent; }).join('');

    // Render each annotation
    annotations.forEach(function(ann) {
      var search = ann.context_before + ann.selected_text + ann.context_after;
      var idx = fullText.indexOf(search);
      if (idx < 0) return; // not found

      var selStart = idx + ann.context_before.length;
      var selEnd = selStart + ann.selected_text.length;

      nodeInfo.forEach(function(info) {
        if (!info.node) return;
        var ns = info.start, ne = ns + info.len;
        if (ne <= selStart || ns >= selEnd) return;

        var cutStart = Math.max(0, selStart - ns);
        var cutEnd = Math.min(info.len, selEnd - ns);
        if (cutStart >= cutEnd) return;

        var txt = info.node.textContent;
        var before = txt.slice(0, cutStart);
        var match = txt.slice(cutStart, cutEnd);
        var after = txt.slice(cutEnd);

        var mark = document.createElement('mark');
        mark.className = 'aifriends-anno';
        mark.dataset.id = ann.id;
        mark.textContent = match;
        mark.style.cssText = 'background:' + (ann.color === 'yellow' ? '#fef08a' : ann.color === 'green' ? '#bbf7d0' : ann.color === 'blue' ? '#bfdbfe' : '#fecaca') + ';cursor:pointer;border-radius:2px;';

        mark.addEventListener('mouseenter', function(e) { showTooltip(e, ann.content); });
        mark.addEventListener('mouseleave', hideTooltip);
        mark.addEventListener('click', function() {
          window.parent.postMessage({ type: 'annotation-click', id: ann.id }, '*');
        });

        var frag = document.createDocumentFragment();
        if (before) frag.appendChild(document.createTextNode(before));
        frag.appendChild(mark);
        if (after) frag.appendChild(document.createTextNode(after));
        info.node.parentNode.replaceChild(frag, info.node);
        info.node = null;
      });
    });
  }

  // --- Inject highlight CSS ---
  function injectStyles() {
    if (document.getElementById('aifriends-styles')) return;
    var style = document.createElement('style');
    style.id = 'aifriends-styles';
    style.textContent = '.aifriends-anno:hover { filter: brightness(0.85); }';
    document.head.appendChild(style);
  }

  // --- Selection detection ---
  function onMouseUp() {
    setTimeout(function() {
      var sel = window.getSelection();
      if (!sel || sel.isCollapsed) {
        window.parent.postMessage({ type: 'selection-cleared' }, '*');
        return;
      }
      var text = sel.toString().trim();
      if (!text || text.length < 2) return;

      var range = sel.getRangeAt(0);
      var container = range.startContainer;
      if (!container || !container.textContent) return;

      // Get surrounding context
      var full = container.textContent;
      var idx = full.indexOf(text);
      if (idx < 0) {
        // Try across the whole body text for context
        full = document.body.textContent || '';
        idx = full.indexOf(text);
      }
      var ctxBefore = idx >= 0 ? full.slice(Math.max(0, idx - 60), idx) : '';
      var ctxAfter = idx >= 0 ? full.slice(idx + text.length, idx + text.length + 60) : '';

      window.parent.postMessage({
        type: 'text-selected',
        text: text.slice(0, 500),
        contextBefore: ctxBefore,
        contextAfter: ctxAfter,
      }, '*');
    }, 10);
  }

  // --- Listen for commands from parent ---
  window.addEventListener('message', function(e) {
    if (!e.data || !e.data.type) return;
    if (e.data.type === 'render-annotations') {
      injectStyles();
      renderAnnotations(e.data.annotations);
    }
  });

  // --- Initialize ---
  document.addEventListener('mouseup', onMouseUp);
  injectStyles();
})();
`;

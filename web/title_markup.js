(function titleMarkupModule(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.TitleMarkup = api;
}(typeof globalThis !== "undefined" ? globalThis : this, () => {
  "use strict";

  const SUPERSCRIPT_PATTERN = /<sup>([\s\S]*?)<\/sup>/gi;

  function text(value) {
    return value == null ? "" : String(value);
  }

  function segments(value) {
    const source = text(value);
    const result = [];
    let cursor = 0;
    let match;
    SUPERSCRIPT_PATTERN.lastIndex = 0;
    while ((match = SUPERSCRIPT_PATTERN.exec(source)) !== null) {
      if (match.index > cursor) {
        result.push({ type: "text", value: source.slice(cursor, match.index) });
      }
      result.push({ type: "sup", value: match[1] });
      cursor = match.index + match[0].length;
    }
    if (cursor < source.length || !result.length) {
      result.push({ type: "text", value: source.slice(cursor) });
    }
    return result;
  }

  function plainText(value) {
    return segments(value).map((segment) => segment.value).join("");
  }

  function searchText(value) {
    const plain = plainText(value);
    const compact = plain.replace(/\s+/g, "");
    return compact && compact !== plain ? `${plain} ${compact}` : plain;
  }

  function fallbackEscape(value) {
    return text(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function toHtml(value, escape = fallbackEscape) {
    return segments(value).map((segment) => {
      const escaped = escape(segment.value);
      return segment.type === "sup" ? `<sup>${escaped}</sup>` : escaped;
    }).join("");
  }

  function render(element, value, fallback = "") {
    const source = text(value) || text(fallback);
    element.replaceChildren();
    segments(source).forEach((segment) => {
      if (segment.type === "sup") {
        const superscript = element.ownerDocument.createElement("sup");
        superscript.textContent = segment.value;
        element.append(superscript);
      } else {
        element.append(element.ownerDocument.createTextNode(segment.value));
      }
    });
    return element;
  }

  return Object.freeze({ segments, plainText, searchText, toHtml, render });
}));

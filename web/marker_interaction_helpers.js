"use strict";

(function initializeMarkerInteractionHelpers(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
  root.MarkerInteractionHelpers = api;
})(typeof globalThis !== "undefined" ? globalThis : this, () => {
  const boundMarkers = new WeakSet();

  function bindMarkerHandlers(marker, handlers) {
    if (boundMarkers.has(marker)) {
      return false;
    }
    boundMarkers.add(marker);

    marker.on("click", (event) => {
      event.originalEvent?.stopPropagation();
      handlers.click(event);
    });
    if (handlers.supportsHover) {
      marker
        .on("mouseover", handlers.hover)
        .on("mouseout", handlers.leave);
    }

    const element = marker.getElement?.();
    if (element) {
      element.setAttribute("role", "button");
      element.setAttribute("tabindex", "0");
      element.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        handlers.click(event);
      });
    }
    return true;
  }

  return { bindMarkerHandlers };
});

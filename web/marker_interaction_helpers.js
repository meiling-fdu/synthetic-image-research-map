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
    return true;
  }

  return { bindMarkerHandlers };
});

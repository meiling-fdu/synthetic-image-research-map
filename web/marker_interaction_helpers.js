"use strict";

(function initializeMarkerInteractionHelpers(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
  root.MarkerInteractionHelpers = api;
})(typeof globalThis !== "undefined" ? globalThis : this, () => {
  const boundMarkers = new WeakSet();

  function createHoverIntentController({ delay = 125, setTimer, clearTimer } = {}) {
    const scheduleTimer = setTimer || ((callback, timeout) => setTimeout(callback, timeout));
    const cancelTimer = clearTimer || ((timer) => clearTimeout(timer));
    let timer = null;
    let generation = 0;

    function cancel() {
      generation += 1;
      if (timer !== null) cancelTimer(timer);
      timer = null;
    }

    function schedule(callback) {
      cancel();
      const scheduledGeneration = generation;
      timer = scheduleTimer(() => {
        timer = null;
        if (scheduledGeneration !== generation) return;
        callback();
      }, delay);
      return scheduledGeneration;
    }

    function runNow(callback) {
      cancel();
      callback();
    }

    return { cancel, runNow, schedule };
  }

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
      if (handlers.accessibleLabel) {
        element.setAttribute("aria-label", handlers.accessibleLabel);
      }
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

  return { bindMarkerHandlers, createHoverIntentController };
});

(function exposeMarkerSizeHelpers(root, factory) {
  const helpers = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = helpers;
  }
  root.MarkerSizeHelpers = helpers;
}(typeof globalThis !== "undefined" ? globalThis : this, function buildHelpers() {
  const MIN_MARKER_RADIUS = 6;
  const MAX_MARKER_RADIUS = 18;
  const MARKER_RADIUS_SCALE = 3;

  function groupInstitutionRecords(records, institutionIdentity, paperIdentity) {
    const groups = new Map();
    records.forEach((record) => {
      const key = institutionIdentity(record);
      let group = groups.get(key);
      if (!group) {
        group = {
          key,
          record,
          records: [],
          paperIds: new Set(),
        };
        groups.set(key, group);
      }
      group.records.push(record);
      group.paperIds.add(paperIdentity(record));
    });
    return [...groups.values()].map((group) => ({
      ...group,
      paperCount: group.paperIds.size,
    }));
  }

  function getMarkerRadius(count) {
    const normalizedCount = Math.max(1, Number(count) || 1);
    return Math.min(
      MAX_MARKER_RADIUS,
      MIN_MARKER_RADIUS + Math.sqrt(normalizedCount - 1) * MARKER_RADIUS_SCALE,
    );
  }

  function formatInstitutionPaperCount(count) {
    const normalizedCount = Math.max(0, Number(count) || 0);
    return `${normalizedCount} paper${normalizedCount === 1 ? "" : "s"} in current view`;
  }

  return {
    MAX_MARKER_RADIUS,
    MIN_MARKER_RADIUS,
    formatInstitutionPaperCount,
    getMarkerRadius,
    groupInstitutionRecords,
  };
}));

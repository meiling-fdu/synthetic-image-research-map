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
  const TASK_LABELS = {
    detection: "Detection",
    source_attribution: "Source attribution",
    detection_and_source_attribution: "Detection + source attribution",
    unknown: "Unknown",
  };

  function normalizeTaskLabel(task) {
    const normalized = String(task || "")
      .normalize("NFKC")
      .toLowerCase()
      .replaceAll("&", "and")
      .replaceAll("+", "and")
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "");
    if (normalized === "detection") {
      return "detection";
    }
    if (["source_attribution", "attribution"].includes(normalized)) {
      return "source_attribution";
    }
    if ([
      "detection_and_source_attribution",
      "detection_source_attribution",
      "combined",
      "mixed",
    ].includes(normalized)) {
      return "detection_and_source_attribution";
    }
    return "unknown";
  }

  function getInstitutionTaskCounts(records, paperIdentity) {
    const counts = {
      detection: 0,
      source_attribution: 0,
      detection_and_source_attribution: 0,
      unknown: 0,
    };
    const seenPaperIds = new Set();
    records.forEach((record) => {
      const paperId = paperIdentity(record);
      if (seenPaperIds.has(paperId)) {
        return;
      }
      seenPaperIds.add(paperId);
      counts[normalizeTaskLabel(record.task)] += 1;
    });
    return counts;
  }

  function getDominantInstitutionTask(taskCounts) {
    const entries = Object.entries(taskCounts || {})
      .filter(([, count]) => Number(count) > 0);
    if (!entries.length) {
      return "unknown";
    }
    const largestCount = Math.max(...entries.map(([, count]) => Number(count)));
    const leaders = entries.filter(([, count]) => Number(count) === largestCount);
    return leaders.length === 1 ? normalizeTaskLabel(leaders[0][0]) : "mixed";
  }

  function formatTaskBreakdown(taskCounts) {
    return Object.entries(TASK_LABELS)
      .filter(([task]) => Number(taskCounts?.[task]) > 0)
      .map(([task, label]) => `${label}: ${taskCounts[task]}`)
      .join(" · ");
  }

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
    formatTaskBreakdown,
    getDominantInstitutionTask,
    getInstitutionTaskCounts,
    getMarkerRadius,
    groupInstitutionRecords,
    normalizeTaskLabel,
  };
}));

(function exposeInstitutionTypeLabels(globalScope) {
  "use strict";

  const values = Object.freeze(["university", "research_unit", "company", "other"]);
  const labels = Object.freeze({
    university: "University",
    research_unit: "Research Institute",
    company: "Company",
    other: "Other",
  });
  const aliases = Object.freeze({
    education: "university",
    educational: "university",
    research: "research_unit",
    institute: "research_unit",
    laboratory: "research_unit",
    department: "research_unit",
    corporate: "company",
    commercial: "company",
    unknown: "other",
  });

  function normalize(value) {
    const normalized = String(value || "")
      .normalize("NFKC")
      .trim()
      .toLocaleLowerCase()
      .replace(/[\s-]+/g, "_");
    const resolved = aliases[normalized] || normalized;
    return values.includes(resolved) ? resolved : "other";
  }

  function label(value) {
    return labels[normalize(value)];
  }

  const resolver = Object.freeze({ values, labels, normalize, label });
  globalScope.InstitutionTypeLabels = resolver;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = resolver;
  }
}(typeof globalThis === "undefined" ? window : globalThis));

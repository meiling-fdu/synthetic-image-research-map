(function exposeInstitutionDisplay(globalScope) {
  "use strict";

  function text(value) {
    return String(value || "").trim().replace(/\s+/g, " ");
  }

  function format(canonicalName, abbreviation) {
    const canonical = text(canonicalName);
    const shortName = text(abbreviation);
    if (!canonical || !shortName) return canonical;
    const suffix = `(${shortName})`;
    return canonical.toLocaleLowerCase().endsWith(suffix.toLocaleLowerCase())
      ? canonical
      : `${canonical} ${suffix}`;
  }

  function formatRecord(record) {
    const value = record || {};
    const canonical = text(
      value.canonical_name
      || value.canonical_institution_name
      || value.institution_name
      || value.institution
      || value.name,
    );
    return format(canonical, value.abbreviation || value.preferred_abbreviation);
  }

  const helper = Object.freeze({ format, formatRecord });
  globalScope.InstitutionDisplay = helper;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = helper;
  }
}(typeof globalThis === "undefined" ? window : globalThis));

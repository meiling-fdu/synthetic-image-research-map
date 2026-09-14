"use strict";

(function exposePublicExportMetadata(globalObject) {
  const UTC_TIMESTAMP = /^(\d{4})-(\d{2})-(\d{2})T\d{2}:\d{2}:\d{2}Z$/;

  function formatPublicPreviewDate(value) {
    if (typeof value !== "string") return "";
    const match = value.match(UTC_TIMESTAMP);
    if (!match) return "";
    const [, rawYear, rawMonth, rawDay] = match;
    const year = Number(rawYear);
    const month = Number(rawMonth);
    const day = Number(rawDay);
    const date = new Date(Date.UTC(year, month - 1, day));
    if (
      date.getUTCFullYear() !== year
      || date.getUTCMonth() !== month - 1
      || date.getUTCDate() !== day
    ) return "";
    return new Intl.DateTimeFormat("en-GB", {
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: "UTC",
    }).format(date);
  }

  const api = { formatPublicPreviewDate };
  globalObject.PublicExportMetadata = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
}(typeof globalThis !== "undefined" ? globalThis : this));

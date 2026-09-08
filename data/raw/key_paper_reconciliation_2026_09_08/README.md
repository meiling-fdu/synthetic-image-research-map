# Targeted reconciliation evidence

Retrieved on 2026-09-08 only for the 46 unresolved checklist cases and bounded
comparisons against existing corpus entries. The resumed pass reused this cache;
it did not perform another literature search.

- `arxiv_*.source`: unmodified arXiv abstract-page HTML (citation metadata and
  version history). Current titles/authors may differ from checklist annotations.
- `crossref_<row>.json`: unmodified Crossref response for an existing nearest
  candidate. The row number identifies the checklist comparison, **not a confirmed
  match**. Rejected candidates are retained as raw evidence. Only the explicit
  decisions in `data/manual/key_paper_reconciliation.json` establish a match.
- `floda.source`, `bidirectional.source`, `quality.source`: exact DOI Crossref
  records. Other named `.source` files are official proceedings/project HTML.
  `source_urls.json` records the download URLs.
- `rdd.pdf`, `dynamic.pdf`: official CVPR and CVWW PDFs, respectively. Source URLs
  appear in the decision registry/report. No related papers, code, datasets or
  model weights were collected.
- `search_*.json`, `web12.json`, `reconcile*.json`: saved retrieval tool results.
  Search engines may return unrelated suggestions; these were not automatically
  accepted or expanded into new corpus candidates.
- `manifest.json`: SHA-256 values for cached evidence files.

The evidence registry preserves checklist metadata separately from resolved
identities, decisions, compared records and deduplication notes. Raw evidence is
not a curation override and is never promoted merely by title similarity.

# Stable Release Checkpoint — 24 August 2026

This checkpoint records the audited public research map, Admin curation console,
curated registry, and public export as the current stable release baseline. It
does not change application behavior or public data semantics.

## Public research map

- Unified the filter and sort controls around one keyboard-accessible dropdown
  pattern with consistent labels, focus states, spacing, and responsive
  behavior.
- Added removable active-filter chips, a clear-all action, no-results recovery,
  and filter state announcements without changing filter semantics.
- Added canonical shareable URL state for filters, result view, sorting,
  institution selection, and stable paper deep links. Back/forward navigation
  restores the corresponding view without clearing unrelated filters.
- Synchronized Map, Results, and Paper Details selection state. Marker hover,
  marker pinning, result-origin selection, progressive result reveal, connection
  lines, and Paper Details use the same stable paper/institution identities.
- Standardized visible data units: raw map relationships, unique papers,
  institutions, countries, task totals, chart values, result counts, and marker
  sizes are labeled according to the population they count.
- Added task, institution, and year chart quick filters with keyboard controls,
  pressed state, accessible labels, and focus preservation across rerenders.
- Improved mobile layouts at the supported narrow widths, including the filter
  dialog, header statistics, results controls, cards, Paper Details, and
  document-level overflow containment.
- Improved accessibility for filter dialogs, custom listboxes, active filters,
  result expansion, map markers, Paper Details, focus restoration, and reduced
  motion. The final audit added accessible names to Leaflet marker buttons and
  returns focus to the originating marker when Paper Details closes.

## Institution identity and location integrity

- Consolidated only exact, reviewed institution identities and aliases while
  retaining ambiguous same-name institutions as separate canonical IDs.
- Preserved every confirmed location and explicit mapping-to-location choice.
  Exact duplicate physical locations can be consolidated through durable ID
  redirects; distinct campuses or offices remain distinct.
- Added conservative identity and location audit scripts plus machine-readable
  and narrative audit reports. Fuzzy or conflicting matches remain review cases.
- Preserved the Northeastern University identities that have conflicting
  confirmed country evidence, and preserved Xiaohongshu's Shanghai and Beijing
  locations without silently selecting one.
- Public export, Admin evidence, aliases, hierarchy/search relationships,
  redirects, audit history, and author–institution mappings reconcile against
  the same canonical identity and location records.

## Admin curation console

- Corrected institution deduplication, merge, alias, hierarchy, location, and
  mapping lifecycle behavior while retaining explicit confirmation and rollback
  boundaries.
- Corrected review-state transitions and suppression so resolved, ambiguous,
  ignored, excluded, and still-actionable records remain distinguishable.
- Added explicit selection when a canonical institution has multiple confirmed
  locations; Admin does not infer a location from locality alone.
- Preserved pagination, search, sorting, queue navigation, editor state, mapping
  history, publish workflow safeguards, and manual review evidence.
- The final production audit fixed the 320px masthead overflow and anchored
  mobile navigation menus to the full navigation bar so all menu items remain
  reachable without horizontal page scrolling.

## Release baseline

The authoritative checkpoint is
`data/processed/current_repository_baseline.json`. Its counts are derived from
the committed curated CSV and public JSON artifacts. Exact repository totals
are asserted only by dedicated integration-baseline tests; frontend behavior
tests continue to use semantic assertions or isolated fixtures and are not
coupled to mutable production totals.

Current primary dataset counts:

- 315 curated paper rows.
- 541 unique public paper records.
- 529 unique map-source paper identities and 528 public papers with at least one
  mapped location.
- 1,205 public paper–institution relationships.
- 600 unique public-map institution identities under validator semantics.
- 635 canonical institution rows, of which 632 are active.
- 853 author–institution mappings and 401 confirmed institution-location rows.
- 53 confirmed institution aliases and 7 confirmed hierarchy edges.

All local public assets use the release cache key
`20260824-stable-release`.

## Manual-curation backlog retained

Warnings remain visible and are not suppressed or automatically resolved:

- Curated validation: 0 errors and 192 warnings, primarily missing or
  conflicting author–institution evidence, preserved historical audit
  references, and explicit review-queue conflicts.
- Public map validation: 0 errors and 0 warnings.
- Public paper validation: 0 errors and 70 warnings for authors without an
  institution index; these require evidence-based mapping review.
- Exclusion validation: 0 errors and 2 warnings for restored exclusions that
  are not currently present in the public preview.
- Identity audit: one conflicting-country same-name institution case remains
  untouched, and one exact Xiaohongshu identity remains intentionally dependent
  on explicit multi-location selection.
- Location audit: no exact duplicate confirmed locations remain.

The non-strict public validator passes. Strict mode intentionally remains
nonzero while the 70 public-paper warnings exist; this checkpoint does not
weaken strict validation or reinterpret those warnings as software defects.

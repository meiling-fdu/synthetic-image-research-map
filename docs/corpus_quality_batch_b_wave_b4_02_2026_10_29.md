# Batch B Wave B4-02 — Local maintainer adjudication

Checkpoint prepared2026-10-29; recovered and applied2026-10-30. This is an unpublished local transaction on `codex/batch-b-b4-02` at `7fc8ceae702324628335944cf4b545a3733fdc56`. No B4-01 merge, export, staging, commit, push or B5 execution occurred.

## Final decisions

| Review | Formal disposition | Authoritative effect |
|---|---|---|
| P001 | VENUE_BINDING_REQUIRES_TRACK_DECISION | No data change; formal unresolved hold. |
| U001 | EVIDENCE_INSUFFICIENT | No data change; formal unresolved hold. |
| U002 | EVIDENCE_INSUFFICIENT | No data change; formal unresolved hold. |
| U003 | EVIDENCE_INSUFFICIENT | No data change; formal unresolved hold. |
| P049 | CANONICAL_JOURNAL_BINDING_ACCEPTED | Canonical journal binding: venue_id, venue_name, venue_type only. |
| U005 | LOCATION_PRECISION_NOT_REPRESENTABLE | No data change; formal unresolved hold. |
| P058 | CANONICAL_JOURNAL_BINDING_ACCEPTED | Canonical journal binding: venue_id, venue_name, venue_type only. |
| U006 | EVIDENCE_INSUFFICIENT | No data change; formal unresolved hold. |
| U007 | EVIDENCE_INSUFFICIENT | No data change; formal unresolved hold. |
| P068 | CANONICAL_JOURNAL_BINDING_ACCEPTED | Canonical journal binding: venue_id, venue_name, venue_type only. |
| U008 | EVIDENCE_INSUFFICIENT | No data change; formal unresolved hold. |
| U014 | EVIDENCE_INSUFFICIENT | No data change; formal unresolved hold. |
| U016 | EVIDENCE_INSUFFICIENT | No data change; formal unresolved hold. |
| U018 | EVIDENCE_INSUFFICIENT | No data change; formal unresolved hold. |
| U023 | EVIDENCE_INSUFFICIENT | No data change; formal unresolved hold. |

All 15 assigned actions receive exactly one native formal decision. P049, P058 and P068 resolve; P001 and all 11 institution-site actions remain open. The three journal canonical names and publication types already matched the sources. Their bindings add nine cells and three aliases, with empty optional acronyms and tracks retained. No unsupported abbreviation or venue ID is invented; IDs use the native deterministic registry convention.

## Venue evidence and P001 binding boundary

- P049: DOI `10.64336/001c.156299`; Journal of High School Science; ordered sole author and title verified against preserved official journal metadata.
- P058: DOI `10.1007/s41060-026-01192-9`; International Journal of Data Science and Analytics; ordered Korkmaz/Özden authors verified. Publisher bibliographic short form is preserved as evidence, not promoted to a letter acronym. The similarly named International Journal of Advanced Computer Science and Applications is a distinct journal, not an alias.
- P068: DOI `10.1007/s00138-026-01836-7`; Machine Vision and Applications; ordered Raj/Mathew/Mondal authors verified. No acronym derived from initials.
- P001: exact conference identity and CISIS acronym are supported. However `scripts/validate_curated_database.py` requires a paper track for a bound conference, while the existing track is blank and the B3 handoff requires preserving it. The materializer would default it to Main. This checkpoint explicitly declines that extra inference: no binding, registry row or track change. This is a binding-policy/schema blocker, not a claim that the conference identity lacks evidence. Preserve first-online2026 versus citation/copyright2027.

Accepted decisions bind the final saved venue state using native `[venue-state:SHA256]` confirmations, plus independent per-action transaction/evidence bindings. All original 103 decision rows are a byte-identical prefix ; 15 unique appends produce 118 rows. New IDs were independently checked against both published history and the 112-row B4-01 pending registry. Original B3 evidence, source hashes, author spelling/date/version distinctions and numerical limitations remain traceable in the manifest.

## U005 precision-policy decision

U005 remains `LOCATION_PRECISION_NOT_REPRESENTABLE` / native action `unresolved`. The school identity and declared paper-time affiliation address, 5 Mihai Eminescu,440014 Satu Mare, are verified separately from the proposed geographic point. They do not prove an author’s physical work location, room or residence.

The official school embed selects viewport centre 47.789438,22.876378 at zoom 19. It is not a verified marker, surveyed coordinate, independently geocoded object or checked campus geometry. CRS is undeclared and positional uncertainty unmeasured. The candidate stays in evidence only.

Existing policy permits checked representative institution/campus points; it does not require exact author buildings for every marker. The narrower blocker here is faithful representation of this viewport-only qualification: the current location schema has no operational point-kind/precision/CRS/accuracy fields, the confirmation path collapses accepted coordinates to `known`, and retired source/review-note fields are rejected or stripped at public boundaries. Formal notes preserve the hold; they cannot change saved/exported point semantics. No schema semantics were silently expanded.

An additional independent operational blocker is that the curated-location save workflow rejects the exact Romania/RO draft under its supported-country table. This is distinct from the database validator’s two-letter ISO syntax check. No country table correction, substitute geography, rounding, location row or mapping change was made.

## Ten evidence holds and additive U002 correction

U001, U002, U003, U006, U007, U008, U014, U016, U018 and U023 retain `EVIDENCE_INSUFFICIENT`. Current contact/HQ addresses and geocodes are not promoted to paper-time campuses. Bitdefender office ambiguity, Wuhan multicampus ambiguity, ENSIA temporal/site gaps, BTU 2020-to-2026 continuity, Turing current-address versus programme-site distinction and IIT Patna’s approximately 1.76km coordinate discrepancy remain explicit.

B3-02 narrative correction, additive only: the saved SAMR contact gives postcode 510630; patent CN112990582A, published 2021-06-18, gives 510663. B3-02’s matrix and source captures were correct, while the human report reversed their source attribution. The originals remain byte-identical. Correcting the attribution neither normalizes the values nor establishes the 2026 laboratory site. Exact preserved source hashes/locators are included in the policy review and adjudication manifest.

## Exact changed-file inventory

| Path | Change |
|---|---|
| data/curated/papers.csv | Nine cells on P049/P058/P068: venue_id, venue_name, venue_type. |
| data/curated/venue_aliases.csv | Three validated full-name journal aliases appended; prior bytes preserved. |
| data/curated/review_decisions.csv |15 native formal decisions appended: three terminal acceptances and 12 unresolved holds. |
| docs/key_paper_coverage_report.md | Only the input-checksum line changes; coverage CSV, report body and counts unchanged. |
| data/raw/corpus_quality_batch_b_wave_b4_02_2026_10_29/adjudication_manifest.json | New machine-readable formal decisions, bindings, evidence history and policy findings. |
| data/raw/corpus_quality_batch_b_wave_b4_02_2026_10_29/b5_handoff.json | New dependency/conflict handoff; no execution authorized. |
| docs/corpus_quality_batch_b_wave_b4_02_2026_10_29.md | This report. |
| tests/test_corpus_quality_batch_b_wave_b4_02.py | Focused positive and negative regression coverage. |

The first three files are the authoritative changes. The checksum-only supporting receipt is necessary because papers.csv is a receipt input. It was checked with the repository’s pure expected-artifact API; no export or broad report regeneration ran. Other paper fields, canonical IDs, authors, DOI/arXiv, metadata sources, timestamps, tasks/types, institutions, coordinates and relationships are unchanged.

## Recomputed accounting and validation

| Metric | Before | After B4-02 alone |
|---|---:|---:|
| original_actions | 159 | 159 |
| original_papers | 148 | 148 |
| terminal_actions | 28 | 31 |
| historical_unresolved_actions | 131 | 128 |
| historical_unresolved_papers | 121 | 121 |
| active_public_unresolved_actions | 129 | 126 |
| active_public_unresolved_papers | 119 | 119 |

Accounting is recomputed from the original 159-action ledger and current native formal decisions. B4-01 is not included. The three newly resolved papers retain independent open institution actions, so unresolved-paper totals remain 121 historical / 119 active-public.

Corpus/public identity counts remain 674 public, 557 formal, 613 mapped, 61 unmapped,1,410 relationships and1,410 unique pairs. Tasks remain 621 detection, 84 source attribution, 45 localization. Research types remain 578 method, 138 dataset, 97 benchmark, 21 survey, 86 analysis study. Public exports are intentionally unchanged.

Focused regression: 185 tests and 34 subtests passed, zero failures. Curated and public validators each reported zero errors. No full suite ran.

One initial new-test failure checked for the word known in policy prose. The check was replaced by a direct schema-field assertion; the separate pure confirmation-loss test still verifies `known` output and discarded qualifiers. Initial 184-pass/1-failure logs and JUnit are preserved. No production behavior, accepted decision or substantive assertion was weakened.

Pre-application independent review, 12 pure location-policy checks, native alias validation and source-bound acceptance checks passed. Final independent preservation audit results are stored with this local checkpoint in the validation archive; they verify the exact four-modified/four-added allowlist, all source-byte boundaries, B4-01 and B3-02 immutability, protected 128, frozen 49, Batch C debts, separate 39-paper inventory, CI acceptance history and concurrent-work isolation.

## B5 integration dependency

B4-01 and B4-02 are two independent unpublished transactions, both based on 7fc8ceae. They overlap in papers.csv, review_decisions.csv and the checksum receipt, but target distinct paper cells and collision-free decision IDs. Future B5 must reconcile records/cells, preserve the common 103-row history, maintain the B4-01 nine-row historical prefix if its tests require it, and append these 15 rows without re-upsert. Never concatenate complete CSV files or select one transaction’s whole-file version.

If no independent changes intervene, the future union would contain 127 decision rows, 39 terminal Batch B actions, 120 historical / 118 active-public unresolved actions and 113 / 111 unresolved papers. Those are planning-only union counts; no union was applied.

B5 must also make the sealed B3 evidence reproducibly available to publication, refresh the combined receipt, run authorized deterministic exports and all full regression/CI/publication gates, and revalidate source-bound confirmations against the then-current remote. Existing historical transaction-test boundaries require deliberate review during B5; no historical tests or frozen receipts were changed here. See b5_handoff.json for exact fingerprints, dependencies and blockers.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

Stopped at the validated local adjudication checkpoint. Nothing staged, committed, exported, pushed or published; B5 not started.

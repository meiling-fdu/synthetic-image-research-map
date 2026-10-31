# Batch B Wave B4-01 — local publication-URL adjudication

Baseline `7fc8ceae702324628335944cf4b545a3733fdc56`; worktree `/Users/meilinger/.codex/worktrees/batch-b-b4-01/synthetic-image-research-map`; branch `codex/batch-b-b4-01`. Exactly nine B2-01 actions adjudicated using the sealed B3-01 evidence packet. No publication discovery or manuscript review was repeated.

**Accepted and stored: P034, P254, P305, P097, P105, P150, P177, P229. P028 retains a formal `unresolved` / `EVIDENCE_INSUFFICIENT` hold.** These are URL-only decisions; no task, type, identity, author, venue, mapping or relationship correction is authorized.

| Action | Formal decision ID | Disposition | Stored authoritative URL |
| --- | --- | --- | --- |
| P034 | `review:905c181f62686fdd1d46` | `PUBLICATION_URL_ADDITION_ACCEPTED` | https://link.springer.com/chapter/10.1007/978-3-032-37429-5_14 |
| P254 | `review:908428d376d858278016` | `PUBLICATION_URL_ADDITION_ACCEPTED` | https://dl.acm.org/doi/10.1145/3770916 |
| P305 | `review:8aa8f164a0591cc84b0c` | `PUBLICATION_URL_ADDITION_ACCEPTED` | https://ebooks.iospress.nl/doi/10.3233/FAIA250925 |
| P028 | `review:5464d1c1552b94847682` | `EVIDENCE_INSUFFICIENT` | No change; exact ACM archival record remains unverified |
| P097 | `review:a1eb8fea1c6f117dbf96` | `PUBLICATION_URL_ADDITION_ACCEPTED` | https://link.springer.com/chapter/10.1007/978-3-032-37321-2_32 |
| P105 | `review:4f3e2bcbf2d0294c6118` | `PUBLICATION_URL_ADDITION_ACCEPTED` | https://link.springer.com/chapter/10.1007/978-3-032-37550-6_18 |
| P150 | `review:d0be82c0d01fb23f6dec` | `PUBLICATION_URL_ADDITION_ACCEPTED` | https://link.springer.com/chapter/10.1007/978-3-032-37464-6_12 |
| P177 | `review:5445762b46f00e76c3c6` | `PUBLICATION_URL_ADDITION_ACCEPTED` | https://link.springer.com/chapter/10.1007/978-3-032-37350-2_34 |
| P229 | `review:c5a66f0b4a9e8c9a1135` | `PUBLICATION_URL_ADDITION_ACCEPTED` | https://link.springer.com/chapter/10.1007/978-3-032-37023-5_10 |

## Exact source changes

- `data/curated/papers.csv`: only six `paper_url` cells, for P034/P097/P105/P150/P177/P229. Original row bytes, quoting and embedded newlines are preserved outside those cells; no timestamp/identifier/author field is rewritten.
- `data/curated/publication_overrides.csv`: append only P254/P305. The established schema repeats their current 2025 year, venue, publication type and arXiv DOI exactly; only `formal_paper_url` changes effective links. The legacy column named `formal_doi` deliberately retains the existing arXiv DOI; it does not assert that this is the publisher DOI. No manual correction file is edited.
- `data/curated/review_decisions.csv`: preserve the complete 103-row byte prefix and append nine unique `publication_venues` decisions: eight `no_action_after_review` terminal corrections, one `unresolved` hold. This queue avoids overwriting P034’s existing R034 decision under `other`. Native IDs are collision-checked before append.
- `docs/key_paper_coverage_report.md`: refresh only its input SHA-256 line after the six URL cells changed. The coverage CSV, every coverage/count row and all other document characters are identical. No public export is regenerated.

Supporting new files: this report; adjudication manifest with original B3 records, decisions and exact URL/action/identity bindings; B5 handoff; targeted B4 regression tests. Full eight-file inventory is in the handoff.

## Accounting from authoritative source

| Measure | Before | After |
| --- | ---: | ---: |
| Original Batch B actions /papers | 159 /148 | 159 /148 |
| Formal terminal actions | 28 | 36 |
| Historical unresolved actions /papers | 131 /121 | 123 /113 |
| Active-public unresolved actions /papers | 129 /119 | 121 /111 |
| Review registry rows | 103 | 112 |

P028, L015 and P562 remain historically unresolved; the latter two are inactive-public holds. No original action or Batch B denominator is added or removed.

## Evidence and caveats

All nine decisions link to their exact B3 per-paper hash and B3 disposition-matrix hash. `publication-url-state` hashes bind the immutable transaction baseline, original action, canonical identity, exact accepted URL, authoritative field/locator and B3 record. They are separate from venue confirmations and do not set a broad `venue-state` marker.

P034 accepts a same-work formal-version link while preserving canonical 12 versus publisher 13 authors, Manni Cui insertion, Chen casing and every earlier numerical, counterevidence, release and version limitation. There is no author replacement or full-version-equivalence claim. P254 retains the 2025 online/2026 print distinction; P305 retains ECAI proceedings context despite book-chapter deposition. Other publisher date/crosslink/manuscript limits remain in the embedded B3 records. P028’s failed archival identification is not nonpublication evidence.

Publisher landing variants for P254/P305/P150/P177/P229 are taken from existing primary deposits/captures. Unlike DOI resolver URLs, these do not derive a new helper DOI and allow source identifiers to remain unchanged. Generic Admin normalization/upsert is deliberately not used for paper rows because it could clear or replace an existing arXiv DOI.

## Validation

- Focused metadata/identity/link/decision/frontend regression: **176 tests and 12 subtests passed**, zero failures, 25.02 seconds. The new B4 coverage includes nine decision gates, native idempotency, invalid-evidence/identity rejection, source identifiers, exact structured-author restoration and proof that URL-only decisions do not confirm venue/type/track.
- Authoritative validator: **0 errors**,294 unchanged warnings. Public map/paper validator: **0 errors**,0/62 unchanged warnings. Key-paper freshness check passed. All 117 offline historical inputs checksum-verified.
- Independent saved-evidence gate: 313/313 pass; independently applied source/decision audit: 143/143 pass. Complete preservation preflight: **14,435 checks passed**, zero failures; the final gate and exact source fingerprints accompany this checkpoint.

Two initial new-test failures came from comparing an intermediate flat byline to a partial decorated B3 projection. The unchanged baseline merge did the same flattening. Tests now compare identical full pipeline stages and additionally execute actual downstream enrichment, proving exact restoration of the full P034/P105 structured authors using their 7/6 marker contexts. No production code or source data was changed to satisfy those tests. Initial logs and independent proof are retained.

The fresh worktree initially lacked an ignored key-paper audit input. Authenticated offline restoration supplied 117 exact inputs without modifying frozen receipts. The subsequent public-validator failure was solely the generated documentation input checksum; coverage body/CSV were unchanged and only that checksum line was refreshed. Original diagnostics are retained.

## Preserved state and B5 boundary

All 674 public identities and 1,410 relationship rows/pairs remain byte-identical. Corpus remains 674 public, 557 formal, 613 mapped; taxonomy remains 621 detection, 84 source attribution, 45 localization, 578 method, 138 dataset, 97 benchmark, 21 survey, 86 analysis study. Source paper IDs, DOI/arXiv values, authors, venue metadata, taxonomy and all mapping/institution files are preserved.

The 128 protected primary files, 49 frozen NeurIPS artifacts, Batch C 13 debts, separate 39-paper inventory, B1Q/B1R/B1S evidence, B2/B3 packets, CI acceptance records and unrelated worktrees are preserved. Authenticated ignored operational inputs remain unstaged.

**Public synchronization and release validation are deferred to B5.** Current public JSON intentionally still contains the previous URLs. B5 must inspect only the authorized link/alias/derived-flag/notes delta, verify deterministic exports and run the full regression/CI gates. Existing B1S/B1E historical transaction tests compare later live files against older endpoints; their historical/current boundaries require explicit justified handling without weakening assertions or modifying frozen receipts. No such test was edited here.

The eight accepted URL corrections and P028 hold are local, unstaged and uncommitted. No public export, stage, commit, push or publication occurred; B5 has not begun.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

```
UNEXPECTED_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
UNRELATED_CURATED_METADATA_CHANGED = 0
PUBLIC_EXPORT_FILES_CHANGED = 0
B2_B3_EVIDENCE_CHANGED = 0
CI_ACCEPTANCE_RECORDS_CHANGED = 0
IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0
```

# NeurIPS 2026 implementation review

**Status: staged, not applied.** The current schema requires a nonempty supported conference track. All eight records have acceptance evidence but no verified track. The request prohibits both fabricated tracks and weakening the validator; a user decision is required before applying this migration.

## Initial working tree

Only four untracked paths existed: the reconciliation JSON, reconciliation Markdown, processed audit directory, and curation script. No tracked files had changes. The JSON and Markdown reconciliation copies match the locked originals byte-for-byte. No literature research or reconciliation was repeated.

The unsupported `Pending` value was removed from the draft payload, action plan, and migration script. No conference-track schema or validator changes were made. No new Pending track category or validator exception was introduced.

## Durable reconciliation

[All 17 candidates](neurips_2026_targeted_gap_fill.md) and [machine-readable reconciliation](../data/manual/neurips_2026_targeted_gap_fill_reconciliation.json) retain the locked decisions: 7 MISSING_ADD, 1 MIRROR update, 7 AMBIGUOUS, 2 HOLD_SCOPE. Historical `pending` text in this immutable evidence means metadata missingness, not a repository track category. [Evidence manifest](../data/processed/neurips_2026_targeted_gap_fill_2026_10/evidence/manifest.json) maps original temporary locations to durable copies; runtime does not depend on temporary files.

## Proposed additions (none applied yet)

- BIAS-ID: A Framework for Analyzing Transformation Biases in AI-Generated Image Detectors
- Post-hoc Selective Classification for Reliable Synthetic Image Detection
- FARE: Forensic Acceptance Region Estimation for Catching Bait-and-Switch Image Generators
- Beyond Real or Fake: A Dual-Channel Authenticity and Reasoning Protocol for Photographic Assessment
- SIGMA: Semantic-Difference Instruction-Grounding Mask Annotator for Text-Driven Image Manipulation Localization
- SALART-VQA: Diagnosing Whether VLMs Understand Salient Artifacts in Generated Images
- Can Pixels Alone Reveal Image Origin? Minimax Limits and Learnable Interfaces for Passive Provenance

All seven titles above, plus MIRROR, have unresolved track metadata. The proposed rows store an empty `venue_track`; the current repository rejects this representation for conferences and would normalize it to Main in some paths. Neither Other nor Poster is established as a missing-track convention.

SIGMA affiliations remain unresolved. Beyond Real or Fake uses the already-saved PDF first-page evidence; existing Google Research and Google DeepMind identities are reused. Proposed new institutions are fbeta GmbH, YouTube, and University of Queensland. No institution aliases or hierarchy records are merged or rewritten.

## MIRROR proposal

Authoritative identity: `curated:8fe7cb0db76df68a5e38`. No MIRROR changes have been applied. The staged update changes these exact fields: `title`, `venue`, `venue_id`, `venue_name`, `venue_acronym`, `venue_type`, `raw_venue`, `paper_url`, `publication_type`, `abstract`, `metadata_source`, `updated_at`.

Publication type would change from preprint to conference; venue from arXiv to NeurIPS. The title drops Generalizable. `paper_url` becomes https://neurips.cc/virtual/2026/poster/149292. The abstract code URL changes from https://github.com/349793927/MIRROR to https://github.com/handsome-rich/MIRROR. The arXiv ID 2602.02222, existing OpenAlex identity, authors, affiliations, and method/dataset/benchmark taxonomy labels stay intact. Taxonomy evidence excerpts and nine mapping titles are synchronized with the title/code correction. Full before/after values are in implementation_review.json.

## Dataset actions

- SalArt-VQA: verified public release evidence preserved at https://huggingface.co/datasets/salartvqa/SalArt-VQA, revision `eacc6d39661b04c0ac2abdcd8ed2c5d37d9ed6f4`, 950 images, 3,681 questions, five Parquet shards plus release manifest/checksums. The repository has no standalone dataset/benchmark table or paper code/data URL fields; the durable payload and audit preserve these resources without introducing a schema. The paper remains taskless, as locked, and is omitted by the existing public task gate.
- No other dataset/benchmark records were added or linked. Existing datasets mentioned by BIAS-ID, ReSIDe, FARE and Pixels Alone remain reuse evidence only.
- ManipBench and SIGMA masks were not added: releases only promised. MLLM-Edit release remains unverified. No Beyond Real or Fake release was verified.

Human-AIGI was not added as a released dataset because the current source still marks it Coming soon.

## Deferred candidates

- **DEDCA: Test-Time Adaptation for Generalized AI-Generated Image Detection** — AMBIGUOUS. See the locked reconciliation row for the evidence and unresolved fields.
- **SAGE: Semantic-Agnostic Image Embedding for Generalized AI-Generated Image Detection** — AMBIGUOUS. See the locked reconciliation row for the evidence and unresolved fields.
- **The road reaches every place, the short cut only one: Self-Adversarial Shortcut Mitigation for AI-Generated Image Detection** — AMBIGUOUS. See the locked reconciliation row for the evidence and unresolved fields.
- **Too Aligned to be Real: Detecting AI-Generated Images via Cross-modal Alignment Shift** — AMBIGUOUS. See the locked reconciliation row for the evidence and unresolved fields.
- **Unified Forensic Preference Learning for Generalizable Synthetic Image Detection** — AMBIGUOUS. See the locked reconciliation row for the evidence and unresolved fields.
- **MLLM-Edit: Benchmarking Image Forgery Detection and Localization under MLLM-based Editing** — AMBIGUOUS. See the locked reconciliation row for the evidence and unresolved fields.
- **ManipShield: A Unified Framework for Image Manipulation Detection, Localization and Explanation** — AMBIGUOUS. See the locked reconciliation row for the evidence and unresolved fields.
- **Can We Model the Artifacts Explicitly? Disentangle Artifacts via Pairwise Edit Relations for Image Manipulation Localization** — HOLD_SCOPE. See the locked reconciliation row for the evidence and unresolved fields.
- **RiSE: Residual Subspace Expert for Generalizable Text-Centric Image Forgery Localization** — HOLD_SCOPE. See the locked reconciliation row for the evidence and unresolved fields.

DEDCA, SAGE, Self-Adversarial Shortcut Mitigation, Too Aligned, and MLLM-Edit lack sufficient primary metadata. Unified Forensic Preference Learning has conflicting author lists. ManipShield explicitly remains blocked by arXiv’s 9 authors versus the NeurIPS author-page’s 7 authors (omitting Qiang Hu and Jing Liu). Pairwise Edit Relations and RiSE lack evidence establishing material generative-AI scope.

## Actual counts and validation

| Measure | Before | Actual after (unapplied) | Staged only |
| --- | ---: | ---: | ---: |
| Public papers | 623 | 623 | Not exported |
| Formally published | 514 | 514 | Not exported |
| Curated paper rows | 479 | 479 | 486 |
| Taxonomy rows | 666 | 666 | 672 |
| Mapped unique papers | 603 | 603 | Not exported |
| Paper-layer located | 602 | 602 | Not exported |
| Validation errors | 0 | 0 | 8 |
| Curated warnings | 245 | 245 | 246 |
| Public affiliation warnings | 22 | 22 | Not exported |

All eight staged errors are missing conference tracks. The one new curated warning is SIGMA’s unresolved author–institution mapping; all 245 pre-existing warnings are preserved. Duplicate candidates: zero in the staged curated validation. Taxonomy and institution checks introduce no other errors. Dataset references are not a schema feature; no invalid references were introduced. Expected public counts of 629/521 in the action plan remain predictions, not verified successor counts.

No count assertions or historical fixtures were edited. No exports were regenerated from invalid staged data. The full test suite is deferred until the policy decision permits application.

## Reproduction

Run `python3 scripts/curate_neurips_2026_targeted_gap_fill.py --stage-only` to regenerate the five reviewed CSVs under `data/processed/neurips_2026_targeted_gap_fill_2026_10/staged/`. Without that flag, the script refuses to apply while missing tracks are invalid. Stable identities, predecessor hashes, duplicate refusal, and deterministic staging are checked. No network operations occur.

No commit or push was performed.

Targeted regressions: **34 passed, zero failed, zero skipped** (conference-track, taxonomy, published-only frontend, public-export metadata). These validate the unchanged authoritative state, not a completed successor export. Migration checks also pass: exact delta, deterministic staging, duplicate refusal, and safe application refusal.

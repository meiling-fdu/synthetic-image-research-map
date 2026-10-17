# Literature51 targeted follow-up — 16 October UTC / 17 October 2026 Shanghai

The completed 38-import/13-HOLD batch was the starting point. This follow-up releases **B03 only**, finalizes **E17 taxonomy only**, and preserves the original plan, receipts, reports, all 38 imported bibliographic rows, and all 130 pre-existing untracked files. No broad discovery, original import replay, full-suite run, staging, commit or push occurred.

## Counts

| Measure | Original batch baseline | Completed batch | Follow-up |
| --- | ---: | ---: | ---: |
| Candidates | 51 | 51 | 51 |
| Imported / held / unexplained | Unassessed | 38 / 13 / 0 | **39 / 12 / 0** |
| Public bibliography | 639 | 677 | **678** |
| Formally published | 531 | 561 | **561** |
| Curated papers | 496 | 534 | 535 |
| Taxonomy rows | 683 | 721 | 722 |
| Imported taxonomy needs_review | — | 15 | **14** |
| Mapped unique papers | 617 | 617 | 617 |
| Map relationships | 1,421 | 1,421 | **1,421** |

Publication types now: 401 conference, 159 journal, 117 preprint, 1 book. The 684 institution/site markers and 567 mapped institutional identities are unchanged. B03 has no marker; all author affiliation mappings remain unresolved. Its manuscript affiliation groups are retained verbatim as source wording in the follow-up review without creating or merging institution identities.

## B03 identity and publication decision

One identity: `arXiv:2511.20722`, imported as `curated:d2d715db72fca20ad5c4`. The citation year is **2025**, its first public arXiv release; v2 is a July 2026 revision. The earlier title “DinoLizer: Learning from the Best for Generative Inpainting Localization” is retained as an alias. The current title is “DinoLizer: Separating VAE and Diffusion Artifacts in Generative Inpainting Localization”.

- v1 (2025-11-25) order: Minh Thong Doi; Jan Butora; Vincent Itier; Jérémie Boulanger; Patrick Bas.
- v2 (2026-07-30) controlling manuscript order: **Minh Thong Doi; Vincent Itier; Jan Butora; Jérémie Boulanger; Patrick Bas**.
- Current HAL API explicitly identifies `hal-05377107v2` and the same v2 author order. The apparent discrepancy is version-specific; no conflicting author-order merge was forced.
- WIFS 2026 paper 137 is accepted only. No WIFS proceedings DOI or formally published conference record is claimed. The source is represented faithfully as an **arXiv preprint**.
- Experimental inpainting masks and IoU support `localization / generative_editing / method`. No generator-attribution output is claimed.
- The original B03 HOLD row remains untouched. A new linked `add_paper` event supersedes only its disposition. A01 and A13 remain imported, with their earlier HOLD rows and linked resolutions unchanged.

Primary evidence: [arXiv v2 manuscript](https://arxiv.org/html/2511.20722v2), [v1 record](https://arxiv.org/abs/2511.20722v1), [HAL](https://hal.science/hal-05377107v2), [WIFS program](https://wifs2026.utt.fr/technical-program). Exact response hashes and version metadata are in the new raw follow-up retrieval manifest. Full manuscript inspection copies were not added to the repository.

## Remaining HOLDs

No additional identity is silently dropped. The following twelve are held; author-order progress is preserved independently of the remaining gates.

| ID | Exact candidate title | Remaining blocker / precise release action |
| --- | --- | --- |
| B01 | FARE: Forensic Acceptance Region Estimation for Catching Bait-and-Switch Image Generators | Existing NeurIPS migration lock: accepted paper has no verified supported official conference track. No duplicate preprint bypass is permitted.  |
| C01 | CAPN-Net: Category-Agnostic and Patch Noise Feature Fusion Network for Universal AI-Generated Image Detection | Publisher-deposited registration and saved publisher XML provide an assigned future issue/cover date, not an actual online publication date. The targeted publisher landing page still returns HTTP 403; no stronger online-first evidence was found. DOI creation, acceptance and cover dates cannot substitute for release. Capture a primary publisher available-online/published-online date/status tied to this exact DOI, preserving the assigned issue date separately. |
| C02 | Gradient-Guided Up-Sampling Artifacts-Aware Adapter Tuning for Generalizable AI-Generated Image Detection | Publisher-deposited registration and saved publisher XML provide an assigned future issue/cover date, not an actual online publication date. The targeted publisher landing page still returns HTTP 403; no stronger online-first evidence was found. DOI creation, acceptance and cover dates cannot substitute for release. Capture a primary publisher available-online/published-online date/status tied to this exact DOI, preserving the assigned issue date separately. |
| C03 | MFF-Net: Multi-View Feature Fusion Network for AI-Generated Image Detection | Publisher-deposited registration and saved publisher XML provide an assigned future issue/cover date, not an actual online publication date. The targeted publisher landing page still returns HTTP 403; no stronger online-first evidence was found. DOI creation, acceptance and cover dates cannot substitute for release. Capture a primary publisher available-online/published-online date/status tied to this exact DOI, preserving the assigned issue date separately. |
| E01 | Training-Free Detection of AI-Generated Images Based on Coherence Analysis of Image Representations | Actual registered online release is scheduled for 2026-11-14, after this 2026-10-16 review; print 2026-11-15. Acceptance and the article DOI do not establish present formal publication.  |
| E04 | AIGen4Det: Leveraging AI-Regeneration for Generalizable Synthetic Facial Image Detection | Official workshop program now verifies the ordered roster and presentation. OpenReview forum, PDF and API are inaccessible; no exact primary manuscript/version or supported formal/preprint publication state was verified. Technical evidence for passive image experiments remains unavailable. Do not import from social-media descriptions. Obtain the matching public primary manuscript, verify experiments and version, and establish a supported publication state; retain this official author order unless the manuscript establishes a revision. |
| E06 | Depth Spectral Fingerprints: AI-Generated Image Detection via Compact Depth Representations | Publisher-deposited registration and saved publisher XML provide an assigned future issue/cover date, not an actual online publication date. The targeted publisher landing page still returns HTTP 403; no stronger online-first evidence was found. DOI creation, acceptance and cover dates cannot substitute for release. Primary technical evidence of passive depth-based image detection also remains insufficient. Capture a primary publisher available-online/published-online date/status tied to this exact DOI, preserving the assigned issue date separately. Inspect the primary abstract/experiments to establish passive detection. |
| E07 | Can Pixels Alone Reveal Image Origin? Minimax Limits and Learnable Interfaces for Passive Provenance | Existing NeurIPS migration lock: accepted paper has no verified supported official conference track. Retain source_attribution/analysis_study and do not create a preprint duplicate.  |
| E09 | Forged Image Model Attribution Based on Hierarchical Fine-Grained Classification | The supplied abstract describes generative-model, architecture-level and model-level fingerprints, making generator attribution plausible. The IEEE original experiment section and author manuscript could not be accessed; no named synthetic generators/datasets or generator-label evaluation were inspected. Bibliography is complete; the remaining blocker is experimental scope evidence, not a missing DOI or author. Inspect the original experiment section showing named image synthesis architectures/model instances and attribution labels; import as source_attribution if confirmed. Otherwise retain or exclude with direct scope evidence. |
| E13 | RFF-Net: Robust Frequency–Noise Fusion Network for AI-Generated Image Discrimination | Publisher-deposited registration and saved publisher XML provide an assigned future issue/cover date, not an actual online publication date. The targeted publisher landing page still returns HTTP 403; no stronger online-first evidence was found. DOI creation, acceptance and cover dates cannot substitute for release. Capture a primary publisher available-online/published-online date/status tied to this exact DOI, preserving the assigned issue date separately. |
| E15 | Hyperparameter-Aware Evaluation of Deep Learning Architectures for AI-Generated Image Detection | Only an institution acceptance listing with initials was verified. Complete primary ordered author identity and a representable released publication state remain unsupported; do not reconstruct full names from acknowledgments.  |
| E18 | Latent Optimization Dynamics for Latent Diffusion Model Attribution | Official workshop program resolves order and Dahlgren spelling and verifies workshop presentation. Repository README establishes a VAE detector but supplies no manuscript or version. OpenReview forum/PDF/API remain inaccessible. The related single-author thesis has a different title and is not proof of the two-author workshop paper identity or publication status. No generator-ID experiment was verified. Obtain the exact two-author primary manuscript/version and supported publication state. Classify as detection; add attribution only after inspecting generator identity prediction experiments. |

E04 official program order: **Andrea Ciamarra; Stefano Berretti; Alberto Del Bimbo; Roberto Caldelli**. E18 official program order: **Martin Dahlgren; Abu Naser Masud**. These come from the [organizer’s program](https://warwick.ac.uk/fac/sci/dcs/research/siplab/AI4MFDD2026/program/), never social-media acknowledgments. The related Dahlgren bachelor thesis is not substituted for the two-author workshop record. Presentation does not establish exact manuscript version or formally released proceedings.

C01/C02/C03/E06/E13 each received one direct publisher-page follow-up. All five returned HTTP 403; the existing XML/registration provides cover/issue dates only. No repeated DOI-registration-date inference was used. E01 remains before its scheduled November 14 online release. B01 and E07 retain their existing NeurIPS migration locks. E15 remains unsupported by a complete original author roster.

## Fifteen taxonomy reviews

| ID | Follow-up outcome |
| --- | --- |
| A02 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| A05 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| A09 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| A10 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| A11 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| A12 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| A14 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| A19 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| D06 | needs_review — The existing primary abstract and targeted manuscript sections 4.1.1 and 5 describe Real/Fully Synthetic/Tampered classes on SID-Set. They do not disaggregate generative edits from conventional local manipulation. Retain the explicit image_scopes review for generative_editing; do not infer localization or attribution. |
| E08 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| E10 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| E11 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| E14 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| E16 | needs_review — Existing primary captures provide bibliographic identity/title only, not a technical abstract or experiments sufficient to confirm all proposed dimensions. Preserve labels and explicit pending reasons; no title-based promotion. |
| E17 | reviewed — The saved CVF primary abstract describes real-versus-synthetic classification, evaluation against unseen image generators, learnable artifact embeddings and contrastive loss. This supports detection / fully_generated / method. Generator-specific feature training is not experimental evidence of an attribution output. All labels remain unchanged. |

E17’s saved CVF abstract was already sufficient; its technical labels remain `detection / fully_generated / method`. Its generator-specific embedding training does not establish generator-ID prediction. D06’s manuscript still combines synthetic and tampered classes without disaggregating generative edits from conventional manipulation; its generative-editing review remains explicit. No uncertain task labels were changed. The original addition-time audit remains an immutable historical checkpoint; the new review is the effective successor.

## All 257 original new files

Each file has a category, exact path, starting/current SHA-256, byte size, proposed staging decision and reason in [file_audit.csv](../data/processed/literature51_2026_10_16/followup/file_audit.csv).

| Category | Files |
| --- | ---: |
| Required production artifact | 0 |
| Required reproducibility/test artifact | 77 |
| Review/audit documentation | 8 |
| Temporary retrieval cache or unnecessary intermediate | 172 |
| **Total** | **257** |

The production data changes are existing tracked CSV/JSON files, hence zero production files in this *new-file* cohort. The proposal includes **85/257** and leaves **172/257** local-only. No raw evidence or intermediate was deleted.

- Preserve all 54 necessary original bibliographic/technical response captures, the consolidated 120-reference source manifest, original reviewed plan/decisions, exact predecessor fixtures, and baseline/final JUnit XML. These support repository-specific offline tests and history checks.
- Exclude 120 redundant per-URL JSON files (the consolidated manifest contains their entries), 34 non-evidence response bodies, 14 broad retrieval logs, and four unnecessary processed intermediates. The 34 bodies comprise 20 bot/access challenges and 14 publisher redirects.
- Those non-evidence responses contain transient WAF/redirect keys and, in 15 bodies, a request IP. No account credential, Authorization header, private key or authenticated login cookie was identified. Their payloads are excluded; only URL/status/hash/disposition metadata remains in the proposed commit.
- No paper PDF/full-manuscript HTML was found in the 88 original compressed responses. Six unstructured retrieval logs include Introduction/References sections and may contain extended copyrighted article text. All fourteen broad retrieval logs remain local. The [compact evidence index](../data/processed/literature51_2026_10_16/followup/evidence_index.json) retains authored factual adjudications, primary URLs and original capture hashes instead of copying those logs.
- Mandatory primary metadata bodies still fail hash/missing-file checks. Non-evidence bodies present locally still fail on hash drift. The compact-cache regression proves identical extracted metadata with the 34 non-evidence bodies and 120 per-URL JSON files absent; it also proves that deleting a required bibliographic body fails.
- Original ignored test logs remain local, with hashes in the original validation receipt; saved baseline/full XML remains in the proposed staging set. The 130 pre-existing untracked files are preserved and excluded from this proposal. Repository-wide historical workspace checks still expect that pre-existing local evidence; this staging proposal does not absorb unrelated unfinished work.

## Validation and drift

- **55 distinct focused tests passed**, plus **12 passing subtests**. Initial run: 53 passed / 2 missing-Node skips. The six-test browser file then passed with bundled Node, resolving both skips; four cases overlap. The latest nine follow-up tests also passed after sealing the compact evidence index.
- Curated validator: **0 errors, 0 duplicate candidates, 291 warnings** (one more unresolved-affiliation warning). Public map: **0 errors / 0 warnings**. Public bibliography: **0 errors / 62 warnings** (one more unresolved-affiliation paper).
- No full suite rerun. The original **1,701 passed / 4 failed** checkpoint is retained. All four saved final failure names and messages match the pre-existing baseline XML. No frontend snapshot was changed.
- All 38 previous imported paper rows and all 70 previous review rows are unchanged. Taxonomy changes are confined to E17 review status/reason/evidence fields and the new B03 row. All labels on the 38 original imports are unchanged.
- **676 of 677** predecessor public objects are exactly unchanged. E17 changes only `taxonomy_status` and `taxonomy_review`; bibliographic, task and affiliation fields remain identical. B03 is the one new object.
- All **1,421 map relationship objects and their order** are unchanged. The map JSON diff is the shared export timestamp only. No institution, mapping, coordinates, exclusions, geocoding cache, manual file, canonical validator, taxonomy policy, frontend source or historical receipt was edited.
- Count expectations changed only for the new reviewed paper: public 677→678; preprints 116→117; no-map 60→61; localization 43→44. B03 is added to the explicit unresolved-affiliation set. No assertion was removed or relaxed to hide an invalid record. Original historical-test boundaries and old 38/13 receipts remain intact; successor checks verify the approved overlay.
- HEAD is `9e7666169cba098f62f022b7f9f60cdf7c7c72e1`; index is empty. No commit or push.

## Exact changed files since this request

These nine existing working-tree files changed; all other pre-existing files are preserved:

- `data/curated/paper_taxonomy.csv`
- `data/curated/papers.csv`
- `data/curated/review_decisions.csv`
- `docs/key_paper_coverage_report.md`
- `scripts/collect_literature51_sources.py`
- `scripts/integrate_literature51_2026_10_16.py`
- `tests/baseline_expectations.py`
- `web/data/public_preview_map_data.json`
- `web/data/public_preview_papers.json`

New follow-up files (including local-only ignored logs):

- `data/processed/literature51_2026_10_16/followup/baseline.json`
- `data/processed/literature51_2026_10_16/followup/browser.log` — local-only log
- `data/processed/literature51_2026_10_16/followup/browser.xml`
- `data/processed/literature51_2026_10_16/followup/cache_policy.json`
- `data/processed/literature51_2026_10_16/followup/curated_validation.log` — local-only log
- `data/processed/literature51_2026_10_16/followup/evidence_index.json`
- `data/processed/literature51_2026_10_16/followup/file_audit.csv`
- `data/processed/literature51_2026_10_16/followup/file_audit_summary.json`
- `data/processed/literature51_2026_10_16/followup/focused.log` — local-only log
- `data/processed/literature51_2026_10_16/followup/focused.xml`
- `data/processed/literature51_2026_10_16/followup/followup_final.log` — local-only log
- `data/processed/literature51_2026_10_16/followup/followup_final.xml`
- `data/processed/literature51_2026_10_16/followup/proposed_staging.txt`
- `data/processed/literature51_2026_10_16/followup/public_papers.before.gz`
- `data/processed/literature51_2026_10_16/followup/public_validation.log` — local-only log
- `data/processed/literature51_2026_10_16/followup/receipt.json`
- `data/processed/literature51_2026_10_16/followup/review.json`
- `data/processed/literature51_2026_10_16/followup/validation.json`
- `data/processed/literature51_2026_10_16/followup/workspace_integrity.json`
- `data/raw/literature51_2026_10_16/followup/arxiv_v1.html.gz`
- `data/raw/literature51_2026_10_16/followup/arxiv_v2.html.gz`
- `data/raw/literature51_2026_10_16/followup/hal_v2.json`
- `data/raw/literature51_2026_10_16/followup/retrieval_manifest.json`
- `data/raw/literature51_2026_10_16/followup/workshop_program.html.gz`
- `docs/literature51_followup_2026_10_17.md`
- `scripts/reassess_literature51_2026_10_16.py`
- `tests/test_literature51_followup.py`

All modified tracked files versus HEAD (includes the completed integration):

- `data/curated/paper_taxonomy.csv`
- `data/curated/papers.csv`
- `data/curated/review_decisions.csv`
- `data/curated/venue_aliases.csv`
- `docs/key_paper_coverage_report.md`
- `tests/baseline_expectations.py`
- `tests/test_corpus_quality_batch_a.py`
- `tests/test_corpus_quality_batch_c_phase1.py`
- `tests/test_corpus_quality_batch_c_wave1.py`
- `tests/test_corpus_quality_batch_c_wave2.py`
- `tests/test_corpus_quality_batch_c_wave3a.py`
- `tests/test_corpus_quality_batch_c_wave3b2.py`
- `tests/test_corpus_quality_batch_c_wave4a.py`
- `tests/test_corpus_quality_batch_c_wave5a.py`
- `tests/test_frontend_published_only_filter.py`
- `tests/test_paper_metadata_consistency_audit.py`
- `tests/test_repository_baseline.py`
- `web/data/public_preview_map_data.json`
- `web/data/public_preview_papers.json`

## Exact proposed staging set

**126 paths**, enumerated without wildcards in [proposed_staging.txt](../data/processed/literature51_2026_10_16/followup/proposed_staging.txt). This includes 19 modified tracked files, 85 original new files, and 22 new follow-up files. No staging command was executed.

The file is suitable for later explicit review with `git add --pathspec-from-file=data/processed/literature51_2026_10_16/followup/proposed_staging.txt`. It excludes every local-only capture/log and all 130 pre-existing untracked paths. It retains the test predecessor fixtures and mandatory primary source bodies rather than weakening their checks.

For the exact path/hash inventory and preserved-workspace assertions, see [workspace_integrity.json](../data/processed/literature51_2026_10_16/followup/workspace_integrity.json). Validation receipt: [validation.json](../data/processed/literature51_2026_10_16/followup/validation.json). Original report remains [unchanged](literature51_integration_2026_10_16.md).

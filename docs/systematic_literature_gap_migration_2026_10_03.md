# Approved 17-paper systematic gap migration — 2026-10-03

The maintainer-approved migration is applied. Discovery was not restarted. All 17 approved works remained absent during the immediate pre-write identity checks and were added once; none was converted to an existing-identity update. All 12 approved metadata changes preserve their existing paper IDs. The frozen NeurIPS work remains separate.

## Corpus counts

Corpus counts come from the authoritative public export. Taxonomy counts were recomputed by clearing the exported labels and joining the authoritative before/after registries to all 623/640 public identities; the 43 actively excluded historical rows are retained in both registries but omitted from these public-corpus counts. Task and research-type counts are multi-valued and non-exclusive.

| Measure | Before | After | Delta |
| --- | ---: | ---: | ---: |
| Public papers | 623 | 640 | +17 |
| Formally published | 514 | 529 | +15 |
| Mapped papers | 602 | 617 | +15 |
| Map relationship rows | 1,392 | 1,423 | +31 |
| detection | 580 | 593 | +13 |
| source_attribution | 79 | 84 | +5 |
| localization | 36 | 38 | +2 |
| method | 534 | 548 | +14 |
| dataset | 128 | 130 | +2 |
| benchmark | 80 | 83 | +3 |
| survey | 19 | 20 | +1 |
| analysis_study | 72 | 74 | +2 |

The formal-publication increase is 12 new formal works plus three existing preprints upgraded to formal publication (OmniAID, TranX-Adapter and Fleet). The other nine metadata updates were already formally published. Five new works remain preprints, including both attribution challenge reports. Publication-type totals are 388 conference, 140 journal, 111 preprint and one book.

## All 17 additions and affiliation outcomes

FULLY_MAPPED means every verified institution relation has a map marker. PARTIALLY_MAPPED means some verified institutions lack coordinates; it does not imply missing author affiliations. UNMAPPED means the paper has no plotted institution.

| Paper / primary publication | Map status | Verified institutions | Unresolved affiliation or location issue |
| --- | --- | --- | --- |
| [Where Detectors Fail: Probing Generative Space for Generalizable AI-Generated Image Detection](https://proceedings.mlr.press/v306/cao26s.html) | `PARTIALLY_MAPPED` | 4: Australian National University; Peng Cheng Laboratory; Sun Yat-sen University; Tsinghua Shenzhen International Graduate School | Coordinates unresolved: Peng Cheng Laboratory |
| [DNA: Uncovering Universal Latent Forgery Knowledge](https://proceedings.mlr.press/v306/dou26b.html) | `FULLY_MAPPED` | 4: National University of Singapore; The Hong Kong Polytechnic University; The University of Sydney; Xiamen University | None |
| [Deep Residual Injection for Full-Spectrum Forensic Signal Perception in Multimodal Large Language Models](https://proceedings.mlr.press/v306/lin26an.html) | `FULLY_MAPPED` | 4: Fudan University; Peking University; Shenzhen University; Tencent Youtu Lab | None |
| [PRPO: Paragraph-Level Policy Optimization for Vision-Language Deepfake Detection](https://proceedings.mlr.press/v306/nguyen26f.html) | `PARTIALLY_MAPPED` | 2: New Jersey Institute of Technology; Qatar Computing Research Institute | Coordinates unresolved: Qatar Computing Research Institute |
| [RA-Det: Towards Universal Detection of AI-Generated Images via Robustness Asymmetry](https://proceedings.mlr.press/v306/wang26ad.html) | `FULLY_MAPPED` | 2: Fudan University; Jiangnan University | None |
| [Order Within Chaos: Capturing Intrinsic Energy Anomalies for AI-Manipulated Image Forgery Localization](https://proceedings.mlr.press/v306/wang26iy.html) | `FULLY_MAPPED` | 1: Zhejiang University | None |
| [Supervised Contrastive Learning for Few-Shot AI-Generated Image Detection and Attribution](https://arxiv.org/abs/2511.16541) | `FULLY_MAPPED` | 1: Technical University of Madrid | None |
| [Learning Continuous Source Responses for Generalizable AI-Generated Image Detection](https://arxiv.org/abs/2609.14316) | `FULLY_MAPPED` | 4: Ant Group; Huazhong University of Science and Technology; Institute of Automation, Chinese Academy of Sciences; Jilin University | None |
| [A Multi-View and Confusion-Guided Ensemble Framework for Robust Synthetic Image Attribution](https://arxiv.org/abs/2609.11188) | `UNMAPPED` | 1: China Southern Power Grid Electric Power Research Institute | Coordinates unresolved: China Southern Power Grid Electric Power Research Institute |
| [Hybrid Semantic and Spectral Ensemble for Robust Synthetic Image Source Attribution](https://arxiv.org/abs/2607.22808) | `FULLY_MAPPED` | 1: Chittagong University of Engineering and Technology | None |
| [Beyond Spectral Peaks: Interpreting the Cues Behind Synthetic Image Detection](https://www.cmsworkshops.com/ICASSP2026/view_paper.php?PaperNum=13550&bare=1) | `FULLY_MAPPED` | 2: Politecnico di Milano; University of Vigo | None |
| [EditTrack: Detecting and Attributing AI-Assisted Image Editing](https://arxiv.org/abs/2510.01173) | `FULLY_MAPPED` | 1: Duke University | None |
| [A Comprehensive Survey on Visual Forensics for AI-Generated Image Detection](https://doi.org/10.11834/jig.250624) | `FULLY_MAPPED` | 1: Chinese People's Armed Police Force Engineering University | None |
| [Synthetic Images at MediaEval 2025: Advancing Detection of Generative AI in Real-World Online Images](https://2025.multimediaeval.com/paper47.pdf) | `PARTIALLY_MAPPED` | 5: Centre for Research and Technology Hellas; Ghent University; University of Amsterdam; University of Naples Federico II; imec | Coordinates unresolved: Ghent University; imec |
| [ViGText: Deepfake Image Detection with Vision-Language Model Explanations and Graph Neural Networks](https://doi.org/10.14722/ndss.2026.230303) | `PARTIALLY_MAPPED` | 3: New Jersey Institute of Technology; Old Dominion University; Qatar Computing Research Institute | Coordinates unresolved: Qatar Computing Research Institute |
| [AdaParse: Personalized Fingerprinting for Visual Generative Model Reverse Engineering](https://doi.org/10.1109/tifs.2026.3671095) | `FULLY_MAPPED` | 1: Tsinghua University | None |
| [Beyond Visual Forensics: Auditing Multimodal Robustness for Synthetic Medical Image Detection](https://papers.miccai.org/miccai-2026/0103-Paper2865.html) | `UNMAPPED` | 0: None verified | Ten paper-time affiliations unresolved; official PDF returned an interstitial |

**11 fully mapped, four partially mapped, two unmapped.** The mapped-paper increase is therefore exactly 15. Affiliation evidence is verified for 16 works, but one of those has no verified coordinates.

Partial map coverage:

- PROBE / Where Detectors Fail: 7 authors, all 7 have verified institution relations, 0 unresolved. Peng Cheng Laboratory lacks coordinates.
- PRPO: 5 authors, all 5 verified, 0 unresolved. Qatar Computing Research Institute (QCRI) lacks coordinates.
- MediaEval: 10 authors, all 10 verified, 0 unresolved. Ghent University and imec lack coordinates; both affiliations remain separate.
- ViGText: 5 authors, all 5 verified, 0 unresolved. QCRI lacks coordinates.

Unmapped papers:

- **A Multi-View and Confusion-Guided Ensemble Framework for Robust Synthetic Image Attribution**: sole author Zuomin Qu has a paper-time affiliation with China Southern Power Grid Electric Power Research Institute. The institution is retained, but its city/coordinates are unverified; no marker was invented.
- **MICCAI Beyond Visual Forensics**: all ten author names are verified, while all ten paper-time affiliations remain unresolved. The official PDF endpoint returned an HTML interstitial; HTTP 200 was not treated as a usable PDF. The paper remains public and each author has an unresolved review event. No institution relationship was fabricated.

Affiliation evidence is recorded in `affiliation_review.json`, `affiliation_pdf_text.json`, `prior_source_references.json`, the original cached sources, and each curated mapping’s `provenance_source` and `raw_affiliation`. Supervised Contrastive Learning retains the official metadata author order, with the different shared PDF-block order recorded as a source note. The confirmed UPM alias is reused without merging institution identities. Three new coordinate records have institution-specific ROR/Wikidata evidence; no city-centroid fallback was introduced. QCRI remains an institution with a reviewed HBKU parent link, rather than being substituted by its parent.

## Relationships and institution integrity

The actual export contains **1,392 → 1,423 relationship rows**, a net increase of 31. All 31 new map rows trace to the 37 new paper-time institution mappings; six verified mappings remain unplotted. The new mappings contain 102 distinct author–institution links. New duplicate paper–institution pairs = 0; new duplicate author–institution links = 0. The institution alias registry is unchanged. Six new institutions, three supported locations and one parent relation were added.

A pre-existing overlap is preserved: *Detection, Attribution and Localization of GAN Generated Images* has two UCSB map rows with different author sets, with Michael Goebel present in both. Both rows are identical to the pre-migration records. Thus strictly unique paper–institution pairs are **1,391 → 1,422**, while the repository’s exported relationship-row measure is **1,392 → 1,423**. The established validator accepts the distinct author-set rows. This unrelated historical overlap was not silently merged. See `relationship_verification.json`.

## All 12 metadata updates

The table records the actual curated before/after values. arXiv IDs are preserved; previous publication links remain in metadata provenance. Canonical formal URLs use the existing DOI/publisher precedence. No update creates a paper identity.

| Work | Existing paper ID | Publication type before → after | Formal publisher / proceedings URL | DOI after |
| --- | --- | --- | --- | --- |
| OmniAID: Decoupling Semantics and Artifacts for Universal AI-Generated Image Detection in the Wild | `curated:d8667aa1db5ef69d199a` | preprint → conference | [Primary publication](https://proceedings.mlr.press/v306/guo26ag.html) | not independently verified |
| Dissect and Prune: Enhancing Robustness in AI-Generated Image Detection | `curated:c87f234ea256991903e1` | conference → conference | [Primary publication](https://proceedings.mlr.press/v306/kim26k.html) | not independently verified |
| TranX-Adapter: Bridging Artifacts and Semantics Within MLLMs for Robust AI-Generated Image Detection | `curated:3514b00c17a56ec752cd` | preprint → conference | [Primary publication](https://proceedings.mlr.press/v306/wang26cj.html) | not independently verified |
| Fleet: Few Shots Lead Effective AI-Generated Image Detection | `curated:f8bc8386ea043eef0a7c` | preprint → conference | [Primary publication](https://proceedings.mlr.press/v306/wang26eo.html) | not independently verified |
| Breaking Manifold Continuity: Vector Quantized Modeling for Real-Centric Deepfake Detection | `curated:7287cadbc4b8408fd16b` | conference → conference | [Primary publication](https://proceedings.mlr.press/v306/wang26it.html) | not independently verified |
| GenShield: Unified Detection and Artifact Correction for AI-Generated Images | `curated:d6fe2666a64b0c70ff6b` | conference → conference | [Primary publication](https://proceedings.mlr.press/v306/xu26cl.html) | not independently verified |
| DGS-Net: Distillation-Guided Gradient Surgery for CLIP Fine-Tuning in AI-Generated Image Detection | `curated:7ed4e932c4dac57d0136` | conference → conference | [Primary publication](https://proceedings.mlr.press/v306/yan26h.html) | not independently verified |
| FiSeR: Fine-Grained Source Representations for Cross-Domain AI Image Detection | `curated:f380c0d31081fc59f1eb` | conference → conference | [Primary publication](https://proceedings.mlr.press/v306/zhang26bi.html) | not independently verified |
| PGC: Peak-Guided Calibration for Generalizable AI-Generated Image Detection | `curated:a570863c3a6ac227b56c` | conference → conference | [Primary publication](https://proceedings.mlr.press/v306/zhou26h.html) | not independently verified |
| ForensicConcept: Transferable Forensic Concepts for AIGI Detection | `curated:078ade9edabe304013a7` | conference → conference | [Primary publication](https://proceedings.mlr.press/v306/zhou26bt.html) | not independently verified |
| Position: We Need to Re-Think the Concept of "Real" Images. | `curated:b45849aa3f89cc8b64ef` | conference → conference | [Primary publication](https://proceedings.mlr.press/v306/keuper26a.html) | not independently verified |
| Fast and Generalizable AI-Generated Image Detection via Model-Agnostic Feature Reconstruction | `curated:773aa77291d6869eaad8` | conference → conference | [Primary publication](https://www.ijcai.org/proceedings/2026/131) | 10.24963/ijcai.2026/131 |

**12/12 METADATA UPDATES APPLIED.** The IJCAI GFRE record has DOI `10.24963/ijcai.2026/131`. ICML records use volume 306 PMLR proceedings links; superseded OpenReview URLs survive in provenance where previously present. Three updated titles were corrected through the existing canonical title normalizer after full-suite validation detected inconsistent casing; the repair is logged in `title_normalization_repairs.json`. No identifiers, original evidence or author affiliations were changed by that normalization.

## Maintainer decisions

The original audit statuses, source evidence, occurrence records and counts remain preserved. New `maintainer_decision` and `migration_outcome` fields are a successor layer, not a rewrite of discovery results. The pre-decision ledger is in `discovery_snapshot.json`.

| Former Set B / ambiguous lead | Final decision |
| --- | --- |
| PRPO | Added: detection method and dataset; independent fully generated image evaluation |
| Multi-View and Confusion-Guided Ensemble | Added: source attribution method; remains preprint |
| Hybrid Semantic and Spectral Ensemble | Added: source attribution method; remains preprint |
| AdaParse | Added: passive generator-hyperparameter reverse engineering / source attribution |
| Beyond Visual Forensics | Added: synthetic medical image authenticity benchmark and analysis, generative editing scope |
| SICA | Excluded under the narrow corpus policy; broad multi-domain framework |
| OmniVL-Guard | Excluded: interleaved multimodal misinformation lacks an independently central synthetic-image forensic contribution |
| Forensic Prompting | Excluded: generic manipulation framework with insufficient generative-image dominance |
| Chimera | Excluded: counter-forensic evasion and provenance circumvention |
| DiCoME | Hold: insufficient independent synthetic-image scope evidence; not permanently excluded |
| AI-Generated Image Detection: An Empirical Study and Future Research Directions | Ambiguous identity; arXiv 2511.02791 and SSRN 6032054 both retained, no corpus identity created |
| BM-DDFN; SCA-Det; Spectral Forensics; Proto-LeakNet | Evidence-insufficient holds; original ambiguous states retained |

Four permanent exclusions and ten non-add review decisions are represented in the curated review layer. The 17 approved additions and all 27 maintainer decisions are represented in the audit layer.

## Validation and reproducibility

| Requested group | Passed | Failed | Warnings | Additional passed subtests |
| --- | ---: | ---: | ---: | ---: |
| Migration / audit | 26 | 0 | 0 | 0 |
| Paper / taxonomy / deduplication / metadata / sync | 93 | 0 | 0 | 6 |
| Affiliation / institution / location | 59 | 0 | 0 | 8 |
| Publication / review | 34 | 0 | 0 | 0 |
| Current baseline / historical integrity | 29 | 0 | 2 | 12 |
| **Targeted total** | **241** | **0** | **2** | **26** |

All five groups were rerun after the final code/data repairs and passed before the final full-suite run. Two supplementary failure-resolution groups also passed (83 and 30 tests).

**Final full suite: 1,577 passed, 0 failed, 0 skipped, 2 warnings; 389 additional passed subtests; 277.41 seconds.** The two inherited `PytestReturnNotNoneWarning` messages come from `test_successor_migration_payload` and `test_successor_migration_text`, which return a dict and string. They are reported, not suppressed. Results are in `test_results.json` and `full_suite.xml`.

The initial full-suite failures are preserved in `full_suite_initial.xml` and classified in `initial_full_suite_triage.json`: missing Node runtime setup, stale current counts, stale pre-existing homepage cache expectations, historical snapshot isolation, and the three-title normalization defect. The Node runtime was exposed on PATH without installing project dependencies. No tests were disabled to obtain a pass.

Historical 623-paper inputs are gzip archives checked against the saved pre-migration hashes on every read. Completed historical reports still validate the original 623/666 predecessor layers. Current state is independently checked by the exact approved-delta migration validator and current repository tests. The old public-refinement fixture remains unchanged; a separate checksum-verified receipt records the homepage branding already committed before this migration. The historical venue artifact is replayed against the predecessor, while current venue/admin/public consistency is checked independently.

Curated database validation: **0 errors, 250 warnings, 0 duplicate candidates**. The predecessor has 245 warnings. Five added warnings are intentional: four permanent exclusion rows have no fabricated paper ID and match by their supported alternate identity; the MICCAI paper has no verified author–institution mapping. All other warning messages are inherited. Public validation: **0 errors, 0 map warnings, 23 paper warnings** (22 inherited plus the MICCAI unresolved affiliation warning). Normal validation passes; strict warning-free validation does not.

Identity checks: duplicate DOI = 0; duplicate arXiv identity = 0; duplicate normalized canonical title = 0. The established publication-family and confirmed-version-merge checks report no unintended duplicate leakage. DNA remains distinct from the existing attribution paper with the same acronym. RA-Det remains distinct from the rejected DRCT enrichment suggestion. No invalid taxonomy tokens were introduced.

## Protected and frozen integrity

- Protected inputs checked: 105.
- EXPECTED_CHANGED: 13 paths — the 11 approved curated CSVs and the two generated public JSON exports.
- UNEXPECTED_CHANGED = 0
- Frozen NeurIPS files checked: 49.
- FROZEN_NEURIPS_CHANGED = 0
- Frozen public MIRROR record: unchanged.
- Existing public records outside the 12 approved metadata updates: unchanged.
- Existing curated rows outside the approved update plan: unchanged; untouched CSV rows retain their original byte representation.
- `data/manual/`: unchanged.

Expected changed protected paths:

- `data/curated/author_institution_mappings.csv`
- `data/curated/institution_audit_log.csv`
- `data/curated/institution_hierarchy.csv`
- `data/curated/institution_location_review.csv`
- `data/curated/institution_locations.csv`
- `data/curated/institutions.csv`
- `data/curated/paper_exclusions.csv`
- `data/curated/paper_taxonomy.csv`
- `data/curated/papers.csv`
- `data/curated/review_decisions.csv`
- `data/curated/venue_aliases.csv`
- `web/data/public_preview_map_data.json`
- `web/data/public_preview_papers.json`

New historical snapshots, source evidence, tests and migration documentation are recorded separately. They are not classified as corpus corruption. Public JSON is generated exclusively by `scripts/export_public_preview.py --preserve-existing`. No frontend or backend implementation change is part of the migration; the site remains static.

**7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA**

## Final Git audit

`git status --short`, `git diff --stat` and `git diff --check` were inspected after validation. The change set contains **29 tracked modifications**: 11 curated CSVs, two generated public exports, one generated coverage report, five historical-input readers, and ten test/expectation files.

There are **204 untracked files**: 116 preserved audit-layer files, 81 migration evidence/snapshot/receipt files, three Python helpers, two regression test files and two reports. The full inventory and classifications are in `git_audit.json`; no unclassified path is present. The structural review covers every public paper and map record, every curated row, all 29 historical archives and all 23 new original-response archives. 5,806 untouched curated rows are byte-identical; 31 map rows were added and 30 prior rows changed only for approved metadata updates.

`git diff --check`: clean. HEAD remains `ecfde6b1fc459a748e34114634fbf21cb9286f65`. No temporary extraction files, cache directories or unrelated source changes are included. The original discovery ledger is identical after removing the separately added decision/outcome fields.

Every changed/untracked path has one category in `git_audit.json`:

| Category | Files |
| --- | ---: |
| curated migration data | 2 |
| taxonomy | 1 |
| author/institution mappings | 4 |
| review decisions | 4 |
| public generated exports | 2 |
| migration/audit evidence | 169 |
| tests | 12 |
| historical pre-migration snapshot | 39 |
| unrelated | 0 |

Only Markdown and validation receipts were completed after the final full-suite run. No source, test or authoritative corpus file changed, so the passing full-suite result remains applicable. Preserved original audit web-search captures are intentional provenance; no accidental search captures were added.

Nothing is staged. No commit or push was performed. Source response archives are deliberate provenance records; scratch extraction files are removed. New test receipts are retained as migration evidence. Existing ignored caches are not included in the change set.

Final outcome: **17-PAPER GAP MIGRATION — COMMIT-READY**

## Commit preparation — explicit allowlist

The preceding Git inventory is the completed pre-commit review checkpoint. The maintainer subsequently authorized exactly one commit, subject `feat: add systematic gap-audit migration`, without pushing. This packaging review changes only Markdown documentation; executable code, tests, curated data and generated exports remain the validated versions.

The commit allowlist contains **105 files: all 29 reviewed tracked modifications and 76 of the 204 individually audited untracked files**. The other **128 files remain local and unstaged**: 115 redundant raw captures, ten local generated/diagnostic receipts and three unusable transient responses. Nothing is deleted. The tables below are the explicit path allowlist; only classifications beginning `COMMIT_` are staged.

The repository already tracks compressed primary evidence and historical fixtures (for example `data/raw/systematic_literature_2026_09/` and the prior migration snapshots). Only four new raw response archives are necessary here: the official PMLR volume index read by publication reconstruction, and three Wikidata institution-coordinate inputs read by migration preparation. All other downloads are represented by stable primary URLs, structured publication/affiliation evidence and source hashes. Search-result bodies and raw web-reader tool responses remain local. No new search was performed.

`source_manifest.json`, original candidate `capture_paths`, and discovery `source_capture` values preserve original local provenance paths even when their bodies are intentionally not committed. Those paths are historical retrieval references, not a promise that every local capture ships in Git. The original audit’s full-capture validation requires those local captures and its original corpus; current migration guards and the checksum-verified historical corpus tests use the committed structured records and predecessor archives.

Compact final validation remains committed in `test_results.json`, `validation.json`, `complete_diff_audit.json` and this report. Verbose test XML, debugging output and earlier workspace inventories remain local. The full-suite baseline is unchanged: 1,577 passed, zero failed, zero skipped, two warnings. Staged-tree counts, exact identity checks, frozen integrity and lightweight migration guards are checked before the single commit.

### Tracked modifications — 29 explicit paths

| Path | Classification | Migration justification |
| --- | --- | --- |
| `data/curated/author_institution_mappings.csv` | `COMMIT_CURATED` | approved curated additions, metadata, taxonomy and review |
| `data/curated/institution_audit_log.csv` | `COMMIT_CURATED` | approved curated additions, metadata, taxonomy and review |
| `data/curated/institution_hierarchy.csv` | `COMMIT_CURATED` | approved curated additions, metadata, taxonomy and review |
| `data/curated/institution_location_review.csv` | `COMMIT_CURATED` | approved curated additions, metadata, taxonomy and review |
| `data/curated/institution_locations.csv` | `COMMIT_CURATED` | approved curated additions, metadata, taxonomy and review |
| `data/curated/institutions.csv` | `COMMIT_CURATED` | approved curated additions, metadata, taxonomy and review |
| `data/curated/paper_exclusions.csv` | `COMMIT_CURATED` | approved curated additions, metadata, taxonomy and review |
| `data/curated/paper_taxonomy.csv` | `COMMIT_CURATED` | approved curated additions, metadata, taxonomy and review |
| `data/curated/papers.csv` | `COMMIT_CURATED` | approved curated additions, metadata, taxonomy and review |
| `data/curated/review_decisions.csv` | `COMMIT_CURATED` | approved curated additions, metadata, taxonomy and review |
| `data/curated/venue_aliases.csv` | `COMMIT_CURATED` | approved curated additions, metadata, taxonomy and review |
| `docs/key_paper_coverage_report.md` | `COMMIT_EVIDENCE` | generated current coverage summary |
| `scripts/frozen_predecessor_666.py` | `COMMIT_HISTORICAL_SNAPSHOT` | historical input isolation |
| `scripts/legacy_scope_exclusion_migration.py` | `COMMIT_HISTORICAL_SNAPSHOT` | historical input isolation |
| `scripts/report_systematic_tier2_application.py` | `COMMIT_HISTORICAL_SNAPSHOT` | historical input isolation |
| `scripts/report_systematic_tier2_normal_priority_evidence.py` | `COMMIT_HISTORICAL_SNAPSHOT` | historical input isolation |
| `scripts/report_systematic_tier2_policy.py` | `COMMIT_HISTORICAL_SNAPSHOT` | historical input isolation |
| `tests/baseline_expectations.py` | `COMMIT_TEST` | current expectations or historical fixture isolation |
| `tests/public_refinement_snapshot.py` | `COMMIT_TEST` | current expectations or historical fixture isolation |
| `tests/test_formal_publication_links.py` | `COMMIT_TEST` | current expectations or historical fixture isolation |
| `tests/test_frontend_published_only_filter.py` | `COMMIT_TEST` | current expectations or historical fixture isolation |
| `tests/test_frontend_result_cards.py` | `COMMIT_TEST` | current expectations or historical fixture isolation |
| `tests/test_manual_location_audit_20260827.py` | `COMMIT_TEST` | current expectations or historical fixture isolation |
| `tests/test_paper_metadata_consistency_audit.py` | `COMMIT_TEST` | current expectations or historical fixture isolation |
| `tests/test_paper_taxonomy_migration.py` | `COMMIT_TEST` | current expectations or historical fixture isolation |
| `tests/test_repository_baseline.py` | `COMMIT_TEST` | current expectations or historical fixture isolation |
| `tests/test_workshop_venue_audit.py` | `COMMIT_TEST` | current expectations or historical fixture isolation |
| `web/data/public_preview_map_data.json` | `COMMIT_EVIDENCE` | existing exporter output |
| `web/data/public_preview_papers.json` | `COMMIT_EVIDENCE` | existing exporter output |

### Untracked inventory — all 204 files

| Path | Classification | Reason |
| --- | --- | --- |
| `data/raw/systematic_gap_audit_2026_10_02/README.md` | `COMMIT_EVIDENCE` | Evidence catalog and local/committed packaging boundary. |
| `data/raw/systematic_gap_audit_2026_10_02/baseline.json` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_audit_2026_10_02/candidates.json` | `COMMIT_EVIDENCE` | Authoritative work decisions and complete original discovery status with separate maintainer successor fields. |
| `data/raw/systematic_gap_audit_2026_10_02/discovery_records.json` | `COMMIT_EVIDENCE` | Structured discovery occurrence ledger: stable URLs, query metadata and decisions, not result-page bodies. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/adaparse_pdf_text.json` | `COMMIT_EVIDENCE` | Primary-source extracted evidence for approved passive attribution and author affiliations. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/bpl_pdf_text.json` | `COMMIT_EVIDENCE` | Extracted primary evidence supporting audit identity/scope adjudication; full PDF omitted. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p01.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p02.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p03.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p04.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p05.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p06.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p07.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p08.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p09.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p10.json` | `TEMPORARY` | Unusable transient/error/interstitial response; retrieval outcome is preserved in structured provenance. Retained locally, not deleted. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p11.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p12.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p13.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p14.json` | `LOCAL_RAW_REDUNDANT` | Raw web-reader response with tool tokens/redundant page content; structured evidence and stable primary URLs are preserved. |
| `data/raw/systematic_gap_audit_2026_10_02/evidence/p15.json` | `TEMPORARY` | Unusable transient/error/interstitial response; retrieval outcome is preserved in structured provenance. Retained locally, not deleted. |
| `data/raw/systematic_gap_audit_2026_10_02/external_changes.json` | `COMMIT_EVIDENCE` | Documents pre-existing branding differences without modifying audit baseline. |
| `data/raw/systematic_gap_audit_2026_10_02/fetch_extra_jobs.json` | `LOCAL_GENERATED` | Superseded retrieval plan, intermediate check, verbose test/validator output, or workspace inventory; compact final evidence is committed. |
| `data/raw/systematic_gap_audit_2026_10_02/fetch_jobs.json` | `LOCAL_GENERATED` | Superseded retrieval plan, intermediate check, verbose test/validator output, or workspace inventory; compact final evidence is committed. |
| `data/raw/systematic_gap_audit_2026_10_02/final_git_audit.json` | `LOCAL_GENERATED` | Superseded retrieval plan, intermediate check, verbose test/validator output, or workspace inventory; compact final evidence is committed. |
| `data/raw/systematic_gap_audit_2026_10_02/icml2026_screening.json` | `COMMIT_EVIDENCE` | Structured proceedings title-screening/count reconciliation required by the audit. |
| `data/raw/systematic_gap_audit_2026_10_02/primary_metadata.json` | `COMMIT_EVIDENCE` | Structured primary publication metadata preserving source authors, abstracts, URLs and identifiers. |
| `data/raw/systematic_gap_audit_2026_10_02/priority_identity_checks.json` | `LOCAL_GENERATED` | Superseded retrieval plan, intermediate check, verbose test/validator output, or workspace inventory; compact final evidence is committed. |
| `data/raw/systematic_gap_audit_2026_10_02/saved_105_checksums.json` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s02.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s03.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s04.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s05.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s06.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s07.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s08.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s09.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s10.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s11.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s12.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s13.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s14.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s15.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s16.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s17.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s18.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s19.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s20.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s21.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s22.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s23.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s24.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s25.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s26.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s27.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s28.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s29.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s30.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s31.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s32.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s33.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s34.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s35.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s36.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s37.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s38.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s39.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s40.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s41.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/s42.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/search/search1.json` | `LOCAL_RAW_REDUNDANT` | Search-engine response body. Structured discovery URLs/query metadata/decisions are committed instead. |
| `data/raw/systematic_gap_audit_2026_10_02/source_coverage.json` | `COMMIT_EVIDENCE` | Reproducible source-family coverage and known discovery limitations. |
| `data/raw/systematic_gap_audit_2026_10_02/source_manifest.json` | `COMMIT_EVIDENCE` | Source URLs, timestamps, content types and hashes; raw captures omitted where redundant/transient. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/051c3d5914447233a502.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/07ae2fe03845e90efc73.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/0c9d75c8d5972bc45b99.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/0d8f525ad77edeeca31a.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/0eae5b4a7b80bf12af72.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/0f57901467d617f93751.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/11fabc988fb3fab919c5.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/14368c4ab7bdeab35ea3.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/159f852178545781233f.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/1cba7ea5b129e2ec3cb2.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/22f620e2c2dd62bfdeb2.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/2d7b6ca1802d6ee49d90.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/34253731a42d856a0e4c.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/524ad6f1ba42aae0a9f3.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/546d7193087adb15c4f1.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/54e776761efd082cb3d2.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/6f4ed920edcc40867457.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/701210428e9ea6004049.gz` | `COMMIT_EVIDENCE` | Official PMLR v306 index: publication_details reads exact pages for approved proceedings records. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/7035461665515d858dc8.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/7a4c82c82ed069574646.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/7df114b7c665207aaae6.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/8ada47029dd8f0b174c4.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/9592abb6f18c8ad21fcf.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/976045a2e78ca6746db5.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/a25f6588cff2ddf4f004.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/a35f640f39dac073b639.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/aa62819cf3e7921f29ac.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/b9197d99543010a07e7b.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/b9d830b2694e009b5b23.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/c07a82c1ae9d34b4a15c.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/c6a0429c0cfeba5793c4.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/cae1a49b2fbbde2c360e.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/cd26ad1627b8f3da0f30.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/d8abce1b847536d125ec.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/dcbffd1f800df14b0719.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/e1786c796da89420a467.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/e2b52e46b1af1f3e33ae.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/e8d510819d0e22d7823b.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/f0a7329c389104ccfb6f.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/f2ae90c9c9a1d82d823d.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/f44fc626846b44fa4906.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/sources/f5021d74419edc6a3859.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_audit_2026_10_02/validation.json` | `COMMIT_EVIDENCE` | Completed historical audit validation receipt. |
| `data/raw/systematic_gap_migration_2026_10_03/README.md` | `COMMIT_EVIDENCE` | Migration evidence catalog and local/committed packaging boundary. |
| `data/raw/systematic_gap_migration_2026_10_03/affiliation_pdf_text.json` | `COMMIT_EVIDENCE` | Paper-page extracts supporting the reviewed author/institution relationships. |
| `data/raw/systematic_gap_migration_2026_10_03/affiliation_review.json` | `COMMIT_EVIDENCE` | Reviewed paper-time affiliations and explicit unresolved MICCAI state. |
| `data/raw/systematic_gap_migration_2026_10_03/approved_candidates.json` | `COMMIT_EVIDENCE` | Exact 17 approved candidate inputs to the reviewed plan. |
| `data/raw/systematic_gap_migration_2026_10_03/baseline.json` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/complete_diff_audit.json` | `COMMIT_EVIDENCE` | Whole-corpus delta, registry-count and provenance integrity receipt. |
| `data/raw/systematic_gap_migration_2026_10_03/curated_validation_after.txt` | `LOCAL_GENERATED` | Superseded retrieval plan, intermediate check, verbose test/validator output, or workspace inventory; compact final evidence is committed. |
| `data/raw/systematic_gap_migration_2026_10_03/curated_validation_before.txt` | `LOCAL_GENERATED` | Superseded retrieval plan, intermediate check, verbose test/validator output, or workspace inventory; compact final evidence is committed. |
| `data/raw/systematic_gap_migration_2026_10_03/discovery_snapshot.json` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/fetch_jobs.json` | `COMMIT_EVIDENCE` | Exact source URLs referenced by migration preparation and affiliation provenance. |
| `data/raw/systematic_gap_migration_2026_10_03/full_suite.xml` | `LOCAL_GENERATED` | Superseded retrieval plan, intermediate check, verbose test/validator output, or workspace inventory; compact final evidence is committed. |
| `data/raw/systematic_gap_migration_2026_10_03/full_suite_initial.xml` | `LOCAL_GENERATED` | Superseded retrieval plan, intermediate check, verbose test/validator output, or workspace inventory; compact final evidence is committed. |
| `data/raw/systematic_gap_migration_2026_10_03/git_audit.json` | `LOCAL_GENERATED` | Superseded retrieval plan, intermediate check, verbose test/validator output, or workspace inventory; compact final evidence is committed. |
| `data/raw/systematic_gap_migration_2026_10_03/initial_full_suite_triage.json` | `LOCAL_GENERATED` | Superseded retrieval plan, intermediate check, verbose test/validator output, or workspace inventory; compact final evidence is committed. |
| `data/raw/systematic_gap_migration_2026_10_03/insertion.json` | `COMMIT_EVIDENCE` | One-time 17-addition/12-update receipt and frozen boundary. |
| `data/raw/systematic_gap_migration_2026_10_03/institution_identity_checks.json` | `COMMIT_EVIDENCE` | Six institution identity adjudications without alias merging. |
| `data/raw/systematic_gap_migration_2026_10_03/live_deduplication.json` | `COMMIT_EVIDENCE` | Seven-layer identity checks immediately before the migration. |
| `data/raw/systematic_gap_migration_2026_10_03/location_evidence.json` | `COMMIT_EVIDENCE` | Structured institution-specific coordinate evidence and source hashes. |
| `data/raw/systematic_gap_migration_2026_10_03/maintainer_decisions.json` | `COMMIT_EVIDENCE` | Explicit maintainer decisions for all additions, exclusions and holds. |
| `data/raw/systematic_gap_migration_2026_10_03/plan.json` | `COMMIT_EVIDENCE` | Exact reviewed additions and identity-preserving row updates; current-delta validation input. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/data/curated/author_institution_mappings.csv.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/data/curated/institution_audit_log.csv.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/data/curated/institution_hierarchy.csv.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/data/curated/institution_location_review.csv.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/data/curated/institution_locations.csv.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/data/curated/institutions.csv.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/data/curated/paper_exclusions.csv.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/data/curated/paper_taxonomy.csv.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/data/curated/papers.csv.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/data/curated/review_decisions.csv.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/data/curated/venue_aliases.csv.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/docs/key_paper_coverage_report.md.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/scripts/frozen_predecessor_666.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/scripts/legacy_scope_exclusion_migration.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/scripts/report_systematic_tier2_application.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/scripts/report_systematic_tier2_normal_priority_evidence.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/scripts/report_systematic_tier2_policy.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/tests/baseline_expectations.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/tests/public_refinement_snapshot.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/tests/test_formal_publication_links.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/tests/test_frontend_published_only_filter.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/tests/test_frontend_result_cards.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/tests/test_manual_location_audit_20260827.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/tests/test_paper_metadata_consistency_audit.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/tests/test_paper_taxonomy_migration.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/tests/test_repository_baseline.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/tests/test_workshop_venue_audit.py.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/web/data/public_preview_map_data.json.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623/web/data/public_preview_papers.json.gz` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/predecessor_623_manifest.json` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/preexisting_branding_snapshot.json` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `data/raw/systematic_gap_migration_2026_10_03/preexport_repairs.json` | `COMMIT_EVIDENCE` | Auditable correction of migration-only unsupported location placeholders. |
| `data/raw/systematic_gap_migration_2026_10_03/prior_source_references.json` | `COMMIT_EVIDENCE` | Stable source URLs/hashes for reused MediaEval and AdaParse evidence. |
| `data/raw/systematic_gap_migration_2026_10_03/relationship_verification.json` | `COMMIT_EVIDENCE` | All new links source-backed; unchanged historical UCSB overlap documented. |
| `data/raw/systematic_gap_migration_2026_10_03/source_manifest.json` | `COMMIT_EVIDENCE` | Original source metadata and hashes; capture-path fields retain local provenance locations. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/05c120058aa769cb54b2.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/06c1e60ff87d4544ebf9.gz` | `TEMPORARY` | Unusable transient/error/interstitial response; retrieval outcome is preserved in structured provenance. Retained locally, not deleted. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/207d525c199521239c15.gz` | `COMMIT_EVIDENCE` | Wikidata institution entity P625: deterministic Old Dominion coordinate evidence. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/23b3e87658f52dc2e825.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/298e571aaa36aff480ec.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/2ea67815bb17f8560a63.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/3a37e3c4c0b088c6492a.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/3c2ad142ba32942d6fe3.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/3d636934fd00fcff46b2.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/3e430a5c102b817594a1.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/3e9d132fc286a8caa51a.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/4f5c9baef9e37c154200.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/5b389f7825eaf5870df9.gz` | `COMMIT_EVIDENCE` | Wikidata institution entity P625: deterministic University of Vigo coordinate evidence. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/677ddbd2cd01bd04be59.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/7e5517ee00e971fad9c6.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/85325afdfb2f84a6863f.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/89cb6b5f2900b992a814.gz` | `COMMIT_EVIDENCE` | Wikidata institution entity P625: deterministic NJIT coordinate evidence. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/9d70acfaca0819eaabd1.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/bf9788aebc1bdddab139.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/dc6d74f70fb57d48c870.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/e439abe166212a6e8a70.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/e9ceafd8b50c2520b4c7.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/sources/ef6cde598d35cce269fa.gz` | `LOCAL_RAW_REDUNDANT` | Full source capture is represented by stable authoritative URLs, structured metadata/affiliation evidence and response hash; no reconstruction code requires these bytes. |
| `data/raw/systematic_gap_migration_2026_10_03/test_results.json` | `COMMIT_EVIDENCE` | Compact final targeted/full-suite and validator receipt; verbose/debug outputs stay local. |
| `data/raw/systematic_gap_migration_2026_10_03/title_normalization_repairs.json` | `COMMIT_EVIDENCE` | Three canonical title corrections and exact affected-row provenance. |
| `data/raw/systematic_gap_migration_2026_10_03/validation.json` | `COMMIT_EVIDENCE` | Final exact delta, counts, affiliation and protected/frozen integrity checks. |
| `docs/systematic_literature_gap_audit_2026_10_02.md` | `COMMIT_EVIDENCE` | Completed audit report and approved successor boundary. |
| `docs/systematic_literature_gap_migration_2026_10_03.md` | `COMMIT_EVIDENCE` | Migration report, validation, limits and explicit commit file audit. |
| `scripts/audit_gap_2026_10_02.py` | `COMMIT_EVIDENCE` | Auditable identity comparison and schema validation implementation. |
| `scripts/gap_migration_history.py` | `COMMIT_HISTORICAL_SNAPSHOT` | Checksum-verified predecessor input or historical-reader support required for reproducibility. |
| `scripts/migrate_systematic_gap_2026_10_03.py` | `COMMIT_CURATED` | Approved migration and exact current-delta validation implementation. |
| `tests/test_audit_gap_2026_10_02.py` | `COMMIT_TEST` | Migration/audit regression guard. |
| `tests/test_systematic_gap_migration_2026_10_03.py` | `COMMIT_TEST` | Migration/audit regression guard. |

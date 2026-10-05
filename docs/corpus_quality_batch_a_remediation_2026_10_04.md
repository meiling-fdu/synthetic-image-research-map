# Corpus Quality Audit — Batch A remediation

Original audit date: 2026-10-04. Continuation/final verification: 2026-10-05. No commit or push is authorized.

Exactly 20 approved actions are applied to 18 existing paper identities. This result layer is separate from the unchanged original audit findings. No Batch B/C/D decision is applied.

## Corpus and taxonomy

| Metric | Before | After |
| --- | ---: | ---: |
| public | 640 | 640 |
| formal | 529 | 532 |
| mapped | 617 | 617 |
| unmapped | 23 | 23 |
| relationship_rows | 1423 | 1422 |
| unique_paper_institution_pairs | 1422 | 1422 |
| detection | 593 | 593 |
| source_attribution | 84 | 85 |
| localization | 38 | 40 |
| method | 548 | 548 |
| analysis_study | 74 | 79 |
| survey | 20 | 20 |
| dataset | 130 | 134 |
| benchmark | 83 | 89 |

Counts are recomputed for the 640 public identities joined to the authoritative 683-row taxonomy registry. The other 43 registry rows remain excluded. Only the three approved preprints become formal; LoRAX was already formal and remains Workshop.

## The 20 applied actions

| Review | Existing paper | Before → applied | Evidence |
| --- | --- | --- | --- |
| L002 | Detection, Attribution and Localization of GAN Generated Images | Four unsupported author–institution links removed; exact paper-time author groups applied | [Saved primary-source reference](https://arxiv.org/pdf/2007.10466) |
| L029 | Detection, Attribution and Localization of GAN Generated Images | 1,423 rows / 1,422 pairs → 1,422 rows / 1,422 pairs; natural exact-relationship collapse | [Saved primary-source reference](https://arxiv.org/pdf/2007.10466) |
| P018 | AEGIS: A Holistic Benchmark for Evaluating Forensic Analysis of AI-Generated Academic Images | preprint 2026 → conference 2026; Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers); DOI: none invented | [Saved primary-source reference](https://aclanthology.org/2026.acl-long.976.pdf) |
| P358 | LADLE-MM: Limited Annotation Based Detector with Learned Ensembles for Multimodal Misinformation | preprint 2025 → journal 2026; Computer Vision and Image Understanding; DOI: 10.1016/j.cviu.2026.104929 | [Saved primary-source reference](https://www.sciencedirect.com/science/article/pii/S1077314226002961) |
| P502 | LoRAX: LoRA eXpandable Networks for Continual Synthetic Image Attribution | Missing canonical formal URL → official BMVC 2024 Workshop PDF; identity/status/taxonomy unchanged | [Saved primary-source reference](https://bmvc2024.org/proceedings/workshop-proceedings/) |
| P572 | Open Set Synthetic Image Source Attribution | preprint 2023 → conference 2023; British Machine Vision Conference; DOI: none invented | [Saved primary-source reference](https://papers.bmvc2023.org/0659.pdf) |
| R063 | Defake-O3: From Speculative Rationales to Verifiable Evidence for Explainable AIGI Detection | method; dataset → method; dataset; benchmark | [Saved primary-source reference](https://arxiv.org/abs/2608.16259) |
| R074 | DNA: Dual-Stage Native Attribution for Generated Image Source Tracing | method; dataset → method; dataset; benchmark | [Saved primary-source reference](https://arxiv.org/abs/2607.13685) |
| R131 | How Well Are Open Sourced AI-Generated Image Detection Models Out-of-the-Box: A Comprehensive Benchmark Study | benchmark → benchmark; analysis_study | [Saved primary-source reference](https://arxiv.org/abs/2602.07814) |
| R210 | SSAFE: Simple and Strong AI-Generated Image Detection via Frozen Vision Encoders | method; analysis_study → method; dataset; benchmark; analysis_study | [Saved primary-source reference](https://arxiv.org/abs/2606.08634) |
| R326 | Fixed-Threshold Evaluation of a Hybrid CNN-ViT for AI-Generated Image Detection Across Photos and Art | method → method; benchmark; analysis_study | [Saved primary-source reference](https://arxiv.org/abs/2512.21512) |
| R346 | Generalized Design Choices for Deepfake Detectors | method → method; analysis_study | [Saved primary-source reference](https://arxiv.org/abs/2511.21507) |
| R388 | RAID: A Dataset for Testing the Adversarial Robustness of AI-Generated Image Detectors | dataset → dataset; benchmark | [Saved primary-source reference](https://arxiv.org/abs/2506.03988) |
| R496 | Improving Interpretability and Robustness for the Detection of AI-Generated Images | method → method; dataset; analysis_study | [Saved primary-source reference](https://arxiv.org/abs/2406.15035) |
| R528 | Towards More Accurate Fake Detection on Images Generated from Advanced Generative and Neural Rendering Models | method → method; dataset | [Saved primary-source reference](https://arxiv.org/abs/2411.08642) |
| R573 | PatchCraft: Exploring Texture Patch for Efficient AI-Generated Image Detection | method → method; dataset; benchmark | [Saved primary-source reference](https://arxiv.org/abs/2311.12397) |
| R614 | Learning to Disentangle GAN Fingerprint for Fake Image Attribution | method → method; analysis_study | [Saved primary-source reference](https://arxiv.org/abs/2106.08749) |
| T403 | SIDA: Social Media Image Deepfake Detection, Localization and Explanation with Large Multimodal Model | detection → detection; localization | [Saved primary-source reference](https://openaccess.thecvf.com/content/CVPR2025/html/Huang_SIDA_Social_Media_Image_Deepfake_Detection_Localization_and_Explanation_with_CVPR_2025_paper.html) |
| T495 | ImagiNet: A Multi-Content Benchmark for Synthetic Image Detection | detection → detection; source_attribution | [Saved primary-source reference](https://arxiv.org/abs/2407.20020) |
| T610 | Detection, Attribution and Localization of GAN Generated Images | detection; source_attribution → detection; source_attribution; localization | [Saved primary-source reference](https://arxiv.org/abs/2007.10466) |

The machine-readable ledger `data/raw/corpus_quality_batch_a_2026_10_04/results.json` retains each review ID, before/after values, evidence URLs, remediation date, resulting existing identity, and validation outcome. P358 preserves the arXiv identity and three-author order while adopting the verified journal title in the repository’s existing canonical title format. The publisher-observed spelling is separately retained in the ledger. Its stored publisher URL is retained in curated data; the exporter uses the verified DOI as the formal link under existing conventions. AEGIS retains its 21 authors and the full ACL Long Papers container in raw venue metadata. P572 retains arXiv 2308.11557 and paper number 659 in the evidence URL; no DOI is invented.

## UCSB R1/R2 and source provenance

`DETERMINISTIC_EXPORT_COLLAPSE_AFTER_R1_R2`

R1 assigns Michael Goebel, Shivkumar Chandrasekaran and B.S. Manjunath to UCSB. It assigns Lakshmanan Nataraj, Tejaswi Nanjundaswamy, Tajuddin Manhar Mohammed, Shivkumar Chandrasekaran and B.S. Manjunath to Mayachitra. These assignments come from the existing primary-paper review; they do not infer present employment.

The two UCSB rows become equivalent after R1. The unchanged general-purpose relationship-key/deduplication function naturally emits one UCSB aggregate during R2. No institution-specific production branch, manual row deletion, new location, coordinate change, institution merge or hierarchy change was introduced.

| Relationship measure | Before | After |
| --- | ---: | ---: |
| rows | 1423 | 1422 |
| unique_pairs | 1422 | 1422 |
| duplicate_pair_groups | 1 | 0 |
| repeated_author_institution_links | 1 | 0 |
| repeated_author_institution_groups | 1 | 0 |

For the affected paper, map rows change 3 → 2 and UCSB aggregate rows change 2 → 1. The complete three original map rows, including OpenAlex W3179128750 and W3043994911, remain in the checksummed pre-remediation snapshot and L002 `previous_value` records. The original relationship-review queue and its source/evidence references are also unchanged. Original raw/processed candidate sources are unchanged.

`NO MANUAL R3 MERGE APPLIED`

R3 remains `REQUIRES_MAINTAINER_DECISION`: the public aggregate collapse does not decide the long-term provenance representation policy.

## Authoritative sources and exporter integration

- `paper_taxonomy.csv`: exactly 14 approved dimension-label updates plus identity metadata synchronization for the three formal versions; companion labels are preserved.
- `papers.csv`: three publication updates and matching approved taxonomy labels where the identity has a curated paper row.
- `author_institution_mappings.csv`: publication title/year/DOI synchronization for those three existing identities; institution and author assignments are unchanged here.
- `institution_author_overrides.csv`: two paper/year/institution reviews using the existing author-override schema (`title,year,institution,authors,notes`), with primary-source evidence in notes.
- `publication_overrides.csv`: one LoRAX URL review using the existing publication-override schema; all existing formal status fields are repeated unchanged.

The exporter reads these two optional curated override sources, reapplies them after preservation, and rebuilds nested author indices. The shrinkage guard accepts an author correction only when the corrected author set is present at the same paper, institution, location and coordinates. Focused negative tests reject unrelated paper/institution/location/author changes. No generated JSON was patched by hand. The generic curated validator checks its established 17-file schema; the two optional override files are additionally checked by their existing loaders and the exact-content Batch A validator.

## BMVC registry consistency

One canonical-name alias was added to `venue_aliases.csv` for the already existing `venue:british-machine-vision-conference`, copying the established BMVC metadata from saved primary-source venue evidence. No duplicate alias or new venue identity was created. The venue-level track stays empty; P572 itself is Main and LoRAX stays Workshop. A regression test compares the effective enriched catalogs before/after and requires exact semantic equality. Unrelated BMVC public records are unchanged.

## Generated key-paper coverage report

Both reports were regenerated with `scripts/audit_key_paper_coverage.py`; neither was hand-edited. Exactly two CSV rows change: checklist 218 updates LADLE-MM’s matched public title, and checklist 26 changes this UCSB paper’s map count 3 → 2 as a direct R2 consequence. No coverage classification changes. AEGIS, P572 and LoRAX produce no per-row coverage delta. The Markdown report changes its input hash, total map rows and the UCSB row count.

## Historical reproducibility

`predecessor_640.json.gz` stores exact pre-remediation bytes with checksums checked against the starting tracked-file manifest. Historical quality-audit, taxonomy-migration and 17-paper-migration tests use that snapshot; their exact historical expectations are unchanged. Older 623/666-paper receipts retain their original snapshots, and their historical reader falls back to verified pre-Batch-A bytes only for files absent from the older snapshot. Current repository, publication-filter and metadata-consistency tests use exact current Batch A counts; immutable release baselines are unchanged. Current Batch A tests independently check current labels, publication identities, affiliations and registry round-trip behavior.

## Validation

- Batch A regression tests: 35 passed. Batch A plus historical quality-audit and 17-paper migration tests: 68 passed.
- Broader targeted regression groups: 313 passed; 14 subtests passed; zero failures.
- Post-repair current-state and Batch A checks: 104 passed; 13 subtests passed. Historical receipt repair group: 39 passed, two existing warnings.
- Full repository suite: **1,627 passed, 389 subtests passed, zero failures, two existing warnings** (308.51 seconds). Both warnings are `PytestReturnNotNoneWarning` from the existing legacy-migration receipt helper tests; neither was suppressed.
- Curated validator: zero errors, 252 warnings (250 baseline warnings plus two notices that optional curated override CSVs are outside its established 17-file schema). The override loaders and exact-content Batch A guards validate those additional files; warnings were not suppressed.
- Public map validator: zero errors, zero warnings. Public paper validator: zero errors, 23 existing affiliation warnings.
- Historical audit validator and current Batch A validator: zero errors.
- Final export and report-regeneration rounds are byte-identical across both JSON exports and both key-paper report artifacts: `EXPORT_REPRODUCIBLE = 1`. SHA-256 values are in `verification.json`.

The initial broader run's three failures were historical count assertions, subsequently repaired by selecting the preserved historical input. BMVC registry consistency and report freshness errors were resolved as documented above. The first full-suite attempt additionally found five stale current-count assertions, three historical hash checks reading successor bytes, and one P358 title-format subtest. Current expectations were updated exactly, historical readers were connected to preserved bytes, and the approved P358 title was normalized with the existing helper. The historical repair group passed 39 tests with the two existing pytest warnings. No assertion was weakened.

## Integrity and remaining review

`UNEXPECTED_CHANGED = 0`

`FROZEN_NEURIPS_CHANGED = 0`

`PREEXISTING_LOCAL_FILES_CHANGED = 0`

All original audit findings remain byte-identical; only the audit validator/test harness gains historical-snapshot support. The 128 excluded local files are unchanged and unstaged. Unmapped identities remain the same 23. No literature discovery, new paper identity, scope change or frontend/homepage change occurred.

Remaining counts are computed by subtracting APPLIED review IDs from the original decision ledger: Batch B 159 actions; Batch C 41 actions; Batch D 1,752 retention decisions. These are decision/dimension counts, not paper counts.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Git review

Final inventory: **17 tracked files modified**, **151 untracked files**, and **zero staged files**. The untracked inventory is exactly 128 pre-existing excluded files, nine original audit files, and 14 Batch A files. Of the nine original audit files, only the validator and test harness changed; the seven findings/evidence files remain byte-identical.

Tracked changes comprise four curated source files, two generated public exports, two generated key-paper reports, four exporter/historical-reader scripts, and five current/historical test files. New Batch A files comprise two curated override sources, seven snapshot/plan/result/validation files, three scripts, one regression test file, and this remediation report. Exact paths are recorded in `verification.json` and `validation.json`.

`git diff --check` passes. No literature additions, Batch B/C remediation, new coordinates, frozen NeurIPS changes, homepage/frontend asset changes, or staging occurred. HEAD remains `ff583614ed50294f17a5dff85d00f40cbfc77079`. No commit or push.

**CORPUS QUALITY BATCH A APPLIED — READY FOR FINAL REVIEW**

# Literature51 integration audit — October 16, 2026

This report covers exactly the 51 candidates embedded in the task. No external candidate file was required. The input inventory remains in `data/raw/literature51_2026_10_16/candidates.json`; the reviewed evidence, exhaustive reconciliation, and exact append plan are under `data/processed/literature51_2026_10_16/`.

Baseline HEAD: `9e7666169cba098f62f022b7f9f60cdf7c7c72e1`. Branch: `detached HEAD`. No commit or push was performed.

## Dispositions

| Disposition | Candidates |
| --- | ---: |
| Newly imported | 38 |
| Already present / reconciled without a new import | 0 |
| Held for insufficient mandatory evidence | 11 |
| Excluded after substantive scope verification | 0 |
| Other blocked: existing NeurIPS migration / track lock | 2 |
| **Total unique candidates** | **51** |

The 38 additions include A01 and A13, whose historical HOLD dispositions were explicitly reconciled. They are counted once as new imports. The 13 non-imports comprise 11 evidence holds and 2 locked NeurIPS candidates. There are no duplicate additions, revived exclusions, or invented article identities.

Fifteen imported taxonomy records remain `needs_review`: fourteen have only publisher-registered titles available for technical classification, and D06 requires experimental disaggregation of generative editing from conventional manipulation. Their proposed dimensions and reasons remain explicit, with `manual_review=true` in the batch audit. Bibliographic verification is independent of taxonomy review and map eligibility.

## Repository integrity

| Measure | Before | After |
| --- | ---: | ---: |
| Total curated papers | 496 | 534 |
| Public papers | 639 | 677 |
| Formally published papers, including verified online-first | 531 | 561 |
| Mapped unique papers | 617 | 617 |
| Institution/site markers | 684 | 684 |
| Distinct public institution identities | 567 | 567 |
| Map relationships | 1421 | 1421 |
| Active exclusions | 98 | 98 |
| Pending paper review items | 7 | 33 |

Marker counts use the frontend’s institution-plus-location/coordinate identity; one institution can have multiple sites. Relationships count all map rows. The institution registry itself remains 748 rows, with 727 active identities.

Pending review items count unique paper identities with an effective unresolved decision or a `needs_review` taxonomy row: 7 before, 33 after (18 effective unresolved decisions plus 15 taxonomy reviews). The append-only decision ledger retains 20 unresolved rows, including the 2 historical HOLDs explicitly superseded by new linked resolution records. The original 19 review rows remain byte-for-byte intact.

All 639 pre-existing public paper objects and all 1,421 map relationships are exactly unchanged. No author–institution mappings, institution identities, locations, aliases, geographic coordinates, geocoding caches, exclusion rows, or `data/manual/` files were changed. All 38 additions remain without map markers. The pre-existing untracked audit files are checksum-preserved. Frontend source, CSS, dependencies, schemas, validators, historical review locks, and historical evidence receipts are unchanged.

## Evidence and publication handling

- DOI/title/ordered-author matches use publisher-deposited Crossref records or original publisher/paper metadata. Raw HTTP bodies, redirect/challenge responses, failure metadata, and targeted primary search captures are retained separately.
- HTTP 200 browser challenges and empty HTTP 202 responses are not treated as verified bibliographic or technical evidence.
- Accepted-only records are held when publication state or mandatory metadata cannot be represented faithfully. No unofficial publication type or conference track was introduced.
- Assigned print/issue dates are kept distinct from actual online dates. A17 and E12 retain 2027 print/citation years and their independently evidenced September 2026 online dates. C01–C03, E06 and E13 remain held because actual online dates could not be verified. A05 keeps the 2026 issue year and labels the supplied 2025 online year as reported, not an invented exact date.
- Original publisher/paper names and ordering are preserved. No author or institution identity merges were performed. Descriptions are labeled primary-source summaries; absent technical abstracts remain empty.
- The ten venue alias additions use the existing reviewed canonical-venue workflow and existing `journal`/`conference` types. No taxonomy vocabulary or membership rule changed.

## Testing and regeneration

| Check | Actual result |
| --- | --- |
| Focused final tests | 58 passed; 0 failed; 0 skipped (8.84 seconds) |
| Current-corpus regression follow-up | 30 passed; 0 failed; 12 subtests passed |
| Full final pytest suite | 1701 passed; 4 failed; 0 skipped; 389 subtests passed; 2 warnings (311.04 seconds) |
| Curated database | 0 errors; 0 duplicate candidates; 290 warnings (252 baseline + 38 new missing-affiliation warnings) |
| Public map validation | 0 errors; 0 warnings; 1421 relationships / 617 papers |
| Public paper validation | 0 errors; 61 warnings; 677 papers (38 new unresolved affiliation warnings) |
| Repeated canonical regeneration | byte-identical public JSON pair; 639 existing papers and 1421 relationships exactly preserved |
| Repeated application | idempotent; no duplicate append or timestamp churn |
| Global public identity checks | no duplicate normalized titles, DOI values, or arXiv IDs |
| Source cache | 120 targeted references; 88 captured responses; 32 documented retrieval failures; 0 missing cache files |
| Unrelated-change audit | 0 unexpected tracked or new files; all 130 pre-existing untracked files preserved |
| Manual/frontend/locks | all unchanged; schemas and validators unchanged; no institution or geographic changes |
| Git diff whitespace | git diff --check passed; index empty; HEAD unchanged; no commit or push |

The full suite is not green. Its four remaining failures are the same historical public-refinement snapshot failures observed before any curated-data edits; each fails with “Public refinement differs from its reviewed snapshot”. No new full-suite failures remain. The initial sandbox-limited baseline run reported 1566 passed, 71 failed, and 64 skipped because Node was absent from PATH and temporary localhost servers were restricted; the final full run used bundled Node and permitted temporary test servers. The first full run after data import had 22 failures; 18 count, report-freshness, or historical-boundary failures were resolved while retaining historical assertions and receipts. Unrelated frontend source and historical snapshot policy were not changed.

- `test_systematic_tier2_application::test_pre_application_baseline_includes_and_preserves_previous_policy_pass`
- `test_systematic_tier2_normal_priority_evidence::test_authoritative_append_is_exact_and_preserves_existing_rows`
- `test_systematic_tier2_normal_priority_evidence::test_report_reproduces_byte_for_byte`
- `test_systematic_tier2_policy::test_pre_task_repository_files_are_byte_identical`

The canonical exporter runs with `--preserve-existing`; the batch wrapper stages the ordinary location-review side output so unrelated queue entries are not written. The generated key-paper Markdown report is refreshed through the canonical coverage renderer only after proving its CSV under `data/manual/` is unchanged. The result is static JSON consumed by the existing Leaflet site; no custom backend is introduced.

Historical Batch C tests retain all prior assertions and counts and use a checksum-verified pre-import snapshot. Current-corpus tests use the reviewed successor counts. No production validator or historical receipt is patched.

## Reproduction

```sh
python3 scripts/collect_literature51_sources.py
python3 scripts/integrate_literature51_2026_10_16.py --apply
python3 scripts/regenerate_literature51_2026_10_16.py
python3 scripts/integrate_literature51_2026_10_16.py --check
python3 scripts/validate_curated_database.py
python3 scripts/validate_public_preview.py
python3 scripts/report_literature51_2026_10_16.py
```

`--apply` is idempotent once its receipt exists. Initial preparation without `--apply` is intended for the pre-import baseline only; it refuses duplicate identities instead of generating another append. No network is needed for replay. Test environment and executed command results are recorded in `validation.json` and `test_results/`; repository dependency files were not changed.

## Changed files

| File or group | Purpose |
| --- | --- |
| `data/curated/papers.csv` | Append 38 verified bibliographic identities and preserve all existing bytes. |
| `data/curated/paper_taxonomy.csv` | Append matching taxonomy, evidence tiers, and explicit pending review reasons. |
| `data/curated/review_decisions.csv` | Append 51 decisions; explicitly link the 2 resolved historical HOLDs. |
| `data/curated/venue_aliases.csv` | Append 10 reviewed venue aliases through the supported workflow. |
| `web/data/public_preview_papers.json`, `web/data/public_preview_map_data.json` | Canonical static export; add 38 papers and synchronize the pair timestamp. Map records are unchanged. |
| `docs/key_paper_coverage_report.md` | Canonical generated count/fingerprint refresh; manual CSV is unchanged. |
| `data/raw/literature51_2026_10_16/` | Task-derived inventory and immutable source captures, URLs, hashes, and failed retrievals. |
| `data/processed/literature51_2026_10_16/` | Reviewed evidence, plan, before snapshots, append receipt, all-51 audit, validation, regeneration, and integrity receipts. |
| `scripts/collect_literature51_sources.py` | Read-only source-cache validation and explicit missing-capture retrieval. |
| `scripts/integrate_literature51_2026_10_16.py` | Offline normalization, deduplication, guarded append, history preservation, and idempotence. |
| `scripts/regenerate_literature51_2026_10_16.py` | Canonical export with exact existing-record preservation checks. |
| `scripts/report_literature51_2026_10_16.py` | Deterministic counts and exhaustive audit rendering. |
| `tests/test_literature51_integration.py` | Evidence, identity, hold/track/date, taxonomy, affiliation, and repeat-apply regressions. |
| `tests/literature51_predecessor.py` and historical Batch A/C test imports | Replay historical assertions against hash-verified predecessor bytes. |
| Current count checks in `tests/baseline_expectations.py`, publication-filter, metadata-consistency, and repository-baseline tests | Reviewed successor totals; preserve earlier release constants and explicit author-review invariants. |
| This report | Complete requested 51-paper audit and exact limitations. |

## Per-paper audit

### A01 — Proto-LeakNet: Towards Signal-Leak Aware Attribution in Synthetic Human Face Imagery

- **Scope:** `in_scope`. Publisher abstract describes closed-set generator classification and open-set rejection using passive diffusion latent signal-leaks, without modifying generator outputs. The synthetic face domain is explicitly retained.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:635db68b6b4f321a6499`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.cviu.2026.104848](https://doi.org/10.1016/j.cviu.2026.104848).
- **Publication:** `published`; Computer Vision and Image Understanding; year 2026.
- **Publication details:** `{"page": "104848", "published-print": {"date-parts": [[2026, 8]]}, "volume": "270"}`.
- **Ordered authors:** Claudio Giusti; Luca Guarnera; Sebastiano Battiato.
- **Taxonomy:** `tasks=source_attribution; image_scopes=fully_generated;deepfake; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Publisher title, DOI, ordered authors, and technical abstract now independently verify the exact held identity and passive generator attribution. Resolve the disposition while retaining the October 3 HOLD row unchanged.
- **Duplicate / historical handling:** Historical HOLD `review:6fdf776f884597171f66` retained; linked resolution `review:919a0e9833bf28d589e1` appended.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://www.sciencedirect.com/science/article/pii/S1077314226002158](https://www.sciencedirect.com/science/article/pii/S1077314226002158); [https://api.crossref.org/works/10.1016/j.cviu.2026.104848](https://api.crossref.org/works/10.1016/j.cviu.2026.104848); [data/raw/literature51_2026_10_16/priority_search.json](../data/raw/literature51_2026_10_16/priority_search.json).

### A02 — MF²DA: Multi-Level Feature Fusion for Robust Detection and Attribution of Universal AI-Generated Images

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection and source_attribution of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:eb779a62c0d905c3a146`.
- **Identifiers:** DOI [https://doi.org/10.1109/tifs.2026.3723156](https://doi.org/10.1109/tifs.2026.3723156).
- **Publication:** `published`; IEEE Transactions on Information Forensics and Security; year 2026.
- **Publication details:** `{"page": "7842-7857", "published-print": {"date-parts": [[2026]]}, "volume": "21"}`.
- **Ordered authors:** Wenpeng Mu; Qiang Xu; Yining Zhang; Xiao Zhang; Huiyuan Wang; Yuefan Li; Xinghao Jiang; Tanfeng Sun.
- **Taxonomy:** `tasks=detection;source_attribution; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned. Normalize publisher superscript markup in MF²DA; preserve submitted MF2DA as an identity alias.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1109/tifs.2026.3723156](https://api.crossref.org/works/10.1109/tifs.2026.3723156).

### A03 — Synthetic Frequency Patterns Injection for Data-Agnostic Deepfake Detection

- **Scope:** `in_scope`. The publisher describes injecting crafted frequency patterns into pristine detector-training images and evaluating on 25 GAN/diffusion generators. This is detector augmentation, not watermark or provenance insertion into released generator outputs.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:c049a37ade69253edfc2`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.cviu.2026.104781](https://doi.org/10.1016/j.cviu.2026.104781).
- **Publication:** `published`; Computer Vision and Image Understanding; year 2026.
- **Publication details:** `{"page": "104781", "published-print": {"date-parts": [[2026, 5]]}, "volume": "268"}`.
- **Ordered authors:** Davide Alessandro Coccomini; Roberto Caldelli; Claudio Gennaro; Giuseppe Fiameni; Giuseppe Amato; Fabrizio Falchi.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated;deepfake; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.cviu.2026.104781](https://api.crossref.org/works/10.1016/j.cviu.2026.104781); [data/raw/literature51_2026_10_16/publisher_scope_a.json](../data/raw/literature51_2026_10_16/publisher_scope_a.json).

### A04 — Exploring Real–Synthetic Boundaries in Diffusion Latent Space

- **Scope:** `in_scope`. The publisher describes real/synthetic discrimination in diffusion latent representations. This concerns passive image detection rather than modifying generated images.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:ac538fc54d877427c2ba`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.cviu.2026.104815](https://doi.org/10.1016/j.cviu.2026.104815).
- **Publication:** `published`; Computer Vision and Image Understanding; year 2026.
- **Publication details:** `{"page": "104815", "published-print": {"date-parts": [[2026, 8]]}, "volume": "270"}`.
- **Ordered authors:** Simone Bonechi; Paolo Andreini; Barbara Toniella Corradini.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.cviu.2026.104815](https://api.crossref.org/works/10.1016/j.cviu.2026.104815); [data/raw/literature51_2026_10_16/publisher_scope_a.json](../data/raw/literature51_2026_10_16/publisher_scope_a.json).

### A05 — Revisiting DIRE: Towards Universal AI-Generated Image Detection

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:e07e2b1ae3b0de2b056d`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.neunet.2025.108084](https://doi.org/10.1016/j.neunet.2025.108084).
- **Publication:** `published`; Neural Networks; year 2026.
- **Publication details:** `{"page": "108084", "published-print": {"date-parts": [[2026, 1]]}, "reported_online_year": 2025, "reported_online_year_source": "data/raw/literature51_2026_10_16/request.txt", "volume": "193"}`.
- **Ordered authors:** Huanqi Lin; Jinghui Qin; Xiaoqi Wu; Tianshui Chen; Zhijing Yang.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned. Keep the 2026 volume-193 issue year. The supplied audit reports 2025 online-first; no exact online date was recovered, so retain that distinction as reported rather than infer a date from its DOI.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.neunet.2025.108084](https://api.crossref.org/works/10.1016/j.neunet.2025.108084).

### A06 — Dual-Branch Asymmetric Discrepancy Learning Based on Fake Image Pattern-Coexistence for AI-Generated Image Detection

- **Scope:** `in_scope`. The official AAAI abstract evaluates DADL on AIGCDetectBenchmark, GenImage, and Chameleon, including Midjourney and Stable Diffusion images. This is whole-image real/generated detection.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:ecb2ef919269ff6c14d3`.
- **Identifiers:** DOI [https://doi.org/10.1609/aaai.v40i2.37071](https://doi.org/10.1609/aaai.v40i2.37071).
- **Publication:** `published`; AAAI Conference on Artificial Intelligence; year 2026; track `Main`.
- **Publication details:** `{}`.
- **Ordered authors:** Chunli Song; Jie Liu; Peiyang Wang; Ying Huang; Guixuan Zhang; Zhi Zeng; Shuwu Zhang.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://ojs.aaai.org/index.php/AAAI/article/view/37071](https://ojs.aaai.org/index.php/AAAI/article/view/37071).

### A07 — Leveraging Arbitrary Data Sources for AI-Generated Image Detection Without Sacrificing Generalization

- **Scope:** `in_scope`. The official CVF page presents generalizable AI-generated image detection using arbitrary training data. Its publication identity is CVPR Findings, not the main conference.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:df9e69d937b77f07a093`.
- **Identifiers:** Primary [https://openaccess.thecvf.com/content/CVPR2026F/html/He_Leveraging_Arbitrary_Data_Sources_for_AI-Generated_Image_Detection_Without_Sacrificing_CVPRF_2026_paper.html](https://openaccess.thecvf.com/content/CVPR2026F/html/He_Leveraging_Arbitrary_Data_Sources_for_AI-Generated_Image_Detection_Without_Sacrificing_CVPRF_2026_paper.html).
- **Publication:** `published`; IEEE/CVF Conference on Computer Vision and Pattern Recognition; year 2026; track `Findings`.
- **Publication details:** `{}`.
- **Ordered authors:** Qinghui He; Haifeng Zhang; Xiuli Bi; Bo Liu; Chi-Man Pun; Bin Xiao.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://openaccess.thecvf.com/content/CVPR2026F/html/He_Leveraging_Arbitrary_Data_Sources_for_AI-Generated_Image_Detection_Without_Sacrificing_CVPRF_2026_paper.html](https://openaccess.thecvf.com/content/CVPR2026F/html/He_Leveraging_Arbitrary_Data_Sources_for_AI-Generated_Image_Detection_Without_Sacrificing_CVPRF_2026_paper.html).

### A08 — GRE-Net: A Forgery Image Detection Framework Based on Gradient Feature and Reconstruction Error

- **Scope:** `in_scope`. The publisher evaluates GRE-Net on images from ten GAN and diffusion generators, combining ProjectedGAN discriminator gradients with DIRE reconstruction error. Only the synthetic-image detection component is included.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:ea0760d1a12e59f8f089`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.cviu.2025.104494](https://doi.org/10.1016/j.cviu.2025.104494).
- **Publication:** `published`; Computer Vision and Image Understanding; year 2025.
- **Publication details:** `{"page": "104494", "published-print": {"date-parts": [[2025, 11]]}, "volume": "261"}`.
- **Ordered authors:** Wenqing Wu; Xinyi Shi; Jinghai Ai; Xiaodong Wang.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.cviu.2025.104494](https://api.crossref.org/works/10.1016/j.cviu.2025.104494); [data/raw/literature51_2026_10_16/scope_dates_followup.json](../data/raw/literature51_2026_10_16/scope_dates_followup.json).

### A09 — LiteUpdate: A Lightweight Framework for Updating AI-Generated Image Detectors

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:a5e09c7c747a03ff3cd6`.
- **Identifiers:** DOI [https://doi.org/10.1109/tcsvt.2026.3683200](https://doi.org/10.1109/tcsvt.2026.3683200).
- **Publication:** `published`; IEEE Transactions on Circuits and Systems for Video Technology; year 2026.
- **Publication details:** `{"issue": "8", "page": "11788-11801", "published-print": {"date-parts": [[2026, 8]]}, "volume": "36"}`.
- **Ordered authors:** Jiajie Lu; Zhenkan Fu; Na Zhao; Long Xing; Xiangkun Wang; Kejiang Chen; Weiming Zhang; Nenghai Yu.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1109/tcsvt.2026.3683200](https://api.crossref.org/works/10.1109/tcsvt.2026.3683200).

### A10 — Dual-Path AI-Generated Image Detection: Leveraging Texture-Rich and Texture-Poor Patches with Global Semantic Features

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:2721935e2934487f3fb3`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.dsp.2025.105840](https://doi.org/10.1016/j.dsp.2025.105840).
- **Publication:** `published`; Digital Signal Processing; year 2026.
- **Publication details:** `{"page": "105840", "published-print": {"date-parts": [[2026, 3]]}, "volume": "171"}`.
- **Ordered authors:** Jiapeng Lin; Qihao Zhou; Jie Li.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.dsp.2025.105840](https://api.crossref.org/works/10.1016/j.dsp.2025.105840).

### A11 — Lightweight AI-Generated Image Detection Based on Enhanced Common Artifact Features

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:d450c63c3edaefd1f45a`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.eswa.2025.130500](https://doi.org/10.1016/j.eswa.2025.130500).
- **Publication:** `published`; Expert Systems with Applications; year 2026.
- **Publication details:** `{"page": "130500", "published-print": {"date-parts": [[2026, 3]]}, "volume": "301"}`.
- **Ordered authors:** Shuyi Li; Li Li; Yanli Ren; Xinpeng Zhang; Guorui Feng.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.eswa.2025.130500](https://api.crossref.org/works/10.1016/j.eswa.2025.130500).

### A12 — SDA-Det: A Subpixel-Aware Dual-Domain Artifact Detector for AI-Generated Image Detection

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:bb7e7c98caa6cfd8e540`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.eswa.2026.132304](https://doi.org/10.1016/j.eswa.2026.132304).
- **Publication:** `published`; Expert Systems with Applications; year 2026.
- **Publication details:** `{"page": "132304", "published-print": {"date-parts": [[2026, 8]]}, "volume": "322"}`.
- **Ordered authors:** Pei Lu; Kunming Liang; Xiaoyong Liu; Xi Lu; Ansheng Li.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.eswa.2026.132304](https://api.crossref.org/works/10.1016/j.eswa.2026.132304).

### A13 — SCA-Det: A Structure-Context Artifact Detector for AI-Generated Image Detection

- **Scope:** `in_scope`. Publisher evidence evaluates SCA-Det on 45 GAN/diffusion image groups. Structure and context artifacts support passive real/generated detection, including unseen generators.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:94a969498e5e02e2b990`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.neucom.2026.133627](https://doi.org/10.1016/j.neucom.2026.133627).
- **Publication:** `published`; Neurocomputing; year 2026.
- **Publication details:** `{"issue_date": "2026-07-07", "volume": "685"}`.
- **Ordered authors:** Kunming Liang; Pei Lu; Xiaoyong Liu; Xi Lu; Ansheng Li.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Publisher title, DOI, ordered authors and GAN/diffusion evaluations now verify the exact held identity. Preserve the October 3 HOLD row and append an explicit resolution.
- **Duplicate / historical handling:** Historical HOLD `review:ba4eefe10289ef9e8a31` retained; linked resolution `review:16fdb2d3b3dee1eabda2` appended.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://www.sciencedirect.com/science/article/pii/S0925231226010246](https://www.sciencedirect.com/science/article/pii/S0925231226010246); [https://doi.org/10.1016/j.neucom.2026.133627](https://doi.org/10.1016/j.neucom.2026.133627); [data/raw/literature51_2026_10_16/priority_search.json](../data/raw/literature51_2026_10_16/priority_search.json).

### A14 — MS-DCL: Multi-Scale Decoupled Contrastive Learning for Universal AI-Generated Image Detection

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:0a43754e9c715ea9c33a`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.knosys.2026.116183](https://doi.org/10.1016/j.knosys.2026.116183).
- **Publication:** `published`; Knowledge-Based Systems; year 2026.
- **Publication details:** `{"page": "116183", "published-print": {"date-parts": [[2026, 7]]}, "volume": "346"}`.
- **Ordered authors:** Wei Qu; Cong Chen; Wei Lu; Tao Li.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.knosys.2026.116183](https://api.crossref.org/works/10.1016/j.knosys.2026.116183).

### A15 — Structure Searchable Network Model for Deepfake Image Detection

- **Scope:** `in_scope`. The publisher explicitly compares AI-generated images against camera images, using color-space correlation and low-frequency-spectrum inputs in a genetic-algorithm network search. Synthetic-generation experiments establish scope.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:342f48802ce5ee538665`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.patcog.2026.113813](https://doi.org/10.1016/j.patcog.2026.113813).
- **Publication:** `journal_online_first`; Pattern Recognition; year 2026.
- **Publication details:** `{"article": "113813", "assigned_issue": "2026-11", "online_date": "2026-04-21", "volume": "179"}`.
- **Ordered authors:** Zinian Liu; Xiaofeng Wang; Qin Wang; Ningning Bai; Ruidong Han; Shanmin Pang.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated;deepfake; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Publisher abstract proves generated-vs-camera experiments. Online April 21, 2026; assigned November 2026 issue. No face-swap-only assumption is made.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://www.sciencedirect.com/science/article/pii/S0031320326007788](https://www.sciencedirect.com/science/article/pii/S0031320326007788); [data/raw/literature51_2026_10_16/publisher_scope_a.json](../data/raw/literature51_2026_10_16/publisher_scope_a.json); [data/raw/literature51_2026_10_16/online_dates_other.json](../data/raw/literature51_2026_10_16/online_dates_other.json).

### A16 — Diversity Matters: Dataset Diversification and Dual-Branch Network for Generalized AI-Generated Image Detection

- **Scope:** `in_scope`. The official CVF workshop paper proposes dataset diversification and a dual-branch network for generalized AI-generated image detection.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:3af3f884610309193138`.
- **Identifiers:** Primary [https://openaccess.thecvf.com/content/CVPR2026W/SVC/html/Tasnim_Diversity_Matters_Dataset_Diversification_and_Dual-Branch_Network_for_Generalized_AI-Generated_CVPRW_2026_paper.html](https://openaccess.thecvf.com/content/CVPR2026W/SVC/html/Tasnim_Diversity_Matters_Dataset_Diversification_and_Dual-Branch_Network_for_Generalized_AI-Generated_CVPRW_2026_paper.html).
- **Publication:** `published`; IEEE/CVF Conference on Computer Vision and Pattern Recognition; year 2026; track `Workshop`.
- **Publication details:** `{}`.
- **Ordered authors:** Nusrat Tasnim; Kutub Uddin; Khalid Malik.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://openaccess.thecvf.com/content/CVPR2026W/SVC/html/Tasnim_Diversity_Matters_Dataset_Diversification_and_Dual-Branch_Network_for_Generalized_AI-Generated_CVPRW_2026_paper.html](https://openaccess.thecvf.com/content/CVPR2026W/SVC/html/Tasnim_Diversity_Matters_Dataset_Diversification_and_Dual-Branch_Network_for_Generalized_AI-Generated_CVPRW_2026_paper.html).

### A17 — S²F-Net: A Robust Spatial-Spectrum Fusion Framework for Cross-Model AIGC Detection

- **Scope:** `in_scope`. The publisher describes a passive spatial-spectrum detector evaluated on AIGCDetectBenchmark with 17 categories of generators. Fingerprints are extracted from existing images, not actively embedded.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:2e6a41de0822fcb4aa73`.
- **Identifiers:** DOI [https://doi.org/10.1016/j.eswa.2026.134399](https://doi.org/10.1016/j.eswa.2026.134399).
- **Publication:** `journal_online_first`; Expert Systems with Applications; year 2027.
- **Publication details:** `{"assigned_issue_date": "2027-02-01", "online_date": "2026-09-12", "page": "134399", "published-print": {"date-parts": [[2027, 2]]}, "volume": "334"}`.
- **Ordered authors:** Xiangyu Hu; Hongchuang Zheng; Yicheng Hong; Wenjun Zeng; Bingyao Liu.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Correct the supplied 2026 issue-year claim: publisher DOI registration assigns volume 334 to February 2027. Retain the verified September 12, 2026 online-first date separately; journal publication is already online.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.eswa.2026.134399](https://api.crossref.org/works/10.1016/j.eswa.2026.134399); [data/raw/literature51_2026_10_16/chapter_and_dates.json](../data/raw/literature51_2026_10_16/chapter_and_dates.json).

### A18 — Explainable AI-Generated Image Forensics: A Low-Resolution Perspective with Novel Artifact Taxonomy

- **Scope:** `in_scope`. Official CVF evidence evaluates low-resolution real/generated classification on augmented CIFAKE and introduces an explainable visual-artifact taxonomy. This is a detection method and forensic analysis.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:d00a291c223534af3390`.
- **Identifiers:** Primary [https://openaccess.thecvf.com/content/ICCV2025W/APAI/html/Sharma_Explainable_AI-Generated_Image_Forensics_A_Low-Resolution_Perspective_with_Novel_Artifact_ICCVW_2025_paper.html](https://openaccess.thecvf.com/content/ICCV2025W/APAI/html/Sharma_Explainable_AI-Generated_Image_Forensics_A_Low-Resolution_Perspective_with_Novel_Artifact_ICCVW_2025_paper.html).
- **Publication:** `published`; IEEE/CVF International Conference on Computer Vision; year 2025; track `Workshop`.
- **Publication details:** `{"pages": "1587–1596"}`.
- **Ordered authors:** Kaustubh Sharma.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method;analysis_study`. Evidence-reviewed.
- **Metadata corrections / evidence:** Official ICCV APAI workshop record and BibTeX verify sole author and pages; keep Workshop rather than Main.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://openaccess.thecvf.com/content/ICCV2025W/APAI/html/Sharma_Explainable_AI-Generated_Image_Forensics_A_Low-Resolution_Perspective_with_Novel_Artifact_ICCVW_2025_paper.html](https://openaccess.thecvf.com/content/ICCV2025W/APAI/html/Sharma_Explainable_AI-Generated_Image_Forensics_A_Low-Resolution_Perspective_with_Novel_Artifact_ICCVW_2025_paper.html); [data/raw/literature51_2026_10_16/other_identity.json](../data/raw/literature51_2026_10_16/other_identity.json).

### A19 — Improving Generalization in AI-Generated Facial Image Detection via Explainable Recovery

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:128d41903480b9eb4b6e`.
- **Identifiers:** DOI [https://doi.org/10.1145/3785353.3815082](https://doi.org/10.1145/3785353.3815082).
- **Publication:** `published`; ACM Workshop on Information Hiding and Multimedia Security; year 2026; track `Main`.
- **Publication details:** `{"page": "229-240", "published-online": {"date-parts": [[2026, 6, 16]]}, "published-print": {"date-parts": [[2026, 6, 17]]}}`.
- **Ordered authors:** Giulia Ciacci; Alessandra Spinaci; Niccolò Biondi; Andrea Ciamarra; Roberto Caldelli.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated;deepfake; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned. Fully synthetic faces are in scope. The standalone IH&MMSec event identity is preserved; the registered online publication date is June 16, 2026.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1145/3785353.3815082](https://api.crossref.org/works/10.1145/3785353.3815082).

### A20 — Spotting the Fakes: A Deep Dive Into GAN-Generated Face Detection

- **Scope:** `in_scope`. The publisher-deposited abstract explicitly reviews detection of fully GAN-generated facial images and compares detector families and human performance. This is a survey, not a face-swap-only detector.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:c57a82bc92cfd4b474b0`.
- **Identifiers:** DOI [https://doi.org/10.1145/3742786](https://doi.org/10.1145/3742786).
- **Publication:** `published`; ACM Transactions on Multimedia Computing, Communications, and Applications; year 2025.
- **Publication details:** `{"issue": "7", "page": "1-24", "published-online": {"date-parts": [[2025, 7, 24]]}, "published-print": {"date-parts": [[2025, 7, 31]]}, "volume": "21"}`.
- **Ordered authors:** Xin Wang; Ting Yu Tsai; Li Lin; Hui Guo; Shu Hu; Ming-Ching Chang; Pradeep K. Atrey; Siwei Lyu.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated;deepfake; research_types=survey`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1145/3742786](https://api.crossref.org/works/10.1145/3742786).

### B01 — FARE: Forensic Acceptance Region Estimation for Catching Bait-and-Switch Image Generators

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive source_attribution of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `BLOCKED_EXISTING_MIGRATION`; no curated or public identity created.
- **Identifiers:** arXiv [https://arxiv.org/abs/2609.30982](https://arxiv.org/abs/2609.30982).
- **Publication:** `accepted_track_unresolved`; Advances in Neural Information Processing Systems; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Kai Yao; Marc Juarez.
- **Taxonomy:** `tasks=source_attribution; image_scopes=fully_generated; research_types=method`. Proposed only; not imported.
- **Metadata corrections / evidence:** Official NeurIPS acceptance is already established in the immutable 7+1 migration. Its official track remains unresolved. Preserve the blocked migration, including its proposed FARE identity; do not import a second preprint identity.
- **Duplicate / historical handling:** Existing locked NeurIPS migration identity `curated:62f8713f970aa4a95432` retained without application or duplicate preprint.
- **Outstanding:** Official NeurIPS acceptance is already established in the immutable 7+1 migration. Its official track remains unresolved. Preserve the blocked migration, including its proposed FARE identity; do not import a second preprint identity.
- **Traceable evidence:** [https://arxiv.org/abs/2609.30982](https://arxiv.org/abs/2609.30982).

### B02 — LEGO: LoRA-Enabled Generator-Oriented Framework for Synthetic Image Detection

- **Scope:** `in_scope`. The arXiv abstract proposes generator-specific LoRA modules combined for binary synthetic-image detection. Generator-oriented features alone do not establish a source-attribution output.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:ab5d8660f748ca81dcc8`.
- **Identifiers:** arXiv [https://arxiv.org/abs/2605.04445](https://arxiv.org/abs/2605.04445).
- **Publication:** `preprint`; arXiv; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Yutong Xiao; Ran Ran; Jiwei Wei; Shuchang Zhou; Ke Liu; Zheng Ziqiang; Caiyan Qin.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Preserve arXiv preprint status. No official ACM Multimedia publication is verified. Preserve the arXiv ordered spelling Zheng Ziqiang, without merging author identities.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://arxiv.org/abs/2605.04445](https://arxiv.org/abs/2605.04445).

### B03 — Dinolizer: Separating VAE and Diffusion Artifacts in Generative Inpainting Localization

- **Scope:** `provisionally_in_scope`. Primary bibliographic title explicitly concerns passive localization of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `HELD_MANDATORY_EVIDENCE`; no curated or public identity created.
- **Identifiers:** Primary [https://wifs2026.utt.fr/technical-program](https://wifs2026.utt.fr/technical-program).
- **Publication:** `accepted_unpublished`; IEEE International Workshop on Information Forensics and Security; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Mandatory complete roster remains unresolved.
- **Taxonomy:** `tasks=localization; image_scopes=generative_editing; research_types=method`. Proposed only; not imported.
- **Metadata corrections / evidence:** Official WIFS technical program verifies exact title and paper ID 137. It provides no complete ordered author roster or formally published proceedings record. Do not label an accepted December conference paper as published.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Official WIFS technical program verifies exact title and paper ID 137. It provides no complete ordered author roster or formally published proceedings record. Do not label an accepted December conference paper as published.
- **Traceable evidence:** [https://wifs2026.utt.fr/technical-program](https://wifs2026.utt.fr/technical-program); [https://wifs2026.utt.fr/technical-program](https://wifs2026.utt.fr/technical-program).

### C01 — CAPN-Net: Category-Agnostic and Patch Noise feature fusion Network for universal AI-generated image detection

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `HELD_MANDATORY_EVIDENCE`; no curated or public identity created.
- **Identifiers:** DOI [https://doi.org/10.1016/j.ins.2026.124123](https://doi.org/10.1016/j.ins.2026.124123).
- **Publication:** `future_issue_online_date_unverified`; Information Sciences; year 2027.
- **Publication details:** `{"page": "124123", "published-print": {"date-parts": [[2027, 1]]}, "volume": "760"}`.
- **Ordered authors:** Jiayu Liang; Weisen Li; Dongdong Ling.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Proposed only; not imported.
- **Metadata corrections / evidence:** DOI registration verifies ordered authors, Information Sciences volume 760, article 124123, assigned January 25, 2027 issue. Publisher online-publication date remains unverified; neither issue date nor metadata deposit date establishes online publication.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** DOI registration verifies ordered authors, Information Sciences volume 760, article 124123, assigned January 25, 2027 issue. Publisher online-publication date remains unverified; neither issue date nor metadata deposit date establishes online publication.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.ins.2026.124123](https://api.crossref.org/works/10.1016/j.ins.2026.124123).

### C02 — Gradient-guided up-sampling artifacts-aware adapter tuning for generalizable AI-generated image detection

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `HELD_MANDATORY_EVIDENCE`; no curated or public identity created.
- **Identifiers:** DOI [https://doi.org/10.1016/j.eswa.2026.134292](https://doi.org/10.1016/j.eswa.2026.134292).
- **Publication:** `future_issue_online_date_unverified`; Expert Systems with Applications; year 2027.
- **Publication details:** `{"page": "134292", "published-print": {"date-parts": [[2027, 1]]}, "volume": "333"}`.
- **Ordered authors:** Zheng Zou; Dunlu Peng; Lin Cheng; Yuru Hou; Ping Kong; Yingzi Chen.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Proposed only; not imported.
- **Metadata corrections / evidence:** DOI registration and publisher preview verify ordered authors and ESWA volume 333, part G, assigned January 15, 2027 issue. Actual online-publication date is absent from retrieved publisher metadata.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** DOI registration and publisher preview verify ordered authors and ESWA volume 333, part G, assigned January 15, 2027 issue. Actual online-publication date is absent from retrieved publisher metadata.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.eswa.2026.134292](https://api.crossref.org/works/10.1016/j.eswa.2026.134292).

### C03 — MFF-Net: Multi-view feature fusion network for AI-generated image detection

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `HELD_MANDATORY_EVIDENCE`; no curated or public identity created.
- **Identifiers:** DOI [https://doi.org/10.1016/j.eswa.2026.134394](https://doi.org/10.1016/j.eswa.2026.134394).
- **Publication:** `future_issue_online_date_unverified`; Expert Systems with Applications; year 2027.
- **Publication details:** `{"page": "134394", "published-print": {"date-parts": [[2027, 2]]}, "volume": "334"}`.
- **Ordered authors:** Hongji Zhang; Hao Tan; Jinghui Qin; Zhijing Yang.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Proposed only; not imported.
- **Metadata corrections / evidence:** DOI registration and publisher preview verify ordered authors and ESWA volume 334, part A, assigned February 1, 2027 issue. Actual online-publication date is unverified.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** DOI registration and publisher preview verify ordered authors and ESWA volume 334, part A, assigned February 1, 2027 issue. Actual online-publication date is unverified.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.eswa.2026.134394](https://api.crossref.org/works/10.1016/j.eswa.2026.134394).

### D01 — REALIS: A Curated Dataset for Studying the Challenges of AI Image Detection

- **Scope:** `in_scope`. The primary abstract introduces REALIS and REALIS-Expert for real/generated image evaluation under generator and post-processing shifts, with a detector benchmark and robustness protocol.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:bdd256f857c0047ac00d`.
- **Identifiers:** arXiv [https://arxiv.org/abs/2609.32734](https://arxiv.org/abs/2609.32734).
- **Publication:** `preprint`; arXiv; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Aleksandr Gushchin; Khaled Abud; Georgii Bychkov; Ekaterina Shumitskaya; Artem Filippov; Sergey Lavrushkin; Dmitriy S. Vatolin; Anastasia Antsiferova.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=dataset;benchmark`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://arxiv.org/abs/2609.32734](https://arxiv.org/abs/2609.32734).

### D02 — Face-Trace: Open-Set Attribution and Progressive Discovery of Synthetic Face Generators

- **Scope:** `in_scope`. The paper evaluates classification, open-set rejection, and incremental discovery of synthetic face generators. Its forensic output is generator source attribution.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:32e56b1ac18747c951a2`.
- **Identifiers:** arXiv [https://arxiv.org/abs/2607.07545](https://arxiv.org/abs/2607.07545).
- **Publication:** `preprint`; arXiv; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Alessia Infantino; Claudio Schiavella; Irene Amerini.
- **Taxonomy:** `tasks=source_attribution; image_scopes=fully_generated;deepfake; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://arxiv.org/abs/2607.07545](https://arxiv.org/abs/2607.07545).

### D03 — Unleashing the Potential of Vision-Language Models for Generalizable AI-Generated Image Detection

- **Scope:** `in_scope`. The primary arXiv abstract studies vision-language representations for generalizable AI-generated image detection.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:e79726e40790ac447c01`.
- **Identifiers:** arXiv [https://arxiv.org/abs/2608.04935](https://arxiv.org/abs/2608.04935).
- **Publication:** `preprint`; arXiv; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Weihan Cai; Hao Tan; Zichang Tan; Jun Wan; Xinping Gao.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://arxiv.org/abs/2608.04935](https://arxiv.org/abs/2608.04935).

### D04 — RED: Reconstruction Evolution Dynamics for Generalizable AI-Generated Image Detection

- **Scope:** `in_scope`. The primary arXiv abstract uses reconstruction evolution dynamics to discriminate real and generated images without modifying their generator.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:d3fbbeb2cea34dd6544a`.
- **Identifiers:** arXiv [https://arxiv.org/abs/2609.36822](https://arxiv.org/abs/2609.36822).
- **Publication:** `preprint`; arXiv; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Wenpeng Mu; Junshan Jin; Tanfeng Sun; Xinghao Jiang; Qiang Xu.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://arxiv.org/abs/2609.36822](https://arxiv.org/abs/2609.36822).

### D05 — Relative Patch Response Learning for Generalizable AI-Generated Image Detection

- **Scope:** `in_scope`. The primary arXiv abstract proposes relative patch responses for generalizable real/generated image detection.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:19320688bf12e56a7559`.
- **Identifiers:** arXiv [https://arxiv.org/abs/2610.11876](https://arxiv.org/abs/2610.11876).
- **Publication:** `preprint`; arXiv; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Tianyu Wang; Ouxiang Li; Yanbin Hao; Zhenhua Tang; Shuo Wang.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://arxiv.org/abs/2610.11876](https://arxiv.org/abs/2610.11876).

### D06 — Unifying Semantic Priors and High-Frequency Traces: Enhancing V-JEPA with Mixture-of-Experts for Robust Synthetic Image Forensics

- **Scope:** `in_scope`. The primary paper evaluates MoE-JEPA on SID-Set with authentic, fully synthetic, and locally tampered images. Whole-image detection is supported; pixel-level localization is not established by the abstract. Generative-editing scope requires a further experimental check.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:a116171fee8869392bc0`.
- **Identifiers:** arXiv [https://arxiv.org/abs/2609.16778](https://arxiv.org/abs/2609.16778).
- **Publication:** `preprint`; arXiv; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Simone Teglia; Irene Amerini.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated;generative_editing; research_types=method`. Pending dimensions: `image_scopes`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: The abstract establishes fully synthetic evaluation and local tampering but does not disaggregate generative edits from conventional manipulation in the experimental results; review the proposed generative_editing label. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://arxiv.org/abs/2609.16778](https://arxiv.org/abs/2609.16778).

### E01 — Training-Free Detection of AI-Generated Images Based on Coherence Analysis of Image Representations

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `HELD_MANDATORY_EVIDENCE`; no curated or public identity created.
- **Identifiers:** DOI [https://doi.org/10.1145/3843205.3845630](https://doi.org/10.1145/3843205.3845630).
- **Publication:** `scheduled_publication`; Proceedings of the 2nd ACM Workshop on Deepfake, Deception, and Disinformation Security; year 2026.
- **Publication details:** `{"article_doi": "10.1145/3843205.3845630", "page": "14-21", "published-online": {"date-parts": [[2026, 11, 14]]}, "published-print": {"date-parts": [[2026, 11, 15]]}}`.
- **Ordered authors:** Ji Li; Kai Wang.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Proposed only; not imported.
- **Metadata corrections / evidence:** Crossref maps this exact article title and ordered Ji Li/Kai Wang authors to article DOI 10.1145/3843205.3845630 (not proceedings DOI). The registered online date is November 14, 2026, after this October 16 audit; the workshop program corroborates acceptance only. No supported accepted-only public representation is used.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Crossref maps this exact article title and ordered Ji Li/Kai Wang authors to article DOI 10.1145/3843205.3845630 (not proceedings DOI). The registered online date is November 14, 2026, after this October 16 audit; the workshop program corroborates acceptance only. No supported accepted-only public representation is used.
- **Traceable evidence:** [https://api.crossref.org/works/10.1145/3843205.3845630](https://api.crossref.org/works/10.1145/3843205.3845630); [https://sites.google.com/view/3d-sec2026/program](https://sites.google.com/view/3d-sec2026/program).

### E02 — MIDNet: Multi-Scale Interaction and Dynamic Hard-Sample Mining for AI-Generated Image Detection

- **Scope:** `in_scope`. The publisher-deposited abstract proposes multi-scale feature interaction and hard-sample mining, introduces a mixed-source AI-generated training dataset, and evaluates on seven detection benchmarks.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:e6b177863b0fbb08d1ba`.
- **Identifiers:** DOI [https://doi.org/10.1117/1.jei.35.5.053003](https://doi.org/10.1117/1.jei.35.5.053003).
- **Publication:** `published`; Journal of Electronic Imaging; year 2026.
- **Publication details:** `{"issue": "05", "page": "1-20", "published-print": {"date-parts": [[2026, 9, 2]]}, "volume": "35"}`.
- **Ordered authors:** Tian Zhang; Yuhan Liu; Gang Cao; Zhen Li; Weiheng Zhu.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method;dataset`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1117/1.jei.35.5.053003](https://api.crossref.org/works/10.1117/1.jei.35.5.053003).

### E03 — Dissecting Agentic Forensics: The Role of Triage, Prompting, and Evidence Arbitration in Open-World Fake Image Detection

- **Scope:** `in_scope`. The primary paper studies triage and evidence arbitration over specialist detectors for fully synthetic images and local manipulations. Detection is substantive. Arbitration is not generator attribution; pixel-localization metrics are not established by the abstract.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:5ad3a29da317a2763b68`.
- **Identifiers:** arXiv [https://arxiv.org/abs/2609.24359](https://arxiv.org/abs/2609.24359).
- **Publication:** `preprint`; arXiv; year 2026.
- **Publication details:** `{"acceptance_source": "data/raw/literature51_2026_10_16/request.txt", "reported_acceptance": "ECCV 2026 AI4MFDD Workshop"}`.
- **Ordered authors:** Xianlong Li; Pietro Bongini; Niccoló Pancino; Marco Blanchini; Benedetta Tondi; Mauro Barni.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=analysis_study`. Evidence-reviewed.
- **Metadata corrections / evidence:** Preserve arXiv status; the supplied audit identifies an ECCV AI4MFDD workshop association, which is retained in provenance rather than promoted to published proceedings. Evidence arbitration is not source attribution. No pixel-localization claim is imported.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://arxiv.org/abs/2609.24359](https://arxiv.org/abs/2609.24359).

### E04 — AIGen4Det: Leveraging AI-Regeneration for Generalizable Synthetic Facial Image Detection

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `HELD_MANDATORY_EVIDENCE`; no curated or public identity created.
- **Identifiers:** Primary [https://openreview.net/forum?id=uOQ4L7aU7y](https://openreview.net/forum?id=uOQ4L7aU7y).
- **Publication:** `workshop_identity_incomplete`; ECCV AI4MFDD Workshop; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Mandatory complete roster remains unresolved.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated;deepfake; research_types=method`. Proposed only; not imported.
- **Metadata corrections / evidence:** OpenReview landing page, API, and PDF each return a browser-verification challenge. Author-reported workshop presentation supports relevance, but original ordered authors and exact publication state cannot be established from the primary paper. No author ordering is reconstructed from social posts.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** OpenReview landing page, API, and PDF each return a browser-verification challenge. Author-reported workshop presentation supports relevance, but original ordered authors and exact publication state cannot be established from the primary paper. No author ordering is reconstructed from social posts.
- **Traceable evidence:** [https://openreview.net/forum?id=uOQ4L7aU7y](https://openreview.net/forum?id=uOQ4L7aU7y).

### E05 — ASAP: Visual Analytics for Identifying and Analyzing Image Patterns in AI-Generated Images

- **Scope:** `in_scope`. The publisher-deposited abstract describes a visual analytics system and user study for authenticity-indicative image patterns across GAN and diffusion benchmarks. It supports detection-related analysis, without claiming a conventional detector or generator-ID classifier.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:0fcf96be580a03a18f2b`.
- **Identifiers:** DOI [https://doi.org/10.1177/14738716261481077](https://doi.org/10.1177/14738716261481077).
- **Publication:** `published`; Information Visualization; year 2026.
- **Publication details:** `{"published-online": {"date-parts": [[2026, 9, 14]]}}`.
- **Ordered authors:** Jinbin Huang; Yuki Ueno; Chen Chen; Aditi Mishra; Bum Chul Kwon; Zhicheng Liu; Chris Bryan.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=analysis_study`. Evidence-reviewed.
- **Metadata corrections / evidence:** Retain analysis_study only: an interactive visual analytics system and user study, not a conventional binary detection method. Official deposited online date September 14, 2026.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1177/14738716261481077](https://api.crossref.org/works/10.1177/14738716261481077).

### E06 — Depth spectral fingerprints: AI-generated image detection via compact depth representations

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `HELD_MANDATORY_EVIDENCE`; no curated or public identity created.
- **Identifiers:** DOI [https://doi.org/10.1016/j.patrec.2026.09.024](https://doi.org/10.1016/j.patrec.2026.09.024).
- **Publication:** `future_issue_online_date_unverified`; Pattern Recognition Letters; year 2026.
- **Publication details:** `{"page": "20-25", "published-print": {"date-parts": [[2026, 12]]}, "volume": "210"}`.
- **Ordered authors:** Zihang Lyu; Zhuoyuan Li; Cong Zhang; Yun Li; Kin-Man Lam.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Proposed only; not imported.
- **Metadata corrections / evidence:** Crossref and publisher XML verify exact DOI/title and ordered Zihang Lyu, Zhuoyuan Li, Cong Zhang, Yun Li, Kin-Man Lam authors; PRL volume 210, pages 20–25, December 2026 issue. Publisher online-publication date and primary technical abstract remain unavailable; no online-first date is inferred from the DOI month.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Crossref and publisher XML verify exact DOI/title and ordered Zihang Lyu, Zhuoyuan Li, Cong Zhang, Yun Li, Kin-Man Lam authors; PRL volume 210, pages 20–25, December 2026 issue. Publisher online-publication date and primary technical abstract remain unavailable; no online-first date is inferred from the DOI month.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.patrec.2026.09.024](https://api.crossref.org/works/10.1016/j.patrec.2026.09.024).

### E07 — Can Pixels Alone Reveal Image Origin? Minimax Limits and Learnable Interfaces for Passive Provenance

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive source_attribution of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `BLOCKED_EXISTING_MIGRATION`; no curated or public identity created.
- **Identifiers:** arXiv [https://arxiv.org/abs/2609.30997](https://arxiv.org/abs/2609.30997).
- **Publication:** `accepted_track_unresolved`; Advances in Neural Information Processing Systems; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Kai Yao.
- **Taxonomy:** `tasks=source_attribution; image_scopes=fully_generated; research_types=analysis_study`. Proposed only; not imported.
- **Metadata corrections / evidence:** The immutable NeurIPS 7+1 migration includes this same arXiv identity. Keep its source_attribution/analysis_study determination and unresolved official track; do not bypass the lock by importing an arXiv duplicate.
- **Duplicate / historical handling:** Existing locked NeurIPS migration identity `curated:36755a9ffdcb1829037c` retained without application or duplicate preprint.
- **Outstanding:** The immutable NeurIPS 7+1 migration includes this same arXiv identity. Keep its source_attribution/analysis_study determination and unresolved official track; do not bypass the lock by importing an arXiv duplicate.
- **Traceable evidence:** [https://arxiv.org/abs/2609.30997](https://arxiv.org/abs/2609.30997).

### E08 — DSC2F: A Multimodal AI-Generated Image Detection System Using Dual-Stream Convolutional Neural Networks with Fast Fourier Transform

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:e9d23abcebd5c5decf52`.
- **Identifiers:** DOI [https://doi.org/10.1109/icivc70586.2026.11686669](https://doi.org/10.1109/icivc70586.2026.11686669).
- **Publication:** `published`; International Conference on Image, Vision and Computing; year 2026; track `Main`.
- **Publication details:** `{"page": "727-731", "published-print": {"date-parts": [[2026, 7]]}}`.
- **Ordered authors:** Tri-Vinh Nguyen; Khoa H.-A. Ngo; Khoi H.-A. Ngo.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1109/icivc70586.2026.11686669](https://api.crossref.org/works/10.1109/icivc70586.2026.11686669).

### E09 — Forged Image Model Attribution Based on Hierarchical Fine-Grained Classification

- **Scope:** `unresolved_generator_identity`. Primary bibliographic title explicitly concerns passive source_attribution of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `HELD_MANDATORY_EVIDENCE`; no curated or public identity created.
- **Identifiers:** DOI [https://doi.org/10.1109/icivc70586.2026.11686643](https://doi.org/10.1109/icivc70586.2026.11686643).
- **Publication:** `scope_evidence_insufficient`; International Conference on Image, Vision and Computing; year 2026.
- **Publication details:** `{"page": "714-720", "published-print": {"date-parts": [[2026, 7]]}}`.
- **Ordered authors:** Hui Yang; ShiYu Liu; Xiang Zhang; Wenbo Zhang; WenYong Zhang.
- **Taxonomy:** `tasks=source_attribution; image_scopes=fully_generated; research_types=method`. Proposed only; not imported.
- **Metadata corrections / evidence:** Crossref verifies exact article DOI/title and complete ordered authors, but IEEE serves an empty HTTP 202 response and targeted primary search yields no abstract. Actual generator/model-identity evaluation remains unverified, so conventional editing-tool attribution cannot be ruled out.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Crossref verifies exact article DOI/title and complete ordered authors, but IEEE serves an empty HTTP 202 response and targeted primary search yields no abstract. Actual generator/model-identity evaluation remains unverified, so conventional editing-tool attribution cannot be ruled out.
- **Traceable evidence:** [https://api.crossref.org/works/10.1109/icivc70586.2026.11686643](https://api.crossref.org/works/10.1109/icivc70586.2026.11686643).

### E10 — A Sanity Check for AI-Generated Underwater Image Detection

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:7666b05ad5d2877e6b2b`.
- **Identifiers:** DOI [https://doi.org/10.1109/icivc70586.2026.11686696](https://doi.org/10.1109/icivc70586.2026.11686696).
- **Publication:** `published`; International Conference on Image, Vision and Computing; year 2026; track `Main`.
- **Publication details:** `{"page": "721-726", "published-print": {"date-parts": [[2026, 7]]}}`.
- **Ordered authors:** Siyi Lv; Yutao Liu.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=analysis_study`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1109/icivc70586.2026.11686696](https://api.crossref.org/works/10.1109/icivc70586.2026.11686696).

### E11 — Robust AIGC Image Detection via Unidirectional Consistency Regularization

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:59c932990aa26f14dd49`.
- **Identifiers:** DOI [https://doi.org/10.1109/icivc70586.2026.11686594](https://doi.org/10.1109/icivc70586.2026.11686594).
- **Publication:** `published`; International Conference on Image, Vision and Computing; year 2026; track `Main`.
- **Publication details:** `{"page": "702-707", "published-print": {"date-parts": [[2026, 7]]}}`.
- **Ordered authors:** Yifan Yang.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1109/icivc70586.2026.11686594](https://api.crossref.org/works/10.1109/icivc70586.2026.11686594).

### E12 — Hierarchical Channel Stacking: A Structured Decision Framework for AI-Generated Image Detection

- **Scope:** `in_scope`. The primary arXiv abstract evaluates hierarchical channel stacking for real/generated image classification on GAN and diffusion sources. The matching Springer chapter supplies the formal publication identity.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:1afb38e9574a326e2173`.
- **Identifiers:** DOI [https://doi.org/10.1007/978-3-032-38407-2_23](https://doi.org/10.1007/978-3-032-38407-2_23); arXiv [https://arxiv.org/abs/2608.26648](https://arxiv.org/abs/2608.26648).
- **Publication:** `conference_online_first`; International Conference on Artificial Neural Networks; year 2027; track `Main`.
- **Publication details:** `{"online_date": "2026-09-14", "page": "285-297", "pages": "285–297", "print_year": 2027, "published-online": {"date-parts": [[2026, 9, 14]]}, "published-print": {"date-parts": [[2027]]}}`.
- **Ordered authors:** Saifullah Shoaib; Akash Borigi; Rupendra Lekkala; Amaury Lendasse; Edward Ratner; Sai Sowjanya Bhamidipati; Alexander Schlager; Peggy Lindner.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Resolve to chapter DOI 10.1007/978-3-032-38407-2_23, pages 285–297; never use the volume DOI as an article DOI. The chapter deposit verifies eight authors in the same order as arXiv. Preserve 2027 print/citation year and September 14, 2026 online date for ICANN 2026.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://link.springer.com/chapter/10.1007/978-3-032-38407-2_23](https://link.springer.com/chapter/10.1007/978-3-032-38407-2_23); [https://arxiv.org/abs/2608.26648](https://arxiv.org/abs/2608.26648).

### E13 — RFF-Net: Robust frequency–noise fusion network for AI-generated image discrimination

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `HELD_MANDATORY_EVIDENCE`; no curated or public identity created.
- **Identifiers:** DOI [https://doi.org/10.1016/j.knosys.2026.117106](https://doi.org/10.1016/j.knosys.2026.117106).
- **Publication:** `future_issue_online_date_unverified`; Knowledge-Based Systems; year 2026.
- **Publication details:** `{"page": "117106", "published-print": {"date-parts": [[2026, 10]]}, "volume": "352"}`.
- **Ordered authors:** Yuntong Xu; Ronggui Yang; Shengyuan Zhou.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Proposed only; not imported.
- **Metadata corrections / evidence:** Crossref and publisher XML verify DOI/title and authors; KBS volume 352, article 117106, issue October 25, 2026. That date is after this audit and no actual online-publication date was recovered.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Crossref and publisher XML verify DOI/title and authors; KBS volume 352, article 117106, issue October 25, 2026. That date is after this audit and no actual online-publication date was recovered.
- **Traceable evidence:** [https://api.crossref.org/works/10.1016/j.knosys.2026.117106](https://api.crossref.org/works/10.1016/j.knosys.2026.117106).

### E14 — One Patch Is Not Enough: A General Framework for Full-Resolution AI Image Detection

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:7f89e638ec42dfb2324d`.
- **Identifiers:** DOI [https://doi.org/10.1109/lsp.2026.3737389](https://doi.org/10.1109/lsp.2026.3737389).
- **Publication:** `published`; IEEE Signal Processing Letters; year 2026.
- **Publication details:** `{"page": "1-5", "published-print": {"date-parts": [[2026]]}}`.
- **Ordered authors:** Yakun Niu; Yingjian Chen; Lei Zhang; Baojun Qiao.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1109/lsp.2026.3737389](https://api.crossref.org/works/10.1109/lsp.2026.3737389).

### E15 — Hyperparameter-Aware Evaluation of Deep Learning Architectures for AI-Generated Image Detection

- **Scope:** `provisionally_in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `HELD_MANDATORY_EVIDENCE`; no curated or public identity created.
- **Identifiers:** Primary [https://tudoster.unideb.hu/en/szerzok/5404](https://tudoster.unideb.hu/en/szerzok/5404).
- **Publication:** `accepted_metadata_incomplete`; IEEE Conference on Information Technology and Data Science; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Mandatory complete roster remains unresolved.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=analysis_study`. Proposed only; not imported.
- **Metadata corrections / evidence:** The supplied University of Debrecen page reports Accepted by Publisher and pages 1–6 for Gafarov, I.; Qasem, Z.; Düzenli, K.; Harangi, B.; Al-Hamadani, M. N. A. Complete original author names and official proceedings/publication state remain unresolved. No DOI is invented.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** The supplied University of Debrecen page reports Accepted by Publisher and pages 1–6 for Gafarov, I.; Qasem, Z.; Düzenli, K.; Harangi, B.; Al-Hamadani, M. N. A. Complete original author names and official proceedings/publication state remain unresolved. No DOI is invented.
- **Traceable evidence:** [https://tudoster.unideb.hu/en/szerzok/5404](https://tudoster.unideb.hu/en/szerzok/5404); [data/raw/literature51_2026_10_16/priority_identity.json](../data/raw/literature51_2026_10_16/priority_identity.json).

### E16 — S-AODP++: Structure-Aware AOI-Guided Scanpath Attention for AI-Generated Image Identification

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:ab051450a8b2338c4575`.
- **Identifiers:** DOI [https://doi.org/10.1145/3776574.3831124](https://doi.org/10.1145/3776574.3831124).
- **Publication:** `published`; International Conference on Multimodal Interaction; year 2026; track `Main`.
- **Publication details:** `{"page": "123-130", "published-online": {"date-parts": [[2026, 10, 4]]}, "published-print": {"date-parts": [[2026, 10, 5]]}}`.
- **Ordered authors:** Jingming Wang; Renwei Meng; Yunjie Si.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Crossref publisher deposit verifies article DOI, October 4, 2026 online publication and author order Jingming Wang; Renwei Meng; Yunjie Si. The supplied author website independently agrees. Co-first status does not reorder names.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://api.crossref.org/works/10.1145/3776574.3831124](https://api.crossref.org/works/10.1145/3776574.3831124); [https://renweimeng.com/en](https://renweimeng.com/en).

### E17 — Improving Synthesized Image Detection by Disentangling Generator-Shared and Generator-Specific Image Artifacts

- **Scope:** `in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:fa41c2810887fb216f5d`.
- **Identifiers:** Primary [https://openaccess.thecvf.com/content/CVPR2026F/html/Yang_Improving_Synthesized_Image_Detection_by_Disentangling_Generator-Shared_and_Generator-Specific_Image_CVPRF_2026_paper.html](https://openaccess.thecvf.com/content/CVPR2026F/html/Yang_Improving_Synthesized_Image_Detection_by_Disentangling_Generator-Shared_and_Generator-Specific_Image_CVPRF_2026_paper.html).
- **Publication:** `published`; IEEE/CVF Conference on Computer Vision and Pattern Recognition; year 2026; track `Findings`.
- **Publication details:** `{}`.
- **Ordered authors:** Yongqi Yang; Yuke Li; Heng Huang; Zhihui Li; Bo Du; Yu Wu.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Pending dimensions: `tasks, image_scopes, research_types`.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** Taxonomy review: Only the publisher-registered title was recoverable for taxonomy; confirm the proposed labels against the primary abstract/full paper. manual_review=true in the batch audit. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://openaccess.thecvf.com/content/CVPR2026F/html/Yang_Improving_Synthesized_Image_Detection_by_Disentangling_Generator-Shared_and_Generator-Specific_Image_CVPRF_2026_paper.html](https://openaccess.thecvf.com/content/CVPR2026F/html/Yang_Improving_Synthesized_Image_Detection_by_Disentangling_Generator-Shared_and_Generator-Specific_Image_CVPRF_2026_paper.html).

### E18 — Latent Optimization Dynamics for Latent Diffusion Model Attribution

- **Scope:** `provisionally_in_scope`. Primary bibliographic title explicitly concerns passive detection of AI-generated images. Taxonomy is provisional until checked against a technical abstract or full paper.
- **Import:** `HELD_MANDATORY_EVIDENCE`; no curated or public identity created.
- **Identifiers:** Primary [https://openreview.net/forum?id=r46D1lErlM](https://openreview.net/forum?id=r46D1lErlM).
- **Publication:** `workshop_identity_incomplete`; ECCV AI4MFDD Workshop; year 2026.
- **Publication details:** `{}`.
- **Ordered authors:** Mandatory complete roster remains unresolved.
- **Taxonomy:** `tasks=detection; image_scopes=fully_generated; research_types=method`. Proposed only; not imported.
- **Metadata corrections / evidence:** The supplied author repository confirms a VAE detector inspired by AEROBLADE/LatentTracer. OpenReview landing/API/PDF return challenges. An author post describes binary real/synthetic experiments, but the primary ordered author roster and Dahlgren spelling cannot be verified. Do not assign source_attribution from the title alone.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** The supplied author repository confirms a VAE detector inspired by AEROBLADE/LatentTracer. OpenReview landing/API/PDF return challenges. An author post describes binary real/synthetic experiments, but the primary ordered author roster and Dahlgren spelling cannot be verified. Do not assign source_attribution from the title alone.
- **Traceable evidence:** [https://openreview.net/forum?id=r46D1lErlM](https://openreview.net/forum?id=r46D1lErlM); [https://github.com/dahlgrenmartin/LOD](https://github.com/dahlgrenmartin/LOD).

### E19 — Asymmetric Anchoring: Opening the MLLM Black Box for Forgery Detection

- **Scope:** `in_scope`. The official Springer abstract evaluates detection and localization on SID-Set and OpenSDID. Synthetic-image and generative-editing evaluation is substantive, rather than a conventional splicing-only scope.
- **Import:** `NEWLY_IMPORTED`; stable ID `curated:c5e97e3e4756545a70ff`.
- **Identifiers:** DOI [https://doi.org/10.1007/978-3-032-37132-4_2](https://doi.org/10.1007/978-3-032-37132-4_2).
- **Publication:** `published`; European Conference on Computer Vision; year 2026; track `Main`.
- **Publication details:** `{}`.
- **Ordered authors:** Zhiqiang Yang; Renshuai Tao; Chunjie Zhang; Zhaoxiang Liu; Xiaolong Zheng; Yao Zhao.
- **Taxonomy:** `tasks=detection;localization; image_scopes=fully_generated;generative_editing; research_types=method`. Evidence-reviewed.
- **Metadata corrections / evidence:** Ordered authors and article identity verified against the cited primary bibliographic metadata. No affiliations or coordinates assigned.
- **Duplicate / historical handling:** No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.
- **Outstanding:** No mandatory bibliographic blocker. Affiliations remain unresolved; no map location assigned.
- **Traceable evidence:** [https://doi.org/10.1007/978-3-032-37132-4_2](https://doi.org/10.1007/978-3-032-37132-4_2).

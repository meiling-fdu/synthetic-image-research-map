# Targeted Ant/AI-edit literature gap-fill audit — 2026-09-05

## Scope and result

This was a closed-set reconciliation against the 576-paper authoritative public
corpus. No broad literature search was performed. The candidate boundary was
the saved Ant Research `Awesome-AIGC-Image-Video-Detection` audit set plus the
previously confirmed AI-edit cases. Identity checks were applied in the required
order: DOI, arXiv ID, OpenAlex ID, normalized exact title, method/acronym, then
fuzzy title only when necessary.

| Decision | Count |
|---|---:|
| `MISSING_ADD` | 37 |
| `EXISTING_CURRENT` | 2 |
| `EXISTING_UPDATE_NEEDED` | 0 |
| `EXCLUDE_OUT_OF_SCOPE` | 15 |
| `AMBIGUOUS` | 1 |
| **Total** | **55** |

Primary snapshot: [Ant Research Awesome-AIGC-Image-Video-Detection](https://github.com/ant-research/Awesome-AIGC-Image-Video-Detection).

## Added papers

All 37 additions have reviewed Taxonomy v2 `tasks`, `image_scopes`, and
`research_types`, authoritative abstract/PDF evidence, canonical author rosters,
and source-backed author–institution relationships. Formal publisher metadata
is preferred where verified; otherwise the record remains explicitly a preprint.

1. **GIM: A Million-Scale Benchmark for Generative Image Manipulation Detection and Localization** — arXiv:2406.16531; AAAI 2025; DOI 10.1609/aaai.v39i2.32231.
2. **FakeShield: Explainable Image Forgery Detection and Localization via Multi-Modal Large Language Models** — arXiv:2410.02761; ICLR 2025.
3. **So-Fake: Benchmarking Social-Media Image Forgery Detection** — arXiv:2505.18660.
4. **Ivy-Fake: A Unified Explainable Framework and Benchmark for Image and Video AIGC Detection** — arXiv:2506.00979.
5. **BusterX++: Towards Unified Cross-Modal AI-Generated Content Detection and Explanation with MLLM** — arXiv:2507.14632.
6. **DF-LLaVA: Unlocking MLLMs for Synthetic Image Detection via Knowledge Injection and Conflict-Driven Self-Reflection** — arXiv:2509.14957.
7. **Seeing Before Reasoning: A Unified Framework for Generalizable and Explainable Fake Image Detection** — arXiv:2509.25502.
8. **OmniAID: Decoupling Semantics and Artifacts for Universal AI-Generated Image Detection in the Wild** — arXiv:2511.08423.
9. **Explainable AI-Generated Image Detection RewardBench** — arXiv:2511.12363.
10. **DINO-Detect: A Simple yet Effective Framework for Blur-Robust AI-Generated Image Detection** — arXiv:2511.12511.
11. **DiffSeg30k: A Multi-Turn Diffusion Editing Benchmark for Localized AIGC Detection** — arXiv:2511.19111.
12. **AlignGemini: Generalizable AI-Generated Image Detection Through Task-Model Alignment** — arXiv:2512.06746.
13. **Simplicity Prevails: The Emergence of Generalizable AIGI Detection in Visual Foundation Models** — arXiv:2602.01738.
14. **MIRROR: Manifold Ideal Reference ReconstructOR for Generalizable AI-Generated Image Detection** — arXiv:2602.02222.
15. **Fake-HR1: Rethinking Reasoning of Vision Language Model for Synthetic Image Detection** — arXiv:2602.10042.
16. **TranX-Adapter: Bridging Artifacts and Semantics Within MLLMs for Robust AI-Generated Image Detection** — arXiv:2602.21716.
17. **AgentFoX: LLM-Driven Agentic Multi-Expert Fusion with Explainability for AI-Generated Image Detection** — arXiv:2603.23115.
18. **DocShield: Towards AI Document Safety via Evidence-Grounded Agentic Reasoning** — arXiv:2604.02694.
19. **SciFigDetect: A Benchmark for AI-Generated Scientific Figure Detection** — arXiv:2604.08211.
20. **AEGIS: A Holistic Benchmark for Evaluating Forensic Analysis of AI-Generated Academic Images** — arXiv:2604.28177.
21. **FraudBench: A Multimodal Benchmark for Detecting AI-Generated Fraudulent Refund Evidence** — arXiv:2605.08820.
22. **Venus-DeFakerOne: Unified Fake Image Detection & Localization** — arXiv:2605.14091.
23. **Reduce the Artifact Bias for More Generalizable AI-Generated Image Detection** — arXiv:2605.14486.
24. **Video as Natural Augmentation: Towards Unified AI-Generated Image and Video Detection** — arXiv:2605.21977.
25. **HydraPrompt: An Adaptive and Asymmetric Framework of Vision-Language Models for Synthetic Image Detection** — arXiv:2605.26421.
26. **SSAFE: Simple and Strong AI-Generated Image Detection via Frozen Vision Encoders** — arXiv:2606.08634.
27. **Fleet: Few Shots Lead Effective AI-Generated Image Detection** — arXiv:2606.31082.
28. **GlobalForge: Towards Robust AI-Generated Image Detection** — arXiv:2607.14684.
29. **Veritas++: Value-Aware On-Policy Distillation for Perception-Enhanced AIGI Detection** — arXiv:2607.27113.
30. **PatchHead: Learning Spatial Patch Evidence for Generalizable AI-Generated Image Detection** — arXiv:2608.09223.
31. **Structured Local Differential Modeling for AI-Generated Image Detection** — arXiv:2608.12811.
32. **SPARED: Reasoning-Based AI-Generated Image Detection via Adversarially Edited Data** — arXiv:2608.12876.
33. **Defake-O3: From Speculative Rationales to Verifiable Evidence for Explainable AIGI Detection** — arXiv:2608.16259.
34. **Training-Free Reconstruction-Based AI-Generated Image Detectors Are Inherently Vulnerable to Adversarial Examples** — arXiv:2608.16646.
35. **Frozen DINO Localizes Image Edits Without a Localizer** — arXiv:2608.18968.
36. **GAP-SAM: A Global Artifact Prior for Generalizable AI-Generated Image Manipulation Localization** — arXiv:2608.20929.
37. **FUSED: Forensic-Semantic Mixture-of-Experts for AI Inpainting Detection and Localization** — arXiv:2608.28302.

Formal sources verified for the two published additions:
[GIM at AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/32231) and
[FakeShield at ICLR](https://proceedings.iclr.cc/paper_files/paper/2025/hash/4d4e0ab9d8ff180bf5b95c258842d16e-Abstract-Conference.html).

## Existing identities

1. **Zoom-In to Sort AI-Generated Images Out** is arXiv:2510.04225 and resolves
   to the existing **Locate-Then-Examine: Grounded Region Reasoning Improves
   Detection of AI-Generated Images** record (`curated:cf55e35fcf11e09fdd12`).
2. **D3QE: Learning Discrete Distribution Discrepancy-aware Quantization Error
   for Autoregressive-Generated Image Detection** resolves by method acronym,
   arXiv:2510.05891, and title normalization to the existing formal ICCV record
   (`curated:3e94d8fc69e41aade2cc`), DOI 10.1109/iccv51701.2025.01512.

Neither identity was added again. No existing paper required a bibliographic
update.

## Excluded candidates

1. **AGIDefect-4K** (arXiv:2608.20713) — generator defect/quality diagnosis,
   not authenticity detection.
2. **LADBench** (arXiv:2606.17433) — logical-anomaly/quality reasoning, not
   image authenticity forensics.
3. **GPT-Image-2 in the Wild** (arXiv:2604.25370) — collection and
   characterization without a forensic task or benchmark.
4. **Veritas: Generalizable Deepfake Detection via Pattern-Aware Reasoning**
   (arXiv:2508.21048) — deepfake-only face forensics.
5. **BusterX** (arXiv:2505.12620) — video-only AIGC detection.
6. **DDL** (arXiv:2506.23292) — deepfake-only image/video dataset.
7. **DF40** (arXiv:2406.13495) — deepfake-only benchmark/detector study.
8. **Explainable Deepfake Detection with Feature-robust Augmentation and
   Evidence-grounded Explanation Optimization** (arXiv:2608.20913) —
   deepfake-only.
9. **PATE-Forensics** (arXiv:2608.18573) — deepfake-only forensic framework.
10. **VIGIL** (arXiv:2603.21526) — deepfake-only reasoning detector.
11. **Environment-Invariant Subspace Learning for Generalizable Deepfake
    Detection** (arXiv:2608.17700) — deepfake-only.
12. **Forensics Adapter** (arXiv:2411.19715) — face-forgery-only.
13. **Exploring Unbiased Deepfake Detection via Token-Level Shuffling and
    Mixing** (arXiv:2501.04376) — deepfake-only.
14. **FakeFormer** (arXiv:2410.21964) — deepfake-only.
15. **AIGuard: A Benchmark and Lightweight Detection for E-commerce AIGC
    Risks** — AIGC risk/content classification, not generated-image
    authenticity detection or source attribution. Publisher identity:
    DOI 10.18653/v1/2025.findings-acl.643.

All 15 decisions are retained in `paper_exclusions.csv` with source identity,
reason, review note, audit date, and creator provenance. None matched or removed
an unrelated baseline public paper.

## Ambiguous candidate

**NeXT-IMDL: Build Benchmark for NeXT-Generation Image Manipulation Detection &
Localization** (arXiv:2512.23374) is substantively in scope, but arXiv marks it
withdrawn, provides no current PDF, and records the withdrawal note “Duplicate
experiment results in Table 3 (Set-1 & Set-2).” It remains `AMBIGUOUS` and was
not inserted into the authoritative corpus. [Current arXiv record](https://arxiv.org/abs/2512.23374).

## Corpus and taxonomy totals

| Measure | Before | Final | Delta |
|---|---:|---:|---:|
| Public papers | 576 | 613 | +37 |
| Papers with a public map location | 570 | 607 | +37 |
| Distinct map-paper identities | 571 | 608 | +37 |
| Map records | 1,307 | 1,403 | +96 |

Taxonomy is multi-label, so dimension totals exceed the number of papers.

| Dimension | Label | Before | Final | Delta |
|---|---|---:|---:|---:|
| Tasks | detection | 542 | 577 | +35 |
| Tasks | source_attribution | 76 | 77 | +1 |
| Tasks | localization | 7 | 18 | +11 |
| Image scopes | fully_generated | 491 | 521 | +30 |
| Image scopes | generative_editing | 14 | 25 | +11 |
| Image scopes | deepfake | 158 | 161 | +3 |
| Image scopes | traditional_manipulation | 9 | 13 | +4 |
| Research types | method | 496 | 527 | +31 |
| Research types | dataset | 96 | 112 | +16 |
| Research types | benchmark | 54 | 69 | +15 |
| Research types | survey | 23 | 23 | 0 |
| Research types | analysis_study | 42 | 58 | +16 |

The registry contains exactly 613 identities, matches all 613 public paper
records and all 1,403 map records, and has zero taxonomy review cases.

## Integrity and idempotence

- Reconstructed the preservation-safe 576-paper/1,307-map-record baseline from
  the pre-gap curated snapshot, then matched it against the final export. All
  576 baseline paper identities survived, and all 576 complete paper record
  dictionaries were unchanged. The final-minus-baseline identity set contains
  exactly the 37 additions above.
- Pre-existing curated rows were compared by stable ID. There were zero missing
  or changed pre-gap paper, mapping, exclusion, taxonomy, location-review, or
  institution-audit rows. New rows comprise 37 papers, 121 mappings, 15
  exclusions, 37 taxonomy decisions, 22 institution identities, 24
  location-review rows, and the explicit non-institutional audit for Chenzhuo
  Zhao.
- Validation reconciled the new `CSIRO` acronym to the pre-existing Commonwealth
  Scientific and Industrial Research Organisation entity and reused its
  confirmed location. SSAFE's KAIST relationship reuses the repository's
  existing cached ROR resolution for Daejeon. No institution was created for
  Chenzhuo Zhao, whose paper explicitly lists “Independent Researcher.”
- A curation rerun produced 0 papers, mappings, taxonomy rows, exclusions,
  independent-author reviews, institution merges, or locations. A subsequent
  preservation-safe export retained identical SHA-256 hashes:
  `56a38a9d4332b1e938ea78caef28522290b2fae55f8c03855709929a432e8eee`
  (papers) and
  `6dee0c6d480f2209b4a2bc308a30b09057454ee1adf3f7b8710a27898a9184da`
  (map).

## Validation results

- Curated database: 17/17 files, 0 errors, 0 duplicate candidates. Historical
  and provenance warnings remain non-blocking.
- Paper exclusions: 53 rows, 47 active, 47 absent from public outputs, 0 stale
  public records, 0 errors. Two pre-existing restored-record warnings remain.
- Taxonomy: 613/613 public identities, 1,403/1,403 map records, 0 review cases.
- Public preview: 613 papers, 1,403 map records, 608 distinct map-paper
  identities; 0 errors and 0 map warnings. Eleven documented pre-existing
  partial-author-index warnings remain; none belongs to the 37 additions.
- Paper metadata consistency: 613 papers × 18 fields = 11,034 rows; 0 true
  inconsistencies, 0 legacy-fallback risks, 0 affiliation mismatches, and 0
  retired-institution leaks.
- Duplicate curated-paper identities: 0.
- JavaScript syntax: every `web/*.js` file passed the bundled Node parser.
- `git diff --check`: passed.
- Full test suite: **1,310 passed, 58 skipped** in 268.07 seconds. An earlier
  run's sole three-second loopback timeout passed in isolation; the final full
  run with loopback access was clean.

## Task-owned files changed

- Curated data: `papers.csv`, `paper_taxonomy.csv`, `paper_exclusions.csv`,
  `author_institution_mappings.csv`, `institutions.csv`,
  `institution_aliases.csv`, `institution_locations.csv`,
  `institution_location_review.csv`, and `institution_audit_log.csv`.
- Preserved raw evidence: `data/raw/ant_gap_fill_2026_09_05/`.
- Reproducible curation: `scripts/curate_ant_gap_fill_2026_09_05.py`.
- Public exports: `web/data/public_preview_papers.json` and
  `web/data/public_preview_map_data.json`.
- Regenerated reports: `docs/paper_taxonomy_migration_audit_2026-09-04.md`,
  `docs/public_preview_report.md`, `docs/missing_author_mappings_report.md`,
  `data/processed/missing_author_mappings_report.csv`, the public relationship,
  metadata-consistency, metadata-status, and link-conflict audit artifacts, and
  this report.
- Reviewed integration baselines/tests: `tests/baseline_expectations.py`,
  taxonomy, affiliation-evidence, publication-filter, location-audit,
  metadata-consistency, metadata-status, and repository-baseline assertions.

The pre-existing `data/manual/missing_author_mappings_report.csv` was restored
to the reconstructed 576-paper baseline; the new automated report is written to
`data/processed/` instead.

# Batch B Wave B1O — R267/R236 research contributions accepted

Maintainer adjudication was applied locally on 2026-10-25 and recovered on 2026-10-26. Published predecessor `9581e17cc1dd78384966009b7f2d767b1961e3b6`. This prefix records the accepted transaction; the complete original evidence-only report follows **verbatim**. Its original pending flags, source observations, timestamps, failed transports and retrieval accounting remain historical evidence.

## Recovered state and export approval boundary

The authoritative edits and two terminal decisions had survived the usage-limit interruption. Their actual contents were compared with the published predecessor and reused without reapplying corrections or appending duplicate decisions. The recovered existing transaction changes 14 semantic cells across four existing target CSV rows and appends exactly two decisions to the 97-row registry (99 afterward). The applied timestamp is the persisted terminal-row creation time `2026-10-25T15:29:55Z`; the unavailable original completion receipt is not reconstructed as historical fact.

The earlier `/private/tmp/b1o-evidence-2026-10-25/` and adjudication temporary directories were absent at recovery. The raw manuscripts, old wrapper and standalone receipts could not be independently rehashed in place. Their scientific findings, source fingerprints and receipt summaries remain embedded in the intact evidence packet; no new downloads or primary review were performed. Both complete original evidence files are also preserved losslessly as deterministic gzip+base64 archives in the manifest.

A narrow raw CSV preservation repair restored original embedded-newline bytes in sixteen unrelated rows without changing any parsed scientific record; its separate informational receipt remains outside the commit. This restores byte preservation rather than applying unrelated metadata changes.

Original export approval outcome: **automatic approval review failed at a usage limit before execution**, rather than an exporter exit-code failure or an unsafe-action determination. The command was not counted as run. The same complete gate command was reconstructed transparently from the prior tool-call source and submitted through the legitimate `require_escalated` approval mechanism. The original on-disk wrapper hash is unavailable; its identity is not invented. Subsequent approval and execution results are recorded separately below and in the manifest.

## R267 — accepted analysis-study addition

**Are High-Quality AI-Generated Images More Difficult for Models to Detect?**, `curated:7693a9c0107feaf90e10`: **method → method;analysis_study**. Accepted outcome **PROPOSE_CORRECTION_ACCEPTED**. Exactly one original research-type action closes through **`review:b9f458d69de24b8aae0a`** under locked **R3**. The original **detection** task and **fully_generated** scope remain unchanged; the substantive patch-selection method remains.

Official ICML 2025 PMLR manuscript: **22 pages, ten publisher authors**, source SHA-256 **`01986259aeeaad807fd4034fa59783dd3d4615045ced2db50545788f566b2358`**. Sections 3–4 independently study image-quality/preference-model scores, detection correctness, prompt content/length, visual features, clustering, regression and detector-specific sensitivity before Section 5 applies regression-guided patch selection. That primary systematic investigation remains informative without the proposed patch method and meets R3 independently.

Four generators comprise the principal study; six appear in the expanded source inventory. Learned preference scores are not direct human judgments or photorealism. Detector correctness is not prediction confidence. Within-generator associations and in-sample fitted regressions do not prove causality, a universal relationship, or independently evaluated predictive generalization. Prompt/content/source dependencies and generator confounding remain. RINE average precision **90.2 → 91.9** accompanies accuracy **75.0 → 74.2**, so no uniform improvement across metrics is claimed. Other detector-specific exceptions and sensitivity experiments remain in the original evidence.

Contribution-role confidence is **high**, empirical interpretation confidence **medium**, operational reproducibility confidence **low**. The inspected author repository contained README/license metadata without a verified implementation. Exact checkpoints, full source/data overlap, complete numerical reproduction, random seeds and confidence-interval evidence remain limited or unverified. Canonical authors and all bibliography are preserved, including the separately recorded out-of-scope author-format observation.

## R236 — one atomic dataset, benchmark and analysis-study resolution

**Unveiling Perceptual Artifacts: A Fine-Grained Benchmark for Interpretable AI-Generated Image Detection**, `curated:64635535d7b7b6a12a32`: **method → method;dataset;benchmark;analysis_study**. Accepted outcome **PROPOSE_CORRECTION_ACCEPTED**. Exactly one original research-type action closes through **`review:aa32e93a24ade10ed99d`**, covering locked **R1, R2 and R3** together rather than creating three actions. Existing **method**, **detection;localization** and **fully_generated** remain.

Official ICLR 2026 publisher manuscript: **29 pages, eleven authors**, SHA-256 **`3604416a9a60e895da2f3d789763f9477f7cbfcf8ef6976e16bb57abbfbbd3b7`**. The original literal title-match failure receipt and separate successful normalized-title/full-source recovery verification remain preserved. The earlier author-deposited arXiv v1 body was not exhaustively compared with this publisher version; whole-version equivalence is not claimed.

- **R1:** X-AIGD is an independently reusable human-curated polygon/category resource, beyond ordinary method samples: **4,000 reused real images**, **13 generator sources**, and **18,285 artifact instances**. These instances are not image counts. Main Section 3.2 reports **3,035 annotated fake images**, while Table 8 and inspected release metadata report **3,337 labeled rows**. Their population discrepancy remains unresolved, with both original source locators preserved; no reconciled image count is inferred.
- **R2:** Separately reusable authenticity judgment, artifact-category and spatial evaluation tasks, ground truth, pixel/category/weak-instance scoring, independent external baselines, generalization protocols and standalone metrics/viewer code establish a benchmark independently of the dataset contribution. Joint segmentation **IoU 27.3 / pixel F1 42.8** differs from classifier heatmap **IoU 4.8 / pixel F1 9.2**. Their heads, ground truth, thresholding and protocols remain distinguished.
- **R3:** The primary systematic detector–artifact alignment and fidelity investigation in Sections 4–5 remains informative independently of Section 6’s alignment method. It studies detector/category differences, spatial explanations, fidelity, supervision and controls rather than only demonstrating the proposed method.

Artifact or attention overlap is **not proof of causal detector reliance, necessity or explanation faithfulness**. Spatial localization and explanatory fidelity remain distinct. Architecture, training data, additional supervision and explanation operators are possible confounds. Chameleon accuracy **71.4 → 71.2** is counterevidence to universal improvement; some generic-mask controls also improve results. Weak-instance selection uses **≥** in the manuscript and **>** in the inspected implementation, an unresolved paper/code discrepancy. Category-specific counterexamples remain in the original evidence.

Contribution-role confidence is **high**; empirical/mechanistic interpretation and operational reproducibility remain **medium/limited**. Full image assets, sample-level split membership, upstream image rights and licensing are not independently verified. Public metadata and standalone metrics/viewer availability are not equivalent to complete asset release. Training/experiment code remained **TODO**, and end-to-end numerical reproduction was not demonstrated.

## T236 and other review boundaries

T236’s finalized **detection;localization**, **fully_generated** state, original author-v1 task rationale, evidence and historical resolution remain unchanged. That resolution exists in the structured Batch C task record, not as a literal terminal `review_decisions.csv` row. No T236 row was invented, no task action reopened or reclosed, and publisher-version research-type evidence did not replace its task provenance. All unrelated pending reviews, including evidence-insufficient R234, Batch C’s 13 deferred debts and the separate 39-paper inventory remain unchanged.

## Authoritative and public semantic delta

`data/curated/papers.csv` changes only `research_types` in the two canonical rows. `data/curated/paper_taxonomy.csv` changes only those two rows’ research types and the necessary research-type review reason, primary evidence tier/source/excerpt and audit date. Total existing semantic cells changed: **14**, across **four existing rows**. Compatibility, task evidence, tasks, image scopes, bibliography, authors, affiliations and institutions are preserved. `data/curated/review_decisions.csv` retains its complete published 97-row prefix byte-for-byte and appends the two existing recovered terminal rows exactly once. The established `no_action_after_review` vocabulary means the accepted bounded correction is completed, not that no data changed.

The actual public semantic check is **PASS**: exactly R267 and R236 change research-type metadata; all other **672** public paper records are semantically unchanged. **9** directly dependent existing map rows change research-type metadata/direct provenance. All **1,410 relationship identities** remain unchanged. No public paper or institution is added or removed, no bibliography changes, and no task or scope changes.

## Recomputed current corpus and Batch B accounting

| Measure | Current value |
| --- | ---: |
| public | 674 |
| formal | 557 |
| mapped | 613 |
| relationship_rows | 1,410 |
| unique_paper_institution_pairs | 1,410 |
| unmapped | 61 |

| Taxonomy | Current count |
| --- | ---: |
| detection | 621 |
| source_attribution | 84 |
| localization | 45 |
| method | 578 |
| dataset | 138 |
| benchmark | 95 |
| survey | 21 |
| analysis_study | 84 |

| Batch B measure | Recomputed count |
| --- | ---: |
| historical_actions | 159 |
| historical_papers | 148 |
| historical_unresolved_actions | 135 |
| historical_unresolved_papers | 125 |
| active_public_unresolved_actions | 133 |
| active_public_unresolved_papers | 123 |

Exactly two original actions close. The original 159-action / 148-paper denominators remain fixed; remaining distinct paper counts were recomputed from the complete ledger, not inferred by subtracting two from prior paper totals. Both independent questions on multi-action papers remain independent.

## Retrieval, validation, preservation and publication

Original retrieval accounting remains **two complete official manuscripts**, one per paper, from **five transport attempts**. The original partial responses, aborted range attempt and title-check clarification remain historical evidence. There were **zero new scientific downloads during recovery or adjudication**. No source was silently substituted or historical receipt rewritten.

Required current transaction validation: **PASS**. Explicit approval was required and obtained through the legitimate `require_escalated` mechanism for the complete offline exporter command; the authorized initial export and two sequential verification exports completed successfully. The original usage-limit approval refusal remains a separate, unexecuted event. The following successful command results are preserved separately from the originally declined, unexecuted command. Earlier evidence-stage checks remain historical results. Only validation receipts, gate status and this paragraph changed after the final-state full suite; original scientific findings, accepted edits, counts, public outputs and the complete evidence-stage report remain unchanged. Final post-stamp protection and receipt checks bind the delivered bytes externally.

```json
{
  "status": "PASS",
  "completed_at_utc": "2026-10-26T03:13:13.601487+00:00",
  "FOCUSED_FAILURES": 0,
  "VALIDATOR_ERRORS": 0,
  "FULL_SUITE_FAILURES": 0,
  "EXPORT_REPRODUCIBLE": 1,
  "exports_run": 3,
  "full_suite_runs": 1,
  "focused": {
    "name": "focused",
    "exit_code": 0,
    "command": [
      "/private/tmp/b1o-adjudication-2026-10-25/test-venv/bin/python",
      "-m",
      "pytest",
      "-q",
      "tests/test_corpus_quality_batch_b_wave_b1o.py",
      "tests/test_corpus_quality_batch_b_wave_b1n.py",
      "tests/test_corpus_quality_batch_b_wave_b1h.py",
      "tests/test_corpus_quality_batch_b_wave_b1i.py",
      "tests/test_repository_baseline.py",
      "tests/test_review_decision_idempotence.py",
      "tests/test_historical_test_fixtures.py",
      "tests/test_public_refinement_successors.py",
      "tests/test_historical_integrity_successors.py",
      "tests/test_literature51_reproducibility.py",
      "-o",
      "cache_dir=/private/tmp/b1o-adjudication-2026-10-25/pytest-cache",
      "--junitxml=/private/tmp/b1o-adjudication-2026-10-25/focused.xml"
    ],
    "head": "9581e17cc1dd78384966009b7f2d767b1961e3b6",
    "log": "/private/tmp/b1o-adjudication-2026-10-25/focused.log",
    "log_sha256": "aaea0cf98efa78474e343cc157cca9b484171672ff5d739af8f4894e3a465ef3",
    "started_at_utc": "2026-10-26T02:58:33.878559+00:00",
    "completed_at_utc": "2026-10-26T02:59:27.198261+00:00",
    "elapsed_seconds": 53.319,
    "passed": 161,
    "subtests_passed": 12,
    "junit": {
      "tests": 173,
      "failures": 0,
      "errors": 0,
      "skipped": 0,
      "sha256": "9b511aaeb9817457ae6ae2ffb74f049c3de59a2ae779ef80fd049049a9cbc75e"
    },
    "errors": [],
    "validator_warnings": []
  },
  "B1O_regression_cases": 36,
  "validators": {
    "curated": {
      "name": "curated",
      "exit_code": 0,
      "command": [
        "/private/tmp/b1o-adjudication-2026-10-25/test-venv/bin/python",
        "scripts/validate_curated_database.py"
      ],
      "head": "9581e17cc1dd78384966009b7f2d767b1961e3b6",
      "log": "/private/tmp/b1o-adjudication-2026-10-25/curated.log",
      "log_sha256": "6af912003cea9f0ff841062b66ff98f3152cf23ecb70a68a04af7fe2fbea75dd",
      "started_at_utc": "2026-10-26T02:53:10.289653+00:00",
      "completed_at_utc": "2026-10-26T02:53:16.107199+00:00",
      "elapsed_seconds": 5.817,
      "errors": [
        0
      ],
      "validator_warnings": [
        294
      ]
    },
    "public": {
      "name": "public",
      "exit_code": 0,
      "command": [
        "/private/tmp/b1o-adjudication-2026-10-25/test-venv/bin/python",
        "scripts/validate_public_preview.py"
      ],
      "head": "9581e17cc1dd78384966009b7f2d767b1961e3b6",
      "log": "/private/tmp/b1o-adjudication-2026-10-25/public.log",
      "log_sha256": "84ed5a622291a93a89b16c5407cd03ce7e3a891f84a4cc1d4caa6e7b2171749a",
      "started_at_utc": "2026-10-26T02:53:10.286854+00:00",
      "completed_at_utc": "2026-10-26T02:53:16.753872+00:00",
      "elapsed_seconds": 6.467,
      "errors": [
        0,
        0
      ],
      "validator_warnings": [
        0,
        62
      ]
    },
    "exclusions": {
      "name": "exclusions",
      "exit_code": 0,
      "command": [
        "/private/tmp/b1o-adjudication-2026-10-25/test-venv/bin/python",
        "scripts/validate_paper_exclusions.py"
      ],
      "head": "9581e17cc1dd78384966009b7f2d767b1961e3b6",
      "log": "/private/tmp/b1o-adjudication-2026-10-25/exclusions.log",
      "log_sha256": "1fadfe0741a198eaf009a4c2dc08fc234e7b451238157f8e1709960fe9732513",
      "started_at_utc": "2026-10-26T02:53:10.288390+00:00",
      "completed_at_utc": "2026-10-26T02:53:12.741342+00:00",
      "elapsed_seconds": 2.453,
      "errors": [
        0
      ],
      "validator_warnings": [
        2
      ]
    },
    "coverage": {
      "name": "coverage",
      "exit_code": 0,
      "command": [
        "/private/tmp/b1o-adjudication-2026-10-25/test-venv/bin/python",
        "scripts/audit_key_paper_coverage.py",
        "--check"
      ],
      "head": "9581e17cc1dd78384966009b7f2d767b1961e3b6",
      "log": "/private/tmp/b1o-adjudication-2026-10-25/coverage.log",
      "log_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "started_at_utc": "2026-10-26T02:53:10.292945+00:00",
      "completed_at_utc": "2026-10-26T02:53:12.258490+00:00",
      "elapsed_seconds": 1.965,
      "errors": [],
      "validator_warnings": []
    }
  },
  "full": {
    "name": "full",
    "exit_code": 0,
    "command": [
      "/private/tmp/b1o-adjudication-2026-10-25/test-venv/bin/python",
      "-m",
      "pytest",
      "-q",
      "tests",
      "-o",
      "cache_dir=/private/tmp/b1o-adjudication-2026-10-25/pytest-cache",
      "--junitxml=/private/tmp/b1o-adjudication-2026-10-25/full.xml"
    ],
    "head": "9581e17cc1dd78384966009b7f2d767b1961e3b6",
    "log": "/private/tmp/b1o-adjudication-2026-10-25/full.log",
    "log_sha256": "08e038ee5adbd885a6e529950b970af5542b74bb51a4af07d763ae8a95b8420a",
    "started_at_utc": "2026-10-26T03:00:17.718496+00:00",
    "completed_at_utc": "2026-10-26T03:08:34.271024+00:00",
    "elapsed_seconds": 496.552,
    "passed": 2202,
    "warnings": 2,
    "subtests_passed": 389,
    "junit": {
      "tests": 2591,
      "failures": 0,
      "errors": 0,
      "skipped": 0,
      "sha256": "05564d0a1e5611422844df3fb73a15ffbb84b8c87c95d5e84bf94390355094bc"
    },
    "errors": [],
    "validator_warnings": []
  },
  "initial_export": {
    "name": "initial-export",
    "exit_code": 0,
    "command": [
      "/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3",
      "scripts/refresh_public_preview.py",
      "--skip-search",
      "--user-agent",
      "SyntheticImageResearchMap/0.1 (offline Batch B B1O adjudication)"
    ],
    "head": "9581e17cc1dd78384966009b7f2d767b1961e3b6",
    "log": "/private/tmp/b1o-adjudication-2026-10-25/initial-export.log",
    "log_sha256": "ea22983b88f7eaf373a1c6656e0905f014b753dc6a8819a74836fa2c2d1f72c8",
    "started_at_utc": "2026-10-26T02:50:34.010161+00:00",
    "completed_at_utc": "2026-10-26T02:51:51.963469+00:00",
    "elapsed_seconds": 77.953,
    "errors": [
      0,
      0
    ],
    "validator_warnings": [
      0,
      62
    ]
  },
  "two_sequential_export_verification": {
    "status": "PASS",
    "started_at_utc": "2026-10-26T03:09:42.593890+00:00",
    "baseline_commit": "9581e17cc1dd78384966009b7f2d767b1961e3b6",
    "full_suite_runs_by_this_verifier": 0,
    "full_suite_result_sha256": "15dda38594294cf618dd8fecd56c84e730ba61032fa640de3896f20fde95f6b2",
    "full_suite_input_inventory_sha256": "bc1d09339c33cb9d7107c7f928015fdbd1c7d4cbf19c91bbe9a4952c50afdbe2",
    "full_suite_input_paths_unchanged": true,
    "compared_path_count": 4635,
    "generated_outputs": [
      "web/data/public_preview_papers.json",
      "web/data/public_preview_map_data.json",
      "docs/public_preview_report.md",
      "docs/missing_author_mappings_report.md",
      "data/manual/missing_author_mappings_report.csv",
      "docs/key_paper_coverage_report.md",
      "data/manual/key_paper_coverage_report.csv"
    ],
    "passes": [
      {
        "pass": 1,
        "exit_code": 0,
        "gate": {
          "name": "export-pass-1",
          "exit_code": 0,
          "command": [
            "/private/tmp/b1o-adjudication-2026-10-25/test-venv/bin/python",
            "scripts/refresh_public_preview.py",
            "--skip-search",
            "--user-agent",
            "SyntheticImageResearchMap/0.1 (offline Batch B B1O adjudication)"
          ],
          "head": "9581e17cc1dd78384966009b7f2d767b1961e3b6",
          "log": "/private/tmp/b1o-adjudication-2026-10-25/export-pass-1.log",
          "log_sha256": "880613febdd40994189f2577f70ae94d247dcdfafc6cd499e350baa584ac669d",
          "started_at_utc": "2026-10-26T03:09:43.578864+00:00",
          "completed_at_utc": "2026-10-26T03:11:02.277970+00:00",
          "elapsed_seconds": 78.699,
          "errors": [
            0,
            0
          ],
          "validator_warnings": [
            0,
            62
          ]
        },
        "elapsed_seconds": 79.873,
        "inventory_path": "/private/tmp/b1o-adjudication-2026-10-25/export-pass-1-inventory.json",
        "inventory_sha256": "bc1d09339c33cb9d7107c7f928015fdbd1c7d4cbf19c91bbe9a4952c50afdbe2",
        "changed_paths": [],
        "compared_path_count": 4635,
        "output_sha256": {
          "web/data/public_preview_papers.json": "42548755bc37f52b25d07243f1eec3ec3d5f9e603f708f39d98b828e4121739e",
          "web/data/public_preview_map_data.json": "952747b4a3e160526d66f980dfaa9b7d8f1800268b6e1c9c308413f13f9e6e47",
          "docs/public_preview_report.md": "923979e4950b730bc8d4834945aeeac8e451e7af175319a16c1b83883ca85bdc",
          "docs/missing_author_mappings_report.md": "37d7455e8b0b0ef3d0c46e261a35bbc11f0b862b313e1ec77b5f65acdb01e11d",
          "data/manual/missing_author_mappings_report.csv": "3d5d447d90bf064346d8ccb2583685c59ce7fc8d8131330155cb9994ec83421d",
          "docs/key_paper_coverage_report.md": "11ce6ccc581ae738a702c15e4498b189442be3fe981259004d7cbcd6bdaa4fdf",
          "data/manual/key_paper_coverage_report.csv": "dbe1bd75e8d619a3a28354df1bccd79037f0aa281de49a37bbb49d3937d75099"
        }
      },
      {
        "pass": 2,
        "exit_code": 0,
        "gate": {
          "name": "export-pass-2",
          "exit_code": 0,
          "command": [
            "/private/tmp/b1o-adjudication-2026-10-25/test-venv/bin/python",
            "scripts/refresh_public_preview.py",
            "--skip-search",
            "--user-agent",
            "SyntheticImageResearchMap/0.1 (offline Batch B B1O adjudication)"
          ],
          "head": "9581e17cc1dd78384966009b7f2d767b1961e3b6",
          "log": "/private/tmp/b1o-adjudication-2026-10-25/export-pass-2.log",
          "log_sha256": "880613febdd40994189f2577f70ae94d247dcdfafc6cd499e350baa584ac669d",
          "started_at_utc": "2026-10-26T03:11:03.455819+00:00",
          "completed_at_utc": "2026-10-26T03:12:20.023184+00:00",
          "elapsed_seconds": 76.565,
          "errors": [
            0,
            0
          ],
          "validator_warnings": [
            0,
            62
          ]
        },
        "elapsed_seconds": 77.681,
        "inventory_path": "/private/tmp/b1o-adjudication-2026-10-25/export-pass-2-inventory.json",
        "inventory_sha256": "bc1d09339c33cb9d7107c7f928015fdbd1c7d4cbf19c91bbe9a4952c50afdbe2",
        "changed_paths": [],
        "compared_path_count": 4635,
        "output_sha256": {
          "web/data/public_preview_papers.json": "42548755bc37f52b25d07243f1eec3ec3d5f9e603f708f39d98b828e4121739e",
          "web/data/public_preview_map_data.json": "952747b4a3e160526d66f980dfaa9b7d8f1800268b6e1c9c308413f13f9e6e47",
          "docs/public_preview_report.md": "923979e4950b730bc8d4834945aeeac8e451e7af175319a16c1b83883ca85bdc",
          "docs/missing_author_mappings_report.md": "37d7455e8b0b0ef3d0c46e261a35bbc11f0b862b313e1ec77b5f65acdb01e11d",
          "data/manual/missing_author_mappings_report.csv": "3d5d447d90bf064346d8ccb2583685c59ce7fc8d8131330155cb9994ec83421d",
          "docs/key_paper_coverage_report.md": "11ce6ccc581ae738a702c15e4498b189442be3fe981259004d7cbcd6bdaa4fdf",
          "data/manual/key_paper_coverage_report.csv": "dbe1bd75e8d619a3a28354df1bccd79037f0aa281de49a37bbb49d3937d75099"
        }
      }
    ],
    "historical_fixture_before": {
      "command": [
        "/private/tmp/b1o-adjudication-2026-10-25/test-venv/bin/python",
        "scripts/restore_historical_test_fixtures.py",
        "--check"
      ],
      "exit_code": 0,
      "log": "/private/tmp/b1o-adjudication-2026-10-25/export-fixtures-before.log",
      "log_sha256": "29e270c07d9d80fadf406d09c082f7fc0cf5f64caeb81bd90b0d6984c500a5bd",
      "verified_inputs": 117,
      "created": 0,
      "mode": "check"
    },
    "historical_fixture_after": {
      "command": [
        "/private/tmp/b1o-adjudication-2026-10-25/test-venv/bin/python",
        "scripts/restore_historical_test_fixtures.py",
        "--check"
      ],
      "exit_code": 0,
      "log": "/private/tmp/b1o-adjudication-2026-10-25/export-fixtures-after.log",
      "log_sha256": "29e270c07d9d80fadf406d09c082f7fc0cf5f64caeb81bd90b0d6984c500a5bd",
      "verified_inputs": 117,
      "created": 0,
      "mode": "check"
    },
    "EXPORT_REPRODUCIBLE": 1,
    "export_invocations_completed": 2,
    "completed_at_utc": "2026-10-26T03:12:23.074210+00:00"
  },
  "integrity": {
    "PREEXISTING_LOCAL_FILES_CHANGED": 0,
    "FROZEN_NEURIPS_CHANGED": 0,
    "UNEXPECTED_CHANGED": 0,
    "IGNORED_OPERATIONAL_INPUTS_COMMITTED": 0
  },
  "protection_checks": {
    "passed": 126,
    "failed": 0,
    "receipt": {
      "path": "/private/tmp/b1o-adjudication-2026-10-25/protection-after-exports.json",
      "sha256": "a409e1b0bb268e3777aad15573e18c958fd8a18561f6a9d297238d64d352ec24"
    }
  },
  "independent_semantic_checks": {
    "passed": 1470,
    "failed": 0,
    "receipt": {
      "path": "/private/tmp/b1o-adjudication-2026-10-25/independent-semantic.json",
      "sha256": "3da611b92451d6223f37d6ce517763854a8ec401e5ec91c1d25d2ff97627b11d"
    }
  },
  "independent_precommit_checks": {
    "passed": 28,
    "receipt": {
      "path": "/private/tmp/b1o-adjudication-2026-10-25/precommit-independent-review.json",
      "sha256": "9690884127fa0de2672be73a90090db1bd58d8b9cd4e6a9f99b336b3c511099e"
    }
  },
  "test_environment": {
    "python": "/private/tmp/b1o-adjudication-2026-10-25/test-venv/bin/python",
    "base_python": "/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3",
    "env_overrides": {
      "PYTHONDONTWRITEBYTECODE": "1",
      "PATH": "/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:/Applications/ChatGPT.app/Contents/Resources/codex-cli/codex-path:/opt/homebrew/bin:/Users/meilinger/.local/bin:/Users/meilinger/.local/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/pkg/env/global/bin:/Library/TeX/texbin:/Users/meilinger/.codex/tmp/arg0-macos/codex-arg0J4Z5HH:/Applications/ChatGPT.app/Contents/Resources/codex-cli/codex-path:/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override:/Users/meilinger/.local/bin:/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback:/Applications/ChatGPT.app/Contents/Resources:/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS"
    },
    "versions": {
      "python": "3.12.14 (main, Aug 25 2026, 13:50:33) [Clang 22.1.3 ]",
      "pytest": "9.1.1",
      "pytest_subtests": "0.15.0"
    },
    "node": "/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node",
    "node_version": "v24.22.1",
    "historical_fixture_check": {
      "exit_code": 0,
      "verified_inputs": 117,
      "created": 0,
      "path": "/private/tmp/b1o-adjudication-2026-10-25/historical-fixture-check.json",
      "sha256": "29e270c07d9d80fadf406d09c082f7fc0cf5f64caeb81bd90b0d6984c500a5bd"
    },
    "localhost_permission": "User explicitly authorizes established localhost test environment; root must use require_escalated for full suite, preserving automatic approval. No server started by this environment check.",
    "test_dependencies_install": {
      "scope": "Disposable TMP venv only",
      "exit_code": 0,
      "requirements": "requirements-test.txt",
      "network_approval": "require_escalated accepted",
      "scientific_downloads": 0
    }
  },
  "full_suite_input_inventory": {
    "path": "/private/tmp/b1o-adjudication-2026-10-25/full-suite-inputs.json",
    "sha256": "bc1d09339c33cb9d7107c7f928015fdbd1c7d4cbf19c91bbe9a4952c50afdbe2"
  },
  "full_suite_input_integrity": {
    "status": "PASS",
    "baseline": "/private/tmp/b1o-adjudication-2026-10-25/full-suite-inputs.json",
    "baseline_sha256": "bc1d09339c33cb9d7107c7f928015fdbd1c7d4cbf19c91bbe9a4952c50afdbe2",
    "compared_path_count": 4635,
    "changed_paths": [],
    "new_groups": {
      "tracked": 4492,
      "untracked": 3,
      "ignored": 140
    }
  },
  "recovery_approval": {
    "status": "RECOVERED_NOT_EXECUTED",
    "prior_command": "python3 /private/tmp/b1o-adjudication-2026-10-25/run_gate.py initial-export /Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/refresh_public_preview.py --skip-search --user-agent SyntheticImageResearchMap/0.1 (offline Batch B B1O adjudication)",
    "prior_tool_outcome": "Automatic approval review failed: usage limit; action was not executed because automatic approval review could not be completed. This was a review failure, not a determination that the action was unsafe.",
    "export_exit_status": null,
    "original_operational_directories_present_at_resume": false,
    "original_wrapper_file_available": false,
    "wrapper_recovery": "Reconstructed same path, purpose and source from prior tool-call source; original on-disk hash unavailable, no historical hash invented.",
    "reconstructed_wrapper_sha256": "e0ca85267542d106dcfc28423901a9b82aa7d9a069fa9b20a909da4433aa234e",
    "legitimate_approval_mechanism": "exec_command sandbox_permissions=require_escalated; retry the same complete reviewed command through approval, no bypass.",
    "existing_initial_export_receipt": false,
    "public_outputs_match_published_baseline": true,
    "resubmission": {
      "mechanism": "Same complete command submitted with exec_command sandbox_permissions=require_escalated; automatic review permitted execution.",
      "status": "AUTHORIZED_AND_COMPLETED",
      "command_changed_to_evade_review": false,
      "initial_export_result": {
        "name": "initial-export",
        "exit_code": 0,
        "command": [
          "/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3",
          "scripts/refresh_public_preview.py",
          "--skip-search",
          "--user-agent",
          "SyntheticImageResearchMap/0.1 (offline Batch B B1O adjudication)"
        ],
        "head": "9581e17cc1dd78384966009b7f2d767b1961e3b6",
        "log": "/private/tmp/b1o-adjudication-2026-10-25/initial-export.log",
        "log_sha256": "ea22983b88f7eaf373a1c6656e0905f014b753dc6a8819a74836fa2c2d1f72c8",
        "started_at_utc": "2026-10-26T02:50:34.010161+00:00",
        "completed_at_utc": "2026-10-26T02:51:51.963469+00:00",
        "elapsed_seconds": 77.953,
        "errors": [
          0,
          0
        ],
        "validator_warnings": [
          0,
          62
        ]
      },
      "initial_export_result_sha256": "6527c371d09abe4bd0223de15ec1de1eed094d89e2d8542234a7588bb011da77",
      "original_refusal_preserved_at": "/private/tmp/b1o-adjudication-2026-10-25/approval-recovery-before-execution.json",
      "original_refusal_sha256": "ae6d82e9de6c4d27d0d6a911d9b37cd95547815b25e59bbd7498bbd1a4c2e971"
    }
  },
  "scientific_source_downloads_during_adjudication_and_recovery": 0,
  "receipt_boundary": "These successful gates bind the stabilized scientific data, test code and outputs. Later validation-only packet metadata is independently verified without rerunning the full suite or claiming prospective publication."
}
```

Publication is not claimed by this packet before a successful normal fast-forward push and independent remote verification. The containing commit’s SHA and parent, exact staged inventory/statistics and remote synchronization are recorded in external publication receipts and the final response, avoiding circular self-reference. Required final state: one permitted commit, local HEAD equal to fetched origin/main, ahead/behind 0/0, isolated tracked working tree and index clean, and primary checkout unchanged. No force push or new review wave is permitted.

Preservation requires **UNEXPECTED_CHANGED = 0**, **FROZEN_NEURIPS_CHANGED = 0**, **PREEXISTING_LOCAL_FILES_CHANGED = 0**, and **IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0**. All 128 protected primary files, 49 frozen NeurIPS artifacts, prior decisions, historical fixtures, ignored operational inputs and concurrent worktrees remain protected. The originally published evidence-only zero-authoritative-change flag below describes that historical stage; the accepted transaction deliberately changes exactly the two approved research-type records.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

---

## Complete original evidence-only report — preserved verbatim

# Batch B Wave B1O: ICML quality paradox and ICLR perceptual artifacts

Evidence-only scientific review dated 2026-10-25. The only original research-type candidates are **R267** and **R236**. Every proposed classification remains pending maintainer acceptance. No terminal decision, authoritative correction, task change, export, commit or push is authorized or applied.

## Baseline and accounting

The existing isolated evidence worktree was fetched and verified at `9581e17cc1dd78384966009b7f2d767b1961e3b6`; HEAD equals fetched origin/main, with ahead/behind 0/0. The primary checkout and all unrelated worktrees are preserved.

| Measure | Recomputed unchanged value |
|---|---:|
| public | 674 |
| formal | 557 |
| mapped | 613 |
| unmapped | 61 |
| relationship_rows | 1,410 |
| unique_paper_institution_pairs | 1,410 |

| Taxonomy | Recomputed unchanged count |
|---|---:|
| detection | 621 |
| source_attribution | 84 |
| localization | 45 |
| method | 578 |
| dataset | 137 |
| benchmark | 94 |
| survey | 21 |
| analysis_study | 82 |

Batch B remains **159 original actions / 148 papers**, **137 historical unresolved actions / 127 papers**, and **135 active-public unresolved actions / 125 papers**. The 97-row terminal registry is unchanged. Evidence sufficiency does not close an action or decrement either unresolved population.

## Locked scientific rules

Source: `data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json`; accepted 2026-10-05. The following rules are reproduced without alteration.

**R1**: Assign dataset only when construction, release, curation, or systematic provision of a reusable dataset/data resource is itself a substantive paper contribution. Data generated or collected solely to run the paper's experiments is insufficient.

**R2**: Assign benchmark only when the paper contributes a reusable evaluation benchmark, challenge, protocol, systematic comparative framework, or benchmark resource intended to evaluate methods. Large experimental tables or evaluation across many generators alone are insufficient.

**R3**: Assign analysis_study only when systematic empirical or theoretical analysis is a primary scientific contribution. Routine ablations, robustness tables, parameter sweeps, or supporting interpretability figures do not qualify by themselves.

R267 is bounded to the original R3 addition question; its existing `method` role is retained. R236 remains one atomic original action, with separate R1/R2/R3 findings and one provisional complete type set. Any independent role must meet its own rule.

## Preserved task decision and source boundary

T236 was resolved in Batch C Wave 5B using the author-deposited arXiv 2601.19430v1 HTML manuscript. Its published structured action, resolution, finalization flag and current taxonomy provenance remain unchanged. No literal T236 terminal-registry row exists, and none is invented here. Existing tasks remain `detection;localization`, scope `fully_generated`; this research-type review neither reopens nor re-closes T236.

The earlier task packet reported PAD-only IoU 27.2 and pixel F1 42.7, with joint-model IoU 27.3 and pixel F1 42.8. Those are preserved author-v1 evidence values. The current wave separately identifies any new official source and compares only material actually available; it does not silently equate versions or interpret scored localization alone as an R2 benchmark contribution.

Old temporary operation directories were already absent when this wave began. Published portable histories were recovered without inventing missing bodies or checksums. The local-first source inventories and failed transports are explicitly retained in the manifest.

## R267 — Primary-source R3 evidence review

**Are High-Quality AI-Generated Images More Difficult for Models to Detect?** (`curated:7693a9c0107feaf90e10`). Current types remain `method`, task `detection`, scope `fully_generated`. The original R267 research-type action remains pending.

### Source identity and preserved history

Official [PMLR record](https://proceedings.mlr.press/v267/xiao25g.html) and [proceedings PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/xiao25g/xiao25g.pdf): ICML 2025, PMLR 267, proceedings pages 68491–68512. The downloaded PDF has 22 pages numbered 1–22, 13,757,845 bytes, SHA-256 `01986259aeeaad807fd4034fa59783dd3d4615045ced2db50545788f566b2358`. Its metadata and first page identify all ten authors: Yao Xiao, Binbin Yang, Weiyan Chen, Jiahao Chen, Zijie Cao, Ziyi Dong, Xiangyang Ji, Liang Lin, Wei Ke, Pengxu Wei. PDF creation/modification metadata is 2025-06-06. OpenReview and other-version byte equivalence is unverified.

All 22 pages were read, including implementation details, controls, interventions and qualitative examples. Rendered pages 1,5,6,8,9,15,16,18,19 were inspected for identities, numerical tables and curve qualifications. The complete PDF/extracted text remain outside Git.

The B1H packet originally obtained zero complete manuscripts and left 14 questions unverified. Its original record and five failed/partial/parser/HEAD/challenge operations remain preserved. Old B1H TMP files are absent; the published historical record is retained. The new local-first search inspected 8,367 files including 2,121 gzip objects and 110 PDF locations / 48 unique parsed PDFs; none matched a complete R267 manuscript. The bounded search excludes files over 200 MB and records inaccessible unrelated files rather than claiming universal coverage.

The new first publisher transport failed before sending request bytes or receiving an HTTP response/body. A single explicitly authorized IPv4 correction of the same official URL obtained the complete manuscript. Both receipts remain separate: two transport attempts, one newly complete manuscript; no alternate complete version, automatic retry, supplement, data payload or checkpoint download.

### Locked policy and provisional roles

Assign analysis_study only when systematic empirical or theoretical analysis is a primary scientific contribution. Routine ablations, robustness tables, parameter sweeps, or supporting interpretability figures do not qualify by themselves.

**Provisional R3 outcome: `ANALYSIS_STUDY_ADDITION_SUPPORTED`. Proposed complete types: `method;analysis_study`.** The core inquiry and first three contributions establish an empirical study of preference-score/detectability association. Sections3–4 analyze it before Section5 treats patch inference as an application. The analysis remains informative without the patch method.

The justification rests on the evaluated within-generator study, prompt/content associations, cluster r/p statistics, pooled regression with source adjustment, external generator/proxy controls and interventions/counterexamples (pp.2–7,13–19). Existing method is retained; neither an R4 removal nor an R1/R2 expansion is authorized. This is a scientific proposal, not maintainer acceptance, a terminal decision or applied remediation.

### Twenty required scientific questions

#### 1. The main research hypothesis

The primary question asks whether generated images assigned higher learned human-preference scores are harder for binary image detectors. The main result is a positive aggregate score–correctness association, especially above each generator’s score-density peak. Sections 3–4 investigate it before Section 5 applies the results to patch selection.

Evidence: pp1–2 introduction/contributions; pp3–7 Sections3–4; p9 conclusion.

Limitations: This is a tendency over selected populations, not a universal image-level rule or a causal law.

#### 2. Formal definitions of perceived image quality

Quality is operationalized through pretrained image-and-text human-preference predictors, rather than a new psychophysical definition. The authors distinguish individual-image assessment from FID/IS distribution measures. Such scores may mix visual appeal and prompt alignment; neither is identical to photorealism, absence of forensic artifacts or human authenticity accuracy.

Evidence: p3 Sections2.2/3.1; p14 AppendixB2.

Limitations: No new direct human-quality rating panel, human authenticity experiment or separately calibrated photorealism measurement is reported.

#### 3. Human-preference predictors and their versions

Main analyses use ImageReward (Xu 2023) and Human Preference Score v2 (Wu2023a); Appendix B1 adds MPS (Zhang2024b). Images and original generation prompts normally form the scoring inputs. Appendix B2 replaces the score-input prompt with the generated image’s BLIP-2 caption, while clustering uses empty text in ImageReward.

Evidence: p3 Section3.1; p13 AppendixA2; pp14–17 AppendicesB1–B2;Figures6–11.

Limitations: The paper names families/publication versions but does not pin exact checkpoint revisions, hashes, several preprocessing settings or MPS dimension selection. No model weights were obtained.

#### 4. Exact text-to-image generator families

The main four models are Stable Diffusion2.1, SDXL1.0, Stable Diffusion3 and PixArt-alpha. Appendices A1/B1 add FLUX.1[dev] and Infinity, covering diffusion/transformer and autoregressive generation. Auxiliary user-created closed-source samples are Midjourneyv6 and DALLE3; they are not another controlled generation of the same 4000 prompts.

Evidence: p3 Section3.1; pp13–16 AppendicesA1/B1;Figures6–9.

Limitations: Exact checkpoint commits, inference steps, guidance values, seeds and negative/modifier strings are not printed. HF metadata declares some fields but their actual row values were not inspected.

#### 5. Prompt sources and prompt-length distribution

COCO, CC3M, LAION-Aesthetic and SA-1B supply original image content. Captions come from BLIP-2, InternVL2-8B with varied instructions, existing COCO captions and existing SA-1B captions. Filtering and length balancing produce 4000 captions, spanning under10 to over 120 words. The paper groups short prompts<=20, medium21–40 and long>40 words.

Evidence: pp3–5 Sections3.1/4.1;Figure3; p13 AppendixA1; pp18,20–22 AppendicesB3/C.

Limitations: Per-bin counts, source proportions, exact filtering rules and captioner instructions are unspecified. Medium prompts can score above the shortest prompts; the result is not simply shorter-is-always-better.

#### 6. Source-image and prompt-content dependencies

Each of 4000 prompts is used once for each of six generators, implying 24000 synthetic images; the author-linked HF card independently declares 24000 fake rows, without verifying their contents. Corresponding real images join clustering but are omitted from subsequent fake-image analyses. The manuscript says generated images match paired-real compression format/quality.

Evidence: p13 AppendicesA1–A2; HF metadata revision9244882a51dbe33e658fe514488692155d20e5dd.

Limitations: 4000 captions do not establish 4000 UNIQUE source photographs or statistically independent prompts. Source reuse, multiple caption variants, prompt groups and their dependencies are not exhaustively identified or deduplicated.

#### 7. Detector identities and training provenance

The six principal detector variants are NPR, RINE, CoDE, SuSy, DRCT(Conv-B) and DRCT(CLIP), run with official pretrained weights/configurations and commonly center-cropped without resizing. Section5 additionally evaluates SSP, retrained on the GenImage all-generator mixture with claimed real/fake compression alignment after poor transfer from official single-generator checkpoints. Main averages contain five end-to-end variants and NPR; patch tests contain seven variants, including two fingerprint methods.

Evidence: pp3–4 Section3.1; pp7–9 Section5/Table3; p14 AppendixA5.

Limitations: Exact weight hashes, all original training-image identities and training overlap are not enumerated. No checkpoints/training data were retrieved. An averaged score trend is not proof of the same relation for every individual detector.

#### 8. Image-quality score distributions

Figures1/6/8 show per-generator preference-score histograms and average correctness curves. Figures2/7/9 reverse grouping by the0–6 detectors making correct predictions on each generated image. Section3.2 uses30 equal-width score-range segments. Distributions and trends differ by generator and preference model; several low-score ranges and MPS curves are visibly nonmonotonic.

Evidence: p1 Figure1; p4 Section3.2/Figure2; pp15–16 Figures6–9.

Limitations: Exact bin counts, point data and uncertainty are not tabulated. No precise values are inferred from unlabelled curve coordinates, and sparse tails cannot establish universal monotonicity.

#### 9. Detection metrics and class-prior conditions

Main correctness and Table2 concern synthetic images only: one image’s average is the number of six binary correct predictions divided by6. It is a class-conditional correctness/recall quantity at the frozen detector thresholds, not detector confidence or balanced all-image accuracy. Table3 separately lists all-image ACC, AP, ACC_fake and ACC_real.

Evidence: p4 Section3.2/Figure2; p8 Table2; p9 Table3; p19 Table5.

Limitations: Class-prior pooling, exact sample denominators, decision thresholds and AP implementation details are incompletely specified. Do not assume deployment priors or balanced accuracy. Appendix B4 does not clearly specify the population/weighting behind Table5.

#### 10. Within-generator versus across-generator correlations

The main curves condition on generator. Figure4 uses retained-cluster means within each main generator: Pearson r0.3698–0.6108, with printed p0.00003–0.02049. Section4.3 pools cluster averages from four generators and includes generator-indicator intercepts to account for different baseline accuracies.

Evidence: pp4–6 Sections3.2/4.2–4.3;Figure4/Table1.

Limitations: Grouped, feature-selected cluster correlations differ from unbiased individual-image correlations. Intercept adjustment does not control all generator interactions or residual content/source confounding.

#### 11. Quality-score versus correctness relationships

The main endpoint is observed binary correctness, including the integer count0–6, rather than confidence probabilities or margins. Higher-score groups tend to be easier above distribution peaks, but distorted-character and porthole clusters can have low scores and high detectability. Patch AP and real/fake tradeoffs are separate endpoints.

Evidence: p4 Figures1–2; pp6–9 Figure5/Sections4.3–5/Tables2–3.

Limitations: No claim of monotonicity for every interval, every image or every detector is justified. Confidence, classification correctness and preference score remain different variables.

#### 12. Generator-level confounding

Generator-specific baseline difficulty is explicitly acknowledged and mitigated with separate intercepts in cluster-level regression. Per-generator plots reduce simple between-generator confounding, while extra model families widen descriptive coverage.

Evidence: p6 Section4.3; pp14–16 AppendixB1.

Limitations: Training data, architecture, resolution, inference settings, modifiers and preference-model biases may still covary. The adjustment does not identify a causal quality effect or guarantee slope transfer to future generators.

#### 13. Content and prompt confounding

Prompt length co-varies with scene/entity complexity and color descriptions. Table4 shows color terms in14.2/37.9/63.2% of0–9/10–19/20–29-word prompts and saturation0.47 with versus0.40 without color terms over prompts under30 words. Generated-image BLIP-2 captions replace original score-input prompts to probe text-alignment effects.

Evidence: pp4–7 Sections4.1–4.3; pp14,16–18 AppendicesB2–B3/Figures10–12/Table4.

Limitations: Caption source, scene content, modifier choices and image provenance are not fully randomized or source-group controlled. Caption substitution reduces one proxy issue; it is not human validation or complete confound removal.

#### 14. Saturation, contrast, texture and complexity analyses

AppendixA3 measures lightness by mean HSV value, contrast by pixel-intensity RMS/standard deviation, saturation by mean HSV saturation, sharpness by grayscale Laplacian variance, texture by Canny-edge-pixel density, and structural complexity by square root of SAM2 segment count. Low-level coefficients have matching positive lightness/contrast/saturation/texture and negative sharpness/complexity signs across accuracy and preference targets.

Evidence: p6 Table1a/Section4.3; p13 AppendixA3.

Limitations: These are operational proxies. SAM2 segmentation settings, edge thresholds and several exact implementations are unreported; complexity, semantic content and texture are not independently randomized properties.

#### 15. Clustering and regression procedures

K-means k50 uses ImageReward features of center224x 224 patches and empty text. Real images take part in clustering and are excluded from subsequent fake analysis. Clusters with fewer than30 generated images are dropped. Standardized least-squares regression fits cluster means pooled across four generators, with source-indicator intercepts. DINOv2 features reduced by PCA to6 dimensions provide a high-level comparison.

Evidence: pp5–6 Sections4.2–4.3/Table1; pp13–14 AppendicesA2–A4.

Limitations: Retained cluster totals, seeds/repeats, exact checkpoints, PCA fitting partition, held-out regression validation and coefficient uncertainty are not specified. Fit R-squared is not held-out detection accuracy.

#### 16. Statistical robustness and confidence intervals

Figure4 reports eight r/p pairs. Low-level regression R-squared is0.77 for accuracy,0.81 for ImageReward and0.74 for HPSv2; the six-PC counterparts are0.76,0.76,0.68. Additional generators, another proxy and caption substitution test descriptive robustness.

Evidence: pp5–6 Figure4/Table1; pp14–17 AppendicesB1–B2; p19 Table5 caption.

Limitations: No confidence intervals, bootstrap/repeated-seed uncertainty, coefficient significance tests, multiplicity correction or prompt/source-group dependence adjustment is reported. Table5 underlining denotes a magnitude threshold over10%, not inferential significance.

#### 17. Data-selection and evaluation leakage safeguards

Documented safeguards include frozen official detectors, paired-real compression matching and external patch evaluation beyond the four regression-analysis generators. AppendixA6 excludes SD2.1/SDXL already used for analysis, commonly trained/similar generators such as SD1.4/1.5, and images<=256x 256 with little patch-selection room.

Evidence: pp3–4 Section3.1; pp8,13–14 Section5.2/AppendicesA1/A5/A6.

Limitations: The design selects detectors that already generalize and eligible image sizes. No full deduplication against detector/preference-model training sets is documented. SSP trains on the GenImage generator mixture while evaluation includes GenImage Midjourney; exact within-dataset splitting is not specified sufficiently to prove absence of leakage.

#### 18. Generalization across detector families

Aggregate observations involve six detector variants and extend to eight generated-image sources. Individual patch outcomes differ: RINE AP90.2→91.9 but ACC75.0→74.2; DRCTCLIP Easiest AP88.4→86.7; NPR Hardest AP78.6 versusEasiest74.6; SSP Hardest AP81.0 versusEasiest77.4. Interventions also differ by family.

Evidence: pp8–9 Section5.2/Tables2–3; p19 AppendixB4/Table5.

Limitations: This supports conditional family-specific responses, not one universal easy patch, a guaranteed all-detector quality relation, or gains in every metric.

#### 19. Dependence on quality-score proxies versus direct human judgments

Preference scores come from pretrained predictors rather than new human ratings of the 24000 generated images. The third preference model and BLIP-2 caption substitution probe proxy robustness but do not turn predicted preferences into observed human judgments.

Evidence: p3 Section3.1; pp14–17 AppendicesB1–B2.

Limitations: Prior human alignment of a predictor does not establish current-image subjective quality, photorealism or human susceptibility. No new human authenticity experiment is reported.

#### 20. Correlational versus causal interpretation

The principal finding is correlational. The paper discusses potential feature confounders, then shows inconsistent responses to lightness/contrast/saturation/sharpness interventions. Half-contrast changes RINE31.8→15.7 but NPR66.8→89.1. Low-score character/porthole outliers and inconsistent real-image trends further limit a universal account.

Evidence: pp6–7 Figure5/discussion; pp18–19 AppendicesB4–B5/Table5/Figure13.

Limitations: Transformations can alter several properties. Regression, clustering and selective patch improvements do not establish a uniform causal effect of image quality or any one visual characteristic.

### Exact numerical transcription

These are reported source values, not independent numerical reproductions. Table cells and printed Figure 4 r/p values were visually checked. Unlabelled plotted curve coordinates are not converted into invented exact observations.

#### Figure 4 — Retained-cluster correlations, p.5

|Generator|Preference model|r|Printed p|
|---|---|---:|---:|
|SD2.1|ImageReward|0.6108|0.00003|
|SDXL1.0|ImageReward|0.5516|0.00019|
|SD3|ImageReward|0.3698|0.02049|
|PixArt-alpha|ImageReward|0.4129|0.00657|
|SD2.1|HPSv2|0.5537|0.00021|
|SDXL1.0|HPSv2|0.5618|0.00013|
|SD3|HPSv2|0.4469|0.00434|
|PixArt-alpha|HPSv2|0.5135|0.00051|

K-means clusters are selected in ImageReward feature space, retained only with at least30 generated images, and averaged. Reported p values have no stated multiplicity correction, confidence intervals or prompt/source-group dependence adjustment; these are not causal effects.

#### Table 1(a) — Low-level regression, p.6

standardized least-squares coefficients; final column is R-squared, not accuracy

|Target|lightness|contrast|saturation|sharpness|texture_richness|structural_complexity|R_squared|
|---|---:|---:|---:|---:|---:|---:|---:|
|Accuracy|0.10|0.52|0.43|-0.33|0.42|-0.30|0.77|
|ImageReward|0.26|0.20|0.34|-0.46|0.35|-0.25|0.81|
|HPSv2|0.32|0.47|0.34|-0.71|0.54|-0.32|0.74|

#### Table 1(b) — DINOv2 six-PC regression, p.6

standardized least-squares coefficients; final column is R-squared

|Target|DINOv2_PC1|DINOv2_PC2|DINOv2_PC3|DINOv2_PC4|DINOv2_PC5|DINOv2_PC6|R_squared|
|---|---:|---:|---:|---:|---:|---:|---:|
|Accuracy|-0.18|-0.23|0.20|-0.23|0.04|0.11|0.76|
|ImageReward|-0.39|-0.22|-0.04|-0.18|-0.02|-0.12|0.76|
|HPSv2|-0.45|-0.09|0.03|-0.30|-0.10|-0.17|0.68|

#### Table 2 — Mean correctness on fake images only, percent, p.8

|Regression target|Strategy|GenImage:Midjourney|DRCT2M:SDXL-Refiner|DRCT2M:SDXL-Turbo|DRCT2M:LCM-SDXL|DRCT2M:SDv2-Ctrl|DRCT2M:SDXL-Ctrl|Synthbuster:DALLE2|Synthbuster:DALLE3|Synthbuster:Firefly|Synthbuster:Midjourney|printed_average|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|none|Center|76.3|75.3|56.8|62.6|75.0|76.2|38.1|51.4|41.4|75.0|62.8|
|Accuracy|Easiest|75.0|76.0|56.6|62.1|74.8|76.0|38.6|51.3|45.4|75.5|63.1|
|Accuracy|Random|70.6|72.0|56.1|61.1|73.6|75.0|36.7|50.9|37.8|71.1|60.5|
|Accuracy|Hardest|63.5|66.4|54.9|60.9|71.8|73.4|34.2|47.8|29.5|63.9|56.6|
|ImageReward|Easiest|73.1|75.0|56.2|60.5|74.4|76.0|37.6|50.1|44.6|70.9|61.8|
|ImageReward|Random|70.6|72.0|56.1|61.1|73.6|75.0|36.7|50.9|37.8|71.1|60.5|
|ImageReward|Hardest|68.6|69.3|54.9|62.4|72.2|73.6|35.7|50.8|37.2|71.5|59.6|
|HPSv2|Easiest|74.1|75.7|56.3|61.0|74.5|76.0|38.6|51.0|44.2|73.7|62.5|
|HPSv2|Random|70.6|72.0|56.1|61.1|73.6|75.0|36.7|50.9|37.8|71.1|60.5|
|HPSv2|Hardest|66.3|67.3|55.0|62.0|72.1|73.5|34.3|49.7|34.5|69.2|58.4|

Five end-to-end detector variants contribute to this mean. Conditional fake correctness is not all-image accuracy, balanced accuracy, AP or calibrated confidence. Best scoring patch often beats Random/Hardest, but not every Center result. Printed averages are preserved; no unreported sample counts or averaging weights inferred.

#### Table 3 — Per-detector patch tradeoffs, percent, p.9

|Detector|Strategy|ACC all|AP|ACC fake|ACC real|
|---|---|---:|---:|---:|---:|
|RINE|Center|75.0|90.2|51.6|98.5|
|RINE|Easiest|74.2|91.9|49.7|98.9|
|RINE|Random|71.4|90.3|44.0|98.9|
|RINE|Hardest|67.6|90.0|36.4|98.9|
|CoDE|Center|79.4|78.8|60.1|98.8|
|CoDE|Easiest|79.7|79.2|60.8|98.7|
|CoDE|Random|79.4|79.0|59.9|99.0|
|CoDE|Hardest|77.8|77.2|56.9|98.7|
|SuSy|Center|76.0|87.6|59.7|92.3|
|SuSy|Easiest|77.8|89.4|62.1|93.6|
|SuSy|Random|74.4|87.0|55.9|93.0|
|SuSy|Hardest|69.8|82.7|48.6|91.1|
|DRCT_ConvB|Center|75.4|84.8|53.7|97.1|
|DRCT_ConvB|Easiest|76.4|87.6|53.8|99.0|
|DRCT_ConvB|Random|75.1|84.2|54.1|96.0|
|DRCT_ConvB|Hardest|73.3|82.5|53.6|93.1|
|DRCT_CLIP|Center|78.9|88.4|89.0|68.9|
|DRCT_CLIP|Easiest|77.6|86.7|89.2|65.9|
|DRCT_CLIP|Random|78.4|87.6|88.5|68.3|
|DRCT_CLIP|Hardest|80.3|88.6|87.7|72.9|
|NPR|Center|71.6|75.9|66.8|76.3|
|NPR|Easiest|69.4|74.6|66.6|72.1|
|NPR|Random|73.7|76.3|68.5|78.9|
|NPR|Hardest|76.6|78.6|71.1|82.2|
|SSP|Center|72.0|79.7|51.7|92.4|
|SSP|Easiest|70.9|77.4|53.8|88.0|
|SSP|Random|73.4|81.0|54.9|92.0|
|SSP|Hardest|74.5|81.0|56.4|92.5|
|SSP|Simplest_original_SSP|74.5|78.3|64.2|84.7|

Per-detector metrics are averaged across evaluated generators; exact image denominators, class-prior pooling weights and AP implementation details are not specified. ACC means all-image accuracy as published, not automatically balanced accuracy. RINE improves AP while losing ACC and fake correctness; DRCTCLIP and fingerprint models contradict a uniform Easiest-patch benefit.

#### Table 4 — Color descriptions and saturation, p.18

|Color terms|0–9 words %|10–19 words %|20–29 words %|Mean saturation|
|---|---:|---:|---:|---:|
|with_color_descriptions|14.2|37.9|63.2|0.47|
|without_color_descriptions|85.8|62.1|36.8|0.4|

Saturation averaged over samples with prompts fewer than30 words; prompt ratios use the stated separate bins. Descriptive association, no randomized color-word intervention.

#### Table 5 — Intervention responses, percent, p.19

|Manipulation|Factor|DRCT_ConvB|DRCT_CLIP|RINE|CoDE|SuSy|NPR|
|---|---:|---:|---:|---:|---:|---:|---:|
|None|N/A|65.6|83.1|31.8|66.7|83.8|66.8|
|Lightness|0.5|51.8|55.8|20.9|68.0|84.9|89.2|
|Lightness|1.5|71.7|93.6|77.8|69.7|79.4|82.0|
|Contrast|0.5|44.4|76.6|15.7|72.9|82.6|89.1|
|Contrast|1.5|76.3|93.3|84.1|69.5|85.5|87.3|
|Saturation|0.5|63.2|84.3|35.8|64.9|84.7|64.2|
|Saturation|1.5|67.6|90.9|56.7|65.1|82.7|68.5|
|Sharpness|0.5|76.6|85.3|34.0|71.2|84.9|89.5|
|Sharpness|1.5|55.0|81.7|52.2|62.5|80.6|73.4|

detector accuracy percent, as table caption; exact evaluated population and real/fake weighting not specified in B4. Underlining marks changes exceeding the authors'10% magnitude threshold; it is not a reported inferential statistical test or confidence interval. Manipulations can change multiple image properties and do not establish isolated uniform causal effects.

### Counterevidence and interpretation

- PixArt-alpha clusters5,16,18 depict distorted characters or portholes: low preference scores can coexist with high detectability. (pp6–7 Figure5)

- Quality curves and count-of-correctness relationships are not uniformly monotonic, including irregular MPS trends for Infinity/FLUX and low-score easy intervals. Unprinted point coordinates are not invented. (p15 Figures6–7)

- Accuracy-regression Easiest mean63.1 is only0.3 percentage points aboveCenter62.8; ImageReward Easiest61.8 and HPSv2 Easiest62.5 fall belowCenter. GenImage Midjourney Easiest75.0 is belowCenter76.3. (p8 Table2)

- RINE AP90.2→91.9 improves while ACC75.0→74.2 and fake correctness51.6→49.7 decline. DRCTCLIP Easiest AP88.4→86.7 and real correctness68.9→65.9; Hardest AP88.6/ACC80.3 is stronger. NPR and SSP prefer the opposite selection direction. (p9 Table3)

- Half-contrast reduces RINE31.8→15.7 and DRCTConvB65.6→44.4, but improves NPR66.8→89.1 and CoDE66.7→72.9. Half-saturation increases RINE31.8→35.8, contrary to a uniform reading of positive pooled saturation coefficients. (p19 Table5)

- Real-image score–correctness trends are less consistent across preference models; fake-image findings do not transfer directly to true-negative behavior. (p19 AppendixB5/Figure13)

The findings support a bounded aggregate correlation. They do not show that every higher-quality image is easier to detect, that preference scores measure photorealism or human vulnerability, that all metrics improve together, or that each detector responds in the same direction. Contradictory observations limit universal causal claims while remaining substantive scientific results under R3.

### Patch-selection method

Extract low-level features from candidate patches; rank with a fitted regression and select the maximum-score or minimum-score patch as input to a frozen detector. Compare with Center, Random and original SSP minimum-texture selection. A technically evaluated inference procedure is distinct from measuring the scientific score–correctness association. Existing method is retained; the original action authorizes R3 addition review, not R4 removal. Patch size/stride and edge handling, repeated random trials, exact operational coefficients and complete implementation are not available from the pinned repository. Different families and endpoints respond differently.

External patch tests use GenImage Midjourney, five DRCT-2M variants (SDXL-Refiner, SDXL-Turbo, LCM-SDXL, SDv2-Ctrl, SDXL-Ctrl), and Synthbuster DALLE2, DALLE3, Firefly, Midjourney. This conditional transfer test does not remove all source, training or class-prior uncertainty.

### Release, licensing and reproduction

[Author repository](https://github.com/Coxy7/AIGI-Detection-Quality-Paradox) pinned at `2f170fa7f15a52e503b2dcb87115fbab51e6e5ae`, tree `cc9c70ab341c0b700932636c11d98c4704411c20`: its complete untruncated listing contains only README.md, LICENSE and .gitignore. No implementation or experiment code is present; the README says supplemental code is forthcoming. The Apache 2.0 text retains boilerplate copyright placeholders and does not establish upstream image/data redistribution rights.

[Author-linked HF dataset](https://huggingface.co/datasets/Coxy7/AIGI-Detection-Quality-Paradox), revision `9244882a51dbe33e658fe514488692155d20e5dd`, was public/non-gated in the metadata check. The card declares a 24,000-example fake split, 15 parquet shards, generator/prompt/seed/generation-setting fields and three preference-score fields. Names also include real_images_metadata.csv and download_real_images.py. The card claims CC-BY4.0. No shard, CSV, script or image body was fetched or executed; image contents, split membership, generator distribution, script correctness, complete availability and upstream rights are not independently verified. CLI output is fingerprinted without inventing raw HTTP headers/status.

Contribution-role confidence: **high**. Bounded empirical association/generalization: **medium**. Operational reproduction: **low**, because exact implementation/configurations and numerical reproduction are unavailable. This does not make code availability an added R3 requirement.

### Out-of-scope observation and evidence-only boundary

`OUT_OF_SCOPE_BIBLIOGRAPHIC_OBSERVATION`: the curated author field contains both Yao Xiao and Yao_Xiao, while PMLR/PDF identify Yao Xiao once; ZiYi Dong versus Ziyi Dong is also preserved as a spelling/capitalization observation. No author, publication, affiliation or relationship correction is applied or added as a historical action.

The original R267 action remains unresolved. The current tasks, scopes, inclusion and all four map relations remain unchanged. This worker made no authoritative/public-output/test/Git/primary-checkout edits, ran no full suite or exporter, and retrieved no extra manuscript version. Root’s independent scientific review was completed before this final recommendation; independent scientific agreement is separate from maintainer acceptance. Global preservation/accounting receipts are supplied by the parent workflow.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## R236 — X-AIGD research-type evidence review

This is one original unresolved Batch B research-type action. The independent provisional proposal is **method;dataset;benchmark;analysis_study**. Each added role is assessed separately under locked R1/R2/R3; maintainer acceptance remains pending. No corpus or review decision is changed.

### Identity, version and full reading

Canonical ID: curated:64635535d7b7b6a12a32. Title: **Unveiling Perceptual Artifacts: A Fine-Grained Benchmark for Interpretable AI-Generated Image Detection**. Current tasks: detection;localization; scope: fully_generated; current research type: method.

Primary source: [official ICLR 2026 manuscript](https://proceedings.iclr.cc/paper_files/paper/2026/file/65b4e84b66ed049f8066919a803e3942-Paper-Conference.pdf), 29 pages, 27,826,426 bytes, SHA-256 3604416a9a60e895da2f3d789763f9477f7cbfcf8ef6976e16bb57abbfbbd3b7. The printed title and all eleven ordered authors match; all pages 1–29, including references and appendices, were read. Critical pages 2,4,6,7,8,9,17,19,22,25,26,27,28 were rendered and visually inspected.

All eleven printed authors: Yao Xiao; Weiyan Chen; Jiahao Chen; Zijie Cao; Weijian Deng; Binbin Yang; Ziyi Dong; Xiangyang Ji; Wei Ke; Pengxu Wei; Liang Lin. The authoritative author casing is preserved, including the stored lowercase jiahao chen.

Three same-URL transport requests yielded exactly one complete new manuscript: initial240s timeout (5,295,817 bytes); ignored Range response stopped after2,932,736 bytes; final full HTTP200/curl0 transfer (27,826,426 bytes). The original final receipt incorrectly marked title_identity false because PDF extraction concatenated title words. A separate normalized-title/all-author/strict29-page recovery receipt corrects only that checker boundary. Original receipts and partial bodies remain unchanged. No download was repeated during recovery; no alternative author PDF was retrieved.

The prior Wave5B arXiv-v1 HTML source survives only as published extracts, not a complete current body. Its four PAD values are independently verified in the official Table2 here; no complete version equivalence or substantive whole-manuscript difference is claimed.

### Independent policy assessments

| Policy | Provisional outcome | Independent basis |
|---|---|---|
| R1 | DATASET_ADDITION_SUPPORTED | X-AIGD construction, human polygon/category curation, paired UID structure and explicit primary resource contribution are independently substantive. This is not ordinary method-specific evaluation data and does not rely solely on an announced release. |
| R2 | BENCHMARK_ADDITION_SUPPORTED | Separately defined AJ/PAD/category-agnostic/weak-instance protocols and held-out resource evaluate external experts,MLLMs and arbitrary output formats independently of their attention-alignment method. Generator count or table size alone is not the basis. |
| R3 | ANALYSIS_STUDY_ADDITION_SUPPORTED | The explicit second primary contribution and §§4–5 investigate existing detectors, fidelity/correctness, human-artifact alignment and auxiliary-task mismatch before §6 introduces an independent method. Their negative and mixed findings remain informative without §6. Supporting ablations alone would not qualify. Descriptive analysis does not validate every causal reliance claim. |

R1 concerns the construction and human curation of a paired/polygon/category resource. R2 concerns the reusable evaluation definitions, held-out protocol and model-independent metric interfaces. R3 concerns the primary §§4–5 investigation that precedes the alignment method, explicitly identified as contribution2 and reiterated in the conclusion/broader impact. None rests solely on big tables, thirteen generators, an announced release or routine method ablations.

### Resource, protocol and scientific findings

X-AIGD starts with4,000 reused real photographs from four sources and4,000 semantically corresponding prompts; thirteen generators create52,000 fakes before12 safety exclusions. AppendixA.2 thus explains the51,988 release-row arithmetic. Main§3.2 reports3,035 valid annotated fake samples, while Table8 and HF metadata report3,337 labeled rows; that denominator discrepancy remains unresolved. Table7 has18,285 artifact instances across seven categories. Twelve trained humans create polygon/category labels through three relay passes, with disputed labels retained. The confidence distribution is not a formal inter-annotator agreement statistic.

The resource supports binary Authenticity Judgment (balanced accuracy/P/R/F1), categorical artifact-region PAD, category-agnostic union-mask PAD and a weak-instance coverage score. A UID pairs a real image/prompt with its generated variants; halves are explicitly split disjointly. The100 shared-UID wording refers to across-generator selection within those halves, not established train–test overlap. Five generators enter training; all thirteen enter test. No UID CSV body or data asset is downloaded to verify actual memberships.

Seven pretrained expert detectors are assessed with Grad-CAM or Relevance Map, fake-class heatmaps thresholded0.5. Swin-B experiments compare AJ-only, PAD-only, transfer and joint learning with a common backbone. DINOv2 attention alignment is a separate method: it trains against patch-level human-artifact fractions. AppendixC additionally evaluates general MLLMs and specialized explanatory detectors. These experiments expose systematic negative/mixed findings even without the new alignment method.

The key distinction is **segmentation output versus classifier explanation**. Table2 PAD-only gives IoU27.2/PixF142.7 and joint segmentation27.3/42.8. Table13 joint classifier heatmaps instead give4.8/9.2, below AJ-only8.8/16.2. Good artifact segmentation does not prove authenticity classification uses those regions. §3.3 describes PAD conditional on a fake prediction, but the separate AJ/PAD tables do not certify a combined operational gating score.

Table2 joint AJ balanced accuracy decreases89.3→89.1 while F1 increases90.2→92.3. Table4 main alignment improves several metrics but Chameleon accuracy decreases71.4→71.2 while F1 rises62.7→63.5. Table12 fine-tuning decreases Color weak-instance F1 from3.0 to1.9. Several Table9 non-Symbol category results exceed random despite the broad narrative emphasis on Symbols. These counterexamples are retained.

Heatmap overlap measures alignment with human regions, not causal necessity, sufficiency or attention faithfulness. The study does not perform an artifact-removal necessity intervention. Architecture, training data, explanation operator, subjective annotation and extra human-mask supervision remain confounds. Random/benign/saliency controls reduce a generic spatial-regularization explanation but do not completely isolate semantic supervision. The appendix LoRA protocol changes attention operator,learning rate,batch and losses, so its numbers are not pooled with the main recipe.
Table14 also contains modest generic-control improvements on CommFor: baseline72.1Acc/63.6F1, Random72.3/64.1 and Saliency72.4/64.5. Artifact73.7/66.5 remains highest, but the controls are not uniformly worse than no alignment.

### Release provenance and reproducibility

The author repository is pinned to36b370adc9f21886f7b1b3f5cec719d6e5e8e59b; eight individual README/metric files were passively read. The49-entry tree contains viewer and standalone metrics; README still marks model training/experiment code TODO. No author code was executed or repository archive cloned.

HF metadata is pinned to92180f32030507ab54a40d6f1b88f39d6cec8178. Declared splits are labeled_train918,labeled_test2,419,unlabeled_train24,013,unlabeled_test24,638. Metadata exposes UID,generator,polygon labels,prompts and generation/compression fields and lists split/real-image CSVs. These are declarations, not independently verified asset contents or completeness. One pinned card-text request timed out with zero bytes; no retry. Code Apache2 and data CC-BY4.0 declarations are separate from unverified upstream image rights.

Current code accumulates pixel counts and outputs fractions; paper tables are percentage-scaled. Its weak-instance matching uses intersection/predicted-box area>threshold, many-to-many flags,5×5 dilation and8-connected components. PaperA.5 prints>=threshold. It is not standard box-IoU/COCO matching. Multiclass overlap priority and patch edge handling remain uncertain.

### Exact question matrix (18 R1 +15 R2 +15 R3)


#### R1 dataset

1. **X-AIGD's original data sources.** Four reused real-image datasets, selected and filtered into 4,000 real images: SA-1B2,972; LAION-Aesthetic856; MSCOCO133; Conceptual Captions39. Real-image content/captions seed newly generated semantically paired fakes. InternVL2 8B filters nonphotographic CC3M/LAION and privacy-blurred SA-1B. [SUPPORTED_WITH_LIMITS; 3.1 p4; A.1 Table5 p17; A.2 pp17–18]

2. **Number of real and synthetic images.** 4,000 real images and 13×4,000=52,000 generated fakes before12 unsafe-image exclusions, giving51,988. Main3.2 says3,035 valid annotated fakes; Table8 says3,337 labeled and48,651 unlabeled. Pinned HF metadata has918+2,419=3,337 labeled and24,013+24,638=48,651 unlabeled. The3,035/3,337 boundary is unexplained; do not force equality or treat all numbers as the same denominator. [SUPPORTED_WITH_INTERNAL_COUNT_DISCREPANCY; 3.1–3.2 p4; A.2 p18; Table8 p20; pinned HF cardData]

3. **Number of image generators.** 13 text-conditioned generators, comprising four diffusion UNets, eight DiTs and one autoregressive model; five contribute training examples and all13 test examples. [SUPPORTED; A.1 Table6 p17]

4. **Generator identities and versions.** Table6 identities and train/test flags are preserved separately. Four community fine-tunes are included alongside SD v1.4,SDXL,PixArt-alpha,Lumina-Next,SD3,HYDiT-v1.2,FLUX.1-dev,SD3.5-L,Infinity. Names/references do not verify exact downloaded checkpoint hashes, generation seeds or complete scheduler settings. Preserve relistic-vision/realistic-vision spelling boundary. [SUPPORTED_WITH_VERSION_LIMITS; Table6 p17; A.2 p18; source references pp11–16]

5. **Original versus reused images.** Real photographs are reused and filtered, prompts combine existing captions and BLIP-2/InternVL2 8B descriptions of varied lengths; fake images are generated for this collection. Human artifact polygons/categories and structured pairing are a new curated resource. This is not evidence that all underlying real-image rights or assets were independently audited. [SUPPORTED; 3.1 p4; A.2 pp17–18; Ethics p10]

6. **Pixel-level artifact annotation procedures.** 12 trained human annotators draw pixel-level polygons and assign artifact categories in Labelme; each image receives three relay passes by different annotators, who inspect prior labels and add missed/disputed regions. All annotations are retained rather than adjudicated into one canonical mask. [SUPPORTED; 3.2 p4; A.3 pp18–19]

7. **Artifact taxonomy and number of categories.** Seven categories in three levels: low-level textures,edges/shapes,symbols,color; high-level semantics; cognitive-level commonsense and physics. Formal taxonomy and localized examples are reusable beyond the alignment model. [SUPPORTED; Figure1 p2; 3.2 p4; Figure11 p27; metrics/constants.py:1–13]

8. **Low-level versus semantic versus counterfactual artifact labels.** Low-level distortions need not require semantic reasoning; high-level semantics concerns structural/compositional object errors; cognitive counterfactuals concern commonsense/physics. Text examples separate distorted letters from spelling/nonsensical-word issues; these boundaries are subjective and models confuse them. [SUPPORTED; Figure1 p2; 5/Figure5 p8; A.3 p19]

9. **Human versus model-assisted annotation.** Artifact region/category annotation is human. Models assist real-image filtering, caption generation and safety filtering, not proven replacement of human polygon labels. Three independent confidence raters assess annotations, while the three creation passes themselves are not blind independent votes. [SUPPORTED_WITH_LIMITS; 3.2 pp4–5; A.2–A.3 pp17–19]

10. **Annotator agreement and quality-control procedures.** Standardized training, three relay passes, out-of-scope/unsafe flags and independent confidence ratings0,0.5,1. Figure2 confidence-bin proportions0.02,0.03,0.19,0.75 are descriptive, rounded and sum0.99. Main text says a random subset; A.3 wording describes scores across annotations. QC subset size, formal kappa/IAA and independent blind agreement are not reported. [SUPPORTED_WITH_LIMITS; 3.2 pp4–5; Figure2 p4; A.3 p19; A.6 p20]

11. **Number and distribution of annotated masks.** Table7 lists18,285 annotated artifact instances with exact per-generator/category counts; this is not a mask-file count or unique-image count. Main3.2 has3,035 valid annotated fakes versus Table8/HF3,337 labeled rows. Retained overlapping annotations can produce more instances than unique spatial components. Actual files were not downloaded. [SUPPORTED_WITH_INTERNAL_COUNT_DISCREPANCY; 3.2 p4; Table7 p19; Table8 p20; HF metadata]

12. **Region overlap and ambiguity.** Relay protocol deliberately retains differing/overlapping annotations rather than imposing consensus. A.6 recommends confidence reweighting, noise-tolerant losses and weak localization. Pinned evaluation rasterizes/truncates/clips polygons and unions masks; paper multiclass segmentation overlap-priority policy is not specified. [SUPPORTED_WITH_IMPLEMENTATION_LIMITS; A.3 pp18–19; A.6 p20; B.2 p21; metrics/masks.py:34–54,69–80,96–107]

13. **Per-category annotation balance.** Severely imbalanced Table7 category totals: textures1,737; edges/shapes10,310; symbols1,998; color301; semantics3,146; commonsense486; physics307, total18,285. Weighted cross-entropy uses approximate inverse pixel frequencies, not proof of unbiased evaluation or balanced instance coverage. [SUPPORTED; Table7 p19; B.2 p21]

14. **Train/validation/test definitions.** 4,000 UID groups tie each real image/prompt to generated variants; halves are split disjointly into train/test.200 UIDs per involved generator are annotated; five train generators/all13 test.100 shared UID wording concerns across-generator selection inside the disjoint halves, not demonstrated train–test overlap. Small internal validation and a separate1,000-UID alignment-selection set are described; actual uid_split.csv membership not verified. [SUPPORTED_WITH_LIMITS; A.3 p18; Table6 p17; B.2–B.3 p21]

15. **Whether original image/source identities are preserved.** Paper defines persistent UID for a real image and its same-prompt generator variants. HF metadata exposes generator,uid,original_prompt,positive/negative prompts,seed,scheduler,inference steps,size/compression fields and lists real_image_metadata.csv/uid_split.csv. Body contents and traceability to each original upstream URL were not inspected. [PARTIALLY_VERIFIED; A.2–A.3 p18; HF pinned revision metadata]

16. **Public annotations and mask-file availability.** Public/un-gated HF metadata lists labeled/unlabeled Parquet shards with labels as categorized polygon points; pinned repository has viewer and metric interfaces to rasterize masks. No image,Parquet,CSV,mask asset,archive or checkpoint was downloaded, so complete accessible assets and membership are not certified. Masks can be constructed from polygons; this is not verification of standalone published PNG mask files. [RELEASE_METADATA_ONLY; README.md; metrics/README.md; HF metadata revision92180f32; metrics/data.py/masks.py]

17. **Release license and upstream image rights.** Repository metadata/README declares Apache2 code license; HF card metadata declares CC-BY4.0 data license. Paper ethics says upstream licenses reviewed/noncommercial academic use and rights-holder contact. We did not fetch LICENSE body, data assets or upstream terms; code/data license declarations and third-party rights must remain distinct. [DECLARED_NOT_INDEPENDENTLY_AUDITED; Ethics p10; pinned README/repository metadata; HF cardData]

18. **Independent use by methods other than the authors' detector.** Task-independent UID/polygon/category resource, generic metric interfaces and evaluations of seven pretrained experts, five general MLLMs and specialized external systems demonstrate intended use independent of their detector. Third-party adoption outside the authors experiments is not established. Dataset contribution is substantive even though full release completeness is not certified. [SUPPORTED_AS_REUSABLE_RESOURCE; Contributions p3; 3–5 pp4–8; C pp22–25; pinned metrics README]


#### R2 benchmark

1. **Formal evaluation tasks.** Authenticity Judgment predicts y=1 generated/fake versus y=0 real; Acc is mean real/fake accuracy plus P/R/F1. PAD predicts artifact instances, regions and one of seven categories, with category-agnostic union-mask option and weak-instance option. [SUPPORTED; 3.3 p5; A.5 p19]

2. **Artifact-region annotation targets.** Human polygon regions and category labels are the target for artifact localization/explanation. PAD is human-perceptible artifact-region prediction, not arbitrary generated-region compositing masks. Real images supply authenticity negatives, not demonstrated exhaustive absence of every visual defect. [SUPPORTED; 3.2–3.3 pp4–5; A.3 pp18–19]

3. **Class/category prediction definitions.** AJ is binary real/fake; PAD has seven artifact classes and segmentation background. Per-category predictions and category-agnostic foreground unions are separately evaluated. Table9 is image-level category-presence F1 from nonempty box lists, not spatial success. [SUPPORTED_WITH_LIMITS; 3.3 p5; B.2 p21; C.1/Table9 p22]

4. **Spatial ground-truth masks.** Held-out human pixel polygons support target masks; overlapping/ambiguous annotations retained. Pinned code converts polygons by int32 truncation/clipping/fillPoly, unions relevant categories and nearest-neighbor resizes. Multiclass training label priority at overlap is not fully specified. [SUPPORTED_WITH_LIMITS; A.3 p19; B.2 p21; metrics/masks.py:34–54,69–80,96–107]

5. **Pixel-level IoU and F1 definitions.** IoU=TP/(TP+FP+FN),PixP=TP/(TP+FP),PixR=TP/(TP+FN),PixF1=2PR/(P+R). Pinned code accumulates pixel counts across images, reports overall/per-generator, zero denominator returns0, no TN term. Code outputs fractions; paper table values use0–100 scale. Do not conflate class F1,weak-instance F1 and pixel F1. [SUPPORTED; 3.3 p5; A.5 p19; metrics/pixel.py:23–58,96–117,169–191]

6. **Any localization threshold and mask-processing rules.** Paper detector interpretation maps are binarized at0.5. Current release prediction-mask threshold defaults>127 for8-bit PNGs and unions masks; optional resizing/cropping changes geometry. A.5 defines predicted-region coverage Area(intersection)/Area(prediction)>=t; code uses strict>t,5×5 dilation/8-connectivity and many-to-many flags, not IoU or COCO matching. [SUPPORTED_WITH_PAPER_CODE_BOUNDARY; 4 p6; A.5 p19; metrics/predictions.py:9–48; instance.py:147–210; masks.py]

7. **Detection–localization joint evaluation.** Multi-task Swin outputs fake probability and category masks; Table2 reports separate AJ and PAD metrics.3.3 describes PAD conditional on a fake prediction, but tables/implementation details do not clearly establish gating for a joint operational score. No combined detection-localization utility is inferred.27.3IoU/42.8PixF1 are segmentation, while classification heatmap gives4.8/9.2 inTable13. [SUPPORTED_WITH_GATING_UNCERTAINTY; 3.3 p5; Tables2–3 p7; B.2 p21; Table13 p26]

8. **Separate interpretability metrics.** Category-agnostic/category-specific spatial overlap against human regions evaluates attention/interpretation alignment; NIQE/MDFS/PAR-stratified fake accuracy adds descriptive fidelity analysis. Table9 image-level presence and weak-instance scores are separate endpoints. No causal necessity/faithfulness test or quantitative confidence-calibration metric follows automatically. [SUPPORTED_WITH_NONCAUSAL_BOUNDARY; 4 pp5–6; Figures3–4 pp5–6; C p22; D.3 p26]

9. **Baseline detector selection.** Seven pretrained end-to-end experts: CNNSpot,Gram-Net,UnivFD,FatFormer,DRCT-ConvB,DRCT-CLIP,CoDE. Five general MLLMs plus FakeVLM,FakeReasoning,LEGION extend assessment. Training provenance/checkpoints differ and are documented, not standardized. [SUPPORTED; 4 pp5–6; Table2 p7; B.1 pp20–21; C pp22–25]

10. **Detector inference and saliency-generation conditions.** Grad-CAM with aug_smooth=True for CNN-like incl Swin; Relevance Map for ViTs; fake-class maps threshold0.5. Resized maps mapped back; patch windows/stride224 aggregated. B.1 says overlapping despite equal window/stride, leaving edge handling ambiguous. Standardized explanation operators are not proof of causal reliance. [SUPPORTED_WITH_LIMITS; 4 p6; B.1 pp20–21]

11. **Train/test and cross-generator protocols.** UID-disjoint halves and five train/all13 test generators; unseen-generator test component; PAD/Swin internal validation and alignment1,000UID/5,000fake+1,000real selection set. External Synthbuster,Chameleon,CommFor evaluate AJ. Group memberships and evaluation cardinalities not independently verified from assets. [SUPPORTED_WITH_LIMITS; Table6 p17; A.3 p18; B.2–B.3 p21; Table4 p9]

12. **Baseline comparison fairness.** Same Swin backbone/recipe makes within-family single/transfer/multitask comparison meaningful, but pretrained experts differ in architecture,training domains and explanation operators. Alignment model adds human mask supervision, not matched information budget. MLLMs differ in training,outputformat and threshold; no universal fair leaderboard is claimed. [LIMITED_FAIRNESS; 5 pp7–8; B pp20–21; C pp22–25; D.4 p26]

13. **Whether other detectors can be evaluated without adopting the authors' method.** Generic AJ/PAD outputs, ground truth and mask/box/point metrics allow other models without the authors alignment loss/backbone. Existing experts/MLLMs are actually evaluated; this reusable resource/protocol is independent of merely presenting big result tables. [SUPPORTED; 3.3 p5; 4 pp5–6; A.5 p19; C pp22–25; metrics/README.md]

14. **Whether evaluation scripts and split definitions are available.** Pinned repo includes standalone pixel/instance evaluation modules and viewer; HF metadata lists UID split CSV/Parquet schemas. README still marks model training/experiment evaluation code TODO; no full experiment scripts/checkpoints/assets verified. Current code not certified as exact paper-time evaluation version. [PARTIALLY_RELEASED; Pinned README.md:TODO; metrics/README.md andtree; HF metadata]

15. **Robustness and source-domain limitations.** Five-to13 generator coverage and three external sets test some generalization; JPEG/rescale/crop/flip augmentations and mask controls provide bounded robustness. Photographic filtering,subjective artifacts,old/currentgenerator distribution,annotation imbalance,compression bias and unseen domains limit generalization. No comprehensive real-world or causal robustness theorem. [SUPPORTED_WITH_LIMITS; A.2 p18; B.2–B.3 p21; Tables4/14 pp9/26; E p28]


#### R3 analysis study

1. **The number and diversity of analyzed detectors.** The primary study examines seven pretrained expert detectors spanning CNN and Transformer families and varied training sources, then compares PAD transfer and joint learning with a common Swin backbone. Appendix C separately studies five general MLLMs and three specialized explanatory systems. These address several scientific questions beyond one method ablation. [SUPPORTED; 4–5 pp5–8; B.1 pp20–21; C pp22–25]

2. **Quantitative measures of artifact reliance.** The measurements are fake-class heatmap overlap with human masks, per-category PAD scores, fidelity-binned authenticity correctness and qualitative counterexamples. They assess spatial alignment and prediction behavior. No artifact-removal necessity intervention or causal mediation identifies actual learned reliance. [SUPPORTED_AS_PROXY_NOT_CAUSAL_RELIANCE; 4 pp5–6; Tables2/3 p7; D.3/Table13 p26]

3. **Pixel-level versus image-level explanation measurements.** Pixel IoU/precision/recall/F1 measure spatial overlap. Table9 instead measures image-level category presence; Table12 uses weak-instance coverage matching. Authenticity correctness, model confidence, segmentation performance and explanation faithfulness remain distinct; no combined operational score is substituted. [SUPPORTED_DISTINCT_ENDPOINTS; 3.3 p5; C.1/Table9 p22; C.3/Table12 pp25–26; Table13 p26]

4. **Differences among low-, mid- and high-level artifact categories.** Table3 shows better edges/symbols than cognitive-artifact prediction: PAD-only physics recall is0.3 and commonsense2.2, compared with symbols54.2 and edges50.1. Texture and color are also weak, so low-level artifacts are not uniformly solved. Categories vary from301 to10,310 instances and have subjective boundaries. [SUPPORTED_WITH_IMBALANCE; Table3 p7; Figure5 p8; Table7 p19]

5. **Detector attention and spatial overlap.** Expert heatmap IoU ranges from0.4 to9.0. Joint-model segmentation scores27.3IoU/42.8PixF1 coexist with classifier heatmap4.8/9.2, below AJ-only8.8/16.2. DINO alignment reaches14.0/24.5, but improving overlap against the training target does not itself prove causal explanation faithfulness. [SUPPORTED_AS_SPATIAL_ALIGNMENT; Tables2 p7; Table13 p26; Figures4/12 pp6/28]

6. **Confounds from detector architecture and training data.** Pretrained detectors differ in data, architecture and Grad-CAM/Relevance Map operators. Threshold and patch preprocessing influence overlap. Swin comparisons control the backbone but vary task supervision. DINO alignment adds masks; appendix D.4 changes LoRA, attention operator, learning rate and batch. All-system causal isolation is not achieved. [CONFOUNDS_EXPLICIT; B pp20–21; D.4 p26]

7. **Model confidence versus explanation quality.** The paper reports authenticity correctness and fake-class interpretation maps, but not a calibrated relationship between confidence and explanation quality. Figure3 concerns correctness on fake samples stratified by fidelity, not confidence calibration or direct human preference. [PARTIALLY_ADDRESSED; 4/Figure3 pp5–6; Tables2/13 pp7/26]

8. **The relation between detectable artifacts and authenticity predictions.** PAD-pretrained linear probing gives AJ accuracy82.1/F182.5, below AJ-only89.3/90.2. Full fine-tuning gives89.9/92.5 and joint learning89.1/92.3: gains are mixed and marginal, while the joint classifier heatmap worsens despite good segmentation. Artifact-predicting features need not govern classification; this remains descriptive rather than causal proof. [SUPPORTED_NEGATIVE_FINDING_WITH_LIMITS; 5 pp7–8; Tables2/13 pp7/26]

9. **Human annotation biases.** Human category boundaries, incomplete coverage, relay rather than blind consensus, retained disagreements, unknown confidence-subset size, category imbalance and photographic filtering affect the reference annotations. Human-recognizable artifacts are not all possible forensic clues; low overlap can reflect useful unannotated features. [LIMITATIONS_EXPLICIT; 3.2 pp4–5; A.3/A.6 pp18–20; 6/E pp9/28]

10. **Whether detector reliance varies by generator or image category.** Seven detector fidelity profiles and13-generator annotations cover varied content. Table7 gives generator/category counts; text/symbol cases illustrate semantic limits. A fully stratified causal dependence model by generator or content is not reported, so source and semantic confounding remain. [PARTIALLY_ADDRESSED; Figure3 p5; Figure5 p8; Table7 p19; Appendix visuals pp27–28]

11. **Whether artifact alignment improves generalization.** Table4 artifact alignment improves X-AIGD accuracy85.7→87.1/F184.3→87.4 and Synthbuster69.1→72.1/55.9→63.2. Chameleon accuracy falls71.4→71.2 while F1 rises62.7→63.5; CommFor accuracy rises only69.7→69.8. Table14 uses a changed recipe and has consistent printed artifact gains. No reported confidence intervals or p-values establish universal superiority. [SUPPORTED_WITH_COUNTEREXAMPLES; Table4 p9; B.3 p21; D.4/Table14 p26]

12. **Whether apparent improvements may be caused by additional supervision.** Artifact alignment introduces human-mask information. Saliency, benign SAM-region and random-mask controls constrain a generic spatial-regularization explanation, but do not fully match the semantic information budget or establish attention faithfulness. Generic masks can also slightly improve CommFor in Table14; artifact-guided gains are not the only positive changes. [CONFOUND_REMAINS; 6 pp8–9; D.4 p26]

13. **Whether alternative interpretations and counterexamples are tested.** Explicit counterevidence includes transfer/joint negative outcomes, expert low overlap, MLLM class bias, a random category-presence baseline and benign/random/saliency controls. Text false alarms, cognitive limits and Chameleon/Color regressions qualify the conclusions. Necessity counterfactuals, causal faithfulness and formal statistical significance are not established. [SUPPORTED_WITH_LIMITS; 5 pp7–8; C pp22–25; Tables9–14 pp22–26; Figure7 p9]

14. **Whether systematic scientific findings are independently emphasized in contributions and conclusions.** The second explicit primary contribution concerns detector underutilization and auxiliary-PAD mismatch. Sections4–5 investigate pretrained detectors and task transfer before section6 introduces attention alignment. The conclusion and broader impact independently emphasize these findings; this exceeds routine ablations or supporting figures. [SUPPORTED_PRIMARY; Primary contributions p3; 4–5 pp5–8; Conclusion p10; F p29]

15. **Whether analysis would remain informative without the authors' proposed method.** Without section6, the fidelity/correctness analysis, expert mask-overlap study, controlled Swin transfer/joint negative findings and MLLM grounding/class-bias results remain informative. They address independent scientific questions about interpretability. Causal language must be qualified, but R3 does not require causal proof. [SUPPORTED_PRIMARY; 4–5 pp5–8; C pp22–25; Conclusion p10; F p29]


### Numerical transcription

All cells below preserve printed decimal strings; slash means not reported. Units are percentage-scaled for performance and integer counts for resource tables. Tables2,3,4,5,7,9–14 contain386 numerical cells. Table8 selected X-AIGD resource values and Figure2 proportions are recorded separately in review.json. Figure curves are not digitized; no unprinted uncertainty or correlation statistic is invented.


#### Table2 — Authenticity Judgment and Category-Agnostic PAD (PDF p7)

X-AIGD held-out test; seven pretrained experts use thresholded classifier interpretation heatmaps for PAD. PAD-only/multi-task PAD use their segmentation outputs. AJ and PAD side-by-side are not a single operational joint-gating score. Swin-B comparison details in B.2.

| Model/resource | AJ balanced Acc | AJ P | AJ R | AJ F1 | PAD IoU | PAD PixP | PAD PixR | PAD PixF1 |
|---|---|---|---|---|---|---|---|---|
| CNNSpot | 48.6 | 39.7 | 5.6 | 9.8 | 0.9 | 7.7 | 1.0 | 1.8 |
| Gram-Net | 62.7 | 57.7 | 95.0 | 71.8 | 5.8 | 16.9 | 8.1 | 11.0 |
| UnivFD | 50.2 | 64.1 | 1.0 | 2.0 | 0.4 | 10.1 | 0.4 | 0.8 |
| FatFormer | 52.1 | 57.3 | 16.3 | 25.4 | 0.5 | 10.2 | 0.5 | 0.9 |
| DRCT-ConvB | 82.5 | 88.4 | 74.8 | 81.0 | 9.0 | 14.8 | 18.8 | 16.6 |
| DRCT-CLIP | 53.0 | 52.2 | 71.4 | 60.3 | 0.7 | 13.7 | 0.8 | 1.5 |
| CoDE | 76.5 | 93.1 | 57.2 | 70.9 | 2.9 | 11.5 | 3.8 | 5.7 |
| AJ-only | 89.3 | 96.3 | 85.8 | 90.2 | / | / | / | / |
| PAD-only | / | / | / | / | 27.2 | 40.4 | 45.4 | 42.7 |
| Transfer learning (linear probing) | 82.1 | 93.5 | 73.9 | 82.5 | / | / | / | / |
| Transfer learning (full fine-tuning) | 89.9 | 93.5 | 91.6 | 92.5 | / | / | / | / |
| Multi-task learning | 89.1 | 92.6 | 92.0 | 92.3 | 27.3 | 36.2 | 52.5 | 42.8 |

#### Table3 — Fine-grained PAD (PDF p7)

Category-specific segmentation metrics on X-AIGD test; low-level includes four columns of categories, high-level semantics, cognitive commonsense/physics. Annotation imbalance and category ambiguity limit comparisons.

| Model/resource | Textures PixP | Textures PixR | Edges&Shapes PixP | Edges&Shapes PixR | Symbols PixP | Symbols PixR | Color PixP | Color PixR | Semantics PixP | Semantics PixR | Commonsense PixP | Commonsense PixR | Physics PixP | Physics PixR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PAD-only | 17.7 | 9.1 | 32.8 | 50.1 | 43.8 | 54.2 | 10.9 | 2.5 | 19.9 | 23.5 | 11.3 | 2.2 | 2.9 | 0.3 |
| Multi-task | 14.9 | 15.6 | 29.8 | 55.6 | 43.3 | 52.3 | 8.4 | 5.4 | 17.9 | 25.5 | 7.4 | 2.2 | 3.4 | 0.8 |

#### Table4 — Main attention-alignment comparison (PDF p9)

DINOv2 ViT-B main full-fine-tuning recipe, B.3, average of ten repeated seeds. Acc is balanced authenticity accuracy. Not identical to the later LoRA/ordinary Attention Rollout recipe in D.4/Table14.

| Model/resource | X-AIGD Acc | X-AIGD F1 | Synthbuster Acc | Synthbuster F1 | Chameleon Acc | Chameleon F1 | CommFor Acc | CommFor F1 |
|---|---|---|---|---|---|---|---|---|
| None | 85.7 | 84.3 | 69.1 | 55.9 | 71.4 | 62.7 | 69.7 | 58.2 |
| Saliency | 86.6 | 86.4 | 71.2 | 60.7 | 68.4 | 58.3 | 69.2 | 59.7 |
| Artifact | 87.1 | 87.4 | 72.1 | 63.2 | 71.2 | 63.5 | 69.8 | 61.4 |

#### Table5 — Real image source counts (PDF p17)

Four source datasets used to derive semantically matched generation prompts. Counts describe the constructed collection, not newly downloaded assets.

| Model/resource | Sample count |
|---|---|
| SA-1B | 2972 |
| Laion-Aesthetic | 856 |
| MSCOCO | 133 |
| Conceptual Captions Dataset | 39 |

#### Table7 — Annotated artifact instances by generator (PDF p19)

Both train and test annotated subsets. Instances are not independent images or nonoverlapping disjoint objects; relay annotations are retained.

| Model/resource | Textures | Edges&Shapes | Symbols | Color | Semantics | Commonsense | Physics | Total |
|---|---|---|---|---|---|---|---|---|
| FLUX.1-dev | 27 | 520 | 143 | 16 | 182 | 50 | 38 | 976 |
| FLUX.1-dev-iPhonePhoto | 85 | 599 | 201 | 36 | 105 | 19 | 20 | 1065 |
| HYDiT-v1.2 | 78 | 618 | 38 | 20 | 271 | 23 | 9 | 1057 |
| Infinity | 50 | 747 | 82 | 25 | 272 | 49 | 24 | 1249 |
| Lumina-Next | 155 | 1304 | 127 | 29 | 310 | 28 | 26 | 1979 |
| PixArt-alpha | 161 | 1200 | 131 | 30 | 358 | 27 | 40 | 1947 |
| SDXL | 138 | 409 | 109 | 7 | 165 | 15 | 6 | 849 |
| SDXL-realism-engine | 81 | 335 | 200 | 31 | 101 | 41 | 28 | 817 |
| SD v1.4 | 103 | 1189 | 94 | 35 | 286 | 24 | 18 | 1749 |
| SD v1.5-realistic-vision | 285 | 1077 | 299 | 19 | 366 | 57 | 25 | 2128 |
| SD 3 | 337 | 1220 | 327 | 28 | 463 | 79 | 44 | 2498 |
| SD 3.5-L | 79 | 614 | 133 | 9 | 153 | 35 | 18 | 1041 |
| SD 3.5-L-iPhonePhoto | 158 | 478 | 114 | 16 | 114 | 39 | 11 | 930 |
| Total | 1737 | 10310 | 1998 | 301 | 3146 | 486 | 307 | 18285 |

#### Table9 — Image-level artifact presence from MLLMs (PDF p22)

C.1 asks boxes for each category but boxes are imprecise, so any nonempty list is converted to category presence. These are image-level F1 scores, NOT pixel or box localization scores.

| Model/resource | Textures | Edges&Shapes | Symbols | Color | Semantics | Commonsense | Physics |
|---|---|---|---|---|---|---|---|
| Qwen2.5-VL 7B | 5.0 | 5.3 | 49.0 | 14.6 | 26.7 | 11.7 | 14.3 |
| InternVL3 8B | 16.2 | 38.6 | 47.2 | 13.2 | 39.6 | 18.7 | 13.4 |
| LLaVa-Next (Mistral-7B) | 32.9 | 69.1 | 28.7 | 9.0 | 52.6 | 17.1 | 12.2 |
| DeepSeek-VL2-Small | 32.3 | 71.1 | 33.2 | 7.8 | 45.2 | 18.5 | 17.1 |
| GPT-4o | 9.3 | 59.5 | 91.7 | 0.0 | 40.5 | 32.3 | 9.1 |
| Random | 29.9 | 56.7 | 30.6 | 9.4 | 49.1 | 19.2 | 12.0 |

#### Table10 — MLLM-based authenticity judgment (PDF p22)

C.2 X-AIGD authenticity evaluation. Avg is real/fake accuracy average as printed; preserve rounding. Strong opposite class biases limit overall conclusions.

| Model/resource | Real Acc | Fake Acc | Avg Acc |
|---|---|---|---|
| FakeVLM | 43.7 | 98.9 | 71.3 |
| FakeReasoning | 81.2 | 39.7 | 60.4 |

#### Table11 — LEGION masks versus DINOv2 interpretation heatmaps (PDF p25)

Category-agnostic PAD. LEGION mask output and DINOv2 interpretation maps have different training/supervision; Ours receives X-AIGD artifact supervision.

| Model/resource | IoU | PixP | PixR | PixF1 |
|---|---|---|---|---|
| Baseline | 0.5 | 24.4 | 0.5 | 1.0 |
| LEGION | 9.1 | 29.1 | 11.7 | 16.7 |
| Ours (Attention Alignment) | 14.0 | 37.2 | 18.2 | 24.5 |

#### Table12 — Qwen2.5-VL 7B GRPO fine-tuning weak-instance PAD (PDF p26)

Instance F1@0.5 following A.5, predicted-region coverage threshold (not box-IoU threshold). Current pinned implementation uses strict > while paper prints >=. These scores are NOT Table9 image-level presence F1.

| Model/resource | Textures | Edges&Shapes | Symbols | Color | Semantics | Commonsense | Physics |
|---|---|---|---|---|---|---|---|
| Qwen2.5-VL 7B | 1.3 | 0.3 | 18.8 | 3.0 | 1.3 | 0.0 | 0.0 |
| Fine-tuned | 1.9 | 1.2 | 31.5 | 1.9 | 3.2 | 2.5 | 2.5 |

#### Table13 — Classifier interpretation heatmap PAD (PDF p26)

D.3 classification-head interpretations, not segmentation outputs from Table2. Multi-task segmentation27.3/42.8 cannot be substituted for its classifier heatmap4.8/9.2.

| Model/resource | IoU | PixP | PixR | PixF1 |
|---|---|---|---|---|
| Swin AJ-only | 8.8 | 11.8 | 25.9 | 16.2 |
| Swin Transfer learning (linear probing) | 6.3 | 10.1 | 14.2 | 11.8 |
| Swin Transfer learning (full fine-tuning) | 6.9 | 15.2 | 11.3 | 13.0 |
| Swin Multi-task | 4.8 | 11.0 | 7.8 | 9.2 |
| DINOv2 Baseline | 0.5 | 24.4 | 0.5 | 1.0 |
| DINOv2 Attention Alignment | 14.0 | 37.2 | 18.2 | 24.5 |

#### Table14 — Additional attention-alignment controls with changed LoRA recipe (PDF p26)

D.4 LoRA rank8, learning rate1e-4 cosine, ordinary Attention Rollout, effective batch32, lambda0.4,beta1.0. Controls differ from Table4 full fine-tuning/Gradient Attention Rollout. Do not treat as identical numerical reproduction.

| Model/resource | X-AIGD Acc | X-AIGD F1 | Synthbuster Acc | Synthbuster F1 | Chameleon Acc | Chameleon F1 | CommFor Acc | CommFor F1 |
|---|---|---|---|---|---|---|---|---|
| None | 82.2 | 82.9 | 71.2 | 60.6 | 68.0 | 68.2 | 72.1 | 63.6 |
| Benign | 80.7 | 81.4 | 70.6 | 60.3 | 65.6 | 66.4 | 71.5 | 63.1 |
| Random | 81.6 | 82.3 | 69.7 | 57.6 | 66.6 | 67.3 | 72.3 | 64.1 |
| Saliency | 81.3 | 81.9 | 71.4 | 61.8 | 66.0 | 66.5 | 72.4 | 64.5 |
| Artifact | 83.1 | 84.0 | 71.8 | 62.3 | 68.7 | 68.8 | 73.7 | 66.5 |

### Limits and preservation

- No new complete arXiv manuscript was obtained this wave; only the prior Wave5B identity-matched v1 extracts survive. No global equivalence with official ICLR2026 is claimed.
- Main3.2 says3,035 valid annotated fakes; Table8 and pinned HF metadata list3,337 labeled rows. The paper does not clearly reconcile valid/total denominators.
- 52,000 generated images minus the12 unsafe-image exclusions in A.2 matches51,988 declared release rows; this explains that arithmetic only, not every asset or split membership.
- Independent confidence ratings are not formal inter-annotator agreement; creation uses three relay passes, not blind independent consensus. Main text random-subset and A.3 across-annotations wording leave coverage uncertain.
- Attention-map overlap is a proxy for alignment with human artifacts, not proof of causal necessity, feature reliance or explanation faithfulness.
- Table2 segmentation PAD27.3IoU/42.8PixF1 and Table13 classification heatmap4.8IoU/9.2PixF1 are different outputs. AJ and PAD side by side do not establish joint operational gating.
- Architecture,pretraining,explanation operator,threshold and extra human-mask supervision are confounds. D.4 changes LoRA,attention operator,learning rate,batch andloss weights relative to Table4.
- Main Table4 has Chameleon accuracy regression71.4→71.2; Table2 joint AJ accuracy89.3→89.1 drops despite F1 gain; Table12 ColorF1 decreases3.0→1.9. Do not claim every metric/model/category improves.
- Table14 generic masks are not uniformly harmful: CommFor changes from baseline72.1Acc/63.6F1 to Random72.3/64.1 and Saliency72.4/64.5. Artifact73.7/66.5 is better, but positive generic-control effects remain counterevidence to an all-or-nothing explanation.
- Main paper A.5 weak-instance coverage uses >=t; pinned code uses >t with many-to-many flags. This is not IoU matching or conventional COCO AP.
- Figure3 fidelity curves are descriptive; no formal correlation coefficients,causal identification,pvalues or confidence intervals are established. Ten-seed averages do not supply unprinted uncertainty bounds.
- Current pinned release has viewer and standalone metrics but training/experiment code remains TODO. No experiments executed,checkpoints fetched,numerical reproduction or asset membership/rights certification.
- Actual UID CSV bodies were not read. Explicit disjoint train/test halves are preserved;100 shared UID wording is not evidence of train–test overlap.
- Table9 MLLM results are image-level category presence, not successful localization; several non-Symbol category scores exceed random despite broad narrative wording.
- B.1 calls patches overlapping while giving equal224window/stride; overlap edge handling remains ambiguous. Multiclass training annotation-overlap priority is not documented.
- Paper-time version of the current metric repository is not verified. Apache2 code and CC-BY4.0 metadata declarations do not establish all upstream image rights.

Scientific-role confidence is high for the three independent contributions. Mechanistic interpretation and exact reproduction confidence are medium. Evidence sufficiency is separate from maintainer acceptance; no action is closed or split, no terminal decision is created and accounting does not decrement.

**T236 remains the previously resolved localization task review.** Existing detection;localization and fully_generated are retained exactly. The new R236 research-type evidence neither reopens nor re-closes T236; no literal registry T236 row is invented.

The authoritative source hashes, all28 prior Batch B artifacts and the Wave5B evidence/report hashes are verified unchanged by the local worker checks. Parent-level preservation independently covers protected primary files,49 frozen NeurIPS artifacts and all unrelated work. No repository tests,export,stage,commit or push are performed by this worker.

7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA

## Comparative research progression

This is a source-grounded research interpretation. Common authorship does not prove common images or a formal research series.

**Author overlap (DEMONSTRATED_FROM_BOTH_OFFICIAL_BYLINES)**: {"shared_authors": ["Yao Xiao", "Binbin Yang", "Weiyan Chen", "Jiahao Chen", "Zijie Cao", "Ziyi Dong", "Xiangyang Ji", "Liang Lin", "Wei Ke", "Pengxu Wei"], "additional_R236_author": ["Weijian Deng"]}
Locators: R267 official PDFp1; R236 official PDFp1. Limit: No canonical name normalization or relationship edit; names alone do not prove a formal research series.

**Related scientific questions (SOURCE_GROUNDED_INTERPRETATION)**: R267 investigates learned preference-score/image-property associations with binary correctness; R236 tests human artifact-region/category alignment of detectors and the effect of artifact supervision. This is an interpretive progression from property correlations to spatial interpretability, not a documented serial project declaration.
Locators: R267 §§3-4,pp3-7; R236 §§4-6,pp5-10. Limit: Prediction correctness, human preference, fidelity, annotation confidence and explanation overlap remain distinct constructs.

**Original image source collections (NAMED_COLLECTION_OVERLAP_DEMONSTRATED)**: ["COCO", "CC3M", "LAION-Aesthetic", "SA-1B"]
Locators: R267 AppendixA1,p13; R236 Table5/AppendixA1-A2,pp17-18. Limit: No source image bytes/metadata CSVs downloaded; common photographs, prompts, UIDs, partitions or image-level overlap are not established.

**Generator overlap (FIVE_SHARED_NAMED_MODEL_FAMILIES)**: ["SDXL (R267 specifies1.0; R236 table uses SDXL)", "SD3", "PixArt-alpha", "FLUX.1-dev", "Infinity"]
Locators: R267 AppendixA1,p13 andB1,p14; R236 Table6,p17. Limit: The four-generator R267 main study differs from its six-generator open source inventory and from the13-model R236 set. Exact checkpoint/sampler/seed/output-byte equivalence is unverified. SD3.5/community derivatives remain distinct from SD3.

**Evaluated detector overlap (THREE_SHARED_NAMED_VARIANTS)**: ["CoDE", "DRCT-ConvB", "DRCT-CLIP"]
Locators: R267 §§3.1/5.2,Tables2-3,pp3-4/8-9; R236 §4,Table 2,pp5-7. Limit: Same method name is not verification of checkpoint bytes, preprocessing or original training-image overlap. R267NPR/RINE/SuSy/SSP and R236CNNSpot/Gram-Net/UnivFD/FatFormer sets differ.

**External evaluation collections (SYNTHBUSTER_SHARED_DATASET_NAME)**: Both evaluate on Synthbuster. R267 also tests GenImage/DRCT-2M; R236 also uses Chameleon/CommunityForensics.
Locators: R267 §5.2,Table 2,p8; R236 §6.2,Table4,p9. Limit: No exact common image subset, dataset revision, class-prior weighting or preprocessing equivalence verified.

**Quality and artifacts (RELATED_NON_EQUIVALENT_MEASUREMENTS)**: R267 uses ImageReward/HPSv2/MPS learned preferences and scalar image properties; R236 uses NIQE/MDFS/PAR and seven human artifact categories. Color/texture/edge concepts overlap thematically. R236 fidelity plots do not establish the same quantity as R267 preference-score curves.
Locators: R267 §4.3/Table1/AppendixA3,pp6/13; R236 Figure3/§4,pp5-6 andFigure1/Table3,pp2/7. Limit: No one-to-one mapping or causal explanation joins the two measurement systems; differing metric populations/detectors preclude declaring confirmation or contradiction solely from the headline claims.

**Direct citation/declared extension (NOT_FOUND_IN_THE_TWO_FULL_OFFICIAL_SOURCES)**: Neither complete official bibliography identifies the other title. R236 references share several prior methods/source collections, but no explicit R267 citation or formal-series declaration was found.
Locators: R267 references,pp9-12; R236 references,pp11-16. Limit: Bounded to these exact official versions, not proof about all revisions or author intentions.

**Shared metadata conventions (SCHEMA_ONLY)**: {"common_feature_names": ["chroma_subsampling", "generator", "guidance_scale", "height", "image", "jpeg_quality", "negative_prompt", "num_inference_steps", "original_prompt", "positive_prompt", "scheduler", "seed", "uid", "width"], "R267_unique_score_fields": ["imagereward_score", "hpsv2_score", "mps_score"], "R236_distinct_annotation_field": "labels with category and polygon point lists"}
Locators: Pinned author-linked HFmetadata revisions in each record. Limit: Similar field names or download_real_images.py basenames do not establish shared rows, script bodies or matching source-image URLs.

**Joint scientific implication (CAUTIOUS_INTERPRETATION)**: Both studies qualify simple intuitions linking visible quality or artifacts to detector behavior. R267 retains low-quality yet detectable examples and opposite fingerprint responses. R236 shows weak explanatory-mask alignment, marginal auxiliary-task gains and a Chameleon accuracy exception.
Locators: R267 Figure5,Tables2-5,pp7-9/18-19; R236 Tables2/4/13/14,pp7/9/26. Limit: Neither correlations nor explanation overlap establish causal necessity. Alignment training comparisons support bounded intervention effects, not an identified universal causal mechanism of existing detector decisions.

## Retrieval and recovery accounting

Exactly two newly complete official manuscripts were obtained in the wave: one R267 PMLR PDF and one R236 ICLR PDF. Recovery downloaded zero manuscripts. No alternate complete version or separate supplement was obtained. No dataset, image, mask, checkpoint, weight, repository archive or clone was downloaded; author experiment code was not executed.

R267 used two transports to its official PDF URL: one pre-HTTP/body failure and one successful IPv4 correction. R236 used three transports to its official PDF URL: an initial incomplete 240-second response; a range request ignored by the server and stopped; and the final complete transfer with an 1,800-second bound. Five transports yielded two complete manuscripts. Partial responses remain separate and were never concatenated.

The original R236 receipt retains its false completeness flag because its literal title check failed on PDF-extracted words joined together. A separate recovery receipt verifies exact byte length, EOF, strict parsing of all 29 pages, SHA-256, normalized printed title and all eleven authors. The original receipt/source are unchanged; this clarification required no download.

No reusable complete earlier author-v1 body was recovered. Published Wave 5B records/task extracts are preserved as historical evidence. Their four PAD values match current official Table 2, without establishing complete textual equivalence or an exhaustive version diff. Metadata/source operation counts and fingerprints are separate in the manifest; CLI-operation counts are not invented underlying HTTP counts. Raw operational receipts, complete primary sources and scripts remain outside Git.

## Independent review and lightweight validation

Completed scientific/source checks: R267 57/57 (recovered), R236 76/76, and independent numerical/scientific checks 82/82. Resume preservation checks: 24/24; draft preflight: 10/10; assembled-packet content/provenance: 33/33; complete preservation gate: 45/45. Every completed group has zero failures. The packet and preservation receipts bind the pre-stamp artifacts; separate final operational receipts bind the delivered bytes after this validation-only stamp. All three change flags are zero. No full suite or exporter is run.

Root and the separate reviewer read both complete primary sources before consuming final source-owner judgments. R267’s completed 57-check review and 37-check independent numerical review are reused. R236 receives only the missing focused evidence checks. Reviewer agreement is separate from maintainer acceptance; empirical/reproduction confidence is separate from contribution-role confidence.

## Delivery and preservation

Only the requested B1O report and evidence manifest are new repository artifacts. Both remain untracked, unstaged, uncommitted and unpushed. No authoritative data, decisions, tasks, bibliography, institution, relationship or export is changed.

Preservation guards cover all 4,492 isolated tracked files, 28 prior B1A-N artifacts, the complete primary 4,414 tracked / 305 untracked state, 128 protected paths / original 130 group, 49 frozen NeurIPS artifacts in each checkout, 140 current ignored inputs including 119 historical inputs, five other active worktrees and 53 current Batch C/original audit files. The old four-path C13 TMP inventory cannot be reconstructed; a fresh explicitly identified current closeout set is preserved without inventing historical paths.

Batch C retains 13 deferred actions and 0 maintainer judgments; the separate 39-paper inventory is unchanged. No new wave is begun.

```text
AUTHORITATIVE_CORPUS_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA
```

# Batch B Wave B1S — controlled integration of accepted B1Q/B1R adjudications

Local integration on 2026-10-27 from published baseline `dace181c2a9edbb7c467978e9e958e83fdddc143`. B1S changes no scientific judgment: it preserves B1Q's evidence and B1R's accepted decisions, then synchronizes their two contribution additions into the public exports. No scientific manuscript, experiment, dataset or checkpoint is retrieved or reproduced.

## Source and remote verification

The latest fetched `origin/main` equals the B1R worktree base. No intervening commit or record overlap requires reconciliation, so the existing isolated worktree is reused. The primary checkout and concurrent work remain untouched.

All six original B1Q/B1R files match their prior validated fingerprints:

| File | SHA-256 |
|---|---|
| `data/curated/paper_taxonomy.csv` | `2388617d62211ebea18af8827095a1a776ce0c160d1942511212fa7324fe0fb9` |
| `data/curated/papers.csv` | `8ff6f43f054b6da18ef498cc7c0b9d4fcf7bd6cc9a9abd01d67255b1909bc65f` |
| `data/curated/review_decisions.csv` | `ce616e76f5b41a2df967c9c72451f9cbeb8b1ad05b488d5ca6240d070c4819dc` |
| `data/raw/corpus_quality_batch_b_wave_b1q_2026_10_26/evidence_manifest.json` | `07deb03f59a03015bb4e8b055b23e1a0f2e9ece66eba750b7354356d37981002` |
| `docs/corpus_quality_batch_b_wave_b1q_2026_10_26.md` | `bccebf430c6d39b815ae63bed40844fdc92b658bf8078e61a65ccddc174c3686` |
| `docs/corpus_quality_batch_b_wave_b1r_2026_10_27.md` | `2606eb4933540741e96c733ff8275d104b1c63efb15194abda27f54592e30e25` |

These six files remain byte-for-byte unchanged during B1S. The original B1Q pending language and B1R no-export local report remain dated historical evidence; this separate integration report records the later authorized export phase. Numerical discrepancies, corrected earlier assessments, manuscript-version limitations, access restrictions and unverified scientific reproducibility remain applicable.

## Baseline HTTP regression recovery

The original [baseline run, attempt 1](https://github.com/meiling-fdu/synthetic-image-research-map/actions/runs/40320465389/attempts/1) recorded 2,233 passed, 389 passing subtests and one failure in `VenueSaveLifecycleTests::test_http_save_removes_resolved_review_and_updates_dashboard_immediately`. The initial dashboard GET and metadata-update POST returned 200. The second dashboard GET exceeded the helper's 3-second deadline while waiting for the HTTP status line; the server later attempted its response and raised BrokenPipeError after the client disconnected. The post-save semantic assertions never ran in that failed request.

Exactly one unchanged baseline-job rerun was requested. [Attempt 2](https://github.com/meiling-fdu/synthetic-image-research-map/actions/runs/40320465389/attempts/2) succeeded at the same baseline commit: **2,234 passed, 389 passing subtests, zero failures**. Authoritative/public validators and corpus/frontend preservation steps also succeeded. This is recorded as a **suspected intermittent HTTP timeout**, not a proven server defect. No HTTP server, client deadline, teardown code or semantic assertion was changed to clear the gate. No further baseline retry was initiated.

The full original traceback and successful retry logs are preserved outside Git. Retry log SHA-256: `93947268ad3ae5985d2e1603b749436ab43f7e2333bcdd249d28df02670bcbfc`. The source-backed timing/fixture/teardown risks remain hypotheses; no internal timing profile established a single causal component. See the independent diagnosis and `recovery/baseline-recovery-receipt.json` in the operational receipt directory.

## Accepted source transaction preserved

| Review | Paper ID | Accepted complete research types | Locked rule | Existing formal decision |
|---|---|---|---|---|
| R026 | `curated:386ccd052b812587c286` | `method;analysis_study` | R3 | `review:001acb4497ed65ffc78b` |
| R253 | `curated:f9eac1aa13a606c6ec88` | `method;dataset;benchmark` | R2 | `review:be6652347897359ff3b3` |

Both preserve `detection` and `fully_generated`. Exactly 14 existing CSV cells differ from the baseline: two paper research-type cells plus six taxonomy fields for each target. The entire prior 101-row review-decision byte prefix survives, followed by exactly two unique terminal decisions (103 rows total). No publication, institution, relationship, task, scope, inclusion or unrelated paper metadata changes.

Contribution acceptance is separate from empirical correctness, causal interpretation, public accessibility, operational availability and independently reproduced numerical results. B1R's independent R3/R2 justifications and the full B1Q limitations remain authoritative; this integration does not reassess them.

## Deterministic export and exact semantic delta

Established offline command:

```sh
python scripts/refresh_public_preview.py --skip-search --user-agent 'SyntheticImageResearchMap/0.1 (offline Batch B B1S integration)'
```

The reviewed Python environment is reused; search, external APIs and geocoding are not run. Existing public records are preserved by the established exporter. Every generated difference is inspected. Only R026/R253 public-paper contribution lists and their direct research-type review reason change. Their seven existing map dependents (four R026, three R253) receive the same updates; 672 other public papers and all 1,410 map IDs/paper–institution pairs remain unchanged. Export metadata may change only the synchronized UTC generation timestamp.

Both offline export passes exited 0. The second pass after the successful full suite preserved every byte across **4,642 inventoried files** and all seven direct outputs: **`EXPORT_REPRODUCIBLE = 1`**. Both JSON files retain the shared generated timestamp `2026-10-27T06:08:15Z` on the no-op rerun.

Exactly four generated files change from the published baseline:
- `web/data/public_preview_papers.json` — two accepted type/review-reason updates.
- `web/data/public_preview_map_data.json` — seven dependent type/review-reason updates.
- `docs/public_preview_report.md` — generation-timestamp line only.
- `docs/key_paper_coverage_report.md` — input SHA-256 line only.

The missing-author Markdown report and both generated manual CSV reports are byte-identical and excluded from the commit. Independent semantic/report-diff audit: **2,114/2,114 checks passed**, zero failed. Its wrapper initially assumed all raw candidate rows had `paper_id`; that wrapper-only assumption was corrected to the existing stable identity rules before the semantic assertions ran. Original diagnostic artifacts remain preserved; no repository data was changed to satisfy the audit.

Export hashes: paper JSON `70cf88511f3adbc1ab0a0a29c67220fc81c5c6c7ec17b4ce5dd1beb71c5769f3`; map JSON `3d7ebd204c5192cf1fd4df3707a7fa11c7bfdb08f9d832fd7ac8f5c7b194cd10`.

## Recomputed taxonomy, corpus and original-action accounting

| Taxonomy | Previous public export | B1S public/source |
|---|---:|---:|
| detection | 621 | 621 |
| source_attribution | 84 | 84 |
| localization | 45 | 45 |
| method | 578 | 578 |
| dataset | 138 | 138 |
| benchmark | 96 | 97 |
| survey | 21 | 21 |
| analysis_study | 85 | 86 |

The pre-export B1R authoritative CSVs already contain benchmark 97/analysis study 86. B1S leaves those source bytes unchanged and brings the public snapshot into agreement. Counts are recomputed from records, not assigned from expected totals.

Corpus is unchanged: **674 public, 557 formal, 613 mapped, 61 unmapped, 1,410 relationships and 1,410 unique pairs**.

Original Batch B inventory remains **159 actions /148 papers**. Compared with the published baseline, exactly R026/R253 close:
- Historical unresolved: **133 actions /123 papers →131 actions /121 papers**.
- Active-public unresolved: **131 actions /121 papers →129 actions /119 papers**.

B1S creates no additional action or terminal decision beyond accepted B1R. Batch C's 13 deferred debts and the separate 39-paper inventory remain unchanged.

## Regression support and results

Current reviewed baseline constants change only benchmark 96→97 and analysis study 85→86. B1P's six whole-transaction test functions read their immutable published endpoint `dace181c2a9edbb7c467978e9e958e83fdddc143`, following the existing B1O convention. All 209 original historical assertion obligations remain. One compound historical/current-total check is split into historical packet equality and a separate current-total check, bringing the assertion count to 210. This preserves historical 96/85 receipts instead of silently rewriting them as B1S outcomes.

The new B1S contract tests cover the actual current 14-cell delta, 101-row prefix/two appends, formal identity/evidence acceptance and negative controls, repeated upsert idempotency, two-paper/seven-map-row public delta, unchanged tasks/scopes/relationships, source/public counts, original action accounting and B1Q/B1R/frozen NeurIPS provenance.

- Focused integration, HTTP, taxonomy, review, exporter, integrity and frontend tests: **359 passed /18 passing subtests**, zero failures/errors/skips.
- Complete regression suite, run once for this integration: **2,271 passed /389 passing subtests**, zero failures/errors/skips; two existing legacy helper return-value warnings.
- Curated validator: 0 errors /294 existing warnings. Public validator: 0 errors /62 existing warnings. Exclusion validator: 0 errors /2 existing warnings. Key-paper coverage `--check`: exit 0.
- Before/after test and export snapshots: zero unexpected changes; all 117 historical fixtures verified, none created or replaced.
- Independent static test-support review: 40/40 checks passed. Independent post-export semantic review: 2,114/2,114 passed.

Full log SHA-256: `f6e61f46a4e3a7943e866b35a4109bafbd1c10edfeb7de1151ae4e6e1a590ddc`; JUnit SHA-256: `cc4381312f9f7d32ea7a34265412d0a1d3ca3634294abee8865a9964d31d8ec4`. Focused log SHA-256: `a49bc864de0d3ea79e39d03135e77fd02f1b2a7e0ca27180233cf93c93463641`.

Runtime: reused Python 3.12.14, pytest 9.1.1, pytest-subtests 0.15.0, bundled Node 24.22.1 and authorized localhost tests. No dependencies or scientific materials were downloaded. GitHub's successful unchanged baseline retry separately exercised its configured Python 3.14.7 /Node 24.19.0 environment.

Operational receipts, logs and JUnit remain under `/private/tmp/b1s-integration-2026-10-27/recovery/`, including `baseline-recovery-receipt.json`, `full-result.json`, `focused-result.json`, `export-reproducibility.json`, `validation/after-full.json` and `validation/after-reproducibility.json`.

## Preservation and exact commit scope

The independent pre-report preservation gate passed **6,884/6,884 checks**, zero failed. It verifies all 13 pre-report paths, the exact accepted source delta, untouched unrelated records and source/history fingerprints. Receipt: `integrity/pre-report-preservation.json`, SHA-256 `e0a566a96957cc33dc020215de6492990292af4c827cb45dd9753e304d742bcd`. Adding only this documentation file yields the final 14-file scope; a separately hashed final report and staged gate must pass before commit.

```text
UNEXPECTED_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0
EXPORT_REPRODUCIBLE = 1
```

All 128 protected primary-checkout files, all 49 frozen artifacts, the blocked NeurIPS inventory, Batch C's 13 debts, the separate 39-paper inventory, all prior review history, 140 ignored local inputs, the primary checkout and five other extant worktrees remain unchanged. Public export changes are the explicitly authorized B1S outputs, not preservation failures. No other curated/manual records or relationships change. Final staged and post-push receipts bind the exact committed blobs and primary/protected state.

Exact intended 14-file commit allowlist:

```text
data/curated/paper_taxonomy.csv
data/curated/papers.csv
data/curated/review_decisions.csv
data/raw/corpus_quality_batch_b_wave_b1q_2026_10_26/evidence_manifest.json
docs/corpus_quality_batch_b_wave_b1q_2026_10_26.md
docs/corpus_quality_batch_b_wave_b1r_2026_10_27.md
docs/corpus_quality_batch_b_wave_b1s_2026_10_27.md
docs/key_paper_coverage_report.md
docs/public_preview_report.md
tests/baseline_expectations.py
tests/test_corpus_quality_batch_b_wave_b1p.py
tests/test_corpus_quality_batch_b_wave_b1s.py
web/data/public_preview_map_data.json
web/data/public_preview_papers.json
```

No ignored operational caches, TMP receipts, manuscripts, screenshots, protected files, unrelated frontend assets or scientific inputs are staged. The primary checkout is not advanced. Publication is allowed only through one normal fast-forward child commit after all gates pass.

This report is a pre-publication validation receipt, not a claim that its own future commit has deployed. The final commit SHA, fetched/independent remote SHA, Pages build/deployment result and live-byte verification are recorded in the final external publication receipt and delivery report after publication. No publication is declared successful from a push or regression result alone.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

## Machine-readable validated integration summary

```json
{
  "status": "VALIDATED_READY_FOR_CONTROLLED_PUBLICATION",
  "baseline": "dace181c2a9edbb7c467978e9e958e83fdddc143",
  "accepted_decisions": {
    "R026": {
      "types": [
        "method",
        "analysis_study"
      ],
      "decision": "review:001acb4497ed65ffc78b"
    },
    "R253": {
      "types": [
        "method",
        "dataset",
        "benchmark"
      ],
      "decision": "review:be6652347897359ff3b3"
    }
  },
  "corpus": {
    "public": 674,
    "formal": 557,
    "mapped": 613,
    "unmapped": 61,
    "relationship_rows": 1410,
    "unique_paper_institution_pairs": 1410
  },
  "taxonomy": {
    "detection": 621,
    "method": 578,
    "analysis_study": 86,
    "survey": 21,
    "source_attribution": 84,
    "dataset": 138,
    "benchmark": 97,
    "localization": 45
  },
  "batch_b": {
    "historical_actions": 159,
    "historical_papers": 148,
    "historical_unresolved_actions": 131,
    "historical_unresolved_papers": 121,
    "active_public_unresolved_actions": 129,
    "active_public_unresolved_papers": 119
  },
  "focused_passed": 359,
  "focused_subtests": 18,
  "full_passed": 2271,
  "full_subtests": 389,
  "full_failures": 0,
  "full_warnings": 2,
  "EXPORT_REPRODUCIBLE": 1,
  "preservation": {
    "UNEXPECTED_CHANGED": 0,
    "FROZEN_NEURIPS_CHANGED": 0,
    "PREEXISTING_LOCAL_FILES_CHANGED": 0,
    "IGNORED_OPERATIONAL_INPUTS_COMMITTED": 0
  },
  "exact_commit_paths": [
    "data/curated/paper_taxonomy.csv",
    "data/curated/papers.csv",
    "data/curated/review_decisions.csv",
    "data/raw/corpus_quality_batch_b_wave_b1q_2026_10_26/evidence_manifest.json",
    "docs/corpus_quality_batch_b_wave_b1q_2026_10_26.md",
    "docs/corpus_quality_batch_b_wave_b1r_2026_10_27.md",
    "docs/corpus_quality_batch_b_wave_b1s_2026_10_27.md",
    "docs/key_paper_coverage_report.md",
    "docs/public_preview_report.md",
    "tests/baseline_expectations.py",
    "tests/test_corpus_quality_batch_b_wave_b1p.py",
    "tests/test_corpus_quality_batch_b_wave_b1s.py",
    "web/data/public_preview_map_data.json",
    "web/data/public_preview_papers.json"
  ],
  "commits_created_at_report_preparation": 0,
  "publication_claimed_at_report_preparation": false
}
```

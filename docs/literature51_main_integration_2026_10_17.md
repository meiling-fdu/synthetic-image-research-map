# Literature51 integration onto published main — 17 October 2026

This successor integrates validated commit `0c1f4089c64fa768ab2a07d6a1bfc394bd0e7f6b` onto remote `a74bdf79f4d8b3c4fb64af7b83701dce60238289`. The original branch and commit remain unchanged. Common ancestor: `f7e6f721dcca4c992285a86f3fc75706d6d3f091`.

Only the literature delta was replayed. Local `9e7666169cba098f62f022b7f9f60cdf7c7c72e1` is patch-identical (`git range-diff`) to published frontend commit `ef0d93fa2658c532fff54df2bfaf21fec65f5b57`; no prerequisite is omitted or duplicated. All eight remote commits remain ancestors of this integration.

Remote-only commits, oldest first:

- `805edcc5bbd2fb5c1afda348e900f32f02fcd450` — fix: adjudicate corpus quality batch-c wave five-b
- `ef0d93fa2658c532fff54df2bfaf21fec65f5b57` — fix: refine desktop research explorer usability
- `829b3c79e28c02c622dde2129bd6ce7b62eeb27f` — fix: adjudicate corpus quality batch-c wave five-c
- `b41a506453cd0a4c985bf7d1a63e6b2a2d391539` — fix: resolve T527 scope and close batch-c audit
- `91de08a904847c47f60eb3dfd124e3db3300a459` — docs: add batch-b intake and priority triage
- `1ea93c53a3d9f5f822ce27f818d8009274d3b12a` — fix: exclude out-of-scope batch-b wave b1a papers
- `65e9422764c34eaad1d151fff2895e6c7503835f` — fix: adjudicate batch-b wave b1b local evidence
- `a74bdf79f4d8b3c4fb64af7b83701dce60238289` — fix: exclude out-of-scope P490 and resolve journal review

Local-only commits were the frontend equivalent above and the validated literature commit. Conflict resolution keeps all remote existing curated rows exactly, appends the reviewed literature rows, and preserves all 29 remote review decisions before the 52 literature decisions. No metadata conflict required new research or an inferred decision. Latest remote tests are the starting point; current corpus counts are updated and exact historical receipt tests remain pinned to their original endpoints.

Eight textual conflicts were reviewed: review_decisions.csv; key_paper_coverage_report.md; baseline_expectations.py; test_corpus_quality_batch_c_wave5a.py; test_frontend_published_only_filter.py; test_paper_metadata_consistency_audit.py; and both public JSON exports. The two CSV identity tables auto-merged compatibly and were additionally checked against an exact remote-plus-reviewed-delta reconstruction. Public JSON was regenerated canonically from remote outputs, never replaced wholesale by the older integration outputs. The coverage Markdown was regenerated after checking its manual CSV is unchanged.

Actual merged counts: **39 imported + 12 held = 51; 535 curated; 674 public; 557 formally published; 613 mapped; 61 unmapped; 1,410 relationships; 722 taxonomy rows; 14 pending taxonomy reviews; 81 review decisions**. Publication types: 400 conference, 156 journal, 117 preprint, 1 book. All 635 remote public objects and all 1,410 map objects/order are unchanged. The four later remote exclusions account for the difference from the original 678/561/617/1,421 checkpoint. The original reports and review receipts retain their historical counts.

Held IDs remain B01, C01, C02, C03, E01, E04, E06, E07, E09, E13, E15, E18, with exact blockers in `data/processed/literature51_2026_10_16/followup/review.json`. B01/E07 migration locks remain effective. Proto-LeakNet and SCA-Det remain journal imports with their original HOLD rows and append-only resolutions; DinoLizer remains one arXiv preprint, not formally published WIFS proceedings.

The new successor verifier checks the exact remote curated rows plus immutable plan/follow-up delta, every remote public object and map relationship, original evidence hashes, allowed tracked inventory, held identities, unique titles/DOIs/arXiv IDs, and all committed reproduction inputs. Negative regressions reject replacing remote classifications or dropping a new import. Original import/check entry points dispatch to this strict successor only when its explicit manifest exists; historical baseline logic and receipts remain intact.

Validation: the independent index checkout passed **95 focused tests plus 12 subtests**, and the final byte-prefix/identity checks passed **6 additional affected tests**. Both metadata validators report zero errors (curated: 294 warnings; map: zero warnings; bibliography: 62 unresolved-affiliation warnings). Two canonical regeneration runs reproduce both public JSON files byte-for-byte. Every upstream CSV prefix, including sixteen mixed-CRLF taxonomy rows, is preserved exactly; E17 is patched before appending its new row.

The broader 34-module affected run evaluated 437 tests: 430 passed, 7 failed, plus 15 subtests passed. One new failure was the historical test's attempt to read ignored fixture paths with `git show`; its live-file assertion was restored and the entire B1C module passed in the independent 95-test run. The six residual names and normalized messages exactly match the current remote baseline (387 passed, 6 failed, 15 subtests). Thus 431/437 affected checks pass after the targeted correction, with zero new regressions. The remote failures comprise one old OpenAlex retrieval-cache dependency and five missing `.DS_Store` fixture checks; no cache was retrieved, no test skipped, and no assertion suppressed to hide them. The four separately saved original full-suite failures remain exactly unchanged; the full suite was not rerun.

The security scan found no credentials, authenticated session headers, PDF payloads or full manuscripts. One Springer `c-article-body` CSS signature was inspected and cleared: its contents are a chapter landing page with abstract, references, affiliations and purchase controls. All 117 original literature evidence/report/receipt files are byte-identical to the validated commit. No excluded bulk retrieval inputs entered the staging set. Two previously untracked audit documents are now legitimate remote tracked files and are verified against the published remote blobs; no local copy is used.

Exact staging inventory and immutable evidence hashes: `data/processed/literature51_2026_10_16/main_integration/manifest.json`. Current validation and lossless baseline/current/focused JUnit receipts: `main_integration/validation.json` and its adjacent `.xml.gz` files. These supplement the original 147-path historical manifest without rewriting it. All 304 original untracked paths/content hashes and the original branch/HEAD remain unchanged.

Publication is authorized only after a final fetch confirms the remote base has not advanced; the actual push/Pages outcome is reported in the conversation. No full-suite run, discovery, retrieval, new paper import, frontend change, validator change, taxonomy policy change, or unrelated cleanup is part of this integration.

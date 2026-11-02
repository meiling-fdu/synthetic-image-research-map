# B5-02 actual historical guard failure matrix

**Verdict: source correct within the authorized B4-03 scope; historical gate blocked. Keep export, full regression, validators, staging and publication stopped.**

The recorded early gate ran three unchanged tests from `d109c70f6994906ec3d9197baad51cf9d8e51f7c` and returned exit1: **3 failures,0 errors**. This review inspected those existing artifacts and source bytes only. It ran no additional tests, validators, exporters or network requests and made no repository changes. No correction is proposed or implemented.

## Actual failures

| Guard | Original checkpoint and purpose | Recorded failure | Independent classification |
|---|---|---|---|
| `tests/test_corpus_quality_batch_b_wave_b1s.py::test_all_accepted_source_bytes_and_B1Q_B1R_reports_survive_controlled_export[data/curated/paper_taxonomy.csv]` at line316 | Keep the B1S accepted source bytes intact through its controlled export, with B1Q/B1R evidence still live. Taxonomy remained unchanged at that historical endpoint. The function reads papers/decisions at its immutable publication, but reads taxonomy from current ROOT. | 2388617d62211ebea18af8827095a1a776ce0c160d1942511212fa7324fe0fb9 expected; 98026dec50ed5b81b60b4792da623e89468da5ee3da96ef7a4a9fc5910da05d3 actual | Historical checkpoint byte assertion encounters later explicitly authorized current taxonomy. Exact30-cell taxonomy change is the expected B4-03 source delta; no source corruption or evidence alteration is shown. The guard failure remains real and blocking. |
| `tests/test_corpus_quality_batch_b_wave_b4_02.py::test_public_identities_task_types_and_all_relationship_pairs_are_preserved` at line378 | B4-02 changes journal venue bindings only; its public identities, tasks/types, relationships and entire authoritative taxonomy must stay fixed to the original checkpoint. The final byte check deliberately prevents unchanged public JSON from hiding a source taxonomy edit. | 2388617d62211ebea18af8827095a1a776ce0c160d1942511212fa7324fe0fb9 expected; 98026dec50ed5b81b60b4792da623e89468da5ee3da96ef7a4a9fc5910da05d3 actual | Historical venue-only transaction invariant conflicts with B4-03 authorized research-type additions. The public JSON is still d109, so earlier public counts/pairs/type assertions reached and passed; the final live-source byte check correctly detects the new30-cell authoritative taxonomy delta. This is not current source/public synchronization acceptance. |
| `tests/test_corpus_quality_batch_b_wave_b5_01.py::test_all_127_formal_rows_preserve_the_original_103_bytes_and_both_append_histories` at line155 | Authenticate exact original103 + B4-01 nine + B4-02 fifteen formal decisions, immutable raw prefix, exact append rows and native identity uniqueness at B5-01 completion. It assumes its own127-row endpoint remains current ROOT. | 103 baseline rows and127 expected current; actual103 baseline and138 current | The B4-03 eleven-row authorized append correctly produces138 current rows; original127 raw bytes and every historical decision remain exact. The count assertion binds historical B5-01 completion to a later current registry. Real blocking failure does not establish decision rewrite, duplicate IDs or an evidence problem. |

The B4-02 test reached the public membership/count/pair/task/type assertions without failure because both public JSON files intentionally remain exact d109 bytes. Its final authoritative-taxonomy assertion caught the new approved source state. First differing byte is offset102833 (zero based): comma0x2c became semicolon0x3b. This does not establish current source/public synchronization.

The B5-01 test stopped at its first count assertion. Assertions below that line were not executed; the following read-only comparisons independently establish prefix and append preservation rather than claiming those pytest assertions passed.

## Source and byte authentication

| Source path | d109 SHA-256 | Accepted/current SHA-256 | Rows |
|---|---|---|---|
| `data/curated/papers.csv` | `0fd82c4b242d86b6fe4dbf0c8dcd98cccc6a6930c0bd2e93b416a49a1bf0c3e4` | `e38c269bb4870ef03914f993a247f809cdbb5c0daf06ae01efa526c762b15d87` | 535 → 535 |
| `data/curated/paper_taxonomy.csv` | `2388617d62211ebea18af8827095a1a776ce0c160d1942511212fa7324fe0fb9` | `98026dec50ed5b81b60b4792da623e89468da5ee3da96ef7a4a9fc5910da05d3` | 722 → 722 |
| `data/curated/review_decisions.csv` | `3430814d49d8e73a5836c71fb04b5acb3e95de3dac56bb795ca62dcf734bfda5` | `9d2a5cd8190634b8bf85afb969549b0a62652e50697c5b129d64970fd64a44ea` | 127 → 138 |

- Exactly120 allowlisted files match their prepared bytes and sizes:3 changed curated CSVs plus117 new portable archive/manifest/report paths. No tracked test, helper, implementation, central baseline or historical receipt changed. The117 new physical paths consist of114 ordinary Git-visible paths plus3 authenticated archived `.log` copies ignored by `.gitignore:59`; this is an inventory/staging distinction, not missing evidence. Staging remains stopped.
- Source delta is exactly35 accepted cells:5 in papers.csv and30 in paper_taxonomy.csv. All source bytes match the accepted B4-03 native checkout.
- review_decisions.csv preserves the entire127-row d109 raw byte prefix and those127 parsed rows; its11 appended rows match every original B4-03 formal decision exactly. Native decision IDs are unique;6 rows are no_action_after_review and5 unresolved.
- The portable evidence entries match their declared original external bytes and pinned hashes. This authenticates transfer; no scientific adjudication was repeated.
- Both public JSON outputs are unchanged d109 bytes. Export, post-export validators, full regression and reproducibility remain unperformed.

| Failed test source | d109/current/recorded SHA-256 |
|---|---|
| `tests/test_corpus_quality_batch_b_wave_b1s.py` | `bde78da60eaf4f3660725dade4d11aed2225e13d28f675eabf52790cde65f5ec` |
| `tests/test_corpus_quality_batch_b_wave_b5_01.py` | `87a1766308c46797b2b921e47da2755ea5f4c9144904b4fddd21b34ce0b5fa64` |
| `tests/test_corpus_quality_batch_b_wave_b4_02.py` | `ede273958436346d7b94e24c4f970a6fca6fc6528f7e87b7f0ce87d71077f3a3` |

The full tracked tests tree has zero diff against d109, and each failed file matches its before/after gate receipt. Exact log/JUnit authentication:

- Gate log SHA-256: `72bb0fdcc81d3eb46fb24a629fb6a38006effc2195ad7172241efb529aea3d85`
- JUnit SHA-256: `fb1fceb83c6be0d59d69a0deda19a8ed18a9ee2a63fc5a938aedd34319c74a81`

## Observed versus forecasted

Only the three selected tests above were run and failed. The prior static inventory contained14 fixed-endpoint categories in total; these three overlap it, leaving11 categories unexecuted. The24 shared current-taxonomy baseline consumers were inventoried but were not run as a full suite. There is no observed full-suite failure count and no full-suite result to report.

## Required historical/current boundary criteria

- Preserve d109 historical test source bytes, original checkpoint assertions and every original evidence/report/manifest/hash; no overwrite of prior acceptance/failure receipts.
- A historical endpoint must authenticate the exact original source/public/decision snapshot and run original assertions at that immutable endpoint. Passing historical replay alone cannot accept B5-02.
- Independent current-source checks must establish d109 to B4-03 exact35-cell allowlist, prior127 raw bytes,11 exact native/evidence-bound decisions,6 accepted and5 held actions, original-action accounting and no unrelated source changes.
- Independent post-export B5-02 checks must verify142dataset/101benchmark and P231 qualified MAD track,674public/557formal/613mapped/1410relationships, unchanged tasks/identities/authors/affiliations/locations, preserved prior B5-01 effects and seven-output byte reproducibility.
- Protection negatives must continue rejecting changed historical snapshots, unexpected paths, unauthorized taxonomy/decision edits, tampered source/evidence bindings, extra terminal closures and loss of original prefix.
- Any proposed narrow boundary correction must be documented only after this actual failed checkpoint, reviewed independently against exact source and test diff, and require explicit authorization under the user stop rule before implementation or rerun. No blanket exemption, changed old hash/count, skip, xfail, weakened assertion or automatic failed-gate retry.

These criteria describe what an independent review must protect. They do not authorize or specify a patch, do not change the user stop instruction, and do not permit further execution while this gate remains blocked.

Machine-readable per-check evidence, exact command, three failure classifications and the original forecast inventory are in `historical_guard_failure_matrix.json`. All17 independent read-only comparisons in this matrix passed.

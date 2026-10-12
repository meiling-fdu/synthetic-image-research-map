# T527 final scope decision — accepted exclusion

Final adjudication: 2026-10-12, following manuscript verification on 2026-10-11. This section supersedes the preserved abstract-only assessment below. The maintainer's conditional approval is satisfied: **`T527_SCOPE_EXCLUDE`**, reason **`TRAINING_IMAGE_PROVENANCE_RETRIEVAL_OUTSIDE_CORE_FORENSIC_SCOPE`**. The decision applies the existing narrow scope; it does not introduce a fourth task label.

## Verified manuscript and scientific evidence

The [specified five-page copy](https://gwern.net/doc/ai/anime/danbooru/2024-xia.pdf) matches the canonical title (case/line-wrap normalization), ordered authors Xiaojie Xia, Liuan Wang, Jun Sun, Akira Nakagawa, and DOI `10.1109/LSP.2024.3388958`. Its IEEE notice identifies an accepted, not fully edited author version. The third-party archive is neither IEEE nor an author repository; final-IEEE byte equivalence is unverified. All five pages were examined; referenced appendices are absent from this copy.

Sections III.A–C describe image-text learning, visual candidate retrieval and cross-modal re-ranking. The output is similar reference/training images. Section IV.A evaluates transformed-image retrieval on a Danbooru-derived dataset: Table I reports R@1/5/10/50/100 of **90.10/96.00/97.35/99.25/100.00%**. Section IV.B's generated-image demonstrations are qualitative, without ground-truth query/source pairs. These retrieval scores do not evaluate authenticity, generator identity or spatial forensics. Duplicate-content matching likewise does not establish real/fake detection.

No substantive A/B/C core task is established in this examined manuscript. Confidence is **high within that version and the approved narrow scope**; no claim is made about unexamined final-IEEE or appendix content. The [evidence manifest](../data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json) records page/section locators, identity checks, the document hash and limitations. The PDF and rendered pages remain temporary and are not repository artifacts.

## Applied reversible mechanism and impact

One active `out_of_scope` row, `exclusion:01bbb5fbdfbbaedf2870`, was appended to [`paper_exclusions.csv`](../data/curated/paper_exclusions.csv). One linked scope decision, `review:3781fd7521baf1916ffc`, was appended to [`review_decisions.csv`](../data/curated/review_decisions.csv) with action `exclude_paper_scope`. Both use the canonical DOI/OpenAlex identity; no curated paper ID was invented.

The exclusion gate removes one formal public paper and its two Fujitsu map relationships. Historical taxonomy remains `source_attribution; fully_generated; method`; bibliographic, author, affiliation, raw evidence and prior review records are preserved. No task set was emptied. A later explicitly approved restoration can deactivate the exclusion and regenerate exports through the existing mechanism.

| Measure | Published Wave 5C before | After exclusion |
| --- | ---: | ---: |
| Public / formal / mapped papers | 639 / 531 / 617 | 638 / 530 / 616 |
| Relationship rows / unique pairs | 1,421 / 1,421 | 1,419 / 1,419 |
| Detection / source attribution / localization | 587 / 85 / 43 | 587 / 84 / 43 |
| Method / dataset / benchmark / survey / analysis study | 547 / 132 / 88 / 20 / 78 | 546 / 132 / 88 / 20 / 78 |

Batch C is **28 resolved, 13 external evidence debts, zero remaining maintainer judgments**. The 13 external questions are unchanged and remain scientifically unresolved. See the [closeout report](corpus_quality_batch_c_closeout_2026_10_11.md) for their inventory and validation.

Validation in the existing isolated worktree passed **137 focused tests and 12 subtests**, then one complete suite: **1,719 tests and 389 subtests passed, zero failures, zero skips, two existing warnings**. Current-scope curated, public, exclusion and key-paper-coverage validators returned **zero errors**. Curated warnings are 253 (one additional expected alternate-identity warning for T527's blank curated `paper_id`); public bibliography warnings remain 23 and exclusion warnings 2. No identifier was fabricated to hide that warning.

The T527 semantic check removes exactly one paper and two Fujitsu relationships; all other public records and non-timestamp metadata are unchanged. Original bibliography, taxonomy, affiliations and prior scientific evidence remain byte-identical. All 49 frozen NeurIPS files and the 128 protected primary-checkout files match their receipts. The temporary audit script and manuscript stay outside the repository and commit.

```text
FULL_SUITE_FAILURES = 0
EXPORT_REPRODUCIBLE = 1
UNEXPECTED_CHANGED = 0
FROZEN_NEURIPS_CHANGED = 0
PREEXISTING_LOCAL_FILES_CHANGED = 0
IGNORED_OPERATIONAL_INPUTS_COMMITTED = 0
```

Two sequential offline export verification passes completed with exit code 0. Each left all 4,296 checked paths byte-identical, including the seven deterministic outputs. No search or new source retrieval was performed.

These are pre-publication validation receipts. Commit and remote-SHA verification follow separately; no push result is pre-asserted here.

---

## Preserved abstract-only assessment — historical, superseded

The following original packet records the evidence available before manuscript verification. Its `INSUFFICIENT_EVIDENCE` recommendation, public counts and pending T527 status are historical, superseded by the final decision above. It is retained to make the change in evidence and authority auditable.

# Batch C T527 — maintainer scope decision packet

Evidence freeze: 2026-10-11. Authoritative baseline: `829b3c79e28c02c622dde2129bd6ce7b62eeb27f` (published Wave 5C). This is a local-evidence review, not a taxonomy or scope change. T527 remains `SCOPE_OR_TASK_EVIDENCE_REQUIRED` and is separate from the 13 external Batch C evidence debts.

## Canonical identity and current state

| Field | Recorded value |
| --- | --- |
| Review / canonical identity | T527 / `doi:10.1109/lsp.2024.3388958` |
| Title | *Towards Generated Image Provenance Analysis via Conceptual-Similar-Guided-SLIP Retrieval* |
| Authors / venue | Xiaojie Xia, Liuan Wang, Jun Sun, Akira Nakagawa; *IEEE Signal Processing Letters* (2024) |
| Source identity | DOI above; OpenAlex `W4394862914` |
| Current taxonomy | `tasks=source_attribution`; `image_scopes=fully_generated`; `research_types=method`; task evidence tier `abstract`, source local OpenAlex raw cache; task review `reviewed` |
| Registry/export state | OpenAlex-matched candidate with a DOI-keyed row in [`paper_taxonomy.csv`](../data/curated/paper_taxonomy.csv), no `paper_id` in that row and no separate curated-papers row. One active public record in [`public_preview_papers.json`](../web/data/public_preview_papers.json) and two map relationships, Fujitsu (China) and Fujitsu (Japan), in [`public_preview_map_data.json`](../web/data/public_preview_map_data.json). No active exclusion row for this DOI. |

The public record is a formal journal paper, currently included and mapped. The task-provenance excerpt in the taxonomy row is only the title, so its `reviewed` flag does not by itself settle this narrower Batch C task question.

## Local scientific evidence

The complete stored abstract in the public export describes CS-SLIP as a self-supervised, contrastive, conceptual-similarity-guided image/text representation with bidirectional cross-modal retrieval and re-ranking. Its target is finding replicated or similar **training images** in the corpus behind generated images. The reported qualitative/quantitative experiments concern that replication/retrieval behavior. This is evidence for a provenance-retrieval method; it is not an evaluated generator-identity endpoint merely because the word “provenance” appears in the title.

The identity and abstract are also preserved in the two local OpenAlex captures, [`20260619T193231Z_017_generated-image-provenance.json`](../data/raw/openalex/20260619T193231Z_017_generated-image-provenance.json) and [`20260619T211726Z_017_generated-image-provenance.json`](../data/raw/openalex/20260619T211726Z_017_generated-image-provenance.json). The examined OpenAlex location is a publisher location, with no PDF URL or best open-access location. The [published evidence-debt triage](corpus_quality_batch_c_evidence_debt_triage_2026_10_08.md#t527--separate-maintainer-scope-decision) records no saved identity-matched full manuscript. The [original corpus audit](corpus_quality_audit_2026_10_04.md) sought full-paper task interpretation; no new paper was obtained for this packet. The negative observations below therefore describe **the local abstract**, not a proven absence throughout the full paper.

| Possible scientific endpoint | What the local record establishes | Task implication |
| --- | --- | --- |
| A. Synthetic-image authenticity detection | No separately defined or scored real-versus-generated decision in the stored abstract. | `detection` is not supported by this evidence. |
| B. Generator/model source attribution | No generator-identity label space, attribution decision rule, or source-model evaluation in the stored abstract. | Training-example matching must not be treated as generator attribution by implication. |
| C. Synthetic/manipulated-region localization | No predicted spatial mask, region, or scored localization endpoint in the stored abstract. | `localization` is not supported by this evidence. |
| D. Training-image provenance/retrieval | Retrieval and re-ranking of similar or replicated original training images is the explicitly described method and evaluation target. | Supported, but its fit to the current three core task labels is the unresolved scope question. |

## Governing scope and review history

The current [narrow Tier 2 scope application](systematic_tier2_policy_application_2026_09.md) defines passive source attribution through naturally occurring image-generation traces to generators/models/sources; its approved narrowed rule superseded the earlier precedent proposal **for new candidates**. The earlier [precedent review](systematic_tier2_scope_policy_review_2026_09.md#policy-ATTRIBUTION) did list CS-SLIP as included training-source provenance. That historical inclusion is evidence of a past policy interpretation, not proof that training-image retrieval satisfies the current task boundary or permission to alter this existing record automatically.

The [pre-decision Batch C sheet](corpus_quality_batch_c_decision_sheet_2026_10_05.md#t-policy-3--existing-vocabulary-applicability-t3) suggested clearing `source_attribution` while keeping the paper public. Its later [maintainer decision section](corpus_quality_batch_c_decision_sheet_2026_10_05.md#d-maintainer-decisions--batch-c-phase-1-2026-10-05) **supersedes that suggestion**: locked T3 requires every active public paper to have at least one core task (`detection`, `source_attribution`, `localization`). If careful review finds none, it triggers scope review, not an empty public task set. The [policy ledger](../data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json) leaves T527 `MAINTAINER_SCOPE_JUDGMENT_REQUIRED` / `SCOPE_OR_TASK_EVIDENCE_REQUIRED`; no T527 remediation was approved in Waves 1–5C.

## Decision alternatives

| Alternative | Assessment on the evidence freeze | Consequence if separately authorized |
| --- | --- | --- |
| `RETAIN` | Requires the maintainer to affirm explicitly that this demonstrated training-image/source-retrieval endpoint belongs within `source_attribution` under the current narrow scope, or to obtain primary evidence of a different core endpoint. The older inclusive precedent alone is insufficient. | Keep the public paper, two relationships and task, with a recorded scope rationale; no silent expansion of the label. |
| `RETAG` | No supported replacement core task: A, B and C are not established by the local abstract, and D has no separate controlled task label. | Only an independently evidenced core task could be assigned; the record may not remain active with `tasks=[]`. |
| `EXCLUDE` | Plausible if the maintainer chooses the narrower boundary and an identity-matched primary full text confirms training-image retrieval is the only substantive endpoint. The current abstract cannot establish that negative full-paper finding. | Use the established reversible DOI-keyed active `out_of_scope` mechanism in [`paper_exclusions.csv`](../data/curated/paper_exclusions.csv), keeping the source/taxonomy/provenance history. Then regenerate deterministic public outputs in a separately authorized remediation. Do not delete the source record. |
| `INSUFFICIENT_EVIDENCE` | **Recommended for this local-only freeze.** D is positively documented, but the full paper is not locally available and the historical inclusive precedent versus current narrow task interpretation needs an explicit maintainer choice. | Preserve the current public assignment provisionally and keep the review open; make no data or export change. |

**Recommended outcome: `INSUFFICIENT_EVIDENCE` — maintainer decision required.** Confidence is **high** that the stored abstract describes D; **moderate-high** that it does not independently substantiate A, B or C at abstract level; and **moderate/limited** about final scope without an identity-matched complete paper and explicit interpretation of training-image provenance. The maintainer should decide whether D itself fits the current controlled `source_attribution` boundary. If not, obtain the primary paper and assess whether any A/B/C endpoint is actually performed before choosing exclusion. This packet does not assume D implies B.

No recommendation is executed. T527 keeps `source_attribution`, remains public/formal/mapped, and retains both Fujitsu relationships. An eventual exclusion, **if approved later**, would conditionally change 639/531/617 public/formal/mapped to 638/530/616, 1,421 relationship rows and unique pairs to 1,419 each, `source_attribution` 85→84 and `method` 547→546; these are projections, not current counts. No active public record is left with an empty core-task set by this review.

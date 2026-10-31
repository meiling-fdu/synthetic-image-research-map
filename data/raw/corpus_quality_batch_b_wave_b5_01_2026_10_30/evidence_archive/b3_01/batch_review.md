# Batch B Wave B3 — first evidence batch B2-01

Baseline `7fc8ceae702324628335944cf4b545a3733fdc56`. Exactly the nine assigned publication actions were reviewed in their original order; batch membership, priority 1 and dependencies are unchanged. P034/P254/P305 were all in this first batch and reused local evidence.

**Scope:** B2-01 asks for canonical formal URLs. The outcomes below concern those publication questions, not taxonomy. No scientific contribution is inferred from a title, abstract, dataset release or experimental table. P034’s completed scientific review is reused with all caveats; other absent method/result evidence is marked not reassessed. The user explicitly confirmed this bounded publication scope. No new manuscript/scientific review was substituted for it. No material taxonomy inconsistency was established incidentally; potential taxonomy follow-ups: none.

| Action | Exact canonical paper ID | Paper | Provisional result | Proposed formal URL |
| --- | --- | --- | --- | --- |
| P034 | `curated:aa7dceb70828cdd6ad39` | Beyond Artifacts: Real-Centric Envelope Modeling for Reliable AI-Generated Image Detection | `SUPPORTED_ADDITION` | https://link.springer.com/chapter/10.1007/978-3-032-37429-5_14 |
| P254 | `doi:10.48550/arxiv.2407.10575` | A Survey of Defenses Against AI-Generated Visual Media: Detection,Disruption, and Authentication | `SUPPORTED_ADDITION` | https://doi.org/10.1145/3770916 |
| P305 | `doi:10.48550/arxiv.2312.02625` | Diffusion Noise Feature: Accurate and Fast Generated Image Detection | `SUPPORTED_ADDITION` | https://doi.org/10.3233/faia250925 |
| P028 | `curated:92fe1dfd435209b21ff4` | Anchor-Regularized Adaptation for Generalizable AI-Generated Image Detection with DINOv3 | `EVIDENCE_INSUFFICIENT` | Not established |
| P097 | `curated:8503e319e1f4890c2e28` | FAIR: Feature-Augmented Implicit Regularization for AI-Generated Fake Image Detection | `SUPPORTED_ADDITION` | https://link.springer.com/chapter/10.1007/978-3-032-37321-2_32 |
| P105 | `curated:be2900947b322f9eb905` | Few-Shot Synthetic Image Attribution: Identifying Unseen Generators with Limited Samples | `SUPPORTED_ADDITION` | https://link.springer.com/chapter/10.1007/978-3-032-37550-6_18 |
| P150 | `curated:7a5ce57b121b69752867` | LoRC: Detecting AI-Generated Images via Low-Rank Collapse in Semantic Residuals | `SUPPORTED_ADDITION` | https://doi.org/10.1007/978-3-032-37464-6_12 |
| P177 | `curated:b460935b64c35e1d074a` | Prior-Conditioned Gaussian Discriminants for Generalizable AI-Generated Image Detection | `SUPPORTED_ADDITION` | https://doi.org/10.1007/978-3-032-37350-2_34 |
| P229 | `curated:55bc4360e3d312e696b7` | UC-VLM: Consistency-Driven Learning for AI-Generated Image Detection with Vision-Language Large Models | `SUPPORTED_ADDITION` | https://doi.org/10.1007/978-3-032-37023-5_10 |

**Eight supported link additions; one insufficient action (P028). Proposed taxonomy changes: none.** Unsupported/identity-blocked outcomes: none. Every original review action remains formally open; historical 131 and active-public 129 unresolved actions are unchanged.

## Evidence, limitations and disagreement

- P034: reuse the verified B1M 19-page Springer source receipt, exact title and 12 shared ordered authors. Publisher adds Manni Cui (13 authors) and Chen casing differs. All previous numerical/arithmetic counterexamples, source/release limits and version observations are copied unchanged. This supports only a conditional same-work formal link, not full manuscript/bibliographic equivalence or new empirical validity.
- P254: exact title after comma-whitespace normalization, all 7 authors, deposited ACM formal DOI and retained arXiv v3 linkage. Preserve online 20 Nov 2025 versus print 30 Apr 2026. Scientific contents were not reassessed.
- P305: exact title/both authors and retained arXiv v3 formal DOI link match the IOSPress deposit. Preserve ECAI 2025 proceedings context; book-chapter deposition alone is not a new book classification. No scientific/reproducibility endorsement.
- P097/P105: direct official Springer chapter headers, full ordered authors, chapter DOI and exact ECCV proceedings contents establish the formal links. Chapter first-online dates differ by one day from the volume eBook dates; those dates are not silently interchanged. No PDF/method/results equivalence is certified.
- P150/P177/P229: exact title and full ordered authors match current records and preserved arXiv metadata. Direct publisher HTML citation metadata verifies chapter identity and DOI; the same-edition proceedings TOC confirms container. Publisher pages have no explicit arXiv crosslink; full-text equivalence remains unverified.
- P028: preserved exact author/arXiv identity and author-lab ACM MM 2026 Main claim are available, but targeted official searches did not yield the exact ACM archival item. Keep `EVIDENCE_INSUFFICIENT`; do not infer nonpublication, revoke formal status or guess a DOI.
- Independent QC identified inaccurate group-B capture locators, not incorrect publisher identity: the specific TOC excerpt is in official-book-title-locators.json and the existing chapter-click chain is separately captured. P150’s TOC byline is truncated; the complete 9-author proof is raw HTML citation_author metadata. Preserve original v1 plus corrected v2 and QC receipts; no new retrieval and no forced scientific consensus.

## Validation and B4 boundary

Every assigned action has one per-paper JSON record, original question/current identity, provisional result, exact sources/locators/checksums, limitations and independent QC. Three local cases and six externally checked cases were cross-reviewed by independent reviewers. Final validation/preservation counts and integrity flags are in `validation.json`; no full test suite or export is run for evidence-only artifacts.

B4 is not authorized or begun. `b4_handoff.json` lists the eight conditional URL additions, P028’s missing gate, exact record hashes and acceptance prerequisites. It explicitly separates supported authoritative URL fields from derived formal_url/formal DOI, preserves stable/arXiv identities, and requires an exact URL/action identity check beyond a venue fingerprint. No current task/type/publication/institution/relationship value, review decision or inclusion decision changes.

## Actual effort and source costs

Primary reviewer wall time: 20.54 aggregate worker-minutes across three parallel groups (368.937, 327.296, 536.253 seconds). This includes model/tool waiting; human analyst hours were not measured. The raw instrumented elapsed through packaging is 615.76 minutes and includes a long interrupted/idle interval; it is not active analyst effort. Initial plan verification is excluded. Neither raw elapsed nor aggregate worker time can be presented as human labor or directly substituted for B2’s 125–245 analyst-minute estimate.

Zero full manuscripts, supplements, code/data downloads or paid source purchases/API fees. Group A: 5 web calls with 8 targeted queries, 4 official metadata opens/clicks and 2 same-document section views; 4 unique official metadata documents. Group B: 3 search queries plus recorded book/chapter/find operations; 3 direct successful chapter HTML captures, 1,054,876 body bytes, durations 5.623/5.941/5.999 seconds, and 3 sandbox DNS failures before connection. No blocked publisher retries. Opaque web transport request counts/bytes are unknown; serialized capture sizes are not wire-transfer sizes. Model/tool billing is not exposed and is not claimed to be zero. Full details are in `effort_and_retrieval.json`.

## Preservation and stop

All artifacts are outside the isolated repository. Primary checkout/concurrent CLIP/BCP work, protected 128 files, frozen 49 artifacts, Batch C 13 debts, separate 39 inventory, B1Q/B1R/B1S evidence, CI acceptance archive and all three B2 planning inputs remain unchanged. No staging, commit, push, deployment, export or authoritative review closure occurred. The next batch and B4 have not begun.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`

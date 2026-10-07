# Corpus Quality Batch C External Evidence and Adjudication — Wave 3B-3

Evidence date: 2026-10-07.

Scope: the finalized first-pass T1 review for T503, T611, and T634 only. One authoritative primary document was attempted per paper. No research-type question was reviewed and no remediation was applied.

| Review | Paper | Primary source | Decision/class space | Real-image role | Authenticity evaluation | Attribution/fingerprint evaluation | Adjudication | Evidence outcome | Final disposition | Proposed taxonomy |
|---|---|---|---|---|---|---|---|---|---|---|
| T503 | *ManiFPT: Defining and Analyzing Fingerprints of Generative Models* | [Official CVF paper](https://openaccess.thecvf.com/content/CVPR2024/papers/Song_ManiFPT_Defining_and_Analyzing_Fingerprints_of_Generative_Models_CVPR_2024_paper.pdf) | Not established; the official PDF returned HTTP 403 | Not established | Not established | Not established | `EVIDENCE_STILL_INSUFFICIENT` | `EVIDENCE_STILL_INSUFFICIENT` | `REMEDIATION_NOT_APPLIED` | none |
| T611 | *Does a GAN Leave Distinct Model-Specific Fingerprints?* | [Official BMVC paper](https://www.bmvc2021-virtualconference.com/assets/papers/0197.pdf) | Not established; the official PDF redirected to an unrelated unsafe domain | Not established | Not established | Not established | `EVIDENCE_STILL_INSUFFICIENT` | `EVIDENCE_STILL_INSUFFICIENT` | `REMEDIATION_NOT_APPLIED` | none |
| T634 | *Do GANs Leave Artificial Fingerprints?* | [Authoritative arXiv paper](https://arxiv.org/pdf/1812.11842) | Multiclass source identification across GAN variants and two real cameras; separate 1,000-image real-versus-GAN challenge | Real cameras are source classes; real is also the explicit authenticity class in the challenge | Fingerprint/deep-network fusion reports AUC 0.999 on real-versus-GAN classification | Same/cross-GAN AUC 0.990/0.998; larger source attribution reports ROCs, confusion matrix, 90.3% accuracy and 90.1% after JPEG | `DETECTION_TASK_SUPPORTED` | `EVIDENCE_RESOLVED_NO_CHANGE` | `TAXONOMY_RETAINED` | retain `detection;source_attribution` |

## Resolution

- `DETECTION_TASK_SUPPORTED = 1`
- `ATTRIBUTION_ONLY_NO_DETECTION = 0`
- `EVIDENCE_STILL_INSUFFICIENT = 2`
- External Batch C unresolved: `24 → 23`
- Remaining task evidence: `8 → 7`
- Remaining task cases: T236, T137, T141, T572, T576, T503, and T611.
- Institution evidence remains 1; research-type evidence remains 15.
- T527 remains a separate maintainer scope judgment and is outside the external-evidence count.

The three-document budget was exhausted exactly. T503 and T611 stopped at their first terminal access failure; no alternate or mirror was used. T634 was resolved from one complete primary paper. The authoritative corpus, taxonomy, and exports remain unchanged.

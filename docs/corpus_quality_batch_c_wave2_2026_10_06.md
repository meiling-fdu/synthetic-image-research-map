# Corpus Quality Batch C External Evidence and Adjudication — Wave 2

Date: 2026-10-06

Scope: U010 and U017 only. The evidence acquisition respected the one-primary-document-per-paper budget. Adjudication applies one authoritative remediation for U017 and leaves U010 unresolved. It makes no institution registry, hierarchy, coordinate, taxonomy, or exclusion change.

| Review | Paper | Official source | Retrieval result | Paper-time affiliation evidence | Adjudication | Final disposition |
|---|---|---|---|---|---|---|
| U010 | *Diffusion-Driven Forgery Detection: Distilling Latent Features for Generalized Image Forensics* | [Official IEEE formatted paper](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=11494515) | IEEE returned HTTP 418 / “Unable to Load Page”; no affiliation block was exposed. | None. The local conflict remains context only: the current mapping assigns all four authors to SUES while its recorded text says Shanghai University. Policy I1 keeps the two institutions distinct. | `EVIDENCE_STILL_INSUFFICIENT` | Remains unresolved. Required evidence: accessible official IEEE paper metadata/PDF containing the complete author-affiliation block and author markers. Do not choose either institution before then. |
| U017 | *Unified Detection of Synthetic and Manipulated Images via Dual-Stream Artifact Fusion* | [Official ACM formatted paper](https://dl.acm.org/doi/pdf/10.1145/3810988.3812660) | The complete page-one author/affiliation block rendered. | Author order: Thinh-Phat Vo; Dang-Khoa Mai; Minh-Triet Tran; Trong-Le Do. ACM uses direct author blocks rather than numbered affiliation superscripts. Every author block separately lists “University of Science, VNU-HCM / Ho Chi Minh, Vietnam” and “Viet Nam National University / Ho Chi Minh City, Vietnam.” Trong-Le Do’s asterisk marks the corresponding author only. | `EVIDENCE_RESOLVED_CHANGE` / `EXPLICIT_DUAL_AFFILIATION_SUPPORTED` | `REMEDIATION_APPLIED`: all four authors map to the University of Science member (`institution:806523d1aae41484`) and the separately listed VNU-HCM parent (`institution:19d2ee8d44bfb9f0`). |

## U017 author assignment

The official ACM paper directly assigns both listed organization units to each author:

| Author | Paper-time affiliations |
|---|---|
| Thinh-Phat Vo | University of Science, VNU-HCM; Viet Nam National University |
| Dang-Khoa Mai | University of Science, VNU-HCM; Viet Nam National University |
| Minh-Triet Tran | University of Science, VNU-HCM; Viet Nam National University |
| Trong-Le Do | University of Science, VNU-HCM; Viet Nam National University |

Policy I2 therefore supports the named member and the separately listed parent. The evidence does not authorize any additional institution, hierarchy, or coordinate change.

The remediation also corrects the second author identity from “Daniel Mai” to “Dang-Khoa Mai.” The two existing canonical identities were reused. The member retains its reviewed parent relation to VNU-HCM. No institution, alias, hierarchy, or coordinate record changed.

## Corpus impact

| Metric | Before | After |
|---|---:|---:|
| Public papers | 639 | 639 |
| Formal publications | 531 | 531 |
| Mapped papers | 616 | 617 |
| Relationship rows | 1,419 | 1,421 |
| Unique paper–institution pairs | 1,419 | 1,421 |

Taxonomy is unchanged: detection 592; source attribution 85; localization 41; method 547; dataset 133; benchmark 88; survey 20; analysis study 78.

## Resolution

- `EVIDENCE_RESOLVED_CHANGE = 1`
- `EVIDENCE_RESOLVED_NO_CHANGE = 0`
- `EVIDENCE_STILL_INSUFFICIENT = 1`
- External-primary-source actions: `30 → 29`
- T527 remains separate as `MAINTAINER_SCOPE_JUDGMENT_REQUIRED`.
- Total unresolved Batch C actions: `30` (29 external-evidence actions plus T527).

The structured evidence ledger is `data/raw/corpus_quality_batch_c_wave2_2026_10_06/evidence_manifest.json`. No raw paper, failed response, search-result page, mirror, snippet, or secondary source is stored. The public export legitimately contains one relationship for the explicit member affiliation and one for the explicit parent affiliation.

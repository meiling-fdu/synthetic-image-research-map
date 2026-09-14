# Repository-wide curation audit — unresolved-inventory pass (2026-08-30)

## Scope and outcome

This pass reviewed only the unresolved inventory from the earlier repository-wide audit: one zero-author-mapping paper, 11 partial-author-mapping papers, five material institution-identity findings, and 29 pending paper–institution location relationships. Author and institution conclusions were accepted only when supported by an original paper, publisher-deposited metadata, or an authoritative institutional source. No affiliation was guessed from a current employer, and no institution identity was merged without evidence.

The later institution-location reconciliation followed a different constraint: the user's manual location decisions in the current working tree are authoritative. They were preserved and structurally validated, not independently re-researched. The only location edits made during reconciliation were structural: removal of one stale duplicate candidate row, consolidation of one duplicate review relationship after a paper-ID transition, and matching review records across canonical paper identities so regeneration does not recreate duplicates.

| Scoped inventory | Initial audit | Final effective state |
| --- | ---: | ---: |
| Zero-author-mapping papers | 1 | 0 |
| Partial-author-mapping papers | 11 | 2 |
| Original targeted missing authors | 16 | 1 unresolved |
| Material institution-identity findings | 5 | 0 high / 0 medium |
| Pending institution-location relationships | 29 | 0 |
| Public bibliography records | 574 | 574 |
| Public map relationships | 1,276 | 1,304 |

The generated author-coverage report now has 572 complete papers, two partial papers, and zero zero-mapping papers. Fifteen of the 16 originally targeted missing authors were resolved; Daniel S. Yeung remains unresolved on the Evasion paper. The other partial is the GHRIET paper: its targeted author, Usha Kosarkar, is resolved, while Gopal Sarkarkar and Shilpa Gedam newly became visible as unresolved when unsupported automatic relationships were removed. The accessible original paper excerpt does not provide their publication affiliations.

## Author–institution review

### Zero-mapping priority

- *Exploiting the Source-Asymmetry Confidence Gap for Generalizable AI-Generated Image Detection*: the CVF paper assigns all six authors to the School of Computer Science and Engineering, Sun Yat-sen University. The relationship is active.

### Original partial-mapping inventory

- *CoDA*: Zexi Jia, Zhiqiang Yuan, Xiaoyue Duan, Jinchao Zhang, and Jie Zhou are assigned to Tencent WeChat AI, Beijing, from the original paper. No office coordinate was inferred.
- *A Hybrid CLIP-Diffusion Architecture*: Andreas Specker, Manjunatha Veerappa, Thomas Golda, and Nadia Burkart are assigned to Fraunhofer IOSB and Fraunhofer Center for Machine Learning as printed in the CVF paper.
- *ReAlign*: the author-affiliation block assigns Qing Huang, Zhipei Xu, Xuanyu Zhang, and Jian Zhang to the School of Electronic and Computer Engineering, Peking University. Because affiliation 1 contains no Shenzhen evidence, it remains canonical Peking University and uses the established PKU location. Qing Huang additionally has affiliation 2 at South China University of Technology, Xiangyu Yu has affiliation 3 there, and only Jian Zhang has affiliation 4 at the Guangdong Provincial Key Laboratory in Peking University Shenzhen Graduate School.
- *Evolution of Detection Performance Throughout the Online Lifespan of Synthetic Images*: the source spelling is Dimitrios Karageogiou; the mapping typo and author position were corrected.
- *Fake Detection Based on Balanced Attention and Information Guidance for Collaborative Image Processing Tasks*: Jia Wang and Qian Luo are assigned to Xinjiang University, and Jeon Gwanggil to Incheon National University, from publisher-deposited metadata.
- *PPM-CLIP*: Zhihui Liu is assigned to Truesight Technology, Xiamen. No company coordinate was inferred.
- *A Novel Framework for Deepfake Image Detection Using Deep Learning Approach*: the publisher deposit resolves all six author affiliations, including Aruna J. Chamatkar at Kamala Nehru College and the exact string “Saraswati College, Shegaon” for Akash Prakash Kharat.
- *Deepfake Image Detection Using ResNet50 Model*: publisher metadata and the official proceedings contents resolve all six authors. The first-author spelling was corrected from the OpenAlex form “Lee Kar Yee” to the proceedings form “Lew Kar Yee”; Chuah ChaiWen remains at Guangdong University of Science and Technology, distinct from Guangdong University of Technology.
- *Revealing and Classification of Deepfakes Video's Images using a Customize Convolution Neural Network Model*: the author-uploaded excerpt assigns Usha Kosarkar to the Department of Science and Technology, GHRIET, Nagpur. Official Raisoni pages establish the exact institution identity. Gopal Sarkarkar and Shilpa Gedam remain unmapped because the accessible original evidence does not supply their affiliation links.
- *Detection of Deepfake Images Created Using Generative Adversarial Networks: A Review*: the source roster and mapping were corrected from “Kamma Vidya” to “K. R. Vidya.”
- *Evasion on General GAN-Generated Image Detection by Disentangled Representation*: Daniel S. Yeung remains unresolved. The paper gives only “Hong Kong, China” for affiliation marker e; it names no institution and does not state that the author is independent.

The three unresolved authors have durable audit records. Missing text was not treated as evidence of an independent/non-institutional affiliation.

## Institution identities

All five previously material findings are resolved. The final institution-consistency audit reports 0 high, 0 medium, and 207 low findings. The low findings are non-blocking name/alias diagnostics, not accepted identity changes.

- The two CQUPT relationships preserve the full affiliation “School of Artificial Intelligence, Chongqing University of Posts and Telecommunications,” supported by the official CQUPT faculty site. The generic alias “School of Artificial Intelligence” was rejected because it caused false matches.
- “University of Information Technology, VNU-HCM” is confirmed as University of Information Technology, Viet Nam National University Ho Chi Minh City.
- “GHRIET” is confirmed as G H Raisoni Institute of Engineering & Technology Nagpur, not the broader Raisoni group or another campus.
- ReAlign preserves generic Peking University for affiliation 1 and Peking University Shenzhen Graduate School only for affiliation 4; the two identities and locations must not coalesce.

### ReAlign canonicalization root cause and same-class audit

The incorrect ReAlign output was caused by a confirmed alias row that mapped the exact raw string `School of Electronic and Computer Engineering, Peking University` to `Peking University Shenzhen Graduate School`. The resolver performs exact normalized canonical-name/abbreviation/alias matching; explanatory alias notes do not constrain resolution. No canonical-parent fallback was responsible, and the exporter does not override an explicit active mapping ID with alias or coordinate evidence.

The repository-wide same-class audit found one affected relationship before correction: ReAlign affiliation 1 (`mapping:495827ef2ecac5603830`). The two other mappings to Peking University Shenzhen Graduate School explicitly contain Shenzhen evidence and remain valid. A separate GenShield mapping with the same generic School of Electronic and Computer Engineering raw affiliation was already canonicalized correctly to generic Peking University.

The alias now resolves to generic Peking University. ReAlign affiliation 1 uses Peking University's confirmed Beijing location; affiliation 4 remains a separate PKU Shenzhen relationship at the confirmed Shenzhen location. A regression asserts that a generic Peking University affiliation can never resolve to PKU Shenzhen and that no current PKU-Shenzhen mapping lacks Shenzhen evidence in its raw affiliation.

## Institution-location reconciliation

The first evidence pass resolved five of the original 29 pending relationships from publication-site evidence: Fraunhofer IOSB Karlsruhe, Pusan National University Busan, Charles Sturt University Bathurst, University of Information Technology VNU-HCM, and the University of Dayton main campus. That left 24 relationships pending in the interrupted working tree.

The user then manually decided those remaining relationships and related newly exposed cases. This continuation preserved those decisions without conducting new location research. Effective location-review state is now:

| Effective status | Count |
| --- | ---: |
| Confirmed | 471 |
| Alias of confirmed | 69 |
| Excluded | 6 |
| Ignore | 32 |
| Pending review | 0 |
| Confirmed location records | 495 |

The append-only source CSV still contains 603 historical rows, including one row whose literal stored status is `pending_review` for TU Wien. It is not a current pending relationship: its paper has an active exclusion, so the effective queue classifies it as excluded. The effective payload contains 578 current review relationships and zero pending relationships.

Structural reconciliation preserved manual coordinates and fixed only:

1. a duplicate `location_id` where a stale `needs_coordinate_review` row coexisted with the later manual known-coordinate row;
2. duplicate ResNet50 review rows caused by OpenAlex versus curated paper IDs, retaining the manual confirmed decision; and
3. review matching so DOI, OpenAlex ID, curated ID, and title/year identities remain connected after canonical-ID changes.

No automatic process overwrote a manual location decision, and the final export created or updated zero review rows.

## Why 579 audited effective records but 574 public records

The venue audit operates on the effective merged curation dataset, not only the public bibliography. Its 579 records are exactly:

- 574 records emitted to the public bibliography; plus
- five curated records retained for provenance, exclusion, and venue-audit history but blocked from public export by active exclusions.

The five non-public effective records are:

1. *Black-Box Adaptation for Deepfake Detection via Local Relation Guided AUC Optimization* — `deepfake_only_not_core`.
2. *Deepfake Image Detection Using Convolutional Neural Network* — `out_of_scope`.
3. *Robust Deepfake Detection: Mitigating Spatial Attention Drift via Calibrated Complementary Ensembles* — `deepfake_only_not_core`.
4. *Towards Explaining Classification Models in Security with Sparse Autoencoders* — `out_of_scope`.
5. *Wavelet-Packet Powered Deepfake Image Detection* — `deepfake_only_not_core`.

Therefore, `579 = 574 public + 5 actively excluded but retained effective records`. The difference is not duplicate inflation and does not represent five missing bibliography entries.

## Public relationship-count reconciliation

- Earlier repository-wide audit checkpoint: 1,276 relationships.
- Interrupted/provisional checkpoint: 1,274 relationships.
- Incorrectly coalesced ReAlign checkpoint: 1,303 relationships.
- Final evidence-consistent export: 1,304 relationships.

The final state is a net increase of 28 over the original 1,276 checkpoint and 30 over the provisional 1,274 checkpoint. Those net changes combine newly map-eligible manual confirmations, author-mapping completions, canonical identity reconciliation, and removal/replacement of stale relationships; they are not all additive markers.

The 1,303 checkpoint incorrectly coalesced ReAlign's generic PKU and PKU Shenzhen affiliations. The source-level correction restores separate canonical relationships and locations for affiliation 1 and affiliation 4, adding the missing generic PKU relationship without duplicating the Shenzhen relationship.

Final public counts:

- 574 bibliography records;
- 569 unique paper identities in map-source relationships;
- 568 bibliography papers with map locations;
- 1,304 map relationships;
- 957 active curated coordinate-bearing markers and 8 source-backed preliminary markers;
- 0 scoped relationships missing usable coordinates.

## Evidence sources

Primary paper evidence included the original CVF PDFs for Source-Asymmetry, Hybrid CLIP-Diffusion, ReAlign, and PPM-CLIP; the original arXiv paper for CoDA; the Zenodo paper for Evolution; the original Evasion paper; publisher-deposited IEEE/Crossref metadata for the CSCWD, LT, and CyberComp papers; the official CyberComp proceedings contents; the author-uploaded GHRIET paper excerpt; and the Springer publication record for K. R. Vidya.

Authoritative institutional evidence included Sun Yat-sen University School of Computer Science and Engineering, Fraunhofer IOSB, Peking University School of Electronic and Computer Engineering, Chongqing University of Posts and Telecommunications, University of Information Technology VNU-HCM, and G H Raisoni institutional pages.

## Final state and verification

- Curated papers: 373. The added curated ResNet50 row represents an already-public paper and corrects publisher-supported metadata; it does not increase the effective or public bibliography count.
- Author-institution mappings: 1,026 total — 968 active, 30 needs review, 28 excluded.
- Institution registry: 679 institutions, 85 aliases, and 495 confirmed location records.
- Author coverage: 574 papers — 572 complete, 2 partial, 0 zero; the only unresolved authors are Daniel S. Yeung, Gopal Sarkarkar, and Shilpa Gedam.
- Curated database validation: 0 errors; 0 duplicate candidates.
- Public preview validation: 0 errors, 0 map warnings, and exactly three bibliography warnings for those unresolved authors.
- Public institution consistency: 574 papers checked, 0 mismatches.
- Institution consistency: 0 high, 0 medium, 207 low.
- Effective location review: 0 pending and 0 coordinate gaps.
- Focused regression suite: 140 passed.
- Prior full suite before the final ReAlign identity split: 1,230 passed, 49 skipped.
- Post-fix source/resolver/public regression suite: 106 passed, 1 unrelated localhost endpoint test deselected.
- Broader sandbox run: 1,190 passed, 49 skipped, 1 deselected; 41 localhost HTTP-server tests were blocked by sandbox port-binding restrictions, with no ReAlign/data regression failures.
- Deterministic export hashes were identical across two consecutive controlled exports:
  - `public_preview_papers.json`: `f5248fb643704c0d79d6889993e1d5b6481c92003cd8e71545ca055c2514a2e8`
  - `public_preview_map_data.json`: `b7d2af3f673c88545a21dbb7de156e2b10c8b258800346660647dc6c4f9e9bb5`
- Nothing was staged, committed, or pushed.

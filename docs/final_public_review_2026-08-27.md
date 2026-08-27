# Scoped public location and author review

Baseline: clean `main` at `c926c18`, up to date with `origin/main`.
Nothing staged or committed. Only the five public-relevant location cases and
ten author warnings were adjudicated. No institution merge, new institution,
new author mapping, geocoded marker, or dormant-coordinate repair was performed.

## Locations

All five remain **Pending Review / Needs Coordinates**. The investigation did
not establish an exact point meeting the requested institution/site standard.
Known textual geography and raw publication affiliations are retained. The full
identity, aliases, author, year, previous evidence, and final decision are in
`final_public_review_cases_2026-08-27.json`.

| Institution / affected author | Evidence checked | Remaining reason |
| --- | --- | --- |
| JD.com / Jawadul H. Bappy | Visually inspected [publisher PDF](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/ei/31/5/art00008); CVF paper entry | Paper confirms JD.com but supplies no author office/site. Headquarters cannot substitute for paper-specific evidence. City, country and coordinates remain blank. |
| Naval Air Warfare Center Weapons Division / Arjuna Flenner | Same publisher PDF; [NAVAIR organization](https://www.navair.navy.mil/organization/NAWCWD); [official Building 1 notice](https://www.navair.navy.mil/node/5061); cached named-feature queries | China Lake, California, US is explicit; 1 Administration Circle/Building 1 is supported. An exact building/address point was not verified. Point Mugu, base centroids and nearby fire-station points were rejected. |
| Huya Inc. / Xiao Meng | Visually inspected [publisher PDF hosted by the author lab](https://tas-lab.org/publication/2024-evasion-on-general-gan-generated-image-detection-by-disentangled-representation/index.pdf); existing annual-report address evidence | Affiliation d says Guangzhou 510006; headquarters uses 511446. No primary source tied the 510006 affiliation to an exact building. Guangzhou/Guangdong/China retained; no centroid. |
| Department of Technical Education, Uttar Pradesh / Digvijay Pandey | [Springer author entry](https://link.springer.com/article/10.1007/s11468-024-02492-1); UP government tender for Directorate at Vikas Nagar; official department site attempt; cached named-feature query | Kanpur directorate identity is supported. The departmental site timed out, and no exact directorate building point was verified. No city center or third-party plus-code substitution. |
| Beijing IrisKing Co., Ltd. / Jing Liu | [Publisher-supplied DOAJ entry](https://doaj.org/article/119351797e28470998c905b4426d63e1); [2024 issuer disclosure](https://epaper.cs.com.cn/zgzqb/images/2024-04/29/B132/zqB13229.pdf); [2022 disclosure](https://epaper.stcn.com/paper/zqsb/html/epaper/index/content_1787832.htm); company site attempt | 2024 registered address: No. 9 North Fourth Ring West Road, floor 22, room 2210. 2022 address: Chengfu Road 45, Building F, room 401. Neither an exact building point nor a publication-time operational-office link was verified. Company site failed TLS verification. Historical/current offices were not mixed. |

| Location metric | Initial | Final |
| --- | ---: | ---: |
| Pending Review | 5 | 5 |
| Needs Coordinates | 5 | 5 |
| Ambiguous | 0 | 0 |
| COMPLETE relationships | 1,261 | 1,261 |
| ACTIONABLE relationships | 5 | 5 |
| EXCLUDED relationships | 29 | 29 |
| ERROR relationships | 0 | 0 |

All five reasons are persisted in the authoritative review queue. No location
was resolved, so there is no new marker or automatic-marker replacement to QA.

## Author adjudication

No author was newly MAPPED in this pass. Three were explicitly reviewed as
non-institutional; seven remain unresolved. All ten remain in their existing
paper author positions with unchanged affiliation indices.

| Author | Final status | Source wording or remaining reason |
| --- | --- | --- |
| Hainan Ren | EXPLICITLY NON-INSTITUTIONAL | [arXiv 2402.00045v7](https://arxiv.org/pdf/2402.00045v7), rendered footnote: `Hainan Ren. e-mail:(hnren666@gmail.com)`. Separate contact-only entry, no institution. This does not assert anything about current employment. |
| Jia Wang | UNRESOLVED | [Official CSCWD programme](https://fyust.edu.cn/gjhyqk/cscwd2026/program.pdf) names Jia Wang; existing pending mapping names Yi-Xiang Wang. IEEE full-text affiliation evidence was unavailable. No identity merge. |
| Yuexuan Tan | UNRESOLVED | Record represents CVPR 2026 and links its [accepted PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Qin_IncreFA_Breaking_the_Static_Wall_of_Generative_Model_Attribution_CVPR_2026_paper.pdf), which has five authors and omits Tan. [arXiv v2](https://arxiv.org/pdf/2604.17736v2) has six, including Tan at BUPT. No authoritative correction reconciles the rosters. Existing roster preserved, no combined affiliation matrix. |
| Jason Li | UNRESOLVED | Rendered [arXiv v1](https://arxiv.org/pdf/2605.01638v1) gives NTU superscript 4; [official project author list and BibTeX](https://tianxiao1201.github.io/omni-fake-project-page/) omit Jason and NTU, while the curated mapping names Xiangtai Li. Conflict remains. |
| Henan Wang | EXPLICITLY NON-INSTITUTIONAL | [Official AAAI entry](https://ojs.aaai.org/index.php/AAAI/article/view/38146): `Independent Researcher`. |
| Aruna J. Chamatkar | UNRESOLVED | [IEEE document](https://ieeexplore.ieee.org/document/10940759) inaccessible; the institutional publication listing did not establish Chamatkar's publication-specific affiliation. Current employment was not used. |
| Chuah ChaiWen | UNRESOLVED | [IEEE document](https://ieeexplore.ieee.org/document/10913843) presented a verification page. Proceedings contents establish authorship, not institution/campus. Secondary Guangdong University of Science and Technology evidence remains unconfirmed by a primary author block. |
| Daniel S. Yeung | UNRESOLVED | Rendered publisher PDF gives affiliation e as `Hong Kong, China`. Geography alone supplies neither organization identity nor an explicit independent role. |
| Reid Southen | EXPLICITLY NON-INSTITUTIONAL | Rendered [manuscript](https://www.mat.ucsb.edu/~g.legrady/academic/courses/24f255/organicOrDiffused.pdf): superscript 1 is `Concept Artist`, separate from the other authors' University of Chicago affiliation. |
| Usha Kosarkar | UNRESOLVED | [ScienceDirect article](https://www.sciencedirect.com/science/article/pii/S1877050923002375) remained blocked (403). Full affiliation layout and exact GHRIET campus unverified. |

The existing append-only institution audit log stores the ten new author-level
review events. Prior unresolved events remain as history. The shared reader
requires exact paper/author identity and source-backed non-institutional
decisions; it does not infer status from missing metadata. A reviewed author
cannot simultaneously have an active contradictory institution mapping.

## Completeness and public output

Author counts are paper-author occurrences, not deduplicated people.

| Metric | Initial | Final |
| --- | ---: | ---: |
| Mapped authors | 2,720 | 2,720 |
| Explicitly non-institutional authors | 0 | 3 |
| Unresolved author warnings | 10 | 7 |
| Affiliation-complete papers / 546 | 536 | 539 |
| Papers with zero mapped authors | 0 | 0 |
| Public paper records | 546 | 546 |
| Raw-map unique paper identities | 540 | 540 |
| Public papers with locations | 539 | 539 |
| Map relationships | 1,261 | 1,261 |
| Unique mapped institutions (validator semantics) | 616 | 616 |
| Public papers flagged missing coordinates | 1 | 1 |
| Public location validation warnings | 0 | 0 |
| Public map validation errors / warnings | 0 / 0 | 0 / 0 |
| Public paper validation errors / warnings | 0 / 10 | 0 / 7 |
| Unexplained relationship shrinkage | 0 | 0 |

Five actionable location relationships and one paper-level `missing_coordinates`
flag are different existing metrics; neither is the map validator warning count.

## Regeneration and preservation

Used the canonical `export_public_preview.py --preserve-existing` workflow;
no public JSON was hand-edited. Refreshed the location, missing-coordinate,
relationship-completeness, author-affiliation and consistency reports. New CSV
reports are under `data/processed/`; the final `data/manual/` contents are unchanged.
No migration or prior institution cleanup was replayed.

Machine verification is in `final_public_review_integrity_2026-08-27.json`:

- All existing public relationships, coordinates, author ordering and indices preserved.
- All curated tables except the five review reasons and appended audit events unchanged.
- Historical audit rows retained byte-for-byte.
- Active references to merged/ignored institutions, duplicate active mappings,
  malformed coordinates/CSV rows, and canonical `Türkiye` values: all zero.
- No Low-backlog decisions or dormant-coordinate curation.
- No downloaded PDF, debug file or credential added to the repository.

The large generated JSON diff adds the author state/count fields across papers
and markers. One pre-existing stale marker venue is also re-normalized by the
unchanged canonical exporter: *Addressing Diffusion Model Based Counter-Forensic
Image Manipulation for Synthetic Image Detection*. Its unregistered legacy
venue ID is removed and its source proceedings title retained. No venue registry
or paper metadata was edited in this pass. The regenerated consistency report
also reorders/reverses equivalent duplicate-candidate display pairs; no decisions
were made on those findings.

## Verification and remaining QA

- Focused verification matrix: **211 passed / 0 skipped / 0 failed**.
- Dedicated author/location/display subset: **74 passed / 0 skipped / 0 failed**.
- Full repository suite: **1,146 passed / 0 skipped / 0 failed**.
- Curated validator: **0 errors, 178 existing warnings, 0 duplicate candidates**.
- Public validators: **0 errors**; map warnings **0**; paper warnings **7**.
- Relationship completeness: **ERROR = 0**.
- Institution consistency: **0 High / 0 Medium**; unrelated Low findings untouched.
- Paper exclusion validator, JavaScript syntax, Python compilation and
  `git diff --check`: passed.
- Static HTTP: index and canonical paper JSON returned HTTP 200 without the
  Admin backend.
- **Interactive browser QA is blocked.** The Browser tool refused
  `http://127.0.0.1:8893/` with `ERR_BLOCKED_BY_CLIENT` before rendering. No bypass
  was attempted. Marker/author/reason visibility and browser console cannot be
  claimed verified. No QA-only curation was saved.

Remaining public-relevant research work is exactly the five locations and seven
unresolved authors above. Interactive browser QA also remains to be completed
when local-site access is available.

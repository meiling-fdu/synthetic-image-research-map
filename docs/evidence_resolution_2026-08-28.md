# Final evidence-resolution pass — 2026-08-28

## Scope and baseline

Started from clean `main` at `69229b3` (up to date with origin/main). No migrations or prior repairs were replayed. This pass covers exactly eight actionable locations and five unresolved authors. Nothing staged or committed.

The [machine-readable audit](evidence_resolution_2026-08-28.json) preserves the complete pre-pass inventory: canonical IDs/names, abbreviations/aliases, affected mappings and authors, raw affiliations, existing locations/candidates, external IDs where present, sources, and final decisions. New raw map responses and coordinate derivation are in [the evidence cache](../data/raw/evidence_resolution_2026-08-28/README.md). PDFs were inspected outside the repository and are not committed.

| Metric | Initial | Final |
| --- | ---: | ---: |
| Pending Review | 8 | 7 |
| Needs Coordinates | 8 | 7 |
| Ambiguous | 0 | 0 |
| COMPLETE relationships | 1,263 | 1,264 |
| ACTIONABLE relationships | 8 | 7 |
| ERROR relationships | 0 | 0 |
| Explicitly excluded relationships | 29 | 29 |
| Confirmed locations | 456 | 457 |
| Public paper records | 546 | 546 |
| Map relationships | 1,263 | 1,264 |
| Mapped institution names | 617 | 618 |
| Unresolved author warnings | 5 | 5 |
| Affiliation-complete papers | 541 / 546 | 541 / 546 |
| High / Medium consistency findings | 0 / 0 | 0 / 0 |

## Locations

### 1. Naval Air Warfare Center Weapons Division — ACTIONABLE

- Institution: `institution:e07792f5cf49ebda`; mapping `mapping:0f51254f7cd4fb7fa8d1`.
- Paper: **Detecting GAN Generated Fake Images Using Co-Occurrence Matrices** (2019); author **Arjuna Flenner**.
- Formal affiliation: Naval Air Warfare Center Weapons Division, China Lake, California, USA.
- Retained geography: China Lake, California, United States. Address evidence: 1 Administration Circle, Building 1 (official command address; exact point unverified).
- Final canonical site: not assigned. Coordinates remain unconfirmed; no public marker.

Formal 2019 paper explicitly places Arjuna Flenner at China Lake, California. NAVAIR command contact and archived Building 1 notice support 1 Administration Circle; DoD check-in guidance gives Knox Road/Blandy Avenue. Exact-address Nominatim query returned no feature. Neither the retained airfield candidate nor a whole-base centroid is a verified building point. Point Mugu is not this paper site.

Evidence checked: [source 1](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/ei/31/5/art00008), [source 2](https://www.navair.navy.mil/nawcwd/Contact_NAWCWD), [source 3](https://www.navair.navy.mil/node/5061), [source 4](https://installations.militaryonesource.mil/military-installation/naval-air-weapons-station-china-lake/base-essentials/check-in-procedures).

### 2. Huya Inc. — ACTIONABLE

- Institution: `institution:2f2a5a5c1021efe4`; mapping `mapping:9121743520db34334d78`.
- Paper: **Evasion on General GAN-Generated Image Detection by Disentangled Representation** (2024); author **Xiao Meng**.
- Formal affiliation: Huya Inc, Guangzhou, 510006, China.
- Retained geography: Guangzhou, Guangdong, China. Address evidence: 510006 (paper); no verified street address.
- Final canonical site: not assigned. Coordinates remain unconfirmed; no public marker.

Formal 2024 PDF affiliation d names Huya Inc, Guangzhou, 510006, China. The company filing dated 2024-04-26 instead lists Building A3, E-Park, 280 Hanxi Road, 511446. No contemporaneous official 510006 office linkage was established. Preserve the paper postcode; do not substitute headquarters or the rejected residential-development candidate.

Evidence checked: [source 1](https://tas-lab.org/publication/2024-evasion-on-general-gan-generated-image-detection-by-disentangled-representation/index.pdf), [source 2](https://filecache.investorroom.com/mr5ir_huya/148/download/HUYA%20%28HUYA%20Inc.%20American%20depositary%20shares%20each%20representing%20one%20Class%20A%29%20%20%2820-F%29%202024-04-26.pdf), [source 3](https://blog.huya.com/policy/1387).

### 3. Department of Technical Education, Uttar Pradesh — ACTIONABLE

- Institution: `institution:96dd3389141fcf35`; mapping `mapping:44292523d51b513f7a9c`.
- Paper: **Enhancing Sensing and Imaging Capabilities Through Surface Plasmon Resonance for Deepfake Image Detection** (2025); author **Digvijay Pandey**.
- Formal affiliation: Department of Technical Education, Kanpur, Uttar Pradesh, India.
- Retained geography: Kanpur, Uttar Pradesh, India. Address evidence: Directorate of Technical Education, Vikas Nagar, Kanpur 208002.
- Final canonical site: not assigned. Coordinates remain unconfirmed; no public marker.

Springer author affiliation identifies Digvijay Pandey at Department of Technical Education, Kanpur, Uttar Pradesh. AICTE 2024 approval and government procurement evidence support the Vikas Nagar directorate. No named government-building point was verified; the retained private-park candidate is rejected. Official department page was inaccessible. Final-volume year remains 2025.

Evidence checked: [source 1](https://link.springer.com/article/10.1007/s11468-024-02492-1), [source 2](https://www.glikanpur.com/uploads/EOA-Report-2024-25.PDF), [source 3](https://etender.up.nic.in/nicgep/app?component=%24DirectLink&page=FrontEndViewTender&service=direct&sp=SeEYJKIfg5KjWhJIAhb1NYg%3D%3D).

### 4. Beijing IrisKing Co., Ltd. — ACTIONABLE

- Institution: `institution:1f939a5a9221dfb6`; mapping `mapping:c9139a042858068c242c`.
- Paper: **Enhancing Deepfake Detection with Diversified Self-Blending Images and Residuals** (2024); author **Jing Liu**.
- Formal affiliation: Beijing IrisKing Company Ltd., Beijing, China.
- Retained geography: Beijing, Beijing, China. Address evidence: Registered residence: No. 9 North Fourth Ring West Road, floor 22, room 2210 (2024 disclosure; paper office not established).
- Final canonical site: not assigned. Coordinates remain unconfirmed; no public marker.

Jing Liu affiliation names Beijing IrisKing Company Ltd., Beijing, China. The 2024-04-29 corporate disclosure lists North Fourth Ring West Road 9, floor 22 room 2210; older Chengfu Road 45 evidence differs. The disclosure does not establish when the author used this office. Retain Beijing geography; neither the garden candidate nor an inferred Yingu Tower office is confirmed for this publication.

Evidence checked: [source 1](https://doi.org/10.1109/ACCESS.2024.3382196), [source 2](https://doaj.org/article/119351797e28470998c905b4426d63e1), [source 3](https://epaper.cs.com.cn/zgzqb/images/2024-04/29/B132/zqB13229.pdf).

### 5. Griffith University — ACTIONABLE

- Institution: `institution:866f00322aa693b8`; mapping `mapping:7b3e580c7133d150e40d`.
- Paper: **Deep Learning for Deepfakes Creation and Detection: A Survey** (2022); author **Quoc Viet Hung Nguyen**.
- Formal affiliation: School of Information and Communication Technology, Griffith University, Queensland, Australia.
- Retained geography: Queensland, Australia. Address evidence: No publication-specific campus.
- Final canonical site: not assigned. Coordinates remain unconfirmed; no public marker.

Formal 2022 survey affiliation b gives School of Information and Communication Technology, Griffith University, Queensland, Australia, without a campus. Later formal papers (2023/2024) place this author at Gold Coast, but do not establish this survey site. No principal-campus default is authorized for an ambiguous paper site; Nathan, Gold Coast and South Bank are not assigned.

Evidence checked: [source 1](https://research-repository.griffith.edu.au/server/api/core/bitstreams/9047c38e-4092-41fe-a8e7-e73d74b6d891/content), [source 2](https://onlinelibrary.wiley.com/doi/10.1155/2023/5494961), [source 3](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/cit2.12362).

### 6. Kumoh National Institute of Technology — CONFIRMED

- Institution: `institution:845768c6b2d48f68`; mapping `mapping:27618b8da3c3e6c1b003`.
- Paper: **Deep Learning for Deepfakes Creation and Detection: A Survey** (2022); author **Thien Huynh-The**.
- Formal affiliation: ICT Convergence Research Center, Kumoh National Institute of Technology, Gyeongbuk, Republic of Korea.
- Retained geography: Gumi, Gyeongsangbuk-do, South Korea. Address evidence: Room 408, Industry-Academic Cooperation Building, 61 Daehak-ro, Gumi 39177.
- Final canonical location: `location:940d31d28b1c4cb7c094`; coordinates **36.148713, 128.3932287**.

Formal 2022 survey affiliation c identifies Thien Huynh-The at ICT Convergence Research Center, Kumoh National Institute of Technology. The center's 2018 and 2020 brochures name the researcher and give Room 408, Industry-Academic Cooperation Building, 61 Daehak-ro. Official KIT pages confirm the Yangho campus address. Named OSM university building 산학협력관 (way 1518535866) matches that building within campus way 234847049. The point is derived inside its footprint, not a city/postcode/campus centroid or Shinpyeong site. Institution identity and original author group remain unchanged.

Evidence checked: [source 1](https://research-repository.griffith.edu.au/server/api/core/bitstreams/9047c38e-4092-41fe-a8e7-e73d74b6d891/content), [source 2](https://ictcrc.org/images/sub/2018_catal.pdf), [source 3](https://ictcrc.org/images/sub/2020_catal.pdf), [source 4](https://www.kumoh.ac.kr/eng/sub01_04.do), [source 5](https://www.kumoh.ac.kr/eng/sub06_04_02.do), [source 6](https://www.openstreetmap.org/way/1518535866).

### 7. Ho Chi Minh City University of Technology (HUTECH) — ACTIONABLE

- Institution: `institution:6ed8b18e4c077bfc`; mapping `mapping:3ccd22bfe50f3c185660`.
- Paper: **Deep Learning for Deepfakes Creation and Detection: A Survey** (2022); author **Thanh Tam Nguyen**.
- Formal affiliation: Faculty of Information Technology, Ho Chi Minh City University of Technology (HUTECH), Ho Chi Minh City, Vietnam.
- Retained geography: Ho Chi Minh City, Ho Chi Minh City, Vietnam. Address evidence: Faculty web footer: 475A Dien Bien Phu (not established as author's 2022 site).
- Final canonical site: not assigned. Coordinates remain unconfirmed; no public marker.

Formal survey affiliation e explicitly identifies Faculty of Information Technology, Ho Chi Minh City University of Technology (HUTECH). Official English faculty news dated 2022-03-27 confirms that exact canonical English identity. Its current footer gives 475A Dien Bien Phu, but does not identify Thanh Tam Nguyen's publication-time campus. Do not confuse HUTECH with VNU-HCM University of Technology or University of Technology and Education; no alias or campus invented.

Evidence checked: [source 1](https://research-repository.griffith.edu.au/server/api/core/bitstreams/9047c38e-4092-41fe-a8e7-e73d74b6d891/content), [source 2](https://www.hutech.edu.vn/khoacntten/news/14618716-hutech-it-open-day-career-orientation-internship-implementation).

### 8. Pusan National University — ACTIONABLE

- Institution: `institution:70691539bab41121`; mapping `mapping:ff5a05296dbb2552e5cb`.
- Paper: **Deep Learning for Deepfakes Creation and Detection: A Survey** (2022); author **Quoc-Viet Pham**.
- Formal affiliation: Korean Southeast Center for the 4th Industrial Revolution Leader Education, Pusan National University, Busan, Republic of Korea.
- Retained geography: Busan, Busan, South Korea. Address evidence: Center web footer: 2 Busandaehak-ro 63beon-gil, Jangjeon-dong, Busan 46241; exact unit site not verified.
- Final canonical site: not assigned. Coordinates remain unconfirmed; no public marker.

Formal survey affiliation f identifies Quoc-Viet Pham at Korean Southeast Center for the 4th Industrial Revolution Leader Education, Pusan National University, Busan. Official center greeting confirms identity and Department of Information Convergence Engineering; footer gives Busan 46241/Jangjeon campus address. The center Map page supplied no usable location content and no publication-time unit/building point was verified. Preserve Busan; do not infer a hospital, Yangsan site or principal-campus marker from a generic footer.

Evidence checked: [source 1](https://research-repository.griffith.edu.au/server/api/core/bitstreams/9047c38e-4092-41fe-a8e7-e73d74b6d891/content), [source 2](https://bk4-iceeng.pusan.ac.kr/bk4-iceeng/57351/subview.do), [source 3](https://bk4-iceeng.pusan.ac.kr/bk4-iceeng/57354/subview.do), [source 4](https://quantum-ai.pusan.ac.kr/pnuProfl/wireless-ai/2135/27021/artclView.do).

Only Kumoh changed geographic output: the 2022 survey names its ICT Convergence Research Center; historical official brochures name the researcher and Room 408 in the Industry-Academic Cooperation Building. The representative point is computed inside the matching named OSM building footprint. It is not an official surveyed room coordinate, and no floor-specific accuracy is claimed. Existing candidate coordinates for NAWCWD, Huya, the Uttar Pradesh department and IrisKing are preserved as rejected/unverified evidence and remain excluded. Griffith, HUTECH and Pusan receive no inferred campus. Textual geography and address evidence remain in the review records, raw affiliation and this audit.

## Authors

### 1. Jia Wang — UNRESOLVED

Paper: **Fake Detection Based on Balanced Attention and Information Guidance for Collaborative Image Processing Tasks**; DOI `10.1109/cscwd68734.2026.11582378`.

Publisher author listing retains Jia Wang; the complete formal affiliation block is unavailable. Do not merge with Yi-Xiang Wang.

Publisher author listing retains Jia Wang, Qian Luo, Jeon Gwanggil. The official CSCWD 2026 programme lists Jia Wang, Qian Luo, Gwanggil Jeon, but supplies no author affiliation markers. IEEE document 11582378 was unavailable. Jia Wang is not merged with Yi-Xiang Wang. Full formal affiliation block and the third author's published spelling remain unverified.

Sources checked: [source 1](https://ieeexplore-custom.ieee.org/author/609900097147935?reload=true), [source 2](https://ieeexplore.ieee.org/document/11582378), [source 3](https://fyust.edu.cn/gjhyqk/cscwd2026/program.pdf).

### 2. Aruna J. Chamatkar — UNRESOLVED

Paper: **A Novel Framework for Deepfake Image Detection Using Deep Learning Approach**; DOI `10.1109/lt64002.2025.10940759`.

Canonical identity retained; the formal publication affiliation is unverified.

IEEE document 10940759 and a publication-specific institutional manuscript could not be retrieved. Current employer/profile suggestions do not prove this paper affiliation. Keep Aruna J. Chamatkar unresolved; six-author roster, spelling, order and numeric mappings retained without claiming a formal-PDF verification.

Sources checked: [source 1](https://ieeexplore.ieee.org/document/10940759).

### 3. Chuah ChaiWen — UNRESOLVED

Paper: **Deepfake Image Detection Using ResNet50 Model**; DOI `10.1109/cybercomp60759.2024.10913843`.

Canonical identity retained; formal university/campus and full author block remain unverified.

IEEE document 10913843 returned a JavaScript verification challenge; no formal affiliation block retrieved. Proceedings TOC and UTHM publication listing spell first author Lew Kar Yee, versus canonical Lee Kar Yee; retain this discrepancy pending the formal publisher source. Secondary Guangdong University of Science and Technology suggestion is not sufficient to assign Chuah or a campus. No identity merge or index shift.

Sources checked: [source 1](https://ieeexplore.ieee.org/document/10913843), [source 2](https://www.proceedings.com/content/079/079233webtoc.pdf), [source 3](https://community.uthm.edu.my/rahmi?print=1).

### 4. Daniel S. Yeung — UNRESOLVED

Paper: **Evasion on General GAN-Generated Image Detection by Disentangled Representation**; DOI `10.1016/j.ins.2024.121267`.

Sixth formal author, marker e; affiliation is “Hong Kong, China” only.

Final 2024 publisher-layout PDF has six authors in canonical order. Daniel S. Yeung is sixth, marker e: Hong Kong, China. Entire text, first-page correspondence, CRediT contribution statement and ending pages checked; no organization or author biography providing one found. Geography is not an institution and does not explicitly establish independent status. Remains unresolved.

Sources checked: [source 1](https://tas-lab.org/publication/2024-evasion-on-general-gan-generated-image-detection-by-disentangled-representation/index.pdf).

### 5. Usha Kosarkar — UNRESOLVED

Paper: **Revealing and Classification of Deepfakes Video's Images using a Customize Convolution Neural Network Model**; DOI `10.1016/j.procs.2023.01.237`.

Canonical identity retained; full formal affiliation block unavailable. The secondary GHRIET/Nagpur excerpt is not sufficient to identify an institution/campus.

ScienceDirect formal paper was inaccessible (403). An author-uploaded ResearchGate excerpt says Department of Science and Technology, GHRIET, Nagpur, India, but the full formal author/affiliation block was not retrievable. Science College Nagpur's institutional research list points to the same DOI without supplying Usha's affiliation block. Exact GHRIET institutional entity/campus remains unverified; do not infer it from an employer profile.

Sources checked: [source 1](https://www.sciencedirect.com/science/article/pii/S1877050923002375), [source 2](https://sscnagpur.ac.in/uploaded_files/3.3.1.1Papers_the_first_page_with_author_and_affiliation_details.pdf), [source 3](https://www.researchgate.net/publication/367596688_Revealing_and_Classification_of_Deepfakes_Video%27s_Images_using_a_Customize_Convolution_Neural_Network_Model).

No author was newly mapped or classified as non-institutional. Every unresolved decision remains in the generated warning report and has an appended durable review note.

## Formal-version consistency

No roster, order, spelling, author identity or affiliation index was changed in this pass. The full formal Evasion PDF verifies its six-author order and Daniel’s geography-only marker. Full formal affiliation blocks for the other four author cases could not be retrieved, so they are **not claimed as fully verified**. Jia’s paper has Jeon Gwanggil / Gwanggil Jeon spelling-order evidence to reconcile; the ResNet50 paper has canonical Lee Kar Yee versus Lew Kar Yee in proceedings/institutional listings. Both discrepancies are explicitly recorded pending the formal publisher block.

Protected decisions remain intact: IncreFA’s five-author CVF roster; Omni-Fake’s Xiangtai Li → NTU; the nine-author 2022 survey; Co-Occurrence spelling corrections; Plasmonics final-volume year 2025; the previous affiliation repairs; Hainan Ren, Henan Wang and Reid Southen’s non-institutional semantics; Deakin’s two survey campus relationships; CUHK provenance; exporter status gating and frontend location deduplication. Curated papers, institution identities, aliases, hierarchy and exclusions are byte-unchanged from the starting inventory.

## Author completeness

- Mapped author occurrences: **2,725**.
- Explicitly non-institutional occurrences: **3** (Hainan Ren, Henan Wang, Reid Southen).
- Unresolved occurrences/warnings: **5**.
- Affiliation-complete papers: **541 / 546**.
- Papers with zero mapped/reviewed authors: **0**.

All exported affiliation superscripts are valid. All **67** active mapping rows with explicit numeric author positions match their canonical author names; no numeric index changed. The repository also retains **743 blank** and **104 positional-label** (`first`/`middle`/`last`) legacy `author_order` fields under existing identity-based mapping semantics. These were not migrated and are not represented as numeric-index verification. Affiliation-order continuity and duplicate-active-mapping checks pass.

## Public output

| Metric | Final |
| --- | ---: |
| Public paper records | 546 |
| Unique paper identities in raw map export | 540 |
| Public paper records with locations | 539 |
| Public paper records without locations | 7 |
| Map relationships | 1,264 |
| Mapped institution names | 618 |
| Actionable location relationships | 7 |
| Map validation errors / warnings | 0 / 0 |
| Generated-paper validation errors / warnings | 0 / 5 |
| Author warnings | 5 |
| Generated papers flagged missing coordinates | 1 |
| Unexplained shrinkage | 0 |

Raw map-source identities and public-paper records use different canonical identity matching; their 540 versus 539 counts are unchanged. The frontend also applies existing canonical deduplication, so its total need not equal the raw exporter total. No record or existing relationship was removed.

Two consecutive final canonical exports (`python3 scripts/export_public_preview.py --preserve-existing`) produced byte-identical JSON, including metadata. SHA-256:

- `public_preview_papers.json`: `3f1d9d0fa493786d27fa1bdc9102c8bb887e4de942b8d368217a6c3d42406bc5`.
- `public_preview_map_data.json`: `2f1b351db3150813f7c9d855531db14234879986e6347653c2c162a358c9337a`.

## Verification

| Check | Result |
| --- | --- |
| Focused location, formal-author, author-index, affiliation-order, non-institutional, completeness, review, baseline and export tests | **218 passed / 0 skipped / 0 failed** |
| Full repository suite, after exact baseline updates | **1,184 passed / 0 skipped / 0 failed** |
| Final baseline/evidence recheck | **66 passed / 0 skipped / 0 failed** |
| Curated validator | 16 files; **0 errors / 178 existing warnings** |
| Public map validator | **0 errors / 0 warnings** |
| Generated-paper validator | **0 errors / 5 expected unresolved-author warnings** |
| Relationship completeness | **1,264 COMPLETE / 7 ACTIONABLE / 29 EXCLUDED / 0 ERROR** |
| Missing-coordinate invariant violations | **0** |
| Malformed map coordinates | **0** |
| Active references to merged/ignored institutions | **0** |
| Duplicate logical locations | **0** |
| Canonical Türkiye country values | **0** |
| Affiliation-order violations | **0** |
| Retained candidate locations suppressed publicly | **4 / 4** |
| JavaScript syntax | **10 files passed** |
| Python compilation | **221 files passed** |
| git diff --check | **passed** |

The focused run used 12 existing test files; 13 case regressions were added to existing location and author test modules. The initial run exposed duplicate queue rows caused by experimental geography-field edits and a sandbox loopback restriction. The seven unconfirmed mappings were restored to their own pre-pass field values, only those newly generated rows were removed, and the final focused/full runs passed with unchanged production code. No prior migration or queue normalization was replayed.

The consistency report was regenerated: **0 High / 0 Medium / 173 Low**. Its generator may reverse/reorder equivalent duplicate-candidate pairs; these are reporting-only differences, not processed cases or identity decisions. Dormant and non-public coordinate tiers are unchanged.

### Browser QA

Used the in-app browser with separate localhost static and Admin servers after final export. No data was saved through the browser.

- All eight Admin decisions were opened; all seven unresolved rows remained visible with the new source/reason in expanded Details. Kumoh displayed the confirmed Gumi coordinates.
- Public institution-record views showed Co-Occurrence: 3 records without NAWCWD; Evasion: 1 without Huya; Plasmonics: 2 without the Uttar Pradesh department; Diversified Self-Blending: 1 without IrisKing; survey: 4 records, preserving two Deakin campuses, UPHF, and Kumoh, with no Griffith/HUTECH/Pusan markers.
- Kumoh’s marker is assigned only to Thien Huynh-The. The expanded survey unique-paper card displays all nine authors and correct institution superscripts (the public display groups the two Deakin affiliations while preserving distinct map locations).
- All five unresolved names remain visible in Admin coverage. Daniel appears sixth in Evasion without a speculative institutional superscript.
- IncreFA shows five authors; Omni-Fake shows Xiangtai Li at NTU; Organic or Diffused shows Reid Southen (Concept Artist), without an institution superscript or invented marker.
- Final browser console logs: **0 public errors / 0 Admin errors**.

Observed limitation: the pinned survey detail pane’s “Show all authors” control did not expand the ninth author. The unique-paper card expands correctly. This is unchanged frontend behavior; it was documented, not repaired, in this data-only pass. Initial localhost navigation trouble was resolved with the separate static server; no production workaround was added.

### Final diff scope

Exactly one existing mapping changed (Kumoh); one confirmed location was appended; eight location-review rows were updated; thirteen institution-audit events were appended. No old location or mapping was removed. Other changes are generated reports/public JSON, exact baseline totals, focused tests, and evidence documentation/cache. No production code, manual override files, PDFs, browser screenshots or credentials were added. No staging or commit.

## Remaining work

Only these public-relevant evidence cases remain:

- Locations: NAWCWD China Lake building; Huya publication-specific 510006 office; Uttar Pradesh directorate building; IrisKing publication-time office; Griffith survey campus; HUTECH survey campus; Pusan survey center site.
- Authors: Jia Wang; Aruna J. Chamatkar; Chuah ChaiWen; Daniel S. Yeung; Usha Kosarkar. Their exact missing evidence and decision reasons are given above.

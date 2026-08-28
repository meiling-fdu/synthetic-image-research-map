# Formal publication and five-location audit

Evidence reviewed 2026-08-27; exporter and final verification continued 2026-08-28.

Five user-entered locations; known/touched publication-version conflicts only. No general Low backlog or dormant Tier-C curation.

## Location verification

All five Admin submissions retain their IDs, creator, creation time, and submitted coordinates in audit history. Only JD.com’s longitude sign changes in the location row. Four rejected points remain stored with `coordinate_status=needs_coordinate_review`; they are excluded from public markers and Admin confirmed-location choices. Exact reasons remain in the Admin review evidence.

| Institution | Submitted coordinates | Final effective state | Public marker |
| --- | --- | --- | --- |
| JD.com (Mountain View) | 37.39381, 122.05238 | confirmed; longitude -122.05238 | eligible and present |
| Naval Air Warfare Center Weapons Division (China Lake) | 35.6857, -117.692 | needs_coordinate_review (pending_review queue) | suppressed |
| Huya Inc. (Guangzhou City) | 23.0009, 113.3268 | needs_coordinate_review (pending_review queue) | suppressed |
| Department of Technical Education, Uttar Pradesh (Kanpur) | 26.4936, 80.3018 | needs_coordinate_review (pending_review queue) | suppressed |
| Beijing IrisKing Co., Ltd. (Beijing) | 39.9856, 116.3096 | needs_coordinate_review (pending_review queue) | suppressed |

### JD.com

Publisher biography (532-6) explicitly places Bappy at JD.Com, Mountain View. The 2019 office at 675 East Middlefield Road is corroborated by published address evidence and OSM named office node 6816244066, created 2019-09-22 at 37.3938075,-122.0523759. Preserve user rounded point with longitude sign corrected; positive 122.05238 was in Asia.

[Independent evidence](https://www.openstreetmap.org/node/6816244066)

### Naval Air Warfare Center Weapons Division

Formal paper identifies Arjuna Flenner at NAWCWD China Lake, California, not Point Mugu. NAVAIR identifies 1 Administration Circle; selected 35.6857,-117.692 has no mapped institution/building linkage (nearest reverse feature is airfield arresting gear 0.5 km away). Site is insufficiently evidenced, not a confirmed building coordinate. Retain submitted point only as a needs-review candidate.

[Independent evidence](https://www.navair.navy.mil/nawcwd/Contact_NAWCWD)

### Huya Inc.

Formal publisher PDF gives Xiao Meng affiliation d: Huya Inc, Guangzhou, 510006, China. Selected 23.0009,113.3268 lies inside OSM residential development 1431856585 (Chimelong Wanbo Yuefu), near apartment Block 12, not a verified Huya 510006 office. Official Huya 2019 move notice names Zexi Street 13, Hanxi commercial center; no publication-specific evidence links this selected residential point to the paper. Do not substitute headquarters postcode 511446.

[Independent evidence](https://blog.huya.com/policy/1387)

### Department of Technical Education, Uttar Pradesh

Springer author entry identifies Digvijay Pandey at Department of Technical Education, Kanpur, Uttar Pradesh. Government evidence identifies Directorate at Vikas Nagar. Selected 26.4936,80.3018 lies inside a mapped private park (OSM way 1211543677), not an identified Directorate office. No institution/building linkage verified; official site timed out. Retain candidate and textual geography, suppress unsupported marker.

[Independent evidence](https://link.springer.com/article/10.1007/s11468-024-02492-1)

### Beijing IrisKing Co., Ltd.

Jing Liu publication affiliation is Beijing IrisKing Company Ltd., Beijing, China (2024). Selected 39.9856,116.3096 lies inside OSM garden 1100981091 near Haidian Road/Peking University. It is not the 2024 disclosed residence at No. 9 North Fourth Ring West Road, floor 22 room 2210 (Yingu Tower), and no publication-time office evidence links IrisKing to this garden. The 2022 Chengfu Road 45 office must not substitute for a verified 2024 site.

[Independent evidence](https://epaper.cs.com.cn/zgzqb/images/2024-04/29/B132/zqB13229.pdf)

JD.com: the published Co-Occurrence biography explicitly places Jawadul H. Bappy at JD.com, Mountain View. OSM node 6816244066 records JD.COM at 675 East Middlefield Road and 37.3938075, -122.0523759; the retained rounded point is 37.39381, -122.05238. The 2019 node is corroboration, not a replacement for the paper-specific biography.

OpenStreetMap reverse responses alone are not building attribution. The cached bounded map extracts support the park/garden/residential feature checks. NAWCWD is an evidence gap: the nearest reverse result is airfield arresting gear roughly 0.5 km away; this does not prove the exact submitted point is on a runway. See the raw-evidence README for queries, attribution, and hashes.

Final effective Admin queue: **Pending Review 8; Needs Coordinates 8; Ambiguous 0; Needs Coordinate Review 4; Confirmed locations 456**. The location file contains 460 rows, including four candidates. Raw review rows include excluded/dormant relationships; effective queue counts are the authoritative public-relevant counts.

Relationship completeness: **COMPLETE 1,263; ACTIONABLE 8; EXCLUDED 29; ERROR 0**. The four additional actionable cases are the newly evidenced survey institutions without confirmed sites.

## Formal-version corrections

The formal publication PDF controls roster, order, spelling, and superscript affiliations over landing-page/BibTeX, preprint, project, and OpenAlex metadata. This is a scoped correction, not a global name merge. Before/after paper and mapping snapshots are appended in the institution audit log; prior events are preserved.

### IncreFA: Breaking the Static Wall of Generative Model Attribution

Paper ID: `curated:246f07c81b9f91e527eb`. [Formal source](https://openaccess.thecvf.com/content/CVPR2026/papers/Qin_IncreFA_Breaking_the_Static_Wall_of_Generative_Model_Attribution_CVPR_2026_paper.pdf). PDF SHA-256: `8950c4ae8818d0e76062f40099f2bdc2111db7450771358a1825a8d73b4ba806`.

Canonical author occurrences: **6 → 5**.

CVF proceedings PDF page 35405 has five authors; Yuexuan Tan is absent. arXiv v2 AND the CVF HTML/BibTeX have six. The inspected publication PDF author block controls this record under the requested rule; the separate IEEE final file was not accessed. Preserve discrepancy, do not infer an affiliation for the absent occurrence. Dongliang Chang is corresponding author.

Previous canonical roster: Haotian Qin, Dongliang Chang, Yueying Gao, Yuexuan Tan, Lei Chen, Zhanyu Ma.

Final canonical roster: Haotian Qin; Dongliang Chang; Yueying Gao; Lei Chen; Zhanyu Ma.

Added author strings: none. Retired author strings: Yuexuan Tan. String changes are publication-version/spelling decisions, not identity merges.

| Final author index | Final author name | Formal marker(s) | Formal affiliation(s) | Mapping IDs |
| ---: | --- | --- | --- | --- |
| 1 | Haotian Qin | 1 | School of Artificial Intelligence, Beijing University of Posts and Telecommunications, China | `mapping:49253d880847ebba366a` |
| 2 | Dongliang Chang | 1* | School of Artificial Intelligence, Beijing University of Posts and Telecommunications, China | `mapping:49253d880847ebba366a` |
| 3 | Yueying Gao | 1 | School of Artificial Intelligence, Beijing University of Posts and Telecommunications, China | `mapping:49253d880847ebba366a` |
| 4 | Lei Chen | 2 | Tsinghua University, China | `mapping:eafafaf4180a2400a7d2` |
| 5 | Zhanyu Ma | 1 | School of Artificial Intelligence, Beijing University of Posts and Telecommunications, China | `mapping:49253d880847ebba366a` |

Mapping positions are regenerated from this exact matrix. Affiliation groups retain explicit ordering and every evidenced multi-affiliation; no numeric position is carried over blindly.

CVF PDF has five authors; CVF landing page and BibTeX have six, including Yuexuan Tan. Tan is retained only in discrepancy/history, not the canonical roster or missing-author warnings. No separate IEEE final PDF was inspected.

### Omni-Fake: Benchmarking Unified Multimodal Social Media Deepfake Detection

Paper ID: `curated:fe42bad5f72f9f6858c5`. [Formal source](https://openaccess.thecvf.com/content/CVPR2026/papers/Li_Omni-Fake_Benchmarking_Unified_Multimodal_Social_Media_Deepfake_Detection_CVPR_2026_paper.pdf). PDF SHA-256: `7b18a193ea5f991ff704e46b284dcc966395b3c465ef2889efffcd2e32fb7440`.

Canonical author occurrences: **13 → 13**.

Formal CVPR PDF page 30299 and CVF BibTeX agree on Xiangtai Li at position 12, superscript 4 Nanyang Technological University. arXiv v1 names Jason Li; project roster differs. This replaces a paper occurrence, not a global identity/alias merge. First three authors contribute equally; Guangliang Cheng is corresponding author. Existing NTU mapping is supported, not a speculative new institution.

Previous canonical roster: Tianxiao Li; Zhenglin Huang; Haiquan Wen; Yiwei He; Xinze Li; Bingyu Zhu; Wuhui Duan; Congang Chen; Zeyu Fu; Yi Dong; Baoyuan Wu; Jason Li; Guangliang Cheng.

Final canonical roster: Tianxiao Li; Zhenglin Huang; Haiquan Wen; Yiwei He; Xinze Li; Bingyu Zhu; Wuhui Duan; Congang Chen; Zeyu Fu; Yi Dong; Baoyuan Wu; Xiangtai Li; Guangliang Cheng.

Added author strings: Xiangtai Li. Retired author strings: Jason Li. String changes are publication-version/spelling decisions, not identity merges.

| Final author index | Final author name | Formal marker(s) | Formal affiliation(s) | Mapping IDs |
| ---: | --- | --- | --- | --- |
| 1 | Tianxiao Li | 1* | University of Liverpool | `mapping:10fc97957d44ff363c83` |
| 2 | Zhenglin Huang | 1* | University of Liverpool | `mapping:10fc97957d44ff363c83` |
| 3 | Haiquan Wen | 1* | University of Liverpool | `mapping:10fc97957d44ff363c83` |
| 4 | Yiwei He | 1 | University of Liverpool | `mapping:10fc97957d44ff363c83` |
| 5 | Xinze Li | 1 | University of Liverpool | `mapping:10fc97957d44ff363c83` |
| 6 | Bingyu Zhu | 1 | University of Liverpool | `mapping:10fc97957d44ff363c83` |
| 7 | Wuhui Duan | 1 | University of Liverpool | `mapping:10fc97957d44ff363c83` |
| 8 | Congang Chen | 1 | University of Liverpool | `mapping:10fc97957d44ff363c83` |
| 9 | Zeyu Fu | 2 | University of Exeter | `mapping:d246b65f7bc657ac85a1` |
| 10 | Yi Dong | 1 | University of Liverpool | `mapping:10fc97957d44ff363c83` |
| 11 | Baoyuan Wu | 3 | The Chinese University of Hong Kong, Shenzhen | `mapping:37832cb186ce24f33da6` |
| 12 | Xiangtai Li | 4 | Nanyang Technological University | `mapping:58921f4d9d84358ac798` |
| 13 | Guangliang Cheng | 1 | University of Liverpool | `mapping:10fc97957d44ff363c83` |

Mapping positions are regenerated from this exact matrix. Affiliation groups retain explicit ordering and every evidenced multi-affiliation; no numeric position is carried over blindly.

Formal author 12 is Xiangtai Li, affiliation 4 NTU. Existing Xiangtai/NTU mapping is retained and reindexed. The previous Jason Li name is version-discrepancy provenance only; no Jason/Xiangtai identity equivalence is asserted.

### Detecting GAN Generated Fake Images Using Co-Occurrence Matrices

Paper ID: `curated:60066ef08c2226131085`. [Formal source](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/ei/31/5/art00008). PDF SHA-256: `1081ddc3a3240f41a72735c93a570da1a91c5c3243dddcba55e1979069049907`.

Canonical author occurrences: **7 → 7**.

Publisher page 532-1: preserve seven-author roster and affiliations; restore B. S. Manjunath spacing and Roy-Chowdhury hyphen. Previous B.S. Manjunath and Roy–Chowdhury strings retained in audit only. Author biography on page 532-6 explicitly identifies Bappy at JD.Com in Mountain View, CA.

Previous canonical roster: Lakshmanan Nataraj; Tajuddin Manhar Mohammed; B.S. Manjunath; Shivkumar Chandrasekaran; Arjuna Flenner; Jawadul H. Bappy; Amit K. Roy–Chowdhury.

Final canonical roster: Lakshmanan Nataraj; Tajuddin Manhar Mohammed; B. S. Manjunath; Shivkumar Chandrasekaran; Arjuna Flenner; Jawadul H. Bappy; Amit K. Roy-Chowdhury.

Added author strings: B. S. Manjunath; Amit K. Roy-Chowdhury. Retired author strings: B.S. Manjunath; Amit K. Roy–Chowdhury. String changes are publication-version/spelling decisions, not identity merges.

| Final author index | Final author name | Formal marker(s) | Formal affiliation(s) | Mapping IDs |
| ---: | --- | --- | --- | --- |
| 1 | Lakshmanan Nataraj | inline | Mayachitra Inc., Santa Barbara, California, USA | `mapping:b2dfbca89d216899e9c8` |
| 2 | Tajuddin Manhar Mohammed | inline | Mayachitra Inc., Santa Barbara, California, USA | `mapping:b2dfbca89d216899e9c8` |
| 3 | B. S. Manjunath | inline | Mayachitra Inc., Santa Barbara, California, USA | `mapping:b2dfbca89d216899e9c8` |
| 4 | Shivkumar Chandrasekaran | inline | Mayachitra Inc., Santa Barbara, California, USA | `mapping:b2dfbca89d216899e9c8` |
| 5 | Arjuna Flenner | inline | Naval Air Warfare Center Weapons Division, China Lake, California, USA | `mapping:0f51254f7cd4fb7fa8d1` |
| 6 | Jawadul H. Bappy | inline | JD.com | `mapping:b6e8a4865abd1e59e3fd` |
| 7 | Amit K. Roy-Chowdhury | inline | University of California, Riverside, California, USA | `mapping:37edafe30f9ae94c3121` |

Mapping positions are regenerated from this exact matrix. Affiliation groups retain explicit ordering and every evidenced multi-affiliation; no numeric position is carried over blindly.

### Deep Learning for Deepfakes Creation and Detection: A Survey

Paper ID: `curated:c071c25bc2957d78569b`. [Formal source](https://research-repository.griffith.edu.au/server/api/core/bitstreams/9047c38e-4092-41fe-a8e7-e73d74b6d891/content). PDF SHA-256: `252b1be5f7ddf291ce0ce78082af09c9e9389c5ce579aeb9b15e4d810137f008`.

Canonical author occurrences: **5 → 9**.

Known five-versus-nine-author conflict from previous audit: 2022 CVIU publication overrides 2020 Figshare deposit. Add Quoc Viet Hung Nguyen, Thien Huynh-The, Thanh Tam Nguyen, Quoc-Viet Pham; move Cuong M. Nguyen from position 2/Deakin to position 9/Polytechnic University of Hauts-de-France. Four new canonical institutions registered from explicit publication affiliations; no new geocoding. Historical Figshare DOI/roster retained in audit. Deakin sites for unchanged authors retained. HUTECH is not VNU-HCM University of Technology.

Previous canonical roster: Thanh Thi Nguyen; Cuong M. Nguyen; Dung Tien Nguyen; Duc Thanh Nguyen; Saeid Nahavandi.

Final canonical roster: Thanh Thi Nguyen; Quoc Viet Hung Nguyen; Dung Tien Nguyen; Duc Thanh Nguyen; Thien Huynh-The; Saeid Nahavandi; Thanh Tam Nguyen; Quoc-Viet Pham; Cuong M. Nguyen.

Added author strings: Quoc Viet Hung Nguyen; Thien Huynh-The; Thanh Tam Nguyen; Quoc-Viet Pham. Retired author strings: none. String changes are publication-version/spelling decisions, not identity merges.

| Final author index | Final author name | Formal marker(s) | Formal affiliation(s) | Mapping IDs |
| ---: | --- | --- | --- | --- |
| 1 | Thanh Thi Nguyen | a | School of Information Technology, Deakin University, Victoria, Australia | `mapping:e52721d76b4e36468169` |
| 2 | Quoc Viet Hung Nguyen | b | School of Information and Communication Technology, Griffith University, Queensland, Australia | `mapping:7b3e580c7133d150e40d` |
| 3 | Dung Tien Nguyen | a | School of Information Technology, Deakin University, Victoria, Australia | `mapping:e52721d76b4e36468169` |
| 4 | Duc Thanh Nguyen | a | School of Information Technology, Deakin University, Victoria, Australia | `mapping:e52721d76b4e36468169` |
| 5 | Thien Huynh-The | c | ICT Convergence Research Center, Kumoh National Institute of Technology, Gyeongbuk, Republic of Korea | `mapping:27618b8da3c3e6c1b003` |
| 6 | Saeid Nahavandi | d | Institute for Intelligent Systems Research and Innovation, Deakin University, Victoria, Australia | `mapping:deakin-waurn-ponds-20260827` |
| 7 | Thanh Tam Nguyen | e | Faculty of Information Technology, Ho Chi Minh City University of Technology (HUTECH), Ho Chi Minh City, Vietnam | `mapping:3ccd22bfe50f3c185660` |
| 8 | Quoc-Viet Pham | f | Korean Southeast Center for the 4th Industrial Revolution Leader Education, Pusan National University, Busan, Republic of Korea | `mapping:ff5a05296dbb2552e5cb` |
| 9 | Cuong M. Nguyen | g | LAMIH UMR CNRS 8201, Universite Polytechnique Hauts-de-France, Valenciennes, France | `mapping:599c44d0adaf713862f4` |

Mapping positions are regenerated from this exact matrix. Affiliation groups retain explicit ordering and every evidenced multi-affiliation; no numeric position is carried over blindly.

The 2020 Figshare deposit (DOI 10.6084/m9.figshare.12731039.v1) is superseded canonically by the 2022 CVIU publication (DOI 10.1016/j.cviu.2022.103525, volume 223, article 103525). Griffith’s institutional cover labels its copy Version of Record; the body has manuscript-style layout. Publisher metadata corroborates the nine-author roster.

Cuong M. Nguyen moves from old index 2/Deakin to formal index 9/Polytechnic University of Hauts-de-France. Saeid Nahavandi moves from index 5 to 6 and remains at the already reviewed Deakin Waurn Ponds site. School of IT authors retain Burwood. New formal authors are Quoc Viet Hung Nguyen, Thien Huynh-The, Thanh Tam Nguyen, and Quoc-Viet Pham. Griffith, Kumoh, HUTECH, and Pusan are explicit institutional affiliations, but no site coordinates were invented. HUTECH is not VNU-HCM University of Technology.

Seven mapping affiliation groups are ordered 1–7; the public paper list deduplicates the two Deakin groups into six institution indexes while retaining both map campuses. All nine authors are affiliation-complete; four institutions remain location-actionable.

### Plasmonics year

[Final Springer citation](https://link.springer.com/article/10.1007/s11468-024-02492-1): volume 20, pages 2945–2964 (2025). Canonical year 2024 → 2025; online-first date 6 September 2024 remains in provenance. Author roster/order and affiliations are unchanged.

## Final author completeness

**2,725 mapped author occurrences; 3 explicitly non-institutional; 5 unresolved warnings; 541/546 affiliation-complete papers.** Hainan Ren, Henan Wang, and Reid Southen remain visible with the established source wording, without fake institutions or markers and without missing-affiliation warnings.

| Remaining unresolved author | Formal-source limitation | Source |
| --- | --- | --- |
| Jia Wang | Formal CSCWD 2026 programme confirms a three-author roster but no accessible formal author-affiliation block. Do not merge the Yi-Xiang Wang identity candidate. | [Source](https://fyust.edu.cn/gjhyqk/cscwd2026/program.pdf) |
| Aruna J. Chamatkar | Formal IEEE L&T 2025 author-affiliation block was inaccessible. A current employer profile does not establish this publication affiliation. | [Source](https://doi.org/10.1109/lt64002.2025.10940759) |
| Chuah ChaiWen | Formal CyberComp 2024 author-affiliation block was inaccessible. Proceedings/aggregator names do not resolve the exact institution/campus; no guessed affiliation or unrelated spelling edit applied. | [Source](https://doi.org/10.1109/cybercomp60759.2024.10913843) |
| Daniel S. Yeung | Formal Evasion publisher PDF labels affiliation e only Hong Kong, China. Geographic text is not an institution or explicit independent-researcher status. | [Source](https://tas-lab.org/publication/2024-evasion-on-general-gan-generated-image-detection-by-disentangled-representation/index.pdf) |
| Usha Kosarkar | Formal Procedia Computer Science article author block was inaccessible. The exact GHRIET campus is not established; co-author/current-employment inference rejected. | [Source](https://doi.org/10.1016/j.procs.2023.01.237) |

The five cases were retained after the corrected-roster report; no speculative affiliation was added. No new investigation was restarted during the continuation.

## Public output

| Metric | Final |
| --- | ---: |
| Papers | 546 |
| Raw map-source paper identities | 540 |
| Public papers with locations | 539 |
| Map relationships in JSON | 1,263 |
| Unique mapped institution names (validator) | 617 |
| Canonical institutions, active / total | 650 / 662 |
| Public map validation errors / warnings | 0 / 0 |
| Public paper validation errors / warnings | 0 / 5 |
| Public paper missing-coordinate flag | 1 |
| Actionable geographic relationships | 8 |
| Unexplained shrinkage | 0 |

The existing frontend applies its own normalization/deduplication: the unfiltered browser showed 1,262 institution records, 616 institutions, 54 countries, and 546 unique papers. Raw map-source paper identities and matched public-paper counts use different identity semantics; neither is an author-completeness count.

## Implementation and verification

Stored locations require a confirmed status plus valid coordinates to be offered as confirmed sites. Explicit candidate status blocks both newly created and preserved markers. The relationship resolver and shrinkage guard use exact institution/location identity; another campus is unaffected. Reconfirmation can restore eligibility.

Formal roster migrations require a durable exact before/after audit, matching current mapping scopes and author indexes for the entire final matrix. A changed DOI alone or a similar name cannot authorize removing an old relationship. Repeated exports are checked for byte stability. Both complete JSON files are byte-identical across the final consecutive exports. The check also exposed an existing unregistered-venue normalization cycle; the resolver now consistently keeps raw source text instead of alternating an unconfirmed generated ID. This affects derived venue fields on 20 paper records / 62 map records, without changing any curated venue, author, year, DOI, or affiliation; no additional venue research or approval occurred.

The schema now permits retained `needs_coordinate_review` candidates in institution_locations.csv without weakening coordinate validation. Admin lists these separately from confirmed choices. No raw or manual source data is rewritten.

Browser QA: the single requested attempt succeeded. The local static map loaded without console warnings/errors. IncreFA five-author roster, Omni-Fake author 12, the expanded nine-author survey/2022 journal citation, and Co-Occurrence’s JD.com relationship (with NAWCWD absent) were inspected interactively. Survey layout was visually inspected. No production workaround or screenshot/debug artifact was added to the repository.

[Machine-readable verification](formal_publication_verification_2026-08-28.json):

| Check | Result |
| --- | --- |
| Focused exporter/location/formal-author/index/order/non-institutional/venue tests | 213 passed; 0 skipped; 0 failed |
| Full repository suite | 1,171 passed; 0 skipped; 0 failed |
| Curated validator | 0 errors; 178 existing warnings |
| Public map validator | 0 errors; 0 warnings |
| Public paper validator | 0 errors; 5 unresolved-author warnings |
| Generated map/paper payload validator | passed |
| Relationship completeness | 1,263 COMPLETE; 8 ACTIONABLE; 29 EXCLUDED; 0 ERROR |
| JavaScript syntax | 10 files passed |
| Python compilation | 14 changed files passed |
| Changed CSV field counts | valid |
| git diff --check | passed |
| Consecutive canonical exports | byte-identical JSON pair |
| Browser QA | passed; no console warnings/errors |

## Remaining public-relevant work

Eight precise site confirmations: NAWCWD China Lake, Huya’s publication-time Guangzhou 510006 office, DTE Uttar Pradesh Kanpur directorate, Beijing IrisKing’s publication-time office; and the formal survey’s Griffith, Kumoh, HUTECH, and Pusan affiliations. Five author-affiliation ambiguities remain as listed above. No general Low backlog or dormant Tier-C work was performed.

Nothing staged or committed.

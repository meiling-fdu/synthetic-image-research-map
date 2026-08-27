# Author-affiliation review — 27 August 2026

## Scope and result

Continued from the live working tree after the user's Admin edits. Reviewed Groups A, B, C, then genuine conflicts. Repaired 37 missing author links across 20 papers; 19 papers became complete. Ten authors remain explicitly unresolved, with paper-specific reasons in the existing `data/curated/institution_audit_log.csv` (`author_affiliation_unresolved`). No speculative institutional affiliation was assigned to remove a warning.

The PDF skill's rendered-page workflow was used for visually encoded author superscripts. PDFs and temporary author-affiliation matrices remained outside the repository. Where a rendered primary PDF was unavailable, the audit explicitly identifies the structured publisher/conference metadata used instead. No current employer was substituted for a historical paper affiliation.

## Live baseline and final counts

| Metric | Initial live state | Final |
| --- | ---: | ---: |
| Public paper records | 546 | 546 |
| Unresolved author links / public author warnings | 47 | 10 |
| Affected papers | 29 | 10 |
| Complete papers | 517 | 536 |
| Papers with zero mapped authors | 0 | 0 |
| Raw-map unique paper identities | 540 | 538 |
| Public paper records with mapped locations | 539 | 537 |
| Public paper records without raw-map relationships | 7 | 9 |
| Raw map relationships | 1,242 | 1,248 |
| Unique mapped institutions, validator semantics | 614 | 609 |
| Public papers missing affiliations | 0 | 0 |
| Public papers flagged missing coordinates | 1 | 7 |
| Curated papers | 325 | 342 |
| Curated author-institution mapping rows | 882 | 936 |
| Canonical institution rows | 647 | 658 |
| Confirmed institution locations | 435 | 435 |
| Unresolved consistency High / Medium / Low | 0 / 0 / 167 | 0 / 0 / 174 |
| Coordinate Tier A | 0 | 25 |
| Effective Admin Pending Review / Needs Coordinates | 0 / 0 | 28 / 28 |
| Curated validation errors / warnings | 0 / 165 | 0 / 177 |
| Public map validation errors / warnings | 0 / 0 | 0 / 0 |
| Public paper validation errors / warnings | 0 / 47 | 0 / 10 |

Raw-map paper identities and public paper records have distinct version-identity counting semantics. Nine paper records have no map relationship. The separate `missing_coordinates` flag counts partial coordinate gaps too: five of its seven flagged papers still have at least one mapped institution. The two newly mapless papers are Co-Occurrence and Complement; the other seven were already mapless. The legacy blocker report labels these two `public_preview_cap_or_filter`, but the reviewed affiliations specifically lack confirmed coordinates. The 25 newly exposed Tier-A institutions (28 paper-specific review rows) come directly from supported author repairs, not reopening the user's resolved cases. No coordinates were invented or changed. Coordinate-report invariant violations: zero. The Low consistency count is reported for comparison only; that backlog was not processed.

## Evidence-supported repairs

The existing mapping and institution audit CSVs retain raw affiliation, canonical institution, author positions, explicit affiliation order, evidence URL, and prior mapping reference where one existed. Group totals count missing links eliminated, not mapping CSV rows.

| Group | Paper | Links repaired | Evidence and decisive interpretation |
| --- | --- | ---: | --- |
| A | SynerDetect | 8 | [AAAI paper](https://ojs.aaai.org/index.php/AAAI/article/view/37568): first seven authors at HKUST Guangzhou; Qing Zhang at Sun Yat-sen; Lei Zhu at both HKUST Guangzhou and HKUST. Exact nine-author order and indices 1 / 3 / 1,2 retained. |
| A | Deep Learning for Deepfakes Creation and Detection: A Survey | 4 | [Version-specific Figshare PDF](https://ndownloader.figshare.com/files/24099812): five-author 2020 deposited version, all at Deakin. Cuong M. Nguyen and Dung Tien Nguyen corrected from erroneous indexed names; later nine-author version not substituted. |
| A | RADAR | 3 | [Author-institution repository PDF](https://pure.uva.nl/ws/files/309086291/RADAR.pdf): Amsterdam, Beihang, Zhejiang Sci-Tech, Xiaohongshu, and Beijing Jiaotong assigned by explicit indices. Xiaolong Jiang uses Xiaohongshu's existing Beijing location. |
| A | The Face Deepfake Detection Challenge | 3 | [Author-hosted publisher PDF](https://www.dmi.unict.it/ortis/articoli/85140647182.pdf): exact 20-author matrix; Antonino Paratore at iCTLab, Linh M. Q. Bui and Marco Fontani at Amped; Roberto Caldelli at both CNIT and Universitas Mercatorum. Two Cagliari departments retain one canonical university identity. |
| B | Detecting GAN Generated Fake Images Using Co-Occurrence Matrices | 2 | [Publisher PDF](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/ei/31/5/art00008), corroborated by arXiv 1903.06836: first four authors at Mayachitra, Arjuna Flenner at Naval Air Warfare Center Weapons Division, Jawadul H. Bappy at JD.com, Amit K. Roy-Chowdhury at UCR. Publisher author order retained; old all-author mappings explicitly retired. |
| B | Evasion on General GAN-Generated Image Detection by Disentangled Representation | 1 | [Author-hosted publisher PDF](https://tas-lab.org/publication/2024-evasion-on-general-gan-generated-image-detection-by-disentangled-representation/index.pdf): first four at SCUT, Xiao Meng at Huya; Daniel S. Yeung has no named institution and remains unresolved. |
| B | Deepfake Generation and Detection: Case Study and Challenges | 2 | [Institutional publisher PDF](https://digitalknowledge.cput.ac.za/bitstream/11189/9706/1/Deepfake_Generation_and_Detection.pdf): Srinivas Aluvala at SR University; Vrince Vimal at both Graphic Era Hill University and Graphic Era University. Pronaya Bhattacharya at Amity only, not every institution in an extracted text block. |
| B | Exposing the Fake | 2 | [Paper PDF](https://arxiv.org/pdf/2307.06272): Ruipeng Ma, Fei Kong, Xiaoshuang Shi at UESTC; Jinhao Duan and Kaidi Xu at Drexel. |
| C | Adaptive Test-Time Semantic Debiasing | 1 | Official CVF 2025 PDF: Xiaoqin Fu corrected to Xiaomeng Fu; already correct IIE-CAS mapping preserved. |
| C | Beyond Known Fakes | 1 | arXiv 2502.10803v2: Li Ping Wang corrected to Li Wang; existing Shandong mapping preserved. |
| C | On Attribution of Deepfakes | 1 | arXiv 2008.09194v2: duplicate Jin Zhou / Jin Peng Zhou consolidated into Jin Peng Zhou at author position 2. Toronto and Vector affiliations retained, as was Ilia Shumailov's additional Cambridge affiliation. |
| C | Fusing Global and Local Features | 1 | [Author PDF](https://havocfixer.github.io/resource/22_ICIP.pdf): Koki Nagano at NVIDIA; other five authors at Buffalo. |
| C | Beyond the Spectrum | 1 | [IJCAI PDF](https://www.ijcai.org/proceedings/2021/0349.pdf): Ning Yu at both Max Planck Institute for Informatics and Maryland; Yang He/Mario Fritz at CISPA; Margret Keuper at Mannheim. |
| C | RIGID | 1 | arXiv 2405.20112v1: Pin‐Yu Chen normalized to Pin-Yu Chen at IBM Research; other two authors at CUHK. Used existing confirmed IBM Research location resolution. |
| C | Complement Face Forensic Detection and Localization with FacialLandmarks | 1 | arXiv 1910.05455v1: Kritaphat Songsri-in at Imperial; Stefanos Zafeiriou at Imperial and Oulu. |
| C | An Improved Dense CNN Architecture | 1 | [Institutional publisher PDF](https://digitalknowledge.cput.ac.za/bitstream/11189/9712/1/Improved_Dense_CNN_Architecture.pdf): Pronaya Bhattacharya at Amity only; author-specific Nirma, Najran, Cape Peninsula, and Durban associations retained. |
| C | Intriguing Properties of Synthetic Images | 1 | Official CVF 2023 workshop PDF: Koki Nagano at NVIDIA; remaining four authors at Naples. Existing Naples mapping ID retained and positions made explicit. |
| C | Addressing Diffusion Model Based Counter-Forensic Image Manipulation | 1 | [Official conference entry 153](https://icvgip.in/2024/accepted-regular-papers): Chandra Sekhar Seelamantula and Nishanth Shetty at IISc; first two authors at NITK. Structured conference metadata, not a claimed rendered PDF. |
| C | Enhancing Sensing and Imaging Capabilities Through Surface Plasmon Resonance | 1 | [Publisher author-affiliation entry](https://link.springer.com/article/10.1007/s11468-024-02492-1): Digvijay Pandey at Department of Technical Education, Uttar Pradesh. R. Uma Maheshwari and B. Paulchamy at Hindusthan Institute of Technology, Coimbatore, not the different Hindustan Institute of Technology and Science. |
| C | Enhancing Deepfake Detection with Diversified Self-Blending Images and Residuals | 1 | [Publisher-supplied structured metadata](https://doaj.org/article/119351797e28470998c905b4426d63e1), corroborated by accepted-paper text: Jing Liu at Beijing IrisKing Co., Ltd.; other three at Academy of Broadcasting Science. Primary PDF rendering unavailable; audit records that limitation. |

Group A repaired 18 links, B repaired 7, and C repaired 12. Additional source-supported full-name corrections include Antonino Paratore, Yogesh Patel, Innocent Ewean Davidson, Thokozile F. Mazibuko, Daniel S. Yeung, and R. Uma Maheshwari. Previously validated preferred author names were not reverted. Four newly curated titles were passed through the existing canonical title normalizer.

## Exact remaining unresolved roster

These are the only remaining author-affiliation cases for this pass. Evidence URLs and complete notes are persisted in the existing institution audit log.

| Author | Exact paper | Reason |
| --- | --- | --- |
| Hainan Ren | Detecting Multimedia Generated by Large AI Models: A Survey | Rendered arXiv 2402.00045v7 footnote supplies an email, not an institution. Current Aibee employment is not a substitute. |
| Jia Wang | Fake Detection Based on Balanced Attention and Information Guidance for Collaborative Image Processing Tasks | Programme names Jia Wang; existing pending mapping names Yi-Xiang Wang. Generic IEEE profile cannot resolve the paper-specific identity conflict; full text unavailable. |
| Yuexuan Tan | IncreFA: Breaking the Static Wall of Generative Model Attribution | CVF accepted PDF has five authors and omits Tan; CVF HTML/BibTeX and arXiv 2604.17736v2 have six, with Tan at BUPT. Publication-version conflict remains. |
| Jason Li | Omni-Fake: Benchmarking Unified Multimodal Social Media Deepfake Detection | Rendered arXiv 2605.01638v1 gives Jason an NTU index; official project/BibTeX omit Jason and NTU, while the curated mapping names Xiangtai Li. No evidence reconciles these identities/versions. |
| Henan Wang | Your AI-Generated Image Detector Can Secretly Achieve SOTA Accuracy, If Calibrated | Official AAAI author entry says Independent Researcher; no institution supplied. |
| Aruna J. Chamatkar | A Novel Framework for Deepfake Image Detection Using Deep Learning Approach | Primary full text unavailable; bibliographic authorship/current profiles do not establish the paper's affiliation. |
| Chuah ChaiWen | Deepfake Image Detection Using ResNet50 Model | Secondary structured metadata suggests Guangdong University of Science and Technology, Dongguan, but accessible primary author-affiliation confirmation was not obtained. Do not conflate it with Guangdong University of Technology. |
| Daniel S. Yeung | Evasion on General GAN-Generated Image Detection by Disentangled Representation | Rendered publisher affiliation e says only Hong Kong, China; no organization. |
| Reid Southen | Organic or Diffused: Can We Distinguish Human Art from AI-Generated Images? | Rendered manuscript says Concept Artist; an older collective Chicago line does not establish his institutional affiliation. |
| Usha Kosarkar | Revealing and Classification of Deepfakes Video's Images using a Customize Convolution Neural Network Model | Publisher PDF blocked; GHRIET Nagpur appears in snippets/cached metadata, but primary layout and exact campus identity were not verified. |

## Protected Admin decisions

Compared 34 protected rows across seven curated CSVs against the live pre-edit snapshot before and after exports. All field values remain identical, including timestamps and review state.

- Jilin Engineering Vocational College retains Siping/Jilin/China, 43.318744, 124.334624, and its confirmed/known Admin decision.
- China Telecom Cloud retains Beijing/China, 39.9458, 116.4217, and its confirmed/known Admin decision.
- ForgeryMoE / Jian Zhao retains mapping `mapping:457e9e85050e4ece4e76`, TeleAI institution `institution:a1ff6f7123083db9`, Beijing location, affiliation order 3, and the user's raw affiliation string. The ignored orphan institution remains ignored.
- No stale generator or report overwrote these rows. The regression test also runs a temporary-output exporter and checks that every curated CSV remains byte-for-byte unchanged.

## Relationship and integrity audit

No paper was removed. Nine semantic relationships were replaced or retired with explicit current curation evidence, and fifteen were added: net +6. Unexplained relationship shrinkage is **zero**; the existing shrinkage guard returns PROCEED.

The nine explained removals are three over-broad Co-Occurrence mappings, three translated Face Challenge institution variants, one Beyond the Spectrum canonical replacement, the incorrect Hindustan association in the SPR paper, and the incomplete Imperial-only Complement relationship. Co-Occurrence and Complement lose their old raw-map presence because corrected affiliations lack confirmed coordinates; both remain complete, visible paper records. The large JSON diff includes record reordering and identity replacement, not unexplained paper deletion.

The automatic-removal resolver now requires an exact DOI when the old automatic record has no paper ID. Correct, different, and missing DOI cases have regression coverage, preventing one paper's audit from removing another paper's relationship. The inherited repeated-detail-pass fix is preserved; a real repaired paper retains every author index through three repeated passes, including institutions without coordinates.

All 887 active mappings resolve to a valid current paper identity or durable exclusion. All 55 numeric-position mappings (the new/updated rows) match source-supported author order, active canonical institutions, no duplicate logical author/institution mappings, and contiguous unique affiliation order. The remaining 85 legacy qualitative positions (`first`/`middle`/`last`) and 747 implicit position fields were preserved rather than bulk rewritten. Curated validation reports zero duplicate candidates and no active-to-inactive institution errors. No public paper has all author affiliations suppressed; the exact ten unresolved authors remain visible.

Four exact consistency decisions document that the Co-Occurrence publisher's Mayachitra affiliation is not UCSB merely because its city is Santa Barbara. No unrelated Low finding was resolved. The 12 additional curated warnings are seven retained source venue IDs needing canonical venue review and five old automatic-relationship audit references without original curated mapping IDs; each removal nevertheless has explicit paper DOI, old institution, authors, and evidence. Warnings were not hidden or assigned fabricated IDs.

## Verification

- Focused author/index/order, duplicate consolidation, multi-affiliation, exporter, relevant institution identity, title normalization, and exact-baseline tests: **152 passed, 0 failed**.
- Full repository suite: **1,048 passed, 48 environment-conditional skipped, 0 failed**, 1,096 collected, 0 deselected (137.24 seconds). Local socket tests ran outside the filesystem sandbox; the earlier sandbox-only bind failure was environmental, not suppressed.
- Curated validator: 16/16 files, 0 errors, 177 warnings, 0 duplicate candidates.
- Public validator: map 0 errors / 0 warnings; papers 0 errors / 10 intentional unresolved-author warnings.
- JavaScript syntax: all 10 `web/*.js` files passed. Python compilation of `scripts` and `tests` passed.
- `git diff --check` passed.
- Browser QA through the in-app browser: SynerDetect exact nine-author order and 1/3/1,2 superscripts; Deepfake Generation's six affiliations and Vrince Vimal 5,6; Omni-Fake's Jason Li still without a speculative index; ForgeryMoE/Jian Zhao/TeleAI; Fake-GPT/China Telecom Cloud; Jilin's preserved location. Unlocated affiliations remain visible without map buttons. No console errors, no Admin saves.
- Only repository generators updated public JSON and derived reports. Downloaded PDFs, temporary scripts, and browser screenshots were kept out of the repository. No credentials or debug code added; no staging, commits, resets, restores, or discarded inherited work.

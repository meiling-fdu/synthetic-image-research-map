# Papers needing curation — completion report

Audit date: 2026-08-28. Source: the current working tree, without modifying research data.

## Current count

**207 active papers have effective `curation_status == needs_review`.**

There are 572 records in the complete Admin browser, which also retains excluded
and superseded records for inspection. All 344 curated paper rows currently say
`confirmed`. The 207 needs-review papers are public/imported records without a
curated override and with no explicit persisted curation status. The established
`normalize_curation_status` rule (also used by the editor) treats an absent/blank
status as `needs_review`. Thus **zero explicit needs-review rows in the curated
CSV is not the effective active-corpus count**.

## Source of truth and invariant

- `load_admin_data` loads public paper records, overlays curated paper metadata
  from `data/curated/papers.csv`, and normalizes effective curation status using
  `curated_schema.normalize_curation_status`. Curated confirmation wins over
  stale imported needs-review metadata; curated reopening wins over stale
  imported confirmation. Legacy import and confirmation values retain their
  existing normalization rules; unknown values still fail validation.
- Active exclusions in `data/curated/paper_exclusions.csv`, explicit inactivity
  or retired paper lifecycle/scope, and confirmed active duplicate sides from
  `data/curated/paper_version_merges.csv` remove papers from the active corpus.
  Exclusion-only audit records do not become active just because restored.
- Exact existing strong identity matching deduplicates public/curated versions.
  No fuzzy author, institution, or paper merging was added.
- `filtered_curation_papers` selects only active effective `needs_review`
  papers. Neither review status, marker evidence, high-risk flags, nor diagnostic
  categories participate. A reviewed paper can still need curation.
- `/api/dashboard` includes the full paper-summary snapshot and its
  `papers_needing_curation` projection. The client validates count, record
  identity/content, and uniqueness before replacing its Dashboard and management
  list together. Failed, incompatible, or out-of-order responses retain the
  previous complete snapshot.
- `/api/papers?curation_status=needs_review` uses the same predicate.
  Dashboard count = Dashboard complete record count = full filtered API count =
  un-narrowed Needs review management-list count.

## Dashboard and editor behavior

The dedicated card shows the authoritative total and the first five papers in
title order. Its compact table has title, year, venue, curation/review/scope
statuses, an available note, and Open/Edit. Notes are visually limited to two
lines, with full text available on hover. Zero results hide the table and show
“No papers currently need curation.”

Review clears unrelated filters, selects Curation status = Needs review, and
opens the existing paper browser with every matching record. Title and Open/Edit
use the exact paper display ID and open the existing metadata editor; no second
review system was added.

The editor and update API now honor an explicit `needs_review` choice instead
of forcing every save to `confirmed`. API patches omitting the field keep the
previous confirmation default. Successful saves await the shared snapshot
refresh; its list and count change together. No export regeneration is needed
to observe curated state changes.

## Files changed for this task

- `scripts/serve_admin.py`: effective curation/corpus fields, identity
  deduplication, filtered API, and Dashboard snapshot.
- `scripts/curated_papers.py`: honor explicit curation status on update.
- `web/admin.html`, `web/admin.css`, `web/admin.js`: compact card, preset
  filter, exact editor navigation, validated atomic refresh and save behavior.
- `tests/test_admin_papers_needing_curation.py`: effective-state/API/save tests.
- `tests/admin_action_required_frontend.cjs`: executable curation rendering,
  filter, navigation, atomic save/refresh, invalid snapshot, and zero-state tests,
  retaining the existing eight-category Action Required regressions.
- `tests/test_paper_metadata_editing.py`: await shared snapshot refresh contract.
- This report.

Other working-tree changes were preserved. Nothing was staged or committed.
The public static site still requires no custom backend; only the existing local
Admin server was extended. Restart that server and reload Admin to activate the
new response contract.

## Verification

- Focused Admin/API/frontend and metadata/curation suite: **200 passed**.
- JavaScript syntax: `web/admin.js` and
  `tests/admin_action_required_frontend.cjs` passed.
- Browser: observed the real 207 count and five-row preview; Review selected
  `needs_review`, cleared all other filters, and returned 207 of 572 Admin
  records. Clicking the first Dashboard title opened that exact title in the
  existing editor with Needs review selected. No research records were saved
  during browser inspection. The compact card was visually inspected.
- Live API audit: Dashboard = full filtered API = refreshed Dashboard, all
  **207 unique papers**, with identical complete records.
- Full suite: **1,160 passed, 49 skipped, 5 pre-existing failures** in 129 seconds.
  The failures match those documented before this task in
  `docs/admin_action_required_invariant.md`: Griffith location review status,
  unresolved geographic relationships, fixed 457-versus-458 location baseline,
  fixed 342-versus-344 curated-paper baseline, and fixed publication-type totals.
  They were not changed or suppressed.
- `git diff --check`: passed.

## All 207 titles

1. A Closer Look at Fourier Spectrum Discrepancies for CNN-Generated Images Detection — `openalex:W3147384726`
2. A GAN-based Approach to Detect AI-Generated Images — `openalex:W4386214843`
3. A Guided-Based Approach for Deepfake Detection: RGB-Depth Integration via Features Fusion — `openalex:W4393375171`
4. A Hybrid CNN-LSTM Approach for Precision Deepfake Image Detection Based on Transfer Learning — `openalex:W4395673009`
5. A Novel Deep Learning Approach for Deepfake Image Detection — `openalex:W4297988790`
6. A Novel Framework for Deepfake Image Detection Using Deep Learning Approach — `openalex:W4409047068`
7. A Novel Neural Model based Framework for Detection of GAN Generated Fake Images — `openalex:W3139320333`
8. A Review on Deepfake Image Detection Approaches, Techniques and Methods — `openalex:W4413255768`
9. A robust ensemble model for Deepfake detection of GAN-generated images on social media — `openalex:W4409526923`
10. A Single Simple Patch is All You Need for AI-generated Image Detection — `openalex:W4391555851`
11. A Survey of Deep Learning-Based Source Image Forensics — `openalex:W3010352349`
12. A Survey of Defenses Against AI-Generated Visual Media: Detection,Disruption, and Authentication — `openalex:W4400716502`
13. A Survey of Detection and Mitigation for Fake Images on Social Media Platforms — `openalex:W4387377174`
14. Adaptive Forensic Feature Refinement via Intrinsic Importance Perception — `openalex:W7155245437`
15. AdaptPrompt: Parameter-Efficient Adaptation of VLMs for Generalizable Deepfake Detection — `openalex:W7117078863`
16. Advanced Detection of AI-Generated Images Through Vision Transformers — `openalex:W4405778887`
17. Advancing AI-Generated Image Detection: Enhanced Accuracy through CNN and Vision Transformer Models with Explainable AI Insights — `openalex:W4392209962`
18. AI Generated Image Detection Using Neural Networks — `openalex:W4392457694`
19. AI-enabled image fraud in scientific publications — `openalex:W4284974950`
20. AI-Generated Image Detection using a Cross-Attention Enhanced Dual-Stream Network — `openalex:W4388820663`
21. AI-Generated Image Detection Using Semantic Feature — `openalex:W4408954780`
22. AI-Generated Image Detection With Wasserstein Distance Compression and Dynamic Aggregation — `openalex:W4402917177`
23. AI-generated Image Detection: Passive or Watermark? — `openalex:W4404649743`
24. AI-Generated-Image Detection Using Deep Learning Techniques — `openalex:W4409362694`
25. An Analysis of Recent Advances in Deepfake Image Detection in an Evolving Threat Landscape — `openalex:W4402264364`
26. An Evaluation of Deep Learning-Based Computer Generated Image Detection Approaches — `openalex:W2973074956`
27. An Eyes-Based Siamese Neural Network for the Detection of GAN-Generated Face Images — `openalex:W4284895444`
28. Analysis Survey on Deepfake detection and Recognition with Convolutional Neural Networks — `openalex:W4283712107`
29. Any-Resolution AI-Generated Image Detection by Spectral Learning — `openalex:W4413144629`
30. Are GAN Generated Images Easy to Detect? A Critical Analysis of the State-of-the-Art — `openalex:W3149674875`
31. Art or Artifact? Segmenting AI-Generated Images for Deeper Detection — `openalex:W4411979039`
32. Artifact feature purification for cross-domain detection of AI-generated images — `openalex:W4400624794`
33. Artifact: A Large-Scale Dataset With Artificial And Factual Images For Generalizable And Robust Synthetic Image Detection — `openalex:W4386590429`
34. Benchmarking Deepart Detection — `openalex:W4322760013`
35. Beyond Generation: A Diffusion-based Low-level Feature Extractor for Detecting AI-generated Images — `openalex:W4413146215`
36. BiHPF: Bilateral High-Pass Filters for Robust Deepfake Detection — `openalex:W3196551054`
37. BOSC: A Backdoor-Based Framework for Open Set Synthetic Image Attribution — `openalex:W4412624408`
38. Breaking Semantic Artifacts for Generalized AI-generated Image Detection — `openalex:W4415797310`
39. C2P-CLIP: Injecting Category Common Prompt in CLIP to Enhance Generalization in Deepfake Detection — `openalex:W4409367167`
40. Can Forensic Detectors Identify GAN Generated Images? — `openalex:W2921230249`
41. Can GPT Tell Us Why These Images Are Synthesized? Empowering Multimodal Large Language Models for Forensics — `openalex:W4411378016`
42. Cascade learning from adversarial synthetic images for accurate pupil detection — `openalex:W2903907439`
43. CNN Detection of GAN-Generated Face Images based on Cross-Band Co-occurrences Analysis — `openalex:W3044151627`
44. CNN-LSTM Model for Deepfake Image Detection — `openalex:W4406611495`
45. Code-in-the-Loop Forensics: Agentic Tool Use for Image Forgery Detection — `openalex:W4417529984`
46. Copy-Move Forgery Detection (CMFD) Using Deep Learning for Image and Video Forensics — `openalex:W3138230904`
47. Cross-Forgery Analysis of Vision Transformers and CNNs for Deepfake Image Detection — `openalex:W4283452332`
48. CSC-Net: Cross-Color Spatial Co-Occurrence Matrix Network for Detecting Synthesized Fake Images — `openalex:W4376461282`
49. Data-Independent Operator: A Training-Free Artifact Representation Extractor for Generalizable Deepfake Detection — `openalex:W4392737360`
50. DCNet: Learning Similarity and Spatial Complementary Features for Generalized AI-Generated Image Detection — `openalex:W7125581744`
51. DE-FAKE: Detection and Attribution of Fake Images Generated by Text-to-Image Generation Models — `openalex:W4388858946`
52. Deep fake detection and classification using error-level analysis and deep learning — `openalex:W4375955734`
53. Deep Fake Image Detection Based on Pairwise Learning — `openalex:W2970868842`
54. Deep Learning applied to Road Accident Detection with Transfer Learning and Synthetic Images — `openalex:W4312518338`
55. Deepfake attribution: On the source identification of artificially generated images — `openalex:W4200053273`
56. DeepFake Detection Based on Discrepancies Between Faces and Their Context — `openalex:W3173581984`
57. DeepFake Detection Improvement for Images Based on a Proposed Method for Local Binary Pattern of the Multiple-Channel Color Space — `openalex:W4367554082`
58. Deepfake detection using deep learning methods: A systematic and comprehensive review — `openalex:W4388851105`
59. Deepfake Detection Without Deepfakes: Generalization via Synthetic Frequency Patterns Injection — `openalex:W4393063559`
60. DeepFake Face Image Detection based on Improved VGG Convolutional Neural Network — `openalex:W3084142230`
61. DeepFake Image Detection — `openalex:W4394009764`
62. Deepfake Image Detection using CNNs and Transfer Learning — `openalex:W4285362588`
63. Deepfake Image Detection Using ResNet50 Model — `openalex:W4408401076`
64. Deepfake Image Detection Using Vision Transformer Models — `openalex:W4402130168`
65. Deepfake Image Detection Using Yolov8 — `openalex:W4408018363`
66. Deepfake Image Detection with Transfer Learning Models — `openalex:W4408853348`
67. Deepfakes Creation and Detection Using Deep Learning — `openalex:W3172046373`
68. DeepGuard: Identification and Attribution of AI-Generated Synthetic Images — `openalex:W4407408001`
69. DeepGuardNet: A Novel CNN Architecture for DeepFake Image Detection — `openalex:W4410253117`
70. DeepSight: Enhancing Deepfake Image Detection and Classification through Ensemble and Deep Learning Techniques — `openalex:W4402353496`
71. Detecting AI Generated Images Through Texture and Frequency Analysis of Patches — `openalex:W4407129617`
72. Detecting AI-Generated Images Using a Hybrid ResNet-SE Attention Model — `openalex:W4411926716`
73. Detecting AI-Generated Images Using Facial Similarity and Feature Extraction for Digital Security — `openalex:W4411172248`
74. Detecting AI-Generated Images Using Vision Transformers: A Robust Approach for Safeguarding Visual Media Integrity — `openalex:W4406443479`
75. Detecting AI-Generated Images via CLIP — `openalex:W4394891207`
76. Detecting AI-Generated Images via Diffusion Snap-Back Reconstruction: A Forensic Approach — `openalex:W4415936841`
77. Detecting AI-generated images with CNN and Interpretation using Explainable AI — `openalex:W4402170813`
78. Detecting and Simulating Artifacts in GAN Fake Images — `openalex:W3012472557`
79. Detecting Artificial Intelligence-Generated Images via Deep Trace Representations and Interactive Feature Fusion — `openalex:W4400616829`
80. Detecting Deepfake Images Using Deep Learning Techniques and Explainable AI Methods — `openalex:W4285791495`
81. Detecting fake images by identifying potential texture difference — `openalex:W3173631964`
82. Detecting GAN-generated synthetic images using semantic inconsistencies — `openalex:W4362684513`
83. Detecting Images Generated by Deep Diffusion Models Using Their Local Intrinsic Dimensionality — `openalex:W4390191016`
84. Detecting Multimedia Generated by Large AI Models: A Survey — `openalex:W4391563741`
85. Detecting soybean leaf disease from synthetic image using multi-feature fusion faster R-CNN — `openalex:W3135589907`
86. Detecting the Undetectable: Combining Kolmogorov-Arnold Networks and MLP for AI-Generated Image Detection — `openalex:W4402524935`
87. Detection of AI-Generated Synthetic Images with a Lightweight CNN — `openalex:W4402240806`
88. Detection of Deep-Morphed Deepfake Images to Make Robust Automatic Facial Recognition Systems — `openalex:W4214857236`
89. Detection of GAN generated image using color gradient representation — `openalex:W4381620941`
90. Detection of GAN-Generated Fake Images over Social Networks — `openalex:W2811414481`
91. Detection of GAN-Generated Images by Estimating Artifact Similarity — `openalex:W3217278836`
92. Detection of GAN-Synthesized Image Based on Discrete Wavelet Transform — `openalex:W3166640306`
93. Detection of real-time deep fakes and face forgery in video conferencing employing generative adversarial networks — `openalex:W4402013517`
94. Detection, Attribution and Localization of GAN Generated Images — `openalex:W3179128750`
95. Development of a Dual-Input Neural Model for Detecting AI-Generated Imagery — `openalex:W4399911107`
96. Diffusion Noise Feature: Accurate and Fast Generated Image Detection — `openalex:W4389421609`
97. Digital Image Forensic Analyzer to Detect AI-generated Fake Images — `openalex:W4385656076`
98. Do GANs Leave Artificial Fingerprints? — `openalex:W2907295878`
99. Does an emotional connection to art really require a human artist? Emotion and intentionality responses to AI- versus human-created art and impact on aesthetic experience — `openalex:W4384297285`
100. E2GenF: Universal AIGC Image Detection Based on Edge Enhanced Generalizable Features — `openalex:W4417166521`
101. EKILA: Synthetic Media Provenance and Attribution for Generative Art — `openalex:W4385801341`
102. Enhanced CNN Architecture with Residual Blocks and Regularization for AI-Generated Image Detection — `openalex:W4410228077`
103. Enhancing AI-Generated Image Detection with a Novel Approach and Comparative Analysis — `openalex:W4407467920`
104. Enhancing Interpretability in AI-Generated Image Detection with Genetic Programming — `openalex:W4391557868`
105. Enhancing Synthetic Generated-Images Detection Through Post-Hoc Calibration — `openalex:W4409917780`
106. Enhancing the Generalization of Synthetic Image Detection Models Through the Exploration of Features in Deep Detection Models — `openalex:W4394624427`
107. Evading Watermark based Detection of AI-Generated Content — `openalex:W4388858443`
108. Explainable Synthetic Image Detection Through Diffusion Timestep Ensembling — `openalex:W7138458380`
109. Exploring the Adversarial Robustness of CLIP for AI-generated Image Detection — `openalex:W4405845641`
110. Exposing Fake Images Generated by Text-to-Image Diffusion Models — `openalex:W4388002730`
111. Face X-Ray for More General Face Forgery Detection — `openalex:W3034196597`
112. FairAdapter: Detecting AI-generated Images with Improved Fairness — `openalex:W4408352289`
113. FakeScope: Large Multimodal Expert Model for Transparent AI-Generated Image Forensics — `openalex:W4417056138`
114. FAMSeC: A Few-Shot-Sample-Based General AI-Generated Image Detection Method — `openalex:W4405021796`
115. Few-Shot Class-Incremental Model Attribution Using Learnable Representation from CLIP-ViT Features — `openalex:W4414577086`
116. Fixed-Threshold Evaluation of a Hybrid CNN-ViT for AI-Generated Image Detection Across Photos and Art — `openalex:W7117537373`
117. Fooling the Watchers: Breaking AIGC Detectors via Semantic Prompt Attacks — `openalex:W4416610205`
118. Forensic Self-Descriptions Are All You Need for Zero-Shot Detection, Open-Set Source Attribution, and Clustering of AI-generated Images — `openalex:W4413145326`
119. Forgery-aware Adaptive Transformer for Generalizable Synthetic Image Detection — `openalex:W4402753859`
120. Fourier Spectrum Discrepancies in Deep Network Generated Images — `openalex:W2985484909`
121. FrePGAN: Robust Deepfake Detection Using Frequency-Level Perturbations — `openalex:W4221149434`
122. From Evidence to Verdict: An Agent-Based Forensic Framework for AI-Generated Image Detection — `openalex:W4415935817`
123. GAN Generated Fake Human Face Image Detection — `openalex:W4392981221`
124. GAN-Generated Image Detection With Self-Attention Mechanism Against GAN Generator Defect — `openalex:W3024207815`
125. GCS-Net: A Universal AI-Generated Visual Content Detection Method Based on CLIP — `openalex:W4410487490`
126. GenDet: Towards Good Generalizations for AI-Generated Image Detection — `openalex:W4389820666`
127. Generalizable AI-Generated Image Detection Based on Fractal Self-Similarity in the Spectrum — `openalex:W4414578321`
128. Generalized and robust model for GAN-generated image detection — `openalex:W4394935852`
129. Generating Synthetic Training Images to Detect Split Defects in Stamped Components — `openalex:W4388666300`
130. Generative Visual AI in News Organizations: Challenges, Opportunities, Perceptions, and Policies — `openalex:W4394571198`
131. GLFF: Global and Local Feature Fusion for AI-Synthesized Image Detection — `openalex:W4386590781`
132. Global Texture Enhancement for Fake Face Detection in the Wild — `openalex:W3034795015`
133. GReX-Bench: Benchmarking Generalization, Robustness, and Explainability in AI-Generated Image Detection — `openalex:W7128674854`
134. Harnessing Attention for Cropping and Fusion in CLIP-Based AIGC Detection — `openalex:W4417526972`
135. Harnessing The Power Of AI To Detect AI Generated Images — `openalex:W4410120556`
136. Harnessing the Power of Large Vision Language Models for Synthetic Image Detection — `openalex:W4393968982`
137. Hierarchical Feature Fusion and Enhanced Attention Mechanism for Robust GAN-Generated Image Detection — `openalex:W4409705469`
138. High-Resolution Network-Based Multi-Feature Fusion for Generalized Forgery Detection — `openalex:W4405895672`
139. How spammers and scammers leverage AI-generated images on Facebook for audience growth — `openalex:W4401607051`
140. HRR: Hierarchical Retrospection Refinement for Generated Image Detection — `openalex:W4415187215`
141. Image Tampering Localization Using a Dense Fully Convolutional Network — `openalex:W3140970613`
142. Improving GAN-Generated Image Detection Generalization Using Unsupervised Domain Adaptation — `openalex:W4293518933`
143. Improving Synthetically Generated Image Detection in Cross-Concept Settings — `openalex:W4367000238`
144. Incremental learning for the detection and classification of GAN-generated images — `openalex:W2978778164`
145. Interpol Review of Detection of AI-Generated Image and Video Deepfakes, 2022-2025 — `openalex:W7164742316`
146. IPD-Net: Detecting AI-Generated Images via Inter-Patch Dependencies — `openalex:W4401287425`
147. LaRE<sup>2</sup>: Latent Reconstruction Error Based Method for Diffusion-Generated Image Detection — `openalex:W4402727598`
148. LATTE: Latent Trajectory Embedding for Diffusion-Generated Image Detection — `openalex:W4415343792`
149. Learning on Gradients: Generalized Artifacts Representation for GAN-Generated Images Detection — `openalex:W4386075954`
150. Learning to Disentangle GAN Fingerprint for Fake Image Attribution — `openalex:W3169220064`
151. Leveraging Image Gradients for Robust GAN-Generated Image Detection in OSN context — `openalex:W4391306866`
152. Local frequency analysis for diffusion-generated image detection — `openalex:W4400828592`
153. LoRAX: LoRA eXpandable Networks for Continual Synthetic Image Attribution — `openalex:W4414827699`
154. LOTA: Bit-Planes Guided AI-Generated Image Detection — `openalex:W7160100074`
155. MaskGAN: A Facial Fusion Algorithm for Deepfake Image Detection — `openalex:W4360766590`
156. Mastering Deepfake Detection: A Cutting-edge Approach to Distinguish GAN and Diffusion-model Images — `openalex:W4392623241`
157. MDTL-NET: Computer-Generated Image Detection Based on Multi-Scale Deep Texture Learning — `openalex:W4391433395`
158. Methods and trends in detecting AI-generated images: A comprehensive review — `openalex:W7125199518`
159. MiraGe: Multimodal Discriminative Representation Learning for Generalizable AI-Generated Image Detection — `openalex:W4415540724`
160. Mirage: Unveiling Hidden Artifacts in Synthetic Images with Large Vision-Language Models — `openalex:W4414970554`
161. MMGANGuard: A Robust Approach for Detecting Fake Images Generated by GANs Using Multi-Model Techniques — `openalex:W4395447483`
162. MSAFNet: multi-scale self-adaptive feature fusion network for AI-generated image detection — `openalex:W4413783451`
163. Multi-modal texture fusion network for detecting AI-generated images — `openalex:W4415418960`
164. Multiclass AI-Generated Deepfake Face Detection Using Patch-Wise Deep Learning Model — `openalex:W4391110866`
165. Navigating the Challenges of AI-Generated Image Detection in the Wild: What Truly Matters? — `openalex:W4414739373`
166. No One Can Escape: A General Approach to Detect Tampered and Generated Image — `openalex:W2972023908`
167. Noise-Informed Diffusion-Generated Image Detection With Anomaly Attention — `openalex:W4410853187`
168. On the use of Benford's law to detect GAN-generated images — `openalex:W3161986877`
169. Online Detection of AI-Generated Images — `openalex:W4390189958`
170. Open Set Classification of GAN-Based Image Manipulations via a ViT-Based Hybrid Architecture — `openalex:W4385800597`
171. Optimized Frequency Collaborative Strategy Drives AI Image Detection — `openalex:W4406657393`
172. PatchCraft: Exploring Texture Patch for Efficient AI-generated Image Detection — `openalex:W4388927818`
173. Penny-Wise and Pound-Foolish in AI-Generated Image Detection — `openalex:W7128818896`
174. Raising the Bar of AI-generated Image Detection with CLIP — `openalex:W4402915983`
175. Reducing the Content Bias for AI-generated Image Detection — `openalex:W4409262730`
176. Rethinking the Up-Sampling Operations in CNN-Based Generative Network for Generalizable Deepfake Detection — `openalex:W4402716164`
177. Revealing and Classification of Deepfakes Video's Images using a Customize Convolution Neural Network Model — `openalex:W4318559723`
178. Robust CLIP-Based Detector for Exposing Diffusion Model-Generated Images — `openalex:W4402594796`
179. Scalable Fine-Grained Generated Image Classification Based on Deep Metric Learning — `openalex:W2997633607`
180. Semantic Distribution and Authenticity Discrepancy Alignment for AI-Generated Image Detection — `openalex:W7131898118`
181. Semantic-Aware Lightweight AI Model for Deepfake Image Detection in Online Retail Platforms — `openalex:W4412112598`
182. SemGIR: Semantic-Guided Image Regeneration Based Method for AI-generated Image Detection and Attribution — `openalex:W4403792090`
183. SIDA: Social Media Image Deepfake Detection, Localization and Explanation with Large Multimodal Model — `openalex:W4413144523`
184. SMNDNet for Multiple Types of Deepfake Image Detection — `openalex:W4408874542`
185. Synthetic Image Verification in the Era of Generative Artificial Intelligence: What Works and What Isn’t There yet — `openalex:W4393972628`
186. Take Fake as Real: Realistic-Like Robust Black-Box Adversarial Attack to Evade AIGC Detection — `openalex:W4405254427`
187. Testing human ability to detect ‘deepfake’ images of human faces — `openalex:W4381851764`
188. Text Modality Oriented Image Feature Extraction for Detecting Diffusion-Based DeepFake — `openalex:W4399151866`
189. Think Twice Before Detecting GAN-generated Fake Images from their Spectral Domain Imprints — `openalex:W4313042219`
190. Towards Discovery and Attribution of Open-world GAN Generated Images — `openalex:W3161417217`
191. Towards Generated Image Provenance Analysis via Conceptual-Similar-Guided-SLIP Retrieval — `openalex:W4394862914`
192. Towards Robust Gan-Generated Image Detection: A Multi-View Completion Representation — `openalex:W4385767391`
193. Towards Universal AI-Generated Image Detection by Variational Information Bottleneck Network — `openalex:W4413144713`
194. Towards Universal GAN Image Detection — `openalex:W4206030296`
195. Transferable Class-Modelling for Decentralized Source Attribution of GAN-Generated Images — `openalex:W4221166157`
196. Transferable Dual-Domain Feature Importance Attack Against AI-Generated Image Detector — `openalex:W7125951995`
197. TriFusionNet: Multi-Branch Architecture for AI-Generated Image Detection — `openalex:W7125513809`
198. Unsupervised Generative Fake Image Detector — `openalex:W4393379633`
199. VIPPrint: Validating Synthetic Image Detection and Source Linking Methods on a Large Scale Dataset of Printed Documents — `openalex:W3134971133`
200. Vision Transformer-Based Framework for AI-Generated Image Detection in Interior Design — `openalex:W4409032835`
201. Visual Veracity: Advancing AI-Generated Image Detection with Convolutional Neural Networks — `openalex:W4396886753`
202. Watch Your Up-Convolution: CNN Based Generative Deep Neural Networks Are Failing to Reproduce Spectral Distributions — `openalex:W3034864980`
203. What Is Real Anymore? A Solution to Detect Hyper Realistic AI-Generated Imagery — `openalex:W7131430408`
204. Where Did I Come From? Origin Attribution of AI-Generated Images — `openalex:W7133223677`
205. Whodunit: Detection and Attribution of Synthetic Images by Leveraging Model-specific Fingerprints — `openalex:W4399261595`
206. X-Transfer: A Transfer Learning-Based Framework for GAN-Generated Fake Image Detection — `openalex:W4402352361`
207. Zooming In on Fakes: A Novel Dataset for Localized AI-Generated Image Detection with Forgery Amplification Approach — `openalex:W7138473655`

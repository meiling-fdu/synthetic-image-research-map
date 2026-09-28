# Reversible legacy-scope exclusion migration (September 2026)

This successor migration uses only the locked 44-paper high-confidence queue from the completed legacy-scope audit. It retains every source record and applies the repository's identity-based active-exclusion layer at the public export boundary.

## Result

- Identity-locked candidates: 44 / 44
- New active exclusions: 42
- Reactivated exclusions: 1
- Already active exclusions: 0
- Blocked migrations: 1
- Public papers: 666 → 623
- Published-only papers: 555 → 514
- Mapped papers: 645 → 602
- Map markers: 1508 → 1392

## Category totals

| Category | Migrated |
|---|---:|
| watermark/provenance | 1 |
| deepfake/face/video | 40 |
| classical manipulation | 2 |

## Migration ledger

| Title | Resolved identity | Category | Identity basis | Prior state | Action | Exclusion ID | Public | Map | Receipt | Remaining issue |
|---|---|---|---|---|---|---|---|---|---|---|
| IoT-Oriented Security for Small Sensor Systems Using DnCNN Denoising and Multimodal Feature Fusion for Image Forgery Detection | curated:3ea88dc6c3224d22d416 | classical manipulation | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-ea456e71491f58989c0e28f44cbf2729 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Copy-Move Forgery Detection (CMFD) Using Deep Learning for Image and Video Forensics | doi:10.3390/jimaging7030059 | classical manipulation | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-7ac02b43ccbf5872a7a3ae0d893b1069 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Aperture: A Patch-Aware Framework for Joint Forgery Detection and Localization | curated:074bb9a77ee85d50090c | deepfake/face/video | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-6c53124e1f7954c09d1aa54937083a22 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| On Attribution of Deepfakes | curated:4b5ef3aeb56177a90939 | deepfake/face/video | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-084918571d5753c09ce1b0f9a317ba17 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Diffusion Models as a Representation Learner for Deepfake Image Detection | curated:6a0913decc4e81abddb3 | deepfake/face/video | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-227d9a482ee8519b9de38b0399e019b2 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| An Improved Dense CNN Architecture for Deepfake Image Detection | curated:80e6fc4ce64c001a2b3d | deepfake/face/video | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-8853fc167d28586ca8ea8fad0d270fa3 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| SpectraGuard: Provably-Private Deepfake Detection with Learnable Frequency-Domain Differential Privacy | curated:8227355571a6d402e4f8 | deepfake/face/video | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-2c63b2b5efce54158b98812cd590b4b1 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Comparative Analysis of Deepfake Image Detection Method Using VGG16, VGG19 and ResNet50 | curated:988373de555945528142 | deepfake/face/video | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-ef468975cb5557ad84248cd68086f317 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Enhancing Deepfake Detection with Diversified Self-Blending Images and Residuals | curated:a0c532923fe10a4ee7c0 | deepfake/face/video | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-f4ae1ceb5cdb5d9aa944500f84a8b6ce | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| The Face Deepfake Detection Challenge | curated:bbe4e9e8c5b41e467a76 | deepfake/face/video | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-801775d4ea7f5121b3cd3f2d31a7625b | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Deep Learning for Deepfakes Creation and Detection: A Survey | curated:c071c25bc2957d78569b | deepfake/face/video | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-6b0f2730deba5bdc971c66c8113375ed | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Complement Face Forensic Detection and Localization with FacialLandmarks | curated:cd18fc45f8a86a30aaf6 | deepfake/face/video | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-05c3b5617df45ad5a3d2de336d77d548 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Beyond Backbones: Degradation-Aware Prototype Fusion for Robust Deepfake Detection | curated:ce21a7aa219b08d1b81a | deepfake/face/video | paper_id | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-a7e2ece9551a54d7891fbd44c2afbf93 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| LADLE-MM: Limited Annotation Based Detector with Learned Ensembles for Multimodal Misinformation | curated:fc87c72c7e8c831652ea | deepfake/face/video | paper_id | CONFLICTING_EXCLUSION_IDENTITY | MIGRATION_CONFLICT_BLOCKED |  | NOT_SUPPRESSED_BLOCKED | NOT_SUPPRESSED_BLOCKED | NOT_REQUIRED_BLOCKED | exact normalized title/year collides with exclusion exclusion-b4edceac7e584ae58b7bda18b45b7bc1, but strong identifiers disagree |
| Deepfake detection using deep learning methods: A systematic and comprehensive review | doi:10.1002/widm.1520 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-2635537f04a351389c18484ffe66feea | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Detecting fake images by identifying potential texture difference | doi:10.1016/j.future.2021.06.043 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-27700ca45d285fedb9419d46677afbdb | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Detection of real-time deep fakes and face forgery in video conferencing employing generative adversarial networks | doi:10.1016/j.heliyon.2024.e37163 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-7b4be4e6e3cc50c48a8482750103e431 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| A Guided-Based Approach for Deepfake Detection: RGB-Depth Integration via Features Fusion | doi:10.1016/j.patrec.2024.03.025 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-88d7ee1dac3c5af4ba1dbdc873bd9f2d | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Revealing and Classification of Deepfakes Video's Images using a Customize Convolution Neural Network Model | doi:10.1016/j.procs.2023.01.237 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-194ecc71b77450369a0b6d9857b00b80 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| DeepGuardNet: A Novel CNN Architecture for DeepFake Image Detection | doi:10.1016/j.procs.2025.04.313 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-e4668477bd275654ba13c93f3d7ff50d | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Deep fake detection and classification using error-level analysis and deep learning | doi:10.1038/s41598-023-34629-3 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-bf1199c148f256298fc2b6e6fa252263 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Testing human ability to detect ‘deepfake’ images of human faces | doi:10.1093/cybsec/tyad011 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-2e0d3010993c56af8f1f134492c69e8f | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Deepfake Image Detection Using Vision Transformer Models | doi:10.1109/blackseacom61746.2024.10646310 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-c082409b8d2652758c8c4b3f20778019 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| MaskGAN: A Facial Fusion Algorithm for Deepfake Image Detection | doi:10.1109/cait56099.2022.10072275 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-6d38ec2572265eb49102c895b7749d2a | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Face X-Ray for More General Face Forgery Detection | doi:10.1109/cvpr42600.2020.00505 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-180a502c420d58529bf33632c99e2cc8 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Analysis Survey on Deepfake detection and Recognition with Convolutional Neural Networks | doi:10.1109/hora55278.2022.9799858 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-3935564de0745e4e9ba574c9f31b2ffe | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| CNN-LSTM Model for Deepfake Image Detection | doi:10.1109/idicaiei61867.2024.10842840 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-0df58eddc18c5fd984ce15d665036e23 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| GAN Generated Fake Human Face Image Detection | doi:10.1109/iitcee59897.2024.10467257 | deepfake/face/video | doi | EXISTING_INACTIVE_EXCLUSION | REACTIVATED_EXCLUSION | exclusion-b4c81bf833c64b808efdec040224d1f4 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Detection of Deep-Morphed Deepfake Images to Make Robust Automatic Facial Recognition Systems | doi:10.1109/ocit53463.2021.00039 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-a79682af30495381a1ec770e10e7dbc6 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Deepfake Image Detection Using Yolov8 | doi:10.1109/punecon63413.2024.10895706 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-863fc138d24c52828f5e11374e435122 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| DeepFake Detection Based on Discrepancies Between Faces and Their Context | doi:10.1109/tpami.2021.3093446 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-97fae1b81f0b51dbb5f91cb3c191fb5a | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| CNN Detection of GAN-Generated Face Images based on Cross-Band Co-occurrences Analysis | doi:10.1109/wifs49906.2020.9360905 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-aea7623d16c95594a12cf879d1cbc774 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Cross-Forgery Analysis of Vision Transformers and CNNs for Deepfake Image Detection | doi:10.1145/3512732.3533582 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-eeeef1e830b95066bcdcb2a9f57b11e8 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Deepfake Image Detection with Transfer Learning Models | doi:10.17798/bitlisfen.1610300 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-d9cb126d981158088834ad44c21b0ebf | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| DeepFake Detection Improvement for Images Based on a Proposed Method for Local Binary Pattern of the Multiple-Channel Color Space | doi:10.22266/ijies2023.0630.07 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-b1529b32d0db5dda9f915a1e9286461b | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| DeepFake Face Image Detection based on Improved VGG Convolutional Neural Network | doi:10.23919/ccc50068.2020.9189596 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-9879d41ce4115af9abf0b38bba16fde3 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| SMNDNet for Multiple Types of Deepfake Image Detection | doi:10.32604/cmc.2025.063141 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-8e826d4cfd9f5a9fbc70fd6412c97b7d | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Detecting Deepfake Images Using Deep Learning Techniques and Explainable AI Methods | doi:10.32604/iasc.2023.029653 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-47852c1cb3855105b48cc9752c1e5728 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| An Eyes-Based Siamese Neural Network for the Detection of GAN-Generated Face Images | doi:10.3389/frsip.2022.918725 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-5e1c14975145569c8a10036276aa86b1 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| A Novel Deep Learning Approach for Deepfake Image Detection | doi:10.3390/app12199820 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-b47752e1f396525cbb1216439758bc23 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Multiclass AI-Generated Deepfake Face Detection Using Patch-Wise Deep Learning Model | doi:10.3390/computers13010031 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-cb465407fa5c5a5ca28fad6dc38326bd | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| A Hybrid CNN-LSTM Approach for Precision Deepfake Image Detection Based on Transfer Learning | doi:10.3390/electronics13091662 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-e59a655659fd5583a491753e5872a1c0 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Semantic-Aware Lightweight AI Model for Deepfake Image Detection in Online Retail Platforms | doi:10.4018/ijswis.384517 | deepfake/face/video | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-e191652c051653ada45bae9fa4dac2c9 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |
| Evading Watermark based Detection of AI-Generated Content | doi:10.1145/3576915.3623189 | watermark/provenance | doi | NO_EXISTING_EXCLUSION | NEW_ACTIVE_EXCLUSION | exclusion-deba9d5d27ee5d978191952ca6557e44 | VERIFIED_ABSENT | VERIFIED_ABSENT | RECORDED |  |

## Reversibility and history

New exclusion rows should be restored by setting them inactive while retaining the row. The reactivated historical row must be restored from its receipt so its prior inactive state, restoration timestamp, restoration note, reason, and review note are recovered. The receipt is evidence for a future explicitly authorized restoration; it is not a parallel suppression mechanism.

The 666-paper predecessor is preserved by a hash-locked delta snapshot containing the exact 44 paper records, 117 map records, prior metadata, prior exclusion registry bytes, and hashes of every unrelated public record. Earlier systematic, Tier 1, Tier 2, HIGH, NORMAL, and legacy-audit artifacts remain byte-preserved.
Current verification compares the 4,061-entry frozen inventory through a stored-hash relationship, hashes 1,014 retained historical artifacts, and reconstructs and hashes three predecessor source files. It does not claim all inventory entries were byte-verified. Per-layer inventory counts, actual byte-comparison counts, methods, and checked artifact hashes are recorded in [historical verification](../data/processed/legacy_scope_exclusion_migration_2026_09/historical_verification.json). Frozen historical receipts describe their original runs.

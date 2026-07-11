# Public Preview Quality Report

Source: `web/data/public_preview_map_data.json`

This report describes map records, not a manually curated bibliography. One paper may produce multiple records when collaborators have multiple institutions.
Unique papers are identified by OpenAlex URL, then DOI, arXiv ID, or normalized title and year when stronger identifiers are unavailable.

## Dataset Metadata

| Field | Value |
| --- | --- |
| dataset_type | mixed_candidate_and_curated_public_preview |
| generated_from | OpenAlex candidate metadata and maintainer-confirmed curated mappings |
| warning | Contains automatically generated candidate records plus explicitly identified maintainer-confirmed curated markers. |

## Overview

| Metric | Count |
| --- | ---: |
| Map records | 878 |
| Unique papers | 404 |
| Unique institutions | 506 |
| Countries | 73 |
| arXiv/preprint records | 486 |
| Records with DOI | 863 |
| Records with venue | 808 |
| Records missing venue | 70 |
| Records missing paper URL | 0 |
| Records missing institution | 0 |
| Records missing coordinates | 0 |
| Records with `needs_review=true` | 0 |

## Records by Task

| Task | Records |
| --- | ---: |
| detection | 752 |
| source_attribution | 82 |
| detection_and_source_attribution | 44 |

## Records by Subtask

| Subtask | Records |
| --- | ---: |
| ai_generated_image_detection | 381 |
| synthetic_image_detection | 266 |
| deepfake_image_detection | 105 |
| generated_image_source_attribution | 56 |
| detection_and_source_attribution | 44 |
| source_identification | 26 |

## Records by Year

| Year | Records |
| --- | ---: |
| 2026 | 92 |
| 2025 | 274 |
| 2024 | 233 |
| 2023 | 125 |
| 2022 | 60 |
| 2021 | 38 |
| 2020 | 28 |
| 2019 | 21 |
| 2018 | 6 |
| 2017 | 1 |

## Top Venues

| Venue | Records |
| --- | ---: |
| arXiv (Cornell University) | 95 |
| ArXiv.org | 53 |
| Lecture notes in computer science | 40 |
| Proceedings of the AAAI Conference on Artificial Intelligence | 31 |
| 2025 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) | 17 |
| IEEE Access | 14 |
| Pattern Recognition Letters | 14 |
| IEEE Signal Processing Letters | 13 |
| IEEE Transactions on Information Forensics and Security | 13 |
| Applied Sciences | 12 |

## Top Countries

| Country | Records |
| --- | ---: |
| China | 189 |
| CN | 141 |
| United States | 70 |
| US | 62 |
| Italy | 43 |
| IN | 40 |
| IT | 32 |
| Germany | 20 |
| DE | 19 |
| GB | 18 |

## Top Institutions

| Institution | Records |
| --- | ---: |
| University of Naples Federico II | 16 |
| Shanghai Jiao Tong University | 14 |
| University of Siena | 14 |
| Beijing Jiaotong University | 12 |
| University of Chinese Academy of Sciences | 12 |
| Fudan University | 11 |
| City University of Hong Kong | 9 |
| Chinese Academy of Sciences | 8 |
| Information Technologies Institute | 8 |
| University of Science and Technology of China | 7 |

## Records by Resolution Confidence

| Confidence | Records |
| --- | ---: |
| high | 705 |
| medium | 173 |

## Potential quality issues

### Records missing venue

Count: **70**

- Forensic Invariant Learning for Synthetic Image Detection: Bridging Benford's Law and Topological Analysis with Machine Learning Ensembles (2026) - Comilla University; `openalex-candidate-ebe60fc6abbab654`
- FIRE: Robust Detection of Diffusion-Generated Images via Frequency-Guided Reconstruction Error (2025) - Beijing University of Posts and Telecommunications; `openalex-candidate-9fc14b2a0f7696ba`
- OpenSDI: Spotting Diffusion-Generated Images in the Open World (2025) - Xi'an Jiaotong University; `openalex-candidate-20ef2bae71c5cf78`
- Secret Lies in Color: Enhancing AI-Generated Images Detection with Color Distribution Analysis (2025) - Tencent (China); `openalex-candidate-6162788b83db1bc7`
- CO-SPY: Combining Semantic and Pixel Features to Detect Synthetic Images by AI (2025) - Purdue University West Lafayette; `openalex-candidate-000ae598a83c4cc6`
- Forensics-Bench: A Comprehensive Forgery Detection Benchmark Suite for Large Vision Language Models (2025) - University of Hong Kong; `openalex-candidate-3e36acb7cecb0f1d`
- LEGION: Learning to Ground and Explain for Synthetic Image Detection (2025) - Shanghai Jiao Tong University; `openalex-candidate-90b5060d79313344`
- Semantic Discrepancy-Aware Detector for Image Forgery Identification (2025) - Nanjing University of Science and Technology; `openalex-candidate-caad465d68fa7710`
- ForgeLens: Data-Efficient Forgery Focus for Generalizable Forgery Image Detection (2025) - Henan University of Engineering; `openalex-candidate-af86ed74fc84674b`
- CatAID: Category-Guided AI-Generated Image Detection via Vision-Language Model Adaptation (2025) - University at Buffalo, State University of New York; `openalex-candidate-348a506b67288d74`
- ExDA: Towards Universal Detection and Plug-and-Play Attribution of AI-Generated Ex-Regulatory Images (2025) - Shanghai Jiao Tong University; `openalex-candidate-071adf2c66af598a`
- Spatial-Temporal Reconstruction Error for AIGC-based Forgery Image Detection (2025) - Zhejiang University; `openalex-candidate-3a2726c50ff6a7d0`
- HFMF: Hierarchical Fusion Meets Multi-Stream Models for Deepfake Detection (2025) - Texas A&M University; `openalex-candidate-2b3de8f25296a245`
- TextureCrop: Enhancing Synthetic Image Detection Through Texture-Based Cropping (2025) - Information Technologies Institute; `openalex-candidate-6d6cebc338c382bb`
- Composite Data Augmentations for Synthetic Image Detection Against Real-World Perturbations (2025) - Aristotle University of Thessaloniki; `openalex-candidate-d451b0dc194a56c5`
- Wavelet-Packet Powered Deepfake Image Detection. (2021) - Fraunhofer-Gesellschaft; `openalex-candidate-6ba9fdeb3689ccf0`
- Light2Lie: Detecting Deepfake Images Using Physical Reflectance Laws (2026) - Technische Universität Darmstadt; `openalex-candidate-ffc5d929530a3f5f`
- "That's another doom I haven't thought about": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation (2026) - Leibniz University Hannover; `openalex-candidate-d2a030d99b35b5f8`
- Forensic Invariant Learning for Synthetic Image Detection: Bridging Benford's Law and Topological Analysis with Machine Learning Ensembles (2026) - Jahangirnagar University; `openalex-candidate-b8c048d2bb06f247`
- OpenSDI: Spotting Diffusion-Generated Images in the Open World (2025) - University of Southampton; `openalex-candidate-2e38546bdad915a5`
- OpenSDI: Spotting Diffusion-Generated Images in the Open World (2025) - Harbin Institute of Technology; `openalex-candidate-b09b2a90b0de5f28`
- Secret Lies in Color: Enhancing AI-Generated Images Detection with Color Distribution Analysis (2025) - Peking University; `openalex-candidate-c7a9ed2c288b1391`
- CO-SPY: Combining Semantic and Pixel Features to Detect Synthetic Images by AI (2025) - Sony Corporation (United States); `openalex-candidate-aa2022c6d0caa8a2`
- CO-SPY: Combining Semantic and Pixel Features to Detect Synthetic Images by AI (2025) - Rutgers Sexual and Reproductive Health and Rights; `openalex-candidate-6ba2d3f176bf7300`
- Forensics-Bench: A Comprehensive Forgery Detection Benchmark Suite for Large Vision Language Models (2025) - Institute for Advanced Study; `openalex-candidate-67df04fbd008401e`
- Forensics-Bench: A Comprehensive Forgery Detection Benchmark Suite for Large Vision Language Models (2025) - Zhejiang University; `openalex-candidate-787bf5e703e8baa7`
- Forensics-Bench: A Comprehensive Forgery Detection Benchmark Suite for Large Vision Language Models (2025) - Alibaba Group (China); `openalex-candidate-b869c4cbd105bd63`
- Forensics-Bench: A Comprehensive Forgery Detection Benchmark Suite for Large Vision Language Models (2025) - Vi Technology (United States); `openalex-candidate-f3b81a41297debcc`
- Forensics-Bench: A Comprehensive Forgery Detection Benchmark Suite for Large Vision Language Models (2025) - Megvii (China); `openalex-candidate-25018a98e35b0b3b`
- Forensics-Bench: A Comprehensive Forgery Detection Benchmark Suite for Large Vision Language Models (2025) - Zhejiang Lab; `openalex-candidate-4cf5006b59bb9f1e`
- Forensics-Bench: A Comprehensive Forgery Detection Benchmark Suite for Large Vision Language Models (2025) - ShangHai JiAi Genetics & IVF Institute; `openalex-candidate-a20705bf89a876c7`
- Forensics-Bench: A Comprehensive Forgery Detection Benchmark Suite for Large Vision Language Models (2025) - Shanghai Artificial Intelligence Laboratory; `openalex-candidate-adbae163f891d223`
- LEGION: Learning to Ground and Explain for Synthetic Image Detection (2025) - Beihang University; `openalex-candidate-14fd0a26117cf71b`
- LEGION: Learning to Ground and Explain for Synthetic Image Detection (2025) - Beijing Academy of Artificial Intelligence; `openalex-candidate-bf82bd2badee947a`
- LEGION: Learning to Ground and Explain for Synthetic Image Detection (2025) - Shanghai Artificial Intelligence Laboratory; `openalex-candidate-e0b769e76fa2e1a5`
- CatAID: Category-Guided AI-Generated Image Detection via Vision-Language Model Adaptation (2025) - Chinese Academy of Sciences; `openalex-candidate-e0b2b9196a6705c5`
- CatAID: Category-Guided AI-Generated Image Detection via Vision-Language Model Adaptation (2025) - Institute of Information Engineering; `openalex-candidate-452f2bb3c9879715`
- Spatial-Temporal Reconstruction Error for AIGC-based Forgery Image Detection (2025) - Alibaba Group (United States); `openalex-candidate-35b487cf0a750d96`
- Spatial-Temporal Reconstruction Error for AIGC-based Forgery Image Detection (2025) - Zhejiang University of Technology; `openalex-candidate-eced2038e5ce940f`
- TextureCrop: Enhancing Synthetic Image Detection Through Texture-Based Cropping (2025) - Centre for Research and Technology Hellas; `openalex-candidate-d9a6970b5514e649`
- Composite Data Augmentations for Synthetic Image Detection Against Real-World Perturbations (2025) - Centre for Research and Technology Hellas; `openalex-candidate-4a516cc1ca95d8a3`
- Wavelet-Packet Powered Deepfake Image Detection. (2021) - University of Bonn; `openalex-candidate-a66244e63c273fee`
- "That's another doom I haven't thought about": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation (2026) - Helmholtz Center for Information Security; `openalex-candidate-ff2c575fbe73b2dd`
- "That's another doom I haven't thought about": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation (2026) - Hannover Re (Germany); `openalex-candidate-2d8466e77a874e50`
- "That's another doom I haven't thought about": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation (2026) - Ruhr University Bochum; `openalex-candidate-ee0060dfde947124`
- "That's another doom I haven't thought about": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation (2026) - Max Planck Institute for Security and Privacy; `openalex-candidate-01f34db1cddbd93f`
- A Survey on Deep-Learning-Based Techniques for Detecting AI-Generated Synthetic Images (2026) - Complutense University of Madrid; `curated-map:af83a7022d551570f56c`
- Adaptive Test-Time Semantic Debiasing for AI-Generated Image Detection (2025) - University at Buffalo; `curated-map:5c099af144a9f6b6b234`
- Adaptive Test-Time Semantic Debiasing for AI-Generated Image Detection (2025) - Institute of Information Engineering, Chinese Academy of Sciences; `curated-map:44229f2cf573ad44149f`
- FLODA: Harnessing Vision-Language Models for Deepfake Assessment (2025) - Yonsei University, International Campus; `curated-map:26f32abc1c8d21b161be`
- FLODA: Harnessing Vision-Language Models for Deepfake Assessment (2025) - Hanyang University; `curated-map:ac242c76014bf1482da6`
- FLODA: Harnessing Vision-Language Models for Deepfake Assessment (2025) - Yonsei University, Sinchon Campus; `curated-map:93fd13c5c391586ba67d`
- FLODA: Harnessing Vision-Language Models for Deepfake Assessment (2025) - University of Toronto; `curated-map:c1f66b25020362a972ae`
- LAID: Lightweight AI-Generated Image Detection in Spatial and Spectral Domains (2025) - Queen's University; `curated-map:c9f7d686cfe5fe526a81`
- Simple Detection of AI-Generated Images based on Noise Correlation (2025) - University of Technology of Troyes; `curated-map:34970fefaf9f848c6bed`
- Simple Detection of AI-Generated Images based on Noise Correlation (2025) - Center for Data-Driven Science and AI, Tohoku University, Sendai, Japan; `curated-map:08ec4dbffcbfe0af24c2`
- Simple Detection of AI-Generated Images based on Noise Correlation (2025) - Université de Lille; `curated-map:1253099dae009c03dc59`
- AEROBLADE: Training-Free Detection of Latent Diffusion Images Using Autoencoder Reconstruction Error (2024) - Ruhr University Bochum; `curated-map:b7697d9eeef6b1581d40`
- CLIPping the Deception: Adapting Vision-Language Models for Universal Deepfake Detection (2024) - University of Bergen; `curated-map:f553f48c2bc3f6f9925a`
- D4: Detection of Adversarial Diffusion Deepfakes Using Disjoint Ensembles (2024) - University of Wisconsin-Madison; `curated-map:b020bec112abfdc7f845`
- D4: Detection of Adversarial Diffusion Deepfakes Using Disjoint Ensembles (2024) - University of Michigan; `curated-map:c0f651d6e27ca965e3ec`
- Did You Note My Palette? Unveiling Synthetic Images Through Color Statistics (2024) - Friedrich-Alexander-Universität Erlangen-Nürnberg; `curated-map:ca27e713b4099020e422`
- Did You Note My Palette? Unveiling Synthetic Images Through Color Statistics (2024) - University of Naples Federico II; `curated-map:01a82e06536e4e4b04f6`
- Frequency Masking for Universal Deepfake Detection (2024) - Singapore University of Technology and Design; `curated-map:9a264429d9d6fe9f88f5`
- On the Exploitation of DCT-Traces in the Generative-AI Domain (2024) - University of Catania; `curated-map:30d9fa78419fea0e6766`
- Shadows Don't Lie and Lines Can't Bend! Generative Models Don't know Projective Geometry…for Now (2024) - University of Illinois Urbana-Champaign; `curated-map:0a0fdc5a8a3277b59027`
- Shadows Don't Lie and Lines Can't Bend! Generative Models Don't know Projective Geometry…for Now (2024) - Toyota Technological Institute at Chicago; `curated-map:74fa58d8d6ebd6f0c84f`
- StealthDiffusion: Towards Evading Diffusion Forensic Detection through Diffusion Model (2024) - Xiamen University; `curated-map:44d04408ebfffce2ca15`
- Towards the Detection of Diffusion Model Deepfakes (2024) - Ruhr University Bochum; `curated-map:7eb6a019bf3f0f4fce56`
- Towards the Detection of Diffusion Model Deepfakes (2024) - CISPA Helmholtz Center for Information Security; `curated-map:c339f8bd4ffbcaada177`

### Records missing URL

Count: **0**

None.

### Records missing institution

Count: **0**

None.

### Records missing coordinates

Count: **0**

None.

### Records with unknown task

Count: **0**

None.

### Records with low or unresolved confidence

Count: **0**

None.

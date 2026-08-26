# Public Preview Quality Report

Source: `web/data/public_preview_map_data.json`

This report describes map records, not a manually curated bibliography. One paper may produce multiple records when collaborators have multiple institutions.
Unique mapped papers are identified by OpenAlex URL, then DOI, arXiv ID, or normalized title and year when stronger identifiers are unavailable.

## Dataset Metadata

| Field | Value |
| --- | --- |
| dataset_type | mixed_candidate_and_curated_public_preview |
| generated_from | OpenAlex candidate metadata and maintainer-confirmed curated mappings |
| public_preview_generated_at | 2026-08-26T11:18:11Z |
| venue_type_order | ["conference", "journal", "preprint", "book"] |
| warning | Contains automatically generated candidate records plus explicitly identified maintainer-confirmed curated markers. |

## Overview

| Metric | Count |
| --- | ---: |
| Map records | 1228 |
| Unique mapped papers | 537 |
| Unique institutions | 607 |
| Countries | 52 |
| arXiv/preprint records | 582 |
| Records with DOI | 1131 |
| Records with venue | 1217 |
| Records missing venue | 11 |
| Records missing paper URL | 0 |
| Records missing institution | 0 |
| Records missing coordinates | 0 |
| Records with `needs_review=true` | 0 |

## Records by Task

| Task | Records |
| --- | ---: |
| detection | 462 |
| source_attribution | 45 |
| detection_and_source_attribution | 30 |

## Records by Year

| Year | Records |
| --- | ---: |
| 2026 | 155 |
| 2025 | 144 |
| 2024 | 113 |
| 2023 | 51 |
| 2022 | 22 |
| 2021 | 23 |
| 2020 | 15 |
| 2019 | 11 |
| 2018 | 3 |

## Top Venues

| Venue | Records |
| --- | ---: |
| IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) | 40 |
| AAAI Conference on Artificial Intelligence (AAAI) | 23 |
| International Conference on Machine Learning (ICML) | 18 |
| Advances in Neural Information Processing Systems (NeurIPS) | 14 |
| IEEE/CVF International Conference on Computer Vision (ICCV) | 14 |
| IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) | 11 |
| IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) · Workshops | 11 |
| International Conference on Learning Representations (ICLR) | 11 |
| European Conference on Computer Vision (ECCV) | 9 |
| ACM International Conference on Multimedia (ACM MM) | 8 |

## Top Countries

| Country | Records |
| --- | ---: |
| China | 549 |
| United States | 167 |
| Italy | 95 |
| India | 63 |
| Germany | 41 |
| South Korea | 38 |
| United Kingdom | 33 |
| France | 29 |
| Singapore | 25 |
| Australia | 20 |

## Top Institutions

| Institution | Records |
| --- | ---: |
| Shanghai Jiao Tong University | 22 |
| Beijing Jiaotong University | 18 |
| University of Naples Federico II | 18 |
| University of Chinese Academy of Sciences | 17 |
| Institute of Automation, Chinese Academy of Sciences | 15 |
| University of Science and Technology of China | 15 |
| University of Siena | 15 |
| Fudan University | 14 |
| Zhejiang University | 13 |
| Centre for Research and Technology Hellas (CERTH) | 11 |

## Records by Resolution Confidence

| Confidence | Records |
| --- | ---: |
| high | 1120 |
| medium | 108 |

## Potential quality issues

### Records missing venue

Count: **11**

- EasyDeep: An IoT Friendly Robust Detection Method for GAN Generated Deepfake Images in Social Media (2022) - University of North Texas; `openalex-candidate-8f1f64353b10e2c1`
- Detection of Deepfake Images Created Using Generative Adversarial Networks: A Review (2021) - APJ Abdul Kalam Technological University; `openalex-candidate-34b247a20f8c86d1`
- Deepfake Image Detection Using Light-Weight Attention Integrated MobileNetV3 Model (2025) - Amrita Vishwa Vidyapeetham; `openalex-candidate-b95f1113154c4bf6`
- Discovering Transferable Forensic Features for CNN-Generated Images Detection (2022) - Singapore Institute of Technology; `openalex-candidate-99e15d52b1295c7d`
- Discovering Transferable Forensic Features for CNN-Generated Images Detection (2022) - University of Oslo; `openalex-candidate-fbde6235f0aade1e`
- FingerprintNet: Synthesized Fingerprints for Generated Image Detection (2022) - University of Seoul; `openalex-candidate-c12aedb83c12d14b`
- FingerprintNet: Synthesized Fingerprints for Generated Image Detection (2022) - Chung-Ang University; `openalex-candidate-f14f0331980a259f`
- AI-Generated Image Detection: Challenges and Recent Advances (2026) - University of Naples Federico II; `curated-map:dde274193da1c0814177`
- AI-Generated Image Detection: Challenges and Recent Advances (2026) - Swiss federal Institute of Technology in Lausanne; `curated-map:5c81d0cf1e05f580d116`
- AI-Generated Image Detection: Challenges and Recent Advances (2026) - Centre for Research and Technology Hellas (CERTH); `curated-map:974352335e3aeee1efcb`
- AI-Generated Image Detection: Challenges and Recent Advances (2026) - Télécom Paris; `curated-map:8c8ae50d70107c3bb13d`

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

# Public Preview Quality Report

Source: `web/data/public_preview_map_data.json`

This report describes map records, not a manually curated bibliography. One paper may produce multiple records when collaborators have multiple institutions.
Unique mapped papers are identified by OpenAlex URL, then DOI, arXiv ID, or normalized title and year when stronger identifiers are unavailable.

## Dataset Metadata

| Field | Value |
| --- | --- |
| dataset_type | mixed_candidate_and_curated_public_preview |
| generated_from | OpenAlex candidate metadata and maintainer-confirmed curated mappings |
| public_preview_generated_at | 2026-09-05T09:40:18Z |
| venue_type_order | ["conference", "journal", "preprint", "book"] |
| warning | Contains automatically generated candidate records plus explicitly identified maintainer-confirmed curated markers. |

## Overview

| Metric | Count |
| --- | ---: |
| Map records | 1403 |
| Unique mapped papers | 608 |
| Unique institutions | 616 |
| Countries | 52 |
| arXiv/preprint records | 708 |
| Records with DOI | 1179 |
| Records with venue | 1399 |
| Records missing venue | 4 |
| Records missing paper URL | 0 |
| Records missing institution | 0 |
| Records missing coordinates | 0 |
| Records with `needs_review=true` | 0 |

## Records by Task

| Task | Records |
| --- | ---: |
| detection | 572 |
| source_attribution | 77 |
| localization | 18 |

## Records by Year

| Year | Records |
| --- | ---: |
| 2026 | 207 |
| 2025 | 168 |
| 2024 | 112 |
| 2023 | 48 |
| 2022 | 22 |
| 2021 | 24 |
| 2020 | 15 |
| 2019 | 10 |
| 2018 | 2 |

## Top Venues

| Venue | Records |
| --- | ---: |
| IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) | 51 |
| AAAI Conference on Artificial Intelligence (AAAI) | 24 |
| Advances in Neural Information Processing Systems (NeurIPS) | 19 |
| International Conference on Machine Learning (ICML) | 18 |
| European Conference on Computer Vision (ECCV) | 15 |
| IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) · Workshop | 14 |
| IEEE/CVF International Conference on Computer Vision (ICCV) | 13 |
| ACM International Conference on Multimedia (ACM MM) | 12 |
| International Conference on Learning Representations (ICLR) | 12 |
| IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) | 11 |

## Top Countries

| Country | Records |
| --- | ---: |
| China | 679 |
| United States | 176 |
| Italy | 98 |
| India | 67 |
| Germany | 45 |
| South Korea | 41 |
| United Kingdom | 34 |
| Singapore | 32 |
| France | 28 |
| Australia | 27 |

## Top Institutions

| Institution | Records |
| --- | ---: |
| Shanghai Jiao Tong University | 27 |
| University of Chinese Academy of Sciences | 23 |
| Institute of Automation, Chinese Academy of Sciences | 21 |
| Beijing Jiaotong University | 20 |
| University of Naples Federico II | 19 |
| Shenzhen University | 18 |
| University of Science and Technology of China | 18 |
| Zhejiang University | 18 |
| Peking University | 15 |
| Tsinghua University | 15 |

## Records by Resolution Confidence

| Confidence | Records |
| --- | ---: |
| high | 1311 |
| medium | 92 |

## Potential quality issues

### Records missing venue

Count: **4**

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

### Records with missing or unknown tasks

Count: **6**

- TWIGMA: A Dataset of AI-Generated Images with Metadata from Twitter (2023) - Stanford University; `openalex-candidate-dae59ecf24556992`
- "That's Another Doom I Haven't Thought About": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation (2026) - Leibniz University Hannover; `openalex-candidate-d2a030d99b35b5f8`
- "That's Another Doom I Haven't Thought About": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation (2026) - CISPA Helmholtz Center for Information Security; `openalex-candidate-ff2c575fbe73b2dd`
- "That's Another Doom I Haven't Thought About": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation (2026) - Hannover Re (Germany); `openalex-candidate-2d8466e77a874e50`
- "That's Another Doom I Haven't Thought About": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation (2026) - Ruhr University Bochum; `openalex-candidate-ee0060dfde947124`
- "That's Another Doom I Haven't Thought About": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation (2026) - Max Planck Institute for Security and Privacy; `openalex-candidate-01f34db1cddbd93f`

### Records with low or unresolved confidence

Count: **0**

None.

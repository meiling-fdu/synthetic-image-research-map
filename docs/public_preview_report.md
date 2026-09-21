# Public Preview Quality Report

Source: `web/data/public_preview_map_data.json`

This report describes map records, not a manually curated bibliography. One paper may produce multiple records when collaborators have multiple institutions.
Unique mapped papers are matched to `web/data/public_preview_papers.json` using the key-paper audit's conservative DOI → arXiv → OpenAlex → exact-title matcher.

## Dataset Metadata

| Field | Value |
| --- | --- |
| dataset_type | mixed_candidate_and_curated_public_preview |
| generated_from | OpenAlex candidate metadata and maintainer-confirmed curated mappings |
| public_preview_generated_at | 2026-09-20T21:30:58Z |
| venue_type_order | ["conference", "journal", "preprint", "book"] |
| warning | Contains automatically generated candidate records plus explicitly identified maintainer-confirmed curated markers. |

## Overview

| Metric | Count |
| --- | ---: |
| Map records | 1508 |
| Unique mapped papers | 645 |
| Unique institutions | 633 |
| Countries | 52 |
| arXiv/preprint records | 782 |
| Records with DOI | 1220 |
| Records with venue | 1504 |
| Records missing venue | 4 |
| Records missing paper URL | 0 |
| Records missing institution | 0 |
| Records missing coordinates | 0 |
| Records with `needs_review=true` | 0 |

## Records by Task

| Task | Records |
| --- | ---: |
| detection | 604 |
| source_attribution | 79 |
| localization | 33 |

## Records by Year

| Year | Records |
| --- | ---: |
| 2027 | 1 |
| 2026 | 219 |
| 2025 | 186 |
| 2024 | 115 |
| 2023 | 50 |
| 2022 | 23 |
| 2021 | 23 |
| 2020 | 16 |
| 2019 | 10 |
| 2018 | 2 |

## Top Venues

| Venue | Records |
| --- | ---: |
| IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) | 53 |
| AAAI Conference on Artificial Intelligence (AAAI) | 24 |
| Advances in Neural Information Processing Systems (NeurIPS) | 23 |
| International Conference on Machine Learning (ICML) | 19 |
| European Conference on Computer Vision (ECCV) | 17 |
| International Conference on Learning Representations (ICLR) | 17 |
| IEEE/CVF International Conference on Computer Vision (ICCV) | 16 |
| IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) · Workshop | 15 |
| ACM International Conference on Multimedia (ACM MM) | 12 |
| IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) | 11 |

## Top Countries

| Country | Records |
| --- | ---: |
| China | 745 |
| United States | 194 |
| Italy | 103 |
| India | 68 |
| Germany | 46 |
| South Korea | 43 |
| United Kingdom | 36 |
| Singapore | 32 |
| France | 29 |
| Australia | 28 |

## Top Institutions

| Institution | Records |
| --- | ---: |
| Shanghai Jiao Tong University | 30 |
| University of Chinese Academy of Sciences | 23 |
| Institute of Automation, Chinese Academy of Sciences | 22 |
| Beijing Jiaotong University | 21 |
| Shenzhen University | 20 |
| University of Naples Federico II | 20 |
| University of Science and Technology of China | 20 |
| Zhejiang University | 20 |
| Tsinghua University | 18 |
| Peking University | 17 |

## Records by Resolution Confidence

| Confidence | Records |
| --- | ---: |
| high | 1416 |
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

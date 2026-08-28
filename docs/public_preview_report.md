# Public Preview Quality Report

Source: `web/data/public_preview_map_data.json`

This report describes map records, not a manually curated bibliography. One paper may produce multiple records when collaborators have multiple institutions.
Unique mapped papers are identified by OpenAlex URL, then DOI, arXiv ID, or normalized title and year when stronger identifiers are unavailable.

## Dataset Metadata

| Field | Value |
| --- | --- |
| dataset_type | mixed_candidate_and_curated_public_preview |
| generated_from | OpenAlex candidate metadata and maintainer-confirmed curated mappings |
| public_preview_generated_at | 2026-08-28T14:22:10Z |
| venue_type_order | ["conference", "journal", "preprint", "book"] |
| warning | Contains automatically generated candidate records plus explicitly identified maintainer-confirmed curated markers. |

## Overview

| Metric | Count |
| --- | ---: |
| Map records | 1233 |
| Unique mapped papers | 539 |
| Unique institutions | 610 |
| Countries | 53 |
| arXiv/preprint records | 579 |
| Records with DOI | 1136 |
| Records with venue | 1229 |
| Records missing venue | 4 |
| Records missing paper URL | 0 |
| Records missing institution | 0 |
| Records missing coordinates | 0 |
| Records with `needs_review=true` | 0 |

## Records by Task

| Task | Records |
| --- | ---: |
| detection | 464 |
| source_attribution | 45 |
| detection_and_source_attribution | 30 |

## Records by Year

| Year | Records |
| --- | ---: |
| 2026 | 157 |
| 2025 | 144 |
| 2024 | 113 |
| 2023 | 51 |
| 2022 | 22 |
| 2021 | 24 |
| 2020 | 14 |
| 2019 | 11 |
| 2018 | 3 |

## Top Venues

| Venue | Records |
| --- | ---: |
| IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) | 41 |
| AAAI Conference on Artificial Intelligence (AAAI) | 23 |
| International Conference on Machine Learning (ICML) | 18 |
| Advances in Neural Information Processing Systems (NeurIPS) | 14 |
| IEEE/CVF International Conference on Computer Vision (ICCV) | 14 |
| European Conference on Computer Vision (ECCV) | 11 |
| IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) | 11 |
| International Conference on Learning Representations (ICLR) | 11 |
| IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) · Workshops | 10 |
| ACM International Conference on Multimedia (ACM MM) | 8 |

## Top Countries

| Country | Records |
| --- | ---: |
| China | 554 |
| United States | 170 |
| Italy | 95 |
| India | 66 |
| Germany | 42 |
| South Korea | 36 |
| United Kingdom | 31 |
| France | 28 |
| Singapore | 24 |
| Australia | 21 |

## Top Institutions

| Institution | Records |
| --- | ---: |
| Shanghai Jiao Tong University | 21 |
| Beijing Jiaotong University | 18 |
| University of Naples Federico II | 18 |
| University of Chinese Academy of Sciences | 17 |
| Institute of Automation, Chinese Academy of Sciences | 16 |
| University of Science and Technology of China | 15 |
| University of Siena | 15 |
| Fudan University | 14 |
| Zhejiang University | 13 |
| Peking University | 11 |

## Records by Resolution Confidence

| Confidence | Records |
| --- | ---: |
| high | 1141 |
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

### Records with unknown task

Count: **0**

None.

### Records with low or unresolved confidence

Count: **0**

None.

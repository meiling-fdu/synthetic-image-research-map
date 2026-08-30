# Public Preview Quality Report

Source: `web/data/public_preview_map_data.json`

This report describes map records, not a manually curated bibliography. One paper may produce multiple records when collaborators have multiple institutions.
Unique mapped papers are identified by OpenAlex URL, then DOI, arXiv ID, or normalized title and year when stronger identifiers are unavailable.

## Dataset Metadata

| Field | Value |
| --- | --- |
| dataset_type | mixed_candidate_and_curated_public_preview |
| generated_from | OpenAlex candidate metadata and maintainer-confirmed curated mappings |
| public_preview_generated_at | 2026-08-30T21:11:01Z |
| venue_type_order | ["conference", "journal", "preprint", "book"] |
| warning | Contains automatically generated candidate records plus explicitly identified maintainer-confirmed curated markers. |

## Overview

| Metric | Count |
| --- | ---: |
| Map records | 1303 |
| Unique mapped papers | 569 |
| Unique institutions | 624 |
| Countries | 53 |
| arXiv/preprint records | 608 |
| Records with DOI | 1171 |
| Records with venue | 1299 |
| Records missing venue | 4 |
| Records missing paper URL | 0 |
| Records missing institution | 0 |
| Records missing coordinates | 0 |
| Records with `needs_review=true` | 0 |

## Records by Task

| Task | Records |
| --- | ---: |
| detection | 494 |
| source_attribution | 45 |
| detection_and_source_attribution | 30 |

## Records by Year

| Year | Records |
| --- | ---: |
| 2026 | 183 |
| 2025 | 149 |
| 2024 | 113 |
| 2023 | 50 |
| 2022 | 22 |
| 2021 | 24 |
| 2020 | 15 |
| 2019 | 10 |
| 2018 | 3 |

## Top Venues

| Venue | Records |
| --- | ---: |
| IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) | 50 |
| AAAI Conference on Artificial Intelligence (AAAI) | 23 |
| International Conference on Machine Learning (ICML) | 18 |
| European Conference on Computer Vision (ECCV) | 16 |
| Advances in Neural Information Processing Systems (NeurIPS) | 15 |
| IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) · Workshop | 14 |
| IEEE/CVF International Conference on Computer Vision (ICCV) | 14 |
| IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) | 11 |
| International Conference on Learning Representations (ICLR) | 11 |
| ACM International Conference on Multimedia (ACM MM) | 9 |

## Top Countries

| Country | Records |
| --- | ---: |
| China | 593 |
| United States | 176 |
| Italy | 98 |
| India | 70 |
| Germany | 45 |
| South Korea | 40 |
| United Kingdom | 31 |
| France | 28 |
| Singapore | 26 |
| Australia | 23 |

## Top Institutions

| Institution | Records |
| --- | ---: |
| Shanghai Jiao Tong University | 22 |
| Beijing Jiaotong University | 20 |
| University of Naples Federico II | 19 |
| University of Chinese Academy of Sciences | 17 |
| Institute of Automation, Chinese Academy of Sciences | 16 |
| University of Science and Technology of China | 15 |
| University of Siena | 15 |
| Fudan University | 14 |
| Zhejiang University | 14 |
| Peking University | 12 |

## Records by Resolution Confidence

| Confidence | Records |
| --- | ---: |
| high | 1211 |
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

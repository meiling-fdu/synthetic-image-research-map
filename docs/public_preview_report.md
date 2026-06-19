# Public Preview Quality Report

Source: `web/data/public_preview_map_data.json`

This report describes map records, not a manually curated bibliography. One paper may produce multiple records when collaborators have multiple institutions.
Unique papers are identified by OpenAlex URL, then DOI, arXiv ID, or normalized title and year when stronger identifiers are unavailable.

## Dataset Metadata

| Field | Value |
| --- | --- |
| dataset_type | uncurated_public_preview |
| generated_from | OpenAlex candidate metadata |
| warning | Automatically generated candidate metadata; not a manually curated bibliography. |

## Overview

| Metric | Count |
| --- | ---: |
| Map records | 264 |
| Unique papers | 131 |
| Unique institutions | 204 |
| Countries | 37 |
| arXiv/preprint records | 20 |
| Records with DOI | 261 |
| Records with venue | 262 |
| Records missing venue | 2 |
| Records missing paper URL | 0 |
| Records with `needs_review=true` | 0 |

## Records by Task

| Task | Records |
| --- | ---: |
| detection | 233 |
| detection_and_source_attribution | 19 |
| source_attribution | 12 |

## Records by Subtask

| Subtask | Records |
| --- | ---: |
| synthetic_image_detection | 112 |
| ai_generated_image_detection | 62 |
| deepfake_image_detection | 59 |
| detection_and_source_attribution | 19 |
| generated_image_source_attribution | 11 |
| source_identification | 1 |

## Records by Year

| Year | Records |
| --- | ---: |
| 2026 | 2 |
| 2025 | 74 |
| 2024 | 69 |
| 2023 | 46 |
| 2022 | 27 |
| 2021 | 20 |
| 2020 | 13 |
| 2019 | 12 |
| 2018 | 1 |

## Top Venues

| Venue | Records |
| --- | ---: |
| Lecture notes in computer science | 20 |
| 2025 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) | 12 |
| IEEE Access | 10 |
| 2025 International Joint Conference on Neural Networks (IJCNN) | 9 |
| Electronics | 7 |
| IEEE Transactions on Information Forensics and Security | 7 |
| Journal of Imaging | 7 |
| 2023 IEEE/CVF International Conference on Computer Vision (ICCV) | 6 |
| 2024 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) | 6 |
| Wiley Interdisciplinary Reviews Data Mining and Knowledge Discovery | 6 |

## Top Countries

| Country | Records |
| --- | ---: |
| CN | 57 |
| IT | 41 |
| US | 28 |
| IN | 25 |
| GB | 12 |
| DE | 10 |
| GR | 9 |
| FR | 8 |
| KR | 8 |
| TR | 7 |

## Top Institutions

| Institution | Records |
| --- | ---: |
| Federico II University Hospital | 8 |
| Information Technologies Institute | 6 |
| Beijing Jiaotong University | 5 |
| University of Siena | 5 |
| University of Catania | 4 |
| University of Naples Federico II | 4 |
| University of Science and Technology of China | 4 |
| Bank of Italy | 3 |
| Centre for Research and Technology Hellas | 3 |
| Microsoft Research Asia (China) | 3 |

## Records by Resolution Confidence

| Confidence | Records |
| --- | ---: |
| high | 264 |

## Potential quality issues

### Records missing venue

Count: **2**

- Wavelet-Packet Powered Deepfake Image Detection. (2021) - Fraunhofer-Gesellschaft; `openalex-candidate-39c8a3334849f752`
- Wavelet-Packet Powered Deepfake Image Detection. (2021) - University of Bonn; `openalex-candidate-4a2a820e836ec7a5`

### Records missing URL

Count: **0**

None.

### Records with unknown task

Count: **0**

None.

### Records with low or unresolved confidence

Count: **0**

None.

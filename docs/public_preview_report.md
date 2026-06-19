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
| Map records | 339 |
| Unique papers | 168 |
| Unique institutions | 254 |
| Countries | 42 |
| arXiv/preprint records | 25 |
| Records with DOI | 336 |
| Records with venue | 337 |
| Records missing venue | 2 |
| Records missing paper URL | 0 |
| Records missing institution | 0 |
| Records missing coordinates | 0 |
| Records with `needs_review=true` | 0 |

## Records by Task

| Task | Records |
| --- | ---: |
| detection | 300 |
| source_attribution | 20 |
| detection_and_source_attribution | 19 |

## Records by Subtask

| Subtask | Records |
| --- | ---: |
| synthetic_image_detection | 143 |
| ai_generated_image_detection | 91 |
| deepfake_image_detection | 66 |
| detection_and_source_attribution | 19 |
| generated_image_source_attribution | 19 |
| source_identification | 1 |

## Records by Year

| Year | Records |
| --- | ---: |
| 2026 | 8 |
| 2025 | 86 |
| 2024 | 93 |
| 2023 | 61 |
| 2022 | 33 |
| 2021 | 24 |
| 2020 | 15 |
| 2019 | 16 |
| 2018 | 2 |
| 2017 | 1 |

## Top Venues

| Venue | Records |
| --- | ---: |
| Lecture notes in computer science | 25 |
| 2025 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) | 14 |
| IEEE Access | 10 |
| Journal of Imaging | 10 |
| 2025 International Joint Conference on Neural Networks (IJCNN) | 9 |
| IEEE Transactions on Information Forensics and Security | 9 |
| Electronics | 7 |
| Scientific Reports | 7 |
| 2023 IEEE/CVF International Conference on Computer Vision (ICCV) | 6 |
| 2024 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) | 6 |

## Top Countries

| Country | Records |
| --- | ---: |
| CN | 73 |
| US | 51 |
| IT | 43 |
| IN | 30 |
| GB | 13 |
| DE | 12 |
| FR | 10 |
| AU | 9 |
| GR | 9 |
| KR | 9 |

## Top Institutions

| Institution | Records |
| --- | ---: |
| Federico II University Hospital | 9 |
| Beijing Jiaotong University | 6 |
| Information Technologies Institute | 6 |
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
| high | 339 |

## Potential quality issues

### Records missing venue

Count: **2**

- Wavelet-Packet Powered Deepfake Image Detection. (2021) - Fraunhofer-Gesellschaft; `openalex-candidate-39c8a3334849f752`
- Wavelet-Packet Powered Deepfake Image Detection. (2021) - University of Bonn; `openalex-candidate-4a2a820e836ec7a5`

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

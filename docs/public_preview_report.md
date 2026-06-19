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
| Map records | 407 |
| Unique papers | 196 |
| Unique institutions | 304 |
| Countries | 48 |
| arXiv/preprint records | 26 |
| Records with DOI | 404 |
| Records with venue | 405 |
| Records missing venue | 2 |
| Records missing paper URL | 0 |
| Records missing institution | 0 |
| Records missing coordinates | 0 |
| Records with `needs_review=true` | 0 |

## Records by Task

| Task | Records |
| --- | ---: |
| detection | 365 |
| source_attribution | 23 |
| detection_and_source_attribution | 19 |

## Records by Subtask

| Subtask | Records |
| --- | ---: |
| synthetic_image_detection | 169 |
| deepfake_image_detection | 99 |
| ai_generated_image_detection | 97 |
| generated_image_source_attribution | 21 |
| detection_and_source_attribution | 19 |
| source_identification | 2 |

## Records by Year

| Year | Records |
| --- | ---: |
| 2026 | 10 |
| 2025 | 104 |
| 2024 | 99 |
| 2023 | 76 |
| 2022 | 47 |
| 2021 | 30 |
| 2020 | 16 |
| 2019 | 17 |
| 2018 | 6 |
| 2017 | 1 |
| 2016 | 1 |

## Top Venues

| Venue | Records |
| --- | ---: |
| Lecture notes in computer science | 26 |
| 2025 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) | 14 |
| Applied Sciences | 12 |
| IEEE Access | 11 |
| Journal of Imaging | 10 |
| 2025 International Joint Conference on Neural Networks (IJCNN) | 9 |
| IEEE Transactions on Information Forensics and Security | 9 |
| Electronics | 7 |
| Scientific Reports | 7 |
| 2023 IEEE/CVF International Conference on Computer Vision (ICCV) | 6 |

## Top Countries

| Country | Records |
| --- | ---: |
| CN | 83 |
| US | 57 |
| IT | 46 |
| IN | 42 |
| KR | 17 |
| China | 16 |
| GB | 16 |
| DE | 13 |
| SA | 12 |
| FR | 10 |

## Top Institutions

| Institution | Records |
| --- | ---: |
| Federico II University Hospital | 10 |
| Beijing Jiaotong University | 6 |
| Information Technologies Institute | 6 |
| University of Siena | 6 |
| University of Naples Federico II | 5 |
| University of Catania | 4 |
| University of Science and Technology of China | 4 |
| Amity University | 3 |
| Bank of Italy | 3 |
| Centre for Research and Technology Hellas | 3 |

## Records by Resolution Confidence

| Confidence | Records |
| --- | ---: |
| high | 407 |

## Potential quality issues

### Records missing venue

Count: **2**

- Wavelet-Packet Powered Deepfake Image Detection. (2021) - Fraunhofer-Gesellschaft; `openalex-candidate-6ba9fdeb3689ccf0`
- Wavelet-Packet Powered Deepfake Image Detection. (2021) - University of Bonn; `openalex-candidate-a66244e63c273fee`

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

# Seven-paper ingestion — 2026-08-29

Requested **7**; added **7**, all `needs_review`; existing records updated **0**; duplicate matches found **0**. The batch contains **38 ordered authors** and **18 affiliation groups**. Five affiliation/location items remain pending and four new canonical institutions were created. No unresolved location generated coordinates or a map marker, and every sourced pending author → institution link remains visible as preliminary paper evidence.

## Requested papers

| Canonical title | Action | Verified venue / year | Track | DOI / arXiv | Authors | Affiliation groups | Pending location | Evidence |
|---|---|---|---|---|---:|---:|---|---|
| Forged Calamity: Benchmark for Cross-Domain Synthetic Disaster Detection in the Age of Diffusion | Added · `needs_review` | International Symposium on Information and Communication Technology · 2025 | Main | 10.1007/978-981-92-2600-9_17 / 2606.18554 | 12 | 5 (3 resolved, 2 pending) | University of Information Technology, Viet Nam National University Ho Chi Minh City, University of Dayton | [Source 1](https://link.springer.com/chapter/10.1007/978-981-92-2600-9_17); [Source 2](https://arxiv.org/abs/2606.18554); [Source 3](https://arxiv.org/pdf/2606.18554v1) |
| Manifold-Contrastive Few-Shot Detection for AI-Generated Images | Added · `needs_review` | International Conference on Intelligent Communications and Computing · 2026 | Main | 10.1109/icicc71012.2026.11638041 / — | 1 | 1 (1 resolved, 0 pending) | None | [Source 1](https://doi.org/10.1109/ICICC71012.2026.11638041); [Source 2](https://api.crossref.org/works/10.1109/ICICC71012.2026.11638041) |
| SpectraGuard: Provably-Private Deepfake Detection with Learnable Frequency-Domain Differential Privacy | Added · `needs_review` | IEEE Transactions on Circuits and Systems for Video Technology · 2026 | — | 10.1109/tcsvt.2026.3724270 / — | 7 | 2 (2 resolved, 0 pending) | None | [Source 1](https://doi.org/10.1109/TCSVT.2026.3724270); [Source 2](https://api.crossref.org/works/10.1109/TCSVT.2026.3724270) |
| All-Around Forgery Clues for Generalizable AI-Generated Image Detection | Added · `needs_review` | Pattern Recognition · 2026 | — | 10.1016/j.patcog.2026.114661 / — | 8 | 5 (4 resolved, 1 pending) | Dongguan University of Technology | [Source 1](https://www.sciencedirect.com/science/article/pii/S0031320326016250); [Source 2](https://doi.org/10.1016/j.patcog.2026.114661); [Source 3](https://openalex.org/W7203819382) |
| HiDD-Net: A Hierarchical Dual-Domain Distillation Network for Efficient Deepfake Detection | Added · `needs_review` | International Conference on Digital Image Processing · 2026 | Main | 10.1117/12.3119955 / — | 3 | 1 (0 resolved, 1 pending) | Beijing Institute of Technology | [Source 1](https://doi.org/10.1117/12.3119955); [Source 2](https://api.crossref.org/works/10.1117/12.3119955); [Source 3](https://openalex.org/W7203837282) |
| Anchor-Regularized Adaptation for Generalizable AI-Generated Image Detection with DINOv3 | Added · `needs_review` | ACM International Conference on Multimedia · 2026 | Main | Not established / 2608.15196 | 5 | 3 (2 resolved, 1 pending) | Secure Machines Lab Inc. | [Source 1](https://arxiv.org/abs/2608.15196); [Source 2](https://arxiv.org/pdf/2608.15196v1); [Source 3](https://dash-lab.github.io/Publication); [Source 4](https://securemachineslab.com/) |
| A Swin Transformer and CLIP-Based Framework for Generalized DeepFake Detection | Added · `needs_review` | International Conference on the Frontiers of Robotics and Software Engineering · 2025 | Main | 10.1007/978-981-95-6825-3_10 / — | 2 | 1 (1 resolved, 0 pending) | None | [Source 1](https://link.springer.com/chapter/10.1007/978-981-95-6825-3_10); [Source 2](https://doi.org/10.1007/978-981-95-6825-3_10) |

## Verification

- Forged Calamity uses the SOICT 2025 event year despite the later Springer proceedings date.
- HiDD-Net is assigned to the underlying ICDIP 2026 conference, not merely the SPIE proceedings container.
- The FRSE paper uses the 2025 event year despite delayed Springer publication metadata.
- Dashboard `needs_review`: **215 → 222**; all seven additions are present.
- Public paper export: **567 → 574**; public map export: **1262 → 1275**.
- Venue-review items for this batch: **0**. Affiliation/location-review items: **5**.
- Snapshot comparison: all 365 prior curated papers, every prior curated row, and every `data/manual/` file are unchanged. The 357 previously confirmed papers retain identical rows and review states.
- Curated and public validators pass with zero errors; public institution consistency reports zero mismatches.
- Focused affected suite: **136 passed**. Full suite: **1191 passed, 49 skipped, 24 failed** because historical static repository/location/count expectations already predate this batch; those unrelated baselines were intentionally not changed.
- No staging, commit, publishing, or deployment was performed.

# Institution type audit

Audit date: 18 July 2026

## Decision and method

The stored taxonomy remains exactly `university`, `research_unit`, `company`, and
`other`. The public and Admin label for `research_unit` is **Research
Institute**. This is a presentation change only; public JSON and CSV retain the
machine value.

All 344 rows in `data/curated/institutions.csv` were checked against existing
curated evidence, aliases, hierarchy, mappings, and locations, with official
organizational identity used for obvious high-confidence candidates. Generic
name tokens are not treated as sufficient evidence. Ambiguous cases remain
unchanged.

Counts changed from 205 universities / 107 research institutes / 30 companies /
2 other to 244 / 57 / 39 / 4. Exactly 50 rows changed type: 39 to
`university`, 9 to `company`, and 2 to `other`.

On the checked-in 488-paper public output, dynamic paper-deduplicated filter
counts changed from University 431 / Research Institute 148 / Company 40 /
Other 58 to 448 / 109 / 49 / 61. A paper can contribute once to more than one
type, so these values are not expected to sum to the paper total.

## Corrected high-confidence errors

| Institution ID | Canonical name | Old | New | Confidence | Evidence or rationale | Decision |
|---|---|---:|---:|---|---|---|
| `institution:73f449eb6a3c05d3` | Alibaba Group | `research_unit` | `company` | High | Corporate entity or corporate research division; not an independent research institution. | Corrected manually |
| `institution:9cd15ab643d7131f` | Beijing Institute of Graphic Communication | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:ffd387a3478eb9e9` | Birla Institute of Technology, Mesra | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:e822c28c6d58a829` | BITS Pilani, Goa | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:99ef70abd8f55fae` | BITS Pilani, Hyderabad | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:678fbbc18157fd45` | École Polytechnique | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:73bb0fe265f6e090` | Friedrich-Alexander-Universität Erlangen-Nürnberg | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:a76d3c97c5824bc9` | Grenoble INP | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:2b9a45614734dda3` | Hand and Upper Limb Clinic | `research_unit` | `other` | High | Clinical-care organization; neither a tertiary institution nor an independent research institute. | Corrected manually |
| `institution:fe438b1c7662476f` | Harbin Institute of Technology | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:6c5bb70e9f4b77ba` | Harbin Institute of Technology, Shenzhen | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:f5c8a9b792d3b901` | IBM Thomas J. Watson Research Center | `research_unit` | `company` | High | Corporate entity or corporate research division; not an independent research institution. | Corrected manually |
| `institution:b91c4ceb2690766e` | IIIT Delhi | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:9958d7ee1cfec4aa` | IMT School for Advanced Studies Lucca | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:4269181ef8bd7d6e` | Indian Institute of Engineering Science and Technology, Shibpur | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:f0c3da144873207a` | Indian Institute of Technology Kharagpur | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:d0b09c4ef698e8de` | Indian Institute of Technology Roorkee | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:7c73c5ea3377e7f2` | Indiana Hand to Shoulder Center | `research_unit` | `other` | High | Clinical-care organization; neither a tertiary institution nor an independent research institute. | Corrected manually |
| `institution:df7499422b3e4d82` | Indraprastha Institute of Information Technology Delhi | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:475fa3f7d32d5d27` | Institut polytechnique de Grenoble | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:a1ff6f7123083db9` | Institute of Artificial Intelligence (TeleAI), China Telecom | `research_unit` | `company` | High | Corporate entity or corporate research division; not an independent research institution. | Corrected manually |
| `institution:33f2056ddfd46aaa` | International Institute of Information Technology | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:118c2f047da4525d` | International Institute of Information Technology, Naya Raipur | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:366058c27e343874` | Massachusetts Institute of Technology | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:7b971ad17fd639eb` | Microsoft Research Asia | `research_unit` | `company` | High | Corporate entity or corporate research division; not an independent research institution. | Corrected manually |
| `institution:d4f85059258439dc` | National Institute of Technology Silchar | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:fbc0802be3266f6f` | Netflix Eyeline Studios | `research_unit` | `company` | High | Corporate entity or corporate research division; not an independent research institution. | Corrected manually |
| `institution:26db9b197bbb7634` | NSFOCUS | `research_unit` | `company` | High | Corporate entity or corporate research division; not an independent research institution. | Corrected manually |
| `institution:64f282fa6abe9403` | Peptidream (Japan) | `research_unit` | `company` | High | Corporate entity or corporate research division; not an independent research institution. | Corrected manually |
| `institution:1ee9da20656fd88b` | Politecnico di Milano | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:35caf31d5104b996` | Polytechnic Institute of Turin, Turin, Italy | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:50c86a6fc102a2c1` | Rensselaer Polytechnic Institute | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:41db7d042136daef` | Salesforce Research | `research_unit` | `company` | High | Corporate entity or corporate research division; not an independent research institution. | Corrected manually |
| `institution:f95d5af831e91b94` | SenseTime | `research_unit` | `company` | High | Corporate entity or corporate research division; not an independent research institution. | Corrected manually |
| `institution:91d1003beb3bcb91` | Skolkovo Institute of Science and Technology | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:9e5e300bb52918ca` | Technion – Israel Institute of Technology | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:386b7a411f4a3220` | Toyota Technological Institute at Chicago | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:230f59b4fb28c236` | Tsinghua Shenzhen International Graduate School | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:2e73bb336e7ad920` | Universidad Complutense de Madrid | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:14daf7f722d7d91d` | Universidade Estadual de Campinas (UNICAMP) | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:1afce89cd4f3571f` | Universitas Mercatorum | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:c76018a960d2cd12` | Université de Lille | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:6c246ba350e11d5f` | Université de Rennes | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:ef7c68d6edbab550` | Université Grenoble Alpes | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:daff50b65ce469a3` | Université Paris Cité | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:0c5e25ec47ce33fe` | Université Paris-Saclay | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:d09040aba5fecf8e` | Université Polytechnique Hauts-de-France | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:4745b20cdc6c5fb0` | Univresity of Tskuba | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:191fc14de0344472` | Virginia Tech | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |
| `institution:cb1cf39b9e67e9ec` | Vishwakarma Institute of Information Technology | `research_unit` | `university` | High | Confirmed degree-granting tertiary institution; organizational status outweighs name tokens. | Corrected manually |

Representative official evidence includes [Rensselaer’s identity as a
technological research university](https://www.rpi.edu/about),
[École Polytechnique’s higher-education and research
mission](https://www.polytechnique.edu/en/school/presentation-ecole-polytechnique),
[MIT’s education and degree programs](https://www.mit.edu/about/),
[Harbin Institute of Technology’s university
identity](https://en.hit.edu.cn/main.htm), [BITS Pilani’s university status and
campuses](https://www.bits-pilani.ac.in/contact-us/), [Politecnico di Milano’s
public-university identity](https://www.polimi.it/en/the-politecnico/about-polimi/),
[Technion’s degree-granting university identity](https://www.technion.ac.il/en/about/),
[Alibaba’s company identity](https://home.alibabagroup.com/en-US/about-alibaba),
[SenseTime’s corporate identity](https://sensetime.com/en/investor/), and
[Microsoft Research Asia’s position as Microsoft’s research
arm](https://www.microsoft.com/en-us/research/lab/microsoft-research-asia/about-us/).

## Verified existing classifications

| Institution ID | Canonical name | Old | New | Confidence | Evidence or rationale | Decision |
|---|---|---:|---:|---|---|---|
| `institution:141dbbea6bba3a37` | Everest English Boarding Secondary School | `other` | `other` | High | K–12 school; `other` is the intentional non-tertiary classification. | Verified; unchanged |
| `institution:04c73587b47761ee` | BASIS International School Nanjing | `other` | `other` | High | K–12 school; `other` is the intentional non-tertiary classification. | Verified; unchanged |
| `institution:bef37c90751e824e` | Max Planck Institute for Informatics | `research_unit` | `research_unit` | High | Independent nonprofit research institute. | Verified; unchanged |
| `institution:3afb6cc453e0a8d9` | Chinese Academy of Sciences | `research_unit` | `research_unit` | High | National research academy. | Verified; unchanged |
| `institution:1ce921cf3475aa52` | Pengcheng Laboratory | `research_unit` | `research_unit` | High | Standalone research laboratory. | Verified; unchanged |
| `institution:3e78e883c14f8bb8` | Tencent Youtu Lab | `company` | `company` | High | Corporate research division represented as part of Tencent. | Verified; unchanged |
| `institution:a5744bc50825ed1f` | WeChat Pay, Tencent | `company` | `company` | High | Tencent business entity. | Verified; unchanged |
| `institution:35e36dc1a5213fa3` | Google Research | `company` | `company` | High | Corporate research division represented as part of Google. | Verified; unchanged |

These are representative controls from the full audit, including the two
required K–12 checks, genuine independent research institutes, and corporate
entities already classified correctly.

## Ambiguous candidates requiring user review

| Institution ID | Canonical name | Old | Proposed/new | Confidence | Evidence or rationale | Decision |
|---|---|---:|---:|---|---|---|
| `institution:b145c3f748543038` | AI Foundation and Algorithm Lab | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:583e34971c9eeb5b` | Artificial Intelligence in Medicine (Canada) | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:647c89e2c8a671f8` | Association Clinique et Thérapeutique Infantile du Val de Marne | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:042deeccb5521315` | Bay Institute | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:721b1fe645c5b099` | CNIT | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:753a256f592cb1fe` | Data Assurance and Communication Security | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:04b81a56c7eb1a69` | Informatics Institute for Postgraduate Studies | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:d1f71b03766ee0a2` | Noeon Research | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:9a0d85eff850f04a` | Shanghai Innovation Institute | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:387a46732b927ccd` | Sino-Russian Research Center for Digital Economy | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:4bff7ae080547794` | TrueMedia | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:2592e804f95fa542` | TrueMedia.org | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |
| `institution:7266fd3d42f0b9ca` | Xpectrum AI | `research_unit` | `research_unit` | Low | Public identity or independence is insufficiently established from current curated evidence. | Left for review |

## Preservation checks

Only `institution_type` and `updated_at` changed on the 50 corrected
institution rows. No IDs, canonical names, aliases, hierarchy, mappings,
locations, paper records, or map records were added, removed, or renamed. The
pre-audit reference counts were 344 institutions, 50 aliases, 584 author
mappings, 256 locations, 488 public papers, and 998 public map records.

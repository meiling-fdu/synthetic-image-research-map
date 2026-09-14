# Institute of Information Engineering canonicalization audit

## Decision

- Canonical institution: `Institute of Information Engineering, Chinese Academy of Sciences`
- Canonical ID: `institution:cee70184073782c7`
- Confirmed short alias: `Institute of Information Engineering`
- Legacy deterministic short-name ID found in public data: `institution:9aae8d70d2d6eed8`
- Parent retained as a separate entity: `Chinese Academy of Sciences` (`institution:3afb6cc453e0a8d9`)

The short name is now a confirmed alias of the existing child institution. No
new canonical institution was created. The confirmed CAS hierarchy remains a
parent/child relationship, not an alias or merge.

## Root cause and observed 4-versus-5 result

The canonical registry contained only the full-name self-alias. Preliminary
OpenAlex-derived records using the short name therefore received the
deterministic name-based ID `institution:9aae8d70d2d6eed8`. Public export and
search treated that ID as distinct from the curated child ID.

Before this repair, the full-name query matched five papers:

1. Semantic Distribution and Authenticity Discrepancy Alignment for AI-Generated Image Detection
2. Adaptive Test-Time Semantic Debiasing for AI-Generated Image Detection
3. CatAID: Category-Guided AI-Generated Image Detection via Vision-Language Model Adaptation
4. ReTD: Reconstruction-Based Traceability Detection for Generated Images
5. CSC-Net: Cross-Color Spatial Co-Occurrence Matrix Network for Detecting Synthesized Fake Images

The short-name query matched four papers:

1. CatAID: Category-Guided AI-Generated Image Detection via Vision-Language Model Adaptation
2. ReTD: Reconstruction-Based Traceability Detection for Generated Images
3. CSC-Net: Cross-Color Spatial Co-Occurrence Matrix Network for Detecting Synthesized Fake Images
4. Can GPT tell us why these images are synthesized? Empowering Multimodal Large Language Models for Forensics

Three papers occurred in both sets because they carried both affiliation IDs.
The union is six papers. After canonicalization both queries resolve to the
canonical child ID and return that same six-paper union.

## Paper-level diagnosis

| Paper | Previous evidence and match | Repaired representation |
|---|---|---|
| Semantic Distribution and Authenticity Discrepancy Alignment | Full-name canonical ID only; full query only | One canonical child affiliation |
| Adaptive Test-Time Semantic Debiasing | Maintainer-curated full-name mapping only; full query only | One canonical child affiliation; remains non-preliminary |
| CatAID | Both canonical and short-name IDs; both queries | Duplicate affiliations and markers collapse to one canonical child record |
| ReTD | Both canonical and short-name IDs; both queries | Duplicate affiliations and markers collapse to one canonical child record |
| CSC-Net | Both canonical and short-name IDs; both queries | Duplicate affiliations and markers collapse to one canonical child record |
| Can GPT tell us why these images are synthesized? | Short-name ID only; short query only | Short evidence resolves to one canonical child affiliation and marker |

The preliminary flag remains on the five OpenAlex-derived paper records that
were already preliminary. Raw short/full source names are retained in
`source_institution_names`; merged evidence, authors, provenance lists, and
affiliation indices are preserved by the exporter and the defensive frontend
canonicalization pass.

## Scope check

The checked-in public baseline keeps all 488 paper records. Only the three
same-paper duplicate child markers are removed, changing map records from 1001
to 998. No unrelated marker or paper was added or removed. The child query does
not expand to sibling CAS institutes. The parent CAS query continues to expand
through the existing confirmed hierarchy rule.

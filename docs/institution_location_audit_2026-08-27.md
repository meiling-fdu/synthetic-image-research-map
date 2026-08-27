# Institution-location audit — 27 August 2026

## Scope and preserved work

Continued from the current working tree, including the user's Admin edits and the
previous author-affiliation repairs. No institution research, merges or location
creation transactions were replayed during final verification. No Low-backlog or
dormant Tier-C cleanup was performed. Nothing was staged or committed.

The independent manual audit covered **15 institutions / 16 manual location rows**:

| Exclusive outcome | Rows |
| --- | ---: |
| Preserved byte-for-byte unchanged | 7 |
| Supported coordinates preserved; city label normalized | 2 |
| Wrong site/campus corrected | 4 |
| Nirma duplicate rows consolidated, valid point preserved | 2 |
| CUHK duplicate institution merged, valid manual campus point preserved | 1 |

The seven unchanged rows are Najran, Amity, Oulu, Graphic Era Hill, NIT Karnataka,
Hindusthan Institute of Technology and UC Riverside. Imperial's city became London
and Zhejiang Sci-Tech's became Hangzhou; their coordinates did not change. Twelve
of the sixteen original coordinate pairs remain supported; only four were wrong-site
selections. This was not a rejection of the manual batch.

## Corrected relationships

| Institution | Final decision |
| --- | --- |
| Durban University of Technology | Paper-specific Durban Steve Biko campus, `-29.852922926731402, 31.005967931251714`; not Pietermaritzburg. Dense CNN retains Thokozile F. Mazibuko. |
| Graphic Era University | Correct university site, `30.2680182, 77.9961185`; Graphic Era Hill remains separate at `30.2726626, 78.0003415`. Vrince Vimal's explicit dual affiliation survives. |
| Cape Peninsula University of Technology | Bellville academic campus, `-33.9318380, 18.6421452`; the student-residence point is rejected. Paper-specific Innocent Ewean Davidson / Royi Nyameko associations survive. |
| Deakin University | Bus stop rejected; two supported campuses and exact author groups retained, as detailed below. |
| Nirma University | One logical Ahmedabad location, `23.1283839, 72.544473`, retained as `location:e90d30e3482b2158a2c7`; duplicate `location:dec1e7f84933bb0b0327` retired with a location-merge redirect. Both paper mappings survive. |
| Chinese University of Hong Kong | One canonical survivor and the user's valid campus point; LOKI's station-entrance point is no longer active. Details below. |

Six genuinely new supported sites were added: five resolved pending institutions
and Deakin Waurn Ponds. The CUHK merge also issued a new ID for an already supported
site. Seven IDs were created and three old IDs retired, giving **451 → 455** location
rows. Existing supported sites were reused; two consolidation operations eliminated
redundant records. No city-centroid, bus-stop, residence or unsupported headquarters
coordinate was accepted by this audit.

## Deakin: one institution, two campuses

For *Deep Learning for Deepfakes Creation and Detection: A Survey* (2020 deposited
version), canonical institution `institution:30e93da233b7eeef` has:

| Campus | Authors | Location |
| --- | --- | --- |
| Burwood | Thanh Thi Nguyen; Dung Tien Nguyen; Duc Thanh Nguyen | `location:c33d30d49f30b6f50b13`; `-37.8475136, 145.1149474` |
| Waurn Ponds | Cuong M. Nguyen; Saeid Nahavandi | `location:bfdefcac4b1b178d6d63`; `-38.1989397, 144.2969971` |

The canonical exporter emits both author/campus relationships. Public deduplication
now distinguishes paper × canonical institution × selected location. The Leaflet
layer also groups by institution/site, and each institution result card targets its
own marker. Paper-level institution totals and affiliation superscripts remain
institution-based: one Deakin identity, not two invented institutions. Title markup
and the institution-display helper were not changed.

Browser QA verified two separate SVG marker paths, two different location-ID targets,
the correct three-author/two-author result cards, and Waurn Ponds selecting its own
marker while Burwood remains unselected. Same-site duplicates still consolidate.

## CUHK provenance and warning semantics

- Survivor: `institution:ff4b6fb0e7e3f155`, **Chinese University of Hong Kong**.
- Merged duplicate: `institution:5396ea72656b4b19`; source name **The Chinese University
  of Hong Kong** remains an alias. Both original structured abbreviations were blank;
  no abbreviation was invented or discarded.
- Active campus: `location:08953a148518042d3bbb`, `22.4201838, 114.2079145`.
- Retired LOKI station-entrance location: `location:c64f284c57cab3a3fe18`.
- The valid source-campus ID `location:30f56beba1c5a386ad80` was re-keyed by the normal
  institution merge; original evidence remains in the audit snapshot/logs.

The curated validator deliberately emits **warnings** for historical transition
references absent from the current location table, but **errors** for active mapping
references to missing locations. Its logic was retained. A regression test proves
the distinction. The CUHK historical warning is therefore retained, not suppressed
or erased; no active mapping or public marker uses the retired station entrance.
Public-map validation itself has zero warnings.

## Pending Review: 10 → 5

Five supported resolutions were verified as fully persisted, without double-creation:

| Institution | Supported site |
| --- | --- |
| iCTLab s.r.l. | Official company/address target pin, Catania, Sicily, Italy; `37.5256898, 15.0730615` |
| Amped Software | Padriciano Building A, Trieste, Friuli-Venezia Giulia, Italy; `45.6573731, 13.8296700` |
| Mayachitra Inc. | Verified 5266 Hollister Avenue address pin, Santa Barbara postal address, California, US; `34.4357895, -119.807088` |
| SR University | Verified Ananthasagar/Hasanparthy campus, Warangal, Telangana, India; `18.0899939, 79.4685340` |
| Govind Ballabh Pant University of Agriculture and Technology | Paper-named College of Technology building, Pantnagar, Uttarakhand, India; `29.0227737, 79.4913268` |

Author, paper, raw affiliation, registry identity, full geography, location ID and
review evidence are captured in `institution_location_final_integrity_2026-08-27.json`
under `resolved_pending_persistence`. Primary sources and rejected alternatives are
in `remaining_institution_location_audit_2026-08-27.json`; cached geodata provenance
is documented under `data/raw/institution_location_audit_2026-08-27/`.

Only these five public-relevant location relationships remain unresolved:

| Institution | Exact remaining evidence gap |
| --- | --- |
| JD.com | Jawadul H. Bappy's 2019 affiliation supplies no city/country or office. Need his paper-date office; Beijing headquarters is not evidence. |
| Naval Air Warfare Center Weapons Division | Arjuna Flenner's China Lake site and official 1 Administration Circle address are supported, but an exact building/address point is not. Do not use a base centroid or Point Mugu. |
| Huya Inc. | Xiao Meng's paper specifies Guangzhou 510006; current executive-office postcode is 511446. Need the paper-date 510006 office/building, not a headquarters substitution. |
| Department of Technical Education, Uttar Pradesh | Digvijay Pandey's Kanpur directorate affiliation is supported; exact directorate building/address coordinate is unverified. City/postcode guesses are insufficient. |
| Beijing IrisKing Co., Ltd. | Jing Liu's 2024 Beijing affiliation is supported; need an authoritative 2024 office address and building point. A 2016 address and recruitment-platform footer are insufficient. |

All five retain explicit actionable reasons and blank unsupported coordinates.

Final authoritative queue: **567** total; **446 confirmed**, **77 alias-confirmed**,
**33 ignored**, **6 excluded**, **5 Pending Review / Needs Coordinates**, **0 ambiguous**.
The confirmed net change is +3, not +5, because the completed consolidations also
reclassify two rows as aliases (+2). No row was dropped to force a target count.

## Relationship completeness and public output

`scripts/report_public_relationship_location_completeness.py --check` is read-only
with respect to curated data and evaluates each paper/institution/selected-site
relationship, including mapping lineage and actual exported coordinates.

| Metric | Starting snapshot | Final |
| --- | ---: | ---: |
| Public paper records | 546 | 546 |
| Raw-map unique paper identities | 538 | 540 |
| Public papers with locations | 537 | 539 |
| Map relationships | 1,248 | 1,261 |
| Unique mapped institutions, validator semantics | 609 | 616 |
| COMPLETE relationships | 1,248 | 1,261 |
| ACTIONABLE relationships | 10 | 5 |
| Completeness ERROR | 18 | 0 |

The starting export was stale relative to the newly saved manual locations; the 18
initial report errors measure that mismatch, not unsupported manual coordinates.
Final EXCLUDED = **29** (10 active mappings under durable paper exclusions and 19
non-active identity-review candidates); NON_GEOGRAPHIC = **0**. COMPLETE retains the
existing export's validated automatic-location semantics; it does not claim a new
independent research audit of every historic automatic coordinate.

No paper was removed. The shrinkage guard explains all eight semantic removals from
the original snapshot through current curated mapping/merge evidence, with **zero
unexplained shrinkage** and no baseline override. Additional same-relationship
coordinate corrections are recorded explicitly. Eleven exact legacy-marker
replacement events and 21 explicit location bindings prevent stale automatic markers
from coexisting with the audited sites; no fuzzy author or institution-wide deletion
rule was introduced.

## Integrity and author preservation

The final integrity snapshot records zero lost active author/institution links after
the CUHK ID redirect, zero active references to merged/ignored identities, zero
duplicate active mapping keys or location IDs/logical locations, zero alias collisions,
zero malformed CSV rows/coordinates, and zero canonical `Türkiye` values.

The previous 37 author-link repairs and explicit multi-affiliations remain intact.
ForgeryMoE/Jian Zhao's current TeleAI mapping is identical to the starting snapshot.
The repeated exporter detail-pass and contiguous author-affiliation ordering tests
pass. A separate current Admin confirmation of Jiguang Zhang's Fake-GPT mapping is
preserved; it accounts for the active-link total increasing from 2,189 to 2,190 and
is not attributed to this location audit. Ten existing public author warnings remain.

## Verification

- Original targeted frontend/chart/completeness batch: 57 passed, 0 failed.
- Broad focused location/geocoding/multi-site/merge/export/author/frontend matrix:
  327 passed, 0 skipped, 0 failed before the final marker-layer refinement.
- Final marker/interaction/completeness/manual/provenance batch: 122 passed, 0 failed.
- Final receipt/baseline/manual/completeness recheck: 41 passed, 0 skipped, 0 failed.
- Final full-suite result: **1,129 passed, 0 skipped, 0 failed** (148.84 seconds;
  repeated after updating the baseline verification receipt).
- Curated validator: 16/16 files, 0 errors, 178 warnings, 0 duplicate candidates.
- Public map: 0 errors, 0 warnings. Public papers: 0 errors, 10 existing author warnings.
- Relationship report: 0 errors. Missing-coordinate audit: 0 invariant violations.
- Institution consistency: 0 High / 0 Medium; 173 Low findings retained, not processed.
- All 10 `web/*.js` syntax checks and Python compilation of `scripts/` and `tests/` pass.
- `git diff --check` passes. No new PDF, browser artifact, credential or debug file was
  added. Large generated JSON diffs were checked semantically with relationship,
  identity and shrinkage invariants; they were produced by the canonical exporter.

Browser checks used the browser skill against the static public site and existing
local Admin server. Corrected Deakin, Durban, CPUT, Graphic Era, Nirma and CUHK records
and iCTLab/Amped were exercised. No QA edits were saved. The final Admin queue showed
exactly the five remaining pending institutions, with the five resolved institutions
absent. JD.com and Huya were opened: their exact paper-date evidence gaps were visible,
both latitude/longitude fields remained blank, and both stayed actionable. Public
paper cards explicitly disabled the JD.com, naval and Huya marker links; their
papers retained only supported markers. Both Deakin campus buttons selected their
own distinct marker. Public and Admin browser consoles reported **0 errors and
0 warnings**.

The final diff audit distinguished existing CSV line-ending normalization from
semantic changes; hierarchy and search-relationship CSVs have no semantic diff
against HEAD. Existing manual reports and the user's venue/Admin decisions were
preserved. No additional formatting cleanup or public export was run during this
final verification pass.

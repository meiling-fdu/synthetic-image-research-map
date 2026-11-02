# P231 independent track semantics review

**Verdict: ACCEPT**, limited to `venue_track=Main` as the repository-normalized regular paper role **within standalone MAD**. Preserve `venue:mad`, the full ACM International Workshop on Multimedia AI against Disinformation name, acronym MAD, conference type and original proceedings provenance. This is a recommendation; no formal decision or repository change was applied.

The captured official MAD program places the exact title and four ordered authors in ordinary Session 2 (14:30–15:30). It does not literally call the track “Main” or “regular-paper track.” Its header says MAD is organized with ICMR; that is host-event context, not an ICMR main publication assertion. The acceptance inference is ordinary paper-session role → normalized Main at MAD.

The active schema and runtime make that bounded interpretation precise. `venue_tracks.py` defines a controlled paper-level vocabulary independent of source titles; `materialize_canonical_venue_metadata` explicitly separates paper track from registry-owned venue identity and defaults missing conference tracks to Main. Both public formatters omit Main from the human venue label. Thus the public presentation remains “ACM International Workshop on Multimedia AI against Disinformation (MAD).” The program need not be misquoted as having an official Main label.

The P231 counterfactual passed through structured Python selection, the effective venue audit, and the actual JavaScript public venue/detail/filter/CSV functions in memory. Details display “Conference | ACM International Workshop on Multimedia AI against Disinformation (MAD) · 2026.” The filter key remains `venue:mad`, with “MAD — All Tracks” when mixed with the unchanged MAD papers. ICMR remains a separate option at `venue:icmr`. CSV fields explicitly pair `venue_track=Main` with MAD’s full name and canonical ID; this is controlled normalized metadata, not a field claiming a literal official track.

`docs/data_schema.md:164–168,224–226` retains conflicting legacy wording about lowercase enums, workshop identity encoded as workshops, and tracks in venue IDs. This documentation inconsistency was considered explicitly. The executable schema, current materialization, dedicated workshop-role documentation and regression tests establish the active independent-paper-track semantics. No documentation or frontend fix is required to make this bounded P231 change faithful, and none was made.

R231 remains independent and unchanged: the program cannot establish NESS dataset or benchmark contribution. No scientific re-review, new retrieval, authoritative write, frontend change, or B3 evidence modification occurred.

30 unique existing tests passed. The first run had 26 pass and 4 Node-dependent skips; all 4 passed after the bundled Node runtime was added to PATH. The P231-specific counterfactual runtime probe passed. Repository status was clean before and after. This is function-level runtime verification with a minimal DOM fixture, not a screenshot/browser audit.

## Exact provenance

Each source is hashed in the companion JSON, with verbatim bounded excerpts and one-based line ranges.

- `program` — [P231-official-program.html](/Users/meilinger/.codex/visualizations/2026/10/02/01a0fd3f-53f2-7811-a204-a10941e224b5/batch-b-b3-03-2026-10-31/evidence/root/P231-official-program.html:188), lines 188–189, 210–216, 278–294. The captured official page identifies the MAD workshop, organized with ICMR. The exact title and four ordered authors occur under ordinary Session 2 at 14:30–15:30. There is no named Main track here; regular paper placement is a role inference from the research-paper session list.

- `b3` — [P231.json](/Users/meilinger/.codex/visualizations/2026/10/02/01a0fd3f-53f2-7811-a204-a10941e224b5/batch-b-b3-03-2026-10-31/per_paper/P231.json:112), lines 112–131, 133–168. B3 proposes only Workshop→Main at the unchanged standalone MAD venue, labels it repository normalization, retains the no-literal-Main caveat, and separates it from R231.

- `qc` — [independent_scientific_QC.json](/Users/meilinger/.codex/visualizations/2026/10/02/01a0fd3f-53f2-7811-a204-a10941e224b5/batch-b-b3-03-2026-10-31/qc/independent_scientific_QC.json:358), lines 358–373. QC explicitly permits only a qualified regular-session→Main normalization within MAD; forbids ICMR-main and official quoted Main claims, automatic name inference and canonical venue replacement.

- `v1` — [batch_c_policy_decisions.json](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json:181), lines 181–197. Locked V1 separates archival venue, event/container information and paper track; it alone does not prove P231 track placement.

- `track_vocab` — [venue_tracks.py](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/scripts/venue_tracks.py:1), lines 1–23. Main belongs to the controlled, normalized paper-level vocabulary independent of source titles. main track is an input alias, not a statement that a primary source used that phrase.

- `active_schema` — [curated_schema.py](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/scripts/curated_schema.py:386), lines 386–391. The active schema imports the shared controlled track vocabulary and normalizer.

- `materialization` — [venues.py](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/scripts/venues.py:274), lines 274–310. Confirmed venue ID supplies name/acronym/type; track stays paper-level and missing conference tracks default to Main. Literal source labeling is therefore not what the normalized Main enum means.

- `inference_default` — [venues.py](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/scripts/venues.py:612), lines 612–632, 758–773. Main is the default paper role after recognized specific roles; exact standalone identity wins. This explains semantics only and is not used as sufficient evidence for changing an existing disputed track.

- `selection` — [curated_papers.py](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/scripts/curated_papers.py:290), lines 290–307, 330–342, 354–370. Structured Main selection validates separately from canonical venue, retains historical raw provenance and rebuilds display label.

- `python_display` — [venues.py](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/scripts/venues.py:106), lines 106–121. Public/export label is full canonical venue plus acronym; Main is suppressed and Workshop in the full venue name remains intact.

- `audit` — [venue_audit.py](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/scripts/venue_audit.py:142), lines 142–145, 313–319, 343–372. The comment explicitly distinguishes primary standalone event from nested paper track; preserved observations stop automatic reassignment. An explicit reviewed paper track is separate and display is rebuilt.

- `public_display` — [app.js](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/web/app.js:1770), lines 1770–1845. Public JavaScript keeps canonical name, ID and normalized paper track separate. The fallback label omits Main and exported venue_label is respected. A Conference type label is a schema type, while the full MAD Workshop name remains visible.

- `public_details` — [app.js](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/web/app.js:4048), lines 4048–4073, 5320–5326. Actual paper details and institution-paper rows consume venueDisplayLabel, preserving the bounded MAD venue name.

- `public_details_helper` — [paper_details_helpers.js](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/web/paper_details_helpers.js:83), lines 83–96. Publication metadata formats supplied full venue and publication type; it does not upgrade it to a host conference.

- `public_filters` — [app.js](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/web/app.js:6148), lines 6148–6195. Venue options are keyed by canonical venue ID, aggregate paper tracks within that venue, and show All Tracks when the normalized tracks differ. Main cannot select ICMR through this path.

- `csv` — [app.js](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/web/app.js:410), lines 410–421, 446–456. Both CSV exports pair the normalized Main track with the explicit MAD ID, name, acronym and display label; neither field is called an official track quote.

- `map_export` — [curated_export.py](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/scripts/curated_export.py:1100), lines 1100–1106. Map export copies the explicit canonical venue identity, paper track and original raw venue separately.

- `norm_docs` — [publication_venue_normalization.md](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/docs/publication_venue_normalization.md:12), lines 12, 20–24, 62–68. Dedicated workshop-role documentation separates canonical identity from track, declares the active singular vocabulary, protects historical assignments until manual review, and synchronizes public surfaces.

- `workshop_docs` — [workshop_venue_audit_report.md](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/docs/workshop_venue_audit_report.md:30), lines 30–32, 42–44, 61. The dedicated report specifically retains MAD as an independent identity and calls for paper/program verification before explicit Main or nested Workshop confirmation; P231 appears on that review list.

- `legacy_doc_conflict` — [data_schema.md](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/docs/data_schema.md:164), lines 164–169, 224–226. These paragraphs retain conflicting legacy lowercase enums and track-bearing venue IDs, including workshop identity encoded via workshops. They do not describe active runtime semantics: active schema import, explicit materialization, dedicated workshop docs and executable tests use independent paper tracks and stable venue IDs. No doc edit is part of this review.

- `existing_public` — [public_preview_papers.json](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/web/data/public_preview_papers.json:102126), lines 102126–102138. Before any change the public P231 record already shows the full MAD workshop name and canonical venue:mad, while retaining Workshop and a separate raw proceedings title.

- `test_schema` — [test_paper_level_venue_track.py](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/tests/test_paper_level_venue_track.py:27), lines 27–48, 59–78. Tests explicitly assert shared venue identity for Main/Workshop, Main omission from the public label, default Main and alias-hint separation.

- `test_workshop` — [test_workshop_venue_audit.py](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/tests/test_workshop_venue_audit.py:55), lines 55–93, 119–128. Tests explicitly cover independent standalone MAD identity, conservative retention of disputed Workshop and explicit later track review; the review does not rely on name-only Main inference.

- `test_frontend` — [test_frontend_venue_filters.py](/Users/meilinger/.codex/worktrees/batch-b-b3-03/synthetic-image-research-map/tests/test_frontend_venue_filters.py:285), lines 285–324, 421–429, 500–543. Frontend coverage checks track/type distinction, canonical ID filter identity, All Tracks aggregation and explicit CSV venue fields.

## Verification artifacts

[Counterfactual results](P231_semantics_probe_results.json), [reproducible probe](P231_semantics_probe.py), [initial test log](P231_tests_initial.log), [Node rerun log](P231_tests_node_rerun.log).

Baseline: `d109c70f6994906ec3d9197baad51cf9d8e51f7c`. All outputs reside outside the repository. Root may apply only the qualified Workshop→Main decision in the later formal B4 worktree.

# Local Admin Workflow

This runbook covers routine maintenance through the localhost admin browser. Run all commands from the repository root. The admin tools update local curated CSVs and generated preview files; they never stage, commit, push, or publish changes.

## Start a maintenance session

1. Check the working tree so existing changes are understood:

   ```bash
   git status --short
   ```

2. Start the local admin server:

   ```bash
   python3 scripts/serve_admin.py
   ```

3. Open the tokenized `http://127.0.0.1:8765/admin/?token=...` URL printed in the terminal. Keep the server on loopback and treat the token as temporary local access.
4. When finished, stop the server with `Ctrl-C`.

## Add Paper

1. Choose **Add Paper** and search by title, DOI, arXiv ID, or paper URL.
2. Select the correct OpenAlex result and verify every prefilled field. If no result is correct, use **Add manually instead**.
3. Confirm the task, optional subtask, provenance, links, and review note before saving.
4. Select the saved paper and add its author–institution mappings separately.

The paper record is written to `data/curated/papers.csv`. Saving a paper does not create affiliations, coordinates, map markers, or generated preview JSON.

## Delete / Scope Review

1. Select the paper and choose **Delete / Exclude from site**.
2. Select the most specific reason and record a review note that explains the decision.
3. Use **Restore** if the scope decision is later reversed.

This creates or updates an auditable decision in `data/curated/paper_exclusions.csv`; it does not delete source or processed metadata. The exclusion reaches the public preview only after a full refresh.

## Author–Institution Mappings

1. Select a paper and review **Current exported/public evidence** for context.
2. Under **Author–Institution Mappings**, add or edit one row for each supported institution.
3. Record the canonical institution name, every author associated with it, the raw affiliation or evidence, mapping status, and a review note.
4. Use **Replace all mappings** only when intentionally superseding all active mappings; prior rows remain in the audit history.

Mappings are written to `data/curated/author_institution_mappings.csv`. Do not assign the whole paper to the first author's institution. Missing or ambiguous institution coordinates are handled in the separate location-review queue.

## Institution Location Review

1. Choose **Institution Location Review** and select a queued institution.
2. Verify the institution and coordinates against a reliable source.
3. Enter the location labels, uppercase two-letter country code, latitude, longitude, source or source URL, and a review note.
4. Confirm the location, or mark the row **ambiguous** or **unresolved** when the evidence is insufficient.

Confirmed coordinates are written to `data/curated/institution_locations.csv`, and the corresponding row in `data/curated/institution_location_review.csv` is updated. Never guess coordinates or resolve ambiguity merely to create a marker.

## Run the full refresh pipeline

After curation changes, choose **Run full refresh pipeline**. It runs, in order:

```text
python3 scripts/validate_curated_database.py
python3 scripts/validate_paper_exclusions.py
python3 scripts/export_public_preview.py
python3 scripts/validate_public_preview.py
python3 scripts/audit_key_paper_coverage.py
python3 scripts/diagnose_paper_marker_blockers.py
```

The pipeline stops at the first failure. Read the command log, correct the underlying curated record, and run it again. **Reload preview data** only rereads existing JSON; it does not export changes.

After a successful refresh:

1. Inspect the changed-file list and command log.
2. Review `git status --short` and the relevant diffs, especially curated CSVs and `web/data/public_preview_*.json`.
3. Check that paper coverage, mappings, exclusions, and markers match the intended decisions.
4. Commit and push separately only after review. GitHub Pages is unchanged until that manual publication step.


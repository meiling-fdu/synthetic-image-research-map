# Admin location confirmation fix audit

Date: 2026-07-29

## Original reproduction

The canonical institution location editor submitted `institution_id` and
`loaded_institution_id` in the body of `POST /api/institution/location`.
Changing either mutable editor value, including through stale selection state,
caused the backend identity guard to return HTTP 400 even when the user intended
only to confirm coordinates. The failure contract was reproduced through the
Admin handler by submitting the loaded canonical record with a different body
ID. Before this change, location persistence depended on two body IDs agreeing.

## Root cause

The location operation reused an institution-management endpoint whose request
contract carried institution identity in mutable form state. The frontend
serialized the hidden form ID and separately copied selected state into
`loaded_institution_id`; the backend compared both body fields before updating
the location. This made stale or diverged editor state look like an attempted
identity change. Display-name and geocoder lookup were not the persistence
target, but the body-ID contract made that separation unnecessarily fragile.

## Changed implementation

- `web/admin.js` binds confirmation to the immutable canonical ID captured when
  the editor is loaded and calls
  `POST /api/admin/institutions/<institution_id>/confirm-location`.
- `scripts/serve_admin.py` treats the decoded path ID as authoritative. An
  inactive or merged ID returns HTTP 409 with `inactive_institution` and the
  active canonical ID when a reviewed merge supplies one.
- `scripts/curated_institutions.py` accepts location fields only, requires any
  compatibility body ID to exactly match the path ID, requires an active
  canonical record, validates coordinates, and never resolves the target by
  display name or alias.
- `scripts/curated_schema.py` defines a separate location-audit schema.
- `data/curated/institution_location_audit_log.csv` is the durable,
  location-only evidence store. No existing curated record was changed.

Old canonical contract:

`POST /api/institution/location` with `institution_id` and
`loaded_institution_id` in the body.

New canonical contract:

`POST /api/admin/institutions/<institution_id>/confirm-location` with city,
region, country, country code, latitude, longitude, coordinate source,
coordinate source URL, status, review note, and reviewer metadata only.

## Preserved invariants

- Location confirmation never changes `institution_id`.
- It never rewrites author–institution mappings, aliases, merges, or identity
  audit evidence.
- Alias and merge resolution can load an active record, but confirmation does
  not silently redirect an inactive path ID.
- The two Chinese/US Northeastern University records remain distinct by ID.
- The merged UBC ID `institution:05b67f44dd9f6846` cannot receive a location
  update; the active reviewed ID remains `institution:94efe2a875dd4d0e`.
- Existing identity-change validation and reviewed mapping replacements remain
  separate.

## Evidence

Each success appends `location_confirmed` or `location_replaced` evidence with
the institution ID, previous and confirmed coordinates, previous and confirmed
address fields, coordinate source and URL, review note, reviewer, and timestamp.
The evidence is stored outside `institution_audit_log.csv`, so it cannot satisfy
institution/mapping replacement shrinkage guards.

## Regression coverage

Focused tests cover creation, unchanged confirmation, coordinate/address
replacement, mapping and identity-audit preservation, body/path mismatch,
unsupported identity fields, active-only enforcement, invalid coordinates,
duplicate-submit UI locking, canonical refresh, same-name Northeastern
separation, merged UBC rejection, merged-ID HTTP 409, and the original HTTP 400
contract. Existing identity/canonicalization, mapping, and shrinkage suites were
also run.

## Validation results

- Focused location/backend/frontend tests: passed.
- Admin loopback route tests: passed.
- Full pytest suite: 702 passed, 20 skipped; two unrelated pre-existing
  repository-baseline failures remain because public map relationships are
  1,080 while the checked-in expectation is 1,077.
- JavaScript syntax, Python compilation, and `git diff --check`: passed.
- Curated validation: passed with 0 errors (existing warnings remain).
- Public preview validation: passed with 0 errors.

## Manual UI verification

The Admin application was run against temporary copies of curated files. The
two same-name Northeastern University rows appeared separately. The US record
`institution:ff1a1bc95dbe91a8` was opened, its existing Boston coordinates were
confirmed, and the request returned success. After automatic refresh, the same
ID, address, and coordinates remained selected and the button was re-enabled.
Exactly one `location_confirmed` evidence row was written. Temporary mappings
and the identity audit remained byte-identical to the authoritative originals.

## Remaining edge cases

The legacy `/api/institution/location` route remains for compatibility and
retains strict body-ID checks. The Admin UI no longer uses it. The unrelated
public relationship baseline mismatch should be reviewed separately.

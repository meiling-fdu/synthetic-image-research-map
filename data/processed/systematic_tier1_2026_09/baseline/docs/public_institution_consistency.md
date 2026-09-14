# Curated/public institution consistency

## Authority rule

For a paper with accepted affiliation curation, the complete set of effective
`mapping_status=active` author–institution mappings is authoritative. This applies
to paper details, marker details, institution summaries, and institution search
IDs. Every active multi-affiliation remains visible, including affiliations
without publishable coordinates. Those affiliations do not manufacture map pins.

Excluded, inactive, and superseded mapping history does not contribute active
affiliations. A history-only paper remains reviewed-empty. Candidate-only
(`needs_review`) and unreviewed papers retain the existing automatic fallback
policy. Paper exclusions and rejected-location rules remain unchanged.

## Root cause

The exporter already selected curated mappings early in integration. Its later
`preserve_map_relationships_after_integration` step restored historical public
markers, however. The older supersession resolver required matching *complete*
author sets or an exact transition audit. For the Diffusion Epistemic paper,
historical Microsoft markers named only Qi Xiong, while the active Tencent
mapping names Yingsong Huang, Hui Guo, and Qi Xiong. The sets did not match.

`add_public_detail_fields` then unioned restored markers and their stale derived
affiliation arrays into every record for the paper. Author-source priority did
not remove the extra paper-level institutions. Separately, re-hashing curated
institution names, coordinate-derived IDs, and alias redirects could override
explicit curated IDs (notably Tencent Youtu Lab and Amazon AI).

The fix applies one shared paper-wide removal policy to preservation, final
selection, and the shrinkage guard. The detail builder seeds a closed set from
the effective mappings and permits only non-author enrichment of those IDs.
Explicit active institution IDs survive name/coordinate/alias processing.
Browser-side normalization joins author metadata by ID and retains coordinate-less
affiliations in summaries; there are no title-specific frontend conditions.

## Audit results (2026-08-28 working tree)

- 546 public papers inspected: 369 curated and 177 unreviewed.
- Before repair: 11 papers had differing institution sets; 28 papers had at least
  one mismatch across affiliation membership, author assignments, preserved
  markers, or coordinate-less summaries.
- After repair: zero mismatches across the 369 curated papers and their public
  markers. No papers were removed. Public map rows changed from 1,265 to 1,233.
- Both public JSON artifacts were regenerated from existing local inputs. No
  curated/manual CSV was changed by this repair and no new geocoding was used.

The 11 institution-set cases were RealNet; Diffusion Epistemic Uncertainty;
Robust AI-Synthesized Image Detection via Multi-Feature Frequency-Aware Learning;
VCT2; Unmasking AI-Created Visual Content; WILD; Addressing Diffusion Model Based
Counter-Forensic Image Manipulation; LaRE2; FingerprintNet; Detection of Deepfake
Images Created Using Generative Adversarial Networks: A Review; and EasyDeep.

The named regression now exports and renders:

| Institution | Authors |
| --- | --- |
| Tencent Inc. | Yingsong Huang; Hui Guo; Qi Xiong |
| Hikvision | Jing Huang |
| Microsoft | Bing Bai |

Four differently spelled source-roster names are no longer assigned through
stale automatic markers: Hyejoo Choi, Jiarui Wang, Dimitrios Karageogiou, and
Kamma Vidya. Their active mappings use different names. These remain explicitly
unresolved instead of introducing unconfirmed author-name merges. Alongside five
previously unresolved authors, public validation reports nine warnings, no errors.

## Verification

Run from the repository root:

```sh
python3 scripts/audit_public_institution_consistency.py
python3 scripts/validate_public_preview.py
python3 -m pytest tests/test_public_institution_consistency.py
```

The audit is read-only by default; `--output` writes an optional derived JSON
report. The saved current result is
`data/processed/public_institution_consistency_audit.json`. Export runs this audit
against its actual mapping input before atomically replacing public outputs.

Regression coverage includes the named paper, all curated public papers, actual
browser-side dataset canonicalization/detail normalization, author superscripts,
stale author subsets, repeat enrichment, multi-affiliations, coordinate-less
affiliations, retired mappings, candidate-only fallback, and protection against
unexplained removal of an active relationship.

Final focused Admin/API/frontend/export run: **302 passed**. The standalone
consistency audit reports zero mismatches; the public validator reports zero
errors and the nine author warnings described above. JavaScript syntax and
`git diff --check` also pass.

The full suite was run with Node available. After updating the institution-type
counts affected by this repair, six broader checks remain failing on recheck:

- Repository checkpoint counts expect 342 curated papers, but the incoming
  working tree already contains 344 (and 945 rather than 942 mappings).
- Publication totals expect 314 conferences / 167 journals rather than the
  current 315 / 166.
- The old geographic coverage checkpoint expects 540 map-source papers rather
  than 539; the corrected export no longer retains an unsupported automatic
  marker for the Chongqing paper.
- The geographic completeness audit reports that Chongqing mapping's pending
  location review lacks precise actionable evidence. Its institution is still
  present in details; no coordinates were fabricated.
- A historical campus-review test expects institution `866f00322aa693b8` to
  remain pending, but current curation marks it confirmed.
- A location-count test expects 457 confirmed locations rather than 458.

These historical checkpoint and location-review facts were not rewritten to
make the broader suite green. The test-generated institution-type CSV report
was restored; no unrelated files were staged or committed.

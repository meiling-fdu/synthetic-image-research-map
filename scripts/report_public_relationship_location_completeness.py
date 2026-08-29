#!/usr/bin/env python3
"""Read-only relationship-level audit; never geocode or mutate curated state.

Curated mappings are checked against their selected location and the actual
export. Existing automatic public relationships retain the export's explicit
confidence/provenance semantics; COMPLETE does not mean newly human-reviewed.
Rows retain author groups and campus selections rather than collapsing an
institution's distinct paper locations into a registry-level boolean.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

try:
    from .curated_export import (
        _coordinate_match_for_keys, _institution_location_keys,
        _mapping_location_lookup_keys, _supported_preliminary_mapping,
        match_institutions_to_known_coordinates,
    )
    from .paper_exclusions import build_active_exclusion_index, record_is_excluded, records_share_any_identity
    from .public_relationships import canonical_author_names, clean
    from .report_missing_institution_coordinates import read_csv, review_is_actionable
except ImportError:
    from curated_export import (
        _coordinate_match_for_keys, _institution_location_keys,
        _mapping_location_lookup_keys, _supported_preliminary_mapping,
        match_institutions_to_known_coordinates,
    )
    from paper_exclusions import build_active_exclusion_index, record_is_excluded, records_share_any_identity
    from public_relationships import canonical_author_names, clean
    from report_missing_institution_coordinates import read_csv, review_is_actionable

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = (
    "paper_id", "title", "institution_id", "canonical_name", "mapping_id",
    "authors", "location_id", "city", "region", "country", "latitude",
    "longitude", "review_status", "classification", "support_source", "reason",
)


def valid_coordinates(row):
    try:
        lat = float(row.get("lat", row.get("latitude", "")))
        lon = float(row.get("lon", row.get("longitude", "")))
        return math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180
    except (TypeError, ValueError):
        return False


def same_site(marker, location):
    return valid_coordinates(marker) and valid_coordinates(location) and all(
        abs(float(marker.get(short, marker.get(long))) - float(location[short])) < 1e-6
        for short, long in (("lat", "latitude"), ("lon", "longitude"))
    )


def build_report(papers, markers, mappings, institutions, locations, reviews, exclusions, audits=(), redirects=None):
    entities = {r["institution_id"]: r for r in institutions}
    redirects = redirects or {}

    def canonical_id(value):
        identifier = clean(value)
        seen = set()
        while identifier in redirects and identifier not in seen:
            seen.add(identifier)
            identifier = redirects[identifier]
        return identifier
    usable = [r for r in locations if r.get("coordinate_status") in {"known", "confirmed"} and valid_coordinates(r)]
    lookup = match_institutions_to_known_coordinates([], [], usable, [])
    keys = {k for r in usable for k in _institution_location_keys(r)}
    exclusion_index = build_active_exclusion_index(exclusions)
    covered_markers = set()
    covered_affiliations = set()
    rows = []

    def add(paper, relation, location, status, classification, source, reason):
        iid = clean(relation.get("institution_id"))
        row = {k: "" for k in COLUMNS}
        row.update(
            paper_id=clean(paper.get("paper_id") or paper.get("id")), title=clean(paper.get("title")),
            institution_id=canonical_id(iid), canonical_name=clean(entities.get(canonical_id(iid), {}).get("canonical_name") or relation.get("institution") or relation.get("name")),
            mapping_id=clean(relation.get("mapping_id")), authors="; ".join(canonical_author_names(relation.get("institution_authors") or relation.get("authors"))),
            location_id=clean(location.get("location_id") or relation.get("location_id")),
            city=clean(location.get("city")), region=clean(location.get("region")), country=clean(location.get("country")),
            latitude=str(location.get("lat", location.get("latitude", ""))), longitude=str(location.get("lon", location.get("longitude", ""))),
            review_status=status, classification=classification, support_source=source, reason=reason,
        )
        rows.append(row)

    for mapping in mappings:
        if mapping.get("mapping_status") not in {"active", "needs_review"}:
            continue
        paper = next((p for p in papers if records_share_any_identity(mapping, p)), None)
        excluded = record_is_excluded(mapping, exclusion_index)
        if paper is None and not excluded:
            continue  # Not in this public release; not a missing public marker.
        paper = paper or mapping
        iid = clean(mapping.get("institution_id"))
        covered_affiliations.add((id(paper), canonical_id(iid)))
        preliminary = mapping.get("mapping_status") == "needs_review"
        if preliminary and not _supported_preliminary_mapping(mapping, paper):
            add(paper, mapping, {}, "needs_review", "EXCLUDED", "affiliation_evidence_unresolved", "Preliminary mapping lacks explicit source-backed author–institution evidence or belongs to a paper outside the needs-review workflow.")
            continue
        related = [r for r in reviews if r.get("institution_id") == iid and records_share_any_identity({**r, "paper_id": r.get("related_paper_id")}, mapping)]
        review = next((r for r in related if review_is_actionable(r)), next(iter(related), {}))
        reason = clean(review.get("evidence_source"))
        # Public marker aggregation may collapse several author-group mappings
        # for the same paper, canonical institution, and confirmed site. Match
        # that aggregate by paper + institution; the site check below still
        # requires the authoritative coordinates to agree.
        matching = [
            (i, m) for i, m in enumerate(markers)
            if canonical_id(m.get("institution_id")) == canonical_id(iid)
            and records_share_any_identity(m, paper)
        ]
        covered_markers.update(i for i, _ in matching)
        match = _coordinate_match_for_keys(_mapping_location_lookup_keys(mapping), lookup, keys)
        location = match.record if match.status == "known" and match.record else {}
        if excluded:
            add(paper, mapping, {}, "excluded", "EXCLUDED", "durable_paper_exclusion", "Active paper exclusion; not part of public geographic display.")
        elif entities.get(iid, {}).get("institution_status") != "active":
            add(paper, mapping, {}, review.get("review_status", ""), "ERROR", "curated_mapping", "Active mapping references inactive or missing canonical institution.")
        elif location and any(same_site(m, location) for _, m in matching):
            status = "source_backed_preliminary" if preliminary else "confirmed"
            add(paper, mapping, location, status, "COMPLETE", "curated_confirmed_location", "Source-backed affiliation, canonical institution identity, and selected location are represented by the exported mapping lineage.")
        elif review_is_actionable(review) and reason and not matching:
            geography = {"city": review.get("suggested_city", ""), "country": review.get("suggested_country", "")}
            for audit in audits:
                if audit.get("institution_id") != iid or audit.get("action") != "coordinate_evidence_unresolved":
                    continue
                if audit.get("paper_id") and audit.get("paper_id") != mapping.get("paper_id"):
                    continue
                try:
                    geography.update({k: v for k, v in json.loads(audit.get("confirmation_text", "{}")).items() if k in {"city", "region", "country"}})
                except (ValueError, AttributeError):
                    pass
            add(paper, mapping, geography, review["review_status"] + "/" + clean(review.get("coordinate_status")), "ACTIONABLE", "explicit_location_review", reason)
        elif review.get("review_status") in {"ignore", "excluded"} and reason and not matching:
            add(paper, mapping, {}, review["review_status"], "NON_GEOGRAPHIC", "explicit_location_review", reason)
        elif (
            not clean(mapping.get("location_id"))
            and not location
            and not matching
        ):
            add(paper, mapping, {}, "location_unresolved", "EXCLUDED", "confirmed_location_required", "The affiliation remains visible in paper details, but no marker is eligible until a confirmed location with authoritative coordinates exists.")
        else:
            add(paper, mapping, location, review.get("review_status", ""), "ERROR", "curated_mapping", "Selected location is missing/ambiguous, export differs or is absent, or precise actionable review is missing.")

    for index, marker in enumerate(markers):
        if index in covered_markers:
            continue
        paper = next((p for p in papers if records_share_any_identity(marker, p)), None)
        if paper is None:
            add(marker, marker, marker, "", "ERROR", "public_marker", "Marker has no public paper.")
            continue
        covered_affiliations.add((id(paper), canonical_id(marker.get("institution_id"))))
        location_id = clean(marker.get("location_id"))
        location = next((r for r in usable if r.get("location_id") == location_id and canonical_id(r.get("institution_id")) == canonical_id(marker.get("institution_id"))), None) if location_id else None
        if location_id:
            supported = location is not None and same_site(marker, location)
            source = "curated_confirmed_location"
        else:
            supported = valid_coordinates(marker) and clean(marker.get("resolution_confidence")) in {"medium", "high"} and clean(marker.get("needs_review")).lower() not in {"true", "1", "yes"}
            source = "existing_validated_automatic_location"
        add(paper, marker, marker, "confirmed" if location_id else "automatic_export_eligible", "COMPLETE" if supported else "ERROR", source, "Existing public location provenance retained; no new geocoding or independent re-review." if supported else "Exported location is invalid, stale, or unsupported by current canonical location.")

    # Only confirmed author-bearing affiliations represent active relationships.
    # Legacy raw_affiliation entries are retained source metadata, not an active
    # mapping. Auditing/reclassifying that general identity backlog is separate.
    for paper in papers:
        for affiliation in paper.get("author_institution_affiliations", []):
            if affiliation.get("mapping_source") != "curated_admin" or not affiliation.get("authors"):
                continue
            iid = canonical_id(affiliation.get("institution_id"))
            if not iid or (id(paper), iid) in covered_affiliations:
                continue
            add(paper, affiliation, {}, "", "ERROR", "public_paper_affiliation", "Public affiliation has neither a mapping, a marker, nor explicit actionable location review.")
            covered_affiliations.add((id(paper), iid))
    return sorted(rows, key=lambda r: (r["classification"], r["title"], r["institution_id"], r["mapping_id"], r["location_id"]))


def repository_report():
    curated = ROOT / "data/curated"
    public = ROOT / "web/data"
    map_payload = json.loads((public / "public_preview_map_data.json").read_text())
    return build_report(
        json.loads((public / "public_preview_papers.json").read_text())["records"],
        map_payload["records"],
        *(read_csv(curated / (name + ".csv")) for name in (
            "author_institution_mappings", "institutions", "institution_locations", "institution_location_review", "paper_exclusions", "institution_audit_log",
        )),
        redirects=map_payload.get("institution_id_redirects", {}),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/public_relationship_location_completeness.csv")
    parser.add_argument("--markdown-output", type=Path, default=ROOT / "docs/public_relationship_location_completeness.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    rows = repository_report()
    counts = Counter(r["classification"] for r in rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# Public relationship location completeness", "", "Generated read-only from the canonical curated data and current public export.", "", "Each row retains a mapping/author group and selected campus. Counts are not unique institution counts or necessarily map-row counts (merged export rows can carry multiple mapping lineages).", "", "COMPLETE includes existing export-eligible automatic relationships; it does not claim that dormant institutions or every historical automatic coordinate were independently audited in this pass.", ""]
    lines += [f"- {name}: {counts[name]}" for name in ("COMPLETE", "ACTIONABLE", "NON_GEOGRAPHIC", "EXCLUDED", "ERROR")]
    lines += ["", "## Actionable or erroneous relationships", "", "| Paper | Institution | State | Reason |", "| --- | --- | --- | --- |"]
    for row in rows:
        if row["classification"] in {"ACTIONABLE", "ERROR"}:
            lines.append("| " + " | ".join(row[k].replace("|", "/") for k in ("title", "canonical_name", "classification", "reason")) + " |")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(dict(sorted(counts.items())), sort_keys=True))
    return int(args.check and counts["ERROR"] > 0)


if __name__ == "__main__":
    raise SystemExit(main())

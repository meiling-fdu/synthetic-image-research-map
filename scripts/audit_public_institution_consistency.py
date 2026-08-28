#!/usr/bin/env python3
"""Read-only all-paper audit of curated versus public affiliation membership."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

try:
    from .curated_export import (
        PaperIdentityCache, PaperIdentityIndex, affiliation_review_state,
        curated_affiliation_removal_reason, load_curated_mappings,
    )
    from .name_matching import canonical_name_key, unique_matching_name
    from .public_relationships import canonical_author_names
except ImportError:
    from curated_export import (
        PaperIdentityCache, PaperIdentityIndex, affiliation_review_state,
        curated_affiliation_removal_reason, load_curated_mappings,
    )
    from name_matching import canonical_name_key, unique_matching_name
    from public_relationships import canonical_author_names


ROOT = Path(__file__).resolve().parents[1]


def audit_consistency(papers, markers, mappings):
    """Check both public schemas, author indices, and every related marker.

    Coordinates are deliberately not required: a valid active affiliation must
    appear in details even when its location is still under review. Automatic
    fallback remains allowed for papers with no accepted affiliation curation.
    """
    cache = PaperIdentityCache()
    mapping_index = PaperIdentityIndex(mappings, cache)
    marker_index = PaperIdentityIndex(markers, cache)
    counts = Counter()
    mismatches = []
    for paper in papers:
        matching = mapping_index.matches(paper)
        state = affiliation_review_state(paper, (), matching_mappings=matching)
        counts[state] += 1
        if state == "unreviewed":
            continue
        active = [row for row in matching if row.get("mapping_status") == "active"]
        expected = {row["institution_id"] for row in active}
        expected_authors = defaultdict(set)
        for row in active:
            for author in canonical_author_names(row.get("institution_authors")):
                expected_authors[canonical_name_key(author)].add(row["institution_id"])
        issues = []
        related = marker_index.matches(paper)
        for record in [paper, *related]:
            label = record.get("id") if record is not paper else "paper"
            for field in ("affiliations", "author_institution_affiliations"):
                actual = {row.get("institution_id", "") for row in record.get(field, [])}
                if actual != expected:
                    issues.append({"record": label, "field": field,
                                   "extra": sorted(actual - expected),
                                   "missing": sorted(expected - actual)})
            # This author-bearing schema drives the frontend affiliation rows.
            # Compare it directly to curation rather than conflating a paper's
            # separately curated roster/spelling with affiliation membership.
            actual_authors = defaultdict(set)
            for row in record.get("author_institution_affiliations", []):
                for author in canonical_author_names(row.get("authors")):
                    key = canonical_name_key(author)
                    key = unique_matching_name(key, list(expected_authors)) or key
                    actual_authors[key].add(row.get("institution_id", ""))
            for author in set(expected_authors) | set(actual_authors):
                if expected_authors[author] != actual_authors[author]:
                    issues.append({"record": label, "field": "authors", "author": author,
                                   "extra": sorted(actual_authors[author] - expected_authors[author]),
                                   "missing": sorted(expected_authors[author] - actual_authors[author])})
            if record is not paper:
                reason = curated_affiliation_removal_reason(record, matching)
                if reason:
                    issues.append({"record": label, "field": "marker", "reason": reason})
        # Canonical display names may include an abbreviation. Compare IDs,
        # not raw name spellings, and retain affiliations without coordinates.
        actual_summary = {row.get("institution_id", "")
                          for row in paper.get("aggregated_locations", [])}
        if actual_summary != expected:
            issues.append({"record": "paper", "field": "aggregated_locations",
                           "extra": sorted(actual_summary - expected),
                           "missing": sorted(expected - actual_summary)})
        if issues:
            mismatches.append({"paper_id": paper.get("paper_id", ""),
                               "title": paper.get("title", ""), "issues": issues})
    return {"papers_checked": len(papers), "states": dict(counts),
            "mismatch_count": len(mismatches), "mismatches": mismatches}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--papers", type=Path, default=ROOT / "web/data/public_preview_papers.json")
    parser.add_argument("--markers", type=Path, default=ROOT / "web/data/public_preview_map_data.json")
    parser.add_argument("--mappings", type=Path, default=ROOT / "data/curated/author_institution_mappings.csv")
    parser.add_argument("--output", type=Path, help="Optional derived JSON audit report")
    args = parser.parse_args(argv)
    report = audit_consistency(json.loads(args.papers.read_text())["records"],
                               json.loads(args.markers.read_text())["records"],
                               load_curated_mappings(args.mappings))
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    return int(bool(report["mismatch_count"]))


if __name__ == "__main__":
    raise SystemExit(main())

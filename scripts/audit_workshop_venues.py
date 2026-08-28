#!/usr/bin/env python3
"""Role-aware inventory and before/after report; never writes raw/manual inputs."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data/processed/workshop_venue_baseline.json"
OUTPUT = ROOT / "data/processed/workshop_venue_audit.json"
MATCH = re.compile(r"workshops?|CVPRW|ICCVW|WACVW|SPW|EuroS&PW|ICDMW|LNCS|CCIS|:(?:main|findings|posters)(?:$|:)", re.I)
FIELDS = {"venue": "canonical_venue", "venue_name": "canonical_venue", "venue_id": "canonical_id",
          "venue_acronym": "canonical_acronym", "venue_track": "paper_track", "track": "paper_track",
          "raw_venue": "provenance", "alias": "source_alias", "aliases": "source_alias",
          "venue_aliases": "source_alias", "container-title": "container_title",
          "short-container-title": "container_abbreviation", "publication_venue": "source_container",
          "host_venue_name": "source_container", "proceedings": "container_title", "booktitle": "container_title"}


def source_hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("data/raw", "data/manual", "data/curated")
            for p in sorted((ROOT / folder).rglob("*")) if p.is_file()}


def inventory():
    matches = []
    def visit(value, file, path="", role=""):
        if isinstance(value, dict):
            for key, item in value.items():
                next_role = FIELDS.get(key, "")
                if key == "name" and ("venue" in file or path.endswith("event")):
                    next_role = "canonical_venue" if "processed" in file else "source_event"
                if file.startswith("data/raw/") and next_role.startswith("canonical_"):
                    next_role = "source_" + next_role.removeprefix("canonical_")
                if file.startswith(("data/manual/", "data/curated/")) and next_role == "paper_track":
                    next_role = "source_paper_track"
                if ("baseline" in file or file.endswith("venue_migration_report.json")) and next_role:
                    next_role = "historical_" + next_role
                visit(item, file, f"{path}.{key}" if path else key, next_role)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, file, f"{path}[{index}]", role)
        elif role and isinstance(value, str) and MATCH.search(value):
            matches.append(dict(file=file, field_path=path, role=role, value=value))
    for folder in ("data", "web/data"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.suffix not in {".json", ".csv"} or path.name.startswith("workshop_venue_"):
                continue
            relative = str(path.relative_to(ROOT))
            if path.suffix == ".csv":
                with path.open(encoding="utf-8-sig", newline="") as handle:
                    visit(list(csv.DictReader(handle)), relative)
            else:
                visit(json.loads(path.read_text()), relative)
    return matches


def snapshot():
    try:
        from .venues import read_venue_aliases, canonical_venue_registry
    except ImportError:
        from venues import read_venue_aliases, canonical_venue_registry
    return dict(papers=json.loads((ROOT / "data/processed/venue_normalized_papers.json").read_text())["records"],
                registry=list(canonical_venue_registry(read_venue_aliases()).values()),
                aliases=read_venue_aliases(), source_hashes=source_hashes())


def write(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args()
    current = snapshot()
    if args.snapshot:
        if BASELINE.exists():
            raise SystemExit("Initial workshop audit snapshot already exists; refusing to overwrite it.")
        write(BASELINE, current)
        print("Preserved initial workshop venue state.")
        return
    before = json.loads(BASELINE.read_text())
    identity = lambda p: p.get("paper_id") or p.get("display_id") or p.get("doi") or p["title"]
    prior = {identity(p): p for p in before["papers"]}
    fields = ("venue", "venue_name", "venue_id", "venue_acronym", "venue_type", "publication_type", "venue_track", "year")
    changes = [{"title": p["title"], "paper_id": identity(p), "doi": p.get("doi", ""),
                "fields": {f: {"before": prior[identity(p)].get(f, ""), "after": p.get(f, "")}
                           for f in fields if prior[identity(p)].get(f, "") != p.get(f, "")}}
               for p in current["papers"] if identity(p) in prior]
    changes = [p for p in changes if p["fields"]]
    registry_before = {p["venue_id"]: p for p in before["registry"]}
    registry_after = {p["venue_id"]: p for p in current["registry"]}
    standalone = {"WIFS", "IH&MMSec", "MAD", "WDC", "CCWC"}
    standalone_before = [p for p in before["papers"] if p.get("venue_acronym") in standalone]
    after_by_id = {identity(p): p for p in current["papers"]}
    reviews = json.loads((ROOT / "data/processed/publication_venue_audit.json").read_text())["records"]
    standalone_reviews = [r for r in reviews if "standalone scholarly workshop" in r["reason"]]
    aliases_before = {a for v in before["registry"] for a in v.get("aliases", [])}
    aliases_after = {a for v in current["registry"] for a in v.get("aliases", [])}
    official_before = {a for a in aliases_before if MATCH.search(a)}
    parent_corrections = [c for c in changes if prior[c["paper_id"]].get("venue_acronym") in {"SPW", "EuroS&PW", "ICDMW"}]
    report = dict(summary={
        "papers_audited": len(current["papers"]), "canonical_venues_before": len(registry_before),
        "canonical_venues_after": len(registry_after), "affected_papers": len(changes),
        "track_values_before": dict(Counter(p.get("venue_track", "") for p in before["papers"])),
        "track_values_after": dict(Counter(p.get("venue_track", "") for p in current["papers"])),
        "workshops_to_workshop": sum(c["fields"].get("venue_track", {}).get("before", "").casefold() == "workshops"
                                     and c["fields"]["venue_track"]["after"] == "Workshop" for c in changes),
        "manual_review": sum(bool(p.get("venue_review_required")) for p in current["papers"]),
        "source_files_unchanged": current["source_hashes"] == before["source_hashes"],
        "parent_workshop_papers_corrected": len(parent_corrections),
        "parent_acronyms_corrected": sum("venue_acronym" in c["fields"] for c in parent_corrections),
        "parent_identities_corrected": sum("venue_id" in c["fields"] for c in parent_corrections),
        "standalone_venues_preserved": len({p["venue_id"] for p in standalone_before}),
        "standalone_papers_preserved": sum(all(after_by_id[identity(p)].get(f) == p.get(f) for f in ("venue_id", "venue_name", "venue_acronym")) for p in standalone_before),
        "standalone_papers_before": len(standalone_before),
        "ambiguous_standalone_tracks": len(standalone_reviews),
        "official_aliases_preserved": len(official_before & aliases_after),
        "official_aliases_missing": sorted(official_before - aliases_after),
        "raw_venue_changes": sum(p.get("raw_venue", "") != prior[identity(p)].get("raw_venue", "") for p in current["papers"]),
        "plural_effective_tracks_remaining": sum(p.get("venue_track") in {"workshops", "Workshops"} for p in current["papers"]),
    }, changes=changes,
        parent_workshop_corrections=parent_corrections,
        ambiguous_standalone_tracks=standalone_reviews,
        retired_registry_ids=sorted(registry_before.keys() - registry_after.keys()),
        affected_registry_records=[dict(before=registry_before.get(i), after=registry_after.get(i))
                                   for i in sorted(registry_before.keys() | registry_after.keys())
                                   if registry_before.get(i) != registry_after.get(i)],
        inventory=inventory())
    write(OUTPUT, report)
    lines = ["# Workshop venue-field audit", "", "This report compares the preserved pre-workshop-audit effective database with the current processed database. Source/manual files are read-only inputs. Empty track means not applicable or unresolved, not a new track value.", "", "## Summary", ""]
    lines.extend(f"- {key}: {value}" for key, value in report["summary"].items())
    lines.extend(["", "## Field roles and decisions", "", "Paper tracks use the shared singular controlled vocabulary. Official proceedings names and acronyms remain literal source aliases/provenance. SPW, EuroS&PW and ICDMW identify verified parent-conference workshop proceedings; WIFS, IH&MMSec, MAD, WDC and CCWC retain independent canonical identities.", "", "Existing Workshop assignments on standalone events remain Workshop pending review; Main is a proposal, not an automatic correction. Pre-audit observations preserve disputed assignments during source rebuilds, including Tiny Autoencoders whose manual track was blank. Explicit later curation supersedes these observations.", "", "The full field-role inventory is in data/processed/workshop_venue_inventory.csv. JSON includes every affected paper/registry record and retained source hashes are in the immutable baseline.", "", "## Parent corrections", ""])
    lines.extend(f"- {c['title']}: {c['fields']}" for c in parent_corrections)
    lines.extend(["", "## Standalone track review", "", "Use Admin Dashboard → Publication venues → Open / Edit; verify the paper/program, then save Main or confirm a documented nested Workshop track.", ""])
    lines.extend(f"- {r['title']} — {r['current_abbreviation']}; {r['current_track']} → proposed {r['proposed_track']}; DOI {r['doi']}" for r in standalone_reviews)
    lines.extend(["", "Other unresolved venue findings remain in data/processed/publication_venue_review.csv and the same live Dashboard queue. No records are suppressed to obtain a clean count.", ""])
    lines.extend(["## Implementation and artifacts", "",
        "Continued implementation: scripts/venue_tracks.py, venues.py, venue_evidence.py, venue_audit.py, audit_workshop_venues.py, curated_schema.py, curated_papers.py, curated_export.py, serve_admin.py, migrate_venues.py, validate_curated_database.py and validate_public_preview.py; web/admin.html, admin.js, app.js and index.html. Existing Dashboard/queue and publication/export changes in the interrupted tree were retained.", "",
        "Regression coverage: tests/test_workshop_venue_audit.py, test_publication_venue_audit.py, test_venue_normalization.py, test_paper_level_venue_track.py, test_venue_metadata_sync.py, test_paper_metadata_editing.py, test_admin_venue_combobox_frontend.py, test_frontend_venue_filters.py and test_curated_location_resolution.py.", "",
        "Processed evidence: workshop_venue_evidence.json and venue_paper_evidence.json. Preserved baseline: workshop_venue_baseline.json. Regenerated outputs: canonical_venues.json, venue_normalized_papers.json/.csv, publication_venue_audit.json, publication_venue_review.csv, workshop_venue_audit.json, workshop_venue_inventory.csv; web/data/public_preview_papers.json and public_preview_map_data.json; docs/publication_venue_audit_report.md, public_preview_report.md and this report. Methodology: docs/publication_venue_normalization.md.", ""])
    (ROOT / "docs/workshop_venue_audit_report.md").write_text("\n".join(lines))
    csv_path = ROOT / "data/processed/workshop_venue_inventory.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("file", "field_path", "role", "value"))
        writer.writeheader()
        writer.writerows(report["inventory"])
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()

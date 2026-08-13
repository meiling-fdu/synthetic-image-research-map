import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.migrate_institution_english_names import (
    AUDIT_COLUMNS,
    build_audit,
    collision_for,
    load_overrides,
    load_tables,
    normalized_key,
    validate_approved,
)
from scripts.serve_admin import prepare_mapping_candidates


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"
OVERRIDES = ROOT / "data" / "manual" / "institution_english_name_overrides.csv"
PARIS_ID = "institution:daff50b65ce469a3"
PARIS_OLD = "Université Paris Cité"
PARIS_NEW = "Paris Cité University"
PAPER_TITLE = "Improving Interpretability and Robustness for the Detection of AI-Generated Images"


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(paths):
    result = {}
    for path in paths:
        result[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


class InstitutionEnglishNameMigrationTests(unittest.TestCase):
    def test_approved_names_and_former_aliases_validate(self):
        tables = load_tables(CURATED)
        overrides = load_overrides(OVERRIDES)
        self.assertEqual(validate_approved(tables, overrides), [])
        institutions = {
            row["institution_id"]: row
            for row in tables["institutions.csv"]["rows"]
        }
        aliases = tables["institution_aliases.csv"]["rows"]
        self.assertEqual(institutions[PARIS_ID]["canonical_name"], PARIS_NEW)
        self.assertTrue(any(
            row["institution_id"] == PARIS_ID and row["alias_name"] == PARIS_OLD
            for row in aliases
        ))

    def test_audit_covers_every_current_active_canonical_institution(self):
        audited_ids = {
            row["institution_id"]
            for row in rows(
                ROOT / "data" / "processed" / "institution_english_name_audit.csv"
            )
        }
        active_ids = {
            row["institution_id"]
            for row in rows(CURATED / "institutions.csv")
            if row["institution_status"] == "active"
        }
        self.assertEqual(audited_ids, active_ids)

    def test_rename_does_not_create_a_duplicate_canonical_institution(self):
        institutions = rows(CURATED / "institutions.csv")
        self.assertEqual(
            [row["institution_id"] for row in institutions if row["institution_id"] == PARIS_ID],
            [PARIS_ID],
        )
        self.assertEqual(
            [row["institution_id"] for row in institutions if row["canonical_name"] == PARIS_NEW],
            [PARIS_ID],
        )
        self.assertFalse(any(
            row["institution_status"] == "active" and row["canonical_name"] == PARIS_OLD
            for row in institutions
        ))

    def test_audit_has_required_schema_and_keeps_legitimate_non_ascii_names(self):
        audit_path = ROOT / "data" / "processed" / "institution_english_name_audit.csv"
        with audit_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            audit = list(reader)
            self.assertEqual(tuple(reader.fieldnames or ()), AUDIT_COLUMNS)
        by_name = {row["current_canonical_name"]: row for row in audit}
        self.assertEqual(by_name["École Polytechnique"]["decision"], "keep")
        self.assertEqual(by_name["University of Žilina"]["decision"], "keep")
        self.assertEqual(by_name[PARIS_OLD]["decision"], "rename")
        self.assertEqual(by_name[PARIS_OLD]["proposed_english_name"], PARIS_NEW)
        self.assertEqual(
            by_name["Universidad Politécnica de Madrid"]["collision_status"],
            "existing_canonical_collision",
        )

    def test_known_paper_mapping_identity_and_raw_affiliation_are_preserved(self):
        mappings = [
            row for row in rows(CURATED / "author_institution_mappings.csv")
            if row["title"] == PAPER_TITLE and row["institution_id"] == PARIS_ID
        ]
        self.assertEqual(len(mappings), 1)
        mapping = mappings[0]
        self.assertEqual(mapping["institution"], PARIS_NEW)
        self.assertEqual(mapping["mapping_id"], "mapping:8bff576c35c180a528ae")
        self.assertEqual(mapping["institution_authors"], "Serguei Barannikov")
        raw_rows = [
            row for row in rows(CURATED / "author_institution_mappings.csv")
            if row["title"] == PAPER_TITLE and PARIS_OLD in row["raw_affiliation"]
        ]
        self.assertTrue(raw_rows)
        self.assertTrue(all(PARIS_OLD in row["raw_affiliation"] for row in raw_rows))

    def test_paris_country_coordinates_and_id_are_unchanged(self):
        location = next(
            row for row in rows(CURATED / "institution_locations.csv")
            if row["institution_id"] == PARIS_ID
        )
        self.assertEqual(location["institution"], PARIS_NEW)
        self.assertEqual(location["country"], "France")
        self.assertEqual((location["lat"], location["lon"]), ("48.8466", "2.3562"))

    def test_accented_and_unaccented_alias_keys_match_without_becoming_identity(self):
        self.assertEqual(normalized_key(PARIS_OLD), normalized_key("Universite Paris Cite"))
        self.assertNotEqual(PARIS_ID, normalized_key(PARIS_OLD))

    def test_admin_alias_lookup_prefills_the_english_canonical_name(self):
        candidates, warnings = prepare_mapping_candidates(
            {"source_database": "manual"},
            [{
                "institution": PARIS_OLD,
                "institution_authors": ["Serguei Barannikov"],
                "raw_affiliation": PARIS_OLD,
            }],
            institution_locations=rows(CURATED / "institution_locations.csv"),
            institution_aliases=rows(CURATED / "institution_aliases.csv"),
        )
        self.assertEqual(warnings, [])
        self.assertEqual(candidates[0]["institution"], PARIS_NEW)
        self.assertEqual(candidates[0]["mapping_status"], "active")

    def test_public_search_uses_english_display_and_retains_local_alias(self):
        payload = json.loads(
            (ROOT / "web" / "data" / "public_preview_papers.json").read_text(
                encoding="utf-8"
            )
        )
        search_record = payload["canonical_institution_search_index"][PARIS_ID]
        self.assertEqual(search_record["canonical_name"], PARIS_NEW)
        self.assertIn(PARIS_OLD, search_record["names"])
        public_alias = next(
            row for row in payload["institution_aliases"]
            if row["alias_name"] == PARIS_OLD
        )
        self.assertEqual(public_alias["canonical_institution_id"], PARIS_ID)
        self.assertEqual(public_alias["canonical_institution_name"], PARIS_NEW)

    def test_admin_selectors_search_aliases_but_submit_canonical_display(self):
        source = (ROOT / "web" / "admin.js").read_text(encoding="utf-8")
        selector = source[
            source.index("function mappingInstitutionMatches"):
            source.index("function syncMappingInstitutionId")
        ]
        draft = source[
            source.index("function mappingDraft"):
            source.index("async function submitMapping")
        ]
        self.assertIn("...(row.aliases || [])", selector)
        self.assertIn("matches.length === 1", source)
        self.assertIn("selectedInstitution.canonical_name", draft)

    def test_cross_country_northeastern_homonyms_remain_distinct(self):
        institutions = rows(CURATED / "institutions.csv")
        northeast = [
            row for row in institutions
            if row["institution_status"] == "active"
            and row["canonical_name"] == "Northeastern University"
        ]
        self.assertEqual(
            {row["institution_id"] for row in northeast},
            {"institution:0008285766dcabc7", "institution:ff1a1bc95dbe91a8"},
        )
        locations = {
            row["institution_id"]: row["country"]
            for row in rows(CURATED / "institution_locations.csv")
        }
        self.assertEqual(
            {locations[row["institution_id"]] for row in northeast},
            {"China", "United States"},
        )

    def test_parent_child_edges_are_not_name_identity(self):
        hierarchy = rows(CURATED / "institution_hierarchy.csv")
        self.assertTrue(hierarchy)
        self.assertTrue(all(
            row["parent_institution_id"].startswith("institution:")
            and row["child_institution_id"].startswith("institution:")
            for row in hierarchy
        ))

    def test_migration_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            curated = root / "curated"
            curated.mkdir()
            for filename in (
                "institutions.csv", "institution_aliases.csv",
                "author_institution_mappings.csv", "institution_locations.csv",
                "institution_location_review.csv", "institution_review_queue.csv",
                "institution_hierarchy.csv", "papers.csv",
            ):
                shutil.copy2(CURATED / filename, curated / filename)
            audit = root / "audit.csv"
            summary = root / "summary.json"
            command = [
                "python3", str(ROOT / "scripts" / "migrate_institution_english_names.py"),
                "--apply", "--curated-dir", str(curated),
                "--overrides", str(OVERRIDES), "--audit-output", str(audit),
                "--summary-output", str(summary),
            ]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
            tracked = [curated / filename for filename in (
                "institutions.csv", "institution_aliases.csv",
                "author_institution_mappings.csv", "institution_locations.csv",
                "institution_location_review.csv", "institution_review_queue.csv",
            )] + [audit, summary]
            first = digest(tracked)
            second_run = subprocess.run(
                command, cwd=ROOT, check=True, capture_output=True, text=True
            )
            self.assertEqual(digest(tracked), first)
            self.assertIn("Applied renames this run: 0", second_run.stdout)

    def test_unsafe_collision_is_reported_and_not_promoted(self):
        tables = load_tables(CURATED)
        audit = build_audit(tables, load_overrides(OVERRIDES))
        madrid = next(
            row for row in audit
            if row["institution_id"] == "institution:4e4d723f7fa11734"
        )
        self.assertEqual(madrid["decision"], "review")
        self.assertEqual(madrid["collision_status"], "existing_canonical_collision")
        collision, ids = collision_for(
            madrid["institution_id"],
            madrid["proposed_english_name"],
            [
                row for row in tables["institutions.csv"]["rows"]
                if row["institution_status"] == "active"
            ],
            {
                row["institution_id"]: row
                for row in tables["institution_locations.csv"]["rows"]
            },
        )
        self.assertEqual(collision, "existing_canonical_collision")
        self.assertEqual(ids, ["institution:2d64a600151c6a44"])

    def test_summary_lists_every_rename_and_unresolved_candidate(self):
        summary = json.loads(
            (ROOT / "data" / "processed" / "institution_english_name_migration_summary.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(summary["total_approved_renames"], 7)
        self.assertEqual(summary["total_unresolved_manual_review_cases"], 5)
        self.assertIn(PARIS_ID, {
            row["institution_id"] for row in summary["renamed_institutions"]
        })


if __name__ == "__main__":
    unittest.main()

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_institutions import (
    CuratedInstitutionError,
    exact_institution_matches,
    format_institution_name,
    update_institution_identity,
)
from scripts.curated_schema import INSTITUTION_ALIAS_COLUMNS, INSTITUTION_COLUMNS
from scripts.export_public_preview import (
    canonicalize_public_institutions,
    normalize_exported_institution_types,
    public_canonical_institution_search_index,
)
from scripts.migrate_institution_abbreviations import (
    LEGACY_COLUMNS, migrate_file, synchronize_canonical_references,
)


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class InstitutionAbbreviationTests(unittest.TestCase):
    def test_conservative_migration_splits_crim_and_certh_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "institutions.csv"
            rows = [
                {column: "" for column in LEGACY_COLUMNS},
                {column: "" for column in LEGACY_COLUMNS},
                {column: "" for column in LEGACY_COLUMNS},
            ]
            rows[0].update(institution_id="institution:crim", canonical_name="Computer Research Institute of Montreal (CRIM)", institution_type="research_unit", institution_status="active")
            rows[1].update(institution_id="institution:certh", canonical_name="Centre for Research and Technology Hellas (CERTH)", institution_type="research_unit", institution_status="active")
            rows[2].update(institution_id="institution:paris", canonical_name="University of Example (Paris)", institution_type="university", institution_status="active")
            original_ids = [row["institution_id"] for row in rows]
            write_csv(path, LEGACY_COLUMNS, rows)

            self.assertEqual(migrate_file(path), 2)
            with path.open(encoding="utf-8", newline="") as handle:
                migrated = list(csv.DictReader(handle))
            self.assertEqual([row["institution_id"] for row in migrated], original_ids)
            self.assertEqual((migrated[0]["canonical_name"], migrated[0]["abbreviation"]), ("Computer Research Institute of Montreal", "CRIM"))
            self.assertEqual((migrated[1]["canonical_name"], migrated[1]["abbreviation"]), ("Centre for Research and Technology Hellas", "CERTH"))
            self.assertEqual((migrated[2]["canonical_name"], migrated[2]["abbreviation"]), ("University of Example (Paris)", ""))
            first_pass = path.read_bytes()
            self.assertEqual(migrate_file(path), 0)
            self.assertEqual(path.read_bytes(), first_pass)

    def test_abbreviation_is_searchable_without_becoming_an_alias(self):
        institutions = [
            {
                "institution_id": "institution:crim",
                "canonical_name": "Computer Research Institute of Montreal",
                "abbreviation": "CRIM",
                "institution_type": "research_unit",
                "institution_status": "active",
            },
            {
                "institution_id": "institution:certh",
                "canonical_name": "Centre for Research and Technology Hellas",
                "abbreviation": "CERTH",
                "institution_type": "research_unit",
                "institution_status": "active",
            },
        ]
        aliases = [{
            "alias_name": "Information Technologies Institute",
            "canonical_institution_id": "institution:certh",
        }]
        index = public_canonical_institution_search_index(institutions, aliases)
        self.assertIn("CRIM", index["institution:crim"]["names"])
        self.assertIn("CERTH", index["institution:certh"]["names"])
        self.assertEqual(aliases[0]["alias_name"], "Information Technologies Institute")
        self.assertNotIn("CRIM", [alias["alias_name"] for alias in aliases])

    def test_reference_migration_preserves_existing_alias_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aliases.csv"
            alias = {column: "" for column in INSTITUTION_ALIAS_COLUMNS}
            alias.update(
                alias_id="alias:iti", alias_name="Information Technologies Institute",
                institution_id="institution:certh",
                canonical_institution_name="Centre for Research and Technology Hellas (CERTH)",
                review_status="confirmed",
            )
            write_csv(path, INSTITUTION_ALIAS_COLUMNS, [alias])
            self.assertEqual(synchronize_canonical_references(
                path, INSTITUTION_ALIAS_COLUMNS,
                {"institution:certh": "Centre for Research and Technology Hellas"},
            ), 1)
            with path.open(encoding="utf-8", newline="") as handle:
                saved = next(csv.DictReader(handle))
            self.assertEqual(saved["alias_id"], "alias:iti")
            self.assertEqual(saved["alias_name"], "Information Technologies Institute")
            self.assertEqual(saved["canonical_institution_name"], "Centre for Research and Technology Hellas")

    def test_display_combines_fields_without_persisting_combined_name(self):
        canonical = "Centre for Research and Technology Hellas"
        self.assertEqual(format_institution_name(canonical, "CERTH"), f"{canonical} (CERTH)")
        self.assertNotIn("(CERTH)", canonical)

    def test_identity_update_rejects_persisted_acronym_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "institutions.csv"
            row = {column: "" for column in INSTITUTION_COLUMNS}
            row.update(institution_id="institution:certh", canonical_name="Centre for Research and Technology Hellas", abbreviation="CERTH", institution_type="research_unit", institution_status="active")
            write_csv(path, INSTITUTION_COLUMNS, [row])
            with self.assertRaisesRegex(CuratedInstitutionError, "full name"):
                update_institution_identity("institution:certh", {**row, "canonical_name": "Centre for Research and Technology Hellas (CERTH)"}, institutions_path=path)

    def test_identity_update_rejects_abbreviation_equivalent_to_canonical_name(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "institutions.csv"
            row = {column: "" for column in INSTITUTION_COLUMNS}
            row.update(institution_id="institution:example", canonical_name="Example Institute", institution_type="research_unit", institution_status="active")
            write_csv(path, INSTITUTION_COLUMNS, [row])
            with self.assertRaisesRegex(CuratedInstitutionError, "must differ"):
                update_institution_identity(
                    "institution:example",
                    {**row, "abbreviation": "Example-Institute"},
                    institutions_path=path,
                )

    def test_public_export_keeps_full_identity_fields_and_explicit_abbreviation(self):
        map_records = [{
            "paper_id": "paper:1",
            "institution": "UPM",
            "institution_id": "institution:upm",
            "institution_authors": ["Ada Author"],
        }]
        exported = canonicalize_public_institutions(
            [], map_records, [], institutions=[{
                "institution_id": "institution:upm",
                "canonical_name": "Technical University of Madrid",
                "abbreviation": "UPM",
                "institution_type": "university",
                "institution_status": "active",
            }],
        )
        self.assertEqual(exported[0]["institution"], "Technical University of Madrid (UPM)")
        self.assertEqual(exported[0]["canonical_name"], "Technical University of Madrid")
        self.assertEqual(exported[0]["canonical_institution_name"], "Technical University of Madrid")
        self.assertEqual(exported[0]["abbreviation"], "UPM")

    def test_final_export_normalization_formats_nested_affiliations(self):
        papers = [{
            "affiliations": [{
                "name": "Technical University of Madrid",
                "canonical_name": "Technical University of Madrid",
                "institution_id": "institution:upm",
            }]
        }]
        normalize_exported_institution_types(papers, [], [{
            "institution_id": "institution:upm",
            "canonical_name": "Technical University of Madrid",
            "abbreviation": "UPM",
            "institution_type": "university",
            "institution_status": "active",
        }])
        affiliation = papers[0]["affiliations"][0]
        self.assertEqual(affiliation["name"], "Technical University of Madrid (UPM)")
        self.assertEqual(affiliation["canonical_name"], "Technical University of Madrid")
        self.assertEqual(affiliation["abbreviation"], "UPM")

    def test_repository_abbreviations_and_aliases_resolve_to_one_identity(self):
        root = Path(__file__).resolve().parents[1]
        with (root / "data/curated/institutions.csv").open(encoding="utf-8", newline="") as handle:
            institutions = list(csv.DictReader(handle))
        with (root / "data/curated/institution_aliases.csv").open(encoding="utf-8", newline="") as handle:
            aliases = list(csv.DictReader(handle))
        expectations = {
            "ISTI-CNR": "institution:541450f1f663948c",
            "Institute of Information Science and Technologies \"Alessandro Faedo\", National Research Council of Italy": "institution:541450f1f663948c",
            "Istituto di Scienza e Tecnologie dell'Informazione \"A. Faedo\", Consiglio Nazionale delle Ricerche": "institution:541450f1f663948c",
            "UPM": "institution:2d64a600151c6a44",
            "Technical University of Madrid": "institution:2d64a600151c6a44",
            "Universidad Politécnica de Madrid": "institution:2d64a600151c6a44",
            "Polytechnic University of Madrid": "institution:2d64a600151c6a44",
            "University at Buffalo": "institution:612630c2527bff83",
            "University at Buffalo, The State University of New York": "institution:612630c2527bff83",
            "University at Buffalo, State University of New York": "institution:612630c2527bff83",
            "State University of New York at Buffalo": "institution:612630c2527bff83",
            "SUNY Buffalo": "institution:612630c2527bff83",
        }
        for name, institution_id in expectations.items():
            with self.subTest(name=name):
                self.assertEqual(
                    exact_institution_matches(name, institutions, aliases),
                    [institution_id],
                )

    def test_original_four_have_explicit_final_registry_states(self):
        root = Path(__file__).resolve().parents[1]
        with (root / "data/curated/institutions.csv").open(encoding="utf-8", newline="") as handle:
            rows = {row["institution_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(rows["institution:541450f1f663948c"]["abbreviation"], "ISTI-CNR")
        self.assertEqual(rows["institution:2d64a600151c6a44"]["abbreviation"], "UPM")
        self.assertEqual(rows["institution:4e4d723f7fa11734"]["institution_status"], "merged")
        self.assertEqual(rows["institution:612630c2527bff83"]["abbreviation"], "UB")
        self.assertEqual(rows["institution:647c89e2c8a671f8"]["institution_status"], "ignored")
        buffalo = [
            row for row in rows.values()
            if row["institution_status"] == "active"
            and row["canonical_name"] == "University at Buffalo"
        ]
        self.assertEqual([row["institution_id"] for row in buffalo], ["institution:612630c2527bff83"])


if __name__ == "__main__":
    unittest.main()

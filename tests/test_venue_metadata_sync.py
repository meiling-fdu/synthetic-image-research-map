import unittest

from scripts.synchronize_venue_metadata import audit_and_synchronize
from scripts.validate_public_preview import validate_venue_consistency
from scripts.venues import VENUE_ALIAS_COLUMNS, VenueRegistryError


def alias(**overrides):
    row = {column: "" for column in VENUE_ALIAS_COLUMNS}
    row.update({
        "alias": "Test Conference",
        "venue_id": "venue:test",
        "venue_name": "Canonical Name",
        "venue_acronym": "TEST",
        "venue_type": "conference",
        "venue_track": "Main",
        "review_status": "confirmed",
    })
    row.update(overrides)
    return row


class VenueMetadataSyncTests(unittest.TestCase):
    def test_audit_repairs_same_id_drift_without_identity_change(self):
        papers = [{
            "paper_id": "paper:one",
            "title": "One",
            "venue": "Old Name",
            "venue_id": "venue:test",
            "venue_name": "Old Name",
            "venue_acronym": "OLD",
            "venue_type": "workshop",
            "venue_track": "",
            "unrelated": "preserved",
        }]
        synchronized, report = audit_and_synchronize(papers, [alias()])
        paper = synchronized[0]
        self.assertEqual(paper["venue_id"], "venue:test")
        self.assertEqual(paper["venue_name"], "Canonical Name")
        self.assertEqual(paper["venue_acronym"], "TEST")
        self.assertEqual(paper["venue_type"], "conference")
        self.assertEqual(paper["venue_track"], "Main")
        self.assertEqual(paper["unrelated"], "preserved")
        self.assertEqual(report["inconsistent_records"], 1)
        second, second_report = audit_and_synchronize(synchronized, [alias()])
        self.assertEqual(second, synchronized)
        self.assertEqual(second_report["inconsistent_records"], 0)

    def test_dangling_id_is_reported_and_not_modified(self):
        papers = [{"paper_id": "paper:one", "title": "One", "venue_id": "venue:missing"}]
        synchronized, report = audit_and_synchronize(papers, [alias()])
        self.assertEqual(synchronized, papers)
        self.assertEqual(report["dangling_records_not_modified"], 1)

    def test_registry_conflict_aborts_before_propagation(self):
        with self.assertRaisesRegex(VenueRegistryError, "inconsistent canonical metadata"):
            audit_and_synchronize([], [alias(), alias(venue_name="Other Name")])

    def test_tracks_vary_per_paper_without_canonical_identity_conflict(self):
        records = [
            {
                "title": "Main",
                "venue_id": "venue:test",
                "venue_name": "Canonical Name",
                "venue_acronym": "TEST",
                "venue_type": "conference",
                "venue_track": "Main",
            },
            {
                "title": "Workshop",
                "venue_id": "venue:test",
                "venue_name": "Canonical Name",
                "venue_acronym": "TEST",
                "venue_type": "conference",
                "venue_track": "Workshop",
            },
        ]
        issues = []
        registry = {"venue:test": {
            "venue_name": "Canonical Name",
            "venue_acronym": "TEST",
            "venue_type": "conference",
        }}
        validate_venue_consistency(records, issues, registry)
        self.assertEqual(issues, [])
        records[1]["venue_track"] = "free text"
        validate_venue_consistency(records, issues, registry)
        self.assertTrue(any("supported paper-level" in issue.message for issue in issues))

    def test_final_validation_rejects_stale_confirmed_metadata(self):
        issues = []
        validate_venue_consistency([{
            "title": "Stale",
            "venue_id": "venue:test",
            "venue_name": "Old Name",
            "venue_acronym": "TEST",
            "venue_type": "conference",
            "venue_track": "Main",
        }], issues, {"venue:test": {
            "venue_name": "Canonical Name",
            "venue_acronym": "TEST",
            "venue_type": "conference",
        }})
        self.assertTrue(any("confirmed canonical registry" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()

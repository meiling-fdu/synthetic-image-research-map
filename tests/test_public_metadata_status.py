import unittest

from scripts.public_metadata_status import (
    PUBLIC_STATUSES,
    add_public_metadata_status,
    metadata_status,
    public_source,
    public_status,
)


class PublicMetadataStatusTests(unittest.TestCase):
    def test_internal_status_mapping_is_explicit_and_closed(self):
        self.assertEqual(public_status("reviewed", "confirmed"), "Verified")
        self.assertEqual(public_status("confirmed"), "Curated")
        self.assertEqual(public_status("needs_review", "reviewed"), "Needs review")
        self.assertEqual(public_status("pending"), "Needs review")
        self.assertEqual(public_status(""), "Source metadata")
        self.assertEqual(public_status("future_unknown_value"), "Source metadata")
        self.assertEqual(
            set(PUBLIC_STATUSES),
            {"Verified", "Curated", "Needs review", "Source metadata"},
        )

    def reviewed_paper(self, **updates):
        record = {
            "title": "Reviewed paper",
            "year": 2025,
            "venue": "CVPR",
            "publication_type": "conference",
            "task": "detection",
            "review_status": "reviewed",
            "curation_status": "confirmed",
            "metadata_source": "openalex",
        }
        record.update(updates)
        return record

    def test_globally_pending_paper(self):
        result = metadata_status(self.reviewed_paper(
            review_status="pending", curation_status="needs_review"
        ))
        self.assertEqual(result["overall"], "Needs review")
        self.assertEqual(result["default_field_status"], "Needs review")

    def test_reviewed_paper_with_unresolved_venue_only(self):
        result = metadata_status(self.reviewed_paper(venue_review_required=True))
        self.assertEqual(result["overall"], "Verified")
        self.assertEqual(result["default_field_status"], "Verified")
        self.assertEqual(
            result["field_overrides"]["venue"]["status"], "Needs review"
        )

    def test_reviewed_paper_with_unresolved_affiliation_only(self):
        result = metadata_status(self.reviewed_paper(
            affiliation_review_state="unreviewed",
            affiliations=[{"name": "Example Lab", "preliminary": True}],
        ))
        self.assertEqual(result["overall"], "Verified")
        self.assertEqual(
            result["field_overrides"]["affiliations"]["status"],
            "Needs review",
        )

    def test_reviewed_paper_with_both_localized_issues(self):
        result = metadata_status(self.reviewed_paper(
            venue_review_required=True,
            affiliation_review_state="unreviewed",
            affiliations=[{"name": "Example Lab"}],
        ))
        self.assertEqual(result["overall"], "Verified")
        self.assertEqual(
            {
                field
                for field, value in result["field_overrides"].items()
                if value.get("status") == "Needs review"
            },
            {"venue", "affiliations"},
        )

    def test_fully_reviewed_paper_is_compact_and_verified(self):
        result = metadata_status(self.reviewed_paper())
        self.assertEqual(result["overall"], "Verified")
        self.assertEqual(result["default_field_status"], "Verified")
        self.assertEqual(result["source"], "OpenAlex")
        self.assertEqual(result["field_overrides"], {})

    def test_curated_but_not_formally_reviewed_paper(self):
        result = metadata_status({
            "title": "Curated paper", "curation_status": "confirmed"
        })
        self.assertEqual(result["overall"], "Curated")
        self.assertEqual(result["default_field_status"], "Curated")

    def test_source_only_paper_with_curated_affiliation_stays_source_metadata(self):
        result = metadata_status({
            "title": "Source-only with affiliation",
            "affiliation_review_state": "curated",
            "affiliations": [{"name": "Example University"}],
        })
        self.assertEqual(result["overall"], "Source metadata")
        self.assertEqual(result["default_field_status"], "Source metadata")
        self.assertEqual(
            result["field_overrides"]["affiliations"]["status"], "Curated"
        )

    def test_missing_optional_metadata_does_not_downgrade_or_create_fields(self):
        result = metadata_status(self.reviewed_paper(
            venue="", doi="", arxiv_id="", publication_date=""
        ))
        self.assertEqual(result["overall"], "Verified")
        self.assertNotIn("venue", result["field_overrides"])
        self.assertNotIn("doi", result["field_overrides"])
        self.assertNotIn("arxiv", result["field_overrides"])

    def test_unknown_internal_status_is_source_metadata(self):
        result = metadata_status({
            "title": "Unknown", "review_status": "future_state"
        })
        self.assertEqual(result["overall"], "Source metadata")

    def test_precedence_conflicts_stay_within_global_scope(self):
        pending = metadata_status(self.reviewed_paper(
            review_status="reviewed", curation_status="needs_review"
        ))
        self.assertEqual(pending["overall"], "Needs review")
        localized = metadata_status(self.reviewed_paper(
            venue_review_required=True, curation_status="confirmed"
        ))
        self.assertEqual(localized["overall"], "Verified")
        self.assertEqual(
            localized["field_overrides"]["venue"]["status"], "Needs review"
        )

    def test_derived_needs_review_is_localized_to_affiliations(self):
        result = metadata_status(self.reviewed_paper(
            needs_review=True,
            affiliation_review_state="curated",
            affiliations=[{"name": "Example University"}],
        ))
        self.assertEqual(result["overall"], "Verified")
        self.assertEqual(
            result["field_overrides"]["affiliations"]["status"],
            "Needs review",
        )

    def test_missing_provenance_does_not_invent_a_source_or_confidence(self):
        result = metadata_status({"title": "Source-only paper", "year": 2024})
        self.assertEqual(result["overall"], "Source metadata")
        self.assertEqual(result["default_field_status"], "Source metadata")
        self.assertNotIn("source", result)
        self.assertEqual(result["field_overrides"], {})

    def test_doi_and_arxiv_sources_remain_distinct(self):
        result = metadata_status({
            "title": "Versions",
            "doi": "10.1000/example",
            "arxiv_id": "2501.00001",
            "review_status": "reviewed",
            "metadata_source": "crossref",
        })
        self.assertEqual(result["source"], "DOI / Crossref")
        self.assertNotIn("doi", result["field_overrides"])
        self.assertEqual(result["field_overrides"]["arxiv"]["source"], "arXiv")
        self.assertEqual(public_source("https://api.crossref.org/works/x"), "DOI / Crossref")

    def test_affiliation_uses_only_normalized_public_provenance(self):
        result = metadata_status({
            "title": "Affiliations",
            "review_status": "reviewed",
            "affiliation_review_state": "curated",
            "affiliations": [{"name": "Example University"}],
        }, [{
            "mapping_status": "active",
            "provenance_source": "OpenAlex authorships",
            "review_id": "internal-only",
            "notes": "must not escape",
        }])
        affiliation = result["field_overrides"]["affiliations"]
        self.assertEqual(affiliation, {"status": "Curated", "source": "OpenAlex"})
        serialized = repr(result)
        self.assertNotIn("review_id", serialized)
        self.assertNotIn("notes", serialized)
        self.assertNotIn("resolution", serialized)

    def test_hierarchy_search_context_is_not_affiliation_evidence(self):
        result = metadata_status({
            "title": "Hierarchy match",
            "review_status": "reviewed",
            "institution_hierarchy": [{"parent": "Parent", "child": "Child"}],
            "search_institution_ids": ["institution:parent"],
        })
        self.assertNotIn("affiliations", result["field_overrides"])
        self.assertNotIn("hierarchy", repr(result).casefold())

    def test_paper_status_is_copied_to_deep_link_map_records_by_identity(self):
        paper = {
            "paper_id": "paper:one",
            "title": "Deep linked",
            "doi": "10.1000/deep",
            "review_status": "reviewed",
            "metadata_source": "openalex",
        }
        marker = {
            "id": "marker:one",
            "title": "Deep linked",
            "doi": "10.1000/deep",
            "institution": "Example University",
        }
        add_public_metadata_status([paper], [marker])
        self.assertEqual(marker["metadata_status"], paper["metadata_status"])
        self.assertEqual(marker["metadata_status"]["overall"], "Verified")


if __name__ == "__main__":
    unittest.main()

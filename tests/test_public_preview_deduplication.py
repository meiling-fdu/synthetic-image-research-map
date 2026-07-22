import json
import subprocess
import unittest
from copy import deepcopy
from pathlib import Path

from scripts.curated_export import _ordered_mapping_authors, build_curated_map_records
from scripts.export_public_preview import (
    add_public_detail_fields,
    apply_key_paper_expected_task,
    apply_ordered_paper_location_summaries,
    canonicalize_public_institutions,
    confirmed_alias_id_redirects,
    exclude_preprint_versions,
    exclude_retracted_records,
    paper_is_retracted,
    public_canonical_institution_search_index,
    public_institution_aliases,
    institution_id_redirects,
    synchronize_publication_types,
)
from scripts.country_normalization import normalize_country_region
from scripts.refresh_public_preview import build_steps, parse_args
from scripts.validate_public_preview import validate_preprint_version_duplicates
from scripts.validate_public_preview import (
    is_bad_author_candidate,
    normalized_author_name,
    validate_paper_detail_schema,
    validate_paper_record,
    validate_record,
    validate_curated_affiliation_supersession,
)


class PublicPreviewDeduplicationTests(unittest.TestCase):
    def test_key_paper_expected_task_makes_cifake_shaped_record_map_eligible(self):
        candidate = {
            "title": "CIFAKE: Image Classification and Explainable Identification of AI-Generated Synthetic Images",
            "year": "2024",
            "publication_year": "2024",
            "doi": "10.1109/access.2024.3356122",
            "openalex_url": "https://openalex.org/W4391019749",
            "preliminary_task": "uncertain",
            "preliminary_subtask": "unknown",
            "in_scope": "false",
            "manual_review": "true",
        }
        key_paper = {
            "title": candidate["title"],
            "year": "2024",
            "expected_task": "detection",
        }

        record = apply_key_paper_expected_task(candidate, key_paper)

        self.assertEqual(record["preliminary_task"], "detection")
        self.assertEqual(record["preliminary_subtask"], "synthetic_image_detection")
        self.assertEqual(record["in_scope"], "true")

    def test_active_openalex_mapping_with_valid_coordinates_emits_one_marker(self):
        paper = {
            "title": "CIFAKE: Image Classification and Explainable Identification of AI-Generated Synthetic Images",
            "year": 2024,
            "publication_year": 2024,
            "task": "detection",
            "subtask": "synthetic_image_detection",
            "doi": "10.1109/access.2024.3356122",
            "openalex_url": "https://openalex.org/W4391019749",
            "authors": ["Jordan J. Bird", "Ahmad Lotfi"],
        }
        mapping = {
            "mapping_id": "mapping:cifake",
            "paper_id": "openalex:W4391019749",
            "title": paper["title"],
            "year": "2024",
            "doi": "10.1109/access.2024.3356122",
            "openalex_url": "https://openalex.org/W4391019749",
            "institution": "Nottingham Trent University",
            "institution_id": "institution:c055ca96e505b797",
            "institution_authors": "Jordan J. Bird; Ahmad Lotfi",
            "raw_affiliation": "Department of Computer Science, Nottingham Trent University, Nottingham, U.K.",
            "mapping_status": "active",
        }
        location = {
            "location_id": "location:ntu",
            "institution": "Nottingham Trent University",
            "institution_id": "institution:c055ca96e505b797",
            "lat": "52.9563",
            "lon": "-1.1514",
            "city": "Nottingham",
            "region": "Nottinghamshire",
            "country": "United Kingdom",
            "country_code": "GB",
        }

        markers, summary = build_curated_map_records(
            [paper],
            [mapping],
            [],
            [],
            confirmed_location_records=[location],
        )

        self.assertEqual(summary["curated_markers_created"], 1)
        self.assertEqual(len(markers), 1)
        self.assertEqual(markers[0]["institution_id"], "institution:c055ca96e505b797")
        self.assertEqual(markers[0]["country"], "United Kingdom")
        self.assertEqual(markers[0]["institution_authors"], ["Jordan J. Bird", "Ahmad Lotfi"])
        self.assertEqual(summary["active_mapping_marker_diagnostics"], [])

    def test_uncertain_active_mapping_with_coordinates_is_diagnosed_when_unemitted(self):
        paper = {
            "title": "Unclassified generated-image paper",
            "year": 2024,
            "publication_year": 2024,
            "task": "uncertain",
            "subtask": "unknown",
            "doi": "10.1234/uncertain",
            "authors": ["Ada Author"],
        }
        mapping = {
            "mapping_id": "mapping:uncertain",
            "paper_id": "openalex:W1",
            "title": paper["title"],
            "year": "2024",
            "doi": "10.1234/uncertain",
            "institution": "Known University",
            "institution_id": "institution:known",
            "institution_authors": "Ada Author",
            "mapping_status": "active",
        }
        location = {
            "location_id": "location:known",
            "institution": "Known University",
            "institution_id": "institution:known",
            "lat": "1",
            "lon": "2",
            "country": "United Kingdom",
            "country_code": "GB",
        }

        markers, summary = build_curated_map_records(
            [paper],
            [mapping],
            [],
            [],
            confirmed_location_records=[location],
        )

        self.assertEqual(markers, [])
        self.assertEqual(
            summary["active_mapping_marker_diagnostics"][0]["final_drop_reason"],
            "non_public_task:uncertain",
        )

    def test_confirmed_alias_redirects_legacy_name_id_to_canonical_id(self):
        self.assertEqual(
            confirmed_alias_id_redirects([{
                "alias_name": "Institute of Information Engineering",
                "canonical_institution_id": "institution:cee70184073782c7",
            }]),
            {
                "institution:9aae8d70d2d6eed8":
                "institution:cee70184073782c7"
            },
        )

    def test_id_first_canonicalization_covers_alias_merge_authors_and_parent_child(self):
        parent_id = "institution:parent"
        child_id = "institution:child"
        canonical_id = "institution:certh"
        merged_id = "institution:certh-old"
        institutions = [
            {"institution_id": canonical_id, "canonical_name": "Centre for Research and Technology Hellas (CERTH)", "institution_status": "active"},
            {"institution_id": merged_id, "canonical_name": "Old CERTH", "institution_status": "merged"},
            {"institution_id": parent_id, "canonical_name": "Parent Academy", "institution_status": "active"},
            {"institution_id": child_id, "canonical_name": "Confirmed Child Lab", "institution_status": "active"},
        ]
        audits = [{"action": "merge", "previous_institution_id": merged_id, "institution_id": canonical_id}]
        aliases = public_institution_aliases([], (), institutions)
        redirects = institution_id_redirects(institutions, audits)
        paper = {"title": "Canonical aggregation", "doi": "10.1/canonical", "year": 2026}
        maps = [
            {**paper, "institution": "Centre for Research and Technology Hellas", "institution_id": "institution:legacy-name", "institution_authors": ["One", "Two"]},
            {**paper, "institution": "Centre for Research and Technology Hellas (CERTH)", "institution_id": canonical_id, "institution_authors": ["Two", "Three"]},
            {**paper, "institution": "Old CERTH", "institution_id": merged_id, "institution_authors": ["Four"]},
            {**paper, "institution": "Centre for Research and Technology Hellas", "institution_id": parent_id, "institution_authors": ["Five"]},
            {**paper, "institution": "Confirmed Child Lab", "institution_id": child_id, "institution_authors": ["Six"]},
        ]

        first_papers, first_maps = deepcopy([paper]), deepcopy(maps)
        canonical_maps = canonicalize_public_institutions(
            first_papers, first_maps, aliases, (), institutions, redirects,
        )
        first = json.dumps([first_papers, canonical_maps], ensure_ascii=False, sort_keys=True)
        second_papers, second_maps = deepcopy([paper]), deepcopy(maps)
        second_result = canonicalize_public_institutions(
            second_papers, second_maps, aliases, (), institutions, redirects,
        )

        self.assertEqual(json.dumps([second_papers, second_result], ensure_ascii=False, sort_keys=True), first)
        self.assertEqual(len(canonical_maps), 3)
        canonical = next(row for row in canonical_maps if row["institution_id"] == canonical_id)
        self.assertEqual(canonical["institution"], "Centre for Research and Technology Hellas (CERTH)")
        self.assertEqual(set(canonical["institution_authors"]), {"One", "Two", "Three", "Four"})
        self.assertEqual({row["institution_id"] for row in canonical_maps}, {canonical_id, parent_id, child_id})
        self.assertEqual(first_papers[0]["map_record_count"], 3)
        self.assertEqual(first_papers[0]["aggregated_institutions"], [
            "Centre for Research and Technology Hellas (CERTH)", "Parent Academy", "Confirmed Child Lab",
        ])

    def test_country_codes_are_normalized_to_public_english_names(self):
        self.assertEqual(normalize_country_region("CN", "")["country"], "China")
        self.assertEqual(normalize_country_region("", "US")["country"], "United States")
        self.assertEqual(normalize_country_region("KR", "KR")["country"], "South Korea")

    def test_ordered_location_summary_preserves_pairs_and_is_deterministic(self):
        paper = {"title": "Ordered locations", "year": 2026, "doi": "10.1/order"}
        maps = [{
            **paper,
            "institution": "Beijing Institute",
            "institution_id": "institution:beijing",
            "country": "CN",
            "country_code": "CN",
            "region": "Beijing",
        }, {
            **paper,
            "institution": "Jiangsu Institute",
            "institution_id": "institution:jiangsu",
            "country": "China",
            "country_code": "CN",
            "region": "Jiangsu",
        }, {
            **paper,
            "institution": "US Institute",
            "institution_id": "institution:us",
            "country": "US",
            "country_code": "US",
            "region": "",
        }, {
            **paper,
            "institution": "Korean Institute",
            "institution_id": "institution:kr",
            "country": "KR",
            "country_code": "KR",
            "region": "Seoul",
        }]

        apply_ordered_paper_location_summaries([paper], maps)
        first = json.dumps(paper, ensure_ascii=False, sort_keys=True)
        apply_ordered_paper_location_summaries([paper], maps)

        self.assertEqual(json.dumps(paper, ensure_ascii=False, sort_keys=True), first)
        self.assertEqual(
            paper["aggregated_country_names"],
            ["China", "United States", "South Korea"],
        )
        self.assertEqual(paper["aggregated_regions"], ["Beijing", "Jiangsu", "Seoul"])
        self.assertEqual(
            [location["location_display"] for location in paper["aggregated_locations"]],
            ["Beijing, China", "Jiangsu, China", "United States", "Seoul, South Korea"],
        )

    def test_alias_records_collapse_before_ordered_location_aggregation(self):
        paper = {"title": "Alias locations", "year": 2025, "doi": "10.1/alias"}
        maps = [{
            **paper,
            "institution": "U Example",
            "institution_id": "institution:alias",
            "country": "US",
            "region": "California",
        }, {
            **paper,
            "institution": "University Example",
            "institution_id": "institution:canonical",
            "country": "United States",
            "country_code": "US",
            "region": "California",
        }]
        aliases = [{
            "alias_name": "U Example",
            "canonical_institution_name": "University Example",
            "canonical_institution_id": "institution:canonical",
        }]

        canonical_maps = canonicalize_public_institutions([paper], maps, aliases)
        apply_ordered_paper_location_summaries([paper], canonical_maps)

        self.assertEqual(len(canonical_maps), 1)
        self.assertEqual(paper["aggregated_institutions"], ["University Example"])
        self.assertEqual(paper["aggregated_country_names"], ["United States"])
        self.assertEqual(paper["aggregated_regions"], ["California"])

    def test_search_index_maps_merged_source_name_to_active_target_only(self):
        target_id = "institution:e278f75918ccf8a7"
        source_id = "institution:dfb3cc816a4476d7"
        canonical_name = (
            "Institute of Computing Technology, Chinese Academy of Sciences"
        )
        aliases = public_institution_aliases([{
            "alias_name": "Institute of Computing Technology",
            "canonical_institution_name": canonical_name,
            "institution_id": target_id,
            "review_status": "confirmed",
            "alias_source": "institution-merge",
        }])
        index = public_canonical_institution_search_index([{
            "institution_id": source_id,
            "canonical_name": "Institute of Computing Technology",
            "institution_status": "merged",
        }, {
            "institution_id": target_id,
            "canonical_name": canonical_name,
            "institution_status": "active",
        }], aliases)

        self.assertEqual(set(index), {target_id})
        self.assertEqual(index[target_id]["canonical_name"], canonical_name)
        self.assertIn("Institute of Computing Technology", index[target_id]["names"])
        self.assertNotIn(source_id, index)

    def test_canonical_institution_types_survive_alias_deduplication(self):
        canonical_id = "institution:canonical"
        institutions = [{
            "institution_id": canonical_id,
            "canonical_name": "Example Research",
            "institution_type": "research_unit",
            "institution_status": "active",
        }]
        aliases = [{
            "alias_name": "Example Lab",
            "canonical_institution_name": "Example Research",
            "canonical_institution_id": canonical_id,
        }]
        paper = {
            "title": "Typed paper",
            "year": 2025,
            "doi": "10.1000/typed",
            "affiliations": [
                {"name": "Example Lab", "institution_id": "institution:merged"},
                {"name": "Example Research", "institution_id": canonical_id},
            ],
        }
        maps = [
            {**paper, "institution": "Example Lab", "institution_id": "institution:merged"},
            {**paper, "institution": "Example Research", "institution_id": canonical_id},
        ]

        canonical_maps = canonicalize_public_institutions(
            [paper], maps, aliases, institutions=institutions,
            id_redirects={"institution:merged": canonical_id},
        )
        apply_ordered_paper_location_summaries([paper], canonical_maps)
        add_public_detail_fields([paper], canonical_maps)
        search_index = public_canonical_institution_search_index(
            institutions, aliases,
        )

        self.assertEqual(len(canonical_maps), 1)
        self.assertEqual(canonical_maps[0]["institution_type"], "research_unit")
        self.assertEqual(len(paper["affiliations"]), 1)
        self.assertEqual(paper["affiliations"][0]["institution_type"], "research_unit")
        self.assertEqual(
            paper["author_institution_affiliations"][0]["institution_type"],
            "research_unit",
        )
        self.assertEqual(paper["aggregated_institution_types"], ["research_unit"])
        self.assertEqual(search_index[canonical_id]["institution_type"], "research_unit")

    def test_duplicate_institution_names_resolve_coordinates_by_canonical_id(self):
        paper = {
            "paper_id": "curated:northeastern",
            "title": "Northeastern regression",
            "year": "2026",
            "task": "detection",
        }
        mapping = {
            "mapping_id": "mapping:neu-us",
            "paper_id": paper["paper_id"],
            "title": paper["title"],
            "year": paper["year"],
            "institution": "Northeastern University",
            "institution_id": "institution:neu-us",
            "institution_authors": "Example Author",
            "raw_affiliation": "Northeastern University",
            "mapping_status": "active",
        }
        locations = [{
            "institution": "Northeastern University",
            "institution_id": "institution:neu-cn",
            "city": "Shenyang",
            "region": "Liaoning",
            "country": "China",
            "country_code": "CN",
            "lat": "41.7634632",
            "lon": "123.4117577",
        }, {
            "institution": "Northeastern University",
            "institution_id": "institution:neu-us",
            "city": "Boston",
            "region": "Massachusetts",
            "country": "United States",
            "country_code": "US",
            "lat": "42.3398",
            "lon": "-71.0892",
        }]

        markers, summary = build_curated_map_records(
            [paper], [mapping], [], confirmed_location_records=locations,
        )

        self.assertEqual(summary["curated_markers_created"], 1)
        self.assertEqual(markers[0]["institution_id"], "institution:neu-us")
        self.assertEqual(markers[0]["city"], "Boston")
        self.assertEqual(markers[0]["country"], "United States")

    def test_duplicate_canonical_names_do_not_canonicalize_name_only_records(self):
        institutions = [{
            "institution_id": "institution:neu-cn",
            "canonical_name": "Northeastern University",
            "institution_status": "active",
        }, {
            "institution_id": "institution:neu-us",
            "canonical_name": "Northeastern University",
            "institution_status": "active",
        }]
        paper = {"title": "Ambiguous name", "year": 2026, "doi": "10.1/neu"}
        maps = [{**paper, "institution": "Northeastern University"}]

        canonical_maps = canonicalize_public_institutions(
            [paper], maps, [], institutions=institutions,
        )

        self.assertFalse(canonical_maps[0].get("institution_id"))

    def test_confirmed_astar_variants_canonicalize_and_dedupe_public_records(self):
        aliases = public_institution_aliases(
            [
                {
                    "alias_name": "Agency for Science, Technology and Research",
                    "canonical_institution_name": "Agency for Science, Technology and Research (A*STAR)",
                    "review_status": "confirmed",
                    "alias_source": "local-admin",
                }
            ],
            [
                {
                    "institution": "A*STAR",
                    "canonical_institution_name": "Agency for Science, Technology and Research (A*STAR)",
                    "review_status": "confirmed",
                },
                {
                    "institution": "A STAR Research Lab",
                    "canonical_institution_name": "Agency for Science, Technology and Research (A*STAR)",
                    "review_status": "alias_candidate",
                },
            ],
        )
        self.assertIn("A*STAR", {row["alias_name"] for row in aliases})
        self.assertNotIn("A STAR Research Lab", {row["alias_name"] for row in aliases})
        canonical_name = "Agency for Science, Technology and Research (A*STAR)"
        canonical_id = next(
            row["canonical_institution_id"]
            for row in aliases
            if row["alias_name"] == "A*STAR"
        )
        paper = {
            "title": "Shared A*STAR paper",
            "year": 2024,
            "doi": "10.1000/astar",
            "authors": ["Alias Author", "Canonical Author", "Other Author"],
            "aggregated_institutions": [
                "A*STAR",
                "Agency for Science, Technology and Research",
                "Other University",
            ],
            "map_record_count": 3,
            "has_map_location": True,
        }
        maps = [
            {
                **paper,
                "institution": "A*STAR",
                "institution_id": "institution:old-astar",
                "institution_authors": ["Alias Author"],
            },
            {
                **paper,
                "institution": "Agency for Science, Technology and Research",
                "institution_id": "institution:old-expanded",
                "institution_authors": ["Canonical Author"],
            },
            {
                **paper,
                "institution": "Other University",
                "institution_id": "institution:other",
                "institution_authors": ["Other Author"],
            },
        ]

        canonical_maps = canonicalize_public_institutions([paper], maps, aliases)
        add_public_detail_fields([paper], canonical_maps)

        self.assertEqual(len(canonical_maps), 2)
        astar = next(row for row in canonical_maps if row["institution_id"] == canonical_id)
        self.assertEqual(astar["institution"], canonical_name)
        self.assertEqual(
            set(astar["institution_authors"]),
            {"Alias Author", "Canonical Author"},
        )
        self.assertEqual(paper["map_record_count"], 2)
        self.assertEqual(
            paper["aggregated_institutions"],
            [canonical_name, "Other University"],
        )
        self.assertEqual(
            [item["name"] for item in paper["affiliations"]],
            [canonical_name, "Other University"],
        )
        self.assertEqual(
            set(paper["affiliations"][0]["source_institution_names"]),
            {"A*STAR", "Agency for Science, Technology and Research"},
        )

    def test_map_markers_inherit_one_normalized_canonical_publication_type(self):
        paper = {
            "title": "Shared paper",
            "year": 2025,
            "publication_type": "journal",
        }
        markers = [
            {**paper, "publication_type": "review", "institution": "One"},
            {**paper, "publication_type": "", "institution": "Two"},
        ]

        unresolved = synchronize_publication_types([paper], markers)

        self.assertEqual(paper["publication_type"], "journal")
        self.assertEqual(
            [marker["publication_type"] for marker in markers],
            ["journal", "journal"],
        )
        self.assertEqual(unresolved, [])

    def test_unresolved_type_is_reported_once_for_many_institutions(self):
        paper = {"title": "Unknown type", "year": 2025, "publication_type": "report"}
        markers = [
            {**paper, "institution": "One"},
            {**paper, "institution": "Two"},
        ]

        unresolved = synchronize_publication_types([paper], markers)

        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0]["title"], "Unknown type")

    def test_retractions_are_removed_from_paper_and_map_outputs(self):
        retractions = [
            {"title": "[Retracted] Bracketed title"},
            {"title": "Retracted: Colon title"},
            {"title": "Retraction notice", "publication_type": "retraction"},
            {"title": "Flagged record", "is_retracted": True},
            {"title": "Curated flag", "retracted": "true"},
            {"title": "Excluded record", "exclusion_reason": "retracted"},
        ]
        normal = {"title": "A valid paper", "publication_type": "journal"}

        for record in retractions:
            with self.subTest(record=record):
                self.assertTrue(paper_is_retracted(record))
        self.assertFalse(paper_is_retracted(normal))

        papers, paper_count = exclude_retracted_records(
            [normal, *retractions]
        )
        markers, marker_count = exclude_retracted_records(
            [{**normal, "institution": "Example University"}, *retractions]
        )

        self.assertEqual(papers, [normal])
        self.assertEqual(
            markers,
            [{**normal, "institution": "Example University"}],
        )
        self.assertEqual(paper_count, len(retractions))
        self.assertEqual(marker_count, len(retractions))

        for validator in (validate_record, validate_paper_record):
            issues = []
            validator(0, retractions[0], issues)
            self.assertTrue(
                any(
                    "retracted paper must not appear" in issue.message
                    for issue in issues
                )
            )

    def test_no_search_refresh_preserves_large_preview_without_default_cap(self):
        args = parse_args(
            [
                "--skip-search",
                "--user-agent",
                "test refresh",
            ]
        )

        steps = build_steps(args)
        commands = [step.command for step in steps]

        self.assertEqual(len(steps), 4)
        self.assertTrue(
            all("run_pipeline.py" not in " ".join(command) for command in commands)
        )
        self.assertIn("--preserve-existing", commands[0])
        self.assertNotIn("--max-records", commands[0])
        self.assertIn("report_public_preview.py", " ".join(commands[1]))
        self.assertIn("report_missing_author_mappings.py", " ".join(commands[2]))

    def test_default_search_refresh_has_no_implicit_processing_or_record_cap(self):
        args = parse_args(["--user-agent", "test refresh"])

        steps = build_steps(args)
        pipeline_command = steps[0].command
        export_command = steps[1].command

        self.assertIn("run_pipeline.py", " ".join(pipeline_command))
        self.assertNotIn("--limit", pipeline_command)
        self.assertIn("--preserve-existing", export_command)
        self.assertNotIn("--max-records", export_command)

    def test_reversed_author_name_matches_curated_name(self):
        self.assertEqual(
            normalized_author_name("Marra, Francesco"),
            normalized_author_name("Francesco Marra"),
        )

    def test_validator_rejects_stale_openalex_affiliation(self):
        paper = {
            "title": "Example",
            "year": 2019,
            "doi": "10.1000/example",
            "curated_mappings": [
                {
                    "institution": "Correct University",
                    "institution_authors": ["Francesco Marra"],
                    "mapping_status": "active",
                }
            ],
        }
        stale = {
            **paper,
            "institution": "Stale Hospital",
            "institution_authors": ["Marra, Francesco"],
            "source_database": "OpenAlex",
        }
        issues = []

        validate_curated_affiliation_supersession(
            [stale], [paper], issues
        )

        self.assertTrue(
            any("stale public and curated institutions" in issue.message for issue in issues)
        )

    def test_validator_uses_canonical_author_id_when_names_differ(self):
        paper = {
            "title": "Canonical author test",
            "year": 2020,
            "doi": "10.1000/author-id",
            "curated_mappings": [
                {
                    "institution": "Correct University",
                    "institution_authors": ["F. Marra"],
                    "institution_author_ids": [
                        "https://openalex.org/A123"
                    ],
                    "mapping_status": "active",
                }
            ],
        }
        stale = {
            **paper,
            "institution": "Stale Hospital",
            "institution_authors": ["Francesco Marra"],
            "institution_author_ids": ["https://openalex.org/A123"],
            "source_database": "OpenAlex",
        }
        issues = []

        validate_curated_affiliation_supersession(
            [stale], [paper], issues
        )

        self.assertTrue(
            any("stale public and curated institutions" in issue.message for issue in issues)
        )

    def test_affiliations_union_across_unique_paper_and_markers(self):
        paper = {
            "title": "Shared paper",
            "year": 2020,
            "doi": "10.1000/shared",
            "authors": ["Doe, Jane", "John Roe"],
        }
        naples = {
            **paper,
            "institution": "University of Naples Federico II",
            "institution_id": "institution:naples",
            "institution_authors": ["Jane Doe"],
            "country": "Italy",
            "region": "Campania",
        }
        trento = {
            **paper,
            "institution": "University of Trento",
            "institution_id": "institution:trento",
            "institution_authors": ["John Roe"],
            "country": "Italy",
            "region": "Trentino-Alto Adige/Südtirol",
        }

        add_public_detail_fields([paper], [naples, trento])

        self.assertEqual(
            [item["name"] for item in paper["affiliations"]],
            ["University of Naples Federico II", "University of Trento"],
        )
        self.assertEqual(
            [author["affiliation_indices"] for author in paper["authors"]],
            [[1], [2]],
        )
        self.assertTrue(naples["authors"][0]["is_current_marker_author"])
        self.assertFalse(naples["authors"][1]["is_current_marker_author"])
        self.assertFalse(trento["authors"][0]["is_current_marker_author"])
        self.assertTrue(trento["authors"][1]["is_current_marker_author"])

    def test_chinese_surname_first_authors_match_curated_western_order(self):
        paper = {
            "title": "人工智能生成图像检测技术综述",
            "year": 2026,
            "doi": "10.11834/jig.250053",
            "authors": [
                "Li Meiling",
                "Qian Zhenxing",
                "Zhang Xinpeng",
            ],
        }
        marker = {
            **paper,
            "institution": "Fudan University",
            "institution_id": "institution:fudan",
            "institution_authors": [
                "Meiling Li",
                "Zhenxing Qian",
                "Xinpeng Zhang",
            ],
            "source_database": "curated",
        }

        add_public_detail_fields([paper], [marker])

        self.assertEqual(
            [author["affiliation_indices"] for author in paper["authors"]],
            [[1], [1], [1]],
        )
        self.assertEqual(
            [
                author["name"]
                for author in marker["authors"]
                if author["is_current_marker_author"]
            ],
            ["Li Meiling", "Qian Zhenxing", "Zhang Xinpeng"],
        )
        self.assertEqual(
            {mapping["source"] for mapping in paper["author_affiliation_indices"]},
            {"curated_admin"},
        )

    def test_one_author_can_have_multiple_affiliations(self):
        paper = {
            "title": "Multiple affiliations",
            "year": 2024,
            "doi": "10.1000/multiple-affiliations",
            "authors": ["Li Meiling", "Jane Doe"],
        }
        first = {
            **paper,
            "institution": "First University",
            "institution_id": "institution:first",
            "institution_authors": ["Meiling Li"],
            "source_database": "curated",
        }
        second = {
            **paper,
            "institution": "Second University",
            "institution_id": "institution:second",
            "institution_authors": ["Li Meiling", "Jane Doe"],
            "source_database": "curated",
        }

        add_public_detail_fields([paper], [first, second])

        self.assertEqual(
            [author["affiliation_indices"] for author in paper["authors"]],
            [[1, 2], [2]],
        )
        self.assertTrue(first["authors"][0]["is_current_marker_author"])
        self.assertFalse(first["authors"][1]["is_current_marker_author"])
        self.assertTrue(second["authors"][0]["is_current_marker_author"])
        self.assertTrue(second["authors"][1]["is_current_marker_author"])

    def test_paper_level_affiliation_does_not_fabricate_author_mapping(self):
        paper = {
            "title": "Manual paper",
            "year": 2021,
            "authors": ["Unmapped Author"],
            "affiliations": ["Known University"],
        }

        add_public_detail_fields([paper], [])

        self.assertEqual(paper["affiliations"][0]["name"], "Known University")
        self.assertEqual(paper["authors"][0]["affiliation_indices"], [])
        self.assertEqual(
            paper["author_affiliation_indices"][0]["source"], "unmapped"
        )
        self.assertFalse(
            paper["author_affiliation_indices"][0]["fallback"]
        )
        self.assertFalse(paper["authors"][0]["is_current_marker_author"])

    def test_curated_mapping_outranks_stale_raw_author_mapping(self):
        paper = {
            "title": "Admin mapping priority",
            "year": 2024,
            "authors": ["Ada Researcher"],
            "author_institution_affiliations": [
                {
                    "index": 1,
                    "institution": "Stale University",
                    "authors": ["Ada Researcher"],
                },
                {
                    "index": 2,
                    "institution": "Curated University",
                    "authors": ["Ada Researcher"],
                    "mapping_source": "curated_admin",
                    "mapping_fallback": False,
                },
            ],
        }

        add_public_detail_fields([paper], [])

        self.assertEqual(paper["authors"][0]["affiliation_indices"], [2])
        self.assertEqual(
            paper["author_affiliation_indices"][0]["source"],
            "curated_admin",
        )
        self.assertFalse(
            paper["author_affiliation_indices"][0]["fallback"]
        )

    def test_author_order_preserved_from_paper_metadata(self):
        paper = {
            "title": "Paper order wins",
            "year": 2024,
            "doi": "10.1000/paper-order",
            "authors": [
                "Author One",
                "Author Two",
                "Unmapped Author",
                "Author Three",
                "Author Four",
            ],
        }
        first_institution = {
            **paper,
            "institution": "First University",
            "institution_id": "institution:first",
            "institution_authors": [
                "Author One",
                "Author Three",
                "Mapping-only Author",
            ],
        }
        second_institution = {
            **paper,
            "institution": "Second University",
            "institution_id": "institution:second",
            "institution_authors": ["Author Two", "Author Four"],
        }

        add_public_detail_fields(
            [paper], [first_institution, second_institution]
        )

        self.assertEqual(
            [author["name"] for author in paper["authors"]],
            [
                "Author One",
                "Author Two",
                "Unmapped Author",
                "Author Three",
                "Author Four",
            ],
        )
        self.assertEqual(
            [
                author["affiliation_indices"]
                for author in paper["authors"]
            ],
            [[1], [2], [], [1], [2]],
        )

    def test_mapping_authors_are_fallback_when_paper_authors_are_missing(self):
        self.assertEqual(
            _ordered_mapping_authors([], ["Mapped One", "Mapped Two"]),
            ["Mapped One", "Mapped Two"],
        )
        paper = {
            "title": "Mapping-only author source",
            "year": 2024,
            "doi": "10.1000/mapping-only",
            "authors": [],
        }
        marker = {
            **paper,
            "institution": "Fallback University",
            "institution_id": "institution:fallback",
            "institution_authors": ["Mapped One", "Mapped Two"],
        }

        add_public_detail_fields([paper], [marker])

        self.assertEqual(
            [author["name"] for author in paper["authors"]],
            ["Mapped One", "Mapped Two"],
        )
        self.assertEqual(
            [
                author["affiliation_indices"]
                for author in paper["authors"]
            ],
            [[1], [1]],
        )

    def test_legacy_detail_fields_migrate_without_fabricated_indices(self):
        paper = {
            "title": "Legacy schema migration",
            "year": 2021,
            "doi": "10.1000/legacy",
            "authors": "Doe, Jane; John Roe",
            "affiliations": "Legacy Paper University",
        }
        marker = {
            **paper,
            "affiliations": [],
            "current_institution": "Legacy Marker University",
        }

        add_public_detail_fields([paper], [marker])

        self.assertEqual(
            [author["name"] for author in paper["authors"]],
            ["Doe, Jane", "John Roe"],
        )
        self.assertTrue(
            all(
                author["affiliation_indices"] == []
                for author in paper["authors"]
            )
        )
        self.assertEqual(
            [affiliation["name"] for affiliation in paper["affiliations"]],
            ["Legacy Paper University", "Legacy Marker University"],
        )
        self.assertIsInstance(marker["current_institution"], dict)
        self.assertEqual(
            marker["current_institution"]["name"],
            "Legacy Marker University",
        )

    def test_incremental_learning_regression_mapping(self):
        title = (
            "Incremental learning for the detection and classification "
            "of GAN-generated images"
        )
        paper = {
            "title": title,
            "year": 2019,
            "doi": "10.1109/wifs47025.2019.9035099",
            "authors": [
                "Marra, Francesco",
                "Saltori, Cristiano",
                "Boato, Giulia",
                "Luisa Verdoliva",
            ],
            "author_institution_affiliations": [
                {
                    "index": 1,
                    "institution_id": "institution:naples",
                    "institution": "University of Naples Federico II",
                    "authors": ["Francesco Marra", "Luisa Verdoliva"],
                },
                {
                    "index": 2,
                    "institution_id": "institution:trento",
                    "institution": "University of Trento",
                    "authors": ["Cristiano Saltori", "Giulia Boato"],
                },
            ],
        }
        naples = {
            **paper,
            "institution": "University of Naples Federico II",
            "institution_id": "institution:naples",
            "institution_authors": ["Francesco Marra", "Luisa Verdoliva"],
        }
        trento = {
            **paper,
            "institution": "University of Trento",
            "institution_id": "institution:trento",
            "institution_authors": ["Cristiano Saltori", "Giulia Boato"],
        }

        add_public_detail_fields([paper], [naples, trento])

        self.assertEqual(
            [author["affiliation_indices"] for author in paper["authors"]],
            [[1], [2], [2], [1]],
        )
        self.assertEqual(
            [
                author["name"]
                for author in naples["authors"]
                if author["is_current_marker_author"]
            ],
            ["Marra, Francesco", "Luisa Verdoliva"],
        )
        self.assertEqual(
            [
                author["name"]
                for author in trento["authors"]
                if author["is_current_marker_author"]
            ],
            ["Saltori, Cristiano", "Boato, Giulia"],
        )

    def test_latent_recovery_mapping_uses_mapping_author_roster(self):
        title = (
            "Did You Use My GAN to Generate Fake? Post-hoc Attribution of "
            "GAN Generated Images via Latent Recovery"
        )
        paper = {
            "title": title,
            "year": 2022,
            "doi": "10.1109/ijcnn55064.2022.9892704",
            "authors": [
                "Syou Hirofumi, Kazuto Fukuchi, Youhei Akimoto, Jun Sakuma"
            ],
        }
        tsukuba = {
            **paper,
            "institution": "University of Tsukuba",
            "institution_id": "institution:tsukuba",
            "institution_authors": [
                "Syou Hirofumi",
                "Kazuto Fukuchi",
                "Youhei Akimoto",
                "Jun Sakuma",
            ],
        }
        riken = {
            **paper,
            "institution": "RIKEN Center for Advanced Intelligence Project",
            "institution_id": "institution:riken",
            "institution_authors": ["Jun Sakuma"],
        }

        add_public_detail_fields([paper], [tsukuba, riken])

        expected_indices = [[1], [1], [1], [1, 2]]
        self.assertEqual(
            [author["affiliation_indices"] for author in paper["authors"]],
            expected_indices,
        )
        self.assertTrue(
            all(
                not author["is_current_marker_author"]
                for author in paper["authors"]
            )
        )
        self.assertEqual(
            [
                author["is_current_marker_author"]
                for author in tsukuba["authors"]
            ],
            [True, True, True, True],
        )
        self.assertEqual(
            [
                author["is_current_marker_author"]
                for author in riken["authors"]
            ],
            [False, False, False, True],
        )

    def test_generated_previews_have_fewer_unsplit_mapped_author_lines(self):
        repository = Path(__file__).resolve().parents[1]
        target_title = (
            "Did You Use My GAN to Generate Fake? Post-hoc Attribution of "
            "GAN Generated Images via Latent Recovery"
        )
        limits = {
            "public_preview_map_data.json": 41,
            "public_preview_papers.json": 21,
        }
        for filename, maximum in limits.items():
            with (repository / "web" / "data" / filename).open(
                encoding="utf-8"
            ) as handle:
                records = json.load(handle)["records"]
            bad = [
                record for record in records
                if is_bad_author_candidate(record)
            ]
            self.assertLessEqual(len(bad), maximum, filename)
            self.assertNotIn(
                target_title,
                {record.get("title") for record in bad},
                filename,
            )

    def test_source_attribution_survey_author_order_regression(self):
        repository = Path(__file__).resolve().parents[1]
        title = "Source Attribution of AI-Generated Images: a Principled Survey"
        expected_names = [
            "Meiling Li",
            "Benedetta Tondi",
            "Pietro Bongini",
            "Zhenxing Qian",
            "Xinpeng Zhang",
            "Mauro Barni",
        ]
        expected_indices = [[1], [2], [2], [1], [1], [2]]

        for filename in (
            "public_preview_map_data.json",
            "public_preview_papers.json",
        ):
            with (repository / "web" / "data" / filename).open(
                encoding="utf-8"
            ) as handle:
                records = json.load(handle)["records"]
            matches = [
                record for record in records
                if record.get("title") == title
            ]
            self.assertTrue(matches, filename)
            for record in matches:
                names = [author["name"] for author in record["authors"]]
                self.assertEqual(names, expected_names, filename)
                self.assertNotIn("Xi Zhang", names, filename)
                self.assertLess(
                    names.index("Benedetta Tondi"),
                    names.index("Zhenxing Qian"),
                )
                self.assertLess(
                    names.index("Pietro Bongini"),
                    names.index("Zhenxing Qian"),
                )
                self.assertEqual(names[0], "Meiling Li")
                self.assertEqual(names[-1], "Mauro Barni")
                self.assertEqual(
                    [
                        author["affiliation_indices"]
                        for author in record["authors"]
                    ],
                    expected_indices,
                    filename,
                )
                active_names = [
                    author["name"]
                    for author in record["authors"]
                    if author["is_current_marker_author"]
                ]
                expected_active = {
                    "Fudan University": [
                        "Meiling Li",
                        "Zhenxing Qian",
                        "Xinpeng Zhang",
                    ],
                    "University of Siena": [
                        "Benedetta Tondi",
                        "Pietro Bongini",
                        "Mauro Barni",
                    ],
                    None: [],
                }
                self.assertEqual(
                    active_names,
                    expected_active[record.get("institution")],
                    filename,
                )

    def test_evoguard_curated_author_mapping_regression(self):
        repository = Path(__file__).resolve().parents[1]
        title = (
            "EvoGuard: An Extensible Agentic RL-based Framework for Practical "
            "and Evolving AI-Generated Image Detection"
        )
        expected = {
            "Chenyang Zhu": [1, 2],
            "Maorong Wang": [2],
            "Jun O. Liu": [2],
            "Ching-Chun Chang": [2],
            "Isao Echizen": [1, 2],
        }
        for filename in (
            "public_preview_map_data.json",
            "public_preview_papers.json",
        ):
            with (repository / "web" / "data" / filename).open(
                encoding="utf-8"
            ) as handle:
                records = json.load(handle)["records"]
            matches = [
                record for record in records if record.get("title") == title
            ]
            self.assertTrue(matches, filename)
            for record in matches:
                self.assertEqual(
                    {
                        author["name"]: author["affiliation_indices"]
                        for author in record["authors"]
                    },
                    expected,
                    filename,
                )
                self.assertEqual(
                    {
                        mapping["source"]
                        for mapping in record["author_affiliation_indices"]
                    },
                    {"curated_admin"},
                    filename,
                )

    def test_frontend_renders_numbers_and_current_author_bold(self):
        helper = (
            Path(__file__).resolve().parents[1]
            / "web"
            / "paper_details_helpers.js"
        )
        node = Path(
            "/Users/meilinger/.cache/codex-runtimes/"
            "codex-primary-runtime/dependencies/node/bin/node"
        )
        script = """
const helpers = require(process.argv[1]);
const html = helpers.renderPaperAuthors(
  {authors: [
    {name: "Jane Doe", affiliation_indices: [1, 2], is_current_marker_author: true},
    {name: "John Roe", affiliation_indices: [], is_current_marker_author: false},
  ]},
  (value) => value,
  1,
);
process.stdout.write(JSON.stringify(html));
"""
        result = subprocess.run(
            [str(node), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)

        self.assertIn(">1,2</sup>", rendered)
        self.assertIn('<strong class="current-institution-author">', rendered)
        self.assertNotIn("John Roe<sup", rendered)

    def test_frontend_legacy_name_fallback_matches_reversed_order_safely(self):
        helper = (
            Path(__file__).resolve().parents[1]
            / "web"
            / "paper_details_helpers.js"
        )
        node = Path(
            "/Users/meilinger/.cache/codex-runtimes/"
            "codex-primary-runtime/dependencies/node/bin/node"
        )
        script = """
const helpers = require(process.argv[1]);
process.stdout.write(JSON.stringify({
  reversed: helpers.namesMatch("Li Meiling", "Meiling Li"),
  unrelated: helpers.namesMatch("Li Wei", "Wei Zhang"),
}));
"""
        result = subprocess.run(
            [str(node), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            json.loads(result.stdout),
            {"reversed": True, "unrelated": False},
        )

    def test_frontend_paper_links_normalize_and_deduplicate_targets(self):
        helper = (
            Path(__file__).resolve().parents[1]
            / "web"
            / "paper_link_helpers.js"
        )
        node = Path(
            "/Users/meilinger/.cache/codex-runtimes/"
            "codex-primary-runtime/dependencies/node/bin/node"
        )
        script = """
const helpers = require(process.argv[1]);
const normalize = (links) => helpers.deduplicatePaperLinks(links);
process.stdout.write(JSON.stringify({
  arxivHttp: normalize([
    {label: "Paper", url: "http://arxiv.org/pdf/2603.01878.pdf/"},
    {label: "arXiv", url: "https://arxiv.org/abs/2603.01878"},
    {label: "OpenAlex", url: "https://openalex.org/W1"},
  ]),
  doiSlash: normalize([
    {label: "Paper", url: "http://dx.doi.org/10.1145/123/"},
    {label: "DOI", url: "https://doi.org/10.1145/123"},
  ]),
  openalexHttp: normalize([
    {label: "Paper", url: "http://openalex.org/W123/"},
    {label: "OpenAlex", url: "https://openalex.org/W123"},
  ]),
  distinct: normalize([
    {label: "Paper", url: "https://publisher.example/paper"},
    {label: "DOI", url: "https://doi.org/10.1145/123"},
    {label: "arXiv", url: "https://arxiv.org/abs/2401.12345"},
    {label: "OpenAlex", url: "https://openalex.org/W1"},
  ]),
  empty: normalize([
    {label: "Paper", url: ""},
    {label: "DOI", url: "javascript:alert(1)"},
  ]),
}));
"""
        result = subprocess.run(
            [str(node), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)

        self.assertEqual(
            [link["label"] for link in rendered["arxivHttp"]],
            ["arXiv", "OpenAlex"],
        )
        self.assertEqual(
            [link["label"] for link in rendered["doiSlash"]],
            ["DOI"],
        )
        self.assertEqual(
            [link["label"] for link in rendered["openalexHttp"]],
            ["OpenAlex"],
        )
        self.assertEqual(
            [link["label"] for link in rendered["distinct"]],
            ["Paper", "DOI", "arXiv", "OpenAlex"],
        )
        self.assertEqual(rendered["empty"], [])

    def test_frontend_renders_public_paper_links(self):
        helper = (
            Path(__file__).resolve().parents[1]
            / "web"
            / "paper_link_helpers.js"
        )
        node = Path(
            "/Users/meilinger/.cache/codex-runtimes/"
            "codex-primary-runtime/dependencies/node/bin/node"
        )
        script = """
const helpers = require(process.argv[1]);
const published = (record) => helpers.publishedVersionUrl(record);
const links = (record, arxivUrl = "") => helpers.paperVersionLinks(record, arxivUrl);
process.stdout.write(JSON.stringify({
  publisherPreferred: published({
    paper_url: "https://publisher.example/article/1",
    doi: "10.1000/example",
    proceedings_url: "https://venue.example/paper/1",
  }),
  doiResolved: published({doi: "doi:10.1000/example"}),
  venueFallback: published({proceedings_url: "https://venue.example/paper/1"}),
  preprintOnly: published({
    paper_url: "https://arxiv.org/abs/2401.12345",
    doi: "10.48550/arXiv.2401.12345",
  }),
  missing: published({openalex_url: "https://openalex.org/W1"}),
  publishedCard: links({
    publisher_url: "https://publisher.example/article/1",
    doi: "10.1000/example",
    openalex_url: "https://openalex.org/W1",
  }, "https://arxiv.org/abs/2401.12345"),
  doiCard: links({
    doi: "10.1000/example",
    openalex_url: "https://openalex.org/W1",
  }),
  preprintCard: links({
    arxiv_url: "https://arxiv.org/abs/2401.12345",
    openalex_url: "https://openalex.org/W1",
  }),
  openAlexOnlyCard: links({openalex_url: "https://openalex.org/W1"}),
  missingCard: links({paper_url: "", arxiv_url: ""}),
}));
"""
        result = subprocess.run(
            [str(node), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            json.loads(result.stdout),
            {
                "publisherPreferred": "https://publisher.example/article/1",
                "doiResolved": "https://doi.org/10.1000/example",
                "venueFallback": "https://venue.example/paper/1",
                "preprintOnly": "",
                "missing": "",
                "publishedCard": [
                    {
                        "label": "Paper",
                        "url": "https://publisher.example/article/1",
                    },
                    {
                        "label": "Preprint",
                        "url": "https://arxiv.org/abs/2401.12345",
                    },
                ],
                "doiCard": [
                    {
                        "label": "Paper",
                        "url": "https://doi.org/10.1000/example",
                    }
                ],
                "preprintCard": [
                    {
                        "label": "Preprint",
                        "url": "https://arxiv.org/abs/2401.12345",
                    }
                ],
                "openAlexOnlyCard": [],
                "missingCard": [],
            },
        )

    def test_validator_warns_for_missing_mapping_without_crashing(self):
        record = {
            "title": "Partially mapped",
            "authors": [
                {
                    "name": "Unmapped Author",
                    "affiliation_indices": [],
                    "is_current_marker_author": False,
                }
            ],
            "affiliations": [
                {
                    "index": 1,
                    "name": "Known University",
                    "institution_id": "institution:known",
                    "country": "",
                    "region": "",
                }
            ],
            "author_affiliation_indices": [
                {
                    "author": "Unmapped Author",
                    "indices": [],
                    "institution_ids": [],
                    "source": "unmapped",
                    "fallback": False,
                }
            ],
            "current_institution": None,
        }
        issues = []

        validate_paper_detail_schema(
            0, record, issues, marker_record=False
        )

        self.assertFalse(
            any(issue.level == "ERROR" for issue in issues)
        )
        validate_paper_record(0, record, issues)
        self.assertTrue(
            any(
                issue.level == "WARNING"
                and "no institution index" in issue.message
                for issue in issues
            )
        )

    def test_validator_rejects_invalid_mapping_indices_and_current_institution(self):
        record = {
            "title": "Invalid mapping",
            "authors": [
                {
                    "name": "Ada Researcher",
                    "affiliation_indices": [1, 1],
                    "is_current_marker_author": True,
                }
            ],
            "affiliations": [
                {
                    "index": 1,
                    "name": "",
                    "institution_id": "institution:one",
                    "country": "",
                    "region": "",
                }
            ],
            "author_affiliation_indices": [
                {
                    "author": "Ada Researcher",
                    "indices": [2],
                    "institution_ids": ["institution:two"],
                    "source": "raw_affiliation",
                    "fallback": False,
                }
            ],
            "current_institution": {
                "index": 1,
                "name": "Different University",
                "institution_id": "institution:different",
            },
        }
        issues = []

        validate_paper_detail_schema(
            0, record, issues, marker_record=True
        )

        messages = {issue.message for issue in issues}
        self.assertTrue(any("has no name" in message for message in messages))
        self.assertTrue(
            any("duplicate affiliation indices" in message for message in messages)
        )
        self.assertTrue(
            any("unknown affiliation index" in message for message in messages)
        )
        self.assertIn(
            "marker current institution does not match affiliation list",
            messages,
        )

    def setUp(self):
        self.preprint = {
            "title": "A Siamese-based Verification System",
            "year": 2023,
            "venue": "arXiv (Cornell University)",
            "publication_type": "preprint",
            "doi": "10.48550/arxiv.2307.09822",
            "is_arxiv_preprint": True,
        }
        self.formal = {
            "title": "a siamese based verification system",
            "year": 2024,
            "venue": "Pattern Recognition Letters",
            "publication_type": "journal",
            "doi": "10.1016/j.patrec.2024.03.002",
            "is_arxiv_preprint": False,
            "authors": ["Lydia Abady"],
            "institution": "University of Siena",
            "country": "Italy",
            "latitude": 43.31822,
            "longitude": 11.33064,
        }

    def test_formal_version_wins_across_title_punctuation_and_case(self):
        records, excluded = exclude_preprint_versions(
            [self.preprint, self.formal]
        )

        self.assertEqual(excluded, 1)
        self.assertEqual(records, [self.formal])
        self.assertEqual(records[0]["doi"], self.formal["doi"])
        self.assertEqual(records[0]["authors"], self.formal["authors"])
        self.assertEqual(records[0]["institution"], self.formal["institution"])
        self.assertEqual(records[0]["latitude"], self.formal["latitude"])

    def test_formal_doi_and_venue_override_stale_preprint_flag(self):
        formal = {**self.formal, "is_arxiv_preprint": True}

        records, excluded = exclude_preprint_versions(
            [self.preprint, formal]
        )

        self.assertEqual(excluded, 1)
        self.assertEqual(records, [formal])

    def test_preprint_without_formal_version_is_retained(self):
        records, excluded = exclude_preprint_versions([self.preprint])

        self.assertEqual(excluded, 0)
        self.assertEqual(records, [self.preprint])

    def test_validator_rejects_unfiltered_preprint_formal_pair(self):
        issues = []

        validate_preprint_version_duplicates(
            [self.preprint, self.formal],
            issues,
        )

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].level, "ERROR")
        self.assertIn("duplicates a formal publication", issues[0].message)


if __name__ == "__main__":
    unittest.main()

"""Exact public-UI successor expectations for four historical audit tests.

Keep historical data/report receipts immutable. Check the reviewed current UI
bytes separately before replaying an audit against its archived frontend.
"""

import hashlib
import json
from pathlib import Path
import subprocess

from scripts.gap_migration_history import EVIDENCE, historical_bytes


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "tests/fixtures/public_website_refinement_2026_10_01.json"

# The fixture records the reviewed 2026-10-01 frontend, while source_head in
# that fixture identifies the earlier corpus baseline. Keep those contracts distinct.
REFINEMENT_COMMIT = "3c0a5fbc25d7434cf4c80de27aae16fc8761a921"
LEAFLET_SRI_PREDECESSOR = "d02b952489b10df438f79ed1b87aee4170ee8aa5"
LEAFLET_SRI_SUCCESSOR = "c589f61b628b787251410964ed50a0fe696a4038"
LEAFLET_INDEX_BEFORE = "ba43571ce429f16d422277597d7e51d95ca1f612d08ecfb02aba18bb8dbf3f58"
LEAFLET_INDEX_AFTER = "f080d23a34c9863eb439b857eb2bf9032b80b8abb659631d6b49ac5de58510c1"
PUBLISHED_FRONTEND_SUCCESSORS = (
    ("c514bea1dbd7645dc4baed49819f14764b9f177b", (
        "tests/test_public_header_metadata.py",
    )),
    ("8b7edb7cd4834ac9f418776220b10442c49e7ee5", (
        "tests/test_frontend_adaptive_details.py",
        "tests/test_frontend_chart_filters.py",
        "tests/test_frontend_interaction_model.py",
        "tests/test_frontend_marker_sizing.py",
        "tests/test_frontend_no_results_recovery.py",
        "tests/test_frontend_public_labels_layout.py",
        "tests/test_frontend_sticky_public_layout.py",
        "tests/test_frontend_year_range_slider.py",
        "web/app.js",
        "web/index.html",
        "web/style.css",
    )),
    # Published scholarly-explorer successor; pin its four overlapping UI/test
    # paths to that commit, leaving the older refinement receipts untouched.
    ("f7e6f721dcca4c992285a86f3fc75706d6d3f091", (
        "tests/public_feature_freeze_browser.cjs",
        "tests/test_frontend_country_institution_type_filters.py",
        "tests/test_frontend_year_range_slider.py",
        "web/app.js",
        "web/index.html",
        "web/style.css",
    )),
    # Later published desktop successor; keep each changed historical path
    # tied to that exact commit instead of reading mutable current bytes.
    ("ef0d93fa2658c532fff54df2bfaf21fec65f5b57", (
        "tests/public_accessibility_browser.cjs",
        "tests/test_frontend_chart_filters.py",
        "tests/test_frontend_public_labels_layout.py",
        # result_cards is archived by the pre-gap manifest and stays frozen there.
        "tests/test_frontend_year_range_slider.py",
        "web/app.js",
        "web/index.html",
        "web/methodology.html",
        "web/style.css",
    )),
    # Only the published, byte-verified Leaflet stylesheet integrity correction.
    (LEAFLET_SRI_SUCCESSOR, ("web/index.html",)),
)


def committed_bytes(commit, relative):
    return subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=ROOT)


def committed_digest(commit, relative):
    value = committed_bytes(commit, relative)
    return hashlib.sha256(value).hexdigest()


def assert_leaflet_sri_transition():
    parent = subprocess.check_output(
        ["git", "rev-parse", LEAFLET_SRI_SUCCESSOR + "^"], cwd=ROOT, text=True
    ).strip()
    assert parent == LEAFLET_SRI_PREDECESSOR, "Unexpected Leaflet predecessor"
    before = committed_bytes(LEAFLET_SRI_PREDECESSOR, "web/index.html")
    after = committed_bytes(LEAFLET_SRI_SUCCESSOR, "web/index.html")
    assert hashlib.sha256(before).hexdigest() == LEAFLET_INDEX_BEFORE
    assert hashlib.sha256(after).hexdigest() == LEAFLET_INDEX_AFTER
    old = b"sha256-p4NxAoJBhIINfQ3ynhymWCqKZs17ecT2n7GqrE/Tq4g="
    new = b"sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
    assert before.count(old) == 1
    assert before.replace(old, new, 1) == after, "Unreviewed Leaflet HTML delta"


def assert_public_refinement_snapshot():
    assert_leaflet_sri_transition()
    expected = {
        relative: digest
        for relative, digest in json.loads(SNAPSHOT.read_text(encoding="utf-8"))["sha256"].items()
        if Path(relative).name != ".DS_Store"
    }
    # Check the immutable snapshot against the commit that introduced it,
    # including files that have since been changed by approved UI successors.
    for relative, digest in expected.items():
        assert committed_digest(REFINEMENT_COMMIT, relative) == digest, relative

    # The committed branding successor predates this migration. Keep the old
    # fixture intact and verify this separately recorded delta against the
    # pre-migration hashes; never approve changes by reading current bytes.
    branding = json.loads((EVIDENCE / "preexisting_branding_snapshot.json").read_text())
    baseline = json.loads((EVIDENCE / "baseline.json").read_text())["tracked_sha256"]
    for relative, digest in branding["sha256"].items():
        if Path(relative).name == ".DS_Store":
            continue
        assert baseline[relative] == digest
        assert committed_digest(branding["source_commit"], relative) == digest
        expected[relative] = digest
    # Later published commits changed eight fixture paths and four other tests.
    # Take reviewed bytes from fixed commits, so an unreviewed edit still fails.
    for commit, paths in PUBLISHED_FRONTEND_SUCCESSORS:
        for relative in paths:
            expected[relative] = committed_digest(commit, relative)

    actual = {
        relative: hashlib.sha256(historical_bytes(ROOT / relative)).hexdigest()
        for relative in expected
    }
    assert actual == expected, "Public refinement differs from its reviewed snapshot"
    expected_frontend = sorted(name for name in expected if name.startswith("web/"))
    current_frontend = sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "web").glob("*")
        if path.is_file() and path.name != ".DS_Store"
    )
    assert current_frontend == expected_frontend
    return expected


# Explicitly reviewed B1A successor, not a blanket exception for test files.
# The predecessor is pinned to the published pre-B1A commit. The new digest
# covers the complete reviewed test, including its original assertions.
B1A_TEST_SUCCESSOR = {
    "path": "tests/test_institution_type_audit.py",
    "predecessor_commit": "91de08a904847c47f60eb3dfd124e3db3300a459",
    "predecessor_sha256": "319d131f4e1b5a4354e52fd190f1f96859815661e4c101159a1a076502130c9b",
    "reviewed_sha256": "b6e31618daacbd3e0bea7919fee7ebcdd1805cb78e7b7aa99a226f0bd2b3b1d6",
}


def assert_b1a_test_successor():
    entry = B1A_TEST_SUCCESSOR
    relative = entry["path"]
    assert committed_digest(entry["predecessor_commit"], relative) == entry["predecessor_sha256"], relative
    actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
    assert actual == entry["reviewed_sha256"], "Unreviewed B1A test successor: " + relative
    return {relative: actual}


def assert_historical_integrity_with_public_refinement(integrity, baseline):
    expected = {**assert_public_refinement_snapshot(), **assert_b1a_test_successor()}
    result = integrity()
    # The original audit still verifies every protected path and its prior
    # data-migration receipts. Only these byte-checked UI/test changes are new.
    # Keep exact path equality: any additional path still fails both guards.
    changed = sorted(
        relative
        for relative, digest in expected.items()
        if relative in baseline
        and baseline[relative] != digest
        and relative not in result["authorized_successor_changes"]
    )
    assert sorted(result["changed_paths"]) == changed
    assert result["changed_count"] == len(changed)
    assert result["protected_files_checked"] == len(baseline)


def historical_normal_priority_diff(tmp_path, monkeypatch):
    import report_systematic_tier2_normal_priority_evidence as report

    expected = assert_public_refinement_snapshot()
    baseline = json.loads((report.OUT / "baseline_sha256.json").read_text(encoding="utf-8"))
    frontend = {
        name: digest
        for name, digest in baseline.items()
        if name.startswith("web/")
        and not name.startswith("web/data/")
    }
    current_frontend = {name for name in expected if name.startswith("web/")}
    semantic_frontend = {name for name in frontend if Path(name).name != ".DS_Store"}
    assert current_frontend == semantic_frontend | {
        "web/methodology.html", "web/paper_search_helpers.js",
    }

    historical_root = tmp_path / "historical-normal-priority-audit"
    (historical_root / "web").mkdir(parents=True)
    for relative, digest in frontend.items():
        archived = (report.OUT / "baseline" / relative).read_bytes()
        assert hashlib.sha256(archived).hexdigest() == digest, relative
        (historical_root / relative).write_bytes(archived)
    # The report reads checksum-verified pre-gap data through its historical
    # reader. Current-corpus deltas are validated independently by migration tests.
    (historical_root / "data").symlink_to(ROOT / "data", target_is_directory=True)
    with monkeypatch.context() as context:
        context.setattr(report, "ROOT", historical_root)
        return report.diff_audit()

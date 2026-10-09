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
)


def committed_digest(commit, relative):
    value = subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=ROOT)
    return hashlib.sha256(value).hexdigest()


def assert_public_refinement_snapshot():
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


def assert_historical_integrity_with_public_refinement(integrity, baseline):
    expected = assert_public_refinement_snapshot()
    result = integrity()
    # The original audit still verifies every protected path and its prior
    # data-migration receipts. Only these byte-checked UI/test changes are new.
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

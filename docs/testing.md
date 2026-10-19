# Reproducible offline tests

Use a disposable checkout with complete local Git history. Historical tests read
fixed commit objects as well as archived files; a shallow source archive is not
sufficient. The validated runtime is Python 3.14.7, pytest 9.1.1,
pytest-subtests 0.15.0 and Node 24.19.0. Python test dependencies are pinned in
`requirements-test.txt`. Put `node` on PATH so JavaScript-backed tests run.

From the repository root, create an isolated worktree and an external environment:

```sh
git worktree add --detach /tmp/sirm-tests HEAD
python3 -m venv /tmp/sirm-test-env
/tmp/sirm-test-env/bin/python -m pip install -r requirements-test.txt
cd /tmp/sirm-tests
node --version
/tmp/sirm-test-env/bin/python scripts/restore_historical_test_fixtures.py
/tmp/sirm-test-env/bin/python scripts/restore_historical_test_fixtures.py --check
/tmp/sirm-test-env/bin/python -m pytest -q tests --junitxml=/tmp/sirm-tests.xml
```

Choose unused scratch paths. Commands work from any current directory when the
script is addressed by its saved path; `--root` can select another disposable
checkout. Tests that create temporary HTTP servers need localhost permission.
The Python suite does not require a browser. Separate browser smoke scripts need
an installed browser and Playwright; they are not dependencies of fixture setup.

The fixture command reuses `literature51_reproducibility.materialize_export_inputs`
for fourteen existing lossless inputs. It restores four historical OS-metadata
paths from three exact, authenticated gzip payloads, and 99 ignored OpenAlex
cache paths from already committed frozen Tier 1 responses. It never requests
OpenAlex or duplicates those response snapshots in Git.

`tests/fixtures/historical_test_fixture_manifest.json` ties each destination to
the original immutable authority, full response/payload SHA-256, source hash and
size. Every source and existing destination is checked before any write; a
missing/corrupt source or a differing destination fails rather than replacing
bytes. Repeated setup is idempotent. `--check` verifies all 117 inputs without
writing. Symlink destinations escaping the checkout are rejected.

Restored files are historical test inputs in the disposable checkout. Canonical
curated tables, reviewed mappings and public exports are never regenerated. The
OS payloads remain under test fixtures in Git and cannot enter normal map data.
All original historical manifests, expected hashes, counts and audit assertions
remain unchanged.

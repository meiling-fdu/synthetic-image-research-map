"""Read immutable audit endpoints with the exporter's preferred public identities."""
from collections import Counter
import csv
from functools import lru_cache
import io
import json
from pathlib import Path
import subprocess

from scripts.curated_export import PaperIdentityCache, PaperIdentityIndex

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATHS = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")


@lru_cache
def published_bytes(ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT)


def csv_records(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


@lru_cache
def published_context(ref):
    """Use each public paper's preferred ID for both paper and map endpoints.

    A map row may omit paper_id when its public paper supplies one (TWIGMA).
    The taxonomy ID is therefore an alias, not a replacement public identity.
    """
    papers, maps = (json.loads(published_bytes(ref, path))["records"] for path in PUBLIC_PATHS)
    registry = csv_records(published_bytes(ref, "data/curated/paper_taxonomy.csv"))
    index = PaperIdentityIndex(registry, PaperIdentityCache())
    by_id, taxonomy, aliases = {}, {}, {}
    for record in papers:
        matches = index.matches(record)
        assert len(matches) == 1, record.get("title")
        entry = matches[0]
        pid = record.get("paper_id") or entry["taxonomy_id"]
        assert pid not in by_id
        by_id[pid], taxonomy[pid] = record, entry
        assert entry["taxonomy_id"] not in aliases
        aliases[entry["taxonomy_id"]] = pid
    pairs = Counter()
    for record in maps:
        matches = index.matches(record)
        assert len(matches) == 1, record.get("id")
        assert matches[0]["taxonomy_id"] in aliases
        pid = aliases[matches[0]["taxonomy_id"]]
        pairs[pid, record["institution_id"]] += 1
    mapped = {pid for pid, _ in pairs}
    assert mapped <= by_id.keys()
    return {"papers": by_id, "taxonomy": taxonomy, "pairs": pairs,
            "taxonomy_to_public_id": aliases, "counts": {
                "public": len(papers),
                "formal": sum(paper["publication_type"] != "preprint" for paper in papers),
                "mapped": len(mapped), "unmapped": len(by_id.keys() - mapped),
                "relationship_rows": len(maps), "unique_paper_institution_pairs": len(pairs)}}

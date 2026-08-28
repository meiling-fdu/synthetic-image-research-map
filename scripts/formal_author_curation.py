"""Plan curated author corrections from a manually verified publication matrix.

This module does not scrape, match names, or merge versions. Callers must inspect
the formal author block first, and persist the resulting plan through the curated
paper/mapping writers with an audit entry. Raw/preprint metadata remains intact.
"""

from copy import deepcopy


def plan_formal_authors(paper, mappings, matrix, *, evidence_url, source_kind):
    """Return canonical names and reindexed mappings without mutating inputs.

    Each matrix row has a one-based ``index``, exact ``name``, and the explicitly
    verified ``mapping_ids`` for that occurrence. Multiple mapping IDs preserve
    multiple affiliations. Empty IDs require an explicit unresolved or
    non-institutional status; they never infer an independent researcher.
    """
    if source_kind != "formal_publication" or not evidence_url.startswith("https://"):
        raise ValueError("A verified formal publication source is required")
    if not matrix or [r["index"] for r in matrix] != list(range(1, len(matrix) + 1)):
        raise ValueError("Matrix indexes must follow formal publication order")
    names = [r["name"] for r in matrix]
    if any(not n.strip() or n != n.strip() for n in names) or len(set(names)) != len(names):
        raise ValueError("Empty/duplicate names require separate occurrence review")
    selected = {m["mapping_id"]: m for m in mappings
                if m["paper_id"] == paper["paper_id"]
                and m["mapping_status"] in {"active", "needs_review"}}
    for row in matrix:
        ids = row["mapping_ids"]
        if len(ids) != len(set(ids)) or set(ids) - selected.keys():
            raise ValueError("Unknown, duplicate, or cross-paper mapping ID")
        if not ids and row.get("status") not in {"unresolved", "non_institutional"}:
            raise ValueError("Unmapped formal authors need an explicit review status")
    updated = []
    for identifier, old in selected.items():
        row = deepcopy(old)
        occurrences = [a for a in matrix if identifier in a["mapping_ids"]]
        if occurrences:
            row.update(institution_authors="; ".join(a["name"] for a in occurrences),
                       author_order="; ".join(str(a["index"]) for a in occurrences),
                       mapping_status="active")
        else:
            # Keep the old occurrence in the curated history, never shift its
            # mapping to the author now occupying its former numeric position.
            row["mapping_status"] = "excluded"
        row["provenance_source"] = "Visually verified formal publication: " + evidence_url
        updated.append(row)
    return {"authors": names, "mappings": updated, "evidence_url": evidence_url}

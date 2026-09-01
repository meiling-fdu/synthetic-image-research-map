"""Normalize paper metadata review and provenance for the public UI.

Only the compact values returned here belong in the public metadata-status
layer. Raw evidence, notes, audit identifiers, and resolver state must stay in
their source records.
"""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence


PUBLIC_STATUSES = ("Verified", "Curated", "Needs review", "Source metadata")
FIELD_ORDER = (
    "title",
    "publication_date",
    "venue",
    "publication_type",
    "doi",
    "arxiv",
    "task_category",
    "affiliations",
)

_NEEDS_REVIEW = {"needs_review", "pending", "pending_review", "unreviewed", "uncertain"}
_VERIFIED = {"reviewed", "verified"}
_CURATED = {"confirmed", "curated", "approved", "active"}


def clean(value: Any) -> str:
    return str(value or "").strip()


def public_status(*internal_values: Any) -> str:
    """Map internal review values to the fixed public vocabulary.

    Precedence is intentional: any unresolved signal wins, then an explicit
    completed review, then accepted curation. An absent or unknown status is
    described without manufacturing a confidence judgment.
    """
    values = {clean(value).casefold().replace("-", "_") for value in internal_values}
    values.discard("")
    if values & _NEEDS_REVIEW:
        return "Needs review"
    if values & _VERIFIED:
        return "Verified"
    if values & _CURATED:
        return "Curated"
    return "Source metadata"


def public_source(value: Any) -> str:
    """Reduce supported source descriptions to a safe public source type."""
    source = clean(value).casefold()
    if not source:
        return ""
    if "crossref" in source:
        return "DOI / Crossref"
    if "arxiv" in source:
        return "arXiv"
    if "openalex" in source:
        return "OpenAlex"
    if source in {"manual", "curated", "manually_confirmed", "curated_admin"}:
        return "Manual curation"
    if "publisher" in source or source.startswith("formal publication"):
        return "Publisher"
    return ""


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return clean(value).casefold() in {"1", "true", "yes", "y"}


def _source_for(record: Mapping[str, Any]) -> str:
    return public_source(record.get("metadata_source")) or public_source(
        record.get("source_database")
    )


def _field(status: str, source: str = "") -> dict[str, str]:
    result = {"status": status}
    if source:
        result["source"] = source
    return result


def metadata_status(
    record: Mapping[str, Any],
    affiliation_evidence: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Build the minimal public review/provenance object for one paper.

    Paper-level review/curation determines ``overall``. Venue, task, and
    affiliation signals can only alter their own field. In this export,
    ``needs_review`` is a derived aggregate (see ``_recalculate_paper_details``
    in curated_export.py), so it is never treated as an independent global
    paper decision.
    """
    internal_review = record.get("review_status")
    internal_curation = record.get("curation_status")
    global_status = public_status(internal_review, internal_curation)
    base_source = _source_for(record)
    fields: dict[str, dict[str, str]] = {}

    if clean(record.get("title")):
        fields["title"] = _field(global_status, base_source)
    if clean(record.get("publication_date")) or clean(
        record.get("publication_year") or record.get("year")
    ):
        fields["publication_date"] = _field(global_status, base_source)
    if clean(record.get("venue") or record.get("venue_name")):
        venue_status = (
            "Needs review"
            if _bool(record.get("venue_review_required"))
            else global_status
        )
        fields["venue"] = _field(venue_status, base_source)
    if clean(record.get("publication_type")):
        fields["publication_type"] = _field(global_status, base_source)
    if clean(record.get("doi")):
        doi_source = (
            "DOI / Crossref"
            if public_source(record.get("metadata_source")) == "DOI / Crossref"
            else base_source
        )
        fields["doi"] = _field(global_status, doi_source)
    if clean(record.get("arxiv_id")):
        fields["arxiv"] = _field(global_status, "arXiv")
    if clean(record.get("task")) or record.get("paper_categories"):
        task_status = (
            "Needs review"
            if clean(record.get("task")).casefold() == "uncertain"
            else global_status
        )
        fields["task_category"] = _field(task_status, base_source)

    affiliation_state = clean(record.get("affiliation_review_state")).casefold()
    affiliations = record.get("affiliations")
    has_affiliations = isinstance(affiliations, list) and bool(affiliations)
    affiliation_sources = []
    affiliation_unresolved = affiliation_state == "unreviewed"
    affiliation_curated = affiliation_state in {"curated", "reviewed_empty"}
    # The public ``needs_review`` flag is recomputed from affiliation coverage,
    # mapping resolution, task uncertainty, and paper review. Once explicit
    # global, venue, and task signals are accounted for, a remaining true flag
    # is localized affiliation/mapping evidence rather than a paper-wide state.
    aggregate_affiliation_review = (
        _bool(record.get("needs_review"))
        and global_status != "Needs review"
        and not _bool(record.get("venue_review_required"))
        and clean(record.get("task")).casefold() != "uncertain"
    )
    affiliation_unresolved = affiliation_unresolved or aggregate_affiliation_review
    for evidence in affiliation_evidence:
        evidence_status = clean(evidence.get("mapping_status")).casefold()
        supported_pending = (
            evidence_status == "needs_review"
            and clean(record.get("curation_status")).casefold() == "needs_review"
            and bool(clean(evidence.get("raw_affiliation")))
            and bool(clean(evidence.get("provenance_source")))
        )
        if evidence_status != "active" and not supported_pending:
            continue
        affiliation_unresolved = affiliation_unresolved or supported_pending
        affiliation_curated = affiliation_curated or evidence_status == "active"
        normalized = public_source(evidence.get("provenance_source"))
        if normalized and normalized not in affiliation_sources:
            affiliation_sources.append(normalized)
    if has_affiliations:
        for affiliation in affiliations:
            if not isinstance(affiliation, Mapping):
                continue
            affiliation_unresolved = affiliation_unresolved or _bool(
                affiliation.get("preliminary")
            )
            for raw_source in affiliation.get("provenance_sources") or ():
                normalized = public_source(raw_source)
                if normalized and normalized not in affiliation_sources:
                    affiliation_sources.append(normalized)
            states = affiliation.get("review_states") or ()
            affiliation_unresolved = affiliation_unresolved or any(
                clean(state).casefold().replace("-", "_") in _NEEDS_REVIEW
                for state in states
            )
    if has_affiliations or affiliation_state or aggregate_affiliation_review:
        if affiliation_unresolved:
            affiliation_status = "Needs review"
        elif affiliation_curated:
            affiliation_status = "Curated"
        else:
            affiliation_status = "Source metadata"
        affiliation_source = (
            affiliation_sources[0]
            if len(affiliation_sources) == 1
            else "Manual curation"
            if affiliation_status == "Curated" and not affiliation_sources
            else ""
        )
        fields["affiliations"] = _field(affiliation_status, affiliation_source)

    ordered_fields = {name: fields[name] for name in FIELD_ORDER if name in fields}
    # The default applies to every present public metadata field. Export only
    # deviations so a reviewed paper remains a small object rather than eight
    # repeated status/source pairs.
    field_overrides = {
        name: value
        for name, value in ordered_fields.items()
        if value.get("status") != global_status
        or value.get("source", "") != base_source
    }
    result: dict[str, Any] = {
        "overall": global_status,
        "default_field_status": global_status,
        "field_overrides": field_overrides,
    }
    if base_source:
        result["source"] = base_source
    return result


def add_public_metadata_status(
    paper_records: Sequence[MutableMapping[str, Any]],
    map_records: Sequence[MutableMapping[str, Any]],
    affiliation_evidence: Sequence[Mapping[str, Any]] = (),
) -> None:
    """Attach one normalized status per paper and copy it to map relationships."""
    def identity(record: Mapping[str, Any]) -> tuple[str, str]:
        doi = clean(record.get("doi")).casefold()
        if doi:
            return ("doi", doi.removeprefix("https://doi.org/"))
        arxiv_id = clean(record.get("arxiv_id")).casefold()
        if arxiv_id:
            return ("arxiv", arxiv_id.removeprefix("arxiv:"))
        openalex = clean(record.get("openalex_url")).casefold().rstrip("/")
        if openalex:
            return ("openalex", openalex.rsplit("/", 1)[-1])
        paper_id = clean(record.get("paper_id"))
        if paper_id:
            return ("paper_id", paper_id)
        return ("title", clean(record.get("title")).casefold())

    def identity_keys(record: Mapping[str, Any]) -> set[tuple[str, str]]:
        keys = {identity(record)}
        for field, kind in (
            ("doi", "doi"), ("arxiv_id", "arxiv"),
            ("openalex_url", "openalex"), ("paper_id", "paper_id"),
        ):
            value = clean(record.get(field)).casefold().rstrip("/")
            if not value:
                continue
            if kind == "doi":
                value = value.removeprefix("https://doi.org/")
            elif kind == "arxiv":
                value = value.removeprefix("arxiv:")
            elif kind == "openalex":
                value = value.rsplit("/", 1)[-1]
            keys.add((kind, value))
        title = clean(record.get("title")).casefold()
        if title:
            keys.add(("title", title))
        return keys

    evidence_by_key: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for evidence in affiliation_evidence:
        for key in identity_keys(evidence):
            evidence_by_key.setdefault(key, []).append(evidence)

    statuses = {}
    for record in paper_records:
        matched = []
        seen = set()
        for key in identity_keys(record):
            for evidence in evidence_by_key.get(key, ()):
                marker = id(evidence)
                if marker not in seen:
                    seen.add(marker)
                    matched.append(evidence)
        statuses[identity(record)] = metadata_status(record, matched)
    for record in paper_records:
        record["metadata_status"] = statuses[identity(record)]
    for record in map_records:
        status = statuses.get(identity(record))
        record["metadata_status"] = status or metadata_status(record)

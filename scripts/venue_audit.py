#!/usr/bin/env python3
"""Conservative, source-preserving venue audit shared by Admin and static exports.

No network is used at runtime. The reviewed registry and checked primary-source
evidence are inputs; generated databases/reports live only in data/processed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import difflib
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

try:
    from .venues import (alias_key, clean_text, canonical_venue_registry,
                         display_venue, resolve_venue, _catalog_index, _stable_id, normalize_venue_track, ALLOWED_VENUE_TRACKS)
except ImportError:
    from venues import (alias_key, clean_text, canonical_venue_registry,
                        display_venue, resolve_venue, _catalog_index, _stable_id, normalize_venue_track, ALLOWED_VENUE_TRACKS)

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_PATH = ROOT / "data/processed/venue_authority_evidence.json"
REPORT_PATH = ROOT / "data/processed/publication_venue_audit.json"
FIELDS = ("year", "publication_type", "venue", "venue_id", "venue_name", "venue_acronym",
          "venue_type", "venue_track")
TYPES = {"conference", "journal", "preprint", "book"}


def evidence_records():
    try:
        from .venue_evidence import crossref_evidence
    except ImportError:
        from venue_evidence import crossref_evidence
    # Explicitly checked websites take precedence over deposited short titles.
    workshop = ROOT / "data/processed/workshop_venue_evidence.json"
    return [*json.loads(workshop.read_text())["venues"],
            *json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))["venues"], *crossref_evidence()[0]]


def series_name(value):
    return bool(re.search(r"lecture notes|\bLNCS\b|\bCCIS\b|communications in computer|transactions on computational science|springer|proceedings|\bvol(?:ume)?[. ]+\d", str(value), re.I))


def enrich_aliases(rows, evidence=None):
    serialized = json.dumps(evidence if evidence is not None else evidence_records(), sort_keys=True)
    source = json.dumps(rows, sort_keys=True)
    return [dict(row) for row in _enriched_alias_cache(source, serialized)]


@lru_cache(maxsize=8)
def _enriched_alias_cache(source, evidence_json):
    return _enrich_aliases(json.loads(source), json.loads(evidence_json))


def _enrich_aliases(rows, evidence):
    """Reuse existing identities; fill blanks, never replace curated short names.

Only a source-backed, explicitly approved type repair may replace a registry
type. Book-series/proceedings ambiguities are proposals, never repairs.
"""
    result = [dict(row) for row in rows]
    for row in result:
        row["venue_track"] = normalize_venue_track(row.get("venue_track"))
    for item in evidence:
        for row in result:
            if row.get("venue_id") in item.get("redirect_ids", []):
                row.update(venue_id=item["venue_id"], venue_name=item["name"],
                           venue_acronym=item["acronym"], venue_type=item["type"], venue_track="Workshop")
    try:
        from .venue_evidence import stable_event
    except ImportError:
        from venue_evidence import stable_event
    # Reconcile only exact stable-name variants with compatible taxonomy. Keep
    # the source CSV untouched and retain old names as searchable aliases.
    preferred = {}
    for row in result:
        if row.get("review_status") != "confirmed" or row.get("venue_type") != "conference":
            continue
        stable, _ = stable_event(row["venue_name"])
        key = (alias_key(stable), row["venue_acronym"], row["venue_type"])
        base_id = re.sub(r":(?:main|workshops|posters|findings)$", "", row["venue_id"])
        row["venue_id"] = preferred.setdefault(key, base_id)
        row["venue_name"] = stable
    for item in evidence if evidence is not None else evidence_records():
        if item.get("review_only"):
            continue
        keys = {alias_key(v) for v in [item["name"], *item.get("aliases", [])]}
        matching = [r for r in result if r.get("review_status") == "confirmed"
                    and (alias_key(r.get("venue_name")) in keys or alias_key(r.get("alias")) in keys)]
        if not matching and item.get("acronym"):
            # IEEE branding variants of an otherwise identical event are not
            # distinct identities; require both the full name and acronym.
            bare = lambda value: re.sub(r"^ieee ", "", alias_key(value))
            matching = [r for r in result if r.get("review_status") == "confirmed"
                        and alias_key(r.get("venue_acronym")) == alias_key(item["acronym"])
                        and bare(r.get("venue_name")) == bare(item["name"])]
        ids = {r["venue_id"] for r in matching}
        if len(ids) > 1:
            continue  # Conflicting registry identities are reviewed, not merged.
        venue_id = next(iter(ids), _stable_id(item["name"], ""))
        current = matching[0] if matching else {}
        if current and current["venue_type"] != item["type"] and not item.get("correct_type"):
            continue
        name = item["name"] if item.get("correct_name") else current.get("venue_name") or item["name"]
        acronym = current.get("venue_acronym") or item.get("acronym", "")
        if acronym in item.get("workshop_aliases", []):
            acronym = item["acronym"]
        if acronym and not current.get("venue_acronym") and any(
                alias_key(other.get("acronym")) == alias_key(acronym)
                and other.get("type") != item["type"] and not other.get("review_only")
                for other in evidence):
            continue  # Cross-type abbreviation collision in the source evidence.
        if acronym and any(alias_key(acronym) in {alias_key(r.get("venue_acronym")), alias_key(r.get("alias")), alias_key(r.get("venue_name"))}
                           and r.get("venue_id") != venue_id for r in result):
            continue  # A publisher's abbreviation is not safe if it collides.
        for row in result:
            if row.get("venue_id") == venue_id:
                row["venue_acronym"] = acronym
                if item.get("correct_name"):
                    row["venue_name"] = name
                if item.get("correct_type"):
                    row["venue_type"] = item["type"]
                    row["venue_track"] = "" if item["type"] != "conference" else row["venue_track"]
        existing_keys = {alias_key(r["alias"]) for r in result if r["venue_id"] == venue_id}
        for value in [item["name"], *item.get("aliases", []), item.get("acronym", "")]:
            if not value or alias_key(value) in existing_keys:
                continue
            if any(r["venue_id"] != venue_id and alias_key(value) in {
                    alias_key(r.get("alias")), alias_key(r.get("venue_acronym")), alias_key(r.get("venue_name"))}
                   for r in result):
                continue
            alias_track = "Workshop" if value in item.get("workshop_aliases", []) else ""
            result.append(dict(alias=value, venue_id=venue_id, venue_name=name,
                               venue_acronym=acronym, venue_type=item["type"], venue_track=alias_track,
                               review_status="confirmed", notes="Primary-source evidence: " + item["source"]))
            existing_keys.add(alias_key(value))
    standalone = {alias_key(item["name"]) for item in evidence if item.get("standalone_workshop")}
    for row in result:
        if alias_key(row["venue_name"]) in standalone and row.get("venue_track") == "Workshop":
            row["venue_track"] = "Main"  # Alias hint describes the primary event, not a nested paper track.
    return result


def source_fingerprint(record):
    values = {f: record.get(f, "") for f in (*FIELDS, "raw_venue", "updated_at")}
    return hashlib.sha256(json.dumps(values, sort_keys=True, default=str).encode()).hexdigest()


def confirmation_fingerprint(record):
    # Bind explicit review to bibliographic identity and venue state, not export
    # formatting or unrelated edits. A later DOI/venue/type change reopens review.
    values = {f: clean_text(record.get(f)) for f in (*FIELDS, "raw_venue", "doi", "title")}
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()


class VenueAudit:
    def __init__(self, aliases, evidence=None, decisions=None):
        try:
            from .venues import _catalog_index as build_catalog
        except ImportError:
            from venues import _catalog_index as build_catalog
        self.aliases = aliases
        self.registry = canonical_venue_registry(aliases)
        self.catalog = build_catalog(aliases)
        self.evidence = evidence if evidence is not None else evidence_records()
        self.evidence_by_key = {}
        for item in self.evidence:
            for value in [item["name"], *item.get("aliases", [])]:
                self.evidence_by_key.setdefault(alias_key(value), item)
        self.full_short_names = {alias_key(item["name"]) for item in self.evidence
                                 if item.get("short_name_is_full")}
        try:
            from .venue_evidence import crossref_evidence, arxiv_publication_status
        except ImportError:
            from venue_evidence import crossref_evidence, arxiv_publication_status
        self.paper_evidence = crossref_evidence()[1] if evidence is None else {}
        self.track_observations = {item["doi"]: item for item in json.loads(
            (ROOT / "data/processed/workshop_venue_evidence.json").read_text()).get("track_observations", [])} if evidence is None else {}
        self.arxiv_status = arxiv_publication_status() if evidence is None else {}
        if decisions is None:
            try:
                from .review_decisions import read_review_decisions
            except ImportError:
                from review_decisions import read_review_decisions
            decisions = read_review_decisions()
        self.confirmations = {match.group(1) for d in decisions
                              if d.get("review_queue") == "publication_venues"
                              and d.get("action") == "no_action_after_review"
                              for match in re.finditer(r"\[venue-state:([a-f0-9]{64})\]", d.get("review_note", ""))}
        self.explicit_conflicts = {match.group(1) for d in decisions
                                  if d.get("review_queue") == "publication_venues" and d.get("action") == "unresolved"
                                  for match in re.finditer(r"\[venue-state:([a-f0-9]{64})\]", d.get("review_note", ""))}
        self.explicit_conflict_notes = {
            match.group(1): clean_text(re.sub(r"\[venue-state:[a-f0-9]{64}\]", "", d.get("review_note", "")))
            for d in decisions
            if d.get("review_queue") == "publication_venues" and d.get("action") == "unresolved"
            for match in re.finditer(r"\[venue-state:([a-f0-9]{64})\]", d.get("review_note", ""))
        }
        identities = defaultdict(set)
        for row in aliases:
            if row.get("review_status") == "confirmed":
                for value in (row.get("alias"), row.get("venue_name"), row.get("venue_acronym")):
                    if value:
                        identities[alias_key(value)].add(row["venue_id"])
        self.duplicates = {key: sorted(ids) for key, ids in identities.items() if len(ids) > 1}

    def paper(self, paper):
        row = dict(paper)
        if "venue_track" in row:
            row["venue_track"] = normalize_venue_track(row["venue_track"])
        if {confirmation_fingerprint(paper), confirmation_fingerprint(row)} & self.confirmations:
            row["venue_label"] = display_venue(row)
            return row, None
        current_type = clean_text(row.get("publication_type")).lower()
        if current_type not in TYPES and current_type not in {"book-chapter", "book chapter", "chapter"}:
            return row, None
        name = clean_text(row.get("venue_name") or row.get("venue"))
        identifier = clean_text(row.get("venue_id"))
        evidence = self.evidence_by_key.get(alias_key(name))
        doi = re.sub(r"^https?://(?:dx\.)?doi.org/", "", clean_text(row.get("doi")), flags=re.I).lower()
        arxiv_id = re.sub(r"v\d+$", "", clean_text(row.get("arxiv_id")))
        fact = self.paper_evidence.get(doi) or self.paper_evidence.get("arxiv:" + arxiv_id) or {}
        prior_selection = fact.get("prior_effective_venue")
        explicit_selection = bool((row.get("curated_record") or {}).get("venue_id") or
                                  str(row.get("paper_id", "")).startswith("curated:") or row.get("metadata_source") == "manual")
        if fact.get("review_only") and prior_selection and not explicit_selection:
            # Rebuilding exports is not a decision on conflicting evidence.
            row.update(prior_selection)
            name, identifier = row["venue_name"], row["venue_id"]
        reasons = []
        standalone_track_review = False
        abbreviation_review = False
        if {confirmation_fingerprint(paper), confirmation_fingerprint(row)} & self.explicit_conflicts:
            # An unresolved venue may concern missing acceptance evidence, not
            # necessarily a publication-type conflict. Retain the saved reason.
            note = next((self.explicit_conflict_notes.get(key) for key in
                         (confirmation_fingerprint(paper), confirmation_fingerprint(row))
                         if self.explicit_conflict_notes.get(key)), "")
            reasons.append(note or "Explicit Admin publication-type override conflicts with the registry; preserve the manual selection until the venue review is confirmed with source evidence.")
        arxiv_status = self.arxiv_status.get(arxiv_id, {})
        if current_type == "preprint" and arxiv_status.get("formal_signal") and not fact.get("name"):
            reasons.append("arXiv reports a formal publication/acceptance or forthcoming book chapter: " +
                           (arxiv_status.get("journal_ref") or arxiv_status.get("comment") or arxiv_status.get("doi")) +
                           ". Verify the final publisher record and venue before reclassifying.")
        if fact.get("title") and row.get("title") and difflib.SequenceMatcher(
                None, alias_key(fact["title"]), alias_key(row["title"])).ratio() < 0.65:
            reasons.append("The DOI title disagrees with this paper; verify the DOI before applying its venue metadata.")
        proposal = {}
        canonical = self.registry.get(identifier)
        resolved = resolve_venue(name, publication_type=current_type,
                                 aliases=self.aliases, catalog=self.catalog)
        matched = self.registry.get(resolved.venue_id) if resolved.ambiguity_status == "resolved" else None
        if canonical is None and matched is None and row.get("raw_venue"):
            raw_resolved = resolve_venue(row["raw_venue"], publication_type=current_type,
                                         aliases=self.aliases, catalog=self.catalog)
            if raw_resolved.ambiguity_status == "resolved":
                resolved = raw_resolved
                matched = self.registry.get(resolved.venue_id)
        proven = None
        if fact.get("name") and not fact.get("review_only"):
            fact_resolved = resolve_venue(fact["name"], publication_type=fact["type"],
                                          aliases=self.aliases, catalog=self.catalog)
            proven = self.registry.get(fact_resolved.venue_id)
        if proven:
            if (canonical or matched) and (canonical or matched)["venue_id"] != proven["venue_id"] and not (series_name(name) or (canonical or matched)["venue_type"] == "preprint"):
                reasons.append("Publisher DOI metadata conflicts with the selected canonical venue; preserve manual selection and verify which version this record describes.")
            else:
                canonical = proven
                matched = proven
                resolved = fact_resolved
                evidence = fact
        if fact.get("review_only"):
            reasons.append(fact["reason"])
        if fact.get("bibliographic_type") == "dissertation":
            reasons.append("The DOI identifies a dissertation, not one of the four supported publication types; review scope and publication version.")
        if identifier and canonical is None and matched is None:
            reasons.append("Stored venue ID is not in the confirmed registry; verify the publication container.")
        if canonical and matched and canonical["venue_id"] != matched["venue_id"] and not proven:
            reasons.append("Stored venue ID and venue name identify different venues; select the correct record.")
        canonical = canonical or matched
        if any(identifier in ids for ids in self.duplicates.values()) or resolved.ambiguity_status == "ambiguous":
            reasons.append("Duplicate/conflicting canonical venue identities share a name or alias; reconcile the registry.")
        if evidence and evidence.get("review_only") and not proven:
            reasons.append(evidence["reason"])
            proposal = dict(venue_name=evidence["name"], venue_type=evidence["type"],
                            venue_acronym=evidence.get("acronym", ""))
        elif canonical:
            proposal = dict(canonical)
            expected = canonical["venue_type"]
            if current_type == "preprint" and expected in {"conference", "journal", "book"} and not proven:
                reasons.append("Preprint has a formal publication venue; verify whether this is the published version or a repository copy.")
            elif current_type != "preprint" and expected == "preprint" and not proven:
                reasons.append("Repository name is being used as a formal venue; verify the actual publication, do not infer preprint status from a deposited copy.")
            elif current_type in {"book", "book-chapter", "book chapter", "chapter"} and expected != "book" and not proven:
                reasons.append("Book/chapter carries a non-book venue; verify chapter versus conference proceedings provenance.")
            elif expected == "book" and current_type != "book":
                reasons.append("Book-series container does not establish the paper type; verify chapter versus conference contribution.")
            if row.get("publication_type_override") and current_type != expected:
                reasons.append("Explicit manually curated publication-type override conflicts with the venue; confirmation required.")
            # Name/abbreviation curation is stronger than an automatic proposal.
            protected = bool(row.get("curated_record") or row.get("is_in_curated_papers")
                             or str(row.get("paper_id", "")).startswith("curated:")
                             or row.get("metadata_source") == "manual")
            if protected and name and matched is None and alias_key(name) != alias_key(canonical["venue_name"]):
                reasons.append("Manually curated venue name conflicts with its canonical ID; preserve it pending confirmation.")
            acronym = clean_text(row.get("venue_acronym"))
            expected_acronym = canonical["venue_acronym"]
            identity_evidence = self.evidence_by_key.get(alias_key(canonical["venue_name"]), {})
            observation = self.track_observations.get(doi, {})
            explicit_track = bool((row.get("curated_record") or {}).get("venue_track") or
                                  row.get("venue_track") and (str(row.get("paper_id", "")).startswith("curated:") or row.get("metadata_source") == "manual"))
            if (not explicit_track and row.get("venue_track") in {None, "", "Main"}
                    and observation.get("venue_id") == canonical["venue_id"]):
                row["venue_track"] = observation["venue_track"]
            official_workshop_acronym = acronym in identity_evidence.get("workshop_aliases", [])
            equivalent_acronyms = {alias_key(expected_acronym), alias_key(expected_acronym.removeprefix("IEEE "))}
            if acronym and not official_workshop_acronym and (alias_key(acronym) not in equivalent_acronyms
                            or protected and acronym != expected_acronym):
                reasons.append("Existing abbreviation conflicts with the canonical abbreviation; verify before replacing it.")
            if expected == "conference" and not expected_acronym:
                reasons.append("Conference abbreviation has not been verified; confirm the standard short name or document that none exists.")
            if expected == "journal" and not expected_acronym:
                abbreviation_review = alias_key(canonical["venue_name"]) not in self.full_short_names
            if series_name(canonical["venue_name"]) and not proven:
                reasons.append("A proceedings/book series is not a scholarly event. Find the underlying conference/workshop from the DOI or volume before choosing a canonical venue.")
            if row.get("venue_track") and row["venue_track"] not in ALLOWED_VENUE_TRACKS:
                reasons.append("Venue track is not a supported schema value; confirm the correct paper-level track.")
            if identity_evidence.get("standalone_workshop") and row.get("venue_track") == "Workshop":
                standalone_track_review = True
        elif name or current_type != "book":
            reasons.append("Venue identity/type/standard abbreviation is not verified in the registry; check the publisher or proceedings and select/create a canonical venue.")
        if current_type == "book" and not name and not identifier and not proven and not reasons:
            return row, None  # Project convention: standalone books have no venue taxonomy.
        if not reasons and canonical:
            raw_resolution = resolve_venue(row.get("raw_venue"), publication_type=canonical["venue_type"],
                                           aliases=self.aliases, catalog=self.catalog)
            raw_track = raw_resolution.venue_track if raw_resolution.venue_id == canonical["venue_id"] else ""
            evidence_track = normalize_venue_track(fact.get("track")) if proven else ""
            identity_evidence = self.evidence_by_key.get(alias_key(canonical["venue_name"]), {})
            if identity_evidence.get("standalone_workshop") and evidence_track == "Workshop":
                evidence_track = ""  # Deposited event-name keyword alone is not a subtrack.
            # Generic parent-event metadata does not disprove a reviewed
            # workshop/findings/poster assignment. Only positive track evidence
            # may repair a populated track; absence of a suffix means default.
            if evidence_track == "Main" and row.get("venue_track"):
                evidence_track = ""
            official_workshop_acronym = any(value in identity_evidence.get("workshop_aliases", [])
                                           for value in (clean_text(row.get("venue_acronym")), fact.get("acronym")))
            track = ("Workshop" if official_workshop_acronym else "") or evidence_track or clean_text(row.get("venue_track")) or raw_track or resolved.venue_track or "Main"
            row.update({field: canonical[field] for field in ("venue_id", "venue_name", "venue_acronym", "venue_type")})
            row["venue"] = canonical["venue_name"]
            row["venue_track"] = track if canonical["venue_type"] == "conference" else ""
            row["publication_type"] = canonical["venue_type"]
            row["venue_label"] = display_venue(row)
            row["venue_aliases"] = list(canonical.get("aliases", []))
            row["ambiguity_status"] = "resolved"
            row["raw_venue"] = paper.get("raw_venue") or name
            edition_years = set(re.findall(r"\b(?:19|20)\d{2}\b", name))
            if not row.get("year") and len(edition_years) == 1:
                row["year"] = int(next(iter(edition_years)))
            if proven and fact.get("year"):
                row["year"] = str(fact["year"]) if isinstance(paper.get("year"), str) else fact["year"]
            if "publication_year" in row:
                row["publication_year"] = row.get("year")
        if standalone_track_review:
            proposal["venue_track"] = "Main"
            reasons.append("This is a standalone scholarly workshop venue. Its name alone does not establish a Workshop subtrack; confirm Main versus an actual nested workshop track from the paper/program, preserving the venue identity.")
        if fact.get("review_only") and fact.get("prior_effective_venue"):
            proposed = resolve_venue(fact["name"], publication_type=fact["type"], aliases=self.aliases, catalog=self.catalog)
            proposal = {**self.registry.get(proposed.venue_id, {}), "venue_track": normalize_venue_track(fact.get("track"))}
        # An unverified short name does not invalidate an independently verified
        # identity/type. Persist those safe fields while keeping this check live.
        if abbreviation_review:
            abbreviation_evidence = self.evidence_by_key.get(alias_key(canonical["venue_name"]), {})
            if abbreviation_evidence.get("acronym") and not abbreviation_evidence.get("review_only"):
                proposal["venue_acronym"] = abbreviation_evidence["acronym"]
                reasons.append("The source-backed journal abbreviation conflicts with another registry identity or alias; confirm a disambiguated standard short name before adding it.")
            else:
                reasons.append("Journal abbreviation has not been verified; confirm its established short name from the publisher or a bibliographic authority, or explicitly document that the full name is the standard short form.")
        if reasons:
            finding = {"paper_id": row.get("paper_id", ""), "display_id": row.get("display_id", ""),
                       "actionable_id": "venue:" + source_fingerprint(paper)[:20] + ":" + clean_text(row.get("paper_id") or row.get("display_id") or row.get("doi") or row.get("title")),
                       "title": row.get("title", ""), "year": row.get("year", ""),
                       "doi": row.get("doi", ""), "openalex_url": row.get("openalex_url", ""),
                       "current_type": current_type, "current_venue": name,
                       "current_abbreviation": row.get("venue_acronym", ""),
                       "current_track": normalize_venue_track(row.get("venue_track")), "current_venue_id": identifier,
                       "proposed_type": proposal.get("venue_type", ""),
                       "proposed_name": proposal.get("venue_name", ""),
                       "proposed_abbreviation": proposal.get("venue_acronym", ""),
                       "proposed_venue_id": proposal.get("venue_id", ""),
                       "proposed_track": proposal.get("venue_track") or normalize_venue_track(fact.get("track")) or (row.get("venue_track") if proposal.get("venue_type") == "conference" else ""),
                       "reason": " ".join(dict.fromkeys(reasons)), "review_type": "publication_venue",
                       "recommended_action": "Verify source, then Open / Edit and save the confirmed venue/type.",
                       "evidence_url": (fact or evidence or arxiv_status).get("source", ""),
                       "manual_review": True, "source_fingerprint": source_fingerprint(paper)}
            return row, finding
        return row, None

    def effective(self, paper):
        row, finding = self.paper(paper)
        row["venue_review_required"] = finding is not None
        # This flag is venue-specific and never implies paper curation status.
        if finding:
            row["venue_review_reason"] = finding["reason"]
            row["ambiguity_status"] = "unresolved"
            # Unverified display text is not a canonical identity. Keep it in
            # venue/raw_venue and in the review finding, not in canonical fields.
            stored = self.registry.get(clean_text(row.get("venue_id")))
            if not stored or any(clean_text(row.get(f)) != clean_text(stored.get(f))
                                 for f in ("venue_name", "venue_type", "venue_acronym")):
                row["venue"] = row.get("venue") or row.get("venue_name") or ""
                for field in ("venue_id", "venue_name", "venue_type", "venue_acronym", "venue_track", "venue_label", "venue_aliases"):
                    row.pop(field, None)
            else:
                row["venue_label"] = display_venue(row)
                row["venue_aliases"] = list(stored.get("aliases", []))
        else:
            row.pop("venue_review_reason", None)
        return row

    def run(self, papers):
        normalized, findings, changes = [], [], []
        audited = 0
        for paper in papers:
            if clean_text(paper.get("publication_type")).lower() not in TYPES | {"book-chapter", "book chapter", "chapter"}:
                normalized.append(dict(paper))
                continue
            audited += 1
            row, finding = self.paper(paper)
            normalized.append(row)
            if finding:
                findings.append(finding)
            differences = {f: {"before": paper.get(f, ""), "after": row.get(f, "")}
                           for f in FIELDS if clean_text(paper.get(f)) != clean_text(row.get(f))}
            if differences:
                changes.append({"paper_id": paper.get("paper_id", ""), "title": paper.get("title", ""),
                                "source_fingerprint": source_fingerprint(paper), "fields": differences})
        summary = {"total_papers_audited": audited, "automatically_corrected": len(changes),
                   "canonical_names_normalized": sum("venue_name" in c["fields"] or "venue" in c["fields"] for c in changes),
                   "abbreviations_added": sum("venue_acronym" in c["fields"] and not c["fields"]["venue_acronym"]["before"] and bool(c["fields"]["venue_acronym"]["after"]) for c in changes),
                   "publication_types_corrected": sum("publication_type" in c["fields"] for c in changes),
                   "canonical_ids_normalized": sum("venue_id" in c["fields"] for c in changes),
                   "acronyms_fixed": sum("venue_acronym" in c["fields"] and bool(c["fields"]["venue_acronym"]["before"]) for c in changes),
                   "venue_tracks_corrected": sum("venue_track" in c["fields"] for c in changes),
                   "years_corrected": sum("year" in c["fields"] for c in changes),
                   "proceedings_series_resolved": sum("venue" in c["fields"] and series_name(c["fields"]["venue"]["before"]) for c in changes),
                   "manual_review": len(findings), "duplicate_registry_keys": len(self.duplicates)}
        return normalized, dict(summary=summary, changes=changes, records=findings,
                               duplicate_registry_keys=self.duplicates)


def source_with_curation(paper):
    source = dict(paper, **(paper.get("curated_record") or {}))
    if not source.get("venue_track") and paper.get("publication_type") == "conference" and normalize_venue_track(paper.get("venue_track")) != "Main":
        source["venue_track"] = paper.get("venue_track", "")
    return source


def review_queue(papers, aliases, decisions=None):
    audit = VenueAudit(aliases, decisions=decisions)
    # Recompute from current source curation, never from old diagnostic CSVs.
    sources = [source_with_curation(p) for p in papers]
    _, report = audit.run(sources)
    records = report["records"]
    return dict(available=True, queue="publication_venues", count=len(records), records=records,
                summary=dict(Counter(r["current_type"] for r in records)), durable_source=True,
                total_unresolved=len(records), hidden_resolved=0, suppression_reasons={})


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_csv(path, rows, fields):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Persist processed effective database, registry and audit; never modify manual/curated sources")
    args = parser.parse_args()
    try:
        from .serve_admin import load_admin_data
        from .venues import read_venue_aliases
    except ImportError:
        from serve_admin import load_admin_data
        from venues import read_venue_aliases
    papers, _ = load_admin_data(apply_venue_audit=False)
    sources = [source_with_curation(p) for p in papers]
    aliases = read_venue_aliases()
    audit = VenueAudit(aliases)
    normalized, report = audit.run(sources)
    report["summary"]["public_papers_audited"] = sum(p.get("publication_type") in TYPES and p.get("is_currently_published", False) for p in sources)
    report["summary"]["non_public_papers_audited"] = report["summary"]["total_papers_audited"] - report["summary"]["public_papers_audited"]
    if args.write:
        baseline_path = ROOT / "data/processed/venue_audit_baseline.json"
        if not baseline_path.exists():
            write_json(baseline_path, sources)
        baseline = json.loads(baseline_path.read_text())
        _, baseline_report = VenueAudit(aliases).run(baseline)
        report["normalization_from_initial_state"] = baseline_report["summary"]
        report["initial_changes"] = baseline_report["changes"]
        effective_by_alias = {r["alias"]: r for r in aliases}
        report["registry_identity_redirects"] = dict(sorted({
            r["venue_id"]: effective_by_alias[r["alias"]]["venue_id"]
            for r in read_venue_aliases(include_evidence=False)
            if r["venue_id"] != effective_by_alias[r["alias"]]["venue_id"]}.items()))
        report["normalization_from_initial_state"]["track_specific_ids_retired"] = len(report["registry_identity_redirects"])
        report["normalization_from_initial_state"]["distinct_naming_variants_normalized"] = len({
            c["fields"]["venue"]["before"] for c in baseline_report["changes"]
            if "venue" in c["fields"] and c["fields"]["venue"]["before"]})
        # Persist the same effective state as static exports. Findings retain
        # original conflicting metadata, rather than certifying it as canonical.
        fields = ("paper_id", "display_id", "title", "doi", "arxiv_id", *FIELDS, "raw_venue",
                  "venue_review_required", "venue_review_reason")
        effective_records = [{**{f: row.get(f, "") for f in fields},
                              "source_fingerprint": source_fingerprint(source)}
                             for source in sources if source.get("publication_type") in TYPES
                             for row in [audit.effective(source)]]
        write_json(REPORT_PATH, report)
        write_json(ROOT / "data/processed/venue_normalized_papers.json", {
            "description": "Effective venue fields derived from current source records; source fingerprints invalidate prior results after edits.",
            "records": effective_records})
        write_csv(ROOT / "data/processed/venue_normalized_papers.csv", effective_records, (*fields, "source_fingerprint"))
        write_csv(ROOT / "data/processed/publication_venue_review.csv", report["records"],
                  tuple(report["records"][0]) if report["records"] else ("title", "doi", "reason"))
        write_json(ROOT / "data/processed/canonical_venues.json", list(canonical_venue_registry(aliases).values()))
        metrics = report["normalization_from_initial_state"]
        lines = ["# Publication venue audit", "", "Generated from current effective state. Baseline correction counts refer to the preserved initial dataset; repeated runs do not count corrections twice.", "",
                 f"Audited: {report['summary']['total_papers_audited']} papers ({report['summary']['public_papers_audited']} public; {report['summary']['non_public_papers_audited']} non-public).", "",
                 "| Metric | Papers / records |", "| --- | ---: |",
                 *[f"| {key.replace('_', ' ')} | {value} |" for key, value in metrics.items()], "",
                 "## Remaining manual review", "",
                 "Every item below is available in Admin → Dashboard → Publication venues → Open / Edit. Counts and rows are recomputed from source state on each request, not read from this report.", ""]
        for finding in report["records"]:
            lines += [f"### {finding['title']}", "", f"DOI: {finding['doi'] or 'not supplied'}", "",
                      f"Current: {finding['current_type']} · {finding['current_venue']} · {finding['current_abbreviation'] or 'no acronym'} · {finding['current_track'] or 'no track'}", "",
                      finding["reason"], ""]
            if finding["evidence_url"]:
                lines += [f"[Verification evidence]({finding['evidence_url']})", ""]
        (ROOT / "docs/publication_venue_audit_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

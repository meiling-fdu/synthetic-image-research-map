"""Interpret locally cached primary bibliographic evidence without guessing venues."""
from __future__ import annotations
import json
import re
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path
try:
    from .venues import clean_text, alias_key, _track_from_text
except ImportError:
    from venues import clean_text, alias_key, _track_from_text

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/raw/venue_audit_crossref"
PAPER_EVIDENCE = ROOT / "data/processed/venue_paper_evidence.json"


def stable_event(value):
    """Remove only explicit edition/track syntax from a publisher's event name."""
    text = clean_text(value)
    text = re.sub(r"^[A-Za-z0-9& ]+\s+['’]?\d{2,4}:\s*", "", text)
    text = re.sub(r"\b(?:19|20)\d{2}\b", "", text)
    text = re.sub(r"\b(?:\d+(?:st|nd|rd|th)|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|thirtieth)\s+", "", text, flags=re.I)
    text = re.sub(r"^(?:Proceedings of (?:the )?|The )", "", text, flags=re.I)
    acronym = ""
    match = re.search(r"\(([A-Za-z][A-Za-z0-9&+.-]{1,20})\s*\)\s*$", text)
    if match:
        acronym = match.group(1)
        text = text[:match.start()]
    # Only a conference-like parent name licenses removing a track suffix.
    # A named recurring workshop can legitimately end in the word Workshop.
    if re.search(r"conference|symposium|congress|meeting|\b(?:ECCV|CVPR|ICCV|WACV|BMVC|ICIAP|NeurIPS)\b", text, re.I):
        text = re.sub(r"\s+(?:Workshops?|Findings|Posters?|Main Track)\s*$", "", text, flags=re.I)
    return clean_text(text), acronym


@lru_cache(maxsize=4)
def _load(signature):
    facts = {}
    venues = []
    for path, _mtime in signature:
        entry = json.loads(Path(path).read_text())
        message = entry["response"]["message"]
        doi = entry["doi"].lower()
        kind = message.get("type")
        titles = [clean_text(v) for v in message.get("container-title", [])]
        event = message.get("event") or {}
        name, acronym, track = "", "", ""
        if kind == "journal-article" and len(titles) == 1:
            name = titles[0]
            short = (message.get("short-container-title") or [""])[0]
            acronym = clean_text(short) if alias_key(short) != alias_key(name) else ""
            venue_type = "journal"
        elif kind == "proceedings-article" and event.get("name"):
            name, acronym = stable_event(event["name"])
            event_acronym = clean_text(event.get("acronym"))
            event_acronym = re.sub(r"\s+['’]?(?:\d{4}|\d{2})\s*$", "", event_acronym)
            acronym = acronym or event_acronym
            track = _track_from_text(" ".join([event["name"], *titles]), name)
            venue_type = "conference"
        elif kind == "posted-content" and message.get("subtype") == "preprint":
            # Require the publisher's own resource URL, not merely a repository
            # name or DOI-shaped string attached to a formally published paper.
            from urllib.parse import urlparse
            host = urlparse(message.get("resource", {}).get("primary", {}).get("URL", "")).hostname
            name = {"www.ssrn.com": "SSRN Electronic Journal", "www.techrxiv.org": "TechRxiv"}.get(host, "")
            if not name:
                facts[doi] = {"bibliographic_type": kind, "containers": titles, "source": entry["source_url"]}
                continue
            venue_type = "preprint"
        else:
            facts[doi] = {"bibliographic_type": kind, "containers": titles, "source": entry["source_url"]}
            continue
        # Deposited metadata can itself be wrong. Do not certify suspicious
        # series, malformed names, or a known cross-venue acronym collision.
        suspicious = bool(re.search(r"procedia|electronic imaging|interantional|\bIJCAI\b", name + " " + acronym, re.I))
        fact = dict(name=name, type=venue_type, acronym=acronym, track=track,
                    source=entry["source_url"], aliases=titles, bibliographic_type=kind,
                    title=clean_text((message.get("title") or [""])[0]),
                    review_only=suspicious)
        # A deposited one-word short title is positive evidence for displaying
        # the full name. Multiword repeats are not evidence of no abbreviation
        # (e.g. Elsevier repeats the full title even when ESWA is established).
        if kind == "journal-article" and len(name.split()) == 1 and short and alias_key(short) == alias_key(name):
            fact["short_name_is_full"] = True
        if suspicious:
            if "procedia" in name.lower():
                fact["reason"] = "Procedia is a proceedings series. The deposited journal-article type does not identify the underlying conference; verify the publisher volume, event name, year and track before assigning a canonical venue."
            elif "electronic imaging" in name.lower():
                fact["reason"] = "Electronic Imaging is deposited as journal-article metadata but also names symposium proceedings. Confirm the paper-level scholarly event (Electronic Imaging or its MWSF conference), publication type and track from the primary proceedings."
            else:
                fact["reason"] = "Publisher-deposited metadata contains a spelling anomaly or conflicting acronym; verify the primary publication page."
        facts[doi] = fact
        venues.append(fact)
    if PAPER_EVIDENCE.exists():
        for fact in json.loads(PAPER_EVIDENCE.read_text())["papers"]:
            if fact.get("doi"):
                facts[fact["doi"].lower()] = fact
            if fact.get("arxiv_id"):
                facts["arxiv:" + fact["arxiv_id"]] = fact
            venues.append(fact)
    return venues, facts


def crossref_evidence():
    signature = tuple((str(p), p.stat().st_mtime_ns) for p in sorted(CACHE.glob("*.json")))
    # Include the curated-evidence file's mtime in the cache key without treating
    # it as a Crossref response.
    return _load_with_paper_mtime(signature, PAPER_EVIDENCE.stat().st_mtime_ns if PAPER_EVIDENCE.exists() else 0)


def arxiv_publication_status():
    records = {}
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    for path in sorted(CACHE.glob("arxiv-full-*.xml")):
        for entry in ET.parse(path).getroot().findall("a:entry", ns):
            url = entry.findtext("a:id", default="", namespaces=ns)
            identifier = re.sub(r"v\d+$", "", url.rsplit("/abs/", 1)[-1])
            comment = entry.findtext("x:comment", default="", namespaces=ns)
            journal = entry.findtext("x:journal_ref", default="", namespaces=ns)
            doi = entry.findtext("x:doi", default="", namespaces=ns)
            records[identifier] = dict(source=url, comment=comment, journal_ref=journal, doi=doi,
                                       formal_signal=bool(journal or doi or re.search(r"accepted|to appear|published", comment, re.I)))
    return records


@lru_cache(maxsize=4)
def _load_with_paper_mtime(signature, paper_mtime):
    _load.cache_clear()
    return _load(signature)

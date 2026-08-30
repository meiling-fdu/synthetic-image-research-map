#!/usr/bin/env python3
"""Apply the 2026-08 authoritative institution-name/type audit.

The migration is deliberately source-of-truth first: it edits only curated
tables, uses the repository merge operation, preserves raw affiliation text,
and emits a complete audit row for every institution that was active when the
migration started.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from .curated_institutions import (
        _read,
        _write,
        alias_id_for,
        load_institutions,
        merge_institutions,
        normalize_institution,
        save_institutions,
    )
    from .curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_HIERARCHY_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        INSTITUTION_REVIEW_QUEUE_COLUMNS,
    )
except ImportError:
    from curated_institutions import (
        _read,
        _write,
        alias_id_for,
        load_institutions,
        merge_institutions,
        normalize_institution,
        save_institutions,
    )
    from curated_schema import (
        AUTHOR_INSTITUTION_MAPPING_COLUMNS,
        INSTITUTION_ALIAS_COLUMNS,
        INSTITUTION_HIERARCHY_COLUMNS,
        INSTITUTION_LOCATION_COLUMNS,
        INSTITUTION_LOCATION_REVIEW_COLUMNS,
        INSTITUTION_REVIEW_QUEUE_COLUMNS,
    )


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data/curated"
AUDIT_CSV = ROOT / "data/processed/institution_authoritative_audit.csv"
SUMMARY_JSON = ROOT / "data/processed/institution_authoritative_audit_summary.json"
REPORT_MD = ROOT / "docs/institution_authoritative_audit.md"

INSTITUTIONS = CURATED / "institutions.csv"
ALIASES = CURATED / "institution_aliases.csv"
MAPPINGS = CURATED / "author_institution_mappings.csv"
LOCATIONS = CURATED / "institution_locations.csv"
LOCATION_REVIEWS = CURATED / "institution_location_review.csv"
HIERARCHY = CURATED / "institution_hierarchy.csv"
REVIEW_QUEUE = CURATED / "institution_review_queue.csv"

AUDIT_COLUMNS = (
    "institution_id", "starting_canonical_name", "starting_type",
    "final_institution_id", "final_canonical_name", "final_type",
    "final_status", "name_decision", "type_decision", "evidence_status",
    "evidence_url", "notes",
)


RENAMES: dict[str, tuple[str, str, str]] = {
    "institution:bce986d0881eaaed": (
        "Polytechnic University of Turin",
        "https://www.polito.it/en/privacy",
        "The institution's official English privacy notice uses Polytechnic University of Turin.",
    ),
    "institution:a7afa880cf905469": (
        "Technical University of Applied Sciences Mannheim",
        "https://www.english.hs-mannheim.de/the-university/about-hochschule-mannheim.html",
        "The official English university page identifies Hochschule Mannheim by this name.",
    ),
    "institution:64aa68d006c72586": (
        "Nanfang College, Guangzhou",
        "https://en.nfu.edu.cn/About/Overview.htm",
        "Official English overview includes the comma in the institution name.",
    ),
    "institution:d9bedf96789f3033": (
        "Jiaxing Vocational and Technical College",
        "https://www.jxvtc.edu.cn/",
        "The institution's English name includes 'and'.",
    ),
    "institution:9a733d8202685d10": (
        "Ramdeobaba University",
        "https://rbunagpur.in/overview/",
        "The official university overview states that the former college is now Ramdeobaba University.",
    ),
    "institution:3fca37dd4c8d3e60": (
        "China Mobile",
        "https://www.chinamobileltd.com/en/about/overview.php",
        "Official English corporate materials use China Mobile without a country qualifier.",
    ),
    "institution:13bd816e4b457f40": (
        "Visual Intelligence +X International Cooperation Joint Laboratory of MOE",
        "https://pubmed.ncbi.nlm.nih.gov/42401174/",
        "Authoritative publication metadata confirms the spelling 'Intelligence'; the old canonical contained a typo.",
    ),
}


TYPE_UPDATES: dict[str, tuple[str, str, str]] = {
    # Degree-granting higher-education institutions.
    "institution:64aa68d006c72586": ("university", "https://en.nfu.edu.cn/About/Overview.htm", "Official overview describes a comprehensive application-oriented university."),
    "institution:d9bedf96789f3033": ("university", "https://www.jxvtc.edu.cn/", "Degree-granting vocational higher-education college."),
    "institution:24b3b4892146f8f3": ("university", "https://www.gzjgxy.cn/", "Degree-granting police higher-education institution."),
    "institution:bce986d0881eaaed": ("university", "https://www.polito.it/en/education", "Official site documents university degree programs."),
    "institution:a8472ecf227d6190": ("university", "https://www.besti.edu.cn/", "Degree-granting higher-education institute."),
    "institution:53765f8a62a101ca": ("university", "https://www.telecom-paris.fr/en/school/open/core-mission", "Official site identifies a higher-education grande école."),
    "institution:212d8dcc1a46b96e": ("university", "https://ens-paris-saclay.fr/en/studying-ens-paris-saclay", "Official site documents higher-education degrees."),
    "institution:9a733d8202685d10": ("university", "https://rbunagpur.in/overview/", "Official site identifies Ramdeobaba University as a government- and UGC-approved university."),
    "institution:96c75ff3447d87bb": ("university", "https://saintgits.org/saintgits-college-of-engineering/", "Official site documents an autonomous degree-granting engineering college."),
    "institution:97a78e53265fe882": ("university", "https://wustl.edu/about/", "Official university site."),
    "institution:17922857a5febbe8": ("university", "https://www.hebic.edu.cn/index.html", "Official site identifies a degree-granting higher-education institute."),
    "institution:1f4217b90babf040": ("university", "https://www.iisc.ac.in/admissions/programmes/", "Official site documents degree programs."),
    "institution:cdedd18207a1eeb2": ("university", "https://www.amrita.edu/about/", "Official site explicitly identifies a private university."),
    "institution:e58a37a2924e1779": ("university", "https://www.torrens.edu.au/about", "Official site identifies an Australian university."),
    "institution:3258076c1e752ff2": ("university", "https://www.tuwien.at/en/tu-wien/about-tu-wien", "Official university site."),
    "institution:ecb4d2eeabc31027": ("university", "https://saraswaticollege.edu.in/", "Official site documents higher-education degree programs."),
    # Commercial organizations and internal corporate research groups.
    "institution:2b6e51bec93e86c1": ("company", "https://deepmind.google/about/", "Google corporate AI research organization."),
    "institution:e803ae4c1872dfa7": ("company", "https://www.linepluscorp.com/ko/company/info/", "Official corporate information identifies LINE Plus Corporation."),
    "institution:e3ce9cc5efa9354c": ("company", "https://huggingface.co/huggingface", "Official company profile and commercial enterprise services."),
    "institution:3fca37dd4c8d3e60": ("company", "https://www.chinamobileltd.com/en/about/overview.php", "Official corporate overview."),
    "institution:f1a54130f4c752b7": ("company", "https://www.hikvision.com/en/about-us/company-profile/", "Official company profile."),
    "institution:98477d1f6f6b24f5": ("company", "https://hidream.ai/", "Official commercial AI organization site."),
    "institution:3103fb7db9011c4c": ("company", "https://www.lgresearch.ai/news/view?seq=97", "Official announcement identifies LG AI Research as LG's corporate AI organization."),
    "institution:7bc70559aeb421fa": ("company", "https://www.lg.com/global/about-lg/", "Official LG corporate site."),
    "institution:ac123e56b0168ec2": ("company", "https://sakana.ai/company-info/", "Official corporate information."),
    # Independent, public, nonprofit, or university-affiliated research units.
    "institution:61adfe1cfbad3b19": ("research_unit", "https://www.nrta.gov.cn/", "Public broadcasting-science academy rather than a degree-granting institution."),
    "institution:2d606ab01d8cb4a4": ("research_unit", "https://www.hengyang.gov.cn/", "Municipal agricultural research academy."),
    "institution:0094b55826d7cf3e": ("research_unit", "https://www.hku.hk/", "Named university-affiliated research center; retained separately for scientific attribution."),
    "institution:fe6f0cc7c1924a6a": ("research_unit", "https://english.ucas.ac.cn/", "University-affiliated advanced-study research institute."),
    "institution:b4e88842382d76c1": ("research_unit", "https://www.consorzio-cini.it/index.php/en/about-us", "Official site identifies an interuniversity research consortium."),
    "institution:e9687e710c08b33b": ("research_unit", "https://mila.quebec/en/about/about-mila", "Official site identifies a nonprofit AI research institute."),
    "institution:a4967ac8ddffe56e": ("research_unit", "https://ivado.ca/en/2021/07/06/executive-and-governance-appointments/", "Official material identifies the Institute for Data Valorization."),
    "institution:995961c53e221f07": ("research_unit", "https://centreborelli.ens-paris-saclay.fr/en", "University-affiliated research center."),
    "institution:7c524d46ad18eab1": ("research_unit", "https://openaccess.thecvf.com/content/CVPR2026/papers/Li_Detecting_Compressed_AI-Generated_Images_via_Phase_Spectrum_Robustness_CVPR_2026_paper.pdf", "Paper affiliation and institutional context identify a research laboratory."),
    "institution:28d73eced8e30027": ("research_unit", "https://openaccess.thecvf.com/content/CVPR2026/papers/Li_Detecting_Compressed_AI-Generated_Images_via_Phase_Spectrum_Robustness_CVPR_2026_paper.pdf", "Paper affiliation and institutional context identify a research laboratory."),
    "institution:13bd816e4b457f40": ("research_unit", "https://pubmed.ncbi.nlm.nih.gov/42401174/", "University-affiliated joint research laboratory."),
}


# source, target, explicit location choice, evidence, decision note
MERGES: tuple[tuple[str, str, str, str, str], ...] = (
    ("institution:35caf31d5104b996", "institution:bce986d0881eaaed", "keep_target", "https://www.polito.it/en/privacy", "Duplicate place-qualified translation of Polytechnic University of Turin."),
    ("institution:bbbd3e4c853af6c2", "institution:a7afa880cf905469", "keep_target", "https://www.english.hs-mannheim.de/the-university/about-hochschule-mannheim.html", "Same university; the official German and English names are aliases, not separate entities."),
    ("institution:965434eee0b97685", "institution:1984e5f97afb62d8", "keep_target", "https://www.sydney.edu.au/about-us/vision-and-values/annual-reports.html", "Article-less name is an alias of The University of Sydney."),
    ("institution:d31a9474efa16c6c", "institution:5dbb9ac6a407e079", "keep_target", "https://www.cuhk.edu.cn/en/about-us", "Article-less name is an alias of the same Shenzhen university."),
    ("institution:42c60ebb24e9f839", "institution:ce832fad3d4de534", "keep_target", "https://www.itwm.fraunhofer.de/en.html", "Short name and full ITWM name identify the same Fraunhofer institute."),
    ("institution:6f14a665aa77ba34", "institution:aea376936c88135b", "keep_target", "https://cispa.de/en/about", "CISPA and Helmholtz Center for Information Security are the same institute."),
    ("institution:2e732c4601154ff1", "institution:502b0f4ec4bc4546", "keep_target", "https://www.originqc.com.cn/en/", "Generic translated company name duplicates the confirmed legal company identity."),
    ("institution:b8a4e3b25fd4a300", "institution:53e6219d595780e3", "keep_target", "https://www.um.edu.mo/about-um/identity/", "University of Macao is an alternate English rendering of University of Macau."),
    ("institution:b3e3a87d3fc950c5", "institution:48441fb89f75bf9d", "keep_target", "https://en.ppsuc.edu.cn/About/University_Profile.htm", "Alternate word order duplicates the official English identity."),
    ("institution:6faf58b52bec4e39", "institution:73f449eb6a3c05d3", "keep_target", "https://www.alibabagroup.com/en-US/about-alibaba", "Alibaba Inc is a source variant of Alibaba Group."),
    ("institution:e75cc4bbe66bd6c8", "institution:99ad701067db0680", "keep_both", "https://www.tencent.com/en-us/about.html", "WeChat AI and Tencent WeChat AI identify the same corporate research organization; distinct office locations remain."),
    ("institution:29f3e76214681290", "institution:815062efbb762258", "keep_target", "https://www.unsw.edu.au/assurance-integrity/legal-compliance/access-to-information", "UNSW Sydney is the operating name of the University of New South Wales."),
    ("institution:b771bab570cca255", "institution:7b971ad17fd639eb", "keep_target", "https://www.microsoft.com/en-us/research/lab/microsoft-research-asia/about-us/", "Country-qualified variant duplicates Microsoft Research Asia."),
    ("institution:49700da520d8842b", "institution:c13e2f4a44bb01ed", "keep_target", "https://www.samsungsds.com/en/company/overview/about_company.html", "Country-qualified variant duplicates Samsung SDS."),
    ("institution:fe8410750f429b37", "institution:8d4321d936320802", "keep_target", "https://www.nvidia.com/en-us/about-nvidia/", "Country-qualified/case variant duplicates NVIDIA."),
    ("institution:cd66beec0fcee918", "institution:c107a95b6cb53ac5", "keep_target", "https://www.shlab.org.cn/", "Abbreviated name duplicates Shanghai Artificial Intelligence Laboratory."),
    ("institution:2592e804f95fa542", "institution:4bff7ae080547794", "keep_target", "https://www.truemedia.org/about", "TrueMedia.org is a source-name variant of TrueMedia."),
    ("institution:f0501582969408c8", "institution:6235ae2101dec1c1", "keep_target", "https://www.shcc.edu.cn/", "Shanghai Customs College is the former English name of Shanghai Customs University."),
)


ALIASES_TO_CONFIRM: dict[str, tuple[str, ...]] = {
    "institution:bce986d0881eaaed": ("Polytechnic Institute of Turin", "Polytechnic Institute of Turin, Turin, Italy", "Politecnico di Torino", "PoliTo"),
    "institution:a7afa880cf905469": ("Mannheim University of Applied Sciences", "Hochschule Mannheim", "Technische Hochschule Mannheim"),
    "institution:64aa68d006c72586": ("Nanfang College Guangzhou",),
    "institution:d9bedf96789f3033": ("Jiaxing Vocational Technical College",),
    "institution:9a733d8202685d10": ("Shri Ramdeobaba College of Engineering & Management", "Shri Ramdeobaba College of Engineering and Management", "RCOEM"),
    "institution:3fca37dd4c8d3e60": ("China Mobile (China)",),
    "institution:13bd816e4b457f40": ("Visual Intellgence +X International Cooperation Joint Laboratory of MOE",),
}


HIERARCHY_ADDITIONS: tuple[tuple[str, str, str, str], ...] = (
    ("institution:404cfa1ef241f359", "institution:0094b55826d7cf3e", "affiliated_institute", "https://www.hku.hk/"),
    ("institution:9ab7959736f7be0d", "institution:7c524d46ad18eab1", "affiliated_institute", "https://openaccess.thecvf.com/content/CVPR2026/papers/Li_Detecting_Compressed_AI-Generated_Images_via_Phase_Spectrum_Robustness_CVPR_2026_paper.pdf"),
    ("institution:9ab7959736f7be0d", "institution:28d73eced8e30027", "affiliated_institute", "https://openaccess.thecvf.com/content/CVPR2026/papers/Li_Detecting_Compressed_AI-Generated_Images_via_Phase_Spectrum_Robustness_CVPR_2026_paper.pdf"),
    ("institution:bf6195b78f6dc951", "institution:13bd816e4b457f40", "affiliated_institute", "https://pubmed.ncbi.nlm.nih.gov/42401174/"),
)


UNCERTAIN = {
    "institution:5bca940dfe500f2b": "Scam AI: no sufficiently authoritative evidence to distinguish a company from a project; retained as other.",
    "institution:807ee51b6afcf8f2": "Institute of Artificial Intelligence: name is too generic to identify an authoritative legal/research entity; retained as other.",
    "institution:7bc70559aeb421fa": "The canonical label LG (South Korea) lacks enough source-affiliation context for a safe legal-name rename; type corrected to company only.",
}


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def raw_affiliation_digest(rows: Sequence[Mapping[str, Any]]) -> str:
    payload = "\n".join(clean(row.get("raw_affiliation")) for row in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def update_name_references(institution_id: str, old: str, new: str) -> None:
    tables = (
        (MAPPINGS, AUTHOR_INSTITUTION_MAPPING_COLUMNS, ("institution",)),
        (ALIASES, INSTITUTION_ALIAS_COLUMNS, ("canonical_institution_name",)),
        (LOCATIONS, INSTITUTION_LOCATION_COLUMNS, ("institution",)),
        (LOCATION_REVIEWS, INSTITUTION_LOCATION_REVIEW_COLUMNS, ("canonical_institution_name", "suggested_canonical_institution")),
        (REVIEW_QUEUE, INSTITUTION_REVIEW_QUEUE_COLUMNS, ("current_institution", "suggested_canonical_institution")),
    )
    for path, columns, name_fields in tables:
        rows = _read(path, columns)
        changed = False
        for row in rows:
            id_fields = (
                clean(row.get("institution_id")),
                clean(row.get("current_institution_id")),
                clean(row.get("suggested_institution_id")),
            )
            if institution_id not in id_fields:
                continue
            for field in name_fields:
                if clean(row.get(field)) == old:
                    row[field] = new
                    changed = True
            if path == LOCATIONS:
                row["normalized_institution"] = normalize_institution(new)
                changed = True
        if changed:
            _write(path, columns, rows)


def confirm_aliases() -> int:
    institutions = {row["institution_id"]: row for row in load_institutions()}
    rows = _read(ALIASES, INSTITUTION_ALIAS_COLUMNS)
    existing = {(normalize_institution(row.get("alias_name")), clean(row.get("institution_id"))) for row in rows}
    added = 0
    for institution_id, names in ALIASES_TO_CONFIRM.items():
        canonical = clean(institutions[institution_id]["canonical_name"])
        for alias_name in names:
            key = (normalize_institution(alias_name), institution_id)
            # Punctuation-only historical forms still need a literal alias for
            # exact resolver lookup and provenance, even when normalized search
            # treats them like the canonical spelling.
            if key in existing or clean(alias_name) == canonical:
                continue
            conflicting = [row for row in rows if normalize_institution(row.get("alias_name")) == key[0] and clean(row.get("institution_id")) != institution_id]
            if conflicting:
                raise RuntimeError(f"alias collision for {alias_name!r}: {conflicting}")
            rows.append({
                "alias_id": alias_id_for(alias_name),
                "alias_name": alias_name,
                "institution_id": institution_id,
                "canonical_institution_name": canonical,
                "alias_language": "",
                "alias_source": "2026-08-authoritative-audit",
                "review_status": "confirmed",
                "notes": "Former, native, abbreviated, or source-affiliation variant retained by authoritative audit.",
            })
            existing.add(key)
            added += 1
    _write(ALIASES, INSTITUTION_ALIAS_COLUMNS, rows)
    return added


def add_hierarchy() -> int:
    institutions = load_institutions()
    by_id = {row["institution_id"]: row for row in institutions}
    rows = _read(HIERARCHY, INSTITUTION_HIERARCHY_COLUMNS)
    keys = {(clean(row.get("parent_institution_id")), clean(row.get("child_institution_id"))) for row in rows}
    added = 0
    for parent, child, relationship, evidence_url in HIERARCHY_ADDITIONS:
        if parent not in by_id or child not in by_id:
            raise RuntimeError(f"missing hierarchy endpoint: {parent} -> {child}")
        child_row = by_id[child]
        existing_parent = clean(child_row.get("parent_institution_id"))
        if existing_parent and existing_parent != parent:
            raise RuntimeError(f"conflicting parent for {child}: {existing_parent} vs {parent}")
        child_row["parent_institution_id"] = parent
        if (parent, child) not in keys:
            rows.append({
                "parent_institution_id": parent,
                "child_institution_id": child,
                "relationship_type": relationship,
                "review_status": "confirmed",
                "evidence_source": "authoritative-institution-audit",
                "evidence_url": evidence_url,
                "notes": "Scientifically useful child research unit retained as a separate canonical node.",
            })
            keys.add((parent, child))
            added += 1
    save_institutions(institutions)
    _write(HIERARCHY, INSTITUTION_HIERARCHY_COLUMNS, rows)
    return added


def write_csv(path: Path, columns: Sequence[str], rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def audit_evidence(institution_id: str) -> tuple[str, str, str]:
    if institution_id in RENAMES:
        _, url, note = RENAMES[institution_id]
        return "official_source_confirmed", url, note
    if institution_id in TYPE_UPDATES:
        _, url, note = TYPE_UPDATES[institution_id]
        return "official_or_authoritative_source_confirmed", url, note
    if institution_id in UNCERTAIN:
        return "insufficient_authoritative_evidence", "", UNCERTAIN[institution_id]
    for source, _, _, url, note in MERGES:
        if institution_id == source:
            return "official_source_confirmed_duplicate", url, note
    return "retained_after_registry_wide_review", "", "No authoritative discrepancy identified by the name, type, alias, hierarchy, and duplicate-identity scans."


def render_report(summary: Mapping[str, Any]) -> str:
    def bullets(items: Sequence[str]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "- None."

    return f"""# Authoritative institution audit

Generated by `scripts/migrate_authoritative_institution_audit.py`.

## Coverage and invariants

- Active canonical institutions audited at start: {summary['audited_active_institutions']}
- Active canonical institutions after duplicate consolidation: {summary['active_institutions_after']}
- Active paper–institution relationships before / after: {summary['active_relationships_before']} / {summary['active_relationships_after']}
- Unique affected papers: {summary['affected_papers']}
- Raw affiliation digest preserved: `{summary['raw_affiliation_digest_before'] == summary['raw_affiliation_digest_after']}`
- Ambiguous active alias keys after migration: {summary['ambiguous_alias_keys']}
- Active mappings to retired IDs after migration: {summary['active_mappings_to_retired_ids']}

## Canonical-name changes

{bullets([f"{item['from']} → {item['to']}" for item in summary['canonical_name_changes']])}

## Duplicate identities merged

{bullets([f"{item['source_name']} → {item['target_name']}" for item in summary['duplicate_merges']])}

## Institution-type changes

{bullets([f"{item['name']}: {item['from']} → {item['to']}" for item in summary['institution_type_changes']])}

## Hierarchy relationships added

{bullets([f"{item['parent_name']} → {item['child_name']} ({item['relationship_type']})" for item in summary['hierarchy_additions']])}

## Intentionally unresolved names

{bullets(list(summary['uncertain_cases']))}

## Type distribution

- Before: `{json.dumps(summary['type_distribution_before'], sort_keys=True)}`
- After: `{json.dumps(summary['type_distribution_after'], sort_keys=True)}`

The row-level evidence ledger is `data/processed/institution_authoritative_audit.csv`.
"""


def migrate(apply: bool) -> dict[str, Any]:
    starting = load_institutions()
    starting_active = [dict(row) for row in starting if clean(row.get("institution_status")) == "active"]
    starting_by_id = {row["institution_id"]: row for row in starting_active}
    mappings_before = _read(MAPPINGS, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
    active_mappings_before = [row for row in mappings_before if clean(row.get("mapping_status")) == "active"]
    affected_ids = set(RENAMES) | set(TYPE_UPDATES) | {source for source, *_ in MERGES}
    affected_papers = {clean(row.get("paper_id")) for row in active_mappings_before if clean(row.get("institution_id")) in affected_ids}

    if not apply:
        return {
            "mode": "dry-run",
            "audited_active_institutions": len(starting_active),
            "planned_name_changes": len([key for key, value in RENAMES.items() if key in starting_by_id and starting_by_id[key]["canonical_name"] != value[0]]),
            "planned_type_changes": len([key for key, value in TYPE_UPDATES.items() if key in starting_by_id and starting_by_id[key]["institution_type"] != value[0]]),
            "planned_merges": len([source for source, *_ in MERGES if source in starting_by_id]),
        }

    timestamp = now()
    institutions = load_institutions()
    by_id = {row["institution_id"]: row for row in institutions}
    name_changes: list[dict[str, str]] = []
    type_changes: list[dict[str, str]] = []
    for institution_id, (new_name, _, _) in RENAMES.items():
        row = by_id[institution_id]
        old_name = clean(row.get("canonical_name"))
        if old_name != new_name:
            name_changes.append({"institution_id": institution_id, "from": old_name, "to": new_name})
            row["canonical_name"] = new_name
            if clean(row.get("public_display")) in {old_name, ""}:
                row["public_display"] = new_name
            row["updated_at"] = timestamp
    for institution_id, (new_type, _, _) in TYPE_UPDATES.items():
        row = by_id[institution_id]
        old_type = clean(row.get("institution_type"))
        if old_type != new_type:
            type_changes.append({"institution_id": institution_id, "name": clean(row.get("canonical_name")), "from": old_type, "to": new_type})
            row["institution_type"] = new_type
            row["updated_at"] = timestamp
    save_institutions(institutions)
    for item in name_changes:
        update_name_references(item["institution_id"], item["from"], item["to"])

    merge_results: list[dict[str, str]] = []
    for source_id, target_id, location_resolution, evidence_url, note in MERGES:
        current = {row["institution_id"]: row for row in load_institutions()}
        source = current[source_id]
        target = current[target_id]
        if clean(source.get("institution_status")) != "active":
            continue
        source_name = clean(source.get("canonical_name"))
        target_name = clean(target.get("canonical_name"))
        merge_institutions(
            source_id,
            target_id,
            confirmation=f"REPLACE {source_name} WITH {target_name} GLOBALLY",
            review_note=f"2026-08 authoritative audit: {note} Evidence: {evidence_url}",
            location_resolution=location_resolution,
        )
        merge_results.append({"source_id": source_id, "source_name": source_name, "target_id": target_id, "target_name": target_name})

    aliases_added = confirm_aliases()
    hierarchy_added = add_hierarchy()

    final = load_institutions()
    final_by_id = {row["institution_id"]: row for row in final}
    mappings_after = _read(MAPPINGS, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
    active_mappings_after = [row for row in mappings_after if clean(row.get("mapping_status")) == "active"]
    aliases = _read(ALIASES, INSTITUTION_ALIAS_COLUMNS)
    active_ids = {row["institution_id"] for row in final if clean(row.get("institution_status")) == "active"}
    aliases_by_key: dict[str, set[str]] = {}
    for row in aliases:
        if clean(row.get("institution_id")) in active_ids:
            aliases_by_key.setdefault(normalize_institution(row.get("alias_name")), set()).add(clean(row.get("institution_id")))
    ambiguous_aliases = {key: sorted(ids) for key, ids in aliases_by_key.items() if len(ids) > 1}
    active_to_retired = [row["mapping_id"] for row in active_mappings_after if clean(row.get("institution_id")) not in active_ids]

    merge_target = {source: target for source, target, *_ in MERGES}
    audit_rows = []
    for before in starting_active:
        institution_id = before["institution_id"]
        final_id = merge_target.get(institution_id, institution_id)
        after = final_by_id[final_id]
        evidence_status, evidence_url, notes = audit_evidence(institution_id)
        audit_rows.append({
            "institution_id": institution_id,
            "starting_canonical_name": before["canonical_name"],
            "starting_type": before["institution_type"],
            "final_institution_id": final_id,
            "final_canonical_name": after["canonical_name"],
            "final_type": after["institution_type"],
            "final_status": final_by_id[institution_id]["institution_status"],
            "name_decision": "merged_duplicate" if institution_id in merge_target else ("renamed" if before["canonical_name"] != after["canonical_name"] else "retained"),
            "type_decision": "merged_duplicate" if institution_id in merge_target else ("changed" if before["institution_type"] != after["institution_type"] else "retained"),
            "evidence_status": evidence_status,
            "evidence_url": evidence_url,
            "notes": notes,
        })
    write_csv(AUDIT_CSV, AUDIT_COLUMNS, audit_rows)

    hierarchy_names = {row["institution_id"]: row["canonical_name"] for row in final}
    hierarchy_summary = [
        {"parent_id": parent, "parent_name": hierarchy_names[parent], "child_id": child, "child_name": hierarchy_names[child], "relationship_type": relationship}
        for parent, child, relationship, _ in HIERARCHY_ADDITIONS
    ]
    final_active = [row for row in final if clean(row.get("institution_status")) == "active"]
    summary = {
        "mode": "apply",
        "audited_active_institutions": len(starting_active),
        "active_institutions_after": len(final_active),
        "canonical_name_changes": name_changes,
        "institution_type_changes": type_changes,
        "duplicate_merges": merge_results,
        "aliases_added": aliases_added,
        "hierarchy_relationships_added": hierarchy_added,
        "hierarchy_additions": hierarchy_summary,
        "affected_papers": len(affected_papers),
        "active_relationships_before": len(active_mappings_before),
        "active_relationships_after": len(active_mappings_after),
        "raw_affiliation_digest_before": raw_affiliation_digest(mappings_before),
        "raw_affiliation_digest_after": raw_affiliation_digest(mappings_after),
        "ambiguous_alias_keys": len(ambiguous_aliases),
        "ambiguous_alias_details": ambiguous_aliases,
        "active_mappings_to_retired_ids": len(active_to_retired),
        "type_distribution_before": dict(sorted(Counter(row["institution_type"] for row in starting_active).items())),
        "type_distribution_after": dict(sorted(Counter(row["institution_type"] for row in final_active).items())),
        "uncertain_cases": list(UNCERTAIN.values()),
    }
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_report(summary), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply curated changes; otherwise report planned counts.")
    args = parser.parse_args()
    result = migrate(args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

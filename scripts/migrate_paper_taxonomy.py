#!/usr/bin/env python3
"""Build the curated taxonomy registry for the reconciled public corpus."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from .curated_schema import PAPER_TAXONOMY_COLUMNS
    from .paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        all_identity_keys,
        build_active_exclusion_index,
        clean,
        read_exclusion_rows,
        record_is_excluded,
    )
    from .paper_taxonomy import serialize_image_scopes, serialize_research_types, serialize_tasks
except ImportError:
    from curated_schema import PAPER_TAXONOMY_COLUMNS
    from paper_exclusions import (
        DEFAULT_EXCLUSIONS_PATH,
        all_identity_keys,
        build_active_exclusion_index,
        clean,
        read_exclusion_rows,
        record_is_excluded,
    )
    from paper_taxonomy import serialize_image_scopes, serialize_research_types, serialize_tasks


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PUBLIC = ROOT / "web/data/public_preview_papers.json"
DEFAULT_REGISTRY = ROOT / "data/curated/paper_taxonomy.csv"
DEFAULT_PRIOR_AUDIT = DEFAULT_REGISTRY
AUDITED_AT = "2026-09-04"

CONFIRMED_NO_TASK_TITLES = {
    '"That\'s Another Doom I Haven\'t Thought About": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation',
    "DynEval: Holistic Evaluations of T2I Generative Models in the Wild",
    "DeepArt: A Benchmark to Advance Fidelity Research in AI-Generated Content",
    "TWIGMA: A Dataset of AI-Generated Images with Metadata from Twitter",
    "How spammers and scammers leverage AI-generated images on Facebook for audience growth",
    "Does an emotional connection to art really require a human artist? Emotion and intentionality responses to AI- versus human-created art and impact on aesthetic experience",
    "Fourier Spectrum Discrepancies in Deep Network Generated Images",
    "Watch Your Up-Convolution: CNN Based Generative Deep Neural Networks Are Failing to Reproduce Spectral Distributions",
}
SCOPE_OVERRIDES = {
    # The paper says that already-generated images may receive quality-control
    # edits; it does not establish that a generative model modifies a source image.
    "MIRAGE: Towards AI-Generated Image Detection in the Wild": ("fully_generated",),
}


def _matches(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in patterns)


DETECTION_PATTERNS = (
    r"\bdetect(?:ion|or|ors|ing|ed)?\b",
    r"\b(?:real|authentic|genuine|human[- ]made)\b.{0,55}\b(?:fake|synthetic|generated)",
    r"\b(?:fake|synthetic|generated)\b.{0,55}\b(?:real|authentic|genuine|human[- ]made)",
    r"\b(?:fake|synthetic|generated) image (?:classification|identification|recognition)\b",
    r"\bforensic (?:classification|identification)\b",
    r"\bexpos(?:e|es|ed|ing)\b.{0,50}\b(?:fake|generated|synthetic) images?\b",
)
ATTRIBUTION_PATTERNS = (
    r"\bsource attribution\b",
    r"\b(?:model|generator|architecture|origin)(?:-| )?(?:level )?attribution\b",
    r"\battribution of (?:ai[- ]generated|synthetic|generated|fake|deepfake)",
    r"\battribut(?:e|es|ed|ing)\b.{0,100}\b(?:source|generator|generative model|gan|diffusion model|architecture)\b",
    r"\b(?:source|generator|generative model|gan|diffusion model|architecture)\b.{0,100}\battribut",
    r"\bwhich (?:gan|model|generator) (?:generated|produced|created)\b",
    r"\b(?:generator|model|source) (?:identification|recognition|classification)\b",
    r"\b(?:synthetic|generated|ai[- ]generated) images?\b.{0,45}\b(?:attribution|provenance)\b",
    r"\b(?:provenance|attribution) (?:analysis )?(?:of|for)\b.{0,45}\b(?:synthetic|generated|generative art|media)\b",
)
# Explanations, saliency maps, attention, and heatmaps do not qualify.
LOCALIZATION_PATTERNS = (
    r"\b(?:forgery|manipulation|tampering) locali[sz]ation\b",
    r"\b(?:detection|forensic|forgery) and locali[sz]ation\b",
    r"\blocali[sz](?:e|es|ed|ing) (?:the )?(?:manipulated|tampered|forged|edited) regions?\b",
    r"\blocali[sz](?:e|es|ed|ing) (?:the )?suspicious regions?\b",
    r"\b(?:pixel|region)[- ]level\b.{0,70}\b(?:forgery|manipulation|tampering)\b.{0,70}\b(?:locali[sz]|segmentation|mask)",
    r"\b(?:segmentation|locali[sz]ation) (?:benchmark|dataset|task|metric|evaluation)\b.{0,90}\b(?:forgery|manipulat|tamper|edit)",
)

FULLY_GENERATED_PATTERNS = (
    r"\bfully (?:ai[- ]?)?generated (?:image|content)",
    r"\bai[- ]generated images?\b",
    r"\bsynthetic images?\b",
    r"\bcomputer[- ]generated images?\b",
    r"\b(?:gan|diffusion|text[- ]to[- ]image|generative model)[- ]generated images?\b",
    r"\bimages? (?:generated|synthesi[sz]ed|produced) (?:by|using|via|from) (?:a |an )?(?:gan|diffusion|text[- ]to[- ]image|generative)",
    r"\b(?:generated|synthetic) (?:imagery|visual content|artwork|image content)\b",
    r"\bai[- ]generated (?:visual media|visual content|multimedia content)\b",
    r"\b(?:aigc|generative)\b.{0,45}\b(?:image|visual|forensic|detect|attribut)",
    r"\bt2i\b",
    r"\b(?:gan|diffusion)[- ]generated (?:fake )?(?:image|imagery|visual content)s?\b",
    r"\b(?:generated|synthesi[sz]ed) (?:fake )?(?:image|imagery|visual content)s?\b",
    r"\b(?:generative|diffusion|gan) models?\b.{0,80}\b(?:attribution|generated output|synthetic output)\b",
)
# A match must name both a source/input image and a generative modification.
GENERATIVE_EDITING_PATTERNS = (
    r"\b(?:real|source|input|original|pristine) images?\b.{0,170}\b(?:inpaint|outpaint|generative edit|diffusion edit|text[- ]guided edit|image[- ]to[- ]image|generative fill)",
    r"\b(?:inpaint|outpaint|generative edit|diffusion edit|text[- ]guided edit|image[- ]to[- ]image|generative fill).{0,170}\b(?:real|source|input|original|pristine) images?\b",
    r"\b(?:source|input|original) images?\b.{0,170}\b(?:edited|modified|manipulated) (?:by|using|via|with) (?:a |an )?(?:generative|diffusion|gan)",
    r"\b(?:diffusion|generative) models?\b.{0,100}\b(?:edit|inpaint|outpaint)\b.{0,120}\b(?:source|input|original|real) images?\b",
)
GENERATIVE_EDITING_EVIDENCE_PATTERNS = GENERATIVE_EDITING_PATTERNS + (
    r"\binpaint(?:ing|ed)?\b", r"\bai[- ]augmented images?\b",
    r"\bedited subset\b.{0,100}\b(?:stargan|gan|diffusion)",
    r"\b(?:generative|diffusion|gan)\b.{0,70}\b(?:facial )?edit(?:ing|ed)?\b",
    r"\bimages? generated and edited by text[- ]to[- ]image generation models?\b",
    r"\bgenerative models?\b.{0,100}\bfacial synthesis and editing\b",
)
DEEPFAKE_PATTERNS = (
    r"\bdeep[ -]?fakes?\b", r"\bface[- ]?swap", r"\b(?:face|facial) manipulation",
    r"\b(?:face|facial) reenact", r"\bforged faces?\b", r"\bfake faces?\b",
)
TRADITIONAL_PATTERNS = (
    r"\bcopy[- ]move\b", r"\bsplic(?:e|ed|ing)\b",
    r"\btraditional (?:image )?manipulation", r"\bconventional (?:image )?manipulation",
    r"\b(?:cut[- ]and[- ]paste|content[- ]aware) (?:forgery|manipulation|editing)\b",
    r"\bimage tamper(?:ing|ed)?\b",
)

SURVEY_PATTERNS = (
    r"\bsurvey\b", r"\bcomprehensive review\b", r"\bsystematic review\b",
    r"\breview of\b", r"\b(?:present|provide)s? an overview\b",
)
BENCHMARK_PATTERNS = (r"\bbenchmark(?:ing|s|ed)?\b", r"\bevaluation suite\b", r"\btestbed\b")
DATASET_PATTERNS = (
    r"\b(?:introduce|present|release|construct|curate|build)\b.{0,80}\b(?:dataset|corpus)\b",
    r"\bnew (?:large[- ]scale )?(?:dataset|corpus)\b", r"\bdataset (?:of|for|with|containing|comprising)\b",
)
ANALYSIS_PATTERNS = (
    r"\buser stud(?:y|ies)\b", r"\bperception study\b",
    r"\bempirical (?:analysis|study|investigation)\b",
    r"\bwe (?:analy[sz]e|investigate|examine|study|evaluate)\b.{0,100}\b(?:impact|behavior|perception|robustness|bias|reliability|generalization|vulnerabilit)",
    r"\bposition(?: paper)?\b",
    r"\b(?:systematic|critical) stud(?:y|ies)\b",
    r"\bwe (?:show|demonstrate|consider)\b",
    r"\bthis stud(?:y|ies) (?:explores?|examines?|investigates?|evaluates?)\b",
)
METHOD_PATTERNS = (
    r"\b(?:we|this (?:paper|work)) (?:propose|present|introduce|develop)s?\b.{0,100}\b(?:method|approach|framework|model|network|detector|system|algorithm|architecture|representation)\b",
    r"\b(?:novel|new)\b.{0,60}\b(?:method|approach|framework|model|network|detector|algorithm|architecture)\b",
    r"\bour (?:method|approach|framework|model|network|detector|system|algorithm|architecture)\b",
    r"\b(?:method|approach|strategy|framework|model|network|detector|system|algorithm|architecture|representation)\b.{0,70}\b(?:is|are|was|were) (?:proposed|introduced|developed|designed)\b",
    r"\bwe (?:employ|use|leverage)\b.{0,100}\b(?:method|approach|strategy|framework|model|network|detector|algorithm|transformer|classifier)\b",
    r"\b(?:study|paper|work) (?:employs?|uses?|leverages?)\b.{0,100}\b(?:method|approach|strategy|framework|model|network|detector|algorithm|transformer|classifier|gradient|representation)\b",
)
TITLE_METHOD_PATTERNS = (
    r"\b(?:method|approach|framework|model|network|detector|system|algorithm|architecture|transformer|cnn|classifier)\w*\b.{0,100}\b(?:detect|attribut|forensic|classif)",
    r"\b(?:detect|attribut|forensic|classif)\w*\b.{0,100}\b(?:method|approach|framework|model|network|detector|system|algorithm|architecture|transformer|cnn|classifier|feature)\w*\b",
    r"\b(?:detection|attribution) (?:using|via|based on|with)\b",
    r"\b(?:incremental|few[- ]shot|zero[- ]shot|open[- ]set|unsupervised|transfer|continual) learning\b.{0,100}\b(?:detect|attribut|classif)",
)
TITLE_ANALYSIS_PATTERNS = (r"\banalysis of\b", r"\ban evaluation of\b")


def _sentences(row: Mapping[str, Any]) -> list[str]:
    abstract = clean(row.get("abstract"))
    if not abstract:
        return [clean(row.get("title"))]
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", abstract) if part.strip()]


def _evidence_excerpt(row: Mapping[str, Any], patterns: Sequence[str]) -> str:
    for pattern in patterns:
        title = clean(row.get("title"))
        if _matches(title, (pattern,)):
            return title[:500]
        for sentence in _sentences(row):
            if _matches(sentence, (pattern,)):
                return sentence[:500]
    return (clean(row.get("abstract")) or clean(row.get("title")))[:500]


def _evidence_source(row: Mapping[str, Any]) -> str:
    return clean(
        row.get("abstract_source") or row.get("paper_url") or row.get("arxiv_url")
        or row.get("openalex_url") or (f"https://doi.org/{row['doi']}" if row.get("doi") else "")
        or "public_registry_metadata"
    )


def _taxonomy_id(row: Mapping[str, Any]) -> str:
    keys = all_identity_keys(row)
    if not keys:
        raise ValueError(f"paper has no stable identity: {row.get('title')!r}")
    return keys[0]


def classify_tasks(text: str) -> tuple[list[str], Sequence[str]]:
    values, patterns = [], []
    for value, selected in (("detection", DETECTION_PATTERNS), ("source_attribution", ATTRIBUTION_PATTERNS), ("localization", LOCALIZATION_PATTERNS)):
        if _matches(text, selected):
            values.append(value)
            patterns.extend(selected)
    return values, patterns


def classify_scopes(text: str) -> tuple[list[str], Sequence[str]]:
    values, patterns = [], []
    for value, selected in (("fully_generated", FULLY_GENERATED_PATTERNS), ("generative_editing", GENERATIVE_EDITING_PATTERNS), ("deepfake", DEEPFAKE_PATTERNS), ("traditional_manipulation", TRADITIONAL_PATTERNS)):
        if _matches(text, selected):
            values.append(value)
            patterns.extend(selected)
    return values, patterns


def classify_research_types(title: str, text: str) -> tuple[list[str], Sequence[str]]:
    values, patterns = [], []
    for value, selected in (("method", METHOD_PATTERNS), ("dataset", DATASET_PATTERNS), ("benchmark", BENCHMARK_PATTERNS), ("survey", SURVEY_PATTERNS), ("analysis_study", ANALYSIS_PATTERNS)):
        if _matches(text, selected):
            values.append(value)
            patterns.extend(selected)
    if "method" not in values and not _matches(title, SURVEY_PATTERNS + ANALYSIS_PATTERNS):
        if _matches(title, TITLE_METHOD_PATTERNS):
            values.insert(0, "method")
            patterns.extend(TITLE_METHOD_PATTERNS)
    if "analysis_study" not in values and _matches(title, TITLE_ANALYSIS_PATTERNS):
        values.append("analysis_study")
        patterns.extend(TITLE_ANALYSIS_PATTERNS)
    return values, patterns


def _dimension_fields(row: Mapping[str, Any], dimension: str, values: Sequence[str], patterns: Sequence[str], *, reused: bool) -> dict[str, str]:
    has_abstract = bool(clean(row.get("abstract")))
    status, reason = "reviewed", ""
    if not values:
        if dimension == "tasks" and clean(row.get("title")) in CONFIRMED_NO_TASK_TITLES:
            reason = "No controlled detection, source-attribution, or localization task applies to this study."
        else:
            status = "needs_review"
            reason = ("No abstract is available and the title does not provide explicit evidence." if not has_abstract else f"No {dimension.replace('_', ' ')} label could be confirmed explicitly from the available title and abstract.")
    tier = "abstract" if has_abstract else "title"
    if reused:
        tier = f"reused_audit+{tier}"
    return {
        f"{dimension}_status": status,
        f"{dimension}_review_reason": reason,
        f"{dimension}_evidence_tier": tier,
        f"{dimension}_evidence_source": _evidence_source(row),
        f"{dimension}_evidence_excerpt": _evidence_excerpt(row, patterns),
    }


def build_registry_row(row: Mapping[str, Any], prior: Mapping[str, str] | None) -> dict[str, str]:
    title, abstract = clean(row.get("title")), clean(row.get("abstract"))
    text = f"{title}. {abstract}"
    computed_tasks, task_patterns = classify_tasks(text)
    computed_scopes, scope_patterns = classify_scopes(text)
    computed_types, type_patterns = classify_research_types(title, text)
    reused = prior is not None
    if prior:
        # The curated registry is authoritative, including intentionally empty
        # reviewed values. Public metadata can refresh identity fields, but must
        # never recompute or erase prior dimension decisions and evidence.
        tasks = [value for value in prior["tasks"].split(";") if value]
        scopes = [value for value in prior["image_scopes"].split(";") if value]
        research_types = [value for value in prior["research_types"].split(";") if value]
    else:
        tasks, scopes, research_types = computed_tasks, computed_scopes, computed_types
    if title in SCOPE_OVERRIDES:
        scopes = list(SCOPE_OVERRIDES[title])
    if "localization" in tasks:
        task_patterns = [*LOCALIZATION_PATTERNS, *task_patterns]
    elif "source_attribution" in tasks:
        task_patterns = [*ATTRIBUTION_PATTERNS, *task_patterns]
    if "generative_editing" in scopes:
        scope_patterns = [*GENERATIVE_EDITING_EVIDENCE_PATTERNS, *scope_patterns]
    result = {
        "taxonomy_id": _taxonomy_id(row), "paper_id": clean(row.get("paper_id")), "title": title,
        "year": clean(row.get("year") or row.get("publication_year")), "doi": clean(row.get("doi")),
        "arxiv_id": clean(row.get("arxiv_id")), "openalex_url": clean(row.get("openalex_url")),
        "tasks": serialize_tasks(tasks), "image_scopes": serialize_image_scopes(scopes),
        "research_types": serialize_research_types(research_types),
    }
    if prior:
        for dimension in ("tasks", "image_scopes", "research_types"):
            for suffix in ("status", "review_reason", "evidence_tier", "evidence_source", "evidence_excerpt"):
                result[f"{dimension}_{suffix}"] = prior[f"{dimension}_{suffix}"]
    else:
        result.update(_dimension_fields(row, "tasks", tasks, task_patterns, reused=reused))
        result.update(_dimension_fields(row, "image_scopes", scopes, scope_patterns, reused=reused))
        result.update(_dimension_fields(row, "research_types", research_types, type_patterns, reused=reused))
    result["taxonomy_status"] = "needs_review" if any(result[f"{dimension}_status"] == "needs_review" for dimension in ("tasks", "image_scopes", "research_types")) else "reviewed"
    result["audited_at"] = prior.get("audited_at", AUDITED_AT) if prior else AUDITED_AT
    return result


def load_prior(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [dict(row) for row in csv.DictReader(handle)]
    index: dict[str, dict[str, str]] = {}
    for row in rows:
        for key in all_identity_keys(row):
            existing = index.get(key)
            if existing is not None and existing is not row:
                raise ValueError(f"prior taxonomy audit has ambiguous identity key: {key}")
            index[key] = row
    return index


def match_prior(row: Mapping[str, Any], prior: Mapping[str, dict[str, str]]) -> dict[str, str] | None:
    matches = {id(prior[key]): prior[key] for key in all_identity_keys(row) if key in prior}
    if len(matches) > 1:
        raise ValueError(f"public paper matches multiple prior taxonomy rows: {row.get('title')!r}")
    return next(iter(matches.values()), None)


def build_registry(
    public_path: Path,
    prior_path: Path,
    exclusions_path: Path | None = DEFAULT_EXCLUSIONS_PATH,
) -> list[dict[str, str]]:
    papers = json.loads(public_path.read_text(encoding="utf-8")).get("records")
    if not isinstance(papers, list):
        raise ValueError(f"{public_path} has no records array")
    if exclusions_path is not None:
        active_exclusion_index = build_active_exclusion_index(
            read_exclusion_rows(exclusions_path)
        )
        papers = [
            paper
            for paper in papers
            if not record_is_excluded(paper, active_exclusion_index)
        ]
    prior = load_prior(prior_path)
    rows = [build_registry_row(paper, match_prior(paper, prior)) for paper in papers]
    ids = [row["taxonomy_id"] for row in rows]
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        raise ValueError("duplicate taxonomy identities: " + ", ".join(duplicates))
    return rows


def write_registry(rows: Sequence[Mapping[str, str]], path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPER_TAXONOMY_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", type=Path, default=DEFAULT_PUBLIC)
    parser.add_argument("--prior-audit", type=Path, default=DEFAULT_PRIOR_AUDIT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument(
        "--paper-exclusions", type=Path, default=DEFAULT_EXCLUSIONS_PATH
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows = build_registry(
        args.public,
        args.prior_audit,
        args.paper_exclusions,
    )
    if not args.check:
        write_registry(rows, args.registry)
    reused = sum(bool(row["paper_id"]) for row in rows)
    reviews = sum(row["taxonomy_status"] == "needs_review" for row in rows)
    print(f"Audited {len(rows)} public paper identities ({reused} reused curated decisions, {len(rows) - reused} public-only); {reviews} need taxonomy review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

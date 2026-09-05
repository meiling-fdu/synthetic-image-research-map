#!/usr/bin/env python3
"""Write a reproducible summary of the reconciled public taxonomy registry."""

from __future__ import annotations

import csv
from collections import Counter
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data/curated/paper_taxonomy.csv"
OUTPUT = ROOT / "docs/paper_taxonomy_migration_audit_2026-09-04.md"
DIMENSIONS = ("tasks", "image_scopes", "research_types")
FOCUSED_REVIEW_START = {"tasks": 5, "image_scopes": 28, "research_types": 39}
EMPTY_TASK_DECISIONS = (
    ('"That\'s Another Doom I Haven\'t Thought About": A User Study on AI Labels as a Safeguard Against Image-Based Misinformation', "Remain empty", "In-scope analysis of labels and human recognition of AI-image misinformation."),
    ("DynEval: Holistic Evaluations of T2I Generative Models in the Wild", "Excluded after scope review", "Generator-quality evaluator/datasets, without a detection, attribution, or localization task."),
    ("DeepArt: A Benchmark to Advance Fidelity Research in AI-Generated Content", "Excluded after scope review", "Generator-fidelity benchmark, without a controlled taxonomy task."),
    ("TWIGMA: A Dataset of AI-Generated Images with Metadata from Twitter", "Remain empty", "In-scope dataset/analysis resource; it does not evaluate a controlled taxonomy task."),
    ("How spammers and scammers leverage AI-generated images on Facebook for audience growth", "Excluded after scope review", "Societal-use analysis, without a controlled taxonomy task."),
    ("Does an emotional connection to art really require a human artist? Emotion and intentionality responses to AI- versus human-created art and impact on aesthetic experience", "Excluded after scope review", "Aesthetic-perception study, without a controlled taxonomy task."),
    ("Fourier Spectrum Discrepancies in Deep Network Generated Images", "Add detection", "Reports real/generated classification accuracy for a proposed detector."),
    ("Watch Your Up-Convolution: CNN Based Generative Deep Neural Networks Are Failing to Reproduce Spectral Distributions", "Add detection", "Explicitly evaluates detection of generated data on public benchmarks."),
)
CORPUS_SCOPE_DECISIONS = (
    ("Can Model Attribution Bridge AI's Accountability Gap in Safety-Critical Domains?", "EXCLUDE_OUT_OF_SCOPE", "Generic remote-service model attribution; no image domain or image scope is established.", "https://doi.org/10.1098/rsta.2025.0117"),
    ("Cascade learning from adversarial synthetic images for accurate pupil detection", "EXCLUDE_OUT_OF_SCOPE", "GAN-refined synthetic eyes are training augmentation for pupil localization on real images rather than a forensic target.", "https://doi.org/10.1016/j.patcog.2018.12.014"),
    ("DynEval: Holistic Evaluations of T2I Generative Models in the Wild", "EXCLUDE_OUT_OF_SCOPE", "Evaluates T2I alignment and output quality rather than authenticity detection or source attribution.", "https://arxiv.org/abs/2607.11199"),
    ("DeepArt: A Benchmark to Advance Fidelity Research in AI-Generated Content", "EXCLUDE_OUT_OF_SCOPE", "Benchmarks GPT-4 image-synthesis fidelity rather than image forensics.", "https://arxiv.org/abs/2312.10407"),
    ("How spammers and scammers leverage AI-generated images on Facebook for audience growth", "EXCLUDE_OUT_OF_SCOPE", "Studies platform misuse and audience awareness rather than an image-forensic task.", "https://doi.org/10.37016/mr-2020-151"),
    ("Does an emotional connection to art really require a human artist? Emotion and intentionality responses to AI- versus human-created art and impact on aesthetic experience", "EXCLUDE_OUT_OF_SCOPE", "Uses computer-generated art as a stimulus for aesthetic-response research rather than image forensics.", "https://doi.org/10.1016/j.chb.2023.107875"),
)


def values(row: dict[str, str], field: str) -> list[str]:
    return [value for value in row.get(field, "").split(";") if value]


def table(rows: list[tuple[str, int]]) -> list[str]:
    return ["| Value | Papers |", "|---|---:|", *[f"| `{name}` | {count} |" for name, count in rows]]


def build_report() -> str:
    with REGISTRY.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    curated_count = sum(bool(row["paper_id"]) for row in rows)
    lines = [
        "# Paper taxonomy migration audit — 2026-09-04", "",
        f"Audited current public paper identities: **{len(rows)} / {len(rows)}**. No literature was added and no source record was deleted. Six records from the prior 582-paper public corpus are preserved as active curated exclusions after focused scope review.", "",
        f"The registry is joined after candidate, preservation, curated-override, version-merge, and exclusion identity reconciliation. The {curated_count} current public identities represented in `papers.csv` reuse their valid prior audit decisions; the other {len(rows) - curated_count} use the stored abstract and linked DOI/arXiv/OpenAlex/project evidence. Taxonomy review state is independent of bibliographic and affiliation review state.", "",
        "`localization` requires an explicit localization task or evaluation; explanations and heatmaps do not qualify. `generative_editing` requires evidence that a source image is modified by a generative model.",
        "", "## Focused review resolution", "",
        "The follow-up audit started with **62 papers** having at least one uncertain taxonomy dimension. All dimension-level cases were resolved: tasks **5 → 0**, image scopes **28 → 0**, and research types **39 → 0**. Bibliographic and affiliation review fields were not part of this registry update.",
    ]
    for field in DIMENSIONS:
        counts = Counter(value for row in rows for value in values(row, field))
        combos = Counter(" + ".join(values(row, field)) for row in rows if len(values(row, field)) > 1)
        pair_counts = Counter()
        for row in rows:
            for pair in combinations(values(row, field), 2):
                pair_counts[" + ".join(pair)] += 1
        reviews = sum(row[f"{field}_status"] == "needs_review" for row in rows)
        lines.extend(["", f"## {field}", "", *table(list(counts.items())), "", f"Multi-label papers: **{sum(len(values(row, field)) > 1 for row in rows)}**. Taxonomy review cases: **{reviews}**."])
        if combos:
            lines.extend(["", "Exact multi-label combinations:", "", *table(list(combos.items()))])
        if pair_counts:
            lines.extend(["", "Pairwise overlaps (inclusive):", "", *table(list(pair_counts.items()))])

    lines.extend(["", "## Taxonomy-only review cases", ""])
    for field in DIMENSIONS:
        review_rows = [row for row in rows if row[f"{field}_status"] == "needs_review"]
        reasons = Counter(row[f"{field}_review_reason"] for row in review_rows)
        lines.extend([f"### {field}", "", f"Cases: **{len(review_rows)}**.", "", *table(list(reasons.items())), "", "| Taxonomy ID | Title | Reason |", "|---|---|---|"])
        for row in review_rows:
            title = row["title"].replace("|", "\\|")
            reason = row[f"{field}_review_reason"].replace("|", "\\|")
            lines.append(f"| `{row['taxonomy_id']}` | {title} | {reason} |")
        lines.append("")
    lines.extend(["## Eight originally reviewed empty-task records", "", "| Paper | Decision | Basis |", "|---|---|---|"])
    for title, decision, basis in EMPTY_TASK_DECISIONS:
        safe_title = title.replace("|", "\\|")
        lines.append(f"| {safe_title} | {decision} | {basis} |")
    lines.extend(["", "## Focused corpus-scope review decisions", "", "All six reviewed records are preserved in the layered source data and curated exclusion history but omitted from the current public paper and map exports.", "", "| Paper | Decision | Reason | Authoritative source |", "|---|---|---|---|"])
    for title, decision, reason, source in CORPUS_SCOPE_DECISIONS:
        safe_title = title.replace("|", "\\|")
        lines.append(f"| {safe_title} | `{decision}` | {reason} | {source} |")
    lines.extend(["", "The dimension-specific evidence tier, linked source, excerpt, status, and review reason are stored in `data/curated/paper_taxonomy.csv`.", ""])
    return "\n".join(lines)


def main() -> int:
    temporary = OUTPUT.with_suffix(".md.tmp")
    temporary.write_text(build_report(), encoding="utf-8")
    temporary.replace(OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

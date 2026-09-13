#!/usr/bin/env python3
"""Deterministic key-paper coverage; bibliography and markers are independent.

The legacy data/manual output is generated, not a manual correction file.
No source, curation, enrichment, or exclusion decisions are written here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

try:
    from .key_paper_reconciliation import apply_decisions, REVIEW_CLASSIFICATIONS
    from .paper_exclusions import active_exclusions, matching_exclusion_rows, read_exclusion_rows, all_identity_keys, exclusions_with_curated_identities
except ImportError:
    from key_paper_reconciliation import apply_decisions, REVIEW_CLASSIFICATIONS
    from paper_exclusions import active_exclusions, matching_exclusion_rows, read_exclusion_rows, all_identity_keys, exclusions_with_curated_identities

ROOT = Path(__file__).resolve().parent.parent
KEY_PATH = Path("data/manual/key_papers.csv")
OA_PATH = Path("data/processed/openalex_candidate_papers.csv")
CANDIDATE_JSON = Path("web/data/openalex_candidate_map_data.json")
PREVIEW_JSON = Path("web/data/public_preview_map_data.json")
PREVIEW_PAPERS_JSON = Path("web/data/public_preview_papers.json")
EXCLUSIONS_PATH = Path("data/curated/paper_exclusions.csv")
CURATED_PAPERS_PATH = Path("data/curated/papers.csv")
RECONCILIATION_PATH = Path("data/manual/key_paper_reconciliation.json")
OUT_PATH = Path("data/manual/key_paper_coverage_report.csv")
MARKDOWN_PATH = Path("docs/key_paper_coverage_report.md")
INPUT_PATHS = (KEY_PATH, OA_PATH, CANDIDATE_JSON, PREVIEW_JSON, PREVIEW_PAPERS_JSON, EXCLUSIONS_PATH, RECONCILIATION_PATH, CURATED_PAPERS_PATH)
ALLOWED_STATUSES = {
    "covered_as_map_marker", "covered_in_public_preview_paper_list",
    "candidate_only", "missing_from_candidate_pool", "possible_title_match_failure", "excluded",
}

def norm_title(s: str) -> str:
    s = (s or "").lower()
    s = s.replace("‐", "-").replace("–", "-").replace("—", "-")
    s = s.replace("real-world", "real world")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())

def load_csv(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_json_records(path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise ValueError(f"{path} must contain a records array")
    return data["records"]

def best_match(target_norm, title_map):
    best_title = ""
    best_score = 0.0
    target_length = len(target_norm)
    target_tokens = set(target_norm.split())
    for nt, title in title_map.items():
        candidate_length = len(nt)
        if not target_length or not candidate_length:
            continue
        length_ratio = min(target_length, candidate_length) / max(
            target_length,
            candidate_length,
        )
        if length_ratio < 0.45:
            continue
        candidate_tokens = set(nt.split())
        overlap = len(target_tokens & candidate_tokens)
        if not overlap:
            continue
        token_ratio = overlap / max(len(target_tokens), len(candidate_tokens))
        if token_ratio < 0.65:
            continue
        score = SequenceMatcher(None, target_norm, nt).ratio()
        if score > best_score:
            best_score = score
            best_title = title
    return best_title, best_score

def make_title_map(rows):
    out = {}
    for r in rows:
        title = r.get("title", "")
        nt = norm_title(title)
        if nt and nt not in out:
            out[nt] = title
    return out

def yesno(x):
    return "yes" if x else "no"

def identity_values(row):
    # Include published/preprint aliases only when explicitly present in metadata.
    keys = all_identity_keys(dict(row, openalex_url=row.get('openalex_url') or row.get('openalex_id', '')))
    values = {kind: set() for kind in ('doi', 'arxiv', 'openalex')}
    for key in keys:
        kind, value = key.split(':', 1)
        if kind in values:
            if kind == 'openalex':
                value = value.rsplit('/', 1)[-1]
            if kind == 'arxiv':
                value = re.sub(r'v\d+$', '', value.removesuffix('.pdf'))
            if kind == 'doi':
                value = value.removeprefix('doi:').strip()
            values[kind].add(value)
    return values


class PaperIndex:
    """Exact matches only. Multiple possible paper rows always require review."""
    def __init__(self, rows):
        self.rows = rows
        self.identities = [identity_values(row) for row in rows]
        self.indices = {kind: defaultdict(set) for kind in ('doi', 'arxiv', 'openalex', 'title')}
        for i, row in enumerate(rows):
            for kind, values in self.identities[i].items():
                for value in values:
                    self.indices[kind][value].add(i)
            title = norm_title(row.get('title', ''))
            if title:
                self.indices['title'][title].add(i)

    def match(self, row):
        values = identity_values(row)
        conflicts = []
        for kind in ('doi', 'arxiv', 'openalex', 'title'):
            tokens = {norm_title(row.get('title', ''))} if kind == 'title' else values[kind]
            matches = set().union(*(self.indices[kind].get(token, set()) for token in tokens))
            if not matches:
                continue
            # A weaker key may not override conflicting stronger identifiers.
            stronger = ('doi', 'arxiv', 'openalex')[:('doi', 'arxiv', 'openalex', 'title').index(kind)]
            before_conflicts = matches
            matches = {i for i in matches if not any(
                values[k] and self.identities[i][k] and values[k].isdisjoint(self.identities[i][k])
                for k in stronger)}
            for i in sorted(before_conflicts - matches):
                conflicts.append('Conflicting identifiers for ' + self.rows[i].get('title', '') + ': checklist=' + json.dumps({k: sorted(v) for k, v in values.items() if v}, sort_keys=True) + '; source=' + json.dumps({k: sorted(v) for k, v in self.identities[i].items() if v}, sort_keys=True))
            if len(matches) == 1:
                return next(iter(matches)), kind, ''
            if matches:
                return None, kind, 'ambiguous exact ' + kind + ': ' + ' | '.join(self.rows[i].get('title', '') for i in sorted(matches))
        return None, '', '; '.join(dict.fromkeys(conflicts))


def compute_audit(keys, candidates, candidate_markers, papers, markers, exclusions, decisions=()):
    effective_keys = apply_decisions(keys, decisions)
    public = PaperIndex(papers)
    candidate = PaperIndex(candidates)
    # Candidate map repeats papers; group identical paper metadata for lookup only.
    candidate_map_rows = list({json.dumps({k: r.get(k, '') for k in ('title', 'doi', 'arxiv_id', 'arxiv_url', 'openalex_url')}, sort_keys=True): r for r in candidate_markers}.values())
    candidate_map = PaperIndex(candidate_map_rows)
    marker_counts = Counter()
    errors = []
    for marker in markers:
        match, _, ambiguity = public.match(marker)
        if match is None:
            errors.append('Map record absent or ambiguous in bibliography: ' + marker.get('title', '') + ('; ' + ambiguity if ambiguity else ''))
        else:
            marker_counts[match] += 1
    active = active_exclusions(exclusions)
    for paper in papers:
        if matching_exclusion_rows(paper, active):
            errors.append('Excluded paper remains public: ' + paper.get('title', ''))
    title_maps = [make_title_map(rows) for rows in (candidates, markers, papers)]
    report = []
    for number, key in enumerate(effective_keys, 1):
        original = keys[number - 1]
        decision = key.get('_reconciliation', {})
        pi, method, ambiguity = public.match(key)
        ci, _, ca = candidate.match(key)
        mi, _, ma = candidate_map.match(key)
        excluded = matching_exclusion_rows(key, active)
        count = marker_counts[pi] if pi is not None else 0
        paper = papers[pi] if pi is not None else {}
        fuzzy = [('', 0.0)] * 3
        if pi is None and not excluded:
            # Reject only the specifically reviewed distinct title, not future suggestions.
            rejected = {norm_title(t) for t in decision.get('rejected_titles', [])}
            fuzzy = [best_match(norm_title(key.get('title', '')), {k: v for k, v in titles.items() if k not in rejected}) for titles in title_maps]
        review = ambiguity or ca or ma
        if pi is None and decision.get('classification') in REVIEW_CLASSIFICATIONS:
            review = decision['reason']
        if excluded:
            status = 'excluded'
        elif pi is not None:
            status = 'covered_as_map_marker' if count else 'covered_in_public_preview_paper_list'
        elif review:
            status = 'possible_title_match_failure'
        elif ci is not None or mi is not None:
            status = 'candidate_only'
        elif max(score for _, score in fuzzy) >= .90:
            status = 'possible_title_match_failure'
        else:
            status = 'missing_from_candidate_pool'
        if status == 'possible_title_match_failure' and not review:
            suggestion, score = max(fuzzy, key=lambda item: item[1])
            review = f'Fuzzy suggestion only ({score:.3f}): {suggestion}'
        evidence = paper or (candidates[ci] if ci is not None else {})
        diagnostics = [name for name in ('missing_affiliation', 'missing_coordinates', 'unresolved_institution', 'export_rule_blocker') if evidence.get(name) in (True, 'true', 'yes')]
        if not count and not excluded and not diagnostics and (pi is not None or ci is not None or mi is not None):
            diagnostics.append('marker_blocker_unresolved')
        action = {
            'covered_as_map_marker': 'no_action', 'excluded': 'no_action',
            'covered_in_public_preview_paper_list': 'check_affiliations_coordinates_or_export_rules',
            'candidate_only': 'check_public_preview_filter',
            'possible_title_match_failure': 'manual_title_match_review',
            'missing_from_candidate_pool': 'manual_or_openalex_title_import_review',
        }[status]
        row = {field: original.get(field, '') for field in ('title', 'year', 'expected_task', 'source_doc', 'section', 'notes')}
        row.update(checklist_row=str(number), doi=key.get('doi', ''), arxiv_id=key.get('arxiv_id', ''), openalex_url=key.get('openalex_url', ''),
                   in_openalex_candidate_papers=yesno(ci is not None), in_candidate_map=yesno(mi is not None),
                   in_public_preview=yesno(pi is not None), in_public_preview_paper_list=yesno(pi is not None),
                   covered_as_map_marker=yesno(bool(count)), map_record_count=str(count),
                   missing_affiliation=yesno('missing_affiliation' in diagnostics), missing_coordinates=yesno('missing_coordinates' in diagnostics),
                   marker_diagnostics='; '.join(diagnostics), missing_stage=status, coverage_status=status,
                   recommended_action=action, match_method=method, matched_public_title=paper.get('title', ''),
                   matched_public_paper_id=paper.get('paper_id', ''), manual_review=yesno(status == 'possible_title_match_failure'),
                   identity_review=review, exclusion_evidence=json.dumps(excluded, sort_keys=True, ensure_ascii=False) if excluded else '')
        row.update(reconciliation_classification=decision.get('classification', ''),
                   reconciliation_evidence='; '.join(decision.get('evidence_urls', [])),
                   reconciliation_reason=decision.get('reason', ''),
                   resolved_title=key.get('title', ''), resolved_year=key.get('year', ''))
        for prefix, (title, score) in zip(('openalex', 'public_preview', 'public_preview_paper'), fuzzy):
            row['best_' + prefix + '_title_match'] = title
            row['best_' + prefix + '_title_score'] = f'{score:.3f}'
        report.append(row)
    counts = Counter(row['coverage_status'] for row in report)
    summary = {
        'public_papers': len(papers), 'unique_mapped_papers': len(marker_counts), 'map_records': len(markers),
        'key_papers': len(keys),
        'bibliography_covered': counts['covered_as_map_marker'] + counts['covered_in_public_preview_paper_list'],
        **{status: counts[status] for status in sorted(ALLOWED_STATUSES)},
    }
    return report, summary, sorted(set(errors))


def render_csv(rows):
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=list(rows[0]) if rows else ['coverage_status'], lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def render_markdown(rows, summary, fingerprint, errors):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    lines = ['# Key Paper Coverage Report', '',
             'Generated by `scripts/audit_key_paper_coverage.py`; do not edit either report.', '',
             'Bibliography coverage means an exact, unambiguous match in `web/data/public_preview_papers.json`. '
             'Marker coverage counts relationships in `web/data/public_preview_map_data.json`. '
             'Markerless papers remain covered. Candidate-only records are not public. '
             'Exclusions follow the active authoritative exclusion registry. Totals count checklist rows; '
             'multiple checklist variants can refer to one public paper.', '',
             'Input SHA-256: `' + fingerprint + '`', '', '## Inputs', '']
    lines += ['- `' + str(path) + '`' for path in INPUT_PATHS]
    lines += ['', '## Summary', '', '| Metric | Count |', '| --- | ---: |']
    lines += [f'| {key} | {value} |' for key, value in summary.items()]
    lines += ['', '## Integrity issues', ''] + (errors or ['None.'])
    lines += ['', '## Records requiring identity review', '']
    review_rows = [row for row in rows if row['manual_review'] == 'yes']
    lines += [f"- Checklist row {row['checklist_row']}: **{cell(row['title'])}** — {cell(row['identity_review'])}" for row in review_rows] or ['None.']
    lines += ['', '## Per-paper status', '', '| # | Key paper | Status | Bibliography | Marker records | Match | Marker diagnostics | Identity review |', '| ---: | --- | --- | --- | ---: | --- | --- | --- |']
    lines += ['| ' + ' | '.join(cell(row[key]) for key in ('checklist_row', 'title', 'coverage_status', 'in_public_preview_paper_list', 'map_record_count', 'match_method', 'marker_diagnostics', 'identity_review')) + ' |' for row in rows]
    return '\n'.join(lines) + '\n'


def expected_artifacts(root=ROOT):
    # Required sources fail closed: a missing input must never resemble zero coverage.
    digest = hashlib.sha256()
    for path in INPUT_PATHS:
        digest.update(str(path).encode())
        digest.update((root / path).read_bytes())
    rows, summary, errors = compute_audit(
        load_csv(root / KEY_PATH), load_csv(root / OA_PATH), load_json_records(root / CANDIDATE_JSON),
        load_json_records(root / PREVIEW_PAPERS_JSON), load_json_records(root / PREVIEW_JSON),
        exclusions_with_curated_identities(read_exclusion_rows(root / EXCLUSIONS_PATH),
                                           load_csv(root / CURATED_PAPERS_PATH)),
        load_json_records(root / RECONCILIATION_PATH))
    return {OUT_PATH: render_csv(rows), MARKDOWN_PATH: render_markdown(rows, summary, digest.hexdigest(), errors)}, summary, errors


def validate_artifacts(root=ROOT):
    try:
        artifacts, _, errors = expected_artifacts(root)
        for path, expected in artifacts.items():
            if not (root / path).exists() or (root / path).read_bytes() != expected.encode('utf-8'):
                errors.append(f'Stale or inconsistent key-paper audit: {path}; run scripts/audit_key_paper_coverage.py')
        return errors
    except (OSError, ValueError, RuntimeError) as error:
        return [f'Key-paper audit input error: {error}']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read-only integrity and freshness check.')
    args = parser.parse_args(argv)
    if args.check:
        errors = validate_artifacts()
    else:
        artifacts, summary, errors = expected_artifacts()
        if not errors:
            for path, content in artifacts.items():
                target = ROOT / path
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = target.with_suffix(target.suffix + '.tmp')
                temporary.write_text(content, encoding='utf-8')
                temporary.replace(target)
        print(json.dumps(summary, indent=2))
    for error in errors:
        print('ERROR: ' + error)
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())

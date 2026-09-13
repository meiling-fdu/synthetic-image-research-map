#!/usr/bin/env python3
"""Render the bounded reconciliation decisions; never change source decisions."""
import argparse
import json
from collections import Counter

try:
    from . import audit_key_paper_coverage as audit
except ImportError:
    import audit_key_paper_coverage as audit

OUTPUT = audit.ROOT / 'docs/key_paper_reconciliation.md'


def cell(value):
    if isinstance(value, list):
        value = '; '.join(str(v) for v in value)
    return str(value or '').replace('|', '\\|').replace('\n', ' ')


def render():
    source = json.loads((audit.ROOT / audit.RECONCILIATION_PATH).read_text())
    decisions = source['records']
    _, totals, errors = audit.expected_artifacts()
    if errors:
        raise ValueError('; '.join(errors))
    papers = audit.load_json_records(audit.ROOT / audit.PREVIEW_PAPERS_JSON)
    curated = {p['paper_id']: p for p in audit.load_csv(audit.ROOT / 'data/curated/papers.csv')}
    public_ids = {p.get('paper_id') for p in papers}
    published = sum(p['publication_type'] in {'conference', 'journal', 'book'} for p in papers)
    lines = ['# Targeted key-paper reconciliation — 2026-09-08', '',
             'Scope: the original 17 identity-review, 3 candidate-only and 26 missing checklist rows. '
             'No citation expansion or new literature search. Decisions are stored separately from the original '
             'checklist in `data/manual/key_paper_reconciliation.json`; it retains original metadata, compared records, '
             'resolved identities, evidence URLs and addition deduplication checks. Raw evidence is cached in '
             '`data/raw/key_paper_reconciliation_2026_09_08/`. Existing taxonomy, affiliation and review decisions are preserved.', '',
             'The 17 identity cases resolve to 16 existing works and one distinct follow-up, now added under the resumed request. Nine of the 26 missing-list '
             'papers are added, nine already exist, six follow exclusion decisions, and two remain ambiguous. '
             'The candidate-only cases resolve to two existing works and one existing exclusion.', '',
             'The tables of original decisions below preserve the addition-time adjudications. Current curation and public membership are shown in the Added papers table; primary-source curation subsequently recognized the existing Provenance, PLADA and FusionDetect exclusions. The prior 623-paper reconciliation milestone is now 620 public papers. No exclusion was restored or newly invented.', '',
             '## Corpus impact', '', '| Metric | Before original reconciliation | Current after primary curation |', '| --- | ---: | ---: |']
    for label, before, after in [
        ('Public bibliography', 613, totals['public_papers']), ('Published-only (conference/journal/book)', 517, published),
        ('Unique mapped bibliography papers', 607, totals['unique_mapped_papers']),
        ('Checklist bibliography-covered', 253, totals['bibliography_covered']),
        ('Checklist covered with marker', 253, totals['covered_as_map_marker']),
        ('Checklist covered but markerless', 0, totals['covered_in_public_preview_paper_list']),
        ('Candidate-only', 3, totals['candidate_only']), ('Possible-match review', 17, totals['possible_title_match_failure']),
        ('Genuinely missing', 26, totals['missing_from_candidate_pool']), ('Excluded checklist rows', 0, totals['excluded']),
    ]:
        lines.append(f'| {label} | {before} | {after} |')
    lines += ['', 'The original zero exclusions was a checklist matching result, not an empty exclusion registry. '
              'Four existing active exclusions are now recognized (Reverse Engineering, HFI, LDR-Net, DeepArt). '
              'The original reconciliation appended three scope exclusions (DBINDS, Over-coherence, Perceptual Artifacts), increasing active registry exclusions from 47 to 50. '
              'Primary curation subsequently recognized three more pre-existing exclusions through verified OpenAlex IDs: Provenance, PLADA and FusionDetect. Active registry exclusions remain 50, while excluded checklist entries are now 10. None was removed or restored.', '']
    for status, heading in [('possible_title_match_failure', 'Identity review — 17 cases'), ('candidate_only', 'Candidate-only — 3 cases'), ('missing_from_candidate_pool', 'Missing checklist — 26 cases')]:
        lines += ['## ' + heading, '', '| Row | Checklist title | Classification | Canonical/current title | IDs and venue/year | Action and evidence |', '| ---: | --- | --- | --- | --- | --- |']
        for d in decisions:
            if d['baseline_status'] != status:
                continue
            p = d['matched_record']
            identity = dict(d['checklist'], **d['resolved'])
            ids = '; '.join(f'{k}: {identity.get(k) or p.get(k)}' for k in ('doi', 'arxiv_id', 'openalex_url') if identity.get(k) or p.get(k))
            ids += '; ' + str(p.get('venue') or '') + ' ' + str(identity.get('year') or '')
            links = ' '.join(f'[source {i}]({url})' for i, url in enumerate(d['evidence_urls'], 1))
            lines.append('| ' + ' | '.join(map(cell, [d['checklist_row'], d['checklist']['title'], d['classification'], p.get('title') or identity['title'], ids, d['action'] + ': ' + d['reason']])) + ' ' + links + ' |')
        lines += ['']
    lines += ['## Added papers', '',
              'All ten authoritative curated records remain auditable. Seven are public; Provenance, PLADA and FusionDetect are CURATED_BUT_EXCLUDED. Their reviewed evidence is retained. '
              'Empty DOI fields follow the existing schema: arXiv-issued DOIs are represented by the arXiv ID, '
              'not treated as formal publication DOIs. Unavailable OpenAlex IDs are not invented.', '',
              '| Canonical title | Internal ID | DOI | arXiv | OpenAlex | Year | Venue | Review state | Public membership |',
              '| --- | --- | --- | --- | --- | ---: | --- | --- | --- |']
    for d in decisions:
        if d['action'] != 'added_needs_review':
            continue
        p = curated[d['matched_record']['paper_id']]
        lines.append('| ' + ' | '.join(cell(p[k]) for k in ('title', 'paper_id', 'doi', 'arxiv_id', 'openalex_url', 'year', 'venue', 'curation_status')) + ' | ' + ('CURATED_AND_PUBLIC' if p['paper_id'] in public_ids else 'CURATED_BUT_EXCLUDED') + ' |')
    lines += ['', '## Identity details and conflicts', '']
    for d in decisions:
        if d['baseline_status'] != 'possible_title_match_failure':
            continue
        p = d['matched_record']
        lines += [f"- Row {d['checklist_row']}: paper ID `{p.get('paper_id') or 'no curated ID; external identity above'}`. "
                  f"Checklist authors: {cell(d['checklist'].get('authors'))}. Compared/current authors: {cell(p.get('authors'))}. "
                  f"Original checklist DOI: `{d['checklist'].get('doi') or 'none'}`. {d['reason']}"]
    lines += ['', '## Marker external-ID reconciliation', '',
              '“Detection, Attribution and Localization of GAN Generated Images” has published DOI '
              '`10.2352/issn.2470-1173.2021.4.mwsf-276`, arXiv `2007.10466`, published OpenAlex '
              '`W3179128750` and preprint OpenAlex `W3043994911`. The two OpenAlex IDs label distinct source-version '
              'records of the same work. [The arXiv record](https://arxiv.org/abs/2007.10466) and the existing '
              '`paper_arxiv_links.csv` / `arxiv_link_enrichment_report.csv` verify the exact title and six-author '
              'linkage. Markers share the formal DOI and resolve to one bibliography paper. Preserve raw source IDs '
              'rather than inventing a single OpenAlex source identity; no duplicate or institution merge is needed.', '',
              '## Pending decisions', '',
              '- Row 73 is a verified distinct 2023 follow-up (arXiv 2311.00962), added as MISSING_ADD during reconciliation and now primary-source reviewed. It remains distinct from the ECCV 2022 paper.',
              '- Row 177 needs accessible primary full text establishing whether there is an in-scope image-only task; '
              'publisher identity is confirmed, scope is not.',
              '- Row 223 needs a dated official publication/proceedings record. The official PDF confirms authors/title '
              'and image anti-detection subject, but not the checklist year.',
              '- HFI and LDR-Net retain their active maintainer exclusions. Their relationships to RDD/FALCON-Net remain '
              'unverified and are recorded as version questions, not accepted merges.', '',
              '## Curation and safety', '',
              '- Primary curation reviewed taxonomy for all ten additions and added 24 author–institution mapping rows. Seven papers are fully curated; Provenance retains an undefined affiliation superscript and publication uncertainty, while UniAIDet and SAFE retain unresolved location details. See `docs/primary_paper_curation_2026_09_08.md` for the independent review dimensions.',
              '- Existing curated paper rows are unchanged except removal of the literal backslash-n in the Human vs. AI '
              'title (stable ID `curated:5fde2c559e029508e0c3`) during the original reconciliation. The subsequent primary-curation audit protects all older paper, taxonomy, institution, location, mapping and review rows; only the ten additions and their new relationships change.',
              '- CVWW resolves through the venue registry as `venue:computer-vision-winter-workshop`, the ID returned '
              'by the existing `scripts/venues.py` stable-ID algorithm. One source-verified venue alias was appended; '
              'the paper is now primary-source reviewed. The same curated venue validation rules apply.',
              '- Additions passed DOI, arXiv, OpenAlex, normalized-title, acronym and bounded fuzzy-title checks against '
              'both public and curated records. Unavailable identifiers remain empty. The registry records the five '
              'nearest title candidates and decision for each addition; similarity never authorizes a merge.',
              '- The audit hashes the evidence registry, checks its exact original checklist snapshots, and still requires '
              'actual unambiguous bibliography membership. A decision alone cannot mark an absent paper covered.', '',
              '## Reproduction', '',
              '```sh', 'python3 scripts/refresh_public_preview.py --skip-search --user-agent targeted-key-reconciliation',
              'python3 scripts/validate_curated_database.py', 'python3 scripts/audit_key_paper_coverage.py --check',
              'python3 scripts/report_key_paper_reconciliation.py', 'python3 scripts/report_key_paper_reconciliation.py --check',
              '```', '', 'Test results, file-level safety comparison and baseline-failure analysis are recorded in '
              '`docs/key_paper_reconciliation_validation.md`. No commit or push was performed.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    expected = render()
    if args.check:
        return int(not OUTPUT.exists() or OUTPUT.read_text() != expected)
    OUTPUT.write_text(expected)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

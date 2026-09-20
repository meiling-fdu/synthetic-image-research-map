#!/usr/bin/env python3
"""Render Tier 1 review and strict append-only audit from recorded decisions."""
import csv
import hashlib
import json
from collections import Counter
from prepare_systematic_tier1 import ROOT, OUT
from reconcile_systematic_literature import read_csv
from paper_exclusions import records_share_any_identity, active_exclusions, exclusions_with_curated_identities, matching_exclusion_rows

CSV = ROOT / 'data/manual/systematic_tier1_reconciliation_2026_09.csv'
REPORT = ROOT / 'docs/systematic_tier1_reconciliation_2026_09.md'


def make_rows():
    proposals = json.loads((OUT / 'proposals.json').read_text())['papers']
    public = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    markers = json.loads((ROOT / 'web/data/public_preview_map_data.json').read_text())['records']
    rows = []
    for p in proposals:
        found = [r for r in public if records_share_any_identity(p, r)]
        assert len(found) == 1, (p['title'], len(found))
        row = {k: p[k] for k in ('candidate_id', 'title', 'outcome', 'paper_id', 'doi', 'arxiv_id', 'openalex_url', 'publication_type', 'year', 'venue', 'bibliography_status', 'taxonomy_status', 'affiliation_status', 'review_status')}
        row.update(authors='; '.join(p['authors']), version_relationship=p['identity_note'] or 'One primary work; no distinct earlier publication established.', primary_evidence=p['paper_url'] + ' | ' + p['primary_pdf_url'], code_url=p['code_url'],
                   verified_affiliations=json.dumps([a for a in p['affiliations'] if a['institution_id']], ensure_ascii=False), unresolved_affiliations=json.dumps(p['unresolved'], ensure_ascii=False),
                   unassigned_authors='; '.join(p['unassigned_authors']), marker_count=str(sum(records_share_any_identity(p, m) for m in markers)))
        for dim in ('tasks', 'image_scopes', 'research_types'):
            row[dim] = ';'.join(p[dim])
            assert set(found[0][dim]) == set(p[dim]), (p['title'], dim)
        assert [a['name'] for a in found[0]['authors']] == p['authors'], p['title']
        rows.append(row)
    return rows


def diff_audit():
    if (ROOT / 'data/processed/systematic_tier2_include_2026_09/insertion.json').exists():
        frozen = json.loads((OUT / 'validation_data.json').read_text())['diff']
        order = ('papers.csv', 'paper_taxonomy.csv', 'author_institution_mappings.csv', 'institutions.csv', 'paper_exclusions.csv', 'institution_aliases.csv', 'institution_locations.csv', 'institution_hierarchy.csv', 'institution_location_review.csv', 'venue_aliases.csv', 'frontend')
        return {name: frozen[name] for name in order}
    result = {}
    for name in ('papers.csv', 'paper_taxonomy.csv', 'author_institution_mappings.csv', 'institutions.csv', 'paper_exclusions.csv', 'institution_aliases.csv', 'institution_locations.csv', 'institution_hierarchy.csv', 'institution_location_review.csv', 'venue_aliases.csv'):
        old = read_csv(OUT / 'baseline/data/curated' / name)
        new = read_csv(ROOT / 'data/curated' / name)
        changed = [i for i, row in enumerate(old) if i >= len(new) or row != new[i]]
        assert not changed, (name, changed)
        result[name] = {'existing_rows': len(old), 'existing_rows_changed': len(changed), 'new_rows': len(new) - len(old)}
    hashes = json.loads((OUT / 'baseline_sha256.json').read_text())
    frontend = [p for p in hashes if p.startswith('web/') and not p.startswith('web/data/')]
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == hashes[p] for p in frontend)
    result['frontend'] = {'files_checked': len(frontend), 'changed': 0}
    return result


def corpus_stats():
    if (ROOT / 'data/processed/systematic_tier2_include_2026_09/insertion.json').exists():
        return json.loads((OUT / 'validation_data.json').read_text())['corpus']
    papers = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    markers = json.loads((ROOT / 'web/data/public_preview_map_data.json').read_text())['records']
    curated = read_csv(ROOT / 'data/curated/papers.csv')
    exclusions = active_exclusions(exclusions_with_curated_identities(read_csv(ROOT / 'data/curated/paper_exclusions.csv'), curated))
    assert not any(matching_exclusion_rows(p, exclusions) for p in papers)
    duplicates = [(a['title'], b['title']) for i, a in enumerate(papers) for b in papers[i+1:] if records_share_any_identity(a, b)]
    assert not duplicates, duplicates
    return {'public': len(papers), 'published': sum(p['publication_type'] != 'preprint' for p in papers), 'mapped': sum(any(records_share_any_identity(p, m) for m in markers) for p in papers), 'markers': len(markers), 'duplicate_identity_pairs': duplicates, 'active_exclusion_leaks': 0}


def render(rows, stats, diffs):
    counts = Counter(r['outcome'] for r in rows)
    lines = ['# Tier 1 reconciliation — September 2026', '',
        'This is the follow-up to the [completed systematic audit](systematic_literature_completeness_audit_2026_09.md). The original audit decisions and report remain historical evidence. Only its 16 Tier 1 candidates were reconciled; Tier 2 and Tier 3 were not reopened.', '',
        'The canonical review table is [systematic_tier1_reconciliation_2026_09.csv](../data/manual/systematic_tier1_reconciliation_2026_09.csv). All totals and the table below are generated from that CSV and actual exports.', '',
        '## Outcomes', '', json.dumps(dict(sorted(counts.items())), sort_keys=True), '',
        f"Public papers: 620 → {stats['public']}; published: 520 → {stats['published']}; mapped: 613 → {stats['mapped']}; final markers: {stats['markers']}.", '',
        '| Title | Outcome / paper ID | Status | Tasks | Image scopes | Research types | Affiliations | Markers | Remaining issue |',
        '|---|---|---|---|---|---|---|---:|---|']
    for r in rows:
        issues = json.loads(r['unresolved_affiliations'])
        values = [r['title'], r['outcome'] + ' / ' + r['paper_id'], r['publication_type'], r['tasks'], r['image_scopes'], r['research_types'], r['affiliation_status'], r['marker_count'], ' '.join(issues) or 'None']
        lines.append('| ' + ' | '.join(v.replace('|', '\\|') for v in values) + ' |')
    lines += ['', '## Identity, versions and field evidence', '',
        'Strong identifier and exclusion checks ran immediately before insertion. `proposals.json` retains all DOI/arXiv/OpenAlex/title checks, primary PDFs, taxonomy rationales and author-specific affiliation groups. `supplemental_identity_checks.json` records author/venue/year and acronym candidates; `institution_identity_checks.json` records registry and alias comparisons. Bounded fuzzy matches were reviewed, not automatically merged.', '',
        'The Detective SAM workshop precursor and expanded ICLR paper are one evolving work: five workshop authors are retained among the six final authors, the method is continuous, and the final paper adds AutoEditForge. Only the final ICLR paper is represented. No verified shared arXiv/DOI was invented. The [version ledger](../data/processed/systematic_tier1_2026_09/version_relationships.json) records earlier/final titles, author overlap, method continuity, chronology and final representation.', '',
        'FUSE uses a new Southeast University (Bangladesh) entity. Its [official address](https://seu.edu.bd/revised-notice-university-closed-from-1012-february-2026-due-to-13th-parliamentary-election) is 252 Tejgaon Industrial Area, Dhaka 1208, Bangladesh (cached `1a04ec79a4a910e0e011.html`). The location-review queue records this city/country evidence with coordinates missing. The Chinese entity is unchanged. No new map coordinates were guessed.', '',
        'NTIRE affiliations use section 7, pages 9–10. TeleAI-TeleGuard authors 25–29 have no canonical institution assigned; Cong Luo remains unresolved; Mikhail Erofeev is explicitly independent. No institution was inferred from an email domain. IBM Research and four Fractal corporate identities remain unresolved. Ser-Nam Lim’s email-only superscript is retained without a guessed employer.', '']
    for r in rows:
        lines += [f"### {r['title']}", '', f"Authors: {r['authors']}", '', r['version_relationship'], '', f"Primary evidence: {r['primary_evidence']}", '']
    lines += ['## Strict pre-task diff', '', '| File | Existing rows changed | Added rows |', '|---|---:|---:|']
    for name, d in diffs.items():
        if name != 'frontend':
            lines.append(f"| {name} | {d['existing_rows_changed']} | {d['new_rows']} |")
    new_institutions = json.loads((OUT / 'planned_additions.json').read_text())['institutions.csv']
    lines += ['', 'New institutions: ' + '; '.join(i['canonical_name'] for i in new_institutions) + '.', '',
        'All pre-existing authoritative rows and frontend assets are unchanged. No institution aliases or hierarchy edges were added; one ICCIT venue alias was added. Verified identity does not imply a verified campus point; new institutions without coordinates remain markerless. [Exact new records](../data/processed/systematic_tier1_2026_09/planned_additions.json) list every paper, taxonomy row, affiliation, institution and review entry.', '',
        '## Validation and handoff', '',
        'The standard refresh uses `--skip-search` and preserves existing public records. Final counts, exclusion leaks, identity duplicate pairs and strict diffs are in `validation_data.json`. Test and validator logs are retained in `data/processed/systematic_tier1_2026_09/`. Run `python3 scripts/report_systematic_tier1.py` to verify the canonical CSV and regenerate this report deterministically.', '',
        'The original audit remains a bounded historical assessment, not a claim of literature completeness. Its frozen inputs are preserved under the Tier 1 baseline. Remaining work here concerns unresolved affiliations and institutional coordinates; no Tier 2 or Tier 3 action is authorized by this pass. No commit or push was performed.', '']
    return '\n'.join(lines)


def main():
    rows = make_rows()
    if not CSV.exists():
        with CSV.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    else:
        assert read_csv(CSV) == rows, 'Canonical review differs; inspect rather than overwrite.'
    diffs, stats = diff_audit(), corpus_stats()
    REPORT.write_text(render(read_csv(CSV), stats, diffs))
    (OUT / 'validation_data.json').write_text(json.dumps({'corpus': stats, 'diff': diffs, 'outcomes': dict(Counter(r['outcome'] for r in rows))}, indent=2, sort_keys=True) + '\n')
    print(json.dumps(stats))


if __name__ == '__main__':
    main()

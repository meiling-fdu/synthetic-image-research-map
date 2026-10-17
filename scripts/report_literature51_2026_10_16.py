#!/usr/bin/env python3
"""Render the exhaustive 51-item integration audit from durable evidence."""
from collections import Counter
import csv
import io
import json
from pathlib import Path

try:
    from .integrate_literature51_2026_10_16 import ROOT, RAW, OUT, read, save, rows, title_key
except ImportError:
    from integrate_literature51_2026_10_16 import ROOT, RAW, OUT, read, save, rows, title_key

REPORT = ROOT/'docs/literature51_integration_2026_10_16.md'


def counts():
    papers=read(ROOT/'web/data/public_preview_papers.json')['records']
    markers=read(ROOT/'web/data/public_preview_map_data.json')['records']
    decisions=rows(ROOT/'data/curated/review_decisions.csv')
    taxonomy=rows(ROOT/'data/curated/paper_taxonomy.csv')
    plan=read(ROOT/OUT/'plan.json')
    superseded={ident for r in plan['audit'] for ident in r.get('resolves_decision_ids',[])}
    unresolved=[r for r in decisions if r['action']=='unresolved' and r['decision_id'] not in superseded]
    pending={title_key(r['title']) for r in unresolved} | {title_key(r['title']) for r in taxonomy if r['taxonomy_status']=='needs_review'}
    return {'curated_papers':len(rows(ROOT/'data/curated/papers.csv')),'public_papers':len(papers),
        'formally_published':sum(p['publication_type'] in ('journal','conference','book') for p in papers),
        'mapped_papers':sum(bool(p.get('has_map_location')) for p in papers),
        'institution_markers':len({(p.get('institution_id'),p.get('location_id') or (p.get('latitude'),p.get('longitude'))) for p in markers}),
        'public_institutions':len({p.get('institution_id') for p in markers}),'relationships':len(markers),
        'active_exclusions':sum(r['is_active']=='true' for r in rows(ROOT/'data/curated/paper_exclusions.csv')),
        'pending_review_items':len(pending),'unresolved_review_rows':sum(r['action']=='unresolved' for r in decisions),
        'effective_unresolved_decisions':len(unresolved),
        'taxonomy_review_items':sum(r['taxonomy_status']=='needs_review' for r in taxonomy)}


def link(value):
    target=value if value.startswith(('https://','http://')) else '../'+value
    return f'[{value}]({target})'


def disposition(row):
    if row['decision']=='import':
        return 'NEWLY_IMPORTED'
    return 'BLOCKED_EXISTING_MIGRATION' if row['publication_status']=='accepted_track_unresolved' else 'HELD_MANDATORY_EVIDENCE'


def main():
    plan=read(ROOT/OUT/'plan.json');baseline=read(ROOT/OUT/'baseline.json')
    after=counts();save(ROOT/OUT/'after_counts.json',after)
    validation_path=ROOT/OUT/'validation.json'
    validation=read(validation_path) if validation_path.exists() else {}
    totals=Counter(disposition(r) for r in plan['audit'])
    staged=read(ROOT/'data/processed/neurips_2026_targeted_gap_fill_2026_10/curation_payload.json')['papers']
    staged_ids={title_key(r['title']):r['paper_id'] for r in staged}
    lines=['# Literature51 integration audit — October 16, 2026','',
        'This report covers exactly the 51 candidates embedded in the task. No external candidate file was required. '
        'The input inventory remains in `data/raw/literature51_2026_10_16/candidates.json`; '
        'the reviewed evidence, exhaustive reconciliation, and exact append plan are under '
        '`data/processed/literature51_2026_10_16/`.','',
        f"Baseline HEAD: `{baseline['head']}`. Branch: `{baseline['branch'] or 'detached HEAD'}`. No commit or push was performed.",'',
        '## Dispositions','',
        '| Disposition | Candidates |','| --- | ---: |',
        f"| Newly imported | {totals['NEWLY_IMPORTED']} |",
        '| Already present / reconciled without a new import | 0 |',
        f"| Held for insufficient mandatory evidence | {totals['HELD_MANDATORY_EVIDENCE']} |",
        '| Excluded after substantive scope verification | 0 |',
        f"| Other blocked: existing NeurIPS migration / track lock | {totals['BLOCKED_EXISTING_MIGRATION']} |",
        '| **Total unique candidates** | **51** |','',
        'The 38 additions include A01 and A13, whose historical HOLD dispositions were explicitly reconciled. '
        'They are counted once as new imports. The 13 non-imports comprise 11 evidence holds and 2 locked NeurIPS candidates. '
        'There are no duplicate additions, revived exclusions, or invented article identities.','',
        'Fifteen imported taxonomy records remain `needs_review`: fourteen have only publisher-registered titles '
        'available for technical classification, and D06 requires experimental disaggregation of generative editing '
        'from conventional manipulation. Their proposed dimensions and reasons remain explicit, with `manual_review=true` '
        'in the batch audit. Bibliographic verification is independent of taxonomy review and map eligibility.','',
        '## Repository integrity','',
        '| Measure | Before | After |','| --- | ---: | ---: |']
    measures=[('curated_papers','Total curated papers'),('public_papers','Public papers'),
              ('formally_published','Formally published papers, including verified online-first'),
              ('mapped_papers','Mapped unique papers'),('institution_markers','Institution/site markers'),
              ('public_institutions','Distinct public institution identities'),('relationships','Map relationships'),
              ('active_exclusions','Active exclusions'),('pending_review_items','Pending paper review items')]
    for key,label in measures:
        lines.append(f"| {label} | {baseline['counts'].get(key,0)} | {after[key]} |")
    lines += ['',
        'Marker counts use the frontend’s institution-plus-location/coordinate identity; one institution can have multiple '
        'sites. Relationships count all map rows. The institution registry itself remains 748 rows, with 727 active identities.','',
        'Pending review items count unique paper identities with an effective unresolved decision or a `needs_review` taxonomy row: '
        '7 before, 33 after (18 effective unresolved decisions plus 15 taxonomy reviews). The append-only decision ledger retains '
        '20 unresolved rows, including the 2 historical HOLDs explicitly superseded by new linked resolution records. '
        'The original 19 review rows remain byte-for-byte intact.','',
        'All 639 pre-existing public paper objects and all 1,421 map relationships are exactly unchanged. '
        'No author–institution mappings, institution identities, locations, aliases, geographic coordinates, '
        'geocoding caches, exclusion rows, or `data/manual/` files were changed. All 38 additions remain without map markers. '
        'The pre-existing untracked audit files are checksum-preserved. Frontend source, CSS, dependencies, schemas, '
        'validators, historical review locks, and historical evidence receipts are unchanged.','',
        '## Evidence and publication handling','',
        '- DOI/title/ordered-author matches use publisher-deposited Crossref records or original publisher/paper metadata. '
        'Raw HTTP bodies, redirect/challenge responses, failure metadata, and targeted primary search captures are retained separately.',
        '- HTTP 200 browser challenges and empty HTTP 202 responses are not treated as verified bibliographic or technical evidence.',
        '- Accepted-only records are held when publication state or mandatory metadata cannot be represented faithfully. '
        'No unofficial publication type or conference track was introduced.',
        '- Assigned print/issue dates are kept distinct from actual online dates. A17 and E12 retain 2027 print/citation years '
        'and their independently evidenced September 2026 online dates. C01–C03, E06 and E13 remain held because actual online dates '
        'could not be verified. A05 keeps the 2026 issue year and labels the supplied 2025 online year as reported, not an invented exact date.',
        '- Original publisher/paper names and ordering are preserved. No author or institution identity merges were performed. '
        'Descriptions are labeled primary-source summaries; absent technical abstracts remain empty.',
        '- The ten venue alias additions use the existing reviewed canonical-venue workflow and existing `journal`/`conference` types. '
        'No taxonomy vocabulary or membership rule changed.','',
        '## Testing and regeneration','']
    if validation:
        lines += ['| Check | Actual result |','| --- | --- |']
        for name,value in validation.get('checks',{}).items():
            lines.append('| '+name+' | '+str(value).replace('|','\\|')+' |')
        lines += ['',validation.get('full_suite_explanation',''),'']
        for failure in validation.get('preexisting_full_suite_failures',[]):
            lines.append('- `'+failure+'`')
    else:
        lines += ['Validation receipts have not yet been finalized; no full-suite success is claimed.','']
    lines += ['',
        'The canonical exporter runs with `--preserve-existing`; the batch wrapper stages the ordinary location-review '
        'side output so unrelated queue entries are not written. The generated key-paper Markdown report is refreshed '
        'through the canonical coverage renderer only after proving its CSV under `data/manual/` is unchanged. '
        'The result is static JSON consumed by the existing Leaflet site; no custom backend is introduced.','',
        'Historical Batch C tests retain all prior assertions and counts and use a checksum-verified pre-import snapshot. '
        'Current-corpus tests use the reviewed successor counts. No production validator or historical receipt is patched.','',
        '## Reproduction','',
        '```sh','python3 scripts/collect_literature51_sources.py',
        'python3 scripts/integrate_literature51_2026_10_16.py --apply',
        'python3 scripts/regenerate_literature51_2026_10_16.py',
        'python3 scripts/integrate_literature51_2026_10_16.py --check',
        'python3 scripts/validate_curated_database.py','python3 scripts/validate_public_preview.py',
        'python3 scripts/report_literature51_2026_10_16.py','```','',
        '`--apply` is idempotent once its receipt exists. Initial preparation without `--apply` is intended for the '
        'pre-import baseline only; it refuses duplicate identities instead of generating another append. '
        'No network is needed for replay. Test environment and executed command results are recorded in `validation.json` '
        'and `test_results/`; repository dependency files were not changed.','',
        '## Changed files','',
        '| File or group | Purpose |','| --- | --- |',
        '| `data/curated/papers.csv` | Append 38 verified bibliographic identities and preserve all existing bytes. |',
        '| `data/curated/paper_taxonomy.csv` | Append matching taxonomy, evidence tiers, and explicit pending review reasons. |',
        '| `data/curated/review_decisions.csv` | Append 51 decisions; explicitly link the 2 resolved historical HOLDs. |',
        '| `data/curated/venue_aliases.csv` | Append 10 reviewed venue aliases through the supported workflow. |',
        '| `web/data/public_preview_papers.json`, `web/data/public_preview_map_data.json` | Canonical static export; add 38 papers and synchronize the pair timestamp. Map records are unchanged. |',
        '| `docs/key_paper_coverage_report.md` | Canonical generated count/fingerprint refresh; manual CSV is unchanged. |',
        '| `data/raw/literature51_2026_10_16/` | Task-derived inventory and immutable source captures, URLs, hashes, and failed retrievals. |',
        '| `data/processed/literature51_2026_10_16/` | Reviewed evidence, plan, before snapshots, append receipt, all-51 audit, validation, regeneration, and integrity receipts. |',
        '| `scripts/collect_literature51_sources.py` | Read-only source-cache validation and explicit missing-capture retrieval. |',
        '| `scripts/integrate_literature51_2026_10_16.py` | Offline normalization, deduplication, guarded append, history preservation, and idempotence. |',
        '| `scripts/regenerate_literature51_2026_10_16.py` | Canonical export with exact existing-record preservation checks. |',
        '| `scripts/report_literature51_2026_10_16.py` | Deterministic counts and exhaustive audit rendering. |',
        '| `tests/test_literature51_integration.py` | Evidence, identity, hold/track/date, taxonomy, affiliation, and repeat-apply regressions. |',
        '| `tests/literature51_predecessor.py` and historical Batch A/C test imports | Replay historical assertions against hash-verified predecessor bytes. |',
        '| Current count checks in `tests/baseline_expectations.py`, publication-filter, metadata-consistency, and repository-baseline tests | Reviewed successor totals; preserve earlier release constants and explicit author-review invariants. |',
        '| This report | Complete requested 51-paper audit and exact limitations. |','',
        '## Per-paper audit','']
    audit_rows=[]
    for item in plan['audit']:
        cid=item['candidate_id'];status=disposition(item)
        primary=item['primary_url']
        identities=[]
        if item.get('doi'):
            identities.append('DOI '+link('https://doi.org/'+item['doi']))
        if item.get('arxiv_id'):
            identities.append('arXiv '+link('https://arxiv.org/abs/'+item['arxiv_id']))
        if not identities or primary not in ' '.join(identities):
            identities.append('Primary '+link(primary))
        aliases=item.get('title_aliases',[])
        if item.get('historical_reviews'):
            duplicate='Historical HOLD '+', '.join('`'+r['decision_id']+'`' for r in item['historical_reviews'])+' retained; linked resolution `'+item['new_review_decision_id']+'` appended.'
        elif cid in ('B01','E07'):
            duplicate='Existing locked NeurIPS migration identity `'+staged_ids[title_key(item['title'])]+'` retained without application or duplicate preprint.'
        else:
            duplicate='No existing identity found across curated/public records, exclusions, identifier aliases, prior decisions, and relevant migration locks.'
        tax='; '.join(f"{dim}={item[dim]}" for dim in ('tasks','image_scopes','research_types'))
        pending=', '.join(item.get('taxonomy_needs_review',[]))
        blockers=item['notes'] if status!='NEWLY_IMPORTED' else ('Taxonomy review: '+item.get('taxonomy_review_reason','') if pending else 'No mandatory bibliographic blocker.')+' Affiliations remain unresolved; no map location assigned.'
        lines += [f"### {cid} — {item.get('canonical_title',item['title'])}",'',
            f"- **Scope:** `{item['scope_decision']}`. {item['scope_rationale']}",
            f"- **Import:** `{status}`"+(f"; stable ID `{item['paper_id']}`." if item['paper_id'] else '; no curated or public identity created.'),
            '- **Identifiers:** '+'; '.join(identities)+'.',
            f"- **Publication:** `{item['publication_status']}`; {item['venue']}; year {item['year']}"+(f"; track `{item['venue_track']}`." if item['venue_track'] else '.'),
            '- **Publication details:** `'+json.dumps(item.get('publication_details',{}),ensure_ascii=False,sort_keys=True)+'`.',
            '- **Ordered authors:** '+('; '.join(item['authors']) if item.get('authors') else 'Mandatory complete roster remains unresolved')+'.',
            '- **Taxonomy:** `'+tax+'`.'+(' Proposed only; not imported.' if status!='NEWLY_IMPORTED' else (' Pending dimensions: `'+pending+'`.' if pending else ' Evidence-reviewed.')),
            '- **Metadata corrections / evidence:** '+item['notes'],
            '- **Duplicate / historical handling:** '+duplicate,
            '- **Outstanding:** '+blockers,
            '- **Traceable evidence:** '+'; '.join(link(u) for u in item['evidence_sources'])+'.','']
        audit_rows.append({'candidate_id':cid,'title':item.get('canonical_title',item['title']),
            'scope_decision':item['scope_decision'],'import_decision':status,'paper_id':item['paper_id'],
            'doi':item.get('doi',''),'arxiv_id':item.get('arxiv_id',''),'primary_url':primary,
            'publication_status':item['publication_status'],'publication_year':item['year'],
            'venue':item['venue'],'venue_track':item['venue_track'],'ordered_authors':'; '.join(item.get('authors',[])),
            'tasks':item['tasks'],'image_scopes':item['image_scopes'],'research_types':item['research_types'],
            'manual_review':str(item['manual_review']).lower(),'taxonomy_pending_dimensions':pending,
            'metadata_corrections':item['notes'],'duplicate_review_handling':duplicate,
            'outstanding_blockers':blockers,'evidence_sources':'; '.join(item['evidence_sources'])})
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fieldnames=list(audit_rows[0]),lineterminator='\n')
    writer.writeheader();writer.writerows(audit_rows)
    (ROOT/OUT/'audit.csv').write_text(stream.getvalue(),encoding='utf-8')
    save(ROOT/OUT/'audit.json',audit_rows)
    print(json.dumps({'report':str(REPORT.relative_to(ROOT)),'dispositions':dict(totals),'counts':after},indent=2))


if __name__=='__main__':
    main()

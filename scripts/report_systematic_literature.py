#!/usr/bin/env python3
"""Generate the audit report and accounting tables from the canonical registry."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from itertools import combinations
from urllib.parse import parse_qs, urlsplit
from collect_systematic_literature import ROOT, PROCESSED, read_response
from screen_systematic_literature import STATUSES
from build_systematic_literature_pass6 import LINEAGES
from reconcile_systematic_literature import corpus_id, compact_title

CANONICAL = ROOT / 'data/manual/systematic_literature_completeness_candidates_2026_09.csv'
REPORT = ROOT / 'docs/systematic_literature_completeness_audit_2026_09.md'
REVIEW = {'CANDIDATE_ADD_NEEDS_SCOPE_REVIEW', 'AMBIGUOUS_IDENTITY', 'AMBIGUOUS_SCOPE'}


def read_csv(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def status_counts(rows):
    counts = Counter(r['final_status'] for r in rows)
    return {s: counts[s] for s in STATUSES}


def overlaps(rows):
    counts = Counter(r['discovery_channels'] for r in rows)
    return {'+'.join(c): counts['+'.join(c)] for n in range(1, 5) for c in combinations('ABCD', n)}


def cell(value):
    return str('—' if value is None or value == '' else value).replace('|', '\\|').replace('\n', ' ')


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |'] +
                     ['| ' + ' | '.join(cell(v) for v in r) + ' |' for r in rows]) + '\n'


def links(value):
    return '; '.join(f'[source {i}]({u})' for i, u in enumerate(value.split(' | '), 1) if u)


def source_logs():
    result = []
    for path in sorted(PROCESSED.glob('*_sources.json')):
        for source in json.loads(path.read_text()):
            source = dict(source)
            source['manifest'] = str(path.relative_to(ROOT))
            source['query'] = source.get('query') or parse_qs(urlsplit(source['url']).query)
            source['retrieval_bound'] = source.get('retrieval_bound') or 'complete returned source; title screening is bounded'
            if not source.get('discovery_pass'):
                match = re.search(r'pass(\d+)', path.name)
                source['discovery_pass'] = int(match[1]) if match else None
            http = source.get('http_status') or (source['status'] if isinstance(source['status'], int) else None)
            if not http:
                error = re.search(r'HTTP Error (\d+)', source.get('error', ''))
                http = int(error[1]) if error else None
            source['http_status'] = http
            source['coverage_level'] = 'BOUNDED_SEARCH' if source['status'] in (200, 'CLI_SUCCESS') else 'NOT_AVAILABLE'
            result.append(source)
    return result


def lineage_review(rows, sources):
    papers = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    records = []
    for family, prefix in LINEAGES.items():
        matches = [p for p in papers if p['title'].casefold().startswith(prefix.casefold())]
        assert len(matches) == 1, (family, matches)
        paper = matches[0]
        matching_sources = [s for s in sources if s['channel'] == 'C' and s['seed'].casefold().startswith(family.casefold())]
        expansions = 'No separate expansion established in this bounded review.'
        method = 'No separate foundational method established; ordinary dataset users are not lineage additions.'
        if family == 'GenImage':
            expansions = 'GenImage++: Breaking Latent Prior Bias in Detectors for Generalizable AIGC Image Detection; present in corpus.'
            method = 'GenDet (arXiv 2312.08880), linked by the author repository, is present in the corpus.'
        elif family == 'GenImage++':
            expansions = 'Distinct expansion of GenImage; represented by the associated Breaking Latent Prior Bias paper.'
        elif family == 'GIM':
            method = 'GIMFormer is introduced in the same existing dataset/benchmark paper, not a second missing work.'
        elif family == 'ForensicHub':
            method = 'Earlier IMDL-BenCo is a distinct benchmark/codebase in Tier 2; traditional-manipulation scope requires review.'
        elif family == 'SAFE':
            method = 'SAFE-FORGE and challenge evaluation are covered by the same previously curated SAFE challenge paper.'
        records.append({'family': family, 'original_dataset_or_benchmark': paper['title'],
                        'corpus_id': corpus_id(paper), 'presence': 'EXISTING_CURRENT',
                        'benchmark_challenge': 'Same existing paper' if family == 'SAFE' else 'Benchmark represented in the existing family paper; no separate challenge established.',
                        'expanded_version': expansions, 'associated_method': method,
                        'sources': sorted({s['url'] for s in matching_sources}),
                        'limitation': 'Bounded family queries and available primary/curated evidence; not an exhaustive history of every dataset user.'})
    ntire = next(r for r in rows if r['canonical_title'].startswith('NTIRE 2026 Challenge on Robust AI-Generated Image'))
    records.append({'family': 'NTIRE AI-generated image detection', 'original_dataset_or_benchmark': ntire['canonical_title'],
                    'corpus_id': '', 'presence': ntire['final_status'], 'candidate_id': ntire['candidate_id'],
                    'benchmark_challenge': 'Missing foundational 2026 challenge report; distinct from the face-deepfake challenge.',
                    'expanded_version': 'No separate expansion established.', 'associated_method': 'Team solution papers are not automatically counted as foundational gaps.',
                    'sources': ntire['primary_evidence_url'].split(' | '), 'limitation': 'Found through A; lineage classification does not manufacture a separate C discovery.'})
    return records


def accounting(rows):
    enums = json.loads((PROCESSED / 'enumerations.json').read_text())
    sources = source_logs()
    provenance = {r['candidate_id']: json.loads(r['observation_provenance']) for r in rows}
    channels = {}
    for ch in 'ABCD':
        subset = [r for r in rows if ch in r['discovery_channels'].split('+')]
        channels[ch] = {'raw_records': sum(e['enumerated'] for e in enums if e['channel'] == ch),
                        'selected_observations': sum(sum(o['channel'] == ch for o in provenance[r['candidate_id']]) for r in subset),
                        'unique_evaluated': len(subset), **status_counts(subset)}
    passes = []
    for number in sorted({int(o['discovery_pass']) for p in provenance.values() for o in p}):
        subset = [r for r in rows if any(int(o['discovery_pass']) == number for o in provenance[r['candidate_id']])]
        first = [r for r in subset if min(int(o['discovery_pass']) for o in provenance[r['candidate_id']]) == number]
        passes.append({'pass': number, 'raw_records': sum(e['enumerated'] for e in enums if e['discovery_pass'] == number),
                       'selected_observations': sum(sum(int(o['discovery_pass']) == number for o in provenance[r['candidate_id']]) for r in subset),
                       'unique_evaluated': len(subset), 'first_seen_works': len(first),
                       'first_seen_high_confidence': sum(r['final_status'] == 'CANDIDATE_ADD_HIGH_CONFIDENCE' for r in first),
                       **status_counts(subset)})
    proceedings = []
    surveys = []
    for e in enums:
        subset = [r for r in rows if any(o['discovery_source'] == e['source'] for o in provenance[r['candidate_id']])]
        record = {**e, 'unique_evaluated': len(subset), **status_counts(subset)}
        record['with_usable_primary_abstract'] = sum(bool(r['primary_evidence_url']) for r in subset)
        if e['kind'].endswith('_index'):
            record['coverage_level'] = 'BOUNDED_SEARCH'
            if '2025' in e['seed'] and 'neurips' in e['source'] or 'papers.nips.cc/paper_files/paper/2025' in e['source']:
                record['track'] = 'Main Conference' if 'vol38-main-conference' in e['source'] else 'Creative AI only'
            proceedings.append(record)
        if e['kind'].startswith('survey_'):
            record['reference_outcomes'] = {s: sum(sum(o['discovery_source'] == e['source'] for o in provenance[r['candidate_id']]) for r in subset if r['final_status'] == s) for s in STATUSES}
            surveys.append(record)
    gaps = {}
    for tier, statuses in [('confirmed', {'CANDIDATE_ADD_HIGH_CONFIDENCE'}), ('review_hypotheses', REVIEW)]:
        subset = [r for r in rows if r['final_status'] in statuses]
        gaps[tier] = {}
        for field in ('year', 'venue', 'proposed_forensic_task', 'proposed_image_scope', 'proposed_research_type'):
            count = Counter()
            for r in subset:
                for value in (r[field].split(' | ') if r[field] else ['unresolved']):
                    count[value] += 1
            gaps[tier][field] = dict(sorted(count.items(), key=lambda p: (-p[1], p[0])))
    return {'unique_works': len(rows), 'status_counts': status_counts(rows), 'channels': channels,
            'overlaps': overlaps(rows), 'passes': passes, 'proceedings': proceedings, 'surveys': surveys,
            'sources': sources, 'gaps': gaps, 'lineages': lineage_review(rows, sources)}


def render(rows, stats, registry_path):
    summary = json.loads((PROCESSED / 'corpus_summary.json').read_text())
    count = stats['status_counts']
    high = [r for r in rows if r['final_status'] == 'CANDIDATE_ADD_HIGH_CONFIDENCE']
    tier2 = [r for r in rows if r['final_status'] == 'CANDIDATE_ADD_NEEDS_SCOPE_REVIEW']
    tier3 = [r for r in rows if r['final_status'] in {'AMBIGUOUS_IDENTITY', 'AMBIGUOUS_SCOPE'}]
    enums = json.loads((PROCESSED / 'enumerations.json').read_text())
    total_raw = sum(e['enumerated'] for e in enums)
    selected = sum(e['screened'] for e in enums)
    out = ['# Systematic literature-completeness audit — finalized 13 September 2026\n',
           'Discovery cutoff: 12 September 2026. Finalization uses the existing caches and introduces no new broad discovery.\n',
           f'**STRONG WITH IDENTIFIABLE GAPS — a bounded assessment, not certification of completeness.** The frozen corpus contains 620 public papers. This audit identifies {len(high)} primary-verified missing works, {len(tier2)} scope-precedent reviews and {len(tier3)} unresolved cases. No candidates were added. The unresolved set and inaccessible sources prevent a stronger conclusion.\n',
           f'Canonical decisions: [{registry_path.name}](../{registry_path.relative_to(ROOT)}). Counts and every table below are generated from this CSV and the cached-source logs. The broad discovery table has {total_raw:,} records; {selected:,} observations were selected for reconciliation into {len(rows):,} unique works. Unselected index rows remain in `raw_discovery.jsonl`; they are not silently labelled out of scope.\n',
           '## Baseline and scope\n',
           '620 public papers; 520 published; 613 mapped. The pre-audit full-suite baseline was 1,440 passed / 0 failed. The existing checklist accounts for all 299 entries but is not evidence of whole-literature completeness.\n',
           table(['Year', 'Corpus papers'], sorted(summary['year'].items())),
           'Localization (21) and generative editing (29) are small categories, not proof of a gap. Source attribution has 77 records; taxonomy dimensions overlap. The 2024–2026 volumes rise (113, 172, 214), without a recent-year collapse or preprint majority. The before-search inventory and year/venue/status cross-tabs remain in `data/processed/systematic_literature_2026_09/corpus_inventory.csv` and `corpus_summary.json`.\n',
           'The existing [taxonomy and scope boundary](data_schema.md) govern this audit. Fully generated images and generative editing are core; deepfake and traditional manipulation preserve historical/mixed coverage. Localization needs an explicit objective and evaluation. Heatmaps or explanations alone do not establish localization. Generation-only, downstream synthetic-data use, feature/causal/data attribution, audio/text-only and video-only endpoints are outside scope. Active fingerprints, watermark hybrids, attacks and traditional-only work require precedent review when the boundary is unclear.\n',
           '## Reproducible method and identity rules\n',
           'A: official venue/year indexes and bounded OpenAlex/Crossref/Hugging Face searches. B: one-hop references and up to 50 most-recent citing works per selected seed, capped at 2026-09-12. C: bounded family queries plus original/companion source checks; ordinary dataset use is not a lineage gap. D: every reference in four survey bibliographies, including all 135 source-attribution references. Surveys are discovery evidence, never sole inclusion evidence.\n',
           'The index title gate uses forensic/forgery/deepfake, attribution/provenance/fingerprint/watermark and proximity combinations of detection/localization/identification/authenticity with generated/synthetic/image/diffusion/GAN. Search terms include synthetic-image detection, image-forgery attribution, dataset-family names, and AI-generated-image localization/attribution. Every query, bound, status, timestamp and cache path is retained in source manifests. Source lookups and primary verification are not counted as independently discovered papers.\n',
           'Matching order: DOI → arXiv → OpenAlex → exact normalized title → reviewed alternate/typographic title → authors/year/venue → method/acronym → bounded fuzzy suggestions. Exact full-title plus author agreement can identify a known work despite database version-ID disagreement; discrepancies remain in provenance and are not made curated aliases. A repeated D³ superscript was resolved using the full subtitle, five authors, year, venue and pages. ForenX was verified as distinct from the fuzzy Ji et al. neighbor using arXiv identity, authors and method/dataset evidence. Fuzzy similarity alone never establishes absence or identity.\n',
           'Active exclusions are checked by strong IDs, exact title and existing curated-identity bridges before candidate status. No exclusion was reopened. Source Generator Attribution via Inversion matches the retained canonical public paper and a separately excluded duplicate by title; its existing-corpus status takes precedence, with both identities retained for traceability. Confirmed versions are collapsed into one work with all observations retained, so a zero DUPLICATE_VERSION total does not imply that version duplicates were absent. Review labels are hypotheses, not proposed corpus mutations. Tier 1 requires an explicit primary-reviewed adjudication; uncertain cases remain review/ambiguous.\n',
           '## Coverage matrix and official-index screening\n',
           '**FULL_ENUMERATION: none claimed.** Complete official books were downloaded for the rows below, but the audit semantically screened a broad title-selected subset, not every paper. A title gate cannot establish exhaustive conceptual coverage. Therefore all these venue/year audit rows remain **BOUNDED_SEARCH**, even when every title in the downloaded book was enumerated.\n',
           '“Unique evaluated” means assigned a reconciliation/scope outcome, including explicit uncertainty. It does not mean every work received full-text manual review. The primary-abstract column distinguishes usable title-matched paper evidence from bibliography/index-only evidence. Existing identities retain corpus decisions; explicit unrelated target tasks are screened out; uncertain forensic crossover cases remain open. Rule-assisted screening and explicit adjudications are preserved separately in the audit scripts and review inputs.\n',
           table(['Official source / track', 'Index records', 'Selected observations', 'Unique evaluated', 'With primary abstract', 'Existing current/alternate', 'Excluded', 'Tier 1', 'Tier 2', 'Ambiguous', 'Out of scope'],
                 [(f'[{e["seed"]}]({e["source"]})' + (' — ' + e['track'] if e.get('track') else ''), e['enumerated'], e['screened'], e['unique_evaluated'], e['with_usable_primary_abstract'],
                   f'{e["EXISTING_CURRENT"]}/{e["EXISTING_ALTERNATE_TITLE"]}', e['EXISTING_EXCLUSION'], e['CANDIDATE_ADD_HIGH_CONFIDENCE'], e['CANDIDATE_ADD_NEEDS_SCOPE_REVIEW'], e['AMBIGUOUS_IDENTITY'] + e['AMBIGUOUS_SCOPE'], e['OUT_OF_SCOPE']) for e in stats['proceedings']]),
           'NeurIPS 2025 required a correction: both initial year endpoints returned **64 Creative AI papers only**. Their track-labelled results remain in the log. The linked `vol38-main-conference` book subsequently provided **5,823 main/position/dataset-track papers**. Main-conference statistics above come from that separate source; Creative AI is never presented as the whole conference. Official ICLR proceedings provided usable alternatives to the blocked OpenReview API; no blocked API response was treated as venue enumeration.\n',
           'Database/keyword venue-year coverage below remains bounded; a successful zero-result query says nothing about complete venue coverage. A source-ID or container query is not an official proceedings enumeration.\n']
    by_seed = {}
    for s in stats['sources']:
        if s['channel'] == 'A' and s['kind'] in {'discovery_search', 'crossref_search', 'openreview_index'}:
            by_seed.setdefault(s['seed'], []).append(s)
    out.append(table(['Venue/year search cell', 'Coverage', 'Successful/attempted requests'],
                     [(seed, 'BOUNDED_SEARCH' if any(s['status'] == 200 for s in group) else 'NOT_AVAILABLE', f'{sum(s["status"] == 200 for s in group)}/{len(group)}') for seed, group in sorted(by_seed.items())]))
    out += ['No usable complete proceedings were established for ECCV 2026, ICML 2026, IJCAI 2026, NeurIPS 2026 or ACM MM 2024–2026 in this audit. ICLR/ICML generic database source IDs, and several signal-processing conference source IDs, have uneven indexing; zero hits are not evidence of absence. No future 2026 publication is presumed discoverable. No missing-edition conclusion is inferred from unsearched years.\n',
            '## Retrieval limitations\n']
    failures = [s for s in stats['sources'] if s['status'] not in (200, 'CLI_SUCCESS')]
    out.append(table(['Failure / unavailable result', 'Requests'], Counter(str(s['http_status'] or s['status']) for s in failures).most_common()))
    out += ['The guessed CVPR2026F URL returned HTTP 404 and remains logged. Five OpenReview API requests returned 403; IJCAI 2026 returned 404. OpenAlex and Crossref rate limits interrupted portions of journal fallback searches. Some publisher DOI resolutions returned empty HTTP 202 responses or 403; these are not usable primary evidence. CLI searches expose exit status, not HTTP status; the log preserves that distinction. The earlier declined compound command was an approval/account-usage event, not an HTTP retrieval failure.\n',
            'All successes and failures, exact URLs, query/filter, bounds, timestamps, hashes and paths are in `source_coverage.json` and the original `*_sources.json` manifests. Raw responses are checksum-verified compressed original bytes. Unversioned arXiv HTML means the bibliography is the cached version available on the retrieval date, not necessarily the first preprint bibliography. No inaccessible source was treated as an empty literature set.\n',
            '## Citation/reference graph\n']
    seed_rows = []
    for s in stats['sources']:
        if s['kind'] != 'seed_metadata' or s['status'] != 200:
            continue
        seed = json.loads(read_response(s))
        refs = set(seed.get('referenced_works', []))
        retrieved = set()
        cited_count = 0
        citation_total = None
        for source in stats['sources']:
            if source['channel'] != 'B' or source['seed'] != s['seed'] or source['status'] != 200:
                continue
            data = json.loads(read_response(source))
            if source['kind'] == 'reference_works':
                retrieved.update(r['id'] for r in data.get('results', []))
            elif source['kind'] == 'citing_works':
                cited_count += len(data.get('results', []))
                citation_total = data.get('meta', {}).get('count')
        seed_rows.append((s['seed'], len(refs), len(refs & retrieved), len(refs - retrieved), cited_count, citation_total if citation_total is not None else 'unavailable'))
    out.append(table(['Seed', 'Graph reference IDs', 'Retrieved reference IDs', 'Unresolved IDs', 'Citing window returned', 'Database citing count'], seed_rows))
    out += ['A zero reference list or citing count can reflect incomplete indexing, especially for recent seeds. It does not establish no references/citations. The separate primary PDF survey extraction supplies 135 references despite incomplete graph metadata. Every retained graph observation records seed, REFERENCES/CITED_BY direction, rank and discovery pass; references preserve seed order when recoverable, while citing ranks are returned database order. No recursive crawl was performed.\n',
            '## Survey bibliography outcomes\n',
            table(['Survey / primary bibliography', 'All references screened', 'Current', 'Alternate', 'Excluded', 'Duplicate', 'Tier 1', 'Tier 2', 'Ambiguous', 'Out of scope'],
                  [(f'[{e["seed"]}]({e["source"]})', e['enumerated'], e['reference_outcomes']['EXISTING_CURRENT'], e['reference_outcomes']['EXISTING_ALTERNATE_TITLE'], e['reference_outcomes']['EXISTING_EXCLUSION'], e['reference_outcomes']['DUPLICATE_VERSION'], e['reference_outcomes']['CANDIDATE_ADD_HIGH_CONFIDENCE'], e['reference_outcomes']['CANDIDATE_ADD_NEEDS_SCOPE_REVIEW'], e['reference_outcomes']['AMBIGUOUS_IDENTITY'] + e['reference_outcomes']['AMBIGUOUS_SCOPE'], e['reference_outcomes']['OUT_OF_SCOPE']) for e in stats['surveys']]),
            'Survey set: Methods and Trends in Detecting AI-Generated Images (2502.15176); Fully AI-Generated Image Detection: Definition, Recent Advances and Challenges (2502.19716); A Survey of Defenses Against AI-Generated Visual Media (2407.10575); Source Attribution of AI-Generated Images: a Principled Survey (Zenodo 20814592). All **135/135** references in the latter have a registry outcome, including generation/background works. Counts here are reference observations; global totals count unique reconciled works.\n',
            '## Dataset and benchmark lineage review\n',
            table(['Family', 'Original/benchmark presence', 'Challenge/expansion', 'Direct associated work / limitation'],
                  [(r['family'], r['original_dataset_or_benchmark'] + ' — ' + r['presence'], r['benchmark_challenge'] + ' ' + r['expanded_version'], r['associated_method']) for r in stats['lineages']]),
            'The bounded lineage inventory covers the 17 selected families above. “No separate work established” is a search limitation, not a claim that no such work exists. The NTIRE report is a missing foundational challenge; IMDL-BenCo is a scope review. The Western-blot paper was discovered via D and is a separate missing scientific-image dataset/method. Lineage annotation does not manufacture independent C overlap for an A- or D-discovered paper.\n',
            '## Reconciliation totals\n', table(['Final status', 'Unique works'], count.items()),
            '## Retrieval and evaluation by channel\n',
            table(['Channel', 'Raw records', 'Selected observations', 'Unique evaluated', 'Current', 'Alternate', 'Exclusions', 'Tier 1', 'Tier 2', 'Ambiguous', 'Out of scope', 'Duplicate'],
                  [(ch, d['raw_records'], d['selected_observations'], d['unique_evaluated'], d['EXISTING_CURRENT'], d['EXISTING_ALTERNATE_TITLE'], d['EXISTING_EXCLUSION'], d['CANDIDATE_ADD_HIGH_CONFIDENCE'], d['CANDIDATE_ADD_NEEDS_SCOPE_REVIEW'], d['AMBIGUOUS_IDENTITY'] + d['AMBIGUOUS_SCOPE'], d['OUT_OF_SCOPE'], d['DUPLICATE_VERSION']) for ch, d in stats['channels'].items()]),
            'Per-channel unique totals overlap and must not be summed. Raw records include unselected index/background items; selected observations include repeated sightings. C includes corpus-seeded family verification, so channel overlap is descriptive and is not a statistical independence or completeness estimator. Primary evidence checks never create a discovery channel.\n',
            table(['Exact channel combination', 'Unique works'], stats['overlaps'].items()),
            table(['Multi-channel Tier 1 work', 'Channels'], [(r['canonical_title'], r['discovery_channels']) for r in high if '+' in r['discovery_channels']]),
            '## Yield and stopping decision\n',
            table(['Pass', 'Raw', 'Selected', 'Unique in pass', 'First-seen works', 'Current', 'Alternate', 'Excl.', 'Tier 1', 'Tier 2', 'Ambig.', 'Out', 'Duplicate status', 'First-seen Tier 1'],
                  [(p['pass'], p['raw_records'], p['selected_observations'], p['unique_evaluated'], p['first_seen_works'], p['EXISTING_CURRENT'], p['EXISTING_ALTERNATE_TITLE'], p['EXISTING_EXCLUSION'], p['CANDIDATE_ADD_HIGH_CONFIDENCE'], p['CANDIDATE_ADD_NEEDS_SCOPE_REVIEW'], p['AMBIGUOUS_IDENTITY'] + p['AMBIGUOUS_SCOPE'], p['OUT_OF_SCOPE'], p['DUPLICATE_VERSION'], p['first_seen_high_confidence']) for p in stats['passes']]),
            'Pass 7 was a 40-result detection search completed before the latest reconciliation-only instruction. Its marginal yield is the first-seen Tier 1 column, not all Tier 1 sightings in that pass. Later requests resolved named candidates only. Broad discovery is stopped: the validation window is predominantly already represented/excluded/out of scope, and the current priority is adjudicating the evidence already collected. This satisfies a bounded diminishing-return criterion; it does **not** establish exhaustive venue coverage, especially in rate-limited journals. No additional broad pass was run after the discovery freeze.\n',
            '## Gap diagnosis\n',
            'The confirmed gaps include core localization/editing work (DeCLIP, weakly supervised diffusion-image localization, Detective SAM), a scientific-image dataset/method, recent detector methods and a 2026 challenge report. Thus the small localization/editing counts partly reflect identifiable omissions; their smaller size alone was not used as evidence. Localization labels were withheld when evidence established only explanatory heatmaps (for example SPECTRA-Net).\n',
            'Source attribution appears comparatively strong in the principled survey cross-check: most relevant passive-attribution references already match. Active fingerprinting and geometric/model-level attribution remain scope questions rather than confirmed passive-attribution gaps. Major selected dataset families are present, but the NTIRE foundational report and Western-blot dataset show that checklist completion did not guarantee dataset completeness. Deepfake/traditional-manipulation and watermark boundary cases dominate much of the review burden and should not be counted as confirmed missing core literature.\n',
            'Recent 2026 work contributes several confirmed gaps, but the audit does not establish that 2026 is proportionately worse covered than 2024 or 2025. The venue/year denominators are not a complete in-scope census. Journal and less accessible proceedings coverage remains weaker; the growing corpus volume alone cannot certify coverage.\n']
    for tier, dimensions in stats['gaps'].items():
        out.append('### ' + ('Confirmed gaps' if tier == 'confirmed' else 'Review hypotheses — not confirmed gaps') + '\n')
        for dimension, values in dimensions.items():
            out.append(table([dimension, 'Works (multi-label where applicable)'], values.items()))
    out += ['## Tier 1 — every high-confidence missing work\n',
            'Identifiers below are the observed publication/preprint identifiers; the primary-evidence links establish scope. Full source observations, authors, identity checks and rationale are in the canonical CSV. No record has been added to the corpus.\n',
            table(['Candidate / title', 'Authors', 'Year / venue', 'DOI; arXiv; OpenAlex', 'Channels', 'Task / scope / type', 'Primary evidence and absence rationale'],
                  [(r['candidate_id'] + ' — ' + r['canonical_title'], r['authors'], r['year'] + ' / ' + r['venue'], '; '.join(x for x in [r['doi'], r['arxiv_id'], r['openalex_id']] if x), r['discovery_channels'], ' / '.join([r['proposed_forensic_task'], r['proposed_image_scope'], r['proposed_research_type']]), links(r['primary_evidence_url']) + ' ' + r['scope_evidence'] + ' ' + r['identity_evidence']) for r in high]),
            '## Tier 2 — every scope-precedent review\n',
            table(['Candidate / title', 'Year', 'Exact scope issue', 'Primary evidence'], [(r['candidate_id'] + ' — ' + r['canonical_title'], r['year'], r['rationale'], links(r['primary_evidence_url'])) for r in tier2]),
            '## Tier 3 — every unresolved identity/scope case\n',
            table(['Candidate / title', 'Status', 'Unresolved issue / evidence limitation', 'Discovery evidence'], [(r['candidate_id'] + ' — ' + r['canonical_title'], r['final_status'], r['rationale'], links(r['primary_evidence_url'] or r['discovery_sources'])) for r in tier3]),
            '## Next-step handoff\n',
            'The next task should reconcile only Tier 1, Tier 2 policy questions, and Tier 3 cases where a specific attainable source can resolve the stated ambiguity. Use the canonical candidate IDs and cached primary evidence; preserve exclusion and scope precedents. No further broad literature search is recommended. Any corpus additions require a separate curation task.\n',
            '## Repository integrity and regeneration\n']
    validation_path = PROCESSED / 'validation.json'
    validation = json.loads(validation_path.read_text()) if validation_path.exists() else {'state': 'Validation pending; this is a draft.'}
    out.append('```json\n' + json.dumps(validation, indent=2, sort_keys=True) + '\n```\n')
    out += ['The frozen baseline is `baseline_sha256.json`: all pre-existing data/web paths are compared byte-for-byte. Earlier uncommitted curation and baseline-test cleanup are preserved; git status alone cannot distinguish those earlier changes from this audit. No authoritative data, public exports or frontend assets were changed by the literature audit. No commit or push was performed.\n',
            'Offline regeneration from repository root:\n\n```sh\npython3 scripts/verify_systematic_literature_sources.py extract\npython3 scripts/parse_systematic_literature.py\npython3 scripts/reconcile_systematic_literature.py\npython3 scripts/screen_systematic_literature.py\npython3 scripts/report_systematic_literature.py\n```\n',
            'The screening script writes only a processed draft. It never overwrites the manual canonical CSV; subsequent human changes remain authoritative. PDF text extraction is recorded separately and can be repeated with the bundled pypdf runtime. Primary adjudications and semantic exclusions are durable review inputs, separate from raw responses.\n',
            'Audit-created files: `data/raw/systematic_literature_2026_09/`, `data/processed/systematic_literature_2026_09/`, the canonical candidate CSV, this generated report, the systematic-literature collection/parsing/reconciliation/report scripts and focused tests. Source logs include failed and unused navigation/verification responses. No unrelated pre-existing changes were discarded.\n']
    return '\n'.join(out)


def generate(draft=False):
    path = PROCESSED / 'candidate_registry_draft.csv' if draft else CANONICAL
    rows = read_csv(path)
    stats = accounting(rows)
    for name, value in [('audit_statistics.json', {k: v for k, v in stats.items() if k != 'sources'}), ('source_coverage.json', stats['sources']), ('lineage_review.json', stats['lineages'])]:
        (PROCESSED / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    output = PROCESSED / 'report_draft.md' if draft else REPORT
    output.write_text(render(rows, stats, path))
    print(json.dumps({'report': str(output.relative_to(ROOT)), 'works': len(rows), 'counts': stats['status_counts']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', action='store_true')
    generate(parser.parse_args().draft)

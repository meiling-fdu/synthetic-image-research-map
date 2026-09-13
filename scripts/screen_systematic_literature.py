#!/usr/bin/env python3
"""Create an auditable screening draft; never overwrite the canonical manual CSV.

The broad gate only selects observations. New high-confidence decisions require
an explicit primary-reviewed adjudication; automatic uncertain labels stay open.
"""
import csv
import hashlib
import io
import json
import re
from collections import Counter
from collect_systematic_literature import ROOT, PROCESSED
from reconcile_systematic_literature import compact_title, corpus_id
from audit_key_paper_coverage import identity_values, norm_title

STATUSES = ('EXISTING_CURRENT', 'EXISTING_ALTERNATE_TITLE', 'EXISTING_EXCLUSION',
            'CANDIDATE_ADD_HIGH_CONFIDENCE', 'CANDIDATE_ADD_NEEDS_SCOPE_REVIEW',
            'AMBIGUOUS_IDENTITY', 'AMBIGUOUS_SCOPE', 'OUT_OF_SCOPE',
            'DUPLICATE_VERSION', 'EXCLUSION_REVIEW_RECOMMENDED')
FIELDS = ('candidate_id', 'canonical_title', 'authors', 'year', 'venue', 'doi', 'arxiv_id',
          'openalex_id', 'discovery_channels', 'discovery_sources', 'venue_year_sources',
          'citation_seeds', 'surveys', 'benchmark_lineages', 'normalized_title_match',
          'matched_corpus_paper_id', 'matched_exclusion_id', 'proposed_forensic_task',
          'proposed_image_scope', 'proposed_research_type', 'identity_evidence', 'scope_evidence',
          'primary_evidence_url', 'final_status', 'confidence', 'rationale', 'manual_review',
          'discovery_passes', 'observation_count', 'observation_provenance', 'method_acronym_matches')


def joined(values):
    return ' | '.join(sorted({str(v) for v in values if v not in ('', None)}))


def provisional_scope(group, evidence):
    title = group['title']
    lower = title.casefold()
    # Explicit target-task exclusions, rather than positive keyword inclusion.
    other_targets = {
        'object/scene recognition, not synthetic-image forensics': r'object detect|3d detect|lane detect|pedestrian detect|person re.ident|person retriev|vessel detect|drone detect|aerial image objects|wildlife|pose estimation|human.object interaction|building (change|attribute)|change detection|shadow detection|salien|medical image re.ident|image.prompted object|ground.to.satellite',
        'anomaly/OOD detection with generative models as tools': r'anomaly detect|anomaly localiz|out.of.distribution|out.of.domain|\bood\b|outlier detect|outlier synthesis|misclassified',
        'feature/data/causal attribution or model explanation, not generator-source attribution': r'feature attribution|data attribution|training.data attribution|training data provenance|causal attribut|neuron attribut|weight attribut|variable.{0,15}attribut|input attribut|attribut.{0,15}input|failure attribut|reward attribut|attribution.{0,15}explain|attribut.{0,20}language model|attribut.{0,15}neural network|influence function|data valuation|data contribution|data provenance|model provenance|membership inference|membership privacy|gradient attribution|integrated attribution',
        'text/audio/music forensics rather than an image-level task': r'audio (deepfake|watermark|temporal)|speech forgery|speech.forensic|text forgery|text watermark|language model.{0,30}(watermark|signature)|watermark.{0,40}language model|watermark.{0,40}llm|large.scale.{0,20}music|text.to.music|lyric|sentence come from|language models radioactive|token rewards',
        'non-media forensics or biometric sensor identification': r'community forensic|forensic (mental|psychiatr|assertive)|forensic science in the united|bacterial community|stalking recidivism|cyber campaign|camera identification|sensor pattern noise|source camera|oct fingerprint|fingerprint extraction|fingerprint data.set|fingerprint sensors|synthetic defocus|forensic knowledge graphs',
        'generation, restoration, editing control or representation learning rather than forensic inference': r'attribute editing|attribute manipulation|attribute control|attribute alignment|attribute translation|attribute disentang|attribute tokens|attribute derivation|attribute extraction|attribute.to.location|attribute.rich|attribute substitutions|attribute domains|attributes guided|attributes.{0,30}synthesis|attributes.{0,30}generation|visual.ground|image super.resolution|spurious correlations in image recognition|training data synthesis|model collapse|memorization|bias detection|evaluat.{0,15}bias|diversity measurement|interpolants|generative adversarial nets|gan training|photorealistic image generation|text.to.image generation|image synthesis|diffusion probabilistic models|attention is all you need|imagenet|microsoft coco|lazy learning|steganalysis',
    }
    forensic_title = bool(re.search(r'forensic|forger|deepfake|fake image|image.{0,30}(detect|attribut|authentic|manipul)|synthetic.{0,30}(detect|attribut)|generat.{0,40}(detect|attribut)|source generator|model attribution', lower))
    for reason, pattern in other_targets.items():
        if re.search(pattern, lower):
            # A direct forensic endpoint wins over a generic generation phrase.
            if reason.startswith('generation,') and forensic_title:
                continue
            return 'OUT_OF_SCOPE', reason, '', '', ''
    if re.search(r'video|audio.visual|audio.video|multimodal.*temporal|temporal forgery', lower):
        if re.search(r'image.and.video|image.level|multi.modal|multimodal', lower):
            return 'CANDIDATE_ADD_NEEDS_SCOPE_REVIEW' if evidence else 'AMBIGUOUS_SCOPE', 'Separate the substantive image-level forensic evaluation from the video/audio or temporal components; inclusion precedent requires review.', 'detection', 'deepfake', 'benchmark' if 'bench' in lower or 'dataset' in lower else 'method'
        return 'OUT_OF_SCOPE', 'The declared endpoint is video/temporal or audio-visual forensics; no separate image-level contribution was established in the available evidence.', '', '', ''
    if re.search(r'evad|adversarial (attack|reality|fake)|backdoor attack|poisoned forgery|red teaming|trace.*eliminat|watermark remov|disrupt|protect.*deepfake|defen[cs]e.*deepfake', lower):
        return 'CANDIDATE_ADD_NEEDS_SCOPE_REVIEW' if evidence else 'AMBIGUOUS_SCOPE', 'Determine whether the detector attack/prevention study contributes substantive forensic detection or attribution beyond evasion/protection under current exclusion precedent.', 'detection', 'fully_generated' if 'image' in lower else 'deepfake', 'analysis_study'
    if re.search(r'watermark|fingerprinting|signature|provenance|copyright', lower):
        if re.search(r'3d|gaussian splat|radiance field|model watermark|watermark.*neural network|neural network.*watermark', lower):
            return 'OUT_OF_SCOPE', 'Model/3D asset ownership or embedded watermark robustness is the target; no image-level synthetic-media forensic endpoint established.', '', '', ''
        return 'CANDIDATE_ADD_NEEDS_SCOPE_REVIEW' if evidence else 'AMBIGUOUS_SCOPE', 'Verify that watermark/provenance recovery provides project-scope image detection or source attribution, beyond watermark embedding, robustness, ownership, or content protection.', 'source_attribution', '', 'method'
    if forensic_title:
        task = 'localization' if re.search(r'localiz|segment', lower) else 'source_attribution' if re.search(r'attribut|source trac|generator identif', lower) else 'detection'
        kind = 'survey' if re.search(r'survey|review', lower) else 'benchmark' if re.search(r'benchmark|dataset|challenge|bench:', lower) else 'method'
        if re.search(r'face|deepfake', lower):
            scope, issue = 'deepfake', 'Confirm a substantive image-level face-manipulation contribution and distinguish it from video-only evaluation; apply the existing deepfake crossover precedent.'
        elif re.search(r'manipulat|forgery|inpaint|edit', lower):
            scope, issue = '', 'Establish whether evaluation covers generative editing/partial synthesis, traditional manipulation, or both; traditional-only inclusion precedent needs review.'
        else:
            scope, issue = 'fully_generated', 'Primary evidence is insufficient to establish the precise image-level forensic contribution and supported taxonomy; verify the paper before inclusion.'
        return 'CANDIDATE_ADD_NEEDS_SCOPE_REVIEW' if evidence else 'AMBIGUOUS_SCOPE', issue, task, scope, kind
    return 'OUT_OF_SCOPE', 'Screened as background generation, recognition, general explanation, or another non-forensic target; no synthetic-image detection, generator attribution, or manipulation-localization contribution identified.', '', '', ''


def build():
    groups = json.loads((PROCESSED / 'candidate_queue.json').read_text())
    papers = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    public = {corpus_id(p): p for p in papers}
    adjudications = json.loads((PROCESSED / 'adjudications.json').read_text()) if (PROCESSED / 'adjudications.json').exists() else {}
    decisions = {compact_title(k): v for k, v in adjudications.items()}
    for review in json.loads((PROCESSED / 'semantic_exclusions.json').read_text()):
        for title in review['titles']:
            decisions[compact_title(title)] = dict(final_status='OUT_OF_SCOPE', proposed_forensic_task='', proposed_image_scope='', proposed_research_type='', scope_evidence=review['reason'], rationale=review['reason'], manual_review='false')
    result = []
    requests = json.loads((PROCESSED / 'primary_sources.json').read_text())
    for group in groups:
        observations = group['observations']
        primary = list({e['primary_url']: e for o in observations for e in o.get('primary_evidence', []) if e['title'] and len(e['abstract']) > 100}.values())
        row = {field: '' for field in FIELDS}
        row.update(candidate_id=group['candidate_id'], canonical_title=group['title'],
                   matched_corpus_paper_id=group['matched_corpus_paper_id'],
                   matched_exclusion_id=joined(group['exclusion_ids']),
                   discovery_channels='+'.join(group['channels']),
                   discovery_sources=joined(o['discovery_source'] for o in observations),
                   venue_year_sources=joined(o['seed'] for o in observations if o['channel'] == 'A'),
                   citation_seeds=joined(o['seed'] for o in observations if o['channel'] == 'B'),
                   surveys=joined(o['seed'] for o in observations if o['channel'] == 'D'),
                   benchmark_lineages=joined(o['seed'] for o in observations if o['channel'] == 'C'),
                   primary_evidence_url=joined(e['primary_url'] for e in primary),
                   discovery_passes=joined(o['discovery_pass'] for o in observations),
                   observation_count=str(len(observations)),
                   observation_provenance=json.dumps([{k: o.get(k, '') for k in ('channel', 'discovery_source', 'source_record_id', 'seed', 'direction', 'rank', 'discovery_pass', 'retrieval_bound', 'raw_path')} for o in observations], sort_keys=True))
        metadata = sorted(primary, key=lambda e: (not e.get('authors'), not e.get('year'))) + observations
        for field in ('authors', 'year', 'venue'):
            row[field] = next((str(o[field]) for o in metadata if o.get(field)), '')
        if not row['venue'] and any(e.get('arxiv_id') for e in primary):
            row['venue'] = 'arXiv'
        if any('/CVPR2026W/NTIRE/' in e['primary_url'] for e in primary):
            row['venue'] = 'CVPR 2026 NTIRE Workshop'
        ids = {k: set() for k in ('doi', 'arxiv', 'openalex')}
        for o in observations + primary:
            for k, values in identity_values(o).items():
                ids[k].update(values)
        row.update(doi=joined(ids['doi']), arxiv_id=joined(ids['arxiv']), openalex_id=joined(ids['openalex']))
        method = re.match(r'^([\w-]{2,22}):', group['title'])
        if method:
            row['method_acronym_matches'] = joined(corpus_id(p) for p in papers if p['title'].casefold().startswith(method[1].casefold() + ':'))
        row['identity_evidence'] = ('Matched by ' + joined(group['identity_matches']) if group['identity_matches'] else 'DOI/arXiv/OpenAlex, normalized/typographic title and reviewed aliases checked against 620 public papers and active exclusions; no confirmed match.')
        if group['fuzzy_suggestions']:
            row['identity_evidence'] += ' Fuzzy suggestions (not automatic matches): ' + json.dumps(group['fuzzy_suggestions'], sort_keys=True)
        if group['conflicts']:
            row['identity_evidence'] += ' ' + joined(group['conflicts'])
        row['identity_evidence'] += ' Authors/year/venue, method/acronym and bounded fuzzy suggestions were considered; observed publication/preprint IDs are preserved, not promoted to curated aliases.'
        if group['matched_corpus_paper_id']:
            p = public[group['matched_corpus_paper_id']]
            alternate = any('version' in k or 'alternate' in k for k in group['identity_matches']) or any(compact_title(o['title']) != compact_title(p['title']) for o in observations)
            row.update(final_status='EXISTING_ALTERNATE_TITLE' if alternate else 'EXISTING_CURRENT', confidence='high', manual_review='false',
                       normalized_title_match=p['title'], rationale='Already represented in the frozen public corpus; observed source variants and identifiers remain in provenance.',
                       scope_evidence='Existing curated/public taxonomy retained for audit comparison; no classification changed.',
                       proposed_forensic_task=joined(p.get('tasks', [])), proposed_image_scope=joined(p.get('image_scopes', [])), proposed_research_type=joined(p.get('research_types', [])))
        elif group['exclusion_ids']:
            row.update(final_status='EXISTING_EXCLUSION', confidence='high', manual_review='false', rationale='Matches an active exclusion, including curated-identity bridges. Decision retained.', scope_evidence='Authoritative exclusion registry; no reopening.')
        else:
            status, reason, task, scope, kind = provisional_scope(group, primary)
            row.update(final_status=status, rationale=reason, scope_evidence=reason,
                       proposed_forensic_task=task, proposed_image_scope=scope, proposed_research_type=kind,
                       confidence='medium' if primary or status == 'OUT_OF_SCOPE' else 'low', manual_review='false' if status == 'OUT_OF_SCOPE' else 'true')
            if group['conflicts'] or any(s['similarity'] >= .85 for s in group['fuzzy_suggestions']):
                row.update(final_status='AMBIGUOUS_IDENTITY', manual_review='true', confidence='low', rationale='Resolve the recorded identifier/title collision before assessing absence; fuzzy similarity alone cannot establish identity.')
            decision = decisions.get(compact_title(group['title']))
            if decision:
                row.update(decision)
                if row['final_status'] == 'OUT_OF_SCOPE':
                    row.update(manual_review='false', confidence='high' if primary else 'medium')
                if row['final_status'] == 'CANDIDATE_ADD_HIGH_CONFIDENCE':
                    if not primary or group['conflicts']:
                        raise ValueError('High-confidence decision lacks primary evidence or has identity conflict: ' + group['title'])
                    row.update(confidence='high', manual_review='false')
            row['scope_evidence'] = row.get('scope_evidence') or row['rationale']
            if row['final_status'] in ('CANDIDATE_ADD_NEEDS_SCOPE_REVIEW', 'AMBIGUOUS_SCOPE'):
                if primary:
                    row['scope_evidence'] += ' Cached primary abstract: ' + primary[0]['abstract']
                    row['rationale'] += ' For this work, inspect the primary abstract preserved in scope_evidence and resolve the stated endpoint/precedent question.'
                else:
                    attempts = [s for s in requests if s.get('paper_title', s.get('seed', '')) in {o['title'] for o in observations}]
                    limitation = '; '.join(s['url'] + ' — ' + str(s.get('error') or s['status']) for s in attempts)
                    row['rationale'] += ' Paper-specific evidence limitation: ' + (limitation if limitation else 'no title-matched usable primary abstract in the cached evidence; the retained bibliography/index record alone cannot resolve scope.')
        result.append(row)
    result.sort(key=lambda r: r['canonical_title'].casefold())
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=FIELDS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(result)
    (PROCESSED / 'candidate_registry_draft.csv').write_text(out.getvalue())
    print(json.dumps({'works': len(result), 'status': dict(Counter(r['final_status'] for r in result))}, indent=2))
    return result


if __name__ == '__main__':
    build()

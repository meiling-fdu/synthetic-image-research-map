#!/usr/bin/env python3
"""Build review queues; authoritative registries and final manual CSV are read-only."""
import csv
import json
import hashlib
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
try:
    from .collect_systematic_literature import ROOT, PROCESSED
    from .audit_key_paper_coverage import PaperIndex, norm_title, identity_values
    from .parse_systematic_literature import text
    from .paper_exclusions import active_exclusions, exclusions_with_curated_identities, matching_exclusion_rows
except ImportError:
    from collect_systematic_literature import ROOT, PROCESSED
    from audit_key_paper_coverage import PaperIndex, norm_title, identity_values
    from parse_systematic_literature import text
    from paper_exclusions import active_exclusions, exclusions_with_curated_identities, matching_exclusion_rows


def read_csv(path):
    with path.open(newline='', encoding='utf-8-sig') as handle:
        return list(csv.DictReader(handle))


def compact_title(title):
    return norm_title(text(title).replace('&', ' and ')).replace(' ', '')


def corpus_id(paper):
    return paper.get('paper_id') or paper.get('openalex_url') or ('arxiv:' + paper['arxiv_id'] if paper.get('arxiv_id') else 'doi:' + paper.get('doi', ''))


def author_tokens(row):
    authors = row.get('authors') or []
    if isinstance(authors, list):
        authors = '; '.join(a.get('name', '') if isinstance(a, dict) else str(a) for a in authors)
    return set(re.findall(r'[a-z]{3,}', authors.casefold())) - {'and', 'etal'}


def reconcile():
    papers = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    public = PaperIndex(papers)
    titles = {compact_title(p['title']): i for i, p in enumerate(papers)}
    aliases = {}
    identity_path = PROCESSED / 'identity_adjudications.json'
    if identity_path.exists():
        for title, decision in json.loads(identity_path.read_text()).items():
            matches = [i for i, p in enumerate(papers) if corpus_id(p) == decision['matched_corpus_paper_id']]
            if len(matches) != 1:
                raise ValueError('Invalid audit identity adjudication: ' + title)
            aliases[compact_title(title)] = matches[0]
    for decision in json.loads((ROOT / 'data/manual/key_paper_reconciliation.json').read_text())['records']:
        if decision['classification'].startswith(('SAME_PAPER', 'EXISTING_CURRENT')):
            i, _, _ = public.match(decision.get('resolved', {}))
            if i is not None:
                aliases[compact_title(decision['checklist']['title'])] = i
    evidence_path = PROCESSED / 'primary_evidence.json'
    primary = json.loads(evidence_path.read_text()) if evidence_path.exists() else []
    by_url = {r['primary_url']: r for r in primary}
    by_title = {}
    for r in primary:
        by_title.setdefault(compact_title(r['requested_title']), []).append(r)
    curated = read_csv(ROOT / 'data/curated/papers.csv')
    exclusions = active_exclusions(exclusions_with_curated_identities(
        read_csv(ROOT / 'data/curated/paper_exclusions.csv'), curated))
    groups = {}
    for observation in json.loads((PROCESSED / 'observations.json').read_text()):
        observation = dict(observation)
        index, kind, conflict = public.match(observation)
        nt = compact_title(observation['title'])
        candidates = by_title.get(nt, [])
        if observation.get('primary_url') in by_url:
            candidates = candidates + [by_url[observation['primary_url']]]
        verified = []
        for source in candidates:
            # A response/page title must agree; a generic error page is not evidence.
            if not source['title'] or compact_title(source['title']) != nt:
                continue
            verified.append(source)
            pi, pk, pc = public.match(source)
            if pi is not None and index is None:
                index, kind, conflict = pi, 'primary_' + pk, ''
        observation['primary_evidence'] = list({r['primary_url']: r for r in verified}.values())
        if index is None and nt in aliases:
            index, kind, conflict = aliases[nt], 'reviewed_alternate_title', ''
        if index is None and nt in titles:
            pi = titles[nt]
            # Typography/line-wrapping equality is exact, not fuzzy. When database
            # IDs conflict, require primary metadata plus author agreement.
            if not conflict or any(author_tokens(r) & author_tokens(papers[pi]) for r in verified):
                index, kind, conflict = pi, 'typographic_title' if not conflict else 'primary_title_authors_version', ''
            elif len(author_tokens(observation) & author_tokens(papers[pi])) >= 3:
                # Existing-paper reconciliation, not a new inclusion: exact full
                # title plus independently recorded authors identifies the work.
                # Keep the disagreeing database identifiers as observed provenance.
                observation['database_identity_discrepancy'] = conflict
                index, kind, conflict = pi, 'exact_title_authors_database_version', ''
        excluded = matching_exclusion_rows(observation, exclusions)
        excluded += [r for r in exclusions if compact_title(r.get('title', '')) == nt]
        for source in verified:
            excluded += matching_exclusion_rows(source, exclusions)
        title = nt
        key = 'public:' + str(index) if index is not None else 'title:' + title
        group = groups.setdefault(key, {'candidate_id': 'audit:' + hashlib.sha256(key.encode()).hexdigest()[:16],
                                      'title': papers[index]['title'] if index is not None else observation['title'],
                                      'matched_corpus_paper_id': corpus_id(papers[index]) if index is not None else '',
                                      'observations': [], 'identity_matches': [], 'conflicts': [],
                                      'exclusion_ids': [], 'fuzzy_suggestions': []})
        group['observations'].append(observation)
        if index is not None:
            group['identity_matches'].append(kind)
        if conflict:
            group['conflicts'].append(conflict)
        group['exclusion_ids'] += [r['exclusion_id'] for r in excluded]
    # Merge equal verified identifiers across novel title variants. Conflicting
    # identities remain in the group for explicit adjudication, never discarded.
    identity_owner = {}
    for key, group in list(groups.items()):
        if key not in groups:
            continue
        keys = set()
        for row in group['observations']:
            for k, values in identity_values(row).items():
                keys.update(k + ':' + v for v in values)
        owners = {identity_owner[k] for k in keys if k in identity_owner and identity_owner[k] in groups}
        if len(owners) == 1:
            owner = next(iter(owners))
            target = groups[owner]
            if not (target['matched_corpus_paper_id'] and group['matched_corpus_paper_id'] and target['matched_corpus_paper_id'] != group['matched_corpus_paper_id']):
                for field in ('observations', 'identity_matches', 'conflicts', 'exclusion_ids'):
                    target[field] += group[field]
                if group['matched_corpus_paper_id']:
                    target['matched_corpus_paper_id'] = group['matched_corpus_paper_id']
                    target['title'] = group['title']
                del groups[key]
                key = owner
        for k in keys:
            identity_owner[k] = key
    for group in groups.values():
        group['channels'] = sorted({r['channel'] for r in group['observations']})
        group['exclusion_ids'] = sorted(set(group['exclusion_ids']))
        group['identity_matches'] = sorted(set(group['identity_matches']))
        if group['identity_matches']:
            group['provisional_status'] = 'EXISTING_CURRENT'
        elif group['exclusion_ids']:
            group['provisional_status'] = 'EXISTING_EXCLUSION'
        else:
            group['provisional_status'] = 'REVIEW_REQUIRED'
            title = norm_title(group['title'])
            for paper in papers:
                other = norm_title(paper['title'])
                if abs(len(title) - len(other)) > max(len(title), len(other)) * .4:
                    continue
                if len(set(title.split()) & set(other.split())) / max(len(set(title.split())), len(set(other.split())), 1) < .55:
                    continue
                similarity = SequenceMatcher(None, title, other).ratio()
                if similarity >= .78:
                    group['fuzzy_suggestions'].append({'paper_id': paper.get('paper_id', ''),
                                                      'title': paper['title'], 'similarity': round(similarity, 4)})
            group['fuzzy_suggestions'].sort(key=lambda r: -r['similarity'])
            group['fuzzy_suggestions'] = group['fuzzy_suggestions'][:5]
    result = sorted(groups.values(), key=lambda r: r['title'].casefold())
    (PROCESSED / 'candidate_queue.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'candidates': len(result), 'status': dict(Counter(r['provisional_status'] for r in result)),
                      'fuzzy_review': sum(bool(r['fuzzy_suggestions']) for r in result)}, indent=2))
    return result


if __name__ == '__main__':
    reconcile()

#!/usr/bin/env python3
"""Render the reviewed Tier 2 policy layer; never write a manual/corpus file."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / 'data/manual/systematic_tier2_scope_policy_clusters_2026_09.csv'
POLICIES = ROOT / 'data/manual/systematic_tier2_scope_policies_2026_09.json'
PROCESSED = ROOT / 'data/processed/systematic_tier2_policy_2026_09'
REPORT = ROOT / 'docs/systematic_tier2_scope_policy_review_2026_09.md'
OUTCOMES = ('LIKELY_INCLUDE', 'LIKELY_EXCLUDE', 'PAPER_SPECIFIC_REVIEW', 'USER_POLICY_DECISION_REQUIRED')
CAUSES = ('POLICY_CONFLICT', 'CURRENT_POLICY_APPLIES', 'PAPER_SPECIFIC_EVIDENCE')
RECOMMENDATIONS = ('RECOMMEND_INCLUDE', 'RECOMMEND_EXCLUDE', 'RECOMMEND_INCLUDE_WITH_CONDITION', 'RECOMMEND_NEEDS_USER_POLICY_DECISION')
SOURCE_STATUS = 'CANDIDATE_ADD_NEEDS_SCOPE_REVIEW'


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def load_inputs():
    return read_csv(CANDIDATES), json.loads(POLICIES.read_text())


def validate(rows, registry):
    """Check joins and disjoint categories before rendering; no classification is inferred."""
    inventory = json.loads((PROCESSED / 'inventory.json').read_text())
    source = read_csv(ROOT / registry['source'])
    selected = [r for r in source if r['final_status'] == SOURCE_STATUS]
    ids = [r['candidate_id'] for r in rows]
    assert len(ids) == len(set(ids)) == 215
    assert ids == sorted(ids)
    assert set(ids) == {r['candidate_id'] for r in selected} == {r['candidate_id'] for r in inventory}
    # Compare the complete frozen evidence, not just IDs or the selected count.
    assert inventory == sorted(selected, key=lambda r: r['candidate_id'])
    policies = {p['cluster_id']: p for p in registry['policies']}
    assert len(policies) == len(registry['policies'])
    assert set(policies) == {r['primary_policy_cluster'] for r in rows}
    original = {r['candidate_id']: r for r in inventory}
    preserved = ('canonical_title', 'year', 'venue', 'doi', 'arxiv_id', 'openalex_id', 'primary_evidence_url', 'discovery_channels', 'proposed_forensic_task', 'proposed_image_scope', 'proposed_research_type')
    for r in rows:
        p = policies[r['primary_policy_cluster']]
        assert r['recommended_policy'] == p['recommended_policy'] in RECOMMENDATIONS
        assert r['provisional_outcome'] in OUTCOMES
        assert r['uncertainty_cause'] in CAUSES
        assert r['original_status'] == SOURCE_STATUS
        for key in preserved:
            assert r[key] == original[r['candidate_id']][key]
        assert r['original_scope_rationale'] == original[r['candidate_id']]['rationale']
        assert r['original_scope_evidence'] == original[r['candidate_id']]['scope_evidence']
        for flag in ('requires_user_decision', 'requires_paper_specific_review'):
            assert r[flag] in ('true', 'false')
        user = r['requires_user_decision'] == 'true'
        evidence = r['requires_paper_specific_review'] == 'true'
        assert user == bool(p['user_question'])
        assert user == (r['uncertainty_cause'] == 'POLICY_CONFLICT')
        assert user == (r['provisional_outcome'] == 'USER_POLICY_DECISION_REQUIRED')
        if not user:
            assert evidence == (r['uncertainty_cause'] == 'PAPER_SPECIFIC_EVIDENCE')
            assert evidence == (r['provisional_outcome'] == 'PAPER_SPECIFIC_REVIEW')
        assert r['policy_rationale'] and r['current_precedent'] == p['hidden_rule_assessment']
    assert all(2 <= len(p['options']) <= 3 for p in policies.values())
    assert all(p['condition'] and p['included_precedent'] for p in policies.values())


def stats(rows, registry):
    def counts(part):
        c = collections.Counter(r['provisional_outcome'] for r in part)
        return {'paper_count': len(part), **{k: c[k] for k in OUTCOMES},
                'additional_evidence_flags': sum(r['requires_paper_specific_review'] == 'true' for r in part)}
    result = {'total': counts(rows), 'causes': dict(sorted(collections.Counter(r['uncertainty_cause'] for r in rows).items())), 'clusters': {}, 'subgroups': {}}
    for p in registry['policies']:
        result['clusters'][p['cluster_id']] = counts([r for r in rows if r['primary_policy_cluster'] == p['cluster_id']])
    for tag in registry['subgroup_tags']:
        part = [r for r in rows if tag in r['secondary_policy_tags'].split(';')]
        result['subgroups'][tag] = {**counts(part), 'policy_clusters': sorted({r['primary_policy_cluster'] for r in part})}
    return result


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def table(headers, lines):
    return ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |'] + ['| ' + ' | '.join(cell(v) for v in line) + ' |' for line in lines]


def ref_text(ref, excluded=False):
    title = ref['title']
    if excluded:
        return f"**{title}** — `{ref['exclusion_id']}`; reason `{ref['reason']}`; exact note: {ref['review_note']}. Source: [active exclusion registry](../data/curated/paper_exclusions.csv)."
    identity = ref.get('paper_id') or ref.get('doi') or title
    labels = '; '.join(f"{k}={','.join(ref.get(k, []))}" for k in ('tasks', 'image_scopes', 'research_types'))
    return f"**{title}** — `{identity}`; {labels}. Source: [current public corpus](../web/data/public_preview_papers.json)."


def render(rows, registry):
    validate(rows, registry)
    s = stats(rows, registry)
    t = s['total']
    lines = ['# Tier 2 scope-policy review — September 2026', '',
             'Policy proposal only. No recommendation is an approved inclusion/exclusion decision. No paper, audit status, taxonomy or public output is changed by this report.', '',
             'Generated from the [215-row reviewed policy CSV](../data/manual/systematic_tier2_scope_policy_clusters_2026_09.csv) and [11-policy canonical registry](../data/manual/systematic_tier2_scope_policies_2026_09.json). Counts are derived, never duplicated in the manual policy registry.', '',
             '## Population and method', '',
             'The [frozen inventory](../data/processed/systematic_tier2_policy_2026_09/inventory.json) preserves every original audit field for exactly 215 rows selected by `final_status == CANDIDATE_ADD_NEEDS_SCOPE_REVIEW`. Selection reads other status values only to exclude them; Tier 1 and Tier 3 evidence is not classified. No broad search or new primary-source adjudication was performed. Cached abstracts, partial summaries and original scope evidence support routing, not final admission.', '',
             'Assignments were reviewed by contribution, endpoint, mechanism and evaluation unit, rather than generated from title keywords. For example, STD-FD concerns diffusion steps rather than video; sequential face edits need not be video; a diffusion segmentation backbone does not establish generative input manipulations; Guard Me If You Know Me is a detector, whereas NullSwap is prevention. Every row has one primary cluster and optional overlapping descriptive tags.', '',
             'The primary uncertainty causes are disjoint: `POLICY_CONFLICT` means an unresolved scope rule is the first blocker; `CURRENT_POLICY_APPLIES` means the cached evidence supports provisional application of an existing explicit or inferred rule; `PAPER_SPECIFIC_EVIDENCE` means a clear rule must be tested against missing evaluation details. The CSV also preserves the earlier request vocabulary in `initial_request_category`.', '',
             'The four provisional outcomes are mutually exclusive. A policy-conflict row is never counted as likely included/excluded. Additional evidence flags may coexist with user-policy conflicts: approving a rule does not verify the paper. When generative coverage is unknown, establish that fact first; if the result is classical-only, the separate TRADITIONAL policy conflict becomes relevant.', '',
             '### Global provisional outcomes', '']
    lines += table(['Outcome', 'Papers'], [(k, t[k]) for k in OUTCOMES] + [('TOTAL', t['paper_count'])])
    lines += ['', f"Uncertainty causes: {s['causes']['CURRENT_POLICY_APPLIES']} current-policy applications; {s['causes']['PAPER_SPECIFIC_EVIDENCE']} paper-specific evidence checks; {s['causes']['POLICY_CONFLICT']} policy conflicts. There are {t['additional_evidence_flags']} paper-specific-review flags in all, including {t['additional_evidence_flags'] - t['PAPER_SPECIFIC_REVIEW']} within the user-policy group. These flags are not a fifth outcome.", '', '## Primary policy clusters', '']
    lines += table(['Cluster', 'Papers', 'Boundary', 'Recommendation', 'Likely include', 'Likely exclude', 'Evidence', 'User'], [
        (p['cluster_id']+' — '+p['cluster_name'], s['clusters'][p['cluster_id']]['paper_count'], p['conceptual_boundary'], p['recommended_policy'], *[s['clusters'][p['cluster_id']][k] for k in OUTCOMES]) for p in registry['policies']])
    lines += ['', '## Decisions requiring user input', '',
              'Only three new decisions are warranted by the inspected precedent. Ranking uses direct affected population, recurring scope ambiguity, conceptual importance and expansion risk. The other eight clusters use existing explicit or defensibly inferred rules; no extra questions are manufactured to reach a target of five to ten.', '']
    for p in sorted([p for p in registry['policies'] if p['user_question']], key=lambda p: p['decision_rank']):
        n = s['clusters'][p['cluster_id']]['paper_count']
        lines += [f"### {p['decision_rank']}. {p['cluster_name']} — {n} directly affected", '', p['user_question'], '',
                  '**Recommended answer: Yes**, subject to this exact condition: '+p['condition'], '',
                  '**If Yes:** '+p['yes_consequence'], '', '**If No:** '+p['no_consequence'], '',
                  '**Main included precedent:** '+p['included_precedent'][0]['title']+'.', '',
                  '**Main excluded precedent:** '+('; '.join(r['title'] for r in p['excluded_precedent']) if p['cluster_id'] != 'TRADITIONAL' else 'No matching explicit classical-only exclusion was found; the conflict is between stated generated-image scope and two included classical-only records')+'.', '',
                  f"This resolves a reusable boundary for up to {n} primary-cluster candidates, not {n} guaranteed admissions. Other clusters may carry a secondary dependency, so these direct counts are conservative and non-overlapping.", '']
    lines += ['## Precedent checks and policy options', '',
              'The inspected current corpus contains 636 papers. Taxonomy comes from [paper_taxonomy.py](../scripts/paper_taxonomy.py) and the [taxonomy registry](../data/curated/paper_taxonomy.csv). [AGENTS.md](../AGENTS.md) establishes the generated-image boundary. The [README](../README.md) automatic candidate filter is a discovery rule, not an infallible description of all manual curation. Current Tier 1 reconciliation is consulted read-only for existing generative editing and scientific-image precedent.', '',
              'The ordinary watermark conflict is reconciled at moderate confidence by contribution type, not by banning all active provenance or pretending embedding papers lack decoders. Face-only and classical-only practice cannot be reconciled fully by task, modality or method-versus-analysis distinctions. Hybrid manipulation forensics is an unresolved extension between embedding and independent forensic evaluation. Opaque exclusion notes such as “ML” do not prove the curator’s intent; the report distinguishes observed practice from explicit rationale.', '',
              'Each option below affects at most the cluster population shown. These are candidates whose policy treatment would be reconsidered, not estimated additions; evidence gaps and later identity/exclusion checks can reduce the realized impact. Recommendation selection follows conceptual fit and precedent, not candidate volume.', '']
    for p in registry['policies']:
        part = [r for r in rows if r['primary_policy_cluster'] == p['cluster_id']]
        c = s['clusters'][p['cluster_id']]
        lines += [f"<a id=\"policy-{p['cluster_id']}\"></a>", '', f"### {p['cluster_id']} — {p['cluster_name']} ({len(part)} papers)", '',
                  '**Boundary:** '+p['conceptual_boundary'], '', '**Precedent assessment:** '+p['hidden_rule_assessment'], '',
                  '**Included precedents:**', '']
        lines += ['- '+ref_text(r) for r in p['included_precedent']]
        lines += ['', '**Excluded or contrasting precedents:**', '']
        lines += ['- '+ref_text(r, True) for r in p['excluded_precedent']]
        if p.get('precedent_detail'):
            lines += ['', '**Mechanism check:** ' + p['precedent_detail'], '', 'Cached source abstracts: ' + ', '.join(f'[{Path(path).name}](../{path})' for path in p['precedent_cache_paths']) + '.', '']
        lines += ['', '**Representative Tier 2 candidates:**', '']
        # Prefer distinct policy/outcome/tag patterns, but never infer a scope decision.
        reps = []
        for r in part:
            if not reps or r['provisional_outcome'] not in {a['provisional_outcome'] for a in reps}:
                reps.append(r)
        for r in part:
            if len(reps) >= 3:
                break
            if r not in reps:
                reps.append(r)
        lines += [f"- {r['canonical_title']} (`{r['candidate_id']}`) — {r['policy_rationale']} [Original primary link]({r['primary_evidence_url']})." for r in reps]
        lines += ['', f"**Recommendation:** `{p['recommended_policy']}`. {p['condition']}", '',
                  f"**Confidence:** {p['policy_confidence']}. **Future recurrence:** {p['future_recurrence']}.", '',
                  '**Over-inclusion risk:** '+p['over_inclusion_risk'], '', '**Under-inclusion risk:** '+p['under_inclusion_risk'], '',
                  f"**Provisional counts:** include {c['LIKELY_INCLUDE']}; exclude {c['LIKELY_EXCLUDE']}; evidence review {c['PAPER_SPECIFIC_REVIEW']}; user decision {c['USER_POLICY_DECISION_REQUIRED']}. Additional paper-specific flags: {c['additional_evidence_flags']}.", '']
        for option in p['options']:
            lines += ['**'+option['label']+'**', '',
                      '- Rationale: '+option['rationale'], '- Taxonomy fit: '+option['taxonomy_fit'],
                      '- Current-corpus impact: '+option['precedent_impact'],
                      f"- Approximate Tier 2 population affected: up to {len(part)}; no existing record is changed.",
                      '- Future literature: '+option['future_implications'], '- Scope-creep risk: '+option['scope_creep'], '']
    lines += ['## Subgroup crosswalks', '',
              'These tags are descriptive and can overlap; only primary-cluster/outcome tables sum to 215. Counts of zero mean no case was established from this inventory, not a claim about the literature. “Embedding-centric” includes a paired decoder; no paper was asserted to be strictly embedding-only without recovery. Cryptographic tags include non-image/general theory candidates and must not be read as three image-credential systems.', '',
              'Each subgroup inherits the exact condition, included/excluded precedents and hidden-rule assessment from the listed policy sections. A mixed subgroup cannot be reduced to one yes/no: its user count shows only the unresolved primary-policy subset.', '']
    families = [('Watermark, provenance and security', ['watermark_embedding_centric'] + registry['subgroup_tags'][:10] + ['credentials_metadata', 'copyright_or_model_ownership', 'generation_prevention']),
                ('Face and modality crossover', ['still_image_face_detection','image_level_deepfake_localization','video_only_deepfake','frame_method_video_system_evaluation','mixed_image_video','identity_authenticity_without_detection','facial_generative_editing','face_evaluation_unit_unverified','text_only']),
                ('Manipulation, endpoint and contribution type', registry['subgroup_tags'][18:])]
    seen = set()
    for name, tags in families:
        tags = [tag for tag in tags if tag in s['subgroups'] and tag not in seen]
        seen.update(tags)
        lines += ['### '+name, '']
        lines += table(['Subgroup', 'Tagged papers', 'Applicable policies / precedents', 'User input', 'Evidence flags'], [
            (tag, s['subgroups'][tag]['paper_count'], ', '.join(f'[{g}](#policy-{g})' for g in s['subgroups'][tag]['policy_clusters']) or 'No established candidate; no new policy question', s['subgroups'][tag]['USER_POLICY_DECISION_REQUIRED'], s['subgroups'][tag]['additional_evidence_flags']) for tag in tags])
        lines += ['']
    missing_tags = [tag for tag in registry['subgroup_tags'] if tag not in seen]
    if missing_tags:
        lines += table(['Additional subgroup', 'Tagged papers', 'Policies', 'User input'], [(tag,s['subgroups'][tag]['paper_count'], ', '.join(s['subgroups'][tag]['policy_clusters']),s['subgroups'][tag]['USER_POLICY_DECISION_REQUIRED']) for tag in missing_tags]) + ['']
    lines += ['### Boundaries not promoted to separate policy questions', '',
              '- Face candidates without an established still-image, spatial-localization, mixed-modality or frame-system subgroup retain an explicit evaluation-unit evidence flag. They remain in the policy-conflict outcome because settling that rule is the first blocker; they are not silently assumed to satisfy the proposed image condition.',
              '- Multimodality and scientific imagery are secondary tags. THEMIS still needs an actual generative-image forensic endpoint checked; specialized domain is not a reason to exclude it. MLLM reasoning is not automatically misinformation-only.',
              '- Passive attribution includes model/source and training-image provenance. Copyright motivation alone is insufficient to exclude MCID; its legal labels versus actual visual-source recovery need paper-specific checking.',
              '- No quality/aesthetic-only cluster or general human-perception policy question is created from the selected candidates. HICOM has a human-study component but a video/image evaluation question. Existing Organic or Diffused and perception benchmarks show that controlled forensic discrimination can qualify without a new detector.',
              '- Analysis type is not automatic admission. Current context-only exceptions include TWIGMA and the AI-label user study, while a GPT-Image-2 Twitter collection and platform-engagement studies are excluded for lacking forensic evaluation. These historical exceptions do not establish a general governance-infrastructure rule; the selected Position paper concerns foundation-model data governance rather than an evaluated image-forensic task.',
              '- Training-data fingerprints used to teach a passive detector (FingerprintNet) differ from signatures injected into released model outputs (Artificial fingerprinting). Sequential image edits and diffusion timesteps differ from temporal video intervals.',
              '- A candidate title/version may match an existing exclusion (Forensics Adapter). This is a flagged future identity check, not a restoration or modification of the original 215-row population.', '',
              '## Integrity and reproducibility', '',
              'The [pre-task SHA-256 baseline](../data/processed/systematic_tier2_policy_2026_09/baseline_sha256.json) covers pre-existing nonignored repository files outside this new Tier 2 layer. It protects the current 636-paper corpus, taxonomy, exclusions, institutions, affiliations, locations, hierarchy, public JSON, frontend, Tier 1 artifacts and historical audit. Hash verification and validation results are recorded separately so this policy report remains deterministic.', '',
              'Reproduce from the repository root:', '', '```sh',
              'python3 scripts/prepare_systematic_tier2_policy.py',
              'python3 scripts/report_systematic_tier2_policy.py --check --verify-integrity',
              'python3 scripts/report_systematic_tier2_policy.py --output-dir /tmp/tier2-policy-reproduction',
              '/usr/bin/python3 -m pytest -q tests/test_systematic_tier2_policy.py',
              'git diff --check', '```', '',
              '`--output-dir` regenerates only the derived report and summary in a separate directory. `--write` explicitly writes the derived report and summary to their canonical paths. Neither mode writes either manual registry or any corpus file. Manual policy recommendations are never recomputed from keywords.', '',
              'See [validation results](../data/processed/systematic_tier2_policy_2026_09/validation.json) and [full-suite output](../data/processed/systematic_tier2_policy_2026_09/full_suite.txt). Approval and actual reconciliation are future layers. No policy is applied here.', '']
    return '\n'.join(lines), json.dumps(s, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def integrity():
    baseline = json.loads((PROCESSED / 'baseline_sha256.json').read_text())
    changed = [p for p, digest in baseline.items() if not (ROOT / p).is_file() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != digest]
    successor = set()
    if (ROOT / 'data/processed/systematic_tier2_include_2026_09/insertion.json').exists():
        successor = {
            'data/curated/author_institution_mappings.csv', 'data/curated/institution_location_review.csv',
            'data/curated/institutions.csv', 'data/curated/paper_taxonomy.csv', 'data/curated/papers.csv',
            'docs/key_paper_coverage_report.md', 'web/data/public_preview_map_data.json',
            'web/data/public_preview_papers.json',
            'scripts/report_systematic_tier1.py', 'tests/baseline_expectations.py',
            'tests/test_manual_location_audit_20260827.py',
            'tests/test_paper_metadata_consistency_audit.py',
            'tests/test_paper_taxonomy_migration.py', 'tests/test_repository_baseline.py',
            'tests/test_frontend_published_only_filter.py',
        }
    unexplained = [p for p in changed if p not in successor]
    return {'protected_files_checked': len(baseline), 'changed_count': len(unexplained),
            'changed_paths': unexplained, 'authorized_successor_changes': sorted(set(changed) & successor)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--verify-integrity', action='store_true')
    args = parser.parse_args()
    report, summary = render(*load_inputs())
    if args.write:
        REPORT.write_text(report)
        (PROCESSED / 'summary.json').write_text(summary)
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / REPORT.name).write_text(report)
        (args.output_dir / 'summary.json').write_text(summary)
    if args.check or not (args.write or args.output_dir):
        assert REPORT.read_text() == report, 'Report is stale'
        assert (PROCESSED / 'summary.json').read_text() == summary, 'Summary is stale'
    if args.verify_integrity:
        result = integrity()
        print(json.dumps(result, sort_keys=True))
        assert result['changed_count'] == 0, 'Protected pre-task files changed'
    print('215 candidates; 11 policies; deterministic report and counts verified.')


if __name__ == '__main__':
    main()

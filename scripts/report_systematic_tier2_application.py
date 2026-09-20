#!/usr/bin/env python3
"""Render approved narrowed-policy queues and audit-only legacy diagnostics.

The two reviewed manual CSVs are read-only inputs. No classification, taxonomy,
corpus decision or original audit status is written by this script.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed/systematic_tier2_application_2026_09'
APPLICATION = ROOT / 'data/manual/systematic_tier2_policy_application_2026_09.csv'
LEGACY = ROOT / 'data/manual/legacy_scope_review_candidates_2026_09.csv'
PREVIOUS = ROOT / 'data/manual/systematic_tier2_scope_policy_clusters_2026_09.csv'
INVENTORY = ROOT / 'data/processed/systematic_tier2_policy_2026_09/inventory.json'
ORIGINAL = ROOT / 'data/manual/systematic_literature_completeness_candidates_2026_09.csv'
# The application report is a historical snapshot. Later authorized curation
# must not make its 636-paper diagnostics depend on the current export.
PUBLIC = ROOT / 'data/processed/systematic_tier2_include_2026_09/baseline/web/data/public_preview_papers.json'
REPORT = ROOT / 'docs/systematic_tier2_policy_application_2026_09.md'
OUTCOMES = ('POLICY_INCLUDE', 'POLICY_EXCLUDE', 'PAPER_SPECIFIC_EVIDENCE_REQUIRED')
REASONS = ('WATERMARK_ACTIVE_PROVENANCE', 'PURE_DEEPFAKE_FACE_ONLY', 'VIDEO_ONLY_DEEPFAKE', 'CLASSICAL_MANIPULATION', 'PROTECTION_GOVERNANCE', 'OTHER')
LEGACY_CATEGORIES = ('LEGACY_SCOPE_REVIEW_WATERMARK', 'LEGACY_SCOPE_REVIEW_DEEPFAKE', 'LEGACY_SCOPE_REVIEW_CLASSICAL')
CLUSTERS = ('EMBED', 'VERIFY', 'WM_EVAL', 'HYBRID', 'PROTECT', 'FACE', 'MODALITY', 'TRADITIONAL', 'IMAGE', 'ATTRIBUTION', 'EVASION')
QUEUES = dict(zip(OUTCOMES, ('queue_a_policy_include.csv', 'queue_b_policy_exclude.csv', 'queue_c_evidence_required.csv')))
INCLUDE_PRIORITY_HIGH = {
    'audit:032ad7d6b71836a2', 'audit:07194f58b4540acc', 'audit:2ec9b9251586d3bb',
    'audit:3e3ef129a9a7d54a', 'audit:5413d2706f713d11', 'audit:5a3a0232762bb033',
    'audit:6bf3721fdb65fc44', 'audit:80dc647f134b129b', 'audit:96a08f643278af6c',
    'audit:bb665e920e4e26be',
}
EVIDENCE_PRIORITY_HIGH = {
    'audit:07f15e7e8a78398a', 'audit:0b72dded38f87a65', 'audit:0dc47031ed0bccc5',
    'audit:202541800aaec592', 'audit:46984fabc086b053', 'audit:6880617d9c9040d4',
    'audit:854cc239481946ba', 'audit:cf16307ced603a1d', 'audit:ea0d7f9972aa1b1c',
    'audit:f12e2be8d1320201', 'audit:f293e205186b3f59', 'audit:f55fbb498b42444f',
}


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def csv_text(rows, fields):
    handle = io.StringIO(newline='')
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue()


def record_hash(record):
    return hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def inputs():
    return read_csv(APPLICATION), read_csv(LEGACY)


def normalized_legacy(row):
    confidence = {
        'high as a review candidate': 'HIGH',
        'medium; possible exception': 'MEDIUM',
        'low; diagnostic only': 'LOW',
    }[row['confidence']]
    basis = row['diagnostic_basis']
    if basis == 'face_or_video_evaluation_evidence':
        disposition = 'LIKELY_PURE_DEEPFAKE'
    elif basis == 'deepfake_only_taxonomy_scope_unverified':
        disposition = 'METADATA_INSUFFICIENT'
    elif basis == 'face_primary_with_possible_broader_exception':
        disposition = 'POSSIBLE_BROADER_SYNTHETIC_IMAGE_WORK'
    else:
        disposition = 'LIKELY_SCOPE_DRIFT'
    return {**row, 'normalized_confidence': confidence, 'diagnostic_disposition': disposition}


def decision_queues(rows):
    inventory = {r['candidate_id']: r for r in json.loads(INVENTORY.read_text())}
    queue_a = []
    queue_c = []
    for row in rows:
        source = inventory[row['candidate_id']]
        if row['policy_outcome'] == 'POLICY_INCLUDE':
            queue_a.append({
                'candidate_id': row['candidate_id'],
                'title': row['canonical_title'],
                'year': row['year'],
                'venue': row['venue'],
                'cluster': row['primary_policy_cluster'],
                'qualifying_synthetic_image_contribution': row['policy_rationale'],
                'proposed_forensic_task': source['proposed_forensic_task'],
                'proposed_image_scope': source['proposed_image_scope'],
                'proposed_research_type': source['proposed_research_type'],
                'saved_primary_evidence_url': row['primary_evidence_url'],
                'saved_evidence': row['scope_evidence'],
                'reconciliation_priority': 'HIGH' if row['candidate_id'] in INCLUDE_PRIORITY_HIGH else 'NORMAL',
            })
        elif row['policy_outcome'] == 'PAPER_SPECIFIC_EVIDENCE_REQUIRED':
            if row['primary_policy_cluster'] == 'FACE':
                negative = 'POLICY_EXCLUDE / PURE_DEEPFAKE_FACE_ONLY'
            elif row['primary_policy_cluster'] == 'VERIFY':
                negative = 'POLICY_EXCLUDE / WATERMARK_ACTIVE_PROVENANCE'
            elif row['primary_policy_cluster'] == 'ATTRIBUTION':
                negative = 'POLICY_EXCLUDE / WATERMARK_ACTIVE_PROVENANCE or PURE_DEEPFAKE_FACE_ONLY, as the source shows'
            else:
                negative = 'POLICY_EXCLUDE / CLASSICAL_MANIPULATION or OTHER, as the source shows'
            queue_c.append({
                'candidate_id': row['candidate_id'],
                'title': row['canonical_title'],
                'year': row['year'],
                'venue': row['venue'],
                'cluster': row['primary_policy_cluster'],
                'exact_unresolved_question': row['evidence_review_question'],
                'evidence_already_available': row['scope_evidence'],
                'exact_additional_evidence_needed': 'Primary-paper method, dataset, and per-subset evaluation evidence that directly answers: ' + row['evidence_review_question'],
                'likely_outcome_if_confirmed': 'POLICY_INCLUDE, followed by identity/exclusion reconciliation and primary-source curation',
                'likely_outcome_if_not_confirmed': negative,
                'evidence_review_priority': 'HIGH' if row['candidate_id'] in EVIDENCE_PRIORITY_HIGH else 'NORMAL',
                'saved_primary_evidence_url': row['primary_evidence_url'],
            })
    return queue_a, queue_c


def validate(rows, legacy):
    inventory = json.loads(INVENTORY.read_text())
    selected = sorted((r for r in read_csv(ORIGINAL) if r['final_status'] == 'CANDIDATE_ADD_NEEDS_SCOPE_REVIEW'), key=lambda r: r['candidate_id'])
    assert inventory == selected, 'Historical inventory/evidence changed'
    previous = {r['candidate_id']: r for r in read_csv(PREVIOUS)}
    ids = [r['candidate_id'] for r in rows]
    assert len(ids) == len(set(ids)) == 215
    assert ids == sorted(ids)
    assert set(ids) == set(previous) == {r['candidate_id'] for r in selected}
    assert {r['primary_policy_cluster'] for r in rows} == set(CLUSTERS)
    for r in rows:
        prior = previous[r['candidate_id']]
        assert r['primary_policy_cluster'] == prior['primary_policy_cluster']
        assert r['previous_provisional_outcome'] == prior['provisional_outcome']
        assert r['original_audit_status'] == 'CANDIDATE_ADD_NEEDS_SCOPE_REVIEW'
        for key in ('canonical_title', 'year', 'venue', 'doi', 'arxiv_id', 'openalex_id', 'primary_evidence_url'):
            assert r[key] == prior[key]
        assert r['policy_outcome'] in OUTCOMES
        assert r['manual_review'] in ('true', 'false')
        assert r['independent_passive_exception_verified'] in ('true', 'false')
        evidence = r['policy_outcome'] == 'PAPER_SPECIFIC_EVIDENCE_REQUIRED'
        excluded = r['policy_outcome'] == 'POLICY_EXCLUDE'
        assert evidence == bool(r['evidence_review_question']) == (r['manual_review'] == 'true')
        if evidence:
            assert '?' in r['evidence_review_question'] and len(r['evidence_review_question']) > 65
            assert 'scope unclear' not in r['evidence_review_question'].lower()
        assert excluded == bool(r['primary_exclusion_reason'])
        if excluded:
            assert r['primary_exclusion_reason'] in REASONS
        if r['primary_policy_cluster'] in {'EMBED', 'VERIFY', 'WM_EVAL', 'HYBRID'} and r['policy_outcome'] == 'POLICY_INCLUDE':
            assert r['independent_passive_exception_verified'] == 'true'
            assert r['mechanism_assessment'] == 'PASSIVE'
        if r['mechanism_assessment'] in {'PROVENANCE_DEPENDENT', 'FACE_FORENSICS', 'VIDEO_OR_AUDIOVISUAL', 'CLASSICAL_ONLY', 'PROTECTION_ONLY', 'NONIMAGE_TEMPORAL'}:
            assert excluded
        assert r['policy_rationale'] and r['scope_evidence']
    public = json.loads(PUBLIC.read_text())['records']
    assert len(public) == 636
    corpus_hashes = {record_hash(r): r for r in public}
    assert len({r['legacy_review_id'] for r in legacy}) == len(legacy)
    assert len({r['paper_identity'] for r in legacy}) == len(legacy)
    for r in legacy:
        assert r['legacy_scope_category'] in LEGACY_CATEGORIES
        assert r['diagnostic_only'] == 'true' and r['corpus_action'] == 'NONE'
        source = corpus_hashes[r['source_record_sha256']]
        assert r['canonical_title'] == source['title']
        assert r['current_image_scopes'] == ';'.join(source['image_scopes'])
        assert r['current_tasks'] == ';'.join(source['tasks'])
        assert r['current_abstract'] == (source.get('abstract') or '')
        assert r['confidence'] in {'high as a review candidate', 'medium; possible exception', 'low; diagnostic only'}
    ledger = json.loads((OUT / 'legacy_screening_636.json').read_text())
    assert len(ledger) == 636 and {r['corpus_index'] for r in ledger} == set(range(636))
    for row in ledger:
        assert row['source_record_sha256'] == record_hash(public[row['corpus_index']])
    assert {r['source_record_sha256'] for r in ledger if r['diagnostic_category']} == {r['source_record_sha256'] for r in legacy}


def summary(rows, legacy):
    total = collections.Counter(r['policy_outcome'] for r in rows)
    clusters = {}
    for cluster in CLUSTERS:
        part = [r for r in rows if r['primary_policy_cluster'] == cluster]
        counts = collections.Counter(r['policy_outcome'] for r in part)
        clusters[cluster] = {'total': len(part), **{k: counts[k] for k in OUTCOMES}}
    reasons = collections.Counter(r['primary_exclusion_reason'] for r in rows if r['policy_outcome'] == 'POLICY_EXCLUDE')
    legacy_counts = collections.Counter(r['legacy_scope_category'] for r in legacy)
    normalized = [normalized_legacy(r) for r in legacy]
    confidence = collections.Counter(r['normalized_confidence'] for r in normalized)
    disposition = collections.Counter(r['diagnostic_disposition'] for r in normalized)
    return {'total': len(rows), 'outcomes': {k: total[k] for k in OUTCOMES}, 'clusters': clusters,
            'exclusion_reasons': {k: reasons[k] for k in REASONS},
            'legacy': {k: legacy_counts[k] for k in LEGACY_CATEGORIES},
            'legacy_confidence': {k: confidence[k] for k in ('HIGH', 'MEDIUM', 'LOW')},
            'legacy_disposition': dict(sorted(disposition.items())),
            'legacy_diagnostic_basis': dict(sorted(collections.Counter(r['diagnostic_basis'] for r in legacy).items())),
            'user_policy_unresolved': 0, 'corpus_decisions_applied': 0}


def table(headers, lines):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    return ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |'] + ['| ' + ' | '.join(cell(v) for v in line) + ' |' for line in lines]


def render(rows, legacy):
    validate(rows, legacy)
    s = summary(rows, legacy)
    queue_a, queue_c = decision_queues(rows)
    lines = ['# Tier 2 application of the approved narrowed scope — September 2026', '',
             'The user-approved policy supersedes the earlier precedent-based proposal for NEW candidates. This is a policy-eligibility layer only: POLICY_INCLUDE does not add a paper, POLICY_EXCLUDE does not enter an exclusion registry, and legacy flags do not authorize removal.', '',
             'Sources: [exact approved request](../data/processed/systematic_tier2_application_2026_09/approved_policy_request.txt), [reviewed application CSV](../data/manual/systematic_tier2_policy_application_2026_09.csv), [audit-only legacy CSV](../data/manual/legacy_scope_review_candidates_2026_09.csv), and [unchanged prior Tier 2 inventory](../data/processed/systematic_tier2_policy_2026_09/inventory.json). No new literature search was conducted.', '',
             '## Applied rules', '',
             '- **P1 — Active mechanisms and protection:** exclude watermark construction, detection, verification, robustness, removal, injected fingerprints, generator-controlled forensic signatures, credentials/C2PA, content authentication and ownership/copyright protection. Keyless or zero-watermark authentication is not automatically passive generator-trace analysis.',
             '- **P1_EXCEPTION:** only a separable, independently evaluated passive synthetic-image method that does not require the active mechanism can qualify. No such exception is asserted as verified in this pass. Abductive Corroboration remains an evidence check for watermark-free results.',
             '- **P2 — Pure deepfake:** face swapping, reenactment, facial/identity manipulation and video/frame deepfake work do not qualify alone. Entire-face GAN/diffusion synthesis or facial localization does not establish the required broader contribution.',
             '- **P3 — Substantive synthetic-image forensics:** general fully generated-image detection and diffusion/generative inpainting, editing or partial-region forensics remain eligible. Manipulated regions are not an exclusion reason.',
             '- **P4 — Classical-only:** conventional copy-move, splicing, compositing and document edits are excluded unless a substantive generative component is independently evaluated. A diffusion detector backbone is not that evidence.',
             '- **P5 — Passive attribution:** inference from naturally occurring image-generation traces to generators/models/sources remains core. Deliberately injected signatures and generic model-ownership tests do not qualify.',
             '- **P6 — Passive-detector robustness/evasion:** analysis or attacks against in-scope AI-generated-image detectors may qualify. Watermark and otherwise out-of-scope face/video detector attacks do not.',
             '- **P7 — Multimodal:** require a substantive independently evaluated synthetic-image forensic component; frame extraction and text-image misinformation consistency alone are insufficient.',
             '- **P8 — Specialized domains:** scientific, biomedical and other domains qualify on their synthetic-image forensic task; specialization alone is not exclusionary.', '',
             '## Revised Tier 2 result', '']
    lines += table(['Outcome', 'Papers'], [(k, s['outcomes'][k]) for k in OUTCOMES] + [('TOTAL', s['total'])])
    lines += ['', '**Remaining user-policy decisions: 0.** Evidence questions concern the actual paper, not conflicting historical decisions.', '',
              'The application preserves the exact 215 candidate IDs and the original 11 primary clusters. The historical audit and prior policy proposal remain unchanged. Saved titles/opening abstracts can establish an unambiguous central task without completing bibliographic or experimental curation; missing details become Queue C only when they affect the substantive scope boundary.', '',
              '### By original policy cluster', '']
    lines += table(['Cluster', 'Papers', 'POLICY_INCLUDE', 'POLICY_EXCLUDE', 'PAPER_SPECIFIC_EVIDENCE_REQUIRED'], [(g,s['clusters'][g]['total'],*[s['clusters'][g][k] for k in OUTCOMES]) for g in CLUSTERS])
    lines += ['', '### Exclusion reasons', '',
              'Each excluded candidate receives one primary reason, so these counts sum to the exclusion queue. Where boundaries overlap, a watermark-primary mechanism takes precedence, including text watermarks and temporal watermark recovery. Generic temporal forgery localization without a specific deepfake/image task is OTHER. Secondary context remains in each rationale; reasons are not added together twice.', '']
    lines += table(['Primary reason', 'Papers'], [(k,s['exclusion_reasons'][k]) for k in REASONS])
    lines += ['', '## Queue A — POLICY_INCLUDE', '',
              f"{s['outcomes']['POLICY_INCLUDE']} papers. These pass the scope gate only; a later task must handle identity/exclusion reconciliation, metadata, publication status and primary-source curation before corpus addition.", '',
              '[Machine-readable Queue A](../data/processed/systematic_tier2_application_2026_09/queue_a_policy_include.csv)', '']
    for r in rows:
        if r['policy_outcome'] == 'POLICY_INCLUDE':
            lines += [f"- **{r['canonical_title']}** (`{r['candidate_id']}`) — {r['policy_rationale']} [Saved primary link]({r['primary_evidence_url']})."]
    lines += ['', '## Queue B — POLICY_EXCLUDE', '',
              f"{s['outcomes']['POLICY_EXCLUDE']} papers. Every title, primary reason and supporting rationale is retained in [Queue B](../data/processed/systematic_tier2_application_2026_09/queue_b_policy_exclude.csv); none has been written to the authoritative exclusion registry.", '',
              '## Queue C — PAPER_SPECIFIC_EVIDENCE_REQUIRED', '',
              f"{s['outcomes']['PAPER_SPECIFIC_EVIDENCE_REQUIRED']} papers. [Machine-readable Queue C](../data/processed/systematic_tier2_application_2026_09/queue_c_evidence_required.csv). A clear face-only or watermark-primary contribution is not held here merely because older similar papers were included.", '']
    lines += table(['Priority', 'Paper / candidate ID', 'Exact question'], [(r['evidence_review_priority'], f"{r['title']} (`{r['candidate_id']}`)", r['exact_unresolved_question']) for r in queue_c])
    lines += ['', '## Important boundary applications', '',
              '- Watermark verification and robustness no longer inherit eligibility from ImageDetectBench or WEvade. FARI, ROAR and keyless watermark detection are excluded. Abductive Corroboration is held only to check an explicitly separable watermark-free contribution.',
              '- FFIM and AdvMark improve passive detection through generator control or injected marks; downstream detector scores alone do not make their contribution independent of the active mechanism.',
              '- VLForgery, VIPGuard and specular-reflection face detection remain pure face-forensics applications despite using diffusion, full-face synthesis, localization or source attribution. A Rich Knowledge Space is held because its saved abstract explicitly also claims an AIGC benchmark, whose broader coverage must be checked.',
              '- STD-FD uses temporal diffusion-process evidence, not video. IFA-Net’s complete saved abstract explicitly reports four diffusion-inpainting benchmarks; that supports inclusion. ForgDiffuser instead generates segmentation masks, leaving the origin of the input tampering unverified.',
              '- Naturally occurring image-source fingerprints in RPA and passive detector attacks in FPBA/PolyJuice differ from injected training signatures in Artificial fingerprinting. A detector-training prompt/prior is not automatically a released provenance signal.',
              '- TGIF2, ImageTrust and Dual-scale model collaborative reasoning have an unambiguous central generative-image forensic task in the saved title/opening. Their abbreviated abstracts remain curation limitations, not unresolved policy choices.', '',
              '## Legacy scope diagnostic — no changes to 636 existing records', '',
              'This is a current-metadata/abstract screening list for a later audit, not an approved exclusion list. A [636-row screening ledger](../data/processed/systematic_tier2_application_2026_09/legacy_screening_636.json) records coverage and source-record hashes. Every flagged row keeps its original taxonomy, identity, abstract and review rationale. Unflagged records are not certified compliant with every narrowed rule.', '']
    lines += table(['Potential legacy category', 'Records'], [(k,s['legacy'][k]) for k in LEGACY_CATEGORIES])
    lines += ['', '### Confidence and safeguards', '']
    lines += table(['Exact confidence', 'Records'], [(k, s['legacy_confidence'][k]) for k in ('HIGH', 'MEDIUM', 'LOW')])
    lines += ['', 'The normalized diagnostic distinguishes likely pure-deepfake scope drift from metadata-insufficient records and a possible broader synthetic-image contribution. The broader-work record is not counted as a likely scope violation.', '']
    lines += table(['Diagnostic disposition', 'Records'], list(s['legacy_disposition'].items()))
    lines += ['', 'The source CSV retains the original reviewed wording; the normalized exact confidence and disposition fields are in [the derived legacy diagnostic](../data/processed/systematic_tier2_application_2026_09/legacy_scope_diagnostic.csv).', '']
    lines += table(['Diagnostic basis', 'Records'], list(s['legacy_diagnostic_basis'].items()))
    lines += ['',
              f"The {s['legacy']['LEGACY_SCOPE_REVIEW_DEEPFAKE']} deepfake flags comprise {s['legacy_diagnostic_basis'].get('face_or_video_evaluation_evidence', 0)} supported by face/video evidence, {s['legacy_diagnostic_basis'].get('deepfake_only_taxonomy_scope_unverified', 0)} low-confidence deepfake-only taxonomy records whose broader component is not settled by saved evidence, and {s['legacy_diagnostic_basis'].get('face_primary_with_possible_broader_exception', 0)} possible broader-contribution exception (Gram-Net). These are **not confirmed pure-deepfake exclusions**. The low-confidence subgroup can contain false positives and must receive evidence review before any removal proposal.", '',
              'The screen checks explicit broader counterevidence rather than treating the deepfake taxonomy label as sufficient. Examples not flagged as pure face-only include Forging the Unknown (GenImage plus FaceForensics++), the Multi-Graph Attention method (GenImage/CIFAKE), Faster Than Lies (COCOFake/CIFAKE), OpenFake, and general image-source/robustness studies. Their stored taxonomy is not changed.', '',
              '### Watermark/provenance flags', '']
    lines += [f"- **{r['canonical_title']}** — {r['review_rationale']}" for r in legacy if r['legacy_scope_category']=='LEGACY_SCOPE_REVIEW_WATERMARK']
    lines += ['', '### Classical-only flags', '']
    lines += [f"- **{r['canonical_title']}** — {r['review_rationale']}" for r in legacy if r['legacy_scope_category']=='LEGACY_SCOPE_REVIEW_CLASSICAL']
    lines += ['', 'All deepfake diagnostic titles and evidence/confidence fields are in the [legacy CSV](../data/manual/legacy_scope_review_candidates_2026_09.csv). Watermark-independent visual source retrieval is not flagged merely because provenance or copyright appears in its motivation; EKILA is flagged because it also incorporates the active credential/rights framework, with the separability exception left for later review.', '',
              '## Integrity, tests and reproduction', '',
              'The [new pre-application hash baseline](../data/processed/systematic_tier2_application_2026_09/baseline_sha256.json) protects all pre-existing files, including the completed Tier 2 policy analysis. Neither reviewed manual CSV is written by the report/queue generator. Original systematic-audit statuses are still CANDIDATE_ADD_NEEDS_SCOPE_REVIEW.', '',
              '```sh', 'python3 scripts/report_systematic_tier2_application.py --check --verify-integrity',
              'python3 scripts/report_systematic_tier2_application.py --output-dir /tmp/tier2-application-reproduction',
              '/usr/bin/python3 -m pytest -q tests/test_systematic_tier2_application.py tests/test_systematic_tier2_policy.py', 'git diff --check', '```', '',
              '`--write` explicitly regenerates only the derived Markdown, summary, three queue CSVs and normalized legacy diagnostic. `--output-dir` writes those same outputs to a separate directory. Manual decisions, the exact approved request and the screening ledger remain read-only inputs.', '',
              'See [validation results](../data/processed/systematic_tier2_application_2026_09/validation.json), [reproducibility evidence](../data/processed/systematic_tier2_application_2026_09/reproducibility.json) and [full-suite output](../data/processed/systematic_tier2_application_2026_09/full_suite.txt). No papers are added or removed, no policies are retroactively applied to the corpus, and nothing is committed or pushed.', '']
    artifacts={REPORT.name:'\n'.join(lines), 'summary.json':json.dumps(s,ensure_ascii=False,indent=2,sort_keys=True)+'\n'}
    artifacts[QUEUES['POLICY_INCLUDE']] = csv_text(queue_a, list(queue_a[0]))
    excluded = [r for r in rows if r['policy_outcome'] == 'POLICY_EXCLUDE']
    artifacts[QUEUES['POLICY_EXCLUDE']] = csv_text(excluded, list(rows[0]))
    artifacts[QUEUES['PAPER_SPECIFIC_EVIDENCE_REQUIRED']] = csv_text(queue_c, list(queue_c[0]))
    normalized = [normalized_legacy(r) for r in legacy]
    artifacts['legacy_scope_diagnostic.csv'] = csv_text(normalized, list(normalized[0]))
    return artifacts


def integrity():
    hashes=json.loads((OUT/'baseline_sha256.json').read_text())
    changed=[p for p,h in hashes.items() if not (ROOT/p).is_file() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    successor = set()
    if (ROOT/'data/processed/systematic_tier2_include_2026_09/insertion.json').exists():
        successor = {
            'data/curated/author_institution_mappings.csv', 'data/curated/institution_location_review.csv',
            'data/curated/institutions.csv', 'data/curated/paper_taxonomy.csv', 'data/curated/papers.csv',
            'docs/key_paper_coverage_report.md', 'web/data/public_preview_map_data.json',
            'web/data/public_preview_papers.json', 'scripts/report_systematic_tier2_policy.py',
            'scripts/report_systematic_tier1.py', 'tests/baseline_expectations.py',
            'tests/test_manual_location_audit_20260827.py',
            'tests/test_paper_metadata_consistency_audit.py',
            'tests/test_paper_taxonomy_migration.py', 'tests/test_repository_baseline.py',
            'tests/test_frontend_published_only_filter.py',
        }
    unexplained=[p for p in changed if p not in successor]
    return {'protected_files_checked':len(hashes),'changed_count':len(unexplained),'changed_paths':unexplained,
            'authorized_successor_changes':sorted(set(changed)&successor)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--verify-integrity',action='store_true')
    args=parser.parse_args()
    artifacts=render(*inputs())
    for name,value in artifacts.items():
        canonical=REPORT if name==REPORT.name else OUT/name
        if args.write:canonical.write_text(value)
        if args.output_dir:
            args.output_dir.mkdir(parents=True,exist_ok=True)
            (args.output_dir/name).write_text(value)
        if args.check or not (args.write or args.output_dir):assert canonical.read_text()==value, 'Stale output: '+name
    if args.verify_integrity:
        result=integrity();print(json.dumps(result,sort_keys=True));assert result['changed_count']==0
    print('215 candidates; three disjoint queues; no unresolved user policy; deterministic outputs verified.')


if __name__=='__main__':
    main()

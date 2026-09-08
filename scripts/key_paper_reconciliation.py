"""Read explicit, evidence-backed checklist decisions; never write manual data."""

IDENTITY_FIELDS = ('title', 'year', 'doi', 'arxiv_id', 'openalex_url')
CLASSIFICATIONS = {
    'SAME_PAPER_METADATA_CONFLICT', 'SAME_PAPER_TITLE_VARIANT', 'DISTINCT_PAPERS',
    'AMBIGUOUS_NEEDS_HUMAN_REVIEW', 'VALID_IN_SCOPE_ADD', 'EXISTING_CURRENT_PAPER',
    'EXISTING_METADATA_UPDATE_NEEDED', 'EXCLUDED_OUT_OF_SCOPE',
    'SUPERSEDED_OR_DUPLICATE', 'INSUFFICIENT_EVIDENCE', 'MISSING_ADD',
    'EXISTING_CURRENT', 'EXISTING_UPDATE_NEEDED', 'EXCLUDE', 'AMBIGUOUS',
}
REVIEW_CLASSIFICATIONS = {'AMBIGUOUS_NEEDS_HUMAN_REVIEW', 'INSUFFICIENT_EVIDENCE', 'AMBIGUOUS'}


def apply_decisions(keys, decisions):
    """Fail closed on stale source rows; decisions cannot manufacture coverage."""
    effective = [dict(row) for row in keys]
    seen = set()
    for decision in decisions:
        number = int(decision['checklist_row'])
        if number in seen or not 1 <= number <= len(keys):
            raise ValueError('Duplicate or invalid reconciliation checklist row')
        seen.add(number)
        if decision.get('checklist') != keys[number - 1]:
            raise ValueError(f'Stale reconciliation evidence for checklist row {number}')
        if decision.get('classification') not in CLASSIFICATIONS:
            raise ValueError(f'Unknown reconciliation classification at row {number}')
        if not decision.get('evidence_urls') or not decision.get('reason'):
            raise ValueError(f'Missing reconciliation evidence at row {number}')
        resolved = decision.get('resolved', {})
        if set(resolved) - set(IDENTITY_FIELDS):
            raise ValueError(f'Unsupported identity override at row {number}')
        effective[number - 1].update(resolved)
        effective[number - 1]['_reconciliation'] = decision
    return effective

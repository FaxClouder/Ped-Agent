"""Adapter to the frozen Layer 2 AND/OR scorer; unchanged three-valued semantics."""
from pathlib import Path
import importlib.util
from support import visible_support

_spec=importlib.util.spec_from_file_location('_pearl_chunking_frozen_evidence_score',Path(__file__).resolve().parent.parent/'pearl-evidence-dev80-20261004'/'score.py')
_old=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_old)
score_support=_old.score_support

def reviewed_support(spans,mapping):
    # Lazy import avoids the existing review scorer -> score_support dependency.
    # Keep certificate-only maps and their historical semantics unchanged.
    if any('visible_universe_review' in r for r in mapping['requirements']):
        from e1_visible_review import support_r06
        support,basis,_=support_r06(spans,mapping)
        return support,basis
    support=visible_support(spans,mapping)
    return support,{r:'certificate' for r in support}

def score_context(context,mapping,stage='final',failure=None):
    spans=[s for u in context[stage]['units'] for s in u['spans']]
    support,basis=reviewed_support(spans,mapping)
    if failure:
        support={r['requirement_id']:'unknown' for r in mapping['requirements']}
        basis={r:'technical_failure' for r in support}
    result=score_support(mapping['groups'],support)
    return dict(intent_id=mapping.get('intent_id'),context_id=context['context_id'],panel_id=context['panel_id'],stage=stage,support=support,support_basis=basis,failure=failure,**result)

def aggregate(rows):
    # Failed and empty cells retain their denominator and explicit unknown label.
    n=len(rows); counts={label:sum(r['sufficient']==label for r in rows) for label in ('yes','no','unknown')}
    return dict(n=n,**counts,complete_group_lower=counts['yes']/n if n else None,complete_group_upper=(counts['yes']+counts['unknown'])/n if n else None,failure_n=sum(bool(r.get('failure')) for r in rows))

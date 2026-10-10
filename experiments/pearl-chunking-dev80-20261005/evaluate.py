"""Offline E0 source-certificate scoring; no labels enter the query runtime."""
import argparse
import json
from pathlib import Path
from runtime import save_json,sha,cache_identity
from score import score_context,aggregate,score_support,reviewed_support

def rows(p):return [json.loads(l) for l in p.read_text('utf8').splitlines() if l.strip()]

def run(output,mapping_path):
    mapping=json.loads(mapping_path.read_text('utf8'));lookup={r['intent_id']:r for r in mapping['records']};details=[];mapping_hash=sha(mapping_path)
    for context in rows(output/'contexts.jsonl'):
        m=lookup[context['intent_id']];context_hash=cache_identity(context)
        for stage in ('raw','expanded','final'):
            result=score_context(context,m,stage)
            result.update(kind='context',groups=m['groups'],cell=f"{context['panel_id']}/{context['strategy']}/{context['budget']}/{stage}",context_sha256=context_hash,mapping_sha256=mapping_hash)
            details.append(result)
    for ranking in rows(output/'rankings.jsonl'):
        m=lookup[ranking['intent_id']];ranking_hash=cache_identity(ranking)
        for method in ('R1','R2','R3','R4'):
            for k in (1,5,10,20):
                visible=[s for child in ranking['results'][method][:k] for s in child['core_spans']+child['overlap_spans']]
                status,basis=reviewed_support(visible,m);failure=None
                if ranking.get('status','success')!='success':
                    status={r['requirement_id']:'unknown' for r in m['requirements']};basis={r:'technical_failure' for r in status};failure='missing_or_failed_retrieval'
                values=score_support(m['groups'],status)
                details.append(dict(kind='layer1_raw',intent_id=m['intent_id'],method=method,k=k,groups=m['groups'],support=status,support_basis=basis,failure=failure,cell=f'layer1_raw/{method}/{k}',mapping_sha256=mapping_hash,ranking_sha256=ranking_hash,**values))
    cells=sorted({r['cell'] for r in details});summaries={cell:aggregate([r for r in details if r['cell']==cell]) for cell in cells}
    reviewed=sum(any(q.get('visible_universe_review') or any(g.get('reviewer_id') and g.get('rationale') and g.get('status') in ('yes','no') for g in q.get('evidence_groups',[])) for q in m['requirements']) for m in lookup.values())
    return {'schema_version':'source-score-review-bridge-v2','scope':'Offline scoring of saved artifacts; no experiment execution or strategy selection.','mapping_path':str(mapping_path),'mapping_sha256':mapping_hash,'source_reviewed_intents':reviewed,'source_review_pending_intents':len(lookup)-reviewed,'review_count_definition':'Intents with at least one explicit certificate or visible-universe review; not complete requirement coverage.','details':details,'summaries':summaries,'true_definition':'Certificate-only maps retain containment semantics; reviewed maps reuse e1_visible_review.support_r06 including r07 adjudication and outside-universe unknown.','generation_calls':0,'remote_judge_calls':0}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--mapping',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();result=run(a.output,a.mapping);save_json(a.receipt,result);print('source scored',len(result['details']),'details',len(result['summaries']),'cells')

if __name__=='__main__':main()

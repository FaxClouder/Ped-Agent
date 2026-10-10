"""Inspect conclusion-relevant 4K gains/losses with actual reviewed witnesses."""
import argparse
from pathlib import Path
from e3 import load,rows,SOURCE
from assemble import union_spans,subtract_spans,key
from e1_visible_review import contained
from runtime import sha,save_rows,save_json
from e3_scope_revision import active_requirement

def run(out,revision):
    mapping=out/f'common-support-map-e3-{revision}.json';maps={m['intent_id']:m for m in load(mapping)['records']}
    elements={key(dict(doc_id=v['doc_id'],source_version=v['source_version'],element_id=e['element_id'])):e for v in load(SOURCE/'source-views-prepared.json') for e in v['elements']}
    base={(c['configuration_id'],c['intent_id']):union_spans([s for u in c['final']['units'] for s in u['spans']]) for p in out.glob('contexts-*-P0-4096-fixed_budget_main.jsonl') for c in rows(p)}
    base_scores={(s['configuration_id'],s['intent_id']):s for s in rows(out/f'score-details-e3-{revision}.jsonl') if s['strategy']=='P0' and s['budget']==4096 and s['panel_id']=='fixed_budget_main' and s['stage']=='final'}
    audited=[]
    for case in rows(out/f'cases-e3-{revision}.jsonl'):
        if case['budget']!=4096 or case['panel_id']!='fixed_budget_main':continue
        # P0 budget losses also explain frozen main baseline constraints.
        m=maps[case['intent_id']];records=[]
        visible={s:union_spans([p for u in case['stages'][s]['units'] for p in u['spans']]) for s in ('raw','expanded','final')}
        visible['P0_final']=base[case['configuration_id'],case['intent_id']]
        for q in m['requirements']:
            q=active_requirement(q)
            rid=q['requirement_id'];states={s:case['stages'][s]['score']['support'][rid] for s in ('raw','expanded','final')}
            states['P0_final']=base_scores[case['configuration_id'],case['intent_id']]['support'][rid]
            if len(set(states.values()))==1:continue
            review=q.get('visible_universe_review',{})
            alternatives=[dict(source_spans=g['necessary_spans'],rationale=g.get('rationale','Frozen affirmative evidence certificate'),provenance='frozen_certificate') for g in q['evidence_groups'] if g['status']=='yes']
            alternatives+=[dict(a,provenance='reviewed_visible_alternative') for a in review.get('alternatives',[])]
            alternatives+=[dict(v,provenance='adjudicated_visible_variant') for u in review.get('uncertain',[]) for v in u.get('adjudicated_variants',[]) if v['verdict']=='supports']
            witnesses=[]
            for stage,status in states.items():
                if status!='yes':continue
                candidates=[a for a in alternatives if contained(a['source_spans'],visible[stage])]
                assert candidates,'Affirmative actual stage lacks an explicit reviewed witness'
                alt=min(candidates,key=lambda a:sum(s['end']-s['start'] for s in a['source_spans']))
                witnesses.append(dict(stage=stage,provenance=alt['provenance'],rationale=alt.get('rationale'),source_spans=alt['source_spans'],actual_text=[elements[key(s)]['text'][s['start']:s['end']] for s in alt['source_spans']],missing_from_raw=subtract_spans(alt['source_spans'],visible['raw']),missing_from_final=subtract_spans(alt['source_spans'],visible['final']),missing_from_P0_final=subtract_spans(alt['source_spans'],visible['P0_final'])))
            records.append(dict(requirement_id=rid,description=q['description'],scope=q.get('scope'),states=states,witnesses=witnesses))
        audited.append(dict(intent_id=case['intent_id'],configuration_id=case['configuration_id'],strategy=case['strategy'],budget=4096,panel_id=case['panel_id'],tags=case['tags'],raw=case['raw'],expanded=case['expanded'],final=case['final'],P0_final=case['P0_final'],context_id=case['context_id'],truncation=case['truncation'],requirements=records,mapping_sha256=sha(mapping),scope='Actual reviewed witness/condition and missing-source interval audit; preserves inherited semantic provenance, not a new score or a paper-coincidence inference.'))
    save_rows(out/f'mechanism-audit-e3-{revision}.jsonl',audited)
    save_json(out/f'mechanism-audit-verification-{revision}.json',dict(status='passed',main4k_cases=len(audited),intents=len({a['intent_id'] for a in audited}),scope='All saved conclusion-relevant 4K Top100 cases; each changing affirmative requirement tied to complete visible certificate/review alternative; source gaps and actual text recorded.',code_sha256=sha(__file__)))
    print('Mechanism source audit',len(audited),'cases',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--revision',required=True);a=p.parse_args();run(a.output.resolve(),a.revision)

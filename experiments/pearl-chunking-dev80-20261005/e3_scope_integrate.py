"""Version explicit scope corrections and bind new proof to actual E3 stages."""
import argparse,copy
from pathlib import Path
from e3 import load,rows,SOURCE
from e1_visible_review import contained
from runtime import ROOT,sha,save_json
from assemble import union_spans,key

def run(out,revision):
    previous=out/'common-support-map-e3-r09.json';review_path=out/'review-adjudications-e3-r10.json';review=load(review_path)
    assert review['base_mapping_sha256']==sha(previous)
    mapping=copy.deepcopy(load(previous));maps={m['intent_id']:m for m in mapping['records']}
    needed={r['intent_id'] for r in review['requirements']};contexts={}
    for p in out.glob('contexts-*.jsonl'):
        for c in rows(p):
            if c['intent_id'] in needed:contexts[c['context_id']]=(p,c)
    elements={key(dict(doc_id=v['doc_id'],source_version=v['source_version'],element_id=e['element_id'])):e for v in load(SOURCE/'source-views-prepared.json') for e in v['elements']}
    updates=[]
    for r in review['requirements']:
        q=next(q for q in maps[r['intent_id']]['requirements'] if q['requirement_id']==r['requirement_id'])
        v=dict(excluded_certificate_indices=r['excluded_certificate_indices'],excluded_alternative_indices=r['excluded_alternative_indices'],negative_scopes=[],review_path=review_path.relative_to(ROOT).as_posix(),review_sha256=sha(review_path),reviewer_id=review['reviewer_id'])
        assert {x['index'] for x in r['certificate_judgments']}==set(range(len(q['evidence_groups'])))
        assert {x['index'] for x in r['alternative_judgments']}==set(range(len(q['visible_universe_review']['alternatives'])))
        for label,entries,field,indices in [('certificate',r['certificate_judgments'],'necessary_spans',v['excluded_certificate_indices']),('alternative',r['alternative_judgments'],'source_spans',v['excluded_alternative_indices'])]:
            original=q['evidence_groups'] if label=='certificate' else q['visible_universe_review']['alternatives']
            for entry in entries:
                assert original[entry['index']][field]==entry['source_spans']
                assert (entry['index'] in indices)==(entry['verdict']=='does_not_support')
        q['visible_universe_review']['scope_revision']=v
        positive_bindings=[]
        for alt in r['complete_source_alternatives']:
            for s in alt['source_spans']:assert 0<=s['start']<s['end']<=len(elements[key(s)]['text'])
            actual=[]
            for p,c in contexts.values():
                if c['intent_id']!=r['intent_id']:continue
                for stage in ('raw','expanded','deduplicated','final'):
                    spans=[s for u in c[stage]['units'] for s in u['spans']]
                    if contained(alt['source_spans'],spans):actual.append(dict(context_id=c['context_id'],stage=stage,text_sha256=c[stage]['text_sha256'],contexts_file_sha256=sha(p)))
            if actual:
                q['visible_universe_review']['alternatives'].append(dict(alt,reviewer_id=review['reviewer_id'],review_result_sha256=sha(review_path),actual_stage_bindings=actual))
                positive_bindings.append(dict(source_spans=alt['source_spans'],actual_stages=len(actual)))
        updates.append(dict(intent_id=r['intent_id'],requirement_id=r['requirement_id'],scope_revision=v,positive_actual_bindings=positive_bindings))
    supplemental=out/'review-final-scopes-independent-r10.json'
    if supplemental.exists():
        result=load(supplemental)
        for verdict in result['requirements']:
            p,c=contexts[verdict['context_id']];assert verdict['final_text_sha256']==c['final']['text_sha256'] and verdict['contexts_file_sha256']==sha(p)
            q=next(q for q in maps[verdict['intent_id']]['requirements'] if q['requirement_id']==verdict['requirement_id'])
            if verdict['status']=='no' and verdict['coverage_complete'] and verdict['alternatives_exhaustive']:
                q['visible_universe_review']['scope_revision']['negative_scopes'].append(union_spans([s for u in c['final']['units'] for s in u['spans']]))
            q['visible_universe_review']['scope_revision']['final_scope_review']=dict(path=supplemental.relative_to(ROOT).as_posix(),sha256=sha(supplemental),status=verdict['status'],coverage_complete=verdict['coverage_complete'],alternatives_exhaustive=verdict['alternatives_exhaustive'])
    mapping['e3_revision']=revision;mapping['schema_version']='source-support-map-e3-scope-'+revision
    target=out/f'common-support-map-e3-{revision}.json';save_json(target,mapping)
    lineage=copy.deepcopy(load(out/'map-lineage-e3-r09.json'));lineage.update(new_mapping_sha256=sha(target),previous_mapping_sha256=sha(previous),scope_corrections=updates,scope_scoring_code_sha256=sha(Path(__file__).with_name('e3_scope_revision.py')),scope_integration_code_sha256=sha(__file__),scope='Historical requirements/groups/certificates literal and retained. Explicit independently reviewed proof exclusions plus actual-stage-bound complete alternatives and exhaustive exact negative scopes; uniform new E3 scoring.');save_json(out/f'map-lineage-e3-{revision}.json',lineage)
    print('Scope corrections integrated',revision,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--revision',required=True);a=p.parse_args();run(a.output.resolve(),a.revision)

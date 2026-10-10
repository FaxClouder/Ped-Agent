"""Version review extensions without relabeling frozen r07 judgments or outputs."""
import argparse
import copy
from pathlib import Path
from e3 import REVIEW,load,rows
from runtime import ROOT,sha,save_json
from assemble import union_spans,subtract_spans,key
from e1_visible_review import contained,portion,overlaps

def uncertain_spans(item):
    if isinstance(item,dict):return item.get('source_spans',[item['source_span']] if 'source_span' in item else [])
    return item

def run(out,revision):
    base=REVIEW/'common-support-map-e1-r07.json';mapping=copy.deepcopy(load(base));maps={r['intent_id']:r for r in mapping['records']};accepted=[]
    contexts={c['context_id']:{**{k:c[k] for k in ('intent_id','configuration_id','strategy','budget','panel_id')},'final':dict(text_sha256=c['final']['text_sha256'],units=[dict(spans=u['spans']) for u in c['final']['units']])} for p in out.glob('contexts-*.jsonl') for c in rows(p)}
    review_statuses={}
    for candidate in sorted((out/'review-results-e3-r08').glob('*.json')):
        r=load(candidate);packet_id=r.get('packet_id',r['intent_id'])
        for v in r['requirements']:review_statuses.setdefault((r['intent_id'],packet_id,v['requirement_id']),set()).add(v['status'])
    for path in sorted((out/'review-results-e3-r08').glob('*.json')):
        result=load(path);i=result['intent_id'];packet_id=result.get('packet_id',i);assert packet_id in (i,i+'-fixed-sample',i+'-selection-final-r09')
        packet_path=out/'review-packets-e3-r08'/(packet_id+'.json');packet=load(packet_path);binding=load(packet_path.with_name(packet_id+'-binding.json'))
        assert sha(packet_path)==binding['packet_sha256'] and binding['mapping_sha256']==sha(base)
        universe=binding['visible_spans'];requests={r['requirement_id'] for r in packet['requirements']}
        assert union_spans(universe)==union_spans([s['source_span'] for s in packet['segments']])
        if binding['contexts']:
            actual=[]
            for c in binding['contexts']:
                ctx=contexts[c['context_id']]
                assert ctx['intent_id']==i and ctx['final']['text_sha256']==c['text_sha256']
                for field in ('configuration_id','strategy','budget','panel_id'):assert ctx[field]==c[field]
                actual.extend(s for u in ctx['final']['units'] for s in u['spans'])
            assert union_spans(actual)==union_spans(universe)
        else:raise ValueError('Review universe has no actual context binding')
        assert len(result['requirements'])==len(requests) and {r['requirement_id'] for r in result['requirements']}==requests and result.get('human_verified') is False
        for verdict in result['requirements']:
            verdict=copy.deepcopy(verdict)
            if verdict['status']=='no' and 'unknown' in review_statuses[i,packet_id,verdict['requirement_id']]:
                verdict['status']='unknown';verdict['alternatives_exhaustive']=False
                verdict.setdefault('caveats',[]).append('Independent reviews of identical packet disagree no/unknown; retain unknown and do not expand negative scope pending adjudication.')
            adjudication_path=out/'review-adjudications-e3-r08'/(i+'.json')
            adjudication_applies=adjudication_path.exists() and path.stem==i
            if adjudication_applies:
                adjudication=load(adjudication_path)
                if adjudication['requirement_id']==verdict['requirement_id']:
                    proposed=verdict.get('alternatives',[]);judgments=adjudication['alternatives']
                    assert {x['index'] for x in judgments}==set(range(len(proposed))) and len(judgments)==len(proposed)
                    verdict['alternatives']=[proposed[x['index']] for x in judgments if x['verdict']=='supports']
                    verdict['alternatives_exhaustive']=adjudication['alternatives_exhaustive']
                    verdict.setdefault('uncertain_spans',[]).extend(adjudication.get('uncertain_spans',[]))
                    verdict.setdefault('caveats',[]).append('Independent alternative-level adjudication: '+adjudication['rationale'])
                    if not verdict['alternatives']:verdict['status']='unknown' if any(x['verdict']=='uncertain' for x in judgments) or verdict.get('uncertain_spans') or not verdict.get('alternatives_exhaustive') else 'no'
            rid=verdict['requirement_id'];q=next(q for q in maps[i]['requirements'] if q['requirement_id']==rid);status=verdict['status'];assert status in ('yes','no','unknown')
            alternatives=verdict.get('alternatives',[])
            if status=='yes':assert alternatives
            else:assert not alternatives, 'Only affirmative requirement verdicts may add complete support alternatives'
            assert verdict.get('rationale')
            for alt in alternatives:assert alt.get('rationale') and contained(alt['source_spans'],universe)
            old=q.get('visible_universe_review')
            if old is None:
                old=dict(universe_status='no' if status=='no' else 'yes' if verdict.get('alternatives_exhaustive') else 'unknown',universe_spans=[],alternatives=[],uncertain=[],reviewer_id=result['reviewer_id'],rationale='E3 actual visible text universe review; original certificates retained.')
                q['visible_universe_review']=old
            exhaustive=verdict.get('coverage_complete') is True and verdict.get('alternatives_exhaustive') is True and status!='unknown'
            if exhaustive:
                old['universe_spans']=union_spans(old['universe_spans']+universe)
                # Resolve only portions actually included in this packet, retaining
                # historical variants and uncertainty beyond this review scope.
                for u in old['uncertain']:
                    part=portion(u['source_spans'],universe)
                    if not part:continue
                    supporting=[a for a in alternatives if contained(a['source_spans'],part)]
                    uncertain=verdict.get('uncertain_spans',[])
                    flag=any(overlaps(uncertain_spans(x),part) for x in uncertain)
                    if not flag:
                        variant=dict(verdict='supports' if supporting else 'does_not_support',source_spans=supporting[0]['source_spans'] if supporting else part,reviewer_id=result['reviewer_id'],rationale=verdict['rationale'],review_result_sha256=sha(path))
                        u.setdefault('adjudicated_variants',[]).append(variant)
            for alt in alternatives:
                if not any(a['source_spans']==alt['source_spans'] for a in old['alternatives']):old['alternatives'].append(dict(alt,reviewer_id=result['reviewer_id'],review_result_sha256=sha(path)))
            for uncertain in verdict.get('uncertain_spans',[]):
                spans=uncertain_spans(uncertain)
                assert contained(spans,universe)
                old['uncertain'].append(dict(source_spans=spans,rationale=uncertain.get('rationale','reviewed unresolved passage') if isinstance(uncertain,dict) else 'reviewed unresolved passage',reviewer_id=result['reviewer_id'],adjudicated_variants=[dict(verdict='uncertain',source_spans=spans,reviewer_id=result['reviewer_id'],rationale='E3 reviewer retained ambiguity; visible portions remain unknown.')]))
            old.setdefault('review_extensions',[]).append(dict(revision=result.get('review_revision','r08'),reviewer_id=result['reviewer_id'],review_result_sha256=sha(path),adjudication_sha256=sha(adjudication_path) if adjudication_applies else None,packet_sha256=sha(packet_path),status=status,coverage_complete=verdict.get('coverage_complete',False),alternatives_exhaustive=verdict.get('alternatives_exhaustive',False),universe_expanded=exhaustive,caveats=verdict.get('caveats',[])))
            accepted.append(dict(intent_id=i,requirement_id=rid,status=status,exhaustive=exhaustive,alternative_count=len(alternatives),reviewer_id=result['reviewer_id'],review_revision=result.get('review_revision','r08')))
    mapping.update(schema_version='source-support-map-e3-review-'+revision,e3_base_schema_version=mapping.get('schema_version'),e3_revision=revision,e3_base_mapping_sha256=sha(base),human_verified=False)
    path=out/f'common-support-map-e3-{revision}.json';save_json(path,mapping)
    save_json(out/f'map-lineage-e3-{revision}.json',dict(base_mapping_path=base.relative_to(ROOT).as_posix(),base_mapping_sha256=sha(base),new_mapping_sha256=sha(path),accepted=accepted,code_sha256=sha(__file__),reviews_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted((out/'review-results-e3-r08').glob('*.json'))},adjudications_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted((out/'review-adjudications-e3-r08').glob('*.json'))},scope='Frozen requirements/groups/certificates retained; only actual reviewed alternatives and explicitly exhaustive reviewed source scope appended. Unknown and historical judgments preserved; all E3 configurations uniformly rescored.'))
    print('Integrated',len(accepted),'requirement reviews',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--revision',required=True);a=p.parse_args();run(a.output.resolve(),a.revision)

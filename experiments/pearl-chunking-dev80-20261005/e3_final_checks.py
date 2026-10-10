"""Reopen review lineage, paired contrasts and the E2 freeze without rescoring."""
import argparse
import collections
import copy
import math
from pathlib import Path
from e3 import CONFIGS,REVIEW,SOURCE,load,rows
from runtime import ROOT,sha,save_json,save_rows
from assemble import union_spans,digest

def run(out,revision):
    base=load(REVIEW/'common-support-map-e1-r07.json')
    new=load(out/f'common-support-map-e3-{revision}.json')
    bm={r['intent_id']:r for r in base['records']};nm={r['intent_id']:r for r in new['records']}
    assert bm.keys()==nm.keys()
    for i in bm:
        a=copy.deepcopy(bm[i]);b=copy.deepcopy(nm[i])
        for r in a['requirements']:r.pop('visible_universe_review',None)
        for r in b['requirements']:r.pop('visible_universe_review',None)
        assert a==b,'Frozen requirement/group/certificate mutation'
    contexts={}
    for p in out.glob('contexts-*.jsonl'):
        for r in rows(p):
            c={k:v for k,v in r.items() if k not in ('raw','expanded','deduplicated','dedup','final')}
            for stage in ('raw','expanded','final'):c[stage]=dict(text_sha256=r[stage]['text_sha256'],units_digest=digest(r[stage]['units']))
            c['final']['units']=[dict(spans=u['spans']) for u in r['final']['units']]
            contexts[r['context_id']]=c
    elements={(v['doc_id'],v['source_version'],e['element_id']):e for v in load(SOURCE/'source-views-prepared.json') for e in v['elements']}
    packets=0;bindings=0
    for p in (out/'review-packets-e3-r08').glob('*.json'):
        if p.stem.endswith('-binding'):continue
        packet=load(p);binding=load(p.with_name(p.stem+'-binding.json'))
        assert sha(p)==binding['packet_sha256']
        assert union_spans(binding['visible_spans'])==union_spans([s['source_span'] for s in packet['segments']])
        for s in packet['segments']:
            span=s['source_span'];e=elements[span['doc_id'],span['source_version'],span['element_id']]
            assert s['text']==e['text'][span['start']:span['end']]
        actual=[]
        for c in binding['contexts']:
            ctx=contexts[c['context_id']]
            assert ctx['intent_id']==packet['intent_id'] and ctx['final']['text_sha256']==c['text_sha256']
            for k in ('configuration_id','strategy','budget','panel_id'):assert ctx[k]==c[k]
            actual.extend(s for u in ctx['final']['units'] for s in u['spans'])
            bindings+=1
        assert union_spans(actual)==union_spans(binding['visible_spans'])
        packets+=1
    details=list(rows(out/f'score-details-e3-{revision}.jsonl'))
    states={(r['configuration_id'],r['panel_id'],r['budget'],r['strategy'],r['intent_id'],r['stage']):r['sufficient'] for r in details}
    for k,status in states.items():
        if k[-1]=='expanded':assert states[k[:-1]+('deduplicated',)]==status,'Source-union dedup changed sufficiency'
    stats=load(out/f'statistics-e3-{revision}.json');tests=[]
    for r in stats['paired']:
        c,p,B,P=r['configuration_id'],r['panel_id'],r['budget'],r['strategy']
        pairs=[(states[c,p,B,P,i,'final'],states[c,p,B,'P0',i,'final']) for i in bm]
        gain=sum(a=='yes' and b=='no' for a,b in pairs);loss=sum(a=='no' and b=='yes' for a,b in pairs)
        assert (gain,loss)==(r['confirmed_gain'],r['confirmed_loss'])
        assert math.isclose(r['confirmed_yes_delta'],sum((a=='yes')-(b=='yes') for a,b in pairs)/80)
        lower=sum((a=='yes')-(b!='no') for a,b in pairs)/80;upper=sum((a!='no')-(b=='yes') for a,b in pairs)/80
        assert r['possible_delta_interval']==[lower,upper]
        if all(a!='unknown' and b!='unknown' for a,b in pairs):
            n=gain+loss;k=min(gain,loss)
            exact=min(1.,2*sum(math.comb(n,j) for j in range(k+1))/2**n) if n else 1.
            assert math.isclose(exact,r['mcnemar_p']);tests.append((exact,r))
        else:assert r['mcnemar_p'] is None
    running=0.
    for j,(pv,r) in enumerate(sorted(tests,key=lambda x:x[0])):
        running=max(running,min(1.,pv*(len(tests)-j)))
        assert math.isclose(running,r['holm_p']) and r['holm_family_size']==len(tests)
    for r in stats['baseline_paired']:
        c,p,B,P=r['configuration_id'],r['panel_id'],r['budget'],r['strategy'];ref=r['reference_configuration']
        pairs=[(states[c,p,B,P,i,'final'],states[ref,p,B,P,i,'final']) for i in bm]
        assert r['confirmed_gain']==sum(a=='yes' and b=='no' for a,b in pairs)
        assert r['confirmed_loss']==sum(a=='no' and b=='yes' for a,b in pairs)
        assert math.isclose(r['confirmed_yes_delta'],sum((a=='yes')-(b=='yes') for a,b in pairs)/80)
        assert r['possible_delta_interval']==[sum((a=='yes')-(b!='no') for a,b in pairs)/80,sum((a!='no')-(b=='yes') for a,b in pairs)/80]
    selection=load(out/f'recovery-selection-e3-{revision}.json');scores=load(out/f'scores-e3-{revision}.json')
    cold=load(out/'cost-reference-e3-r02.json')
    for c,decision in selection['all_configuration_decisions'].items():
        costs={r['strategy']:r['mean_seconds'] for r in cold['summary'] if r['configuration_id']==c}
        cells=[r for r in scores['summary'] if r['configuration_id']==c and r['budget']==4096 and r['panel_id']=='fixed_budget_main']
        ordered=sorted(cells,key=lambda r:(-r['yes'],costs[r['strategy']],r['strategy']));best=ordered[0]
        threats=[r['strategy'] for r in ordered[1:] if r['yes']+r['unknown']>best['yes'] or (r['yes']+r['unknown']==best['yes'] and (costs[r['strategy']],r['strategy'])<(costs[best['strategy']],best['strategy']))]
        assert decision['threats']==threats and decision['status']==('pending_review' if threats else 'frozen')
        assert decision['selected']==(None if threats else best['strategy'])
    assert selection['basis_configuration']==CONFIGS[1] and selection['E2_started'] is False
    case_count=0
    for case in rows(out/f'cases-e3-{revision}.jsonl'):
        ctx=contexts[case['context_id']]
        assert case['mapping_sha256']==sha(out/f'common-support-map-e3-{revision}.json')
        for stage in ('raw','expanded','final'):
            assert digest(case['stages'][stage]['units'])==ctx[stage]['units_digest']
            assert case['stages'][stage]['score']['visible_text_sha256']==ctx[stage]['text_sha256']
        assert case['truncation']==ctx['truncation'];case_count+=1
    old={(r['configuration_id'],r['panel_id'],r['budget'],r['strategy'],r['intent_id'],r['stage']):r for r in rows(out/'score-details-e3-r07.jsonl')}
    changes=[]
    for r in details:
        key=tuple(r[k] for k in ('configuration_id','panel_id','budget','strategy','intent_id','stage'));o=old[key]
        assert o['visible_text_sha256']==r['visible_text_sha256'] and o['ranking_file_sha256']==r['ranking_file_sha256']
        if o['support']!=r['support'] or o['sufficient']!=r['sufficient']:
            changes.append(dict(zip(('configuration_id','panel_id','budget','strategy','intent_id','stage'),key),before=o['sufficient'],after=r['sufficient'],before_support=o['support'],after_support=r['support'],visible_text_sha256=r['visible_text_sha256']))
    save_rows(out/f'scoring-revision-changes-{revision}.jsonl',changes)
    save_json(out/f'final-analysis-verification-{revision}.json',dict(status='passed',frozen_records=80,actual_packet_texts=packets,packet_context_bindings=bindings,reviewed_universe_three_way_equality='all packets, bound final contexts, and reviewed universe',cases_reopened=case_count,paired_contrasts=len(stats['paired']),binary_exact_tests=len(tests),revision_changes=len(changes),revision_change_scope='Same frozen text/rankings; review-version changes kept distinct from restoration gains.',selection_status=selection['status'],code_sha256=sha(__file__)))
    print('Final independent checks passed',selection['status'],len(changes),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--revision',required=True);a=p.parse_args();run(a.output.resolve(),a.revision)

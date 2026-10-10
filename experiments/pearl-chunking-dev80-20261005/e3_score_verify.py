"""Gate E3 scoring and independently reopen every saved score and transition."""
import argparse
import collections
from pathlib import Path
from runtime import ROOT,sha,save_json
from e3 import score,rows,load,CONFIGS,PANELS,STAGES,REVIEW
from e1_visible_review_verify import intervals,req_status,sufficient
from e1_visible_review import support_r06

def run(out,mp,revision):
    verification=load(out/'assembly-verification-r01.json');assert verification['status']=='passed' and verification['contexts_checked']==2880
    runtime=load(out/'runtime-r01.json');base=REVIEW/'common-support-map-e1-r07.json'
    assert sha(base)==runtime['map_sha256']
    if revision=='r07':assert mp==base and sha(mp)==runtime['map_sha256']
    else:
        lineage=load(out/f'map-lineage-e3-{revision}.json')
        assert lineage['base_mapping_sha256']==sha(base) and lineage['new_mapping_sha256']==sha(mp)
    maps={m['intent_id']:m for m in load(mp)['records']};assert len(maps)==80
    cost=load(out/'cost-e3-r01.json');cells={}
    for record in cost['cells']:
        cell=record['configuration_id'],record['strategy'],record['budget'],record['panel_id']
        assert cell not in cells;cells[cell]=record
    assert set(cells)=={(c,P,B,panel) for c in CONFIGS for P in ('P0','P1','P2') for B in (4096,8192) for panel in PANELS}
    contexts={};input_hashes={}
    for cell,record in cells.items():
        c,P,B,panel=cell;path=out/f'contexts-{c}-{P}-{B}-{panel}.jsonl'
        assert sha(path)==record['contexts_file_sha256'];input_hashes[path.relative_to(ROOT).as_posix()]=sha(path)
        saved=list(rows(path));assert len(saved)==80 and {r['intent_id'] for r in saved}==set(maps)
        for ctx in saved:
            assert (ctx['configuration_id'],ctx['strategy'],ctx['budget'],ctx['panel_id'])==cell
            compact={k:v for k,v in ctx.items() if k not in STAGES and k not in ('dedup',)}
            for stage in STAGES:compact[stage]=dict(text_sha256=ctx[stage]['text_sha256'],units=[dict(spans=u['spans']) for u in ctx[stage]['units']])
            contexts[cell+(ctx['intent_id'],)]=compact
    assert len(contexts)==2880
    save_json(out/f'score-gate-e3-{revision}.json',dict(status='passed',contexts=2880,input_sha256=input_hashes,mapping_sha256=sha(mp),assembly_verification_sha256=sha(out/'assembly-verification-r01.json'),scoring_code_sha256={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'experiments/pearl-chunking-dev80-20261005'/n for n in ('e3.py','score.py','e1_visible_review.py','e3_score_verify.py')]}))
    score(out,mp,revision)
    # All following checks reopen serialized outputs. No in-memory score trust.
    details=list(rows(out/f'score-details-e3-{revision}.jsonl'));actual={};states={};n=0
    for r in details:
        cell=r['configuration_id'],r['strategy'],r['budget'],r['panel_id'],r['intent_id'];ctx=contexts[cell];stage=r['stage']
        k=cell+(stage,);assert k not in actual;actual[k]=r
        spans=[s for u in ctx[stage]['units'] for s in u['spans']];iv=intervals(spans)
        sup={q['requirement_id']:req_status(q,spans,iv) for q in maps[r['intent_id']]['requirements']}
        assert r['support']==sup and r['sufficient']==sufficient(maps[r['intent_id']]['groups'],sup)
        groups=maps[r['intent_id']]['groups']
        assert r['coverage_lower']==max(sum(sup[x]=='yes' for x in g)/len(g) for g in groups)
        assert r['coverage_upper']==max(sum(sup[x]!='no' for x in g)/len(g) for g in groups)
        assert r['support_basis']==support_r06(spans,maps[r['intent_id']])[1]
        assert r['context_id']==ctx['context_id'] and r['mapping_sha256']==sha(mp) and r['visible_text_sha256']==ctx[stage]['text_sha256']
        assert r['ranking_file_sha256']==ctx['ranking_file_sha256']
        states[k]=r['sufficient'];n+=1
    assert n==11520
    summary=load(out/f'scores-e3-{revision}.json');assert summary['score_cells']==n
    for s in summary['summary']:
        cell=s['configuration_id'],s['strategy'],s['budget'],s['panel_id']
        counts=collections.Counter(states[cell+(i,'final')] for i in maps)
        assert s['n']==80 and all(s[k]==counts[k] for k in ('yes','no','unknown'))
        assert s['complete_group_lower']==counts['yes']/80 and s['complete_group_upper']==(counts['yes']+counts['unknown'])/80
    transitions=list(rows(out/f'transitions-e3-{revision}.jsonl'));seen=set()
    for t in transitions:
        cell=t['configuration_id'],t['strategy'],t['budget'],t['panel_id'],t['intent_id'];a,b=t['comparison'].split('->')
        if a=='P0_final':before=states[(cell[0],'P0',cell[2],cell[3],cell[4],'final')];after=states[cell+('final',)]
        else:before=states[cell+(a,)];after=states[cell+(b,)]
        assert (before,after)==(t['before'],t['after'])
        label='confirmed_gain' if before=='no' and after=='yes' else 'confirmed_loss' if before=='yes' and after=='no' else 'possible_loss' if before=='yes' and after=='unknown' else 'unresolved_to_yes' if before=='unknown' and after=='yes' else before+'->'+after
        assert t['transition']==label
        k=cell+(t['comparison'],);assert k not in seen;seen.add(k)
    assert len(transitions)==10560
    unknown=list(rows(out/f'unknown-e3-{revision}.jsonl'))
    ukeys={(r['configuration_id'],r['strategy'],r['budget'],r['panel_id'],r['intent_id'],'final') for r in unknown}
    assert len(ukeys)==len(unknown) and ukeys=={k for k,v in states.items() if k[-1]=='final' and v=='unknown'}
    files=[out/f'{name}-e3-{revision}.{extension}' for name,extension in [('score-details','jsonl'),('scores','json'),('transitions','jsonl'),('unknown','jsonl')]]
    save_json(out/f'score-verification-e3-{revision}.json',dict(status='passed',saved_detail_checks=n,aggregate_cells=36,transition_checks=len(transitions),unknown_cells=len(unknown),mapping_sha256=sha(mp),artifact_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files},verification_code_sha256=sha(__file__)))
    print('Saved score verification passed',n,len(transitions),len(unknown),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--mapping',type=Path,required=True);p.add_argument('--revision',required=True);a=p.parse_args();run(a.output.resolve(),a.mapping.resolve(),a.revision)

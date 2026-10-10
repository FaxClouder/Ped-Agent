"""E3 only: assemble frozen R4, score actual text, keep r07 unknowns explicit."""
import argparse
import json
import os
import statistics
import time
from pathlib import Path
from runtime import ROOT, EXP, sha, save_json, save_rows, load_queries
from smoke import counter
from assemble import assemble, digest
from e1_batch import batched_search
from e1_closeout import verify_manifest
from e1_visible_review_verify import intervals, req_status, sufficient
from score import score_context, aggregate

SOURCE=ROOT/'outputs/pearl-chunking-dev80-20261005-05'
REVIEW=ROOT/'outputs/pearl-chunking-dev80-20261005-07'
CLOSE=ROOT/'outputs/pearl-chunking-dev80-20261006-06'
CONFIGS=('B0-regex320-overlap48-M0','C2-L384-O0-M0','C3-L256-O0-M0')
PANELS=('fixed_budget_main','seed10_diagnostic')
STAGES=('raw','expanded','deduplicated','final')

def load(p):return json.loads(Path(p).read_text('utf8'))
def rows(p):
    with Path(p).open(encoding='utf8') as f:
        for line in f:
            if line.strip():yield json.loads(line)

def transition(a,b):
    if a=='no' and b=='yes':return 'confirmed_gain'
    if a=='yes' and b=='no':return 'confirmed_loss'
    if a=='yes' and b=='unknown':return 'possible_loss'
    if a=='unknown' and b=='yes':return 'unresolved_to_yes'
    return a+'->'+b

def choose_recovery(table):
    order=sorted(table,key=lambda r:(-r['yes'],r['mean_seconds'],r['strategy']))
    best=order[0]
    threats=[r['strategy'] for r in order if r['strategy']!=best['strategy'] and r['yes']+r['unknown']>=best['yes']]
    return dict(status='pending_review' if threats or best['unknown'] else 'frozen',selected=None if threats or best['unknown'] else best['strategy'],threats=threats,order=[r['strategy'] for r in order],rule='4K confirmed complete groups descending; measured assembly seconds ascending for ties; strategy id. Unknowns that can alter choice require review.')

def prepare(output):
    output.mkdir(exist_ok=False)
    preservation={}
    for run in (CLOSE,REVIEW,SOURCE):
        print('hashing',run.name,flush=True)
        preservation[run.name]=verify_manifest(run)
    if preservation[CLOSE.name]['code_drift']:raise ValueError('Session A scoring code drift')
    save_json(output/'input-preservation-r01.json',preservation)
    selection=load(REVIEW/'candidate-selection-e1-r07.json')
    v=load(REVIEW/'verification-e1-r07.json')
    mp=REVIEW/'common-support-map-e1-r07.json'
    assert selection['status']=='frozen' and selection['selected']==list(CONFIGS[1:])
    assert v['status']=='passed' and v['mapping_sha256']==sha(mp)
    c=counter()
    save_json(output/'runtime-r01.json',dict(tokenizer_fingerprint=c.fingerprint,tokenizer_sha256=sha(ROOT/'memPed/knowledge/models/bge-m3/tokenizer.json'),code_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [EXP/n for n in ('e3.py','assemble.py','e1_batch.py','score.py','e1_visible_review.py','e1_visible_review_verify.py','smoke.py')]},configuration_ids=CONFIGS,ranking_inputs={config:sha(SOURCE/('index-'+config)/'rankings.jsonl') for config in CONFIGS},source_views_sha256=sha(SOURCE/'source-views-prepared.json'),parent_sha256=sha(SOURCE/'public-parent-graph.json'),map_sha256=sha(mp),retrieval_calls=0,index_builds=0,generation_calls=0,remote_judge_calls=0,E2_units=0))
    queries=load_queries(SOURCE/'queries.jsonl',80)
    views=load(SOURCE/'source-views-prepared.json');parents=load(SOURCE/'public-parent-graph.json')
    frozen=load(SOURCE/'verification-e1-r01.json');cost=[]
    with batched_search():
        for config in CONFIGS:
            directory=SOURCE/('index-'+config)
            rankpath=directory/'rankings.jsonl'
            assert sha(rankpath)==frozen['checks'][config]['artifact_sha256']['rankings.jsonl']
            ranks=list(rows(rankpath));assert len(ranks)==80 and {r['intent_id'] for r in ranks}=={q['intent_id'] for q in queries}
            for P in ('P0','P1','P2'):
                for B in (4096,8192):
                    for panel in PANELS:
                        path=output/f'contexts-{config}-{P}-{B}-{panel}.jsonl'
                        started=time.perf_counter();seconds=[];tokens=[];sizes=[];n=0
                        with path.open('x',encoding='utf8',newline='\n') as f:
                            for row in ranks:
                                assert row['status']=='success'
                                value=assemble(row['results']['R4'],views,parents,P,B,panel,c)
                                value.update(intent_id=row['intent_id'],configuration_id=config,ranking_file_sha256=sha(rankpath),query_sha256=row['query_sha256'])
                                f.write(json.dumps(value,ensure_ascii=False)+'\n');n+=1
                                seconds.append(value['assembly_seconds']);tokens.append(value['final']['token_count']);sizes.append(len(value['final']['serialized_context'].encode()))
                                if n%20==0:print(config,P,B,panel,n,flush=True)
                        cost.append(dict(configuration_id=config,strategy=P,budget=B,panel_id=panel,contexts=n,wall_seconds=time.perf_counter()-started,mean_seconds=statistics.mean(seconds),median_seconds=statistics.median(seconds),mean_final_tokens=statistics.mean(tokens),serialized_bytes=sum(sizes),contexts_file_sha256=sha(path)))
                        save_json(output/(path.stem+'-receipt.json'),cost[-1])
    save_json(output/'cost-e3-r01.json',dict(cells=cost,contexts=2880,index_builds=0,retrieval_calls=0,generation_calls=0,remote_judge_calls=0,scope='Measured assembly only; JSON writing and hashing in cell wall time; no historical retrieval time added; provider usage and monetary cost not applicable.'))

def score(output,map_path,revision):
    mapping=load(map_path);maps={r['intent_id']:r for r in mapping['records']};mh=sha(map_path)
    summary=[];details=[];transitions=[];unknown=[];look={};cost=load(output/'cost-e3-r01.json')
    for path in sorted(output.glob('contexts-*.jsonl')):
        print('score',path.name,flush=True);fh=sha(path);local=[]
        for ctx in rows(path):
            m=maps[ctx['intent_id']];st={}
            for stage in STAGES:
                spans=[s for u in ctx[stage]['units'] for s in u['spans']]
                result=score_context(ctx,m,stage)
                independent={r['requirement_id']:req_status(r,spans,intervals(spans)) for r in m['requirements']}
                assert independent==result['support'] and sufficient(m['groups'],independent)==result['sufficient']
                result.update(configuration_id=ctx['configuration_id'],strategy=ctx['strategy'],budget=ctx['budget'],mapping_sha256=mh,contexts_file_sha256=fh,ranking_file_sha256=ctx['ranking_file_sha256'],visible_text_sha256=ctx[stage]['text_sha256'])
                st[stage]=result;details.append(result)
                if stage=='final' and result['sufficient']=='unknown':
                    unknown.append(dict(**result,visible_spans=spans,context_file=path.relative_to(ROOT).as_posix()))
            local.append(st['final']);look[ctx['configuration_id'],ctx['panel_id'],ctx['strategy'],ctx['budget'],ctx['intent_id']]=st
            for a,b in (('raw','expanded'),('expanded','deduplicated'),('expanded','final')):
                transitions.append(dict(configuration_id=ctx['configuration_id'],panel_id=ctx['panel_id'],strategy=ctx['strategy'],budget=ctx['budget'],intent_id=ctx['intent_id'],comparison=a+'->'+b,before=st[a]['sufficient'],after=st[b]['sufficient'],transition=transition(st[a]['sufficient'],st[b]['sufficient']),context_id=ctx['context_id'],contexts_file_sha256=fh,mapping_sha256=mh))
        first=local[0];summary.append(dict(configuration_id=first['configuration_id'],panel_id=first['panel_id'],strategy=first['strategy'],budget=first['budget'],**aggregate(local)))
    for (config,panel,P,B,i),st in look.items():
        if P=='P0':continue
        a=look[config,panel,'P0',B,i]['final']['sufficient'];b=st['final']['sufficient']
        transitions.append(dict(configuration_id=config,panel_id=panel,strategy=P,budget=B,intent_id=i,comparison='P0_final->'+P+'_final',before=a,after=b,transition=transition(a,b),context_id=st['final']['context_id'],contexts_file_sha256=st['final']['contexts_file_sha256'],mapping_sha256=mh))
    decisions={}
    for config in CONFIGS:
        table=[dict(r,mean_seconds=next(x['mean_seconds'] for x in cost['cells'] if all(x[k]==r[k] for k in ('configuration_id','strategy','budget','panel_id')))) for r in summary if r['configuration_id']==config and r['panel_id']=='fixed_budget_main' and r['budget']==4096]
        decisions[config]=choose_recovery(table)
    save_rows(output/f'score-details-e3-{revision}.jsonl',details)
    save_rows(output/f'transitions-e3-{revision}.jsonl',transitions)
    save_rows(output/f'unknown-e3-{revision}.jsonl',unknown)
    save_json(output/f'scores-e3-{revision}.json',dict(mapping_path=str(map_path),mapping_sha256=mh,summary=summary,decisions=decisions,score_cells=len(details),independent_score_checks=len(details),contexts=2880,independent_intents=80,stage='E3',generation_calls=0))
    print(json.dumps(dict(summary=summary,decisions=decisions),ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['assemble','score']);p.add_argument('--output',type=Path,required=True);p.add_argument('--mapping',type=Path,default=REVIEW/'common-support-map-e1-r07.json');p.add_argument('--revision',default='r07');a=p.parse_args()
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['RAYON_NUM_THREADS']='8'
    if a.stage=='assemble':prepare(a.output.resolve())
    else:score(a.output.resolve(),a.mapping.resolve(),a.revision)

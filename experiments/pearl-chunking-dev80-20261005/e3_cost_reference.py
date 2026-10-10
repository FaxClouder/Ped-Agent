"""Comparable original cold assembly cost on a fixed stratified intent sample."""
import argparse
from pathlib import Path
import os
import random
import statistics
import time
from e3 import SOURCE,REVIEW,CONFIGS,rows,load
from e1_batch import batched_search
from assemble import assemble
from smoke import counter
from runtime import save_json,sha

def run(out):
    maps=load(REVIEW/'common-support-map-e1-r07.json')['records'];strata={}
    for m in maps:strata.setdefault(m['main_stratum'],[]).append(m['intent_id'])
    rng=random.Random(20261005);selected={s:sorted(rng.sample(sorted(ids),min(2,len(ids)))) for s,ids in sorted(strata.items())};ids=sorted(i for group in selected.values() for i in group)
    save_json(out/'cost-reference-sample-e3-r02.json',dict(seed=20261005,strata=selected,intents=ids,policy='2 uniformly sampled intents per main_stratum; fixed before cost execution, no quality selection'))
    c=counter();views=load(SOURCE/'source-views-prepared.json');parents=load(SOURCE/'public-parent-graph.json');records=[]
    with batched_search():
        for config in CONFIGS:
            rp=SOURCE/('index-'+config)/'rankings.jsonl';ranking={r['intent_id']:r for r in rows(rp) if r['intent_id'] in ids}
            for i in ids:
                strategies=['P0','P1','P2'];rng.shuffle(strategies)
                for P in strategies:
                    t=time.perf_counter();ctx=assemble(ranking[i]['results']['R4'],views,parents,P,4096,'fixed_budget_main',c);elapsed=time.perf_counter()-t
                    records.append(dict(configuration_id=config,intent_id=i,strategy=P,seconds=elapsed,context_id=ctx['context_id'],ranking_sha256=sha(rp)))
                print('cost reference',config,i,flush=True)
    summary=[dict(configuration_id=config,strategy=P,n=len(ids),mean_seconds=statistics.mean(r['seconds'] for r in records if r['configuration_id']==config and r['strategy']==P),median_seconds=statistics.median(r['seconds'] for r in records if r['configuration_id']==config and r['strategy']==P)) for config in CONFIGS for P in ('P0','P1','P2')]
    save_json(out/'cost-reference-e3-r02.json',dict(status='passed',records=records,summary=summary,sample_sha256=sha(out/'cost-reference-sample-e3-r02.json'),code_sha256=sha(__file__),scope='Original public assembler, original tokenizer, original batched exhaustive search. No E3 snapshot/search memo or frozen context reuse; shared loaded assets/tokenizer. Random strategy order within fixed paired intents; descriptive sample latency, not full80 end-to-end retrieval time.',rayon_num_threads=6,retrieval_calls=0,generation_calls=0))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();os.environ['RAYON_NUM_THREADS']='6';run(args.output.resolve())

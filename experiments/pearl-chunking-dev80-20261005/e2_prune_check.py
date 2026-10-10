"""Pre-run evidence for the E2 overlap pruning: full pruned pass + seeded original comparison."""
import argparse,json,random,time,math
from pathlib import Path
import e2
from runtime import ROOT,sha,save_json
from smoke import counter
from chunkers import attach_overlap

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--sample',type=int,nargs=2,default=(60,200),help='C2 and C3 sample sizes');a=p.parse_args()
    target=a.output/'e2-pruning-equivalence-r01.json'
    if target.exists():raise FileExistsError(target)
    c=counter();views={v['doc_id']:v for v in json.loads((e2.E0/'source-views-prepared.json').read_text('utf8'))};res={}
    for config,(base,r) in e2.CONFIGS.items():
        C,L=e2.BASES[base];rows=e2.base_children(base);t=time.perf_counter()
        e2.PRUNE_STATS.update(candidates=0,exactly_counted=0)
        out=[e2.attach_overlap_batched(ch,r,L,views[ch['doc_id']],c) for ch in rows];pruned_s=time.perf_counter()-t;stats=dict(e2.PRUNE_STATS)
        n=a.sample[0] if C=='C2' else a.sample[1];idx=sorted(random.Random(20261006).sample(range(len(rows)),n));t=time.perf_counter();mism=[]
        for i in idx:
            if out[i]!=attach_overlap(rows[i],r,L,views[rows[i]['doc_id']],c):mism.append(rows[i]['chunk_id'])
        res[config]=dict(children=len(rows),attached=sum(bool(o['overlap_spans']) for o in out),pruned_pass_seconds=pruned_s,candidates=stats['candidates'],exactly_counted=stats['exactly_counted'],original_comparison=dict(sample=n,seed=20261006,mismatches=mism,seconds=time.perf_counter()-t),limit_tokens=math.floor(r*L))
        print(config,json.dumps(res[config]),flush=True)
        if mism:raise SystemExit('pruned overlap differs from chunkers.attach_overlap: '+config)
    save_json(target,dict(status='passed',e2_sha256=sha(Path(e2.__file__)),checker_sha256=sha(Path(__file__)),configs=res,note='Full pruned pass over all E1 core children; seeded sample compared field-for-field with the original chunkers.attach_overlap.'))
    print('saved',target,flush=True)

if __name__=='__main__':main()

"""Intent-cluster bootstrap preserving all five arms and fixed eligibility."""
import numpy as np

PAIRS=[('A1-4096','A0-4096'),('A1-8192','A0-8192'),('A0-8192','A0-4096'),('A1-8192','A1-4096'),('Aref-8192','A1-8192')]

def paired_bootstrap(rows,iterations=10000,seed=20261004):
    cells={(r['intent_id'],r['arm']):r for r in rows}
    ids=sorted({r['intent_id'] for r in rows}); strata={i:next(r['stratum'] for r in rows if r['intent_id']==i) for i in ids}
    groups={s:[i for i in ids if strata[i]==s] for s in sorted(set(strata.values()))}
    rng=np.random.default_rng(seed)
    # Draw the entire intent panel, and retain a fixed jointly applicable set per pair.
    draws=[np.concatenate([rng.choice(g,len(g),replace=True) for g in groups.values()]) for _ in range(iterations)]
    results=[]
    for a,b in PAIRS:
        for metric in ('faithfulness','unsupported_rate','context_contradiction_rate','factuality'):
            common={i for i in ids if cells[i,a][metric][0] is not None and cells[i,b][metric][0] is not None}
            record=dict(pair=f'{a} - {b}',metric=metric,common_N=len(common),left_NA=sum(cells[i,a][metric][0] is None for i in ids),right_NA=sum(cells[i,b][metric][0] is None for i in ids),iterations=iterations,seed=seed,stratified_by_intent=True)
            for j,name in enumerate(('lower','upper')):
                diff={i:cells[i,a][metric][j]-cells[i,b][metric][1-j] for i in common}
                vals=[np.mean([diff[i] for i in draw if i in common]) for draw in draws if any(i in common for i in draw)]
                record[name]=dict(difference=float(np.mean(list(diff.values()))) if common else None,ci95=[float(x) for x in np.percentile(vals,[2.5,97.5],method='linear')] if vals else [None,None])
            results.append(record)
    return dict(schema_version='pearl-layer4-paired-bootstrap-v1',results=results,citation_and_rejection='descriptive separate coverage; not ranked by unknown filtering',posthoc_significance_tests=False)

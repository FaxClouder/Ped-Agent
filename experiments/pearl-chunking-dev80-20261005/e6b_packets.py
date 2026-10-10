"""Session 6B blind research packets for the 720 E5 answers (offline; assigns no labels).

Layer 3: query + anonymous answer + frozen semantic reference (no context, configuration or score).
Layer 4: answerability (query, actual 4K context, fixed requirements), grounding/citation (query,
context, raw_answer, position-preserving candidates), behavior (query, context, raw_answer,
requirements). Factuality packets need the selected grounding claims and are exported later.
Exact-duplicate rule (5B frozen): a packet byte-identical in its inputs is judged once and bound to
every cell that uses it; answerability inputs contain no answer, so the three replicates of a
(configuration, intent) share one packet. Blind order: random.Random(20261005) shuffle.
Secondary fixed sample (frozen before labels): every fifth cell of the shuffled 720-cell order,
per layer/task (144 cells each; Layer 3 144, Layer 4 4 x 144 = 576).
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import random
from pathlib import Path
from runtime import ROOT, sha, save_json, cache_identity

S6A=ROOT/'outputs/pearl-chunking-dev80-20261006-14'
OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-15'
REFS=ROOT/'outputs/pearl-answer-dev80-20261004-01/reference-freeze-r01.json'
FACTS=ROOT/'outputs/pearl-layer4-dev80-20261004-01/facts/facts-r03.json'
L4CAL=ROOT/'outputs/pearl-layer4-dev80-20261004-01/calibration/judge-packets'
SEED=20261005


def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def cells():
    contexts={(r['arm'],r['intent_id']):r for r in map(json.loads,(S6A/'e5-cells-r01.jsonl').read_text(encoding='utf8').splitlines())}
    rows=[]
    for p in sorted((S6A/'generation').glob('*.json')):
        g=load(p);c=contexts[(g['arm'],g['intent_id'])]
        if c['context_sha256']!=g['context_sha256'] or sha_text(c['context'])!=g['context_sha256']:raise ValueError('context binding')
        if sha_text(g['raw_answer'])!=g['response_sha256']:raise ValueError('answer binding')
        rows.append({'cell_id':g['cell_id'],'arm':g['arm'],'intent_id':g['intent_id'],'replicate':int(g['cell_id'].rsplit('rep',1)[1]),
                     'query':g['query'],'raw_answer':g['raw_answer'],'response_sha256':g['response_sha256'],'context':c['context'],
                     'context_sha256':g['context_sha256'],'record_path':p.relative_to(ROOT).as_posix(),'record_sha256':sha(p)})
    if len(rows)!=720:raise ValueError('expected 720 cells')
    return rows


def sha_text(s):
    import hashlib;return hashlib.sha256(s.encode('utf8')).hexdigest()


def build():
    review=module('l3review',ROOT/'experiments/pearl-answer-dev80-20261004/review.py')
    extract=module('l4extract',ROOT/'experiments/pearl-layer4-dev80-20261004/extract.py')
    refs={r['intent_id']:r for r in load(REFS)['rows']};facts={x['intent_id']:x for x in load(FACTS)['items']}
    instruction={t:load(L4CAL/t/'cal-01.json')['instruction'] for t in ('answerability','grounding','behavior','factuality')}
    rows=cells();order=list(rows);random.Random(SEED).shuffle(order)
    packets={'layer3':{},'answerability':{},'grounding':{},'behavior':{}};bindings={k:{} for k in packets}
    def add(task,key,make,cell):
        if key not in bindings[task]:
            blind=f'{task if task!="layer3" else "answer"}-{len(bindings[task])+1:04d}'
            packets[task][blind]=make(blind);bindings[task][key]={'blind_id':blind,'cells':[]}
        bindings[task][key]['cells'].append(cell['cell_id'])
    for c in order:
        ref=refs[c['intent_id']];fact=facts[c['intent_id']]
        semantic={k:v for k,v in ref.items() if k in review.SEMANTIC_REFERENCE_FIELDS}
        add('layer3',(c['query'],c['context_sha256'],c['response_sha256']),
            lambda b:{'packet_id':b,'query':c['query'],'answer':c['raw_answer'],'reference':review._clean_reference(semantic),'rubric_version':'r01'},c)
        reqs={'task':c['query'],'necessary_conclusions':fact['requirements'],'necessary_groups':fact['necessary_groups']}
        add('answerability',(c['query'],c['context_sha256']),
            lambda b:{'anchor_id':b,'query':c['query'],'context':c['context'],'context_sha256':c['context_sha256'],'requirements':reqs,'instruction':instruction['answerability']},c)
        cand=extract.extract_answer(c['raw_answer'])
        claims=[{'claim_id':f'c{i+1}','text':x['quote'],'occurrences':[[x['start'],x['end']]]} for i,x in enumerate(cand['candidates'])]
        add('grounding',(c['query'],c['context_sha256'],c['response_sha256']),
            lambda b:{'anchor_id':b,'query':c['query'],'context':c['context'],'context_sha256':c['context_sha256'],'raw_answer':c['raw_answer'],
                      'response_sha256':c['response_sha256'],'claims_candidates':claims,'instruction':instruction['grounding']},c)
        add('behavior',(c['query'],c['context_sha256'],c['response_sha256']),
            lambda b:{'anchor_id':b,'query':c['query'],'raw_answer':c['raw_answer'],'response_sha256':c['response_sha256'],'context':c['context'],
                      'context_sha256':c['context_sha256'],'requirements':reqs,'instruction':instruction['behavior']},c)
    secondary={t:[c['cell_id'] for c in order[::5]] for t in ('layer3','answerability','grounding','factuality','behavior')}
    cell_to_packet={t:{cid:b['blind_id'] for b in bindings[t].values() for cid in b['cells']} for t in bindings}
    forbidden={'cell_id','intent_id','arm','config_id','model','score','strict','l2_sufficient','replicate'}
    for t,ps in packets.items():
        for p in ps.values():
            if set(p)&forbidden:raise ValueError('identity leak')
    return rows,order,packets,bindings,secondary,cell_to_packet


def write(revision):
    d=OUT/f'research-packets-{revision}'
    if d.exists():raise FileExistsError(d)
    rows,order,packets,bindings,secondary,c2p=build()
    for t,ps in packets.items():
        (d/t).mkdir(parents=True)
        for b,p in ps.items():
            with (d/t/f'{b}.json').open('x',encoding='utf8',newline='\n') as f:json.dump(p,f,ensure_ascii=False,indent=1)
    mapping={'schema_version':'pearl-e6b-identity-map-v1','note':'evaluation-side only; never sent to the judge',
             'seed':SEED,'blind_cell_order':[c['cell_id'] for c in order],
             'cells':{c['cell_id']:{k:c[k] for k in ('arm','intent_id','replicate','response_sha256','context_sha256','record_path','record_sha256')} for c in rows},
             'bindings':{t:[{'blind_id':v['blind_id'],'cells':v['cells'],'packet_sha256':sha(d/t/f'{v["blind_id"]}.json')} for v in b.values()] for t,b in bindings.items()},
             'cell_to_packet':c2p}
    save_json(OUT/f'research-identity-map-{revision}.json',mapping)
    sec={'schema_version':'pearl-e6b-secondary-sample-v1','status':'frozen_before_research_labels','rule':'every fifth cell of the seed-20261005 shuffled 720-cell order, per layer/task',
         'cells':secondary,'unique_packets':{t:sorted({c2p[t if t in c2p else 'grounding'][x] for x in v}) for t,v in secondary.items() if t!='factuality'},
         'factuality_note':'factuality secondary packets are exported after primary grounding selection, for the same fixed cells',
         'units_cap':{'layer3_secondary':144,'layer4_secondary':576}}
    save_json(OUT/f'secondary-sample-{revision}.json',sec)
    counts={t:len(p) for t,p in packets.items()}
    print(json.dumps({'packets':counts,'cells':len(rows),'secondary_unique':{t:len(v) for t,v in sec['unique_packets'].items()}}))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--revision',default='r01');a=ap.parse_args();write(a.revision)

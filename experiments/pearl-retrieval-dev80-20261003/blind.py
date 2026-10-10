"""Create content-only support-review packets from immutable first-pass rankings."""
from pathlib import Path
import argparse
import random
import json
from prepare import ROOT, INDEX, GOLD, sha, read, rows, write

FORBIDDEN={'method','rank','score','r3_rank','r1_rank','r2_rank','sqlite_rank','in_top100','parent_chunk_id'}
CHILD_FIELDS=('chunk_id','text','text_sha256','source_id','source_sha256','title','page_start','page_end','locator','parser_version')
INTENT_FIELDS=('intent_id','query','reference_answer','requirements','atoms','evidence_groups')

def assert_blind(v):
    if isinstance(v,dict):
        if set(v)&FORBIDDEN:raise ValueError('method/ranking context in blind packet')
        for x in v.values():assert_blind(x)
    elif isinstance(v,list):
        for x in v:assert_blind(x)

def packet(q,candidates,supplement):
    clean=lambda c:{k:c[k] for k in CHILD_FIELDS if k in c}
    p={'intent':{k:q[k] for k in INTENT_FIELDS if k in q},
       'candidates':[clean(c) for c in candidates],
       'supplementary_candidates':[clean(c) for c in supplement]}
    assert_blind(p);return p

def generate(directory, complete_only=False):
    rank=rows(directory/'rankings.jsonl')
    gold=read(GOLD);children={c['chunk_id']:c for c in rows(INDEX/'child_chunks.jsonl')}
    grouped={q['intent_id']:[] for q in gold['intents']}
    for r in rank:
        if r['intent_id'] not in grouped:raise ValueError('unknown query')
        grouped[r['intent_id']].append(r)
    packets=directory/'review/packets';decisions=directory/'review/decisions'
    packets.mkdir(parents=True,exist_ok=True);decisions.mkdir(exist_ok=True)
    manifest=[]
    for q in gold['intents']:
        rs=grouped[q['intent_id']]
        if len(rs)!=4:
            if complete_only:continue
            raise ValueError('missing four-method ranking')
        if {r['method'] for r in rs}!={'R1','R2','R3','R4'}:raise ValueError('duplicate method')
        core={c['chunk_id'] for r in rs for c in r['results'][:20]}
        pool={c['chunk_id'] for r in rs for c in r['results']}
        sources={a['source_id'] for a in q['atoms']}
        pool|={cid for cid,c in children.items() if c['source_id'] in sources}
        # Core membership is retained privately for validation, never labeled by origin in packets.
        rng=random.Random(20260929+int(q['intent_id'][-3:]))
        cs=[children[c] for c in sorted(core)];ss=[children[c] for c in sorted(pool-core)]
        rng.shuffle(cs);rng.shuffle(ss)
        p=packet(q,cs,ss);path=packets/(q['intent_id']+'.json')
        if path.exists():
            if read(path)!=p:raise ValueError('existing packet differs')
        else:write(path,p)
        manifest.append({'intent_id':q['intent_id'],'path':str(path.relative_to(directory)),
                         'packet_sha256':sha(path),'candidate_count':len(cs),'supplementary_count':len(ss)})
    mp=directory/'review/packet-manifest.json'
    if not complete_only:
        write(mp,{'gold_sha256':sha(GOLD),'rankings_sha256':sha(directory/'rankings.jsonl'),
                  'blind_generator_sha256':sha(Path(__file__)),'packets':manifest})
    print(json.dumps({'packets':len(manifest),'core_candidates':sum(x['candidate_count'] for x in manifest),
                      'supplementary':sum(x['supplementary_count'] for x in manifest)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--complete-only',action='store_true')
    a=p.parse_args();generate(a.directory.resolve(),a.complete_only)

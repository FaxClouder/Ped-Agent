"""Independent interval subtraction and ranked budget-prefix ordering check."""
import argparse
from pathlib import Path
from e3 import SOURCE,rows,load
from e1_visible_review_verify import intervals,k
from assemble import unit,views_by_id,prefix_unit,serialize
from smoke import counter
from runtime import sha,save_json

def verify(out):
    vs=views_by_id(load(SOURCE/'source-views-prepared.json'));c=counter();n=0
    for path in sorted(out.glob('contexts-*.jsonl')):
        for ctx in rows(path):
            seen={};expected=[]
            for u in ctx['expanded']['units']:
                residual=[]
                for s in u['spans']:
                    pieces=[(s['start'],s['end'])]
                    for a,b in seen.get(k(s),[]):
                        next_pieces=[]
                        for x,y in pieces:
                            if y<=a or b<=x:next_pieces.append((x,y))
                            else:
                                if x<a:next_pieces.append((x,a))
                                if b<y:next_pieces.append((b,y))
                        pieces=next_pieces
                    residual.extend(dict(s,start=x,end=y) for x,y in pieces)
                if residual:expected.append(unit(residual,vs,u['seed_chunk_id'],u['rank']))
                combined=[dict(doc_id=key[0],source_version=key[1],element_id=key[2],start=a,end=b) for key,values in seen.items() for a,b in values]+u['spans']
                seen=intervals(combined)
            assert expected==ctx['deduplicated']['units']
            final=ctx['final']['units'];assert len(final)<=len(expected)
            for j,u in enumerate(final):
                original=expected[j]
                if u['truncated']:
                    assert j==len(final)-1 and u==prefix_unit(original,len(u['text']),vs)
                else:assert u==original
            if not ctx['truncation']:assert final==expected
            else:
                stop=ctx['truncation'][0];stop_unit=next(u for u in expected if u['seed_chunk_id']==stop['seed_chunk_id'])
                kept=[u for u in final if u['rank']<stop_unit['rank']]
                assert c.count(serialize(kept+[stop_unit]))>ctx['budget']
                retained=next((u for u in final if u['rank']==stop_unit['rank']),None)
                assert stop['retained_characters']==(len(retained['text']) if retained else 0)
            n+=1
    assert n==2880
    save_json(out/'rank-order-verification-r01.json',dict(status='passed',contexts=n,independent_source_subtraction='interval subtract with explicit disjoint branches; compared full dedup units',ranking_first_occurrence_attribution='all units',final_prefix_order='all contexts; full units followed by at most one legal source prefix',overflow='full stop unit over budget for every truncated context',maximality='separately sampled original exhaustive search in assembly-verification-r01.json',code_sha256=sha(__file__)))
    print('Rank/source budget order passed',n,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();verify(a.output.resolve())

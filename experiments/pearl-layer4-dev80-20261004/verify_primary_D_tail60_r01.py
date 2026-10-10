"""Mechanical evidence/identity check for this actual authored60 review batch only."""
import json,hashlib,collections,re
from pathlib import Path
from citations_D_r01 import source_spans
R=Path('outputs/pearl-layer4-dev80-20261004-01')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def span(text,e):assert text[e['start']:e['end']]==e['quote'] and e['end']>e['start']
rows=[];count=collections.Counter()
for i in range(241,301):
 gp=R/'packets/grounding-D300-r02'/f'grounding-{i:04d}.json';bp=R/'packets/behavior-D300-r02'/f'behavior-{i:04d}.json'
 gr=R/'reviews/primary'/('grounding-D300-supplement-r01' if i in (245,298,299) else 'grounding-D300-r02')/f'grounding-{i:04d}.json'
 br=R/'reviews/primary/behavior-D300-tail60-canonical-r03'/f'behavior-{i:04d}.json'
 x=read(gp);b=read(bp);g=read(gr);v=read(br);assert x['context']==b['context'] and x['raw_answer']==b['raw_answer']
 assert g['blind_id']==x['blind_id'] and v['blind_id']==b['blind_id']
 assert g['provenance']['packet_sha256']==sha(gp) and v['provenance']['packet_sha256']==sha(bp)
 assert hashlib.sha256(x['raw_answer'].encode()).hexdigest()==x['response_sha256'];assert hashlib.sha256(x['context'].encode()).hexdigest()==x['context_sha256']
 windows=source_spans(x['context']);ids=set()
 def ev(e):
  span(x['context'],e);assert any(w['source_label']==e['source_label'] and w['start']<=e['start']<e['end']<=w['end'] for w in windows)
 for c in g['claims']:
  assert c['claim_id'] not in ids;ids.add(c['claim_id']);span(x['raw_answer'],c)
  for o in c['occurrences']:span(x['raw_answer'],o)
  assert c['grounding']['label'] in ('supported','partial','unsupported','contradicted','unknown')
  if c['grounding']['label'] in ('supported','partial','contradicted'):assert c['grounding']['evidence']
  for e in c['grounding']['evidence']:ev(e)
 for q in g['citation_pairs']:
  assert q['claim_id'] in ids;assert x['raw_answer'][q['citation_start']:q['citation_end']]==q['citation_quote']
  for e in q['evidence']:
   ev(e)
   if q.get('citation_page') is None:assert q['citation_source_id'] in e['source_label']
   else:assert e['source_label']==q['source_label']
 assert type(v['unsupported_completion']) is bool and type(v['abstain']) is bool
 assert v['reason']['label'] in ('correct','incorrect','unknown','na')
 assert v['behavior'] in ('full_answer','bounded_partial','pure_abstention','ambiguous')
 if v['behavior']=='full_answer':assert v['reason']['label']=='na' and not v['abstain']
 for e in v['behavior_evidence']:span(x['raw_answer'],e)
 count['grounding_reviews']+=1;count['behavior_reviews']+=1;count['claims']+=len(g['claims']);count['citation_pairs']+=len(g['citation_pairs']);count[v['behavior']]+=1;count['unsupported_completion']+=v['unsupported_completion']
 rows.append({'number':i,'grounding':{'path':str(gr),'sha256':sha(gr),'packet_path':str(gp),'packet_sha256':sha(gp)},'behavior':{'path':str(br),'sha256':sha(br),'packet_path':str(bp),'packet_sha256':sha(bp)},'pending_revisions':False})
out={'status':'current','task':'D241-300 primary grounding and behavior only','counts':dict(count),'rows':rows,'verification':'All60 actual saved JSON reopened; packet/text hashes, claim/occurrence/citation/evidence exact intervals, context source windows, same source citation evidence and canonical booleans checked. Semantic sourcefacts and final scores not read or generated.'}
p=R/'primary-D300-tail60-selection-r01.json'
with p.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps(out['counts'],ensure_ascii=False));print(p)

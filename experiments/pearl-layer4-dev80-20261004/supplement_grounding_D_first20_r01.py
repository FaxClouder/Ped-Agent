"""Actual reread corrections; preserve original review and bind it by SHA."""
import json,hashlib
from grounding_inspect_D_r01 import ROOT,packet,candidates
from grounding_write_D_r01 import locate
from citations_D_r01 import textual_pairs
BASE=ROOT/'reviews/primary/grounding-D300-r02'
OUT=ROOT/'reviews/primary/grounding-D300-supplement-r01'
OUT.mkdir(exist_ok=True)
for i in (1,2,3,4,5,6,7,11,15,18):
 p=BASE/f'grounding-{i:04}.json';r=json.loads(p.read_text('utf-8'));x=packet(i);cs=candidates(x)
 dup={3:{7:[12,13,14],16:[7,12,13,14],17:[18,23,28]},6:{2:[1,2]},7:{8:[1,10]}}.get(i,{})
 for idx,targets in dup.items():
  c=cs[idx-1]
  for t in targets:
   r['claims'][t-1]['occurrences'].append({k:c[k] for k in ('start','end','quote')})
 if i==2:
  r['claims'][0]['grounding']['evidence']+=locate(x['context'],[r'characteristic density.{0,80}2\.5'])
 if i in(11,15):
  targets=(4,5) if i==11 else (6,7)
  patterns=[r'proportion of velocities below 0\.5 ms−1.{0,140}volunteers never stop',r'volunteers never stop.{0,180}prescribed safety distance']
  for target,pat in zip(targets,patterns):
   c=r['claims'][target-1];ev=locate(x['context'],[pat])
   assert ev
   c['grounding']={'label':'supported','evidence':ev,'reason':'补读可见完整段明确低于0.5m/s的比例指标、fast volunteers never stop，以及其可能解释违距次数增加。'}
 if i==18:
  c=r['claims'][6];ev=locate(x['context'],[r'there is no upward or downward trend over extended periods of time'])
  assert ev
  c['grounding']={'label':'supported','evidence':ev,'reason':'补读段明确写无长时间上升/下降趋势，与完整原子一致。'}
 r['citation_pairs']=textual_pairs(x['raw_answer'],r['claims'],x['context'])
 if i==2:
  for pair in r['citation_pairs']:
   if pair['claim_id']=='c001' and pair['citation_page']=='12-14':
    pair['label']='partial';pair['reason']='该页数值2.5可见，但m负指数文字损坏；整体G单位来自另页，不回填该引用。'
 if i==3:
  for pair in r['citation_pairs']:
   if pair['claim_id']=='c006' and pair['citation_page']=='1':
    pair['label']='unsupported';pair['evidence']=[];pair['reason']='实际p1摘要仅举消防人员与emergency managers以及other similar scenarios；未断言其他responders相对于normal evacuees的具体方向，此断言在p1-2而非所引p1。'
 r['provenance']['origin_review_path']=str(p);r['provenance']['origin_review_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 r['provenance']['supplement_reason']='新独立版本修补i.e.句点引用定位与同义复述occurrences；11/15/18补读明确完整段后改判；原件保留。'
 with(OUT/f'grounding-{i:04}.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
 print(i,len(r['claims']),len(r['citation_pairs']))

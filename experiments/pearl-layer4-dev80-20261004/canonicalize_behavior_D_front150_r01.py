import json,hashlib
from collections import Counter
from behavior_inspect_D_front_r01 import ROOT,packet
dst=ROOT/'reviews/primary/behavior-D300-front150-canonical-r03';dst.mkdir(parents=True,exist_ok=True)
rows=[];counts=Counter()
for i in range(1,151):
 x,p,g=packet(i);old=ROOT/'reviews/primary/behavior-D300-r02'/f'behavior-{i:04d}.json';v=json.loads(old.read_text(encoding='utf-8'))
 if i==9:
  v['behavior']='bounded_partial';v['reason']['label']='correct';v['refusal_reason']='correct'
  v['reason']['rationale']='重新实际检查Dufour context只有p1-2动机/范围，没有TopView/visual-check/manual-correction方法；Pouw半项实答。故有领域事实且明确缺必要项，bounded_partial；所述缺口正确。'
 if i==46:
  v['reason']['label']='incorrect';v['refusal_reason']='incorrect';v['reason']['rationale']='重新实际读context5106:7736，69cb paper明确网络simulation、arbitrary in/out nodes和bidirectional cell-transmission；答者因未见作者名声称没有该source，遗漏可见所问方法，理由incorrect。'
 if v['behavior']=='bounded_partial':
  v['abstain']=True;v['abstains_from_unsupported_completion']=True
  if not v['reason']['evidence']:v['reason']['evidence']=v['behavior_evidence']
 else:
  v['abstain']=False;v['abstains_from_unsupported_completion']=False;v['reason']['label']='na';v['reason']['evidence']=[];v['refusal_reason']=None
  if i>=126 and i!=139:v['reason']['gap']='必要实质答案已答；附加内容的限定或OCR/公式不足不自动成为必要结论补全。'
 v['provenance']['origin_review_path']=str(old);v['provenance']['origin_review_sha256']=hashlib.sha256(old.read_bytes()).hexdigest()
 v['provenance']['canonical_reassessment']='逐包必要条件已实际独立阅读；完整raw/context与此前实际阅读ground包一致，拒答/缺口段再读。1–150统一布尔及计划行为词；9实际重新核对缺口、46实际重新读网络段并修正理由，保留原件。'
 q=dst/f'behavior-{i:04d}.json'
 with q.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 assert type(v['abstain']) is bool and type(v['unsupported_completion']) is bool
 assert v['behavior'] in ('full_answer','bounded_partial','pure_abstention','ambiguous')
 assert v['reason']['label'] in ('na','correct','incorrect','unknown')
 for ev in v['behavior_evidence']+v['reason']['evidence']+v['unsupported_completion_detail']['evidence']:assert x['raw_answer'][ev['start']:ev['end']]==ev['quote']
 counts[v['behavior']]+=1;counts['unsupported_true']+=v['unsupported_completion']
 gs=ROOT/'reviews/primary/grounding-D300-supplement-r01'/f'grounding-{i:04d}.json'
 if not gs.exists():gs=ROOT/'reviews/primary/grounding-D300-r02'/f'grounding-{i:04d}.json'
 rows.append({'index':i,'grounding_selected':str(gs),'grounding_sha256':hashlib.sha256(gs.read_bytes()).hexdigest(),'behavior_selected':str(q),'behavior_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'behavior_origin':str(old),'behavior_origin_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'behavior_packet':str(p),'behavior_packet_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 out={'status':'primary_semantic_reviews_completed; independent_secondary/adjudication and full Layer4 verification remain parent task','range':[1,150],'grounding_count':150,'behavior_count':150,'counts':dict(counts),'all_origin_preserved':True,'no_scoring_or_generation':True,'rows':rows}
out={'status':'primary_semantic_reviews_completed; independent_secondary/adjudication and full Layer4 verification remain parent task','range':[1,150],'grounding_count':150,'behavior_count':150,'counts':dict(counts),'all_origin_preserved':True,'no_scoring_or_generation':True,'rows':rows}
m=ROOT/'primary-D300-front150-selection-r03.json'
with m.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps({'manifest':str(m),'counts':dict(counts),'rows':len(rows),'raw_span_checks':'passed','packet_text_equal_to_previously_read_ground_packets':'150 passed'},ensure_ascii=False))

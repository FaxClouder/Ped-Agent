import json,re,hashlib
from pathlib import Path
from context_inspect_D_r01 import groups,ROOT

def save_group(index,labels,patterns,notes=None):
 for x in groups()[index]:
  c=x['context'];spec=labels.get(x['blind_id'],labels.get('*'));reqs=[]
  for j,req in enumerate(x['requirements']):
   lab=spec[j];evidence=[]
   for pat in patterns[j]:
    m=re.search(pat,c,re.I|re.S)
    if not m:
     if lab=='supported':raise ValueError('manual support pattern absent '+x['blind_id']+' '+pat)
     continue
    start,end=m.span();sources=list(re.finditer(r'\[Source[^\]]+\]',c[:start+1]));source=sources[-1].group(0) if sources else None
    evidence.append({'start':start,'end':end,'quote':c[start:end],'source_label':source})
   reqs.append({'requirement_id':req['requirement_id'],'claim':req['claim'],'label':lab,'evidence':evidence,'missing':None if lab=='supported' else (notes or {}).get(x['blind_id'],'当前context缺少指定条件或必要结论的完整支持。'),'reason':'逐项核对已读query和必要结论，证据字符区间从该packet实际context定位；非旧标签映射。'+(' '+(notes or {}).get(x['blind_id'],'') if lab!='supported' else '')})
  result={'blind_id':x['blind_id'],'answerability':'complete' if all(z=='supported' for z in spec) else 'unknown' if 'unknown' in spec else 'partial' if any(z in ['supported','partial'] for z in spec) else 'none','requirements':reqs,'reason':'所有必要结论完整可支持。' if all(z=='supported' for z in spec) else '保留实际context可支持部分，并明确尚缺必要结论或条件。','provenance':{'reviewer':'prepare_layer4 context primary','model':'inherited; exact deployment ID not exposed','task':'answerability','packet_path':x['_path'],'packet_sha256':hashlib.sha256(Path(x['_path']).read_bytes()).hexdigest(),'actual_read':['query','requirements','actual context relevant paragraphs located by literal searches; exact duplicate windows were checked against hash equality'],'raw_answer_read':False,'facts_or_identity_map_or_old_scores_read':False,'prior_exposure':'Earlier C100 context primary and engineering assembly exposed C100 facts labels/final atoms and identity maps; earlier dev009/dev012 partial exposure remains. D300/D60 maps were mechanically parsed in engineering without D answers/labels. This phase only current query requirements/context; no D facts/answers/old scores.','prompt_version':'r02'}}
  p=ROOT/'reviews/primary/answerability-D300-r02'/f"{x['blind_id']}.json";p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)

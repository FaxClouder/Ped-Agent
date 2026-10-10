"""Position-preserving candidates only; semantic completeness requires review."""
import hashlib,json,re
from pathlib import Path

def extract_answer(answer):
 candidates=[]
 for m in re.finditer(r'[^\n.!?]+(?:[.!?](?!\d)|$)',answer):
  start,end=m.span()
  while start<end and answer[start].isspace(): start+=1
  while end>start and answer[end-1].isspace(): end-=1
  if start==end: continue
  candidates.append({'candidate_id':f'candidate-{len(candidates)+1:03d}','start':start,'end':end,'quote':answer[start:end],'status':'semantic_review_pending','normalized_claim':None,'conditions':None})
 citations=[{'citation_id':f'citation-{i+1:03d}','start':m.start(),'end':m.end(),'quote':m.group(0),'scope':'review_pending'} for i,m in enumerate(re.finditer(r'\[(?:Source\s+)?[^\]\n]*(?:pearl-src-|Source\s+)[^\]\n]*\]|\[Source[^\]\n]+\]',answer))]
 return {'raw_answer_sha256':hashlib.sha256(answer.encode('utf-8')).hexdigest(),'candidates':candidates,'citations':citations,'extraction_status':'candidate_only_complete_semantic_review_required'}
def extract_packets(inputs:list[dict],out:Path)->dict:
 out=Path(out); out.mkdir(parents=True,exist_ok=True)
 for row in inputs:
  p=out/(row['cell_id'].replace('::','--')+'.json')
  with p.open('x',encoding='utf-8') as f: json.dump(extract_answer(row['raw_answer']),f,ensure_ascii=False,indent=2)
 return {'packets':len(inputs),'semantic_labels_assigned':False}

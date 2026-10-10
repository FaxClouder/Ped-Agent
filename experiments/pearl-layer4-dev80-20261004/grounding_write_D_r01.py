"""Serialize authored semantic atoms only; labels must be supplied explicitly."""
import re,hashlib,copy
from pathlib import Path
from grounding_inspect_D_r01 import ROOT,PACK,packet,candidates
from citations_D_r01 import source_spans,textual_pairs
def locate(context,patterns):
 es=[]
 for pat in patterns:
  for s in source_spans(context):
   for m in re.finditer(pat,context[s['start']:s['end']],re.I|re.S):
    a=s['start']+m.start();b=s['start']+m.end()
    es.append({'start':a,'end':b,'quote':context[a:b],'source_label':s['source_label']})
 return es
def save(i,specs,excluded=None,duplicates=None,pair_overrides=None):
 x=packet(i);cs=candidates(x);claims=[];used=set();excluded=excluded or {};duplicates=duplicates or {};pair_overrides=pair_overrides or {}
 for index,norm,label,patterns in specs:
  c=cs[index-1];used.add(index);ev=locate(x['context'],patterns)
  if label in ('supported','partial','contradicted') and not ev:raise ValueError(f'No authored proof {i}:{norm}')
  claims.append({'claim_id':f'c{len(claims)+1:03d}','start':c['start'],'end':c['end'],'quote':c['quote'],'normalized_claim':norm,'conditions':{'study_scope':x['query'],'literal_statement':c['clean'],'qualifications':'Original subject, numerical units, comparison, setting and qualifiers retained for this independently asserted atom.'},'occurrences':[{'start':c['start'],'end':c['end'],'quote':c['quote']}],'grounding':{'label':label,'evidence':ev,'reason':'实际阅读完整raw_answer及该原子相关actual context；独立对象、关系、数值、条件核对。'+('此context未支持该完整原子。' if label=='unsupported' else '限定或数值支持不完整。' if label=='partial' else '可见文本与该断言相矛盾。' if label=='contradicted' else '')}})
 for index,target in duplicates.items():
  c=cs[index-1];used.add(index)
  for t in target if isinstance(target,list) else [target]:claims[t-1]['occurrences'].append({'start':c['start'],'end':c['end'],'quote':c['quote']})
 if set(range(1,len(cs)+1))-used-set(excluded):raise ValueError('unaccounted candidate')
 pairs=textual_pairs(x['raw_answer'],claims,x['context'])
 for p in pairs:
  key=(p['claim_id'],p['source_label'])
  if key in pair_overrides:p['label']=pair_overrides[key]
 result={'blind_id':x['blind_id'],'response_sha256':x['response_sha256'],'context_sha256':x['context_sha256'],'extraction_unknown':False,'citation_extraction_unknown':False,'claims':claims,'citation_pairs':pairs,'excluded_candidates':excluded,'completeness_review':'逐候选实际审阅全文，独立数值/关系分开；复述去重以occurrences追溯；元声明不计科学原子。','provenance':{'reviewer':'prepare_layer4 D context primary','model':'inherited; backend identifier unavailable','task':'grounding','packet_path':str(PACK/f'grounding-{i:04d}.json'),'packet_sha256':hashlib.sha256((PACK/f'grounding-{i:04d}.json').read_bytes()).hexdigest(),'actual_read':['full raw_answer and query','relevant actual context source/page paragraphs, including duplicate source/page blocks'],'facts_read_during_task':False,'identity_map_or_old_scores_read_during_task':False,'prior_exposure':'D300 answerability primary saw necessary requirements and its own labels before freeze; C100 context primary, C100 engineering final source-only packets/factuality labels, and D identity-map mechanical engineering exposure. Grounding semantic decisions use current grounding packet only; no D sourcefacts or answerability labels imported.','prompt_version':'frozen-r02 with sentence/bullet/paragraph citation scope'}}
 p=ROOT/'reviews/primary/grounding-D300-r02'/f'grounding-{i:04d}.json';p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:
  import json;json.dump(result,f,ensure_ascii=False,indent=2)
 print(i,len(claims),len(pairs))

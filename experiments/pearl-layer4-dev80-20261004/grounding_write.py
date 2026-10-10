"""Serialize the primary agent's explicit, read-based claim decisions; no semantic classifier."""
import json,re,hashlib
from pathlib import Path
from grounding_inspect import ROOT,PACK,CITE,packet,candidates

def sources(c):
 ms=list(re.finditer(r'\[Source[^\]]+\]',c));return [(m.group(0),m.start(),ms[i+1].start() if i+1<len(ms) else len(c)) for i,m in enumerate(ms)]
def evidence(c,patterns):
 es=[]
 for pattern in patterns if isinstance(patterns,list) else [patterns]:
  if not pattern:continue
  matches=list(re.finditer(pattern,c,re.I|re.S))
  if not matches:raise ValueError('evidence pattern absent '+pattern)
  # Search source blocks separately so an earlier truncated duplicate cannot consume a later complete match.
  for label,start,end in sources(c):
   for m in re.finditer(pattern,c[start:end],re.I|re.S):
    es.append({'quote':m.group(0),'start':start+m.start(),'end':start+m.end(),'source_label':label})
 return es

def save(i,specs,excluded=None,pair_overrides=None):
 x=packet(i);cs=candidates(x);claims=[];allids=set();excluded=excluded or {};pair_overrides=pair_overrides or {}
 for spec in specs:
  index,normal,patterns,*options=spec;c=cs[index-1];allids.add(index);label=options[0] if options else 'supported';ev=evidence(x['context'],patterns)
  claims.append({'claim_id':f'c{len(claims)+1:03}','start':c['start'],'end':c['end'],'quote':c['quote'],'normalized_claim':normal or c['clean'],'conditions':{'study_scope':x['query'],'qualification':'literal qualifiers of original quote retained; no universal extrapolation'},'occurrences':[{'start':c['start'],'end':c['end'],'quote':c['quote']}],'grounding':{'label':label,'evidence':ev,'reason':'实际读取答案及相关context证据；对象、关系、数值单位、条件逐项核对。'+(' 部分条件/结论当前缺失。' if label=='partial' else ' 当前无此项支持。' if label=='unsupported' else '')}})
 # Explicit duplicate metadata kept as occurrences on the selected normalized atom.
 for index,reason in excluded.items():
  if isinstance(reason,int):
   c=cs[index-1];target=claims[reason-1];target['occurrences'].append({'start':c['start'],'end':c['end'],'quote':c['quote']});allids.add(index)
 if set(range(1,len(cs)+1))-allids-set(excluded):raise ValueError('candidate not accounted '+str(set(range(1,len(cs)+1))-allids-set(excluded)))
 pairs=[];a=x['raw_answer'];masked=list(a)
 for m in CITE.finditer(a):
  for n in range(m.start(),m.end()):masked[n]=' '
 masked=''.join(masked)
 for m in re.finditer(r'(?:Adj|et al|vs|e\.g|i\.e)\.',masked):masked=masked[:m.end()-1]+' '+masked[m.end():]
 for cite in CITE.finditer(a):
  previous=[m.end() for m in re.finditer(r'\n\s*\n|(?<=[.!?])\s+(?=[A-Z*])',masked[:cite.start()])];start=previous[-1] if previous else 0
  # r02: sentence end inline citations stay within the immediately preceding sentence.
  scoped=[c for c in claims if any(o['end']>start and o['start']<cite.end() for o in c['occurrences'])]
  refs=list(re.finditer(r'(pearl-src-[a-f0-9]+)(?:\s*\|)?',cite.group(0)))
  for j,ref in enumerate(refs):
   tail=cite.group(0)[ref.end():refs[j+1].start() if j+1<len(refs) else len(cite.group(0))];pages=re.findall(r'p\.\s*([\d-]+)',tail)
   for page in pages or [None]:
    label=f'[Source {ref.group(1)} | p.{page}]' if page else None;source_id=ref.group(1);available=label in {s[0] for s in sources(x['context'])} if page else any(source_id in s[0] for s in sources(x['context']))
    for c in scoped:
     proof=[ev for ev in c['grounding']['evidence'] if ev['source_label']==label or (page is None and source_id in ev['source_label'])];resolved_label=label if page else proof[0]['source_label'] if proof else next((s[0] for s in sources(x['context']) if source_id in s[0]),'[Source '+source_id+']');status='outside-context' if not available else c['grounding']['label'] if proof else 'unsupported'
     status=pair_overrides.get((c['claim_id'],label),status)
     pairs.append({'claim_id':c['claim_id'],'citation_start':cite.start(),'citation_end':cite.end(),'citation_quote':cite.group(0),'source_label':resolved_label,'citation_source_id':source_id,'citation_page_specified':page,'source_id_only_scope':page is None,'resolved_source_labels':sorted({ev['source_label'] for ev in proof}),'label':status,'evidence':proof,'reason':'r02同行句作用域；实际Source/page独立核对，未自动配Gold；具体可见证据如列。'})
 result={'blind_id':x['blind_id'],'response_sha256':x['response_sha256'],'context_sha256':x['context_sha256'],'extraction_unknown':False,'citation_extraction_unknown':False,'claims':claims,'citation_pairs':pairs,'excluded_candidates':{str(k):v for k,v in excluded.items() if not isinstance(v,int)},'completeness_review':'完整raw_answer逐句审阅；全部candidate保留、拆atom、重复合并或明确元声明/格式排除；独立数值/关系以normalized_claim区别，同句atoms可共享原文区间。','provenance':{'reviewer':'prepare_layer4 context primary','model':'inherited; exact deployment ID not exposed','task':'grounding','packet_path':str(PACK/f'grounding-{i:04}.json'),'packet_sha256':hashlib.sha256((PACK/f'grounding-{i:04}.json').read_bytes()).hexdigest(),'actual_read':['full raw_answer','query','actual context located relevant paragraphs; literal duplicate windows checked'],'facts_read':False,'identity_map_or_old_scores_read_during_task':False,'prior_exposure':'same role previously reviewed answerability task necessary requirements/context; engineering role saw partial dev009 old score/reference and dev012 generation metadata; no independent factuality package read. Grounding labels use only actual grounding context.','prompt_version':'r02'}}
 p=ROOT/'reviews/primary/grounding-C100-r02'/f'grounding-{i:04}.json';p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(i,len(claims),len(pairs))

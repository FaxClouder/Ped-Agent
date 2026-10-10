"""Independent saved-artifact verifier. Never imports scorer or generates semantic labels."""
import argparse,hashlib,itertools,json,math,re
from collections import Counter
from pathlib import Path

def read(path): return json.loads(Path(path).read_text('utf-8-sig'))
def canonical(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sha_text(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()
def div(n,d): return n/d if d else None
def avg(xs):
 xs=[x for x in xs if x is not None]; return sum(xs)/len(xs) if xs else None

def assert_equal(expected,actual,path='score'):
 if isinstance(expected,dict):
  if not isinstance(actual,dict): raise ValueError(path+' type')
  for k,v in expected.items():
   if k not in actual: raise ValueError(path+' missing '+k)
   assert_equal(v,actual[k],path+'.'+str(k))
 elif isinstance(expected,list):
  if not isinstance(actual,list) or len(expected)!=len(actual): raise ValueError(path+' length')
  for i,(a,b) in enumerate(zip(expected,actual)): assert_equal(a,b,path+f'[{i}]')
 elif isinstance(expected,(float,int)) and not isinstance(expected,bool):
  if not isinstance(actual,(float,int)) or not math.isclose(expected,actual,rel_tol=1e-10,abs_tol=1e-12): raise ValueError(path+' numeric mismatch')
 elif expected!=actual: raise ValueError(path+' mismatch')

def check_span(text,span):
 start,end=span.get('start'),span.get('end'); quote=span.get('quote')
 if type(start)!=int or type(end)!=int or not 0<=start<end<=len(text) or text[start:end]!=quote: raise ValueError('quote interval mismatch')

def recompute_claims(claims,unknown):
 gs=[c['grounding']['label'] for c in claims];fs=[c['factuality']['label'] for c in claims]
 if any(x not in ['supported','partial','unsupported','contradicted','unknown'] for x in gs) or any(x not in ['true','false','unknown'] for x in fs): raise ValueError('invalid label')
 n=len(gs);g=Counter(gs);f=Counter(fs);s,p,u,c,x=[g[k] for k in ['supported','partial','unsupported','contradicted','unknown']];t,wrong,xf=[f[k] for k in ['true','false','unknown']]
 b=lambda a,z:[None,None] if unknown else [div(a,n),div(z,n)]
 return {'N':n,'grounding_counts':dict(g),'factuality_counts':dict(f),'extraction_unknown':unknown,'faithfulness':b(s,s+x),'unsupported_rate':b(p+u+c,p+u+c+x),'context_contradiction_rate':b(c,c+x),'partial_rate':None if unknown else div(p,n),'missing_rate':None if unknown else div(u,n),'factuality':b(t,t+xf),'factuality_resolved_accuracy':None if unknown else div(t,t+wrong),'factuality_coverage':None if unknown else div(t+wrong,n),'fact_conflict_rate':None if unknown else div(wrong,n)}

def recompute_citations(claims,pairs,claim_unknown,citation_unknown):
 ids={x['claim_id'] for x in claims}
 if len(ids)!=len(claims) or any(x['claim_id'] not in ids for x in pairs): raise ValueError('pair claim identity')
 allowed={'supported','partial','unsupported','contradicted','unknown','invalid','outside-context'}
 if any(p['label'] not in allowed for p in pairs): raise ValueError('citation label')
 counts=Counter(p['label'] for p in pairs);good={p['claim_id'] for p in pairs if p['label']=='supported'};possible=good|{p['claim_id'] for p in pairs if p['label']=='unknown'};n=len(pairs)
 return {'pair_N':n,'claim_N':len(ids),'counts':dict(counts),'precision':[None,None] if citation_unknown else [div(counts['supported'],n),div(counts['supported']+counts['unknown'],n)],'recall':[None,None] if citation_unknown or claim_unknown else [div(len(good),len(ids)),div(len(possible),len(ids))]}

def recompute_reliability(rows):
 definite=[0,0,0,0];unresolved=[]
 for r in rows:
  a,b=r['answerability'],r['abstain']
  if a not in ['complete','partial','none','unknown']: raise ValueError('answerability label')
  if b is not None and type(b)!=bool: raise ValueError('abstain type')
  options=[]
  for answerable,abstain in itertools.product([True,False] if a=='unknown' else [a=='complete'],[True,False] if b is None else [b]):
   options.append(1 if answerable and abstain else 3 if answerable else 0 if abstain else 2)
  options=set(options)
  if len(options)==1: definite[next(iter(options))]+=1
  else: unresolved.append(options)
 tables={tuple(definite)};fallback=False
 for options in unresolved:
  expanded=set()
  for tab in tables:
   for index in options:
    amended=list(tab);amended[index]+=1;expanded.add(tuple(amended))
  tables=expanded
  if len(tables)>100000: fallback=True;break
 tp,fp,fn,tn=definite
 def metrics(tab):
  a,b,c,d=tab;return {'precision':div(a,a+b),'recall':div(a,a+c),'f1':div(2*a,2*a+b+c),'false_answer_rate':div(c,a+c),'false_refusal_rate':div(b,b+d)}
 result=dict(TP=tp,FP=fp,FN=fn,TN=tn,total_cells=len(rows),resolved_cells=len(rows)-len(unresolved),unknown_cells=len(unresolved),coverage=div(len(rows)-len(unresolved),len(rows)),answerability_counts=dict(Counter(r['answerability'] for r in rows)))
 for key,value in metrics(definite).items():
  vals=[0.,1.] if fallback else [metrics(t)[key] for t in tables];valid=[v for v in vals if v is not None]
  result[key]=value;result[key+'_bounds']=[min(valid),max(valid)] if valid else [None,None];result[key+'_may_be_na']=any(v is None for v in vals)
 return result

def recompute_summary(rows):
 known=[r for r in rows if not r['extraction_unknown']]; n=sum(r['N'] for r in rows)
 result={'cell_N':len(rows),'claim_N':n,'claim_na':sum(r['faithfulness'][0] is None for r in rows),'extraction_unknown_cells':sum(r['extraction_unknown'] for r in rows)}
 for metric in ['faithfulness','unsupported_rate','context_contradiction_rate','factuality']:
  result[metric+'_macro']=[avg([r[metric][j] for r in rows]) for j in [0,1]];eligible=[r for r in rows if r[metric][0] is not None];den=sum(r['N'] for r in eligible)
  result[metric+'_micro']=[div(sum(r[metric][j]*r['N'] for r in eligible),den) for j in [0,1]]
 result['factuality_coverage_macro']=avg([r['factuality_coverage'] for r in rows]);result['factuality_coverage_micro']=div(sum(r['factuality_counts'].get('true',0)+r['factuality_counts'].get('false',0) for r in known),sum(r['N'] for r in known))
 for name in ['grounding_counts','factuality_counts']:
  c=Counter()
  for row in rows:c.update(row[name])
  result[name]=dict(c)
 for metric,denominator in [('precision','pair_N'),('recall','claim_N')]:
  result['citation_'+metric+'_macro']=[avg([r['citation'][metric][j] for r in rows]) for j in [0,1]];eligible=[r for r in rows if r['citation'][metric][0] is not None];den=sum(r['citation'][denominator] for r in eligible)
  result['citation_'+metric+'_micro']=[div(sum(r['citation'][metric][j]*r['citation'][denominator] for r in eligible),den) for j in [0,1]];result['citation_'+metric+'_na']=len(rows)-len(eligible)
 result['citation_pair_N']=sum(r['citation']['pair_N'] for r in rows);result['reliability']=recompute_reliability(rows);result['behavior_counts']=dict(Counter(r['behavior'] for r in rows));reasons=[r['reason'] for r in rows if r['reason']!='na'];result['reason_counts']=dict(Counter(reasons));result['reason_accuracy']=div(reasons.count('correct'),sum(x!='unknown' for x in reasons))
 complete=[r for r in rows if r['answerability']=='complete'];correct=sum(r['old_strict']=='yes' for r in complete);result['complete_strict']={'N':len(complete),'correct':correct,'rate':div(correct,len(complete))}
 joint=Counter()
 for r in rows:
  support='fully_supported' if r['N'] and r['grounding_counts'].get('supported',0)==r['N'] and not r['extraction_unknown'] else 'not_fully_supported' if r['N'] else 'no_claims';joint['|'.join((r['answerability'],r['behavior'],r['old_strict'],support))]+=1
 result['joint_counts']=dict(joint);return result

def validate_review(review,inp,facts=None):
 answer,context=inp['raw_answer'],inp['context']; ids=set();labels={s['source_label'] for s in inp['source_map']}
 for c in review['claims']:
  if c['claim_id'] in ids: raise ValueError('duplicate claim')
  ids.add(c['claim_id']);check_span(answer,c)
  for occurrence in c.get('occurrences',[]):check_span(answer,occurrence)
  for ev in c['grounding'].get('evidence',[]):
   check_span(context,ev)
   if ev.get('source_label') not in labels:raise ValueError('evidence source identity')
   if not any(s['source_label']==ev['source_label'] and s['start']<=ev['start']<ev['end']<=s['end'] for s in inp['source_map']): raise ValueError('evidence source range')
  if c['grounding']['label'] in ['supported','partial','contradicted'] and not c['grounding'].get('evidence'):raise ValueError('grounding evidence missing')
  if c['factuality']['label'] in ['true','false'] and not c['factuality'].get('source_evidence'):raise ValueError('factuality source evidence missing')
  for ev in c['factuality'].get('source_evidence',[]):
   if facts is None:raise ValueError('fact packet absent')
   matches=[s for s in facts.get('sources',[]) if s['source_id']==ev.get('source_id') and s.get('chunk_id')==ev.get('chunk_id')]
   if len(matches)!=1:raise ValueError('fact source identity')
   source=matches[0];check_span(source['text'],ev)
   if ev.get('text_sha256')!=source['text_sha256'] or sha_text(source['text'])!=source['text_sha256']:raise ValueError('fact source SHA')
 for pair in review['citation_pairs']:
  if pair['claim_id'] not in ids:raise ValueError('citation claim identity')
  check_span(answer,{'start':pair['citation_start'],'end':pair['citation_end'],'quote':pair['citation_quote']})
  identity=re.fullmatch(r'\[Source\s+([^\s|\]]+)(?:\s*\|\s*p\.([^\]]+))?\]',pair['source_label'])
  matching=[]
  if identity:
   sid,page=identity.groups();literals=list(re.finditer(r'(?<![\w-])'+re.escape(sid)+r'(?![\w-])',pair['citation_quote']))
   if literals:
    cited_pages=[]
    for literal in literals:
     tail=pair['citation_quote'][literal.end():];next_id=re.search(r'pearl-src-[a-f0-9]+',tail)
     if next_id:tail=tail[:next_id.start()]
     cited_pages.extend(re.findall(r'p\.\s*([0-9]+(?:[-–][0-9]+)?)',tail))
    if cited_pages and page and page.replace('–','-') not in [p.replace('–','-') for p in cited_pages]:raise ValueError('citation literal page mismatch')
    for s in inp['source_map']:
     si=re.fullmatch(r'\[Source\s+([^\s|\]]+)\s*\|\s*p\.([^\]]+)\]',s['source_label'])
     if si and si.group(1)==sid and (page is None or si.group(2).replace('–','-')==page.replace('–','-')) and (not cited_pages or si.group(2).replace('–','-') in [p.replace('–','-') for p in cited_pages]):matching.append(s)
   elif pair['label'] not in ['invalid','outside-context','unknown']:raise ValueError('citation identity literal source mismatch')
  if pair['label'] not in ['invalid','outside-context','unknown'] and not matching:raise ValueError('citation identity absent from context')
  if pair['label']=='supported' and not pair.get('evidence'):raise ValueError('citation support evidence missing')
  for ev in pair.get('evidence',[]):
   check_span(context,ev)
   if pair['label'] in ['supported','partial','contradicted']:
    if not any(s['source_label']==ev.get('source_label') and s['start']<=ev['start']<ev['end']<=s['end'] for s in matching):raise ValueError('citation support source')
 return True

def semantic_claims(row):
 return [{k:c[k] for k in ('claim_id','start','end','quote','normalized_claim','conditions','occurrences') if k in c} for c in row['claims']]

def validate_exact_reuse(decision,packet,required):
 reuse=decision.get('provenance',{}).get('reuse',{})
 if not reuse.get('exact_content_equal_except_blind_id'):return
 for kind in ['packet','review']:
  path=reuse['original_'+kind+'_path'];required(path)
  if sha_file(path)!=reuse['original_'+kind+'_sha256']:raise ValueError('reuse original SHA')
 original_packet=read(reuse['original_packet_path'])
 if canonical({k:v for k,v in original_packet.items() if k!='blind_id'})!=canonical({k:v for k,v in packet.items() if k!='blind_id'}):raise ValueError('reuse.packet strict mismatch')
 original=read(reuse['original_review_path'])
 project=lambda d:[{k:c[k] for k in ['claim_id','normalized_claim','label','source_evidence','reason'] if k in c} for c in d['claims']]
 if canonical(project(original))!=canonical(project(decision)):raise ValueError('reuse.decision strict mismatch')

def validate_atom_reuse(decision,packet,required):
 for reuse in decision.get('provenance',{}).get('atom_reuse',[]):
  for kind in ['packet','review']:
   path=reuse['original_'+kind+'_path'];required(path)
   if sha_file(path)!=reuse['original_'+kind+'_sha256']:raise ValueError('reuse atom original SHA')
  old_packet=read(reuse['original_packet_path']);old_review=read(reuse['original_review_path'])
  one=lambda xs,key:next(x for x in xs if x['claim_id']==key)
  previous=one(old_packet['claims'],reuse['origin_claim_id']);current=one(packet['claims'],reuse['claim_id'])
  fields=('start','end','quote','normalized_claim','conditions','occurrences')
  project=lambda c:{k:c[k] for k in fields if k in c}
  if canonical(project(previous))!=canonical(project(current)):raise ValueError('reuse.atom semantic strict mismatch')
  semantic_sha=sha_text(canonical(project(current)))
  if reuse.get('semantic_sha256',semantic_sha)!=semantic_sha:raise ValueError('reuse atom semantic SHA')
  previous_decision=one(old_review['claims'],reuse['origin_claim_id']);current_decision=one(decision['claims'],reuse['claim_id'])
  for field in ['label','reason','source_evidence']:
   if canonical(previous_decision[field])!=canonical(current_decision[field]):raise ValueError('reuse.atom '+field+' strict mismatch')

def validate_selected_decision(row,task,decision):
 """A valid label still must match its saved, bound selected review."""
 if task=='grounding':
  fields=('claim_id','start','end','quote','normalized_claim','conditions','occurrences','grounding')
  project=lambda r:{'claims':[{k:c[k] for k in fields if k in c} for c in r['claims']], 'citation_pairs':r['citation_pairs'],'extraction_unknown':r.get('extraction_unknown',False),'citation_extraction_unknown':r.get('citation_extraction_unknown',False)}
  if canonical(project(decision))!=canonical(project(row)):raise ValueError('selected.grounding strict mismatch')
 elif task=='factuality':
  if {c['claim_id'] for c in row['claims']}!={c['claim_id'] for c in decision['claims']}:raise ValueError('selected.fact claim set')
  byid={c['claim_id']:c for c in decision['claims']}
  for c in row['claims']:
   d=byid[c['claim_id']];f=c['factuality']
   if d.get('normalized_claim',c['normalized_claim'])!=c['normalized_claim']:raise ValueError('selected.fact semantic identity')
   for key in ['label','source_evidence','reason']:assert_equal(d[key],f[key],'selected.factuality.'+key)
 elif task=='answerability':assert_equal(decision['answerability'],row['answerability'],'selected.answerability')
 elif task=='behavior':
  for key in ['behavior','abstain','unsupported_completion']:assert_equal(decision.get(key),row.get(key),'selected.behavior.'+key)
  reason=decision.get('reason');label=reason.get('label') if isinstance(reason,dict) else reason
  assert_equal(label or 'na',row['reason'],'selected.behavior.reason')
 else:raise ValueError('selected task invalid')
 return True

def verify(bindings:Path,out:Path)->dict:
 bindings=Path(bindings);out=Path(out);b=read(bindings);artifacts=b['artifacts'];bound={str(Path(x['path']).resolve()):x for x in artifacts}
 for x in artifacts:
  if sha_file(x['path'])!=x['sha256']:raise ValueError('artifact SHA mismatch '+x['path'])
 def required(path):
  if str(Path(path).resolve()) not in bound:raise ValueError('required artifact unbound '+str(path))
 for key in ['input_path','reviewed_path','result_path','old_l3_path']:required(b[key])
 inputs=read(b['input_path']);raw={r['cell_id']:r for r in inputs['cells']};reviews=read(b['reviewed_path'])['rows'];saved=read(b['result_path']);old={(r['intent_id'],r['arm']):r for r in read(b['old_l3_path'])['rows']}
 if len(raw)!=len(inputs['cells']) or len({r['cell_id'] for r in reviews})!=len(reviews):raise ValueError('duplicate cell')
 if b.get('expected_cells') is not None and set(b['expected_cells'])!={r['cell_id'] for r in reviews}:raise ValueError('expected matrix')
 facts={}
 for ref in inputs['references']:
  required(ref['path']);facts[ref['intent_id']]=read(ref['path'])
 recomputed=[]
 for r in reviews:
  inp=raw[r['cell_id']];generation_path=Path(inputs['l3_root']).parent.parent/inp['generation_path'];required(generation_path)
  generation=read(generation_path)
  if sha_file(generation_path)!=inp['generation_file_sha256'] or generation['raw_answer']!=inp['raw_answer'] or generation['response_sha256']!=inp['response_sha256'] or generation['context_sha256']!=inp['context_sha256']:raise ValueError('generation input binding')
  body={k:v for k,v in generation.items() if k!='record_sha256'}
  if sha_text(canonical(body))!=generation['record_sha256'] or generation['record_sha256']!=inp['generation_record_sha256']:raise ValueError('generation self SHA')
  if r['response_sha256']!=inp['response_sha256'] or sha_text(inp['raw_answer'])!=inp['response_sha256'] or sha_text(inp['context'])!=inp['context_sha256']:raise ValueError('review input SHA')
  validate_review(r,inp,facts.get(r['intent_id']))
  row={k:r[k] for k in ['cell_id','intent_id','arm','stratum','answerability','behavior','abstain','reason']};row.update(recompute_claims(r['claims'],r.get('extraction_unknown',False)));row['citation']=recompute_citations(r['claims'],r['citation_pairs'],r.get('extraction_unknown',False),r.get('citation_extraction_unknown',False));row['old_strict']=old[(r['intent_id'],r['arm'])]['strict'];recomputed.append(row)
 assert_equal(recomputed,saved['rows'],'score.rows')
 for arm in {r['arm'] for r in recomputed}:
  subset=[r for r in recomputed if r['arm']==arm];summary=recompute_summary(subset);summary['strata']={s:recompute_summary([r for r in subset if r['stratum']==s]) for s in {r['stratum'] for r in subset}};assert_equal(summary,saved['arms'][arm],'score.arm.'+arm)
 chains=b.get('review_chain',[]);seen=set()
 for chain in chains:
  key=(chain['cell_id'],chain['task'])
  if key in seen:raise ValueError('duplicate review chain')
  seen.add(key)
  for field in ['primary_path','secondary_path','adjudication_path']:
   if chain.get(field):
    required(chain[field]);decision=read(chain[field])
    if decision.get('cell_id',chain['cell_id'])!=chain['cell_id']:raise ValueError('review chain cell identity')
    if decision.get('task',chain['task'])!=chain['task']:raise ValueError('review chain task identity')
    expected_blind=chain.get(field.replace('_path','_blind_id'),chain.get('expected_blind_id'))
    if expected_blind and decision.get('blind_id')!=expected_blind:raise ValueError('review chain blind identity')
    provenance=decision.get('provenance',{})
    if not (provenance.get('reviewer') or provenance.get('role')):raise ValueError('review provenance reviewer missing')
    packet=provenance.get('packet_path')
    if packet:
     required(packet)
     if provenance.get('packet_sha256')!=sha_file(packet):raise ValueError('review packet SHA')
    if chain.get(field.replace('_path','_sha256')) and sha_file(chain[field])!=chain[field.replace('_path','_sha256')]:raise ValueError('review chain SHA')
  if not chain.get('primary_path'):raise ValueError('missing primary review')
  selected=chain.get('selected_path')
  if b.get('require_selected_chain',True) and not selected:raise ValueError('selected decision missing')
  if selected:
   required(selected);decision=read(selected);row=next(r for r in reviews if r['cell_id']==chain['cell_id']);validate_selected_decision(row,chain['task'],decision)
   if chain['task']=='factuality':
    packet=decision.get('provenance',{}).get('packet_path')
    if not packet:raise ValueError('selected factuality packet missing')
    required(packet)
    if canonical(read(packet)['claims'])!=canonical(semantic_claims(row)):raise ValueError('selected.fact canonical claims strict mismatch')
    validate_exact_reuse(decision,read(packet),required)
    validate_atom_reuse(decision,read(packet),required)
 if b.get('require_full_chain',True):
  expected={(r['cell_id'],task) for r in reviews for task in ['answerability','grounding','factuality','behavior']}
  if seen!=expected:raise ValueError('review chain incomplete')
 reuse=b.get('reuse',[])
 for item in reuse:
  required(item['source_path']);source=read(item['source_path']);source_rows=source['rows'] if isinstance(source,dict) and 'rows' in source else [source];matches=[r for r in source_rows if r['cell_id']==item['cell_id']]
  if len(matches)!=1 or sha_text(canonical(matches[0]))!=item['canonical_sha256']:raise ValueError('reuse canonical SHA')
  current=next(r for r in reviews if r['cell_id']==item['cell_id'])
  if canonical(current)!=canonical(matches[0]):raise ValueError('reuse row changed')
 calibration=b.get('calibration')
 if calibration:
  for field in ['expected_path','judge_path','compare_path']:required(calibration[field])
  compare=read(calibration['compare_path'])
  if not (compare.get('status')=='passed' or compare.get('passed',compare.get('verified',False))):raise ValueError('calibration failed')
 result={'verified':True,'cell_n':len(reviews),'claim_n':sum(r['N'] for r in recomputed),'citation_pair_n':sum(r['citation']['pair_N'] for r in recomputed),'binding_n':len(artifacts),'review_chain_n':len(chains),'reuse_n':len(reuse),'calibration_bound':bool(calibration),'independent_arithmetic':True,'scorer_imported':False,'bindings_sha256':sha_file(bindings)}
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('bindings',type=Path);p.add_argument('out',type=Path);a=p.parse_args();print(json.dumps(verify(a.bindings,a.out)))

"""Exclusive C100 assembly; explicit selected chains, never infers semantic labels.

export selection.json new-directory: source-only final atoms and exact reuse audit.
assemble selection.json reviewed.json bindings.json: requires all four decisions.
Selection rows: cell_id, chains {task: primary_path,secondary_path,
adjudication_path(optional),selected_path}. Top-level old_l3_path, result_path,
calibration optional. No scoring is invoked by this program.
"""
import argparse, copy, hashlib, json
from pathlib import Path

ROOT=Path('outputs/pearl-layer4-dev80-20261004-01')
FIELDS=('claim_id','start','end','quote','normalized_claim','conditions','occurrences')
TASKS=('answerability','grounding','factuality','behavior')
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f: json.dump(x,f,ensure_ascii=False,indent=2)
def atom(c): return {k:c[k] for k in FIELDS if k in c}
def semantic(c): return {k:c[k] for k in FIELDS[1:] if k in c}
def exact_aliases(final,previous,origin_path):
 """ID-independent equality, including presence/absence of every semantic field."""
 result=[]
 for c in final:
  matches=[p for p in previous if canonical(semantic(p))==canonical(semantic(c))]
  result.append({'claim_id':c['claim_id'],'semantic_sha256':hashlib.sha256(canonical(semantic(c)).encode()).hexdigest(),
   'origin_path':str(origin_path),'origin_sha256':sha(origin_path),
   'origin_claim_ids':[p['claim_id'] for p in matches],'status':'exact_atom_reusable' if len(matches)==1 else 'requires_actual_review'})
 return result
def selected(chain):
 p=Path(chain['selected_path'])
 if str(p) not in [str(Path(chain[k])) for k in ('primary_path','secondary_path','adjudication_path') if chain.get(k)]:
  raise ValueError('selected_path outside review chain')
 for k in ('primary_path','secondary_path','adjudication_path'):
  if chain.get(k) and not Path(chain[k]).is_file(): raise ValueError('missing review '+chain[k])
 return read(p)
def export(selection,out):
 out=Path(out)
 if out.exists(): raise FileExistsError(out)
 # All checks precede creation: no partially published packet set on missing adjudication.
 facts={x['intent_id']:x for x in read(ROOT/'facts/facts-r03.json')['items']}
 prepared=[]
 for i,row in enumerate(selection['rows'],1):
  g=selected(row['chains']['grounding']);ident=f'factuality-{i:04d}'
  item=facts[row['cell_id'].split('::')[0]]
  packet={'blind_id':ident,'claims':[atom(c) for c in g['claims']],
   'response_sha256':g['response_sha256'],'facts':{'sources':item['evidence'],
    'supplementary_facts':item.get('supplementary_facts',[])},
   'rubric':'true / false / unknown; source-only review of all final atoms and conditions'}
  audits=[]
  for origin in row.get('factuality_origin_paths',[]):
   d=read(origin);p=d.get('provenance',{}).get('packet_path')
   if not p: raise ValueError('origin missing packet binding '+origin)
   if d['provenance'].get('packet_sha256')!=sha(p): raise ValueError('origin packet SHA mismatch')
   audits.append({'review_path':origin,'review_sha256':sha(origin),'packet_path':p,
    'aliases':exact_aliases(packet['claims'],read(p)['claims'],p)})
  prepared.append((packet,row['cell_id'],audits))
 out.mkdir(parents=True)
 mapping=[]
 for packet,cell,audits in prepared:
  p=out/(packet['blind_id']+'.json');write(p,packet)
  mapping.append({'cell_id':cell,'blind_id':packet['blind_id'],'packet_path':str(p),'packet_sha256':sha(p),'origin_audit':audits})
 write(out.parent/(out.name+'-identity-and-reuse-audit.json'),mapping)
 return {'packet_n':len(prepared),'directory':str(out),'labels_generated':False}
def assemble(selection,reviewed_path,bindings_path):
 inputs=read(ROOT/'inputs-r01.json');cells={x['cell_id']:x for x in inputs['cells']}
 expected=read(ROOT/'stage-selection-freeze-r01.json')['C100_cell_ids']
 ids=[r['cell_id'] for r in selection['rows']]
 if len(ids)!=100 or len(set(ids))!=100 or set(ids)!=set(expected):raise ValueError('C100 selection mismatch')
 paths={str(ROOT/'inputs-r01.json'),str(ROOT/'stage-selection-freeze-r01.json'),str(selection['old_l3_path'])}
 def bind(p):
  paths.add(str(p));return sha(p)
 def bind_origins(value):
  if isinstance(value,list):
   for v in value:bind_origins(v)
  elif isinstance(value,dict):
   for k,v in value.items():
    if isinstance(v,str) and (k.endswith('_path') or k=='path') and Path(v).is_file():
     actual=bind(v);hashkey=k[:-5]+'_sha256' if k.endswith('_path') else 'sha256'
     if hashkey in value and value[hashkey]!=actual:raise ValueError('origin SHA mismatch '+v)
    elif isinstance(v,(list,dict)):bind_origins(v)
 rows=[];chains=[]
 for r in selection['rows']:
  decisions={t:selected(r['chains'][t]) for t in TASKS}
  inp=cells[r['cell_id']];g=decisions['grounding'];f=decisions['factuality'];beh=decisions['behavior']
  row={k:inp[k] for k in ('cell_id','intent_id','arm','response_sha256','context_sha256')}
  ref=next(x for x in inputs['references'] if x['intent_id']==inp['intent_id'])
  row['stratum']=read(ref['path'])['stratum']
  row.update({k:copy.deepcopy(g[k]) for k in ('claims','citation_pairs')})
  for k in ('extraction_unknown','citation_extraction_unknown'):row[k]=g.get(k,False)
  fm={c['claim_id']:c for c in f['claims']}
  if set(fm)!={c['claim_id'] for c in row['claims']}:raise ValueError('factuality ID mismatch')
  fp=f.get('provenance',{}).get('packet_path')
  if not fp or canonical(read(fp)['claims'])!=canonical([atom(c) for c in row['claims']]):raise ValueError('final factuality packet atoms mismatch')
  for c in row['claims']:
   d=fm[c['claim_id']]
   if d['normalized_claim']!=c['normalized_claim']:raise ValueError('normalized claim mismatch')
   c['factuality']={k:d[k] for k in ('label','source_evidence','reason')}
  row['answerability']=decisions['answerability']['answerability']
  for k in ('behavior','abstain','reason','unsupported_completion'):row[k]=beh[k]
  reason=row['reason'];row['reason']=(reason.get('label') if isinstance(reason,dict) else reason) or 'na'
  rows.append(row)
  for task in TASKS:
   chain={'cell_id':row['cell_id'],'task':task,**r['chains'][task]}
   for role in ('primary','secondary','adjudication'):
    p=chain.get(role+'_path')
    if p:
     chain[role+'_sha256']=bind(p);d=read(p);chain[role+'_blind_id']=d['blind_id']
     prov=d.get('provenance',{});bind_origins(prov);packet=prov.get('packet_path')
     if packet:
      if prov.get('packet_sha256')!=bind(packet):raise ValueError('review packet SHA mismatch')
   chains.append(chain)
 for ref in inputs['references']:bind(ref['path'])
 for inp in inputs['cells']:bind(inp['generation_path'])
 calibration=selection.get('calibration')
 if calibration:
  for k in ('expected_path','judge_path','compare_path'):bind(calibration[k])
 # Refuse preexisting targets before either write.
 if Path(reviewed_path).exists() or Path(bindings_path).exists():raise FileExistsError('assembly target exists')
 write(reviewed_path,{'status':'assembled_not_scored','rows':rows})
 bind(reviewed_path)
 bindings={'input_path':str(ROOT/'inputs-r01.json'),'reviewed_path':str(reviewed_path),
  'result_path':selection['result_path'],'old_l3_path':selection['old_l3_path'],
  'expected_cells':expected,'review_chain':chains,'require_full_chain':True,'require_selected_chain':True,
  'artifacts':[{'path':p,'sha256':sha(p)} for p in sorted(paths)]}
 if calibration:bindings['calibration']=calibration
 write(bindings_path,bindings)
 return {'cell_n':len(rows),'chain_n':len(chains),'scored':False}
def finalize_bindings(source,out):
 b=read(source)
 for entry in b['artifacts']:
  if sha(entry['path'])!=entry['sha256']:raise ValueError('bound artifact changed '+entry['path'])
 p=b['result_path']
 if not Path(p).is_file():raise ValueError('score result missing')
 if any(Path(x['path']).resolve()==Path(p).resolve() for x in b['artifacts']):raise ValueError('result already bound')
 b['artifacts'].append({'path':p,'sha256':sha(p)})
 b['assembly_bindings_origin']={'path':str(source),'sha256':sha(source)}
 write(out,b);return {'result_bound':True,'scored_by_this_tool':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['export','assemble','finalize-bindings']);p.add_argument('selection',type=Path);p.add_argument('out',type=Path);p.add_argument('--bindings',type=Path);a=p.parse_args()
 s=read(a.selection)
 if a.mode=='export':result=export(s,a.out)
 elif a.mode=='finalize-bindings':result=finalize_bindings(a.selection,a.out)
 else:
  if not a.bindings:p.error('--bindings required for assemble')
  result=assemble(s,a.out,a.bindings)
 print(json.dumps(result))

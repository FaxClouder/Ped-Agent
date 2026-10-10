"""D300/Eval400 engineering assembly; no judge, generation, or scoring calls."""
import argparse,copy,hashlib,json
from pathlib import Path
from assemble_c100_r01 import ROOT,TASKS,atom,canonical,read,selected,sha,write,finalize_bindings

def validate_behavior_decision(d):
 behavior=d.get('behavior')
 if behavior not in {'full_answer','bounded_partial','pure_abstain','ambiguous'}:raise ValueError('behavior vocabulary')
 reason=d.get('reason');reason=reason.get('label') if isinstance(reason,dict) else reason
 if reason not in {'correct','incorrect','unknown','na',None}:raise ValueError('reason vocabulary')
 for field in ('abstain','unsupported_completion'):
  if d.get(field) is not None and type(d[field]) is not bool:raise ValueError('behavior boolean')
 if behavior=='full_answer' and d.get('abstain') is not False:raise ValueError('behavior action')
 if behavior=='full_answer' and reason!='na':raise ValueError('full answer reason')
 if behavior in {'bounded_partial','pure_abstain'} and reason in {'na',None}:raise ValueError('refusal reason judgment missing')
 if behavior in {'bounded_partial','pure_abstain'} and d.get('abstain') is not True:raise ValueError('behavior action')
 # This gate checks vocabulary and recorded action consistency only. It never
 # assigns labels or decides whether a conclusion is actually supported.

def validate_sampling(rows,fixed):
 ids=[r['cell_id'] for r in rows];expected=fixed['D300_shuffled_cell_ids'];sample=set(fixed['D60_secondary_cell_ids'])
 if len(ids)!=300 or len(set(ids))!=300 or set(ids)!=set(expected):raise ValueError('D300 selection mismatch')
 for r in rows:
  if set(r['chains'])!=set(TASKS):raise ValueError('four task chains required')
  for task,c in r['chains'].items():
   if not c.get('primary_path'):raise ValueError('primary missing')
   if bool(c.get('secondary_path'))!=(r['cell_id'] in sample):raise ValueError('secondary outside fixed D60 or sampled secondary missing')
 return sample
def bind_tree(value,artifacts):
 if isinstance(value,list):
  for v in value:bind_tree(v,artifacts)
 elif isinstance(value,dict):
  for k,v in value.items():
   if isinstance(v,str) and (k.endswith('_path') or k=='path') and Path(v).is_file():
    digest=sha(v);h=k[:-5]+'_sha256' if k.endswith('_path') else 'sha256'
    if h in value and value[h]!=digest:raise ValueError('origin SHA mismatch')
    artifacts[str(Path(v))]=digest
   elif isinstance(v,(list,dict)):bind_tree(v,artifacts)
def row_and_chains(spec,inp,stratum,artifacts):
 ds={t:selected(spec['chains'][t]) for t in TASKS};g=ds['grounding'];f=ds['factuality'];beh=ds['behavior']
 validate_behavior_decision(beh)
 row={k:inp[k] for k in ('cell_id','intent_id','arm','response_sha256','context_sha256')};row['stratum']=stratum
 row.update({k:copy.deepcopy(g[k]) for k in ('claims','citation_pairs')})
 for k in ('extraction_unknown','citation_extraction_unknown'):row[k]=g.get(k,False)
 fm={c['claim_id']:c for c in f['claims']}
 if len(fm)!=len(f['claims']) or set(fm)!={c['claim_id'] for c in row['claims']}:raise ValueError('fact ID mismatch')
 packet=f.get('provenance',{}).get('packet_path')
 if not packet or canonical(read(packet)['claims'])!=canonical([atom(c) for c in row['claims']]):raise ValueError('fact packet final atoms mismatch')
 for c in row['claims']:
  fc=fm[c['claim_id']]
  if fc['normalized_claim']!=c['normalized_claim']:raise ValueError('fact normalized mismatch')
  c['factuality']={k:copy.deepcopy(fc[k]) for k in ('label','source_evidence','reason')}
 row['answerability']=ds['answerability']['answerability']
 for k in ('behavior','abstain','unsupported_completion'):row[k]=beh[k]
 reason=beh['reason'];row['reason']=(reason.get('label') if isinstance(reason,dict) else reason) or 'na'
 chains=[]
 for task in TASKS:
  chain={'cell_id':inp['cell_id'],'task':task,**spec['chains'][task]}
  for role in ('primary','secondary','adjudication'):
   p=chain.get(role+'_path')
   if p:
    d=read(p);chain[role+'_sha256']=sha(p);chain[role+'_blind_id']=d['blind_id'];artifacts[p]=sha(p)
    prov=d.get('provenance',{});bind_tree(prov,artifacts)
    packet=prov.get('packet_path')
    if packet and prov.get('packet_sha256')!=sha(packet):raise ValueError('packet SHA mismatch')
  chains.append(chain)
 return row,chains
def assemble_d(selection,out,bindings_out):
 fixed=read(ROOT/'stage-selection-freeze-r01.json');sample=validate_sampling(selection['rows'],fixed)
 inputs=read(ROOT/'inputs-r01.json');cells={r['cell_id']:r for r in inputs['cells']};refs={x['intent_id']:x for x in inputs['references']}
 artifacts={};rows=[];chains=[]
 maps={}
 for task in ('answerability','grounding','behavior'):
  for role,stage in (('primary','D300'),('secondary','D60')):
   p=ROOT/'packets'/f'{task}-{stage}-r02-identity-map.json'
   maps[(task,role)]={x['cell_id']:x['blind_id'] for x in read(p)};artifacts[str(p)]=sha(p)
 for r in selection['rows']:
  for task in ('answerability','grounding','behavior'):
   for role in ('primary','secondary'):
    p=r['chains'][task].get(role+'_path')
    if p and read(p)['blind_id']!=maps[(task,role)][r['cell_id']]:raise ValueError('D300/D60 blind identity mapping mismatch')
  inp=cells[r['cell_id']];row,chain=row_and_chains(r,inp,read(refs[inp['intent_id']]['path'])['stratum'],artifacts);rows.append(row);chains.extend(chain)
 for p in [ROOT/'inputs-r01.json',ROOT/'stage-selection-freeze-r01.json',selection['old_l3_path']]+[x['path'] for x in inputs['references']]+[x['generation_path'] for x in inputs['cells']]:artifacts[str(p)]=sha(p)
 if Path(out).exists() or Path(bindings_out).exists():raise FileExistsError('output exists')
 write(out,{'status':'assembled_not_scored','rows':rows});artifacts[str(out)]=sha(out)
 b={'input_path':str(ROOT/'inputs-r01.json'),'reviewed_path':str(out),'old_l3_path':selection['old_l3_path'],'result_path':selection['result_path'],'expected_cells':fixed['D300_shuffled_cell_ids'],'review_chain':chains,'require_full_chain':True,'require_selected_chain':True,'secondary_sampling':{'stage_selection_path':str(ROOT/'stage-selection-freeze-r01.json'),'stage_selection_sha256':sha(ROOT/'stage-selection-freeze-r01.json'),'sampled_cell_ids':sorted(sample),'primary_only_cell_ids':sorted(set(fixed['D300_shuffled_cell_ids'])-sample)},'artifacts':[{'path':p,'sha256':h} for p,h in sorted(artifacts.items())]}
 if selection.get('calibration'):
  b['calibration']=selection['calibration']
  for p in b['calibration'].values():
   if isinstance(p,str) and Path(p).is_file():b['artifacts'].append({'path':p,'sha256':sha(p)})
 write(bindings_out,b);return {'cell_n':300,'secondary_cell_n':60,'primary_only_cell_n':240,'scored':False}
def combine400(c_bindings,d_bindings,out,bindings_out,result_path):
 c=read(c_bindings);d=read(d_bindings);fixed=read(ROOT/'stage-selection-freeze-r01.json')
 artifacts={}
 for b in (c,d):
  for x in b['artifacts']:
   if sha(x['path'])!=x['sha256']:raise ValueError('origin bound artifact changed')
   artifacts[x['path']]=x['sha256']
 cr=read(c['reviewed_path'])['rows'];dr=read(d['reviewed_path'])['rows']
 if {r['cell_id'] for r in cr}!=set(fixed['C100_cell_ids']) or len(cr)!=100:raise ValueError('C100 origin mismatch')
 if {r['cell_id'] for r in dr}!=set(fixed['D300_shuffled_cell_ids']) or len(dr)!=300:raise ValueError('D300 origin mismatch')
 if c['old_l3_path']!=d['old_l3_path']:raise ValueError('L3 origins differ')
 # Copy whole rows exactly; never recompute or normalize C decisions here.
 rows=copy.deepcopy(cr+dr);reuse=[{'cell_id':r['cell_id'],'source_path':c['reviewed_path'],'canonical_sha256':hashlib.sha256(canonical(r).encode()).hexdigest()} for r in cr]
 if Path(out).exists() or Path(bindings_out).exists():raise FileExistsError('output exists')
 write(out,{'status':'assembled_not_scored','rows':rows});artifacts[str(out)]=sha(out)
 for p in (c_bindings,d_bindings):artifacts[str(p)]=sha(p)
 b={k:copy.deepcopy(d[k]) for k in ('input_path','old_l3_path','secondary_sampling','require_full_chain','require_selected_chain')};b.update(reviewed_path=str(out),result_path=str(result_path),expected_cells=fixed['C100_cell_ids']+fixed['D300_shuffled_cell_ids'],review_chain=c['review_chain']+d['review_chain'],reuse=reuse,artifacts=[{'path':p,'sha256':h} for p,h in sorted(artifacts.items())])
 if c.get('calibration'):b['calibration']=c['calibration']
 write(bindings_out,b);return {'cell_n':400,'exact_C100_reuse_n':100,'scored':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['D300','Eval400','finalize-bindings']);p.add_argument('source',type=Path);p.add_argument('out',type=Path);p.add_argument('--bindings',type=Path);p.add_argument('--D-bindings',type=Path);p.add_argument('--result',type=Path);a=p.parse_args()
 if a.mode=='finalize-bindings':r=finalize_bindings(a.source,a.out)
 elif a.mode=='D300':r=assemble_d(read(a.source),a.out,a.bindings)
 else:r=combine400(a.source,a.D_bindings,a.out,a.bindings,a.result)
 print(json.dumps(r))

"""Independent fixed-sampling gate before existing independent arithmetic verifier."""
import argparse
from pathlib import Path
from assemble_c100_r01 import read,sha,canonical
from verify import verify

def validate_chain_cell(decision, inp, expected_blind):
 if decision.get('blind_id')!=expected_blind:raise ValueError('blind identity')
 provenance=decision.get('provenance',{});packet=provenance.get('packet_path')
 if not packet:raise ValueError('cell input packet missing')
 white=read(packet)
 for field in ('response_sha256','context_sha256','query','raw_answer','context'):
  for obj in (decision,white):
   if field in obj and field in inp and obj[field]!=inp[field]:raise ValueError('cell input '+field)
 task=expected_blind.split('-')[0]
 fields={'answerability':{'blind_id','query','context','context_sha256','requirements'},'grounding':{'blind_id','query','raw_answer','context','context_sha256','response_sha256'},'behavior':{'blind_id','query','raw_answer','context','context_sha256','response_sha256','requirements'},'factuality':{'blind_id','claims','response_sha256','facts'}}[task]
 if not fields<=set(white):raise ValueError('required packet fields')
 if white['blind_id']!=expected_blind:raise ValueError('packet blind identity')
 if provenance.get('packet_sha256')!=sha(packet):raise ValueError('cell input packet SHA')

def validate_reuse_coverage(bindings,fixed):
 reuse=bindings.get('reuse',[])
 if len(reuse)!=100 or {x['cell_id'] for x in reuse}!=set(fixed['C100_cell_ids']):raise ValueError('C100 reuse coverage')

def validate_actual_identity(bindings):
 fixed=read(bindings['secondary_sampling']['stage_selection_path'])
 validate_reuse_coverage(bindings,fixed)
 inputs={x['cell_id']:x for x in read(bindings['input_path'])['cells']}
 root=Path(bindings['input_path']).parent;maps={}
 artifacts={str(Path(x['path']).resolve()):x['sha256'] for x in bindings['artifacts']}
 for task in ('answerability','grounding','behavior'):
  for role,stage in (('primary','D300'),('secondary','D60')):
   mp=root/'packets'/f'{task}-{stage}-r02-identity-map.json'
   if artifacts.get(str(mp.resolve()))!=sha(mp):raise ValueError('identity map not bound')
   maps[task,role]={x['cell_id']:x for x in read(mp)}
 dset=set(fixed['D300_shuffled_cell_ids']);sample=set(fixed['D60_secondary_cell_ids'])
 for chain in bindings['review_chain']:
  if chain['cell_id'] not in dset:continue
  paths=[chain[k] for k in ('primary_path','secondary_path','adjudication_path') if chain.get(k)]
  if chain.get('selected_path') not in paths:raise ValueError('selected outside actual chain')
  task=chain['task'];cell=chain['cell_id']
  for role in ('primary','secondary','adjudication'):
   p=chain.get(role+'_path')
   if not p:continue
   if task=='factuality':
    index=fixed['D300_shuffled_cell_ids'].index(cell)+1 if role=='primary' else int(maps['grounding','secondary'][cell]['blind_id'].split('-')[-1])
    blind=f'factuality-{index:04d}'
   else:
    maprole='secondary' if role=='adjudication' and cell in sample else role if role!='adjudication' else 'primary'
    identity=maps[task,maprole][cell];blind=identity['blind_id'];stage='D60' if maprole=='secondary' else 'D300'
    original=root/'packets'/f'{task}-{stage}-r02'/f'{blind}.json'
    if sha(original)!=identity['packet_sha256'] or artifacts.get(str(original.resolve()))!=sha(original):raise ValueError('original white packet not bound')
    actual=read(read(p)['provenance']['packet_path']);frozen=read(original)
    for key in ('query','context','raw_answer','requirements'):
     if key in frozen and (key not in actual or canonical(actual[key])!=canonical(frozen[key])):raise ValueError('original white packet '+key)
   validate_chain_cell(read(p),inputs[cell],blind)

def validate_decision_vocabulary(rows):
 for row in rows:
  if row.get('behavior') not in ('full_answer','bounded_partial','pure_abstain','ambiguous') or row.get('reason') not in ('correct','incorrect','unknown','na'):
   raise ValueError('saved decision vocabulary')
  for key in ('abstain','unsupported_completion'):
   if row.get(key) is not None and type(row[key]) is not bool:raise ValueError('saved decision boolean')
  if row['behavior']=='full_answer' and row.get('abstain') is not False:raise ValueError('saved decision action')
  if row['behavior']=='full_answer' and row.get('reason')!='na':raise ValueError('full answer reason')
  if row['behavior'] in ('bounded_partial','pure_abstain') and row.get('reason')=='na':raise ValueError('refusal reason judgment missing')
  if row['behavior'] in ('bounded_partial','pure_abstain') and row.get('abstain') is not True:raise ValueError('saved decision action')
  if row['behavior']=='bounded_partial' and any(c['grounding']['label']!='supported' for c in row.get('claims',[])):raise ValueError('bounded answer claim support')
def validate_fixed_sampling(bindings):
 p=bindings['secondary_sampling'];fixed=read(p['stage_selection_path'])
 if sha(p['stage_selection_path'])!=p['stage_selection_sha256']:raise ValueError('sampling SHA')
 sample=set(fixed['D60_secondary_cell_ids']);all_d=set(fixed['D300_shuffled_cell_ids'])
 if set(p['sampled_cell_ids'])!=sample or set(p['primary_only_cell_ids'])!=all_d-sample:raise ValueError('fixed sample mismatch')
 chains=[x for x in bindings['review_chain'] if x['cell_id'] in all_d]
 if len(chains)!=1200:raise ValueError('D four-task chain count')
 seen=set()
 for c in chains:
  key=(c['cell_id'],c['task'])
  if key in seen:raise ValueError('duplicate D chain')
  seen.add(key)
  if bool(c.get('secondary_path'))!=(c['cell_id'] in sample):raise ValueError('secondary sampling violation')
 return {'secondary_cell_n':60,'primary_only_cell_n':240}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('bindings',type=Path);p.add_argument('out',type=Path);a=p.parse_args();b=read(a.bindings);validate_fixed_sampling(b);validate_actual_identity(b);validate_decision_vocabulary(read(b['reviewed_path'])['rows']);print(verify(a.bindings,a.out))

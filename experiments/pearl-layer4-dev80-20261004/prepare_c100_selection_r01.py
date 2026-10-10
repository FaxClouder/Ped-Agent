"""Write an explicit engineering template, preserving all origin decisions."""
from assemble_c100_r01 import ROOT,read,write
from pathlib import Path
def path(role,directory,ident):return str(ROOT/'reviews'/role/directory/(ident+'.json'))
def preferred(role,base,supplement,ident):
 p=path(role,supplement,ident)
 return p if Path(p).is_file() else path(role,base,ident)
if __name__=='__main__':
 freeze={r['cell_id']:r for r in read(ROOT/'answerability-C100-freeze-r01.json')['rows']}
 maps={task:{x['cell_id']:x['blind_id'] for x in read(ROOT/'packets'/f'{task}-C100-r02-identity-map.json')} for task in ('grounding','behavior')}
 fm={x['cell_id']:x['blind_id'] for x in read(ROOT/'packets/factuality-C100-fine-candidates-r03-identity-map.json')}
 rows=[]
 for cell,gid in maps['grounding'].items():
  i=int(gid.rsplit('-',1)[1]);bid=maps['behavior'][cell];fid=fm[cell];ans=freeze[cell]
  gc='grounding-C100-r05' if i<=10 else 'grounding-C100-batch02-r03' if i<=20 else 'grounding-C100-r09' if i<=40 else 'grounding-C100-r11' if i<=50 else 'grounding-C100-r10'
  bc='behavior-C100-r12' if i<=20 else 'behavior-C100-r09-reason-r01' if i<=40 else 'behavior-C100-r11' if i<=50 else 'behavior-C100-r10'
  gs=preferred('adjudication',gc,'grounding-C100-r10-supplement-r01',gid) if i>50 else path('adjudication',gc,gid)
  bs=preferred('adjudication',bc,'behavior-C100-r10-supplement-r01',bid) if i>50 else path('adjudication',bc,bid)
  chains={}
  ac={k:ans[k] for k in ('primary_path','secondary_path','selected_path')}
  if ac['selected_path'] not in (ac['primary_path'],ac['secondary_path']):ac['adjudication_path']=ac['selected_path']
  chains['answerability']=ac
  for task,ident,sel in [('grounding',gid,gs),('behavior',bid,bs)]:
   chains[task]={'primary_path':path('primary',task+'-C100-r02',ident),'secondary_path':path('secondary',task+'-C100-r02',ident),'adjudication_path':sel,'selected_path':sel}
  fp=path('primary','factuality-C100-fine-candidates-r03',fid);fs=path('secondary','factuality-C100-fine-candidates-r03',fid);fa=path('adjudication','factuality-C100-fine-candidates-r04',fid)
  chains['factuality']={'primary_path':fp,'secondary_path':fs,'selected_path':fa if Path(fa).is_file() else fp}
  if Path(fa).is_file():chains['factuality']['adjudication_path']=fa
  rows.append({'cell_id':cell,'chains':chains,'factuality_origin_paths':[fp,fs]+([fa] if Path(fa).is_file() else [])})
 template={'status':'engineering_selection_template_final_fact_atoms_and_tail_supplements_pending','rows':rows,
  'old_l3_path':'outputs/pearl-answer-dev80-20261004-01/stage80/scores-r01.json',
  'result_path':str(ROOT/'C100-scores-final-r01.json'),
  'notes':['Refresh tail selected paths to r10-supplement-r01 when available.','Factuality chains currently origins; replace with final atom-bound reviews before assembly.','No C score or D evaluation executed.']}
 write(ROOT/'C100-assembly-selection-template-r01.json',template)
 print('Saved explicit selection template; not scored')

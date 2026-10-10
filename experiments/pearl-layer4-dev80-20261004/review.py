"""Task-specific exact top-level allowlists; identities remain evaluation-side."""
import hashlib,json,random
from pathlib import Path
ALLOW={'grounding':{'blind_id','query','raw_answer','response_sha256','context','context_sha256','claims','citations','rubric'},'factuality':{'blind_id','claims','response_sha256','facts','rubric'},'answerability':{'blind_id','query','context','context_sha256','requirements','rubric'},'behavior':{'blind_id','query','raw_answer','response_sha256','context','context_sha256','requirements','rubric'}}
FORBIDDEN={'cell_id','intent_id','arm','model','strategy','score','scores','l2_sufficient','decision','reference_answer','answerability_label','grounding_label','factuality_label'}
def validate_packet(packet,task):
 if task not in ALLOW: raise ValueError('task')
 if set(packet)-ALLOW[task]: raise ValueError('forbidden packet fields: '+str(set(packet)-ALLOW[task]))
 def scan(value):
  if isinstance(value,dict):
   if set(value)&FORBIDDEN: raise ValueError('forbidden nested fields')
   for v in value.values(): scan(v)
  elif isinstance(value,list):
   for v in value: scan(v)
 scan(packet)
 return True
def export_packets(inputs:list[dict],task:str,seed:int,out:Path)->dict:
 if task not in ALLOW: raise ValueError('task')
 rows=list(inputs); random.Random(seed).shuffle(rows); out=Path(out); out.mkdir(parents=True,exist_ok=True); mapping=[]
 for i,row in enumerate(rows):
  blind=f'{task}-{i+1:04d}'; packet={'blind_id':blind}
  for k in ALLOW[task]-{'blind_id'}:
   if k in row: packet[k]=row[k]
  validate_packet(packet,task)
  p=out/(blind+'.json')
  with p.open('x',encoding='utf-8') as f: json.dump(packet,f,ensure_ascii=False,indent=2)
  mapping.append({'blind_id':blind,'cell_id':row['cell_id'],'packet_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 with (out.parent/(out.name+'-identity-map.json')).open('x',encoding='utf-8') as f: json.dump(mapping,f,indent=2)
 return {'task':task,'count':len(mapping),'identity_map_outside_packet_directory':True}

"""Exclusive offline Layer 4 input preparation; no generation/retrieval calls."""
import argparse, hashlib, json, re
from pathlib import Path
ARMS=['A0-4096','A1-4096','A0-8192','A1-8192','Aref-8192']
PINNED={'delivery-manifest-r01.json':'0eeda54df9a0af9369f3ddcf6450465125754f74d24ba5e4d9304bd918cbe3cf','delivery-verification-r01.json':'47acda3e8695283fdd5cddcc4dffb869c942fdfe2e61633d8efb873a78d812db','reference-freeze-r01.json':'521279422ddc479602d39cc748ba37799772db100b71667092ed8f4444bc3c1e','stage80/score-input-r01.json':'80eb4ea7f7b1e04035ea43e381fab4cbbba7ded9feec66a447c44c78ae9fbd08','stage80/scores-r01.json':'e5a4584fd23560c404c7c6064f0c68d54ffc256771f9f5594f1313c67260db01'}
def canonical(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha_text(x): return hashlib.sha256(x.encode('utf-8')).hexdigest()
def sha_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def write(p,x):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f: json.dump(x,f,ensure_ascii=False,indent=2); f.write('\n')
def validate_cells(rows):
 ids=[x['cell_id'] for x in rows]
 if len(ids)!=len(set(ids)): raise ValueError('duplicate cell')
def validate_row(r):
 if sha_text(r['raw_answer'])!=r['response_sha256']: raise ValueError('response SHA mismatch')
 if sha_text(r['context'])!=r['context_sha256']: raise ValueError('context SHA mismatch')
def source_map(context):
 matches=list(re.finditer(r'\[Source ([^\]|]+)\s*\|\s*p\.([^\]]+)\]',context)); result=[]
 for i,m in enumerate(matches): result.append({'source_label':m.group(0),'source_id':m.group(1).strip(),'page':m.group(2).strip(),'start':m.start(),'end':matches[i+1].start() if i+1<len(matches) else len(context)})
 return result

def prepare_inputs(l3_root:Path,out:Path)->dict:
 l3_root=Path(l3_root).resolve(); out=Path(out).resolve(); root=l3_root.parent.parent
 if (out/'inputs-r01.json').exists(): raise FileExistsError(out)
 audit=[]
 def check(p,h,baseline):
  p=Path(p); actual=sha_file(p) if p.is_file() else None; rel=p.relative_to(root).as_posix(); exception=rel=='docs/README.md' and actual is not None and actual!=h
  audit.append({'path':rel,'expected_sha256':h,'actual_sha256':actual,'matched':h==actual,'navigation_exception':exception,'baseline':baseline})
  if actual!=h and not exception: raise ValueError('scientific asset drift: '+rel)
 for p,h in PINNED.items(): check(l3_root/p,h,'plan fixed SHA')
 for rec in read(l3_root/'delivery-manifest-r01.json')['files']: check(root/rec['path'],rec['sha256'],'L3 delivery')
 im=read(l3_root/'input-manifest.json')
 for key in ['pinned_sha256','frozen_input_sha256']:
  for p,h in im[key].items(): check(root/p,h,'L3 '+key)
 ev=root/'outputs/pearl-evidence-dev80-20261004-01'
 for rec in read(ev/'delivery-manifest-r01.json')['files']: check(root/rec['path'],rec['sha256'],'L2 delivery')
 for key in ['input_sha256','old_assets_sha256']:
  for p,h in read(ev/'stage80/input-manifest.json')[key].items(): check(root/p,h,'L2 protection '+key)
 bindings=read(l3_root/'stage80/score-bindings-r01.json')
 for rec in bindings['artifacts']: check(rec['path'],rec['sha256'],'L3 score bindings')
 records={}
 for rec in bindings['artifacts']:
  p=Path(rec['path'])
  if p.parent.name!='generation' or p.suffix!='.json': continue
  r=read(p)
  if 'raw_answer' not in r: continue
  if r['record_sha256']!=sha_text(canonical({k:v for k,v in r.items() if k!='record_sha256'})): raise ValueError('generation self hash')
  if r['cell_id'] in records: raise ValueError('duplicate physical generation')
  records[r['cell_id']]=(r,p,rec['sha256'])
 generated=[json.loads(x) for x in (l3_root/'generation/all-inputs-r01.jsonl').read_text('utf-8-sig').splitlines() if x.strip()]; validate_cells(generated)
 old=read(l3_root/'stage80/score-input-r01.json'); scored={r['intent_id']+'::'+r['arm']:r for r in old['cells']}
 rows=[]
 for g in generated:
  r,p,file_sha=records[g['cell_id']]; s=scored[g['cell_id']]
  item={k:g[k] for k in ['cell_id','intent_id','arm','query','context','context_sha256','request_sha256']}; item.update(raw_answer=r['raw_answer'],response_sha256=r['response_sha256'],generation_path=p.relative_to(root).as_posix(),generation_file_sha256=file_sha,generation_record_sha256=r['record_sha256'],source_map=source_map(g['context']))
  validate_row(item)
  if g['request']!=r['request'] or sha_text(g['request'])!=g['request_sha256']: raise ValueError('request content SHA mismatch')
  if not g['request'].endswith('Context:\n'+g['context']) or ('Question:\n'+g['query']+'\n\nContext:\n') not in g['request']: raise ValueError('query/context request association')
  if sha_text(canonical(r['messages']))!=r['messages_sha256']: raise ValueError('messages SHA mismatch')
  if sha_text(canonical(r['config']))!=r['config_sha256']: raise ValueError('config SHA mismatch')
  for key in ['request_sha256','context_sha256','response_sha256']:
   if item[key]!=s[key] or item[key]!=r[key]: raise ValueError('input/score/generation '+key)
  if r['query']!=g['query'] or r['intent_id']!=g['intent_id'] or r['arm']!=g['arm']: raise ValueError('query identity')
  rows.append(item)
 ids=set(im['intent_ids'])
 if len(rows)!=400 or len(records)!=400 or {(r['intent_id'],r['arm']) for r in rows}!={(i,a) for i in ids for a in ARMS}: raise ValueError('80x5 matrix')
 facts=[]
 for intent in sorted(ids):
  p=l3_root/'evaluation/reference-build'/f'{intent}.json'; packet=read(p)
  pure={k:packet[k] for k in ['intent_id','query','stratum','requirements','atoms','evidence_groups','sources','gold_sha256','source_scope']}
  for source in pure['sources']:
   if sha_text(source['text'])!=source['text_sha256']: raise ValueError('source text SHA')
  pure.update(schema_version='pearl-layer4-source-build-v1',input_source_path=p.relative_to(root).as_posix(),input_source_sha256=sha_file(p)); write(out/'source-build'/f'{intent}.json',pure); facts.append({'intent_id':intent,'path':str(out/'source-build'/f'{intent}.json'),'sha256':sha_file(out/'source-build'/f'{intent}.json')})
 result={'schema_version':'pearl-layer4-input-v1','cells':rows,'intent_n':80,'cell_n':400,'actual_n':320,'oracle_n':80,'original20':im['original20'],'references':facts,'l3_root':str(l3_root),'pinned_sha256':PINNED,'read_only':True}
 write(out/'protected-assets-audit-r01.json',{'verified':True,'checks':len(audit),'records':audit,'scientific_drift':0,'navigation_exception_n':sum(x['navigation_exception'] for x in audit)}); write(out/'inputs-r01.json',result)
 return {'verified':True,'cells':400,'physical_records':len(records),'protected_checks':len(audit),'source_build_packets':80}
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('l3_root',type=Path); p.add_argument('out',type=Path); a=p.parse_args(); print(json.dumps(prepare_inputs(a.l3_root,a.out)))

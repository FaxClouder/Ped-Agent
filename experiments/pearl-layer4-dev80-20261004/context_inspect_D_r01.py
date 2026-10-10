import json,re
from pathlib import Path
ROOT=Path('outputs/pearl-layer4-dev80-20261004-01')
PACK=ROOT/'packets/answerability-D300-r02'
def groups():
 grouped={}
 for p in sorted(PACK.glob('*.json')):
  x=json.loads(p.read_text('utf-8'));x['_path']=str(p);grouped.setdefault(x['query'],[]).append(x)
 return list(grouped.values())
def show(index,pattern):
 rows=groups()[index];seen={}
 print('GROUP',index,rows[0]['query'])
 for x in rows:
  print(x['blind_id'],'context_chars',len(x['context']))
  if x['context_sha256'] in seen:print('EXACT_SAME_CONTEXT_AS',seen[x['context_sha256']]);continue
  seen[x['context_sha256']]=x['blind_id'];c=x['context'];intervals=[]
  for m in re.finditer(pattern,c,re.I):
   start=max(0,c.rfind('\n\n',0,m.start())+2);end=c.find('\n\n',m.end());end=len(c) if end<0 else end
   if (start,end) not in intervals:intervals.append((start,end))
  for start,end in intervals:print(f'[{start},{end})',c[start:end])
  if not intervals:print('NO_MATCHES; context:',c)

PRINTED={}
def compact(index,pattern):
 rows=groups()[index];print('GROUP',index,rows[0]['query'])
 for x in rows:
  c=x['context'];intervals=[];seen=[]
  for m in re.finditer(pattern,c,re.I):
   start=max(0,m.start()-120);end=min(len(c),m.end()+420)
   if intervals and start<intervals[-1][1]:intervals[-1]=(intervals[-1][0],max(end,intervals[-1][1]))
   else:intervals.append((start,end))
  print(x['blind_id'],'chars',len(c))
  for start,end in intervals:
   text=c[start:end]
   if text in PRINTED:print('exact-window-repeat',PRINTED[text],f'[{start},{end})')
   else:
    tag=f'window-{len(PRINTED)+1}';PRINTED[text]=tag;print(tag,f'[{start},{end})',text)
  if not intervals:print('NO MATCHES',c[:1200], 'TAIL',c[-1200:])

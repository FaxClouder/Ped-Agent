import json,re
from pathlib import Path
ROOT=Path('outputs/pearl-layer4-dev80-20261004-01')
PACK=ROOT/'packets/grounding-D300-r02'
CITE=re.compile(r'\[(?:Source\s+)?pearl-src-[^\]]+\]|\((?:Source\s+)?pearl-src-[^\)]+\)|(?<![\w\[])Source\s+pearl-src-[a-f0-9]+\s*\|\s*p\.[\d; \-]+',re.I)
def packet(i):return json.loads((PACK/f'grounding-{i:04}.json').read_text('utf-8'))
def candidates(x):
 a=x['raw_answer'];masked=list(a)
 for m in CITE.finditer(a):
  for p in range(m.start(),m.end()):masked[p]=' '
 text=''.join(masked)
 for m in re.finditer(r'(?:Adj|Figs|Fig|et al|vs|e\.g|i\.e)\.',text):
  text=text[:m.end()-1]+' '+text[m.end():]
 spans=[];start=0
 for m in re.finditer(r'\n\s*\n|\n(?=- )|(?<=[.!?])\s+(?=[A-Z*])|;\s+(?=(?:the |[A-Z]|vn =|vf =))| and (?=vn =)',text):
  spans.append((start,m.start()));start=m.end()
 spans.append((start,len(a)));result=[]
 for start,end in spans:
  while start<end and (text[start].isspace() or text[start] in '*-'):start+=1
  while end>start and text[end-1].isspace():end-=1
  if start>=end:continue
  quote=a[start:end];result.append({'candidate_id':len(result)+1,'start':start,'end':end,'quote':quote,'clean':re.sub(r'\s+',' ',CITE.sub('',quote)).strip()})
 return result
if __name__=='__main__':
 import sys
 for i in map(int,sys.argv[1:]):
  x=packet(i);print('\nPACKET',i,x['query'])
  for c in candidates(x):print(c['candidate_id'],c['quote'])

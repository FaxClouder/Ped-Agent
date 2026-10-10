import re,hashlib
from grounding_inspect_D_r01 import packet
from citations import source_spans
SEEN={}
def view(i,pattern,limit=5):
 x=packet(i);print('PACK',i,x['query'])
 for s in source_spans(x['context']):
  text=x['context'][s['start']:s['end']];matches=list(re.finditer(pattern,text,re.I|re.S))
  if not matches:continue
  print(s['source_label'],s['start'],s['end'],'matches',len(matches))
  for m in matches[:limit]:
   a=max(0,m.start()-80);b=min(len(text),m.end()+180);t=text[a:b];h=hashlib.sha256(t.encode()).hexdigest()
   if h in SEEN:print(' exact repeat',SEEN[h])
   else:SEEN[h]=f'{i}:{s["start"]+a}:{s["start"]+b}';print(s['start']+a,s['start']+b,repr(t))

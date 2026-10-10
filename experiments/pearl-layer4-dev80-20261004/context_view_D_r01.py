"""Context-only literal-location viewer, with exact excerpt deduplication."""
import re,hashlib
from context_inspect_D_r01 import groups
SEEN={}
def view(i,patterns):
 rs=groups()[i];print('\nGROUP',i,rs[0]['query'],'REQUIREMENTS',rs[0]['requirements'])
 for x in rs:
  print(x['blind_id'],'chars',len(x['context']))
  for j,pat in enumerate(patterns):
   ms=list(re.finditer(pat,x['context'],re.I|re.S));print(' req',j,'matches',len(ms))
   for m in ms[:3]:
    a=max(0,m.start()-100);b=min(len(x['context']),m.end()+180);t=x['context'][a:b];h=hashlib.sha256(t.encode()).hexdigest()
    if h in SEEN:print(' exact excerpt repeat',SEEN[h],a,b)
    else:SEEN[h]=f"{x['blind_id']}:{a}:{b}";print(a,b,repr(t))

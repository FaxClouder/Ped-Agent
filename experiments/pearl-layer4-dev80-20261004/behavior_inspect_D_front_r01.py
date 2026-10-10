import json,hashlib,re,sys
from pathlib import Path
ROOT=Path('outputs/pearl-layer4-dev80-20261004-01')
def packet(i):
 p=ROOT/'packets/behavior-D300-r02'/f'behavior-{i:04d}.json';x=json.loads(p.read_text(encoding='utf-8'))
 g=ROOT/'packets/grounding-D300-r02'/f'grounding-{i:04d}.json';y=json.loads(g.read_text(encoding='utf-8'))
 assert x['raw_answer']==y['raw_answer'] and x['context']==y['context']
 return x,p,g
def show(a,b):
 for i in range(a,b+1):
  x,p,g=packet(i);print(i,x['query']);print('NECESSARY',*[r['claim'] for r in x['requirements']],sep=' | ')
  print('ANSWER start',x['raw_answer'][:400]);print('LIMIT/REFUSAL',*[x['raw_answer'][max(0,m.start()-100):min(len(x['raw_answer']),m.end()+350)] for m in re.finditer(r'cannot|not establish|does not provide|unable|limitation|not available|insufficient|not specify|not supported',x['raw_answer'],re.I)],sep=' | ')
if __name__=='__main__':show(int(sys.argv[1]),int(sys.argv[2]))

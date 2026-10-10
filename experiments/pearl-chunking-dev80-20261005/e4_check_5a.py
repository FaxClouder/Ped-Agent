import json,hashlib,sys
from pathlib import Path
R=Path('.').resolve()
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
run=R/'outputs/pearl-chunking-dev80-20261006-12'
st=json.load(open(R/'outputs/pearl-chunking-chain-20261006/status-5A.json',encoding='utf8'))
m=json.load(open(run/'delivery-manifest.json',encoding='utf8'))
dv=json.load(open(run/'delivery-verification-r02.json',encoding='utf8'))
drift=[n for n,h in m['artifacts_sha256'].items() if not (R/n).is_file() or sha(R/n)!=h]
sel=json.load(open(run/'e2-overlap-selection-r01.json',encoding='utf8'))
out=dict(status='passed' if not drift and sha(run/'delivery-manifest.json')==st['delivery_manifest_sha256'] and dv['status']=='passed' else 'failed',
 status_5A_sha256=sha(R/'outputs/pearl-chunking-chain-20261006/status-5A.json'),manifest_sha256=sha(run/'delivery-manifest.json'),manifest_expected=st['delivery_manifest_sha256'],
 delivery_verification_status=dv['status'],artifacts_checked=len(m['artifacts_sha256']),drift=drift,
 selection={k:dict(status=v['status'],selected=v['selected'],threats=v['threats'],order=v.get('order')) for k,v in sel['cores'].items()},first_choice_for_5B=sel['first_choice_for_5B'],
 mapping_sha256=sel['mapping_sha256'],mapping_file_sha256=sha(run/'common-support-map-e2-r11.json'),selection_sha256=sha(run/'e2-overlap-selection-r01.json'))
p=R/'outputs/pearl-chunking-dev80-20261006-13/input-check-5A-r01.json'
with open(p,'x',encoding='utf8',newline='\n') as f:json.dump(out,f,ensure_ascii=False,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if k!='drift'},ensure_ascii=False),len(drift))

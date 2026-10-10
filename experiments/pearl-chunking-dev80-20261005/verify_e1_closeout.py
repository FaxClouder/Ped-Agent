"""Reopen final delivery and independently check binary counts/tests and links."""
import argparse
import json
import re
from pathlib import Path
from scipy.stats import binomtest
from runtime import ROOT,EXP,sha,save_json

def verify(output):
    load=lambda p:json.loads(Path(p).read_text('utf8'))
    manifest=load(output/'delivery-manifest.json');drift=[]
    for name,expected in {**manifest['inputs'],**manifest['artifacts_sha256']}.items():
        if not (ROOT/name).is_file() or sha(ROOT/name)!=expected:drift.append(name)
    if drift:raise ValueError('Delivery drift '+str(drift))
    stats=load(output/'statistics-e1-r07-closeout-r01.json');run=ROOT/'outputs/pearl-chunking-dev80-20261005-07';lookups={}
    for c in {r['configuration_id'] for r in stats['overall']}:
        rows=[json.loads(s) for s in (run/('index-'+c)/'score-details-e1-r07.jsonl').read_text('utf8').splitlines()]
        lookups[c]={(r['intent_id'],r['cell']):r for r in rows}
    panel_cell={'R4_CEGR10':'layer1_raw/R4/10','P0_CGC4096':'fixed_budget_main/P0/4096/final','P0_CGC8192':'fixed_budget_main/P0/8192/final'}
    checked=[]
    for row in stats['paired']:
        cell=panel_cell[row['panel']];a=lookups[row['configuration_id']];b=lookups[row['baseline']]
        ids=sorted(i for i,s in a if s==cell);assert len(ids)==80
        gain=sum(a[i,cell]['sufficient']=='yes' and b[i,cell]['sufficient']=='no' for i in ids)
        loss=sum(a[i,cell]['sufficient']=='no' and b[i,cell]['sufficient']=='yes' for i in ids)
        assert (gain,loss)==(row['confirmed_gains'],row['confirmed_losses'])
        lo=sum(int(a[i,cell]['sufficient']=='yes')-int(b[i,cell]['sufficient']!='no') for i in ids)/80
        hi=sum(int(a[i,cell]['sufficient']!='no')-int(b[i,cell]['sufficient']=='yes') for i in ids)/80
        assert max(abs(x-y) for x,y in zip((lo,hi),row['possible_delta_interval']))<1e-12
        if row['binary']:
            p=binomtest(gain,gain+loss,.5,alternative='two-sided').pvalue if gain+loss else 1.
            assert abs(p-row['mcnemar_exact_p'])<1e-12
        else:assert row['mcnemar_exact_p'] is None
        checked.append(dict(configuration_id=row['configuration_id'],baseline=row['baseline'],panel=row['panel']))
    family=sorted([r for r in stats['paired'] if r['family']=='baseline_family' and r['binary']],key=lambda r:r['mcnemar_exact_p'])
    previous=0.
    for rank,row in enumerate(family):
        previous=max(previous,min(1.,(len(family)-rank)*row['mcnemar_exact_p']))
        assert abs(previous-row['holm_p'])<1e-12
    assert len(family)==24
    link_count=0
    for doc in (EXP/'README.md',EXP/'session3-closeout-2026-10-06.md',output/'handoff.md'):
        for target in re.findall(r'\]\(([^)]+)\)',doc.read_text('utf8')):
            if '://' in target or target.startswith('#'):continue
            path=(doc.parent/target.split('#')[0]).resolve()
            if path==output/'delivery-verification-r01.json':continue
            assert path.exists(),str(path);link_count+=1
        text=doc.read_text('utf8');assert len(re.findall(r'^# ',text,re.M))==1
        assert 'status: current' in text
    receipt=dict(status='passed',manifest_sha256=sha(output/'delivery-manifest.json'),artifacts_checked=len(manifest['artifacts_sha256']),input_bindings_checked=len(manifest['inputs']),drift=[],paired_rows_independently_checked=len(checked),exact_binary_test_reference='scipy.stats.binomtest two-sided',holm_family_size=24,links_checked=link_count,final_verification_self_link='Written below with exclusive creation; file exists on successful return.',E3_units=0)
    save_json(output/'delivery-verification-r01.json',receipt)
    assert (output/'delivery-verification-r01.json').is_file()
    print(json.dumps(receipt,ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();verify(a.output.resolve())

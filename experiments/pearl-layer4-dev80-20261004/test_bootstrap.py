import importlib.util
from pathlib import Path

def test_unknown_paired_difference_uses_opposing_bounds():
    spec=importlib.util.spec_from_file_location('bootstrap_l4',Path(__file__).with_name('bootstrap.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    arms=['A0-4096','A0-8192','A1-4096','A1-8192','Aref-8192']
    rows=[]
    for arm in arms:
        bounds=[.4,.8] if arm=='A1-4096' else [.2,.6]
        rows.append(dict(intent_id='one',arm=arm,stratum='single',**{key:bounds for key in ('faithfulness','unsupported_rate','context_contradiction_rate','factuality')}))
    result=m.paired_bootstrap(rows,iterations=10)['results'][0]
    assert abs(result['lower']['difference']-(-.2))<1e-12
    assert abs(result['upper']['difference']-.6)<1e-12

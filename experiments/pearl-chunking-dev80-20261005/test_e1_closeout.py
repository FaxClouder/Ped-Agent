"""Fixed paired numerical examples and heterogeneous historical manifest gates."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import pytest
import e1_closeout as closeout
from runtime import save_json,sha

def test_exact_binary_reference_and_holm_family():
    assert closeout.exact_mcnemar(7,0)==0.015625
    assert closeout.exact_mcnemar(6,3)==0.5078125
    assert closeout.exact_mcnemar(0,0)==1
    assert closeout.holm([0.015625]+[1]*23)==[0.375]+[1]*23

def test_manifest_artifacts_and_nested_gate_inputs(tmp_path,monkeypatch):
    monkeypatch.setattr(closeout,'ROOT',tmp_path)
    p=tmp_path/'file.txt';p.write_text('frozen',encoding='utf8')
    old=tmp_path/'old';old.mkdir();save_json(old/'delivery-manifest.json',{'artifacts_sha256':{'file.txt':sha(p)},'inputs':{'phase_code_sha256':{'a.py':'metadata'}}})
    assert closeout.verify_manifest(old)['checked']==1
    gate=tmp_path/'gate';gate.mkdir();save_json(gate/'delivery-manifest.json',{'inputs':{'plan':{'path':'file.txt','sha256':sha(p)}}})
    assert closeout.verify_manifest(gate)['checked']==1
    p.write_text('drift',encoding='utf8')
    with pytest.raises(ValueError,match='Frozen output drift'):closeout.verify_manifest(gate)

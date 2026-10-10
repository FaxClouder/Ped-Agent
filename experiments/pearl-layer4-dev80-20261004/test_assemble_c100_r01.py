import importlib.util,json
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('assembly',Path(__file__).with_name('assemble_c100_r01.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def claim(cid='a'):
 return dict(claim_id=cid,start=0,end=2,quote='ab',normalized_claim='ab',conditions={'unit':'m'},occurrences=[{'start':0,'end':2,'quote':'ab'}])
def test_alias_id_change_only(tmp_path):
 p=tmp_path/'origin.json';p.write_text('{}');x=m.exact_aliases([claim('new')],[claim('old')],p)[0]
 assert x['status']=='exact_atom_reusable' and x['origin_claim_ids']==['old'] and x['origin_sha256']==m.sha(p)
@pytest.mark.parametrize('field,value',[('quote','zz'),('normalized_claim','zz'),('conditions',{'unit':'cm'}),('occurrences',[])])
def test_changed_atom_never_reuses(tmp_path,field,value):
 p=tmp_path/'origin.json';p.write_text('{}');c=claim();c[field]=value
 assert m.exact_aliases([c],[claim()],p)[0]['status']=='requires_actual_review'
def test_duplicate_origin_ambiguous(tmp_path):
 p=tmp_path/'origin.json';p.write_text('{}')
 assert m.exact_aliases([claim()],[claim('x'),claim('y')],p)[0]['status']=='requires_actual_review'
def test_selected_outside_chain_rejected(tmp_path):
 with pytest.raises(ValueError,match='outside'):m.selected({'primary_path':'a','secondary_path':'b','selected_path':'c'})
def test_missing_review_fails():
 with pytest.raises(ValueError,match='missing'):m.selected({'primary_path':'no-such-review','selected_path':'no-such-review'})
def test_exclusive_write(tmp_path):
 p=tmp_path/'x';m.write(p,{'a':1})
 with pytest.raises(FileExistsError):m.write(p,{'a':2})
 assert json.loads(p.read_text())=={'a':1}
def test_finalize_checks_original_sha(tmp_path):
 p=tmp_path/'p';p.write_text('original');s=tmp_path/'b';m.write(s,{'artifacts':[{'path':str(p),'sha256':m.sha(p)}],'result_path':str(tmp_path/'r')});p.write_text('changed')
 with pytest.raises(ValueError,match='changed'):m.finalize_bindings(s,tmp_path/'out')
def test_finalize_requires_saved_result(tmp_path):
 s=tmp_path/'b';m.write(s,{'artifacts':[],'result_path':str(tmp_path/'r')})
 with pytest.raises(ValueError,match='missing'):m.finalize_bindings(s,tmp_path/'out')

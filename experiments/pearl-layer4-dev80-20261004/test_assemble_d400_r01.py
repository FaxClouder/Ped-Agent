import copy
import pytest
from assemble_d400_r01 import validate_sampling
from verify_d400_r01 import validate_fixed_sampling
def fixture():
 fixed={'D300_shuffled_cell_ids':[f'd{i}' for i in range(300)],'D60_secondary_cell_ids':[f'd{i}' for i in range(4,300,5)]}
 rows=[{'cell_id':c,'chains':{t:{'primary_path':'p',**({'secondary_path':'s'} if c in fixed['D60_secondary_cell_ids'] else {})} for t in ('answerability','grounding','factuality','behavior')}} for c in fixed['D300_shuffled_cell_ids']]
 return fixed,rows
def test_real_60_only():
 f,r=fixture();assert len(validate_sampling(r,f))==60
def test_fake_secondary_rejected():
 f,r=fixture();r[0]['chains']['grounding']['secondary_path']='s'
 with pytest.raises(ValueError,match='secondary'):validate_sampling(r,f)
def test_sampled_missing_rejected():
 f,r=fixture();del r[4]['chains']['behavior']['secondary_path']
 with pytest.raises(ValueError,match='secondary'):validate_sampling(r,f)
def test_duplicate_cell_rejected():
 f,r=fixture();r[-1]=copy.deepcopy(r[0])
 with pytest.raises(ValueError,match='selection'):validate_sampling(r,f)
def test_missing_task_rejected():
 f,r=fixture();del r[0]['chains']['behavior']
 with pytest.raises(ValueError,match='four'):validate_sampling(r,f)
def test_independent_sampling_gate(tmp_path):
 import json,hashlib
 f,r=fixture();p=tmp_path/'fixed';p.write_text(json.dumps(f));b={'secondary_sampling':{'stage_selection_path':str(p),'stage_selection_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sampled_cell_ids':f['D60_secondary_cell_ids'],'primary_only_cell_ids':sorted(set(f['D300_shuffled_cell_ids'])-set(f['D60_secondary_cell_ids']))},'review_chain':[{'cell_id':x['cell_id'],'task':t,**ch} for x in r for t,ch in x['chains'].items()]}
 assert validate_fixed_sampling(b)['primary_only_cell_n']==240
 b['review_chain'][0]['secondary_path']='fake'
 with pytest.raises(ValueError,match='sampling'):validate_fixed_sampling(b)

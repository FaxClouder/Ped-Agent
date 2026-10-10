import importlib.util
from pathlib import Path
import pytest
BASE=Path(__file__).parent

def load(name):
 s=importlib.util.spec_from_file_location('l4_'+name, BASE/(name+'.py')); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def test_duplicate_cell():
 with pytest.raises(ValueError,match='duplicate'): load('prepare').validate_cells([{'cell_id':'i::a'},{'cell_id':'i::a'}])
def test_answer_hash():
 with pytest.raises(ValueError,match='response'): load('prepare').validate_row({'raw_answer':'a','response_sha256':'bad','context':'x','context_sha256':'bad'})
def test_context_hash_parent_backfill():
 p=load('prepare')
 with pytest.raises(ValueError,match='context'): p.validate_row({'raw_answer':'a','response_sha256':p.sha_text('a'),'context':'expanded parent','context_sha256':p.sha_text('actual child')})
def test_blind_score_rejected():
 with pytest.raises(ValueError,match='forbidden'): load('review').validate_packet({'blind_id':'b','query':'q','context':'c','score':1},'answerability')
def test_blind_answer_rejected():
 with pytest.raises(ValueError,match='forbidden'): load('review').validate_packet({'blind_id':'b','query':'q','context':'c','raw_answer':'a'},'answerability')
def test_extract_intervals():
 m=load('extract'); p=m.extract_answer('Speed is 1 m/s. [Source s | p.2]'); assert p['candidates']; assert all('Speed is 1 m/s. [Source s | p.2]'[c['start']:c['end']]==c['quote'] for c in p['candidates'])


def test_nested_score_rejected():
 with pytest.raises(ValueError,match='forbidden'): load('review').validate_packet({'blind_id':'b','claims':[{'score':1}]},'grounding')
def test_factuality_context_rejected():
 with pytest.raises(ValueError,match='forbidden'): load('review').validate_packet({'blind_id':'b','context':'parent','claims':[]},'factuality')
def test_source_intervals_exact():
 p=load('prepare'); text='[Source s1 | p.1]\none\n[Source s2 | p.2]\ntwo'; sources=p.source_map(text)
 assert len(sources)==2 and text[sources[0]['start']:sources[0]['end']]=='[Source s1 | p.1]\none\n'
 assert sources[1]['source_id']=='s2' and sources[1]['end']==len(text)
def test_unknown_task_rejected(tmp_path):
 with pytest.raises(ValueError,match='task'): load('review').export_packets([], 'combined',1,tmp_path)
def test_exclusive_output(tmp_path):
 p=load('prepare'); path=tmp_path/'x.json'; p.write(path,{'a':1})
 with pytest.raises(FileExistsError): p.write(path,{'a':2})
 assert p.read(path)=={'a':1}

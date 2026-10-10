import json
import pytest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from runtime import load_queries, cache_identity, build_fts, verify_index, save_json

def test_queries_no_gold(tmp_path):
    p=tmp_path/'q.jsonl'
    p.write_text(json.dumps({'intent_id':'i','query':'real question','atoms':[]})+'\n')
    with pytest.raises(ValueError): load_queries(p,1)
    p.write_text(json.dumps({'intent_id':'i','query':'real question'})+'\n')
    assert len(load_queries(p,1))==1

def test_each_identity_changes_cache():
    d=dict(source='s',chunker='c',prefix='m',model='w',budget=4096,mapping='a')
    h=cache_identity(d)
    for key in d:
        assert cache_identity(dict(d,**{key:str(d[key])+'different'}))!=h

def test_independent_fts_and_hash_gate(tmp_path):
    rows=[dict(chunk_id='x',resource_id='d',version_id='v',title='',heading_path=[],text='density flow relationship',locator='{}')]
    p=tmp_path/'fts.sqlite3'
    build_fts(p,rows,{'policy':'C1'})
    with pytest.raises(FileExistsError): build_fts(p,rows,{'policy':'C2'})
    import hashlib
    m={'output_sha256':{'fts.sqlite3':hashlib.sha256(p.read_bytes()).hexdigest()}}
    save_json(tmp_path/'manifest.json',m)
    assert verify_index(tmp_path/'manifest.json')['status']=='passed'
    p.write_bytes(p.read_bytes()+b'drift')
    with pytest.raises(ValueError):verify_index(tmp_path/'manifest.json')

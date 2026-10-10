import importlib.util
from pathlib import Path
import pytest


def module():
    path = Path(__file__).with_name('prepare.py')
    assert path.exists(), 'offline prepare implementation is missing'
    spec = importlib.util.spec_from_file_location('answer_prepare', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generation_projects_only_query_and_exact_context():
    m = module()
    row = {'intent_id':'i1','configuration':'C0-4096','query':'Q','serialized_context':'α\n exact ','text_sha256':m.sha_text('α\n exact '),'reference_answer':'SECRET','support':'yes'}
    result = m.generation_row(row)
    assert result['context'] == row['serialized_context']
    assert result['arm'] == 'A0-4096'
    assert 'SECRET' not in str(result)
    assert result['request_sha256'] == m.sha_text(result['request'])
    assert set(result) == {'cell_id','intent_id','arm','query','context','context_sha256','request','request_sha256'}


def test_context_digest_mismatch_rejected():
    m = module()
    with pytest.raises(ValueError, match='context hash'):
        m.generation_row({'intent_id':'i','configuration':'C0-4096','query':'Q','serialized_context':'x','text_sha256':'bad'})


@pytest.mark.parametrize('rows', [[('i','A0-4096')], [('i',a) for a in ['A0-4096','A0-8192','A1-4096','A1-8192']] + [('i','A0-4096')]])
def test_missing_and_duplicate_cells_rejected(rows):
    with pytest.raises(ValueError):
        module().validate_cells([{'intent_id':i,'arm':a} for i,a in rows], ['i'])


def test_scientific_hash_mismatch_fatal_navigation_disclosed(tmp_path):
    m = module()
    (tmp_path/'science').write_text('frozen')
    (tmp_path/'docs').mkdir()
    (tmp_path/'docs/README.md').write_text('new navigation')
    files = [{'path':'science','sha256':m.sha_text('frozen')},{'path':'docs/README.md','sha256':'old'}]
    result = m.audit_files(tmp_path, files)
    assert result['matched'] == 1 and result['navigation_changes'][0]['path']=='docs/README.md'
    (tmp_path/'science').write_text('changed')
    with pytest.raises(ValueError, match='frozen file'):
        m.audit_files(tmp_path, files)


def test_reference_packet_whitelist_and_exact_source_bytes(tmp_path):
    m = module()
    text = 'Original α source 1.2 m/s'
    chunk = {'source_id':'s','chunk_id':'p','text':text,'text_sha256':m.sha_text(text),'source_sha256':'pdfsha','page_start':1,'page_end':2,'locator':'p.1-2','title':'Title','version_id':'v','parser_version':'adobe','policy_version':'v1'}
    intent = {'intent_id':'i','query':'Q','main_stratum':'numeric','requirements':[{'requirement_id':'r','claim':'Target','support_bundles':[['a']]}], 'atoms':[{'atom_id':'a','source_id':'s','anchor_text':'1.2','page':1,'supports':'Target'}],'evidence_groups':[{'group_id':'g','requirements':['r']}], 'reference_answer':'FORBIDDEN','review_note':'FORBIDDEN'}
    packet = m.reference_packet(intent, [dict(chunk, jsonl_byte_start=0,jsonl_byte_end=10)], 'goldsha')
    assert 'FORBIDDEN' not in str(packet)
    assert packet['sources'][0]['text']==text
    assert packet['sources'][0]['jsonl_byte_end']==10
    assert packet['atoms'][0]['atom_id']=='a'


def test_new_artifact_write_refuses_overwrite(tmp_path):
    m=module()
    p=tmp_path/'x.json'
    m.write_new_json(p, {'x':1})
    with pytest.raises(FileExistsError): m.write_new_json(p, {'x':2})

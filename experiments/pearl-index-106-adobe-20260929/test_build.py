import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest


def runner():
    path = Path(__file__).with_name('build.py')
    assert path.exists(), 'isolated build runner is not implemented'
    spec = importlib.util.spec_from_file_location('pearl_index_build', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exact_member_selection_excludes_foreign_sources_and_rejects_duplicates():
    m = runner()
    sources = [{'source_id': 's', 'sha256': 'abc'}]
    verified = {'source_count': 1, 'sources': [{'source_id': 's', 'source_sha256': 'abc', 'parser_version': m.PARSER}]}
    assert list(m.validate_members(sources, verified, expected_count=1)) == ['abc']
    with pytest.raises(ValueError, match='duplicate'):
        m.validate_members(sources * 2, verified, expected_count=2)
    with pytest.raises(ValueError, match='membership'):
        m.validate_members([{'source_id': 's', 'sha256': 'foreign'}], verified, expected_count=1)
    verified['sources'][0]['parser_version'] = 'pymupdf'
    with pytest.raises(ValueError, match='Adobe'):
        m.validate_members(sources, verified, expected_count=1)


def test_body_only_fts_unique_or_tokens_and_stable_ties(tmp_path):
    m = runner()
    rows = [dict(chunk_id=i, resource_id='r', version_id='v', locator='{}',
                 text=text, title='UNIQUE_TITLE', heading_path=['UNIQUE_HEADING'])
            for i, text in [('b', 'pedestrian flow'), ('a', 'pedestrian flow'), ('c', 'bottleneck')]]
    path = tmp_path / 'fts.sqlite3'
    m.build_fts(path, rows, 'digest', 'revision')
    assert m.sparse_query(path, 'UNIQUE_TITLE UNIQUE_HEADING') == []
    results = m.sparse_query(path, 'Pedestrian pedestrian')
    assert [r['chunk_id'] for r in results] == ['a', 'b']
    assert results == m.sparse_query(path, 'pedestrian')
    assert {r['chunk_id'] for r in m.sparse_query(path, 'pedestrian bottleneck')} == {'a', 'b', 'c'}
    assert m.EnglishLexicalAnalyzer().analyze('ＦＬＯＷ pedestrian-flow 1.25 m2 中文') == ['flow', 'pedestrian', 'flow', '1', '25', 'm', '2']
    with pytest.raises(ValueError, match='duplicate'):
        m.build_fts(tmp_path / 'bad.sqlite3', rows + rows[:1], 'digest', 'revision')
    m.verify_fts(path, rows)
    with sqlite3.connect(path) as conn:
        conn.execute("UPDATE documents SET body='corrupted' WHERE chunk_id='a'")
    with pytest.raises(ValueError, match='FTS content'):
        m.verify_fts(path, rows)


def test_vectors_and_exact_tie_breaking():
    import numpy as np
    m = runner()
    vectors = np.zeros((2, 1024), dtype=np.float32)
    vectors[:, 0] = 1
    m.validate_vectors(vectors, 2)
    assert [x['chunk_id'] for x in m.exact_dense(vectors, vectors[0], ['b', 'a'])] == ['a', 'b']
    rows = [dict(chunk_id='b', text='text', source_id='s', text_sha256=m.text_sha('text')),
            dict(chunk_id='a', text='other', source_id='s', text_sha256=m.text_sha('other'))]
    assert m.content_digest(rows, vectors) == m.content_digest(rows[::-1], vectors[::-1])
    changed = [dict(rows[0], text='changed'), rows[1]]
    assert m.content_digest(rows, vectors) != m.content_digest(changed, vectors)
    vectors[0, 0] = float('nan')
    with pytest.raises(ValueError, match='finite'):
        m.validate_vectors(vectors, 2)


def test_existing_output_is_never_reused(tmp_path):
    m = runner()
    with pytest.raises(FileExistsError):
        m.create_output(tmp_path)

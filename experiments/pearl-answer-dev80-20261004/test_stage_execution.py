import importlib.util
from pathlib import Path

import pytest


def stage_module():
    path=Path(__file__).resolve().parents[2]/'outputs/pearl-answer-dev80-20261004-01/run_generation_stage_r02.py'
    assert path.exists(), 'pre-request matrix guard missing'
    spec=importlib.util.spec_from_file_location('stage_guard',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def sample():
    arms=['A0-4096','A0-8192','A1-4096','A1-8192','Aref-8192']
    return [{'cell_id':'i::'+a,'intent_id':'i','arm':a} for a in arms]


def test_expected_matrix_checked_before_any_provider_work():
    m=stage_module();cells=sample();refs=[{'intent_id':'i','oracle_eligible':True}]
    m.validate_stage_cells(cells,['i'],refs)
    for bad in [cells[:-1],cells+[cells[0]],cells+[{**cells[0],'intent_id':'other'}]]:
        with pytest.raises(ValueError):m.validate_stage_cells(bad,['i'],refs)
    with pytest.raises(ValueError):m.validate_stage_cells([{**cells[0],'cell_id':'wrong'}]+cells[1:],['i'],refs)


def test_identical_request_does_not_authorize_different_cell_reuse():
    m=stage_module();c=sample()[0]
    m.validate_reuse_identity(c,dict(c))
    with pytest.raises(ValueError):m.validate_reuse_identity(c,{**c,'arm':'A1-4096'})

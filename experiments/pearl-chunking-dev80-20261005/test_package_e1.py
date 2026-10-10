import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).parent))
from package_e1 import validate_stage

def good():
    matrix=dict(status='passed',configuration_count=13,failed_configurations=[],generation_calls=0)
    scores=dict(details_count=22880,summaries=[dict(n=80,failure_n=0) for _ in range(286)],execution=[dict(status='scored',retrieved=80,assembled=160,retrieval_failed=0,assembly_failed=0) for _ in range(13)])
    verify=dict(status='passed',rankings=1040,contexts=2080,score_details=22880)
    return matrix,scores,verify

def test_failure_or_missing_cell_cannot_be_sealed_as_complete():
    args=good();assert validate_stage(*args)
    args[0]['failed_configurations']=['C4-L512-O0-M0']
    with pytest.raises(ValueError):validate_stage(*args)
    args=good();args[1]['execution'][0]['retrieved']=79
    with pytest.raises(ValueError):validate_stage(*args)

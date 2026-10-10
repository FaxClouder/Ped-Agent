"""Independent population/identity counterexamples using fixed finite vectors."""
from copy import deepcopy
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).parent))
from source_view import build_source_view,digest
from semantic_threshold import freeze_threshold
from audit_assets import check_calibration_population


@pytest.fixture
def calibration():
    views=[build_source_view(dict(doc_id="d",source_version="v",elements=[dict(element_id="e",element_type="paragraph",text="First. Second. Third. Fourth.",heading_path=[],order=0)]))]
    vectors=np.asarray([[1,0],[0,1],[1,0],[-1,0]],dtype=np.float32)
    class FixedVectors:
        def encode(self,texts):
            assert len(texts)==4
            return vectors
    return freeze_threshold(views,None,FixedVectors()),views,vectors


def reseal(manifest):
    manifest["manifest_sha256"]=digest({k:v for k,v in manifest.items() if k!="manifest_sha256"})


def test_full_fixed_calibration_population_accepted(calibration):
    manifest,views,vectors=calibration
    check_calibration_population(manifest,views,vectors)


@pytest.mark.parametrize("tamper",["pair_omission","sentence_omission","vector_bytes","internal_hash","sentence_hash","distance_representation","source_view_hash"])
def test_semantic_population_or_identity_tamper_rejected(calibration,tamper):
    original,views,original_vectors=calibration
    manifest=deepcopy(original);vectors=original_vectors.copy()
    if tamper=="pair_omission":
        manifest["pairs"].pop()
        manifest["distance_values"]=[p["distance"] for p in manifest["pairs"]]
        manifest["distances"]={p["right"]:p["distance"] for p in manifest["pairs"]}
        manifest["threshold"]=float(np.quantile(manifest["distance_values"],.9,method="linear"))
        reseal(manifest)
    elif tamper=="sentence_omission":
        manifest["sentences"].pop();reseal(manifest)
    elif tamper=="vector_bytes":
        vectors[0,0]=.5
    elif tamper=="internal_hash":
        manifest["manifest_sha256"]="incorrect"
    elif tamper=="sentence_hash":
        manifest["sentence_sha256"]="incorrect";reseal(manifest)
    elif tamper=="distance_representation":
        manifest["distance_values"][0]=7.;reseal(manifest)
    else:
        manifest["view_sha256s"]=["incorrect"];reseal(manifest)
    with pytest.raises(ValueError):
        check_calibration_population(manifest,views,vectors)

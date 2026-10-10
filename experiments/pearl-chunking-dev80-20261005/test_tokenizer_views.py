"""Real pinned-tokenizer regression; distinct counting and forward representations."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
import pytest
from audit_assets import check_model_input
from ped_knowledge.tokenization import HuggingFaceTokenCounter

def test_model_tokenizer_trailing_space_is_audited_exactly():
    from transformers import AutoTokenizer
    path=Path('memPed/knowledge/models/bge-m3')
    model_tokenizer=AutoTokenizer.from_pretrained(str(path),local_files_only=True)
    counter=HuggingFaceTokenCounter.from_local_path(path)
    text='The fundamental diagram. '
    actual=model_tokenizer(text,add_special_tokens=True,truncation=False)['input_ids']
    counting=counter.encode(text)
    assert actual!=counting
    row={'sentence_index':18,'input_ids':actual,'actual_forward_inputs_verified':True,'truncated':False}
    assert check_model_input(text,row,model_tokenizer,18)
    row['input_ids']=counting
    with pytest.raises(ValueError):check_model_input(text,row,model_tokenizer,18)

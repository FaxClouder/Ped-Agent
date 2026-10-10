import pytest
from smoke import counter
from e3_token_memo import ExactCountMemo

def test_actual_frozen_tokenizer_pipeline_counts_all_unicode_prefixes():
    c=counter();memo=ExactCountMemo(c._tokenizer)
    text='[Source [["d","v","e",0,391]]]\nUnicode 疏散 é Å ﬁ ² \n  严格条件；关系。 rarewordxyz 👍🏽\n<mask> <s> </s>'
    for n in range(len(text)+1):assert memo.fast_count(text[:n])==c.count(text[:n])
    text='[Source [["d","v","e",0,999]]]\nThe relation must hold under the stated conditions.\n\n'*20
    assert [len(e.ids) for e in memo.encode_batch([text[:n] for n in range(len(text)+1)])]==[c.count(text[:n]) for n in range(len(text)+1)]

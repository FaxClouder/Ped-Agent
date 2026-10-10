"""Exact Unigram token-count memoization at the frozen pretokenizer boundary.

No prefix is skipped. Every candidate is normalized and pretokenized by the
original Rust backend; identical pretokenized segments reuse original model
tokenization. Added-token strings use the original whole encoding. Exact public
whole-context encoding still rechecks the chosen prefix in e1_batch.
"""
from functools import lru_cache
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
import e3_cached
from smoke import counter as real_counter
from runtime import ROOT,sha,save_json

class ExactCountMemo:
    def __init__(self,tokenizer):
        self.original=tokenizer;config=json.loads(tokenizer.to_str())
        assert config['model']['type']=='Unigram' and config['pre_tokenizer']==dict(type='Metaspace',replacement='▁',prepend_scheme='always',split=True)
        assert config['truncation'] is None and config['padding'] is None
        assert config['post_processor']['single']==[{'SpecialToken':{'id':'<s>','type_id':0}},{'Sequence':{'id':'A','type_id':0}},{'SpecialToken':{'id':'</s>','type_id':0}}]
        self.added=tuple(a['content'] for a in config['added_tokens'])
        self.segment_count=lru_cache(maxsize=100000)(lambda text:len(tokenizer.model.tokenize(text)))

    def encode(self,*args,**kwargs):return self.original.encode(*args,**kwargs)
    def fast_count(self,text):
        if any(a in text for a in self.added):return len(self.original.encode(text).ids)
        normalized=self.original.normalizer.normalize_str(text)
        if any(a in normalized for a in self.added):return len(self.original.encode(text).ids)
        return 2+sum(self.segment_count(piece) for piece,_ in self.original.pre_tokenizer.pre_tokenize_str(normalized))
    def encode_batch(self,texts):return [SimpleNamespace(ids=range(self.fast_count(t))) for t in texts]

def fast_counter():
    c=real_counter();c._tokenizer=ExactCountMemo(c._tokenizer);return c

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--attempt',type=Path,required=True);a=p.parse_args()
    e3_cached.counter=fast_counter
    def save_with_driver(path,value):
        if path.name=='runtime-r01.json':
            value['assembly_driver']='e3_token_memo.py -> e3_cached.py'
            value['code_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(__file__)
            value['token_count_acceleration']='Original normalizer, Metaspace pretokenizer, Unigram model; memo identical pretokenized segments. All candidates checked; selected candidate original encode recheck.'
        save_json(path,value)
    e3_cached.save_json=save_with_driver
    e3_cached.run(a.output.resolve(),a.attempt.resolve())

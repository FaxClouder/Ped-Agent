"""Query-only stub model backend; real retrieval algorithms, no Gold custody."""
from pathlib import Path
import numpy as np
from runtime import algorithm, read, rows

class Backend:
    """Real FTS5, normalized float32 exact dot product, fixed RRF; stub model inference."""
    def __init__(self,c):
        self.old=algorithm();self.index=Path(c['index_dir']);self.children={x['chunk_id']:x for x in rows(self.index/'child_chunks.jsonl')}
        self.ids=read(self.index/'dense_ids.json');self.vectors=np.load(self.index/'dense_vectors.npy',allow_pickle=False)

    def __call__(self,q):
        vector=np.zeros(1024,dtype=np.float32);vector[0]=1
        suffix=q['query'].split()[-1].rstrip('?')
        if self.ids and suffix.isdigit():
            target=(int(suffix)*7)%len(self.ids)
            vector[0]=np.sqrt(.91);vector[target+1]=.3
            if int(suffix)%3==0:vector[target+1]=-.3
        class StubModels:
            config={}
            def encode(_,query):
                tokens=list(query.encode())
                self.old.assert_actual_inputs([tokens],[tokens])
                return vector,dict(query=query,query_sha256=self.old.text_sha(query),token_ids=tokens,token_count=len(tokens),truncated=False,
                                   actual_forward_inputs_verified=True,encode_gross_seconds=0.,input_capture_seconds=0.),0.
            def rerank(_,query,original):
                audits=[]
                for child in original:
                    tokens=list((query+' '+child['text']).encode())
                    self.old.assert_actual_inputs([tokens],[tokens])
                    audits.append(dict(chunk_id=child['chunk_id'],r3_rank=child['rank'],query_text=query,query_sha256=self.old.text_sha(query),
                        child_text=child['text'],child_text_sha256=child['text_sha256'],model_input_ids=tokens,model_input_length=len(tokens),
                        model_input_ids_sha256=self.old.json_hash(tokens),actual_forward_inputs_verified=True,
                        query_truncated=False,child_truncated_initial=False,child_truncated_pair=False))
                target=1+6*(int(suffix)%4) if suffix.isdigit() else 1
                scores=[float(abs(int(c['chunk_id'][-3:])-target)<=1) for c in original]
                ranked=self.old.rerank.rerank_results(original,scores)
                return ranked,audits,dict(r4_reranker_seconds=0.,r4_reranker_gross_seconds=0.,r4_input_capture_seconds=0.,r4_sort_seconds=0.,r4_validation_seconds=0.,r4_input_audit_seconds=0.)
        result,union,v,dense,pairs,times=self.old.retrieve(StubModels(),self.index,self.vectors,self.ids,self.children,q['query'])
        return dict(backend='synthetic-stub',results=result,union=union,vector=v.tolist(),dense_audit=dense,pair_audits=pairs,times=times)

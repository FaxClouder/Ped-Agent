"""Actual reread correction: heading/background alone does not support dataset type."""
from assemble_c100_r01 import ROOT,read,sha,write
if __name__=='__main__':
 p=ROOT/'reviews/primary/answerability-D300-r02/answerability-0268.json';d=read(p)
 r=d['requirements'][1];r['label']='unsupported';r['evidence']=[];r['missing']='Dufour仅标题和Background开头关于拥挤场景研究动机，未出现Lyon 2022采集、field evidence或multiscale数据结论。';r['reason']='实际重新阅读本packet Dufour全部可见source块；标题不能替代数据采集方法/结论。'
 d['provenance']['supplement_origin_path']=str(p);d['provenance']['supplement_origin_sha256']=sha(p);d['provenance']['actual_reread']='All visible Dufour source block (16268..17197), query and both requirements.'
 write(ROOT/'reviews/primary/answerability-D300-supplement-r01/answerability-0268.json',d)

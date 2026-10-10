"""Package observed E1 closeout artifacts; require passed parity and test logs."""
import argparse
import csv
import re
import shutil
from pathlib import Path
from runtime import ROOT,EXP,sha,save_json
from e1_closeout import load

def package(output):
    receipt=load(output/'closeout-receipt-r01.json');parity=load(output/'scoring-parity-r01.json');stats=load(output/'statistics-e1-r07-closeout-r01.json')
    assert receipt['status']=='completed' and parity['status']=='passed'
    assert parity['detail_cells']==22880 and parity['context_stage_cells']==6240
    assert receipt['E3_units']==receipt['index_builds']==receipt['retrieval_runs']==0
    logs=['pearl-chunking-closeout-20261006-06-command.log','pearl-chunking-closeout-20261006-tests-r03.log','pearl-chunking-closeout-20261006-tests-r04.log']
    for name in logs:
        dest=output/name
        if dest.exists():raise FileExistsError(dest)
        shutil.copyfile(ROOT/'outputs'/name,dest)
    assert '141 passed' in (output/logs[1]).read_text('utf8')
    assert '6 passed' in (output/logs[2]).read_text('utf8')
    code=['score.py','evaluate.py','e1_closeout.py','package_e1_closeout.py','verify_e1_closeout.py','test_score_review_bridge.py','test_e1_closeout.py','e1_visible_review.py','e1_visible_review_verify.py']
    snap=output/'code-snapshot-r01';snap.mkdir()
    for name in code:shutil.copyfile(EXP/name,snap/name)
    p=output/'statistics-table-r07-r01.csv'
    with p.open('x',encoding='utf8',newline='') as f:
        names=['configuration_id','baseline','panel','family','certificate_lower_difference','certificate_lower_difference_ci','possible_delta_interval','possible_delta_bootstrap_envelope','confirmed_gains','confirmed_losses','binary','mcnemar_exact_p','holm_p']
        w=csv.DictWriter(f,fieldnames=names,extrasaction='ignore');w.writeheader();w.writerows(stats['paired'])
    save_json(output/'commands-and-checks-r01.json',dict(
        runtime='Repository Windows .venv; CPython 3.12.7 (Anaconda build)',
        closeout=dict(command='.\\.venv\\Scripts\\python experiments/pearl-chunking-dev80-20261005/e1_closeout.py --source-run outputs/pearl-chunking-dev80-20261005-05 --reviewed-run outputs/pearl-chunking-dev80-20261005-07 --output outputs/pearl-chunking-dev80-20261006-06',exit_code=0,log=logs[0]),
        tests=[dict(command='.\\.venv\\Scripts\\python -m pytest experiments/pearl-chunking-dev80-20261005 -q --import-mode=importlib',exit_code=0,passed=141,log=logs[1]),dict(command='.\\.venv\\Scripts\\python -m pytest experiments/pearl-chunking-dev80-20261005/test_e1_closeout.py experiments/pearl-chunking-dev80-20261005/test_score_review_bridge.py -q --import-mode=importlib',exit_code=0,passed=6,log=logs[2])],
        unique_tests=143,shared_tests=4,stable_contract_changed=False,full_repository_suite_run=False,
        failed_attempts=[dict(run='pearl-chunking-dev80-20261006-01',status='failed_no_results',reason='Legacy -06 manifest has nested inputs rather than artifacts_sha256; no original shell log retained.'),dict(run='pearl-chunking-dev80-20261006-02',status='failed_no_results',reason='Same legacy schema error; confirmed exit 1.'),dict(run='pearl-chunking-dev80-20261006-03',status='failed_no_results',reason='-05 inputs also contain code metadata, not path/sha256 records.',log='outputs/pearl-chunking-closeout-20261006-03-command.log'),dict(run='pearl-chunking-dev80-20261006-04',status='failed_parity_coverage',reason='Adapter indentation omitted K1/5/10; corrected after failing coverage test.',log='outputs/pearl-chunking-closeout-20261006-04-command.log'),dict(run='pearl-chunking-dev80-20261006-05',status='interrupted',reason='Stopped own offline process to cache repeated content hashing; no result counted.',log='outputs/pearl-chunking-closeout-20261006-05-command.log')],
        test_attempts=[dict(log='outputs/pearl-chunking-closeout-20261006-tests-r01.log',status='failed',reason='Pre-correction evaluate indentation loaded at process start; 140 passed, 1 coverage failure.'),dict(log='outputs/pearl-chunking-closeout-20261006-tests-r02.log',status='passed',passed=46)],
        real_model_inference=0,generation_calls=0,remote_judge_calls=0))
    handoff='''# E1 收尾完成：下一会话唯一入口

*r07 开发结果与 E3 评分衔接交付 · status: current · 2026-10-06*

本阶段 `E1_closeout_complete_E3_not_started`。候选仍为 `C2-L384-O0-M0`、`C3-L256-O0-M0`；基线 `B0-regex320-overlap48-M0`。
开发入选不等于显著优胜；两个候选对 B0 的两个选择面板均未通过 24 项联合 Holm 家族的 0.05 门槛。
4K 净增分别 7/80、6/80；C3 CEGR@10 低于 B0。8K 仍保留 136 个 unknown。

## 已完成与核验

- [中文收尾报告](../../experiments/pearl-chunking-dev80-20261005/session3-closeout-2026-10-06.md)：完整方法、统计、046/057/068 及 018/077 案例与限制。
- [输入保全](preservation-inputs-r01.json)：r07 全部 489 产物、-05 全部 430 产物及 -06 输入重新 hash；旧输出漂移为零，score/evaluate 代码变化单列。
- [r07 配对统计](statistics-e1-r07-closeout-r01.json) / [CSV](statistics-table-r07-r01.csv)：13 配置、80 intent、三个面板；配对分层 bootstrap、二值 McNemar/Holm，unknown 不做二值检验。
- [差异案例](paired-difference-cases-r07-r01.jsonl)、[预算转移](budget-transitions-r07-r01.jsonl)、[裁定转移](r06-r07-status-changes-r01.jsonl)：现有实际可见内容、源区间、reviewer/caveat 与绑定；没有新增语义审查。
- [评分一致性](scoring-parity-r01.json)：旧 score/evaluate 复用新版支持判断；22,880 明细与 r07 零差异，已有 P0 三阶段 6,240 单元另经独立区间实现复核。未验证真实 P1/P2。
- [实际命令与检查](commands-and-checks-r01.json)：全实验目录 141 测试通过，另 6 项固定统计/适配测试通过（其中 4 项重合，共 143 项）。失败或中止尝试保留，不计为成功。

索引重建 0、重新检索 0、组装 0、E3 单元 0、生成/远程模型/裁判调用 0。未运行 E2/E4/E5，也未读旧 200 题进行分析。
输入来自 -05 的已有 rankings/contexts、-07 的 r07 map/评分/审查及原计划和协议。
本次不改变 -07 的 r07 map，不改变候选规则；新统计和评分入口以本次 manifest 为准，原 r05/r07 结果保持冻结。
代码快照和全部新增文件 SHA 见 [delivery-manifest.json](delivery-manifest.json)；最后重开核验见 [delivery-verification-r01.json](delivery-verification-r01.json)。

## 可复制的下一会话任务

> 在 `E:\\F_Workspace\\F-Agent-Paper` 只执行原切片 session 计划的 Session 4 / E3。先读本 handoff 与中文收尾报告，重开核验本目录 delivery-manifest.json、delivery-verification-r01.json，以及 -07 的 delivery-manifest.json、verification-e1-r07.json 和 candidate-selection-e1-r07.json；确认 frozen 与两个候选 C2-L384-O0-M0、C3-L256-O0-M0，B0 保留。核验本次 score/evaluate 和复用 e1_visible_review 的代码 SHA。仅使用这三个配置在 -05 的已有索引与同一 R4 rankings.jsonl（SHA 以 r05 verification-e1-r01 和本次 parity 回执为准），不新增检索。先核验 resolved_manifest 中同一 BGE tokenizer 的本地资产 SHA 和序列化预算，再比较 P0/P1/P2 × 4K/8K；分别保存 Top100 固定预算主面板和 Top10 raw/expanded/final 诊断面板，禁止跨面板差量。支持判断用 -07 common-support-map-e1-r07.json 与本次已适配评分入口，超出已审全集或未裁定部分保持 unknown；影响主结论时按协议审查并新增 map/run 版本，统一重算受影响配置。完成同排名/预算/来源去重核验、恢复增益与损失、成本和案例，冻结 E2 恢复策略后交接并停止。不执行 E2/E4/E5、不生成答案、不改检索器、不分析旧 200 题。

## 剩余事项

1. E3 的 P1/P2 与双面板预算组装、验证、评分和成本尚未执行；现有 P0 parity 不替代它们。
2. 8K 及新恢复内容的 unknown 可能影响结论；按协议补审，不能将区间上界当成绩。
3. E2 恢复策略未冻结；E2/E4/E5 仍待各自后续 session。
4. 候选语义审查单轮、046 temporal 隐含、同 dev80 选择偏差和来源依赖仍保留；独立确认尚缺。

完成本阶段后停止。未 commit/push/merge。
'''
    with (output/'handoff.md').open('x',encoding='utf8',newline='\n') as f:f.write(handoff)
    docs=[EXP/'README.md',EXP/'session3-closeout-2026-10-06.md',output/'handoff.md']
    links=[]
    for doc in docs:
        for target in re.findall(r'\]\(([^)]+)\)',doc.read_text('utf8')):
            if '://' in target or target.startswith('#'):continue
            path=(doc.parent/target.split('#')[0]).resolve()
            if path in ((output/'delivery-manifest.json').resolve(),(output/'delivery-verification-r01.json').resolve()):continue
            if not path.exists():raise ValueError('Unresolved link '+str(doc)+' '+target)
            links.append(dict(document=str(doc.relative_to(ROOT)),target=target))
    # Newly changed navigation lines, not unrelated historical documentation.
    for nav in (ROOT/'docs/README.md',ROOT/'experiments/README.md'):
        for line in nav.read_text('utf8').splitlines():
            if '20261006-06' not in line and 'session3-closeout' not in line:continue
            for target in re.findall(r'\]\(([^)]+)\)',line):
                if not (nav.parent/target).resolve().exists():raise ValueError('Unresolved current navigation '+target)
                links.append(dict(document=str(nav.relative_to(ROOT)),target=target))
    save_json(output/'document-links-r01.json',dict(status='passed',links=links,pending_generated_link='delivery-verification-r01.json; checked during final reopen'))
    tracked=[EXP/name for name in code]+[EXP/'README.md',EXP/'session3-closeout-2026-10-06.md',ROOT/'docs/README.md',ROOT/'experiments/README.md']
    artifacts={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted(output.rglob('*')) if p.is_file()}
    artifacts.update({str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in tracked})
    inputs={str((ROOT/'outputs'/run/'delivery-manifest.json').relative_to(ROOT)).replace('\\','/'):sha(ROOT/'outputs'/run/'delivery-manifest.json') for run in ('pearl-chunking-dev80-20261005-05','pearl-chunking-dev80-20261005-06','pearl-chunking-dev80-20261005-07')}
    inputs.update({str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in (ROOT/'docs/superpowers/plans/2026-10-05-pearl-chunking-sessions.md',EXP/'protocol.md')})
    save_json(output/'delivery-manifest.json',dict(schema_version='e1-closeout-e3-bridge-r01',status='E1_closeout_complete_E3_not_started',inputs=inputs,artifact_count=len(artifacts),artifacts_sha256=artifacts,decisions=dict(selected=receipt['selected'],baseline=receipt['baseline'],development_selection_not_significant_superiority=True),counts=receipt,verification=dict(parity='scoring-parity-r01.json',inputs='preservation-inputs-r01.json',tests='commands-and-checks-r01.json'),next='Only this handoff.md is the Session 4 entry; E3 not started.'))
    print('packaged',len(artifacts),'artifacts',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();package(a.output.resolve())

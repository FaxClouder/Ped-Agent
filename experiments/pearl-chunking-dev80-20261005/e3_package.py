"""Package verified E3 facts; never runs retrieval, scoring or E2."""
import argparse
from pathlib import Path
from e3 import CONFIGS,load,rows,REVIEW,SOURCE,CLOSE
from runtime import ROOT,EXP,sha,save_json

def table(headers,records):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in records])

def write(path,text):
    with path.open('x',encoding='utf8',newline='\n') as f:f.write(text.rstrip()+'\n')

def run(out,revision):
    selection=load(out/f'recovery-selection-e3-{revision}.json');assert selection['status']=='frozen'
    for name in ('assembly-verification-r01.json','rank-order-verification-r01.json',f'score-verification-e3-{revision}.json',f'final-analysis-verification-{revision}.json',f'mechanism-audit-verification-{revision}.json'):
        assert load(out/name)['status']=='passed'
    scores=load(out/f'scores-e3-{revision}.json');stats=load(out/f'statistics-e3-{revision}.json')
    lineage=load(out/f'map-lineage-e3-{revision}.json');cold=load(out/'cost-reference-e3-r02.json')
    report=['# PEARL Session 4：E3 恢复与预算实测',f'*固定 R4 排名的开发比较与 E2 恢复策略冻结 · status: current · 2026-10-06 · 评分 {revision}*','',f'完成 E3；冻结共同恢复策略 **{selection["selected"]}**，依据 E1 主候选 `{CONFIGS[1]}` 的 Top100 / 4096 实测完整性及可比成本。B0 与 C3 的决定单列为稳健性检查；其 unknown 仍可改变各自局部优选，因此不能宣称共同策略对三个配置普遍最优。未启动 E2、E4、E5，没有新检索、建库或答案生成。','',
    '## 输入与评分边界','',
    '已读取原 Session 计划、研究设计、公共协议以及会话 A 的交接和验证。会话 A 的 22,880 个旧评分细节、6,240 个 P0 阶段评分兼容核验零差异；本次在组装前重开输入 manifest 并核验输出字节。沿用 `-05` 的相同 R4 排名、source views、公共 parent 图和 BGE-M3 tokenizer。480 个冻结 P0 主面板上下文复用，其余 2,400 个上下文组装或合法 Top10 投影，共 2,880 条上下文；独立问题数始终为 80。','',
    f'r07 原评分保留；新增实际文本审查形成共同 `{revision}` map，三个配置、两个预算和两个面板统一重评。完整性采用冻结 AND/OR requirement；原 requirements、groups、证据 certificates 的历史定义未改写；r10 通过显式 scope_revision 排除经独立裁定不充分的正证据，评分时投影生效。dev051 的完整 verbal-exchange 原证书保留，一般 communication 替代条目排除；dev056 单独趋势段缺 logistic 关系，排除其单独充分性，仅采用实际 stage 可见的完整组合。两条 exact final 全文穷尽补审后记 no，其余未审与歧义仍 unknown。共新增 {len(lineage["accepted"])} 个 requirement 审查记录。仅覆盖完整且穷尽的审查扩展 reviewed universe；其中显式歧义范围继续 unknown，不形成已知否定。其余未审文本继续 unknown。source-map 版本变动单列在 `scoring-revision-changes-{revision}.jsonl`，不计为恢复收益。','',
    'Agent 审查与独立裁定属于正式开发评价，`human_verified=false`。关键限定包括：dev026 四个跨文献组合未建立场景关联；dev051 的 social communication 不自动等于 verbal exchange；dev035 的数值与 PDF 最大值关系等歧义保留 unknown；dev056 只有实际可见完整 logistic 关系组合可判 yes。参考证据仅解释要求，不加入上下文。','',
    '## Top100 预算主面板','',
    '每格 n=80；yes/no/unknown 为最终实际序列化上下文评分。确定下界=yes/80，可能上界=(yes+unknown)/80；可能界不是置信区间。','']
    for panel,title in [('fixed_budget_main',''),('seed10_diagnostic','## Top10 种子诊断')]:
        if title:report += [title,'','以同一 R4 的前十个命中为种子单独组装和评分，绝不与 Top100 互减。','']
        report += [table(['配置','策略','预算','yes','no','unknown','完整率界'],[(r['configuration_id'],r['strategy'],r['budget'],r['yes'],r['no'],r['unknown'],f"{r['complete_group_lower']:.3f}–{r['complete_group_upper']:.3f}") for r in scores['summary'] if r['panel_id']==panel]),'']
    report += ['## 恢复收益、预算损失与配对比较','','下表为各面板同配置、同预算的 P0→P1/P2 最终上下文比较。确定收益仅 no→yes，确定损失仅 yes→no；unknown 不能作为 no。确定 yes 差值另含 unknown→yes 等变化。', '',table(['配置','面板','预算','策略','确定收益','确定损失','yes差值','可能差值界'],[(r['configuration_id'],r['panel_id'],r['budget'],r['strategy'],r['confirmed_gain'],r['confirmed_loss'],f"{r['confirmed_yes_delta']:.3f}",str(r['possible_delta_interval'])) for r in stats['paired']]),'',
    '同面板 raw→expanded、expanded→deduplicated、expanded→final 逐题转移全部保存于 transitions 与 statistics；actual raw、expanded、final 文本、来源区间、截断 trace 和 map 身份保存在 cases。所有 Top100/4K 结论相关案例另在 mechanism-audit 逐项绑定实际完整支持 witness、条件、缺失的来源区间与 P0 对照，使用原 certificate 或明确审查 provenance。完整支持被截断降为 unknown 与被截断降为 no 分开报告。', '',
    table(['配置','面板','预算','策略','扩展挽回 no→yes','截断 yes→no','截断 yes→unknown'],[(c,p,B,P,next(r['transitions'].get('confirmed_gain',0) for r in stats['stage_transitions'] if (r['configuration_id'],r['panel_id'],r['budget'],r['strategy'],r['comparison'])==(c,p,B,P,'raw->expanded')),next(r['transitions'].get('confirmed_loss',0) for r in stats['stage_transitions'] if (r['configuration_id'],r['panel_id'],r['budget'],r['strategy'],r['comparison'])==(c,p,B,P,'expanded->final')),next(r['transitions'].get('possible_loss',0) for r in stats['stage_transitions'] if (r['configuration_id'],r['panel_id'],r['budget'],r['strategy'],r['comparison'])==(c,p,B,P,'expanded->final'))) for c in CONFIGS for p in ('fixed_budget_main','seed10_diagnostic') for B in (4096,8192) for P in ('P0','P1','P2')]),'',
    '配对 bootstrap 以 intent 为单位，按 main_stratum 分层，10,000 次、seed=20261005；确定 yes 差值的描述性 95% 区间与 unknown 可能界分别保存。仅无 unknown 的对比执行精确 McNemar，并对全部合格 E3 恢复对比联合 Holm 校正。开发选择偏差仍存在，不宣称总体显著优胜。','',
    '## 成本与画像','','缓存组装记录是按 P0/P1/P2、4K/8K、主面板/诊断顺序的增量成本；后续主面板可复用已被诊断预热的缓存。P0 主面板复用时间为零，不能解释为算法延迟。独立成本参考在固定的每层两题、共八题上调用原组装器、原 tokenizer 和穷举 prefix 搜索，无 E3 memo 或冻结上下文复用，意图内随机策略顺序。该样本仅是组装成本，未加旧检索时长；配置线程并发的 wall time不相加成端到端延迟。','',table(['配置','策略','样本 n','原始组装 mean 秒','median 秒'],[(r['configuration_id'],r['strategy'],r['n'],f"{r['mean_seconds']:.3f}",f"{r['median_seconds']:.3f}") for r in cold['summary']]),'',
    '来源数、实际最终 tokens、source-interval 重复率、扩展序列化倍率按 36 格保存在 context-profiles 与 comparison CSV。全部序列化重新用冻结 tokenizer 计数且未超预算；全部来源文本、四阶段 offsets、来源去重与首 rank 顺序独立核验。36 格各固定抽一条，发生截断时用冻结的等价批量计数穷举所有合法 Unicode 前缀并复核最大值，拟合边界再用原单次计数核验；未截断完整序列也独立核验预算。实验性的 token memo 通过等价检查但实测更慢，没有用于最终组装。','',
    '## 审查与核验覆盖','','语义抽查固定 seed=20261005，每层两题，共八个意图，选择与分数无关，实际可见 Top100/4K 并集全文审查。结论相关 unknown 意图另行全文补审；原判决与独立裁定均保留。8K 和 Top10 的超出审查范围实际文本仍按三值评分保留 unknown；没有推定为已审。','',
    f'已保存并重开核验 11,520 个四阶段细节、10,560 个转移、36 格聚合，以及所有 unknown 明细。最终统计独立复算 gain/loss、可能界、二项式精确检验、Holm 与选择上下界；packet 字节和 context/text SHA 绑定另行核验。测试记录见最终 delivery manifest；这是实验模块核验，不是 OCR、GPU、在线模型或全系统集成验证。','',
    '## E2 冻结与停止','','冻结规则 r02 在 E3 正式评分前保存：主候选 C2 的 4K 确定完整性降序，同分按固定样本原始组装 mean 秒、策略 ID；仅当竞争者 unknown 上界能改变选择时继续补审。领先策略本身有 unknown 但无法改变选择时允许冻结。r01 额外的“自身 unknown 阻止”保留为初步规则，scores 内缓存成本决定为非权威诊断；以 recovery-selection 为准。','',
    table(['配置','状态','选择','威胁'],[(c,d['status'],d['selected'],str(d['threats'])) for c,d in selection['all_configuration_decisions'].items()]),'',
    f'E2 共同策略为 `{selection["selected"]}`，预算入口固定4096；C2/C3 的 O/M 消融网格仍未执行。'+(' 因选择 P0，E2 中 P0 与恢复臂应登记别名，禁止重复执行相同配置。' if selection['selected']=='P0' else ''),'',
    '输出尝试 -07 原始低效组装停止；-08 只采纳关闭并 hash 完整的 B0 12格，其后重复 C2 片段不计完成。C2/C3 来自独立 -09/-10 关闭 worker，统一最终输出为 -11。组装与核验尝试日志、部分输出及历史输入保留，没有覆盖冻结研究结果。三份本次新生成的无效审查 JSON 曾就地修正，原无效字节无法恢复，单独失败记录如实保存；正确审查结果已重开核验。项目 embedding、rerank、检索、generation、remote-judge API 调用为零；语义审查是本会话 Agent 工作，单独记录。没有访问封存 Eval200 内容。','',
    f'[最终交接](../../{out.relative_to(ROOT).as_posix()}/handoff.md) · [输出清单](../../{out.relative_to(ROOT).as_posix()}/delivery-manifest.json) · [评分选择](../../{out.relative_to(ROOT).as_posix()}/recovery-selection-e3-{revision}.json)']
    write(EXP/'session4-e3-2026-10-06.md','\n'.join(report))
    write(out/'handoff.md',f'''# PEARL E3 完成交接

*固定排名恢复策略冻结；下一阶段 E2 尚未启动 · status: current · 2026-10-06*

E3 已完成并独立核验。共同恢复策略 **{selection['selected']}** 已冻结，以 C2-L384-O0-M0 / Top100 / 4096 为选择依据；统一评分图为 `{revision}`。冻结身份与 SHA 见 [选择](recovery-selection-e3-{revision}.json)、[评分](scores-e3-{revision}.json)、[map lineage](map-lineage-e3-{revision}.json)。开发选择不代表总体显著优胜。

读取 [完整报告](../../experiments/pearl-chunking-dev80-20261005/session4-e3-2026-10-06.md)、[delivery manifest](delivery-manifest.json) 与 [交付核验](delivery-verification-r01.json)，再按 [原 Session 计划](../../docs/superpowers/plans/2026-10-05-pearl-chunking-sessions.md)进入 E2。当前请求只授权 E3；此处为交接，不是 E2 执行授权。

E2 沿用冻结 C2-L384、C3-L256、B0 及公共源/父图/tokenizer，恢复参数用 `{selection['selected']}`，主预算4096。{'P0 与恢复臂必须别名复用，避免重复配置。' if selection['selected']=='P0' else '保持 P0 对照与冻结恢复臂的完整配置身份。'} 不从 E3 8K/Top10 诊断另挑策略。E2 O/M 网格未运行；E4、E5、答案生成、封存 Eval200 均未启动。

scores 内 decisions 是 r01 额外 unknown 门槛与缓存耗时的非权威初步诊断；冻结只以 recovery-selection 为准。B0/C3 局部策略优选仍受 unknown 影响，不能将共同 E2 策略解释为对三个配置普遍最优。

对比恢复效果必须使用共同 {revision} P0 基线；`scoring-revision-changes-{revision}.jsonl` 是审查版本变化，不能归为恢复收益。unknown 仍是 unknown；继续使用已审范围之外的新实际文本时，按原三值规则或版本化补审。r07 原 map、E1排名与结果未改写。

可从36个 contexts 文件、r07/{revision} scores、transitions、statistics、cases、context profiles、两种成本记录和全部 review packet/results/adjudications 重开核验。主面板与 Top10 种子诊断严格分开。-07/-08 的中止尝试保留；最终只采纳三配置完整关闭单元，计2,880 contexts、80独立intent。
''')
    save_json(out/'stage-boundary-e3-r01.json',dict(stage='E3',status='complete',E2_started=False,E4_started=False,E5_started=False,retrieval_calls=0,index_builds=0,embedding_calls=0,rerank_calls=0,generation_calls=0,remote_judge_api_calls=0,semantic_agent_review_files=len(list((out/'review-results-e3-r08').glob('*.json'))),independent_adjudication_files=len(list((out/'review-adjudications-e3-r08').glob('*.json')))+len(list(out.glob('review*scopes*r10*.json')))+len(list(out.glob('review-adjudications-e3-r10*.json'))),selected_recovery=selection['selected'],mapping_sha256=sha(out/f'common-support-map-e3-{revision}.json'),frozen_ranking_sha256=load(out/'runtime-r01.json')['ranking_inputs']))
    print('Packaged E3 report and handoff',selection['selected'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--revision',required=True);a=p.parse_args();run(a.output.resolve(),a.revision)

"""Chinese tables from saved Layer 4 scores; never supplies semantic judgments."""
import json
from pathlib import Path

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def percent(x):return 'NA' if x is None else f'{100*x:.2f}%'
def bound(xs):return percent(xs[0]) if xs[0]==xs[1] else f'{percent(xs[0])}–{percent(xs[1])}'

def analyze(root:Path,out:Path,completed=False,revision='r01'):
    root=Path(root);scores=read(root/f'scores-{revision}.json');verified=read(root/f'independent-verification-{revision}.json')
    reviewed=read(root/f'reviewed-{revision}.json')['rows']
    if completed and (not verified['verified'] or verified['cell_n']!=400 or verified['reuse_n']!=100):raise ValueError('completion requires verified 400 cells and 100 exact reused rows')
    arms=['A0-4096','A0-8192','A1-4096','A1-8192','Aref-8192']
    lines=['# PEARL Layer 4 Grounding 与 Reliability 中文分析','', '*固定400回答与实际context的正式Agent开发评价 · status: current · 2026-10-04*','',
        '本轮只评价既有80题×五臂400回答；原C100整行精确复用于最终400，D新增审查300，不新增生成请求。human_verified=false。Grounding与Reliability分别汇总，不构造合成总分。', '',
        '## 有据性、事实准确性与引用','',
        '|臂|题数／claims|Faithfulness宏平均|广义未完整支持宏平均|Context冲突宏平均|Factuality宏平均|事实解析覆盖微平均|Citation P宏平均|Citation R宏平均|',
        '|---|---|---|---|---|---|---|---|---|']
    for a in arms:
        s=scores['arms'][a]
        lines.append('|'+ '|'.join([a,f"{s['cell_N']} / {s['claim_N']}",bound(s['faithfulness_macro']),bound(s['unsupported_rate_macro']),bound(s['context_contradiction_rate_macro']),bound(s['factuality_macro']),percent(s['factuality_coverage_micro']),bound(s['citation_precision_macro']),bound(s['citation_recall_macro'])])+'|')
    lines+=['','主指标为逐题宏平均；不同长度回答并非等量claim样本。partial严格不给半分；unknown形成上下界。纯拒答N=0为NA，不记Faithfulness满分。事实范围以冻结本地源段为限；范围外额外断言unknown，未完成全域事实查证。','',
        '|臂|S/P/U/C/X|事实T/F/X|Faithfulness微平均|Factuality微平均|Citation P微平均|Citation R微平均|claims NA题／引用P NA题|实际pairs|','|---|---|---|---|---|---|---|---|---|']
    for a in arms:
        s=scores['arms'][a];g=s['grounding_counts'];f=s['factuality_counts']
        lines.append('|'+ '|'.join([a,'/'.join(str(g.get(k,0)) for k in ('supported','partial','unsupported','contradicted','unknown')),'/'.join(str(f.get(k,0)) for k in ('true','false','unknown')),bound(s['faithfulness_micro']),bound(s['factuality_micro']),bound(s['citation_precision_micro']),bound(s['citation_recall_micro']),f"{s['claim_na']} / {s['citation_precision_na']}",str(s['citation_pair_N'])])+'|')
    lines+=['','|臂|事实已解析准确率 T/(T+F)|已解析／全部claims|引用supported/partial/unsupported/contradicted/unknown/invalid/outside-context|','|---|---|---|---|']
    for a in arms:
        f=scores['arms'][a]['factuality_counts'];t=f.get('true',0);wrong=f.get('false',0);counts={}
        for row in scores['rows']:
            if row['arm']==a:
                for label,n in row['citation']['counts'].items():counts[label]=counts.get(label,0)+n
        lines.append('|'+ '|'.join([a,percent(t/(t+wrong) if t+wrong else None),f"{t+wrong}/{scores['arms'][a]['claim_N']}",'/'.join(str(counts.get(k,0)) for k in ['supported','partial','unsupported','contradicted','unknown','invalid','outside-context'])])+'|')
    lines+=['','已解析事实准确率只描述冻结源段可核验部分；不能将其高值外推到unknown断言或全域准确率。无引用回答的引用precision为NA，但非空事实claims的recall分母仍保留。','',
        '## 可回答性、受限回答与拒答','',
        '|臂|complete/partial/none/unknown|TP/FP/FN/TN|拒补全P/R/F1|False Answer|误拒率|确定混淆表覆盖|complete旧Strict正确／N|','|---|---|---|---|---|---|---|---|']
    for a in arms:
        s=scores['arms'][a];r=s['reliability'];c=s['complete_strict'];v=r['answerability_counts']
        lines.append('|'+ '|'.join([a,'/'.join(str(v.get(k,0)) for k in ('complete','partial','none','unknown')),'/'.join(str(r[k]) for k in ('TP','FP','FN','TN')),' / '.join(percent(r[k]) for k in ('precision','recall','f1')),percent(r['false_answer_rate']),percent(r['false_refusal_rate']),f"{r['resolved_cells']}/{r['total_cells']}",f"{c['correct']}/{c['N']} ({percent(c['rate'])})"])+'|')
    lines+=['','正类partial/none表示不能补全必要结论。bounded_partial仅在明确缺口、已说内容均受支持且没有补出缺失结论时计为拒绝补全，与pure_abstain分别列。零分母P/R/F1/False Answer均NA。理由准确性独立，不能由合理行为自动推出；full_answer附加局限不计拒答理由。','',
        '|臂|无支持补全标志数／回答数|Reliability未知数|P/R/F1可能界|False Answer可能界|误拒可能界|', '|---|---|---|---|---|---|']
    for a in arms:
        r=scores['arms'][a]['reliability'];sub=[x for x in reviewed if x['arm']==a]
        lines.append('|'+ '|'.join([a,f"{sum(bool(x['unsupported_completion']) for x in sub)}/{len(sub)}",str(r['unknown_cells']),' / '.join(bound(r[k+'_bounds'])+(' (可NA)' if r[k+'_may_be_na'] else '') for k in ('precision','recall','f1')),bound(r['false_answer_rate_bounds']),bound(r['false_refusal_rate_bounds'])])+'|')
    lines+=['','可能界只对未定answerability/拒补决策作最好最坏赋值；覆盖率不足时不能只比较确定子集的点估计。unsupported_completion是行为另列标志，不能替代每个claim有据性，也不自动等于全部FN。','',
        '|臂|full_answer/bounded_partial/pure_abstain/ambiguous|理由correct/incorrect/unknown|已解析理由准确性|','|---|---|---|---|']
    for a in arms:
        s=scores['arms'][a];b=s['behavior_counts'];r=s['reason_counts']
        lines.append('|'+ '|'.join([a,'/'.join(str(b.get(k,0)) for k in ('full_answer','bounded_partial','pure_abstain','ambiguous')),'/'.join(str(r.get(k,0)) for k in ('correct','incorrect','unknown')),percent(s['reason_accuracy'])])+'|')
    lines+=['','## 分层与联合诊断','', '|臂／题型|题数／适用题|Faithfulness宏平均|Factuality宏平均|引用Recall宏平均|False Answer|','|---|---|---|---|---|---|']
    for a in arms:
        for name,s in scores['arms'][a]['strata'].items():
            lines.append('|'+ '|'.join([a+' / '+name,f"{s['cell_N']} / {s['cell_N']-s['claim_na']}",bound(s['faithfulness_macro']),bound(s['factuality_macro']),bound(s['citation_recall_macro']),percent(s['reliability']['false_answer_rate'])])+'|')
    lines+=['','联合逐题表保留complete上的旧Strict达标／未达标、已说声明是否全部有据及误拒，partial/none上的受限回答、纯拒答与无支持补全。旧Strict未达标可能来自遗漏或条件错误，不能当作每个声明事实为false；逐claim正确但无支持、错误且有支持及未知另用独立factuality交叉表。旧L2标签不改写。对应计数见scores-r01.json的joint_counts与cross-layer-diagnostics-r01.json。正确但无支持不推定来自参数知识、外部补证或L2误判。','',
        '## 配对差与不确定性','',
        '五项预设比较使用同一intent面板、分single/numeric/within/cross四层重抽10000次，seed20261004，95%线性百分位；不进行事后显著性检验。Faithfulness在每对固定共同适用题集合上比较，NA数和共同集合N明确保存。unknown差值下界为lowerA−upperB，上界为upperA−lowerB，分别bootstrap。Citation/Rejection及事实覆盖明显变化时只作带分母的描述。','',
        '|配对|共同适用N|Faithfulness差下界〔95%区间〕|差上界〔95%区间〕|两侧NA|','|---|---|---|---|---|']
    bootstrap=read(root/f'paired-bootstrap-{revision}.json')
    for r in bootstrap['results']:
        if r['metric']!='faithfulness':continue
        interval=lambda v:percent(v['difference'])+' ['+', '.join(percent(x) for x in v['ci95'])+']'
        lines.append('|'+ '|'.join([r['pair'],str(r['common_N']),interval(r['lower']),interval(r['upper']),f"{r['left_NA']} / {r['right_NA']}"])+'|')
    lines+=['','## 评审、核验与限制','',
        f"独立保存核验：verified={verified['verified']}，{verified['cell_n']} cells、{verified['claim_n']} claims、{verified['citation_pair_n']}实际pairs、{verified['binding_n']}绑定、{verified['review_chain_n']}任务链、{verified['reuse_n']}精确复用行。验证器不import评分核心，重新计算逐题与宏微汇总并检查原记录自哈希、证据区间、引用身份、裁决及复用链。",'',
        '独立语义评审采用任务白名单与匿名包。早期活动线程上限阻止新增角色，已有任务完成后成功启动不继承上下文的context_secondary_tail负责C后50次审。角色复用及各包既往暴露均保留，不声称不同独立模型或全程双盲：context primary工程阶段接触009部分旧定义/score与012部分生成信息，并机械解析过D匿名映射；context secondary未看真实事实包、旧成绩和primary；facts primary未看实际context/旧score，首次源文准备见009旧必要结论；facts_secondary_c为不继承上下文的源侧独立次审；根事实复核与第三裁决知道C事实包及旧总体分数，负责评估侧身份关联；D context第三角色中，root先完成19份Grounding和首12份行为裁决，随后为事实格式/裁决读过D源侧结果，后续root行为裁决保留该暴露。其他独立D context第三角色未读实际源侧Gold。各逐包provenance记录实际阅读和既往暴露，不能把任务隔离说成全程独立盲测。C100全量二审，D新增300中预定60二审，剩余240不称二审。','',
        'C尾部次审自己的新建、未冻结QA中间文件发生过覆盖与按生成规则重构，无首版字节SHA，不能宣称恢复首版；最终r03与mutation audit独立冻结，旧Layer3科学资产未改动。第三裁决、字节核验及后续新版本修正均保留实际来源。该过程限制与主审工程暴露一并披露。','',
        '天然样本不扩造拒答、冲突或噪声题；未覆盖类型不宣称测量完成。034/035源文密度单位损坏保留unknown，044不相关数值矛盾保留，不修改原参考/答案。35题child4K/8K请求相同仍可能答案不同；单次生成无seed，oracle更短且完整源文选择不同，不能单独归因为预算或parent展开。多题共用source存在依赖，intent bootstrap不消除文献聚类风险。','',
        '本轮被测生成请求0；Agent审查usage/费用未由平台返回，不推测费用，也不称全框架效率评价完成。原Retrieval/Evidence/Answer科学资产最终SHA保护审计另存，维护docs导航允许差异保留。没有人工审查、commit/push/merge或清理。','',
        '交付止于Layer4；不继续Layer5/6，不新增200题评价。']
    with Path(out).open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
    return out

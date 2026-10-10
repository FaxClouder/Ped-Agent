# Session 1 资产与实现审计

*真实只读核验结果与待适配边界 · status: current · 2026-10-05*

## 保存身份

commit：`6d6eed42eec621ca2f63a0e825c05677a0219bbf`；分支`main`。现有dirty工作区保持，相关代码SHA逐项保存在[baseline](../../outputs/pearl-chunking-dev80-20261005-02/workspace-baseline.json)。本阶段仅新增审计/文档，更新维护导航；没有实现chunker、index或运行时adapter。

| 资产 | 实际数量/核验 | 机器证据 |
| --- | --- | --- |
| 原稿 | D:/GoogleDownload原稿存在，SHA与策略方案一致 | baseline.user_draft |
| 语料 | 106 PDF/106 canonical/106 Adobe ZIP；PDF及canonical声明SHA吻合 | [source registry](source_registry.json)含各路径及SHA |
| 派生/模型/索引输入 | 1683项记录，无缺失、无声明SHA不符 | [asset audit](../../outputs/pearl-chunking-dev80-20261005-02/asset-audit.json) |
| H0 child/parent | 6433/2830；offset、containment、parent重建均6433/6433；当前默认实现重建106源所有ID与正文相同 | [policy reconstruction](../../outputs/pearl-chunking-dev80-20261005-02/legacy-policy-reconstruction.json) |
| dev80/Gold r02 | 查询80与Gold query/intent逐项相同；4类各20；r02 SHA 7f64ac4559fbf604c0d4d6aca81e23685f1dcbf009853ee3c8637dc368ad29f5 | resolved_manifest inputs |
| 原support map | analysis-r02-01/support-map.json，绑定原chunk、Gold与真实path_evidence | asset audit与下面迁移分级 |
| 独立答案参考 | reference-freeze-r01.json含80 resolved参考，intent集合一致；不直接以旧答案作为新输出 | resolved_manifest inputs；旧参考/候选包纳入protected哈希 |
| 历史保护 | 10335文件字节SHA，包括H0和Layer1–4、旧eval200结果；Chroma物理文件排除且不打开数据库 | [protected hashes](../../outputs/pearl-chunking-dev80-20261005-02/protected-assets-sha256.json) |
| 旧200身份 | 仅读C/D发布报告与四层汇总，未反序列化题目/Gold/排名用于开发；保护中只读字节hash | [C/D入口](../pearl-retrieval-eval200-20261003/README.md)；原独立评价身份保留，今后仅已暴露回归 |

模型权重及配置已hash，不代表本阶段加载GPU或执行真实forward。真实检索和语义支持审查未运行。

## Gold跨切片追溯的三类

174 atoms的119个有唯一canonical元素文本定位候选；55个无精确元素锚点，涉及39 intents。0个atom的source缺失。这是位置审计，不是119个已完成语义迁移。页码优先选锚点、记录所有匹配，source版本严格固定。[逐原子明细](../../outputs/pearl-chunking-dev80-20261005-02/gold-location-audit.json)保留未决。

573个历史实际支持引文全部在原child中；312可唯一精确定位到canonical元素，261需跨元素/规范化/重复歧义追溯与语义审查。[r02引文明细](../../outputs/pearl-chunking-dev80-20261005-02/legacy-support-location-audit-r02.json)枚举全部出现位置；r01保留为早期定位快照，不作最终唯一性依据。

| 类别 | 当前判定 | Session 2处理 |
| --- | --- | --- |
| 可确定性迁移候选 | 版本/hash、历史parent offsets、精确引文位置可恢复；完整支持范围尚未冻结 | 构建reversible span map后，只有实际保留全部已核验支持范围才能继承；短anchor/quote单独不能证明条件完整 |
| 需语义审查 | 55非精确anchors、261非唯一元素excerpt定位；新切片/联合文本及截尾 | 对真实来源与需求读全文，保留三值；逐题登记受影响requirements/组，不关键词赋true |
| 无法恢复 | 当前source缺失0；不能据此称完整锚点恢复成功 | 若源损坏/支持范围无法回映，登记source_unrecoverable并阻止受影响正式比较，不能偷偷排除题目 |

Layer2 raw与Retrieval r02已有不同审查视图；本轮必须构建共同map，不能混用较高历史标签。39意图是位置审计优先清单，不等于确定失败或可以删除的分母。

## H0/B0逐项差异

| 项 | H0实际实现 | B0公共协议与适配 |
| --- | --- | --- |
| 正文长度 | RegexTokenCounter，窗口min(320,450)=320、overlap48；parent target1200/max1800；不是BGE长度；超长元素可超过parent max | 保留真实正则方法/overlap，但转到公共source view；与C1 BGE O0不等价，B0不是纯边界对照 |
| 表格 | ordinary element参与父分组及文本窗口，无屏障/公共cell snapshot | 公共独立table snapshot，对全部配置相同；表格分组参数待冻结 |
| 标题/前缀 | _render_elements注入heading_path，正文元素还可能包含heading；sparse额外title/heading字段为空 | 正文标题一次、M0无额外prefix；M1仅原文结构，检索表示与支持正文分开 |
| 父图 | child依赖历史parent分组、每child一个parent | 构建独立公共parent≤1536 BGE，P2多父；B0不私用H0父恢复 |
| 候选 | R1/R2 depth100、RRF60、R4 rerank100，固定旧索引路径/6433/80校验 | 相同参数，动态新chunk数、新索引、新排名，不改模型帮助chunker |
| 去重 | Evidence unit_id去重，child重叠仍可重复 | 版本化来源span/cell并集，跨文献同句不去重 |
| 预算 | serialize包含Source/locator/Title，BGE count；首次溢出字符二分截尾并停止 | 复用完整计量，新增可逆截断和最大合法prefix验证；并非新增预算计数 |
| 面板 | 固定Top10 raw/expanded/final | 新Top100 fixed-budget主面板，保留Top10诊断，panel独立 |
| 支持/评分 | r02 atom_paths绑定旧chunk；Evidence三值实际正文审查 | 共同source support图、同AND/OR逻辑、实际final审查；旧映射不直接跨切片复用 |

## 参数与授权缺口

真实检索配置、权重SHA、revision、seed、tokenizer已解析，具体在[resolved manifest](resolved_manifest.yaml)。公共来源视图、表格行组/超长cell、公共父图、共同支持图、C4分句器/实测阈值、M1配额与实际CLI为null。不是自动猜测值，也不能用脚手架替代。

旧Layer3记录的deepseek-flash、nonthinking、temperature0、输出2048、timeout120仅历史配置线索。本轮当前provider/judge能力和调用授权未知；本轮实际生成/裁判/API模型调用0。最多720答案是后续计划，不是授权额度。无需因此暂停独立本地Session2工作。

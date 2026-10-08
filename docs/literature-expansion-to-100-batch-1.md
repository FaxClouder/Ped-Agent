# 扩充至 100 篇：批次 1 文献检索与下载清单

_50→75 篇阶段的 25 篇候选文献 · status: plan · verified: 2026-09-21_

---

## 批次结论

本批以当前 Catalog 中的 50 篇文献为去重基线，从既有候选池中重新筛选并通过 DOI、
出版社页面或作者机构页面核验 25 篇正式期刊论文。批次配额为 T1=5、T2=5、T3=5、
T4=6、T5=4；全部下载并通过正式筛选后，文献规模将由 50 篇增至 75 篇。

本清单只证明题名、作者、年份、期刊、DOI 和主题价值已经完成初筛。中科院分区、
Clarivate JCI、WoS/Scopus 引用量、撤稿/关注声明以及全文质量评分仍需在下载后按
[`../memPed/knowledge/collection_standard.md`](../memPed/knowledge/collection_standard.md)
核验，不应仅凭期刊声誉直接标记为 A/B 级。

| 主题 | 当前估算 | 本批 | 批次完成后 | 100 篇目标 |
| --- | ---: | ---: | ---: | ---: |
| T1 行人流基础理论 | 10 | 5 | 15 | 20 |
| T2 实验与测量 | 11 | 5 | 16 | 20 |
| T3 设施与场景流动 | 9 | 5 | 14 | 20 |
| T4 疏散行为与模型 | 13 | 6 | 19 | 25 |
| T5 安全风险与干预 | 7 | 4 | 11 | 15 |
| **总计** | **50** | **25** | **75** | **100** |

> 当前主题数依据已有 34 篇和本地 Batch 3 唯一内容推算；Batch 3 中有 2 个 SHA-256
> 重复项未重复计数。正式统计应在 Catalog 元数据修复并补齐 `primary_topic` 后重算。

## 下载优先级

- **P1**：方法或证据价值高，且来源质量较强；先下载。
- **P2**：覆盖重要缺口；在 P1 后下载。
- **P3**：内容有价值，但期刊指标或正式门槛风险较高；先查 JCI/分区再下载。
- **OA**：已找到公开全文入口；`机构` 表示通常需学校图书馆或作者稿。

## T1：行人流基础理论（5 篇）

| 编号 | 文献信息与 DOI | 核心贡献 | 优先级 / 获取 | 建议文件名 |
| --- | --- | --- | --- | --- |
| B1-T1-01 | Moussaïd et al. (2010), *The Walking Behaviour of Pedestrian Social Groups and Its Impact on Crowd Dynamics*, PLOS ONE. [DOI](https://doi.org/10.1371/journal.pone.0010047) | 基于约 1500 个自然场景行人群组，揭示密度上升时并排队形向 V 形转变，并量化社交群组对流动效率的影响。 | P1 / OA | `B1-T1-01-moussaid-social-groups-2010.pdf` |
| B1-T1-02 | Tian et al. (2012), *Experimental study of pedestrian behaviors in a corridor based on digital image processing*, Fire Safety Journal. [DOI](https://doi.org/10.1016/j.firesaf.2011.09.005) | 用视频轨迹提取分析走廊瓶颈中的速度、密度、流率和时间间隔，给出宽度与流率关系及分道效应。 | P1 / 机构 | `B1-T1-02-tian-corridor-video-2012.pdf` |
| B1-T1-03 | Nicolas et al. (2017), *Pedestrian flows through a narrow doorway: Effect of individual behaviours on the global flow and microscopic dynamics*, Transportation Research Part B. [DOI](https://doi.org/10.1016/j.trb.2017.01.008) | 通过礼让/自利行为的受控实验，将行为差异与门口密度、流率及逃逸时间间隔联系起来。 | P1 / 机构 | `B1-T1-03-nicolas-doorway-behaviour-2017.pdf` |
| B1-T1-04 | Parisi et al. (2021), *Pedestrian dynamics at the running of the bulls evidence an inaccessible region in the fundamental diagram*, PNAS. [DOI](https://doi.org/10.1073/pnas.2107827118) | 基于奔牛节真实高速人群，发现速度随密度上升的非常规区间，并提出包含期望速度与跌倒边界的扩展基本图。 | P1 / OA（PMC） | `B1-T1-04-parisi-running-bulls-2021.pdf` |
| B1-T1-05 | Wang et al. (2018), *Step styles of pedestrians at different densities*, Journal of Statistical Mechanics. [DOI](https://doi.org/10.1088/1742-5468/aaac57) | 39 人单列环形实验识别六类步态，说明高密度下步长交替与缩短机制，为微观步态模型提供标定证据。 | P2 / 作者机构稿 | `B1-T1-05-wang-step-styles-2018.pdf` |

## T2：实验与测量（5 篇）

| 编号 | 文献信息与 DOI | 核心贡献 | 优先级 / 获取 | 建议文件名 |
| --- | --- | --- | --- | --- |
| B1-T2-01 | Jin et al. (2019), *Observational characteristics of pedestrian flows under high-density conditions based on controlled experiments*, Transportation Research Part C. [DOI](https://doi.org/10.1016/j.trc.2019.10.013) | 在环形走廊和单列轨道上覆盖最高约 9 人/㎡，比较单双向高密度流、车道形成和无瓶颈时的波动。 | P1 / 机构 | `B1-T2-01-jin-high-density-experiment-2019.pdf` |
| B1-T2-02 | Seitz & Köster (2012), *Natural discretization of pedestrian movement in continuous space*, Physical Review E. [DOI](https://doi.org/10.1103/PhysRevE.86.046108) | 从实测步长—速度关系构造连续空间中的自然步进模型，并用疏散时间进行验证。 | P1 / 机构或作者稿 | `B1-T2-02-seitz-natural-discretization-2012.pdf` |
| B1-T2-03 | Feliciani & Nishinari (2018), *Measurement of congestion and intrinsic risk in pedestrian crowds*, Transportation Research Part C. [DOI](https://doi.org/10.1016/j.trc.2018.03.027) | 提出基于速度矢量场的拥堵水平与人群危险度，比较密度、流量和 crowd pressure，并在多类实验中验证。 | P1 / 机构 | `B1-T2-03-feliciani-congestion-risk-2018.pdf` |
| B1-T2-04 | Zhao & Shibasaki (2005), *A Novel System for Tracking Pedestrians Using Multiple Single-Row Laser-Range Scanners*, IEEE Transactions on Systems, Man, and Cybernetics Part A. [DOI](https://doi.org/10.1109/TSMCA.2005.843396) | 多台单线激光扫描仪融合足部截面，利用卡尔曼滤波跟踪大范围行人轨迹，覆盖约 60×60 m 场地。 | P2 / 机构 | `B1-T2-04-zhao-laser-tracking-2005.pdf` |
| B1-T2-05 | Shi et al. (2024), *How do age compositions affect pedestrian dynamics on stairways? Findings from controlled experiments*, Safety Science. [DOI](https://doi.org/10.1016/j.ssci.2024.106623) | 131 名、五个年龄组的楼梯实验，给出自由速度回归、基本图和同龄/混龄流量差异。 | P1 / 机构 | `B1-T2-05-shi-age-stairway-2024.pdf` |

## T3：设施与场景流动（5 篇）

| 编号 | 文献信息与 DOI | 核心贡献 | 优先级 / 获取 | 建议文件名 |
| --- | --- | --- | --- | --- |
| B1-T3-01 | Geoerg et al. (2019), *The Influence of Wheelchair Users on Movement in a Bottleneck and a Corridor*, Journal of Advanced Transportation. [DOI](https://doi.org/10.1155/2019/9717208) | 大规模受控实验说明轮椅使用者会改变整体速度—密度关系，传统 specific flow 对混合能力人群并不总适用。 | P1 / OA；先核验分区 | `B1-T3-01-geoerg-wheelchair-bottleneck-2019.pdf` |
| B1-T3-02 | Geoerg et al. (2019), *Engineering egress data considering pedestrians with reduced mobility*, Fire and Materials. [DOI](https://doi.org/10.1002/fam.2736) | 汇总身体、认知和年龄相关行动受限者的疏散前及水平移动数据，为性能化防火设计提供工程参数。 | P2 / 机构 | `B1-T3-02-geoerg-reduced-mobility-2019.pdf` |
| B1-T3-03 | Zanlungo et al. (2023), *A pure number to assess “congestion” in pedestrian crowds*, Transportation Research Part C. [DOI](https://doi.org/10.1016/j.trc.2023.104041) | 将拥堵水平改进为无量纲 Congestion Number，并用仿真、受控实验和真实车站数据解释安全阈值。 | P1 / 公开作者稿 | `B1-T3-03-zanlungo-congestion-number-2023.pdf` |
| B1-T3-04 | Hänseler et al. (2017), *A dynamic network loading model for anisotropic and congested pedestrian flows*, Transportation Research Part B. [DOI](https://doi.org/10.1016/j.trb.2016.10.017) | 提出考虑方向各向异性的宏观网络加载模型，并在香港对向流与柏林交叉流数据上标定。 | P1 / 机构 | `B1-T3-04-hanseler-anisotropic-loading-2017.pdf` |
| B1-T3-05 | Deng et al. (2024), *Bidirectional Evacuation in Subway Fires Considering the Number of Retrograders and Proactive Avoidance Behavior Based on Experiments and Simulations*, International Journal of Disaster Risk Science. [DOI](https://doi.org/10.1007/s13753-024-00608-z) | 结合实验与仿真研究地铁火灾双向疏散、逆行人数及主动避让行为，补充交通枢纽冲突流证据。 | P1 / Springer；核验 OA | `B1-T3-05-deng-subway-fire-counterflow-2024.pdf` |

## T4：疏散行为与模型（6 篇）

| 编号 | 文献信息与 DOI | 核心贡献 | 优先级 / 获取 | 建议文件名 |
| --- | --- | --- | --- | --- |
| B1-T4-01 | Han et al. (2017), *Extended route choice model based on available evacuation route set and its application in crowd evacuation simulation*, Simulation Modelling Practice and Theory. [DOI](https://doi.org/10.1016/j.simpat.2017.03.010) | 将路线距离、长度、拥堵和出口容量纳入可用路线集，并以改进社会力模型与路线学习进行仿真。 | P2 / 机构 | `B1-T4-01-han-route-choice-2017.pdf` |
| B1-T4-02 | Wang et al. (2021), *Incorporating human factors in emergency evacuation – An overview of behavioral factors and models*, International Journal of Disaster Risk Reduction. [DOI](https://doi.org/10.1016/j.ijdrr.2021.102254) | 以贯穿疏散全过程的时间线组织实证研究，凝练 42 条行为陈述并对照现有模型能力。 | P1 / OA | `B1-T4-02-wang-human-factors-review-2021.pdf` |
| B1-T4-03 | Tong & Bode (2022), *The principles of pedestrian route choice*, Journal of the Royal Society Interface. [DOI](https://doi.org/10.1098/rsif.2022.0061) | 将路径选择归纳为信息感知、整合、响应和决策机制四项原则，并强调情境依赖。 | P1 / OA | `B1-T4-03-tong-route-choice-principles-2022.pdf` |
| B1-T4-04 | Wang et al. (2019), *A machine learning based study on pedestrian movement dynamics under emergency evacuation*, Fire Safety Journal. [DOI](https://doi.org/10.1016/j.firesaf.2019.04.008) | 从两段准紧急疏散视频提取逐步运动模式，比较统计模型与四类机器学习方法并识别主要影响因素。 | P1 / 机构 | `B1-T4-04-wang-ml-evacuation-motion-2019.pdf` |
| B1-T4-05 | von Sivers et al. (2016), *Modelling social identification and helping in evacuation simulation*, Safety Science. [DOI](https://doi.org/10.1016/j.ssci.2016.07.001) | 将社会认同和帮助行为形式化为行人仿真规则，并以伦敦地铁爆炸疏散资料作定性验证。 | P1 / OA | `B1-T4-05-von-sivers-social-identity-2016.pdf` |
| B1-T4-06 | López-Carmona & Paricio-Garcia (2021), *CellEVAC: An adaptive guidance system for crowd evacuation through behavioral optimization*, Safety Science. [DOI](https://doi.org/10.1016/j.ssci.2021.105215) | 以行为模型和仿真优化动态分配出口指引，同时考虑疏散时间与基本图安全约束。 | P1 / OA | `B1-T4-06-lopez-carmona-cellevac-2021.pdf` |

## T5：安全风险与干预（4 篇）

| 编号 | 文献信息与 DOI | 核心贡献 | 优先级 / 获取 | 建议文件名 |
| --- | --- | --- | --- | --- |
| B1-T5-01 | Barr et al. (2024), *Beyond ‘stampedes’: Towards a new psychology of crowd crush disasters*, British Journal of Social Psychology. [DOI](https://doi.org/10.1111/bjso.12666) | 以历史 crowd-crush 事件资料挑战“集体恐慌/踩踏”叙事，强调群体认同、情境和结构性风险。 | P1 / Wiley；核验 OA | `B1-T5-01-barr-crowd-crush-psychology-2024.pdf` |
| B1-T5-02 | Haghani et al. (2023), *A roadmap for the future of crowd safety research and practice: Introducing the Swiss Cheese Model of Crowd Safety and the imperative of a Vision Zero target*, Safety Science. [DOI](https://doi.org/10.1016/j.ssci.2023.106292) | 提出人群安全“瑞士奶酪”多层防御模型和 Vision Zero 目标，适合作为风险治理与干预框架证据。 | P1 / OA | `B1-T5-02-haghani-crowd-safety-roadmap-2023.pdf` |
| B1-T5-03 | Owaidah et al. (2019), *Review of Modelling and Simulating Crowds at Mass Gathering Events: Hajj as a Case Study*, Journal of Artificial Societies and Social Simulation. [DOI](https://doi.org/10.18564/jasss.3997) | 系统梳理朝觐大型活动中的 ABM、元胞自动机和社会力模型，以及正常和应急人群管理应用。 | P2 / OA；先核验分区 | `B1-T5-03-owaidah-hajj-review-2019.pdf` |
| B1-T5-04 | Al-Shaery et al. (2020), *In-Depth Survey to Detect, Monitor and Manage Crowd*, IEEE Access. [DOI](https://doi.org/10.1109/ACCESS.2020.3038334) | 将技术链划分为人群检测、监测分析和管理决策，比较视觉、无线和混合方法并指出早期预警缺口。 | P2 / OA；先核验分区 | `B1-T5-04-al-shaery-crowd-management-survey-2020.pdf` |

## 备选文献（不计入本批 25 篇）

若 P3/指标复核未通过，可按相同主题替换：

| 主题 | 备选文献 | DOI |
| --- | --- | --- |
| T1 | *First-Order Pedestrian Traffic Flow Theory* (Daamen et al., 2005) | [10.1177/0361198105193400105](https://doi.org/10.1177/0361198105193400105)；旧 DOI `10.3141/1934-05` |
| T1/T2 | *Generating Pedestrian Trajectories Consistent with the Fundamental Diagram Based on Physiological and Psychological Factors* (Narang et al., 2015) | [10.1371/journal.pone.0117856](https://doi.org/10.1371/journal.pone.0117856) |
| T2/T3 | *Understanding pedestrian movement with baggage on stairway: Insights from controlled experiments* (Shi et al., 2024) | [10.1016/j.tbs.2024.100754](https://doi.org/10.1016/j.tbs.2024.100754) |
| T4 | *Developing a database for pedestrians’ earthquake emergency evacuation in indoor scenarios* (Sun et al., 2018) | [10.1371/journal.pone.0197964](https://doi.org/10.1371/journal.pone.0197964) |
| T5 | *ICE-MoCha: Intelligent Crowd Engineering using Mobility Characterization and Analytics* (Jabbari et al., 2019) | [10.3390/s19051025](https://doi.org/10.3390/s19051025) |

## 建议检索与下载顺序

1. 先按 DOI 在学校 Web of Science/JCR 中核验中科院分区、JCI 和引用量；不达标者立即启用备选。
2. 下载 P1 的 OA 正式版本，再通过学校图书馆下载 P1 的机构访问版本。
3. 最后处理 P2，并优先寻找出版社 Version of Record；作者接受稿必须记录版本类型。
4. PDF 下载后按本表文件名保存，但不要直接覆盖已有 Vault 或研究输出。
5. 对每份 PDF 检查题名页、页码、可复制文本和完整参考文献，再进入全文评分与技术预检。

## 本批去重与核验说明

- 以 `knowledge.sqlite3` 中 50 条 literature 记录、34 个原批次 PDF 文件名、Batch 3
  Manifest 以及 `candidates.csv` DOI 为联合去重基线。
- DOI 精确匹配优先；题名规范化匹配用于发现无 DOI 或元数据被截断的本地记录。
- 本批 25 个 DOI 均未与现有 Catalog 的已识别正式版本重复。
- 核验来源包括出版社页面、DOI 注册元数据、作者机构库与开放全文库；未使用预印本替代正式版本。
- 本批检索截止日期为 2026-09-21。

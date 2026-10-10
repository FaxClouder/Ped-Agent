# research-citation-r03 run notes

*status: current；704 包引用评审及结构校验已完成；仅完成引用重做，不导入或评分。*

## 产品、模型与时间
- 产品：Codex desktop；协调者模型：GPT-6（精确型号 unknown）；推理强度 unknown。子代理继承当前模型设置，精确型号与推理强度以各自记录为准。
- 开始：2026-10-08T03:40:00-06:00（近似）；结束：2026-10-08T05:08:44.925870-06:00。

## 上下文与负责范围
| 上下文 | job_id 范围 | 包数 |
| --- | --- | --- |
| /root | citation-0001 至 citation-0176 | 176 |
| /root/review_0177_0352 | citation-0177 至 citation-0352 | 176 |
| /root/review_0353_0528 | citation-0353 至 citation-0528 | 176 |
| /root/review_0529_0704 | citation-0529 至 citation-0704 | 176 |

派发逐字使用 README F6 模板，仅替换起止 job_id，fork_turns=none；没有附加判断规则。

## 关于判断的全部往来
无判断问题、规则解释或标签交换。派发与进度、机械问题、运行记录汇总不含判断规则。

## 允许范围外读取
协调者在首次读到本轮 README 限制之前，按仓库入口要求读取了仓库 README.md、AGENTS.md、docs/project-architecture.md；读取 C:/Users/11315/.codex/skills/using-superpowers/SKILL.md，检索 C:/Users/11315/.codex/memories/MEMORY.md（关键词 calibration、judge-workpackage、research-citation）。记忆内容没有用作本轮判断规则。没有继续读取 docs、experiments 或任何禁读轮次。

## 未覆盖情况
各上下文的原逐包记录保留于下文，并附最终按 manifest 顺序汇总。

## 修正记录
机械修正及完整修改前备份见下文；未进行已写入判断的语义修改。

## 错误、截断与续做
协调者一次输出规则、允许的工作包根 README、校验器和整个 manifest，工具输出截断。规则随后独立完整重读。manifest 将按原始字符区间分段完整重读。该次未读任何 packet，未基于截断内容判断。

## 验证
最终全量校验：704 packets，704 valid，problems=0。校验只涉及结构与逐字复制等机械要求，不证明语义正确或 F7 验收通过。
- citation-0001：文档级引用对应多个片段，规则未覆盖 fragment_id 唯一归属；unknown。

- 协调者显示 citation-0002 时因控制台 GBK 无法编码 emoji 报 UnicodeEncodeError，尚未显示包，改用 PYTHONIOENCODING=utf-8 完整重读；citation-0001 已写入，未改动。

- citation-0004：被引密度单位 mŁ 1 损坏，无法按冻结规则复原；两个引用 pair 记 unknown。

- citation-0005：abstract 引文标题与摘要跨片段，描述性定位唯一归属未覆盖；该 pair unknown。

- citation-0006：同句作者年份括号为转述报告身份或独立引用的性质未覆盖，保留三对 unknown。

- citation-0014：范围下界 Ł 0.38 s 损坏符号无法按规则复原，c16 pair unknown。

- citation-0016：句内 Ziemer et al. (2016) 的转述二级来源引用身份未覆盖，保留 unknown。

- 协调者上下文压缩后续做，已写 citation-0001 至 citation-0016 保持不变。

- citation-0022：作者年份为转述身份或独立引用及片段映射未覆盖，保留 unknown。

- citation-0023：faster for the ascending process 比较措辞歧义，c13 unknown，未自行修补。

- citation-0024：Flötteröd and Rohde (2011) 转述身份或独立引用及片段映射未覆盖，unknown。

- citation-0029：Pouw et al. (2020, 2022) 装置转述身份或独立引用及片段映射未覆盖，unknown。

- citation-0031：Source: Geoerg et al. abstract 与 Source: Li et al. 无明确片段定位，映射未覆盖，unknown。

- citation-0032：Zhou et al. (2022)、Xie et al. (2007) 转述身份或独立引用及片段映射未覆盖，unknown。

- citation-0033：Geoerg et al. (2019) 转述身份或独立引用及片段映射未覆盖，unknown。

- citation-0034：引号内Pouw et al. (2020, 2022)转述作者年份或独立引用身份及映射未覆盖，unknown。

### 子代理 review_0353_0528 机械修正 2026-10-08T04:02:06.396800-06:00

- job_id: citation-0396
- 字段: source_id、label
- 修改前: B6F1/B1F1；partially_supported
- 修改后: B6-F1/B1-F1；partial
- 原因: 上下文压缩摘要使用了缩略标识，续做时误将缩略标识和非枚举拼写写入；仅恢复片段编号格式与 partial 的合法枚举，不改变配对或判断。
- 修改前完整内容备份:
```json
{
 "anchor_id": "citation-0396",
 "citation_pairs": [
  {
   "claim_id": "c14",
   "citation_text": "[Source [\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",612,2381]]",
   "citation_occurrence": 1,
   "source_id": "B6F1",
   "label": "supported",
   "reason": "片段明确说明年龄对上下楼梯速度有显著非线性影响。"
  },
  {
   "claim_id": "c15",
   "citation_text": "[Source [\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",612,2381]]",
   "citation_occurrence": 1,
   "source_id": "B6F1",
   "label": "partially_supported",
   "reason": "片段说明年龄与上下楼梯速度的非线性关系，但未限定为个体无约束速度。"
  },
  {
   "claim_id": "c14",
   "citation_text": "[Source [\"pearl-src-551c6f4b4febcc8a\",\"551c6f4b4febcc8a5cf03b32f6563c2526a802844983bceb6f526f132e6b970a\",\"9595ba7a648dd596515c9b61\",0,1604]]",
   "citation_occurrence": 1,
   "source_id": "B1F1",
   "label": "supported",
   "reason": "摘要明确说明年龄对个体无约束上下楼梯速度有实质性非线性影响。"
  },
  {
   "claim_id": "c15",
   "citation_text": "[Source [\"pearl-src-551c6f4b4febcc8a\",\"551c6f4b4febcc8a5cf03b32f6563c2526a802844983bceb6f526f132e6b970a\",\"9595ba7a648dd596515c9b61\",0,1604]]",
   "citation_occurrence": 1,
   "source_id": "B1F1",
   "label": "supported",
   "reason": "摘要明确说明年龄对个体无约束上下楼梯速度有实质性非线性影响。"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "仅抽取实际引用关系；未引用的 Xie 结论不生成配对。"
}
```

- 协调者第2次上下文压缩后继续：citation-0001 至 citation-0037 已写入，citation-0038 已完整读取并在续接后写入；未重判既有响应。

- citation-0040：作者年份引用 Seyfried et al., 2009a / Garcimartín et al., 2016 无唯一片段映射，unknown；四项来源原样保留 invalid，未补写。

- citation-0043：B3-F1 的密度公式单位原文为ρ =2.5−m，不能确定m⁻¹，c7保留unknown。

- citation-0044：全部文档级标识涉及多片段且未指明片段；映射规则未覆盖，保留unknown。

- citation-0048：文档级标识对应多片段，未覆盖唯一片段归属；保留unknown。

- citation-0050：两处 Pouw et al. (2020, 2022) 作者年份引用不能唯一映射片段，unknown。

- citation-0052：Pouw et al. (2020, 2022) 的片段映射未覆盖，unknown。

- citation-0053：文档级标识对应多片段，未覆盖唯一片段归属；unknown。

- citation-0054：Source 引用仅给引文无标识，固定主张还位于引文内部；片段映射及内部归属未覆盖，unknown。

- citation-0055：6d44文档级标识对应多片段，片段归属未覆盖，unknown。

- citation-0057：B1-F1单位mŁ 1与主张m⁻²不能由所给材料无歧义对应，c13/c14 unknown。

- citation-0060：编号[24]缺少source_fragments身份映射，未覆盖，unknown。

- 协调者上下文第 3 次压缩后继续；citation-0060 已写入，citation-0061 的完整读取及待写判断由上下文摘要保留，随后写入。

## 修正记录：citation-0061 字段名

- 时间：2026-10-08T04:14:41.036046-06:00；字段：citation_extraction_unknown_reason；修改前：字段名 citation_extraction_unknown_reason；修改后：reason；原因：按 Output format 机械修正字段名，字段值及全部判断原样保留。
- 修改前完整文件：
```json
{
  "anchor_id": "citation-0061",
  "citation_pairs": [
    {
      "claim_id": "c9",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "supported",
      "reason": "片段明确要求与同向前人保留有限头距。"
    },
    {
      "claim_id": "c10",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "supported",
      "reason": "片段明确可在不同来向前人后近距离通过。"
    },
    {
      "claim_id": "c11",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3ea58b3238d8dc0e60b1ab59\",0,684]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F1",
      "label": "supported",
      "reason": "片段明确不同来向后出现短时间间隔。"
    },
    {
      "claim_id": "c12",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3ea58b3238d8dc0e60b1ab59\",0,684]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F1",
      "label": "supported",
      "reason": "片段明确同向来人等待更久，并给出25度范围。"
    },
    {
      "claim_id": "c13",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d829a857f5a7eb0b82b25e02\",1087,1778]]]",
      "citation_occurrence": 1,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "片段明确机制比平行车道交替更一般。"
    },
    {
      "claim_id": "c14",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d829a857f5a7eb0b82b25e02\",1087,1778]]]",
      "citation_occurrence": 1,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "片段明确100%匆忙条件仍有强负相关。"
    },
    {
      "claim_id": "c15",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d829a857f5a7eb0b82b25e02\",1087,1778]]]",
      "citation_occurrence": 1,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "片段明确该条件下没有可辨识车道。"
    },
    {
      "claim_id": "c16",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d829a857f5a7eb0b82b25e02\",1087,1778]]]",
      "citation_occurrence": 2,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "片段明确前方空出者可几乎同时跟随不同来向前人。"
    },
    {
      "claim_id": "c17",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d829a857f5a7eb0b82b25e02\",1087,1778]]]",
      "citation_occurrence": 2,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "片段明确无头距时有堵门风险，受试者不冒险。"
    },
    {
      "claim_id": "c18",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a1ac7c127271411f51f93226\",0,75]]]",
      "citation_occurrence": 1,
      "source_id": "B10-F1",
      "label": "unsupported",
      "reason": "所引片段仅为标题，没有显著性及例外条件。"
    },
    {
      "claim_id": "c19",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3ea58b3238d8dc0e60b1ab59\",0,684]]]",
      "citation_occurrence": 2,
      "source_id": "B3-F1",
      "label": "unsupported",
      "reason": "所引片段讨论时间间隔，没有非失控交替的陈述。"
    },
    {
      "claim_id": "c20",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3ea58b3238d8dc0e60b1ab59\",0,684]]]",
      "citation_occurrence": 2,
      "source_id": "B3-F1",
      "label": "unsupported",
      "reason": "所引片段没有有序逐个通过或事先排齐的陈述。"
    }
  ],
  "citation_extraction_unknown": false,
  "citation_extraction_unknown_reason": ""
}
```

## 修正记录：citation-0062 字段名

- 时间：2026-10-08T04:14:41.043944-06:00；字段：citation_extraction_unknown_reason；修改前：字段名 citation_extraction_unknown_reason；修改后：reason；原因：按 Output format 机械修正字段名，字段值及全部判断原样保留。
- 修改前完整文件：
```json
{
  "anchor_id": "citation-0062",
  "citation_pairs": [
    {
      "claim_id": "c10",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "片段明确两者为同一问题的两个方面。"
    },
    {
      "claim_id": "c11",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "片段明确死锁表示预期车道行为受扰。"
    },
    {
      "claim_id": "c12",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468]]]",
      "citation_occurrence": 2,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "片段明确共同研究车道形成与死锁因素。"
    },
    {
      "claim_id": "c11",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468]]]",
      "citation_occurrence": 2,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "片段明确死锁表示预期车道行为受扰。"
    },
    {
      "claim_id": "c12",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F10",
      "label": "supported",
      "reason": "片段明确共同研究两者机制与因素。"
    },
    {
      "claim_id": "c11",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F10",
      "label": "supported",
      "reason": "片段明确死锁表示预期车道行为受扰。"
    },
    {
      "claim_id": "c13",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468]]]",
      "citation_occurrence": 3,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "片段明确速度型个人空间模型复现上下行车道。"
    },
    {
      "claim_id": "c14",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642]]]",
      "citation_occurrence": 2,
      "source_id": "B3-F10",
      "label": "unsupported",
      "reason": "所引片段没有窄楼梯两车道及分布无关条件。"
    },
    {
      "claim_id": "c15",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642]]]",
      "citation_occurrence": 2,
      "source_id": "B3-F10",
      "label": "unsupported",
      "reason": "所引片段没有楼梯与平地车道倾向比较。"
    },
    {
      "claim_id": "c16",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468]]]",
      "citation_occurrence": 4,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "片段列明所有所述操纵参数。"
    },
    {
      "claim_id": "c16",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F2",
      "label": "supported",
      "reason": "片段列明所有所述操纵参数。"
    },
    {
      "claim_id": "c17",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909]]]",
      "citation_occurrence": 2,
      "source_id": "B2-F2",
      "label": "supported",
      "reason": "片段明确起始时间、概率和清空时间。"
    },
    {
      "claim_id": "c18",
      "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909]]]",
      "citation_occurrence": 3,
      "source_id": "B2-F2",
      "label": "unsupported",
      "reason": "所引片段没有Lf及Ls最小20厘米条件。"
    }
  ],
  "citation_extraction_unknown": false,
  "citation_extraction_unknown_reason": ""
}
```

## 修正记录：citation-0063 字段名

- 时间：2026-10-08T04:14:41.050381-06:00；字段：citation_extraction_unknown_reason；修改前：字段名 citation_extraction_unknown_reason；修改后：reason；原因：按 Output format 机械修正字段名，字段值及全部判断原样保留。
- 修改前完整文件：
```json
{
  "anchor_id": "citation-0063",
  "citation_pairs": [
    {
      "claim_id": "c9",
      "citation_text": "[Source [[\"pearl-src-786237ff86268f24\",\"786237ff86268f2405f2d2bec0f2490b1651654c6b5b3c0e402d36e9ebeae52a\",\"6fbdc91592dc16572edfff4b\",0,1282]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "supported",
      "reason": "片段明确有经验且方向感敏锐的领导者可减轻从众不利影响。"
    },
    {
      "claim_id": "c10",
      "citation_text": "[Source [[\"pearl-src-786237ff86268f24\",\"786237ff86268f2405f2d2bec0f2490b1651654c6b5b3c0e402d36e9ebeae52a\",\"81f52cf7be5013945d431eaf\",0,1458]]",
      "citation_occurrence": 1,
      "source_id": "B3-F1",
      "label": "supported",
      "reason": "片段明确领导力强者独立规划并依赖疏散标识。"
    },
    {
      "claim_id": "c11",
      "citation_text": "[Source [[\"pearl-src-786237ff86268f24\",\"786237ff86268f2405f2d2bec0f2490b1651654c6b5b3c0e402d36e9ebeae52a\",\"81f52cf7be5013945d431eaf\",0,1458]]",
      "citation_occurrence": 1,
      "source_id": "B3-F1",
      "label": "supported",
      "reason": "片段明确从众者依赖同伴并选热门而非标识最短路线。"
    },
    {
      "claim_id": "c12",
      "citation_text": "[Source [[\"pearl-src-786237ff86268f24\",\"786237ff86268f2405f2d2bec0f2490b1651654c6b5b3c0e402d36e9ebeae52a\",\"59f7a72bd0aa584aa939e718\",0,573]]",
      "citation_occurrence": 1,
      "source_id": "B6-F1",
      "label": "supported",
      "reason": "片段明确访谈肯定领导者作用及权威说服力。"
    },
    {
      "claim_id": "c13",
      "citation_text": "[Source [[\"pearl-src-786237ff86268f24\",\"786237ff86268f2405f2d2bec0f2490b1651654c6b5b3c0e402d36e9ebeae52a\",\"59df6535e8e038e500d0a631\",0,192]]",
      "citation_occurrence": 1,
      "source_id": "B4-F1",
      "label": "unsupported",
      "reason": "所引片段讨论个性与可见性，没有训练和标识改进建议。"
    },
    {
      "claim_id": "c14",
      "citation_text": "[Source [[\"pearl-src-786237ff86268f24\",\"786237ff86268f2405f2d2bec0f2490b1651654c6b5b3c0e402d36e9ebeae52a\",\"c553fc83fde1c5e29fa49bed\",0,1698]]",
      "citation_occurrence": 1,
      "source_id": "B2-F1",
      "label": "supported",
      "reason": "片段明确低可见度下标识清楚，尤其高层交叉点。"
    },
    {
      "claim_id": "c15",
      "citation_text": "[Source [[\"pearl-src-786237ff86268f24\",\"786237ff86268f2405f2d2bec0f2490b1651654c6b5b3c0e402d36e9ebeae52a\",\"c553fc83fde1c5e29fa49bed\",0,1698]]",
      "citation_occurrence": 1,
      "source_id": "B2-F1",
      "label": "supported",
      "reason": "片段明确短间距鲜亮标识减轻聚集导致的信息损失。"
    },
    {
      "claim_id": "c16",
      "citation_text": "[Source [[\"pearl-src-786237ff86268f24\",\"786237ff86268f2405f2d2bec0f2490b1651654c6b5b3c0e402d36e9ebeae52a\",\"c553fc83fde1c5e29fa49bed\",0,1698]]",
      "citation_occurrence": 1,
      "source_id": "B2-F1",
      "label": "supported",
      "reason": "片段明确所列实时人流声音引导系统的缓解作用。"
    }
  ],
  "citation_extraction_unknown": false,
  "citation_extraction_unknown_reason": ""
}
```

## 修正记录：citation-0064 字段名

- 时间：2026-10-08T04:14:41.056295-06:00；字段：citation_extraction_unknown_reason；修改前：字段名 citation_extraction_unknown_reason；修改后：reason；原因：按 Output format 机械修正字段名，字段值及全部判断原样保留。
- 修改前完整文件：
```json
{
  "anchor_id": "citation-0064",
  "citation_pairs": [
    {
      "claim_id": "c5",
      "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"bad0f368d7eab7e61a8801fa\",0,8],[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"016601a5f2f26416dc1895aa\",0,1043]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "所引片段仅为abstract标题。"
    },
    {
      "claim_id": "c5",
      "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"bad0f368d7eab7e61a8801fa\",0,8],[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"016601a5f2f26416dc1895aa\",0,1043]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "摘要明确增大到达率后竞争空间、正交流人数均衡且无支配流。"
    },
    {
      "claim_id": "c5",
      "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F1",
      "label": "unsupported",
      "reason": "所引片段仅为章节标题。"
    },
    {
      "claim_id": "c5",
      "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F2",
      "label": "supported",
      "reason": "片段明确增大到达率后竞争空间、正交流人数均衡且无支配流。"
    },
    {
      "claim_id": "c6",
      "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"bad0f368d7eab7e61a8801fa\",0,8],[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"016601a5f2f26416dc1895aa\",0,1043]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "所引片段仅为abstract标题。"
    },
    {
      "claim_id": "c6",
      "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"bad0f368d7eab7e61a8801fa\",0,8],[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"016601a5f2f26416dc1895aa\",0,1043]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "摘要明确增大到达率后竞争空间、正交流人数均衡且无支配流。"
    },
    {
      "claim_id": "c6",
      "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F1",
      "label": "unsupported",
      "reason": "所引片段仅为章节标题。"
    },
    {
      "claim_id": "c6",
      "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F2",
      "label": "supported",
      "reason": "片段明确增大到达率后竞争空间、正交流人数均衡且无支配流。"
    },
    {
      "claim_id": "c7",
      "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"bad0f368d7eab7e61a8801fa\",0,8],[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"016601a5f2f26416dc1895aa\",0,1043]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "所引片段仅为abstract标题。"
    },
    {
      "claim_id": "c7",
      "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"bad0f368d7eab7e61a8801fa\",0,8],[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"016601a5f2f26416dc1895aa\",0,1043]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "摘要明确增大到达率后竞争空间、正交流人数均衡且无支配流。"
    },
    {
      "claim_id": "c7",
      "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F1",
      "label": "unsupported",
      "reason": "所引片段仅为章节标题。"
    },
    {
      "claim_id": "c7",
      "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F2",
      "label": "supported",
      "reason": "片段明确增大到达率后竞争空间、正交流人数均衡且无支配流。"
    },
    {
      "claim_id": "c8",
      "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"7d52232625458bb0e72b7c4d\",0,859]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F1",
      "label": "supported",
      "reason": "片段明确均衡时两股流人数相同及随机波动例外。"
    },
    {
      "claim_id": "c9",
      "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"7d52232625458bb0e72b7c4d\",0,859]]]",
      "citation_occurrence": 2,
      "source_id": "B3-F1",
      "label": "supported",
      "reason": "片段明确四股流下模型2与3优劣证据不明确。"
    }
  ],
  "citation_extraction_unknown": false,
  "citation_extraction_unknown_reason": ""
}
```

- 未覆盖情况 citation-0065：Chen et al. (2017) 作者年份标识没有片段映射；保留 unknown。

- 未覆盖情况 citation-0068：文档级引用对应多片段，未指定版本、元素及区间；保留 unknown。

- 未覆盖情况 citation-0070：文档级标识对应多片段，无元素、版本和区间；保留 unknown。

- 未覆盖情况 citation-0073：文档级引用对应多片段，无元素、版本及区间；保留 unknown。

- 未覆盖情况 citation-0074：文档及章节名称对应多片段，无元素、版本和区间；保留 unknown。

- 未覆盖情况 citation-0076：文档级引用对应多片段，无元素、版本及区间；保留 unknown。

- 未覆盖情况 citation-0082：Pouw et al. (2020, 2022) 无具体片段映射；保留 unknown。

- 未覆盖情况 citation-0083：引述内作者年份标识无片段映射且自身嵌在固定claim中；保留 unknown。四项无匹配标识按冻结规则保留 invalid。

- citation-0084：Li (2023) 作者年份引用无法映射片段，unknown，待统一处理。
- 协调者第 4 次上下文压缩：0083 已写入，0084 已完整读取；续做时重新读取 README、规则与 0084 内容，再完成 0084。

- citation-0087：B3-F2 的密度原文单位 ρ =2.5−m 与回答 m⁻¹ 的对应不能确定，unknown，未自行修补。

- citation-0090：Pastor et al. (2015) 作者年份引用映射未覆盖，unknown。

- citation-0093：两种文档级标识对应多片段及 Shahhoseini 作者年份引用，映射未覆盖，unknown。

- citation-0095：文档级 Source: pearl-src-72f5997118149dbe 对应多个片段，映射未覆盖，unknown。

- citation-0097：文档:元素简写无版本与区间，尤其894f1843dce8ee3f1f2098f5对应两片段，映射未覆盖，unknown。

- citation-0098：文档级引用多片段映射未覆盖，且固定c4/c5包含引文，unknown。

- citation-0099：固定c3/c5包含引文本身，对整体claim引用评判未覆盖，unknown。

- citation-0101：文档级标识映射多片段且c3包含引文，unknown。

- citation-0104：三个文档级标识及 Pouw et al. (2020, 2022) 映射未覆盖，c7含引文，unknown。

- 未覆盖情况 citation-0106：c7固定claim包含引用串本身，记unknown。
- 上下文压缩续做：协调者第5次压缩后在0106落盘前继续，重新完整读取README、规则及0106；已写回答不改。

- 未覆盖情况 citation-0107：c3固定claim包含引用串本身，记unknown。

- 未覆盖情况 citation-0108：c7固定claim包含引用串本身，记unknown。

- 未覆盖情况 citation-0109：Moussaïd et al. (2010)作者年份引用缺少片段身份，记unknown。

- 未覆盖情况 citation-0110：c3、c4、c6固定claim包含引用串本身，记unknown。

- 未覆盖情况 citation-0111：c3固定claim包含引用串本身，记unknown。

- 未覆盖情况 citation-0112：c5固定claim包含引用串本身，记unknown。

- 未覆盖情况 citation-0113：c5、c6固定claim包含引用串本身，记unknown。

- 未覆盖情况 citation-0115：Li et al. (2023)作者年份映射未覆盖；c3固定claim含引用串，记unknown。

- 未覆盖情况 citation-0116：Li (2023)、Kremer et al. (2021)作者年份映射未覆盖；c6固定claim含引用串，记unknown。

- 未覆盖情况 citation-0117：Toelch (2015)作者年份引用映射未覆盖，记unknown。

- 未覆盖情况 citation-0119：c3固定claim包含引用串本身，记unknown。

- 未覆盖情况 citation-0120：c3、c5固定claim包含引用串本身，记unknown。

- 未覆盖情况 citation-0123：c5固定claim包含引用串本身，记unknown。

- 未覆盖情况 citation-0124：Moustaid et al. (2021)作者年份引用映射未覆盖，记unknown。

- 未覆盖情况 citation-0125：c1固定claim包含引用串本身，记unknown。

- 未覆盖情况 citation-0126：Li (2023)作者年份映射未覆盖；c6固定claim含引用串，记unknown。

- 未覆盖情况 citation-0127：c2至c8固定claim包含引用串本身，记unknown。

- 协调者第 6 次上下文压缩发生于 citation-0128 读取后、写入前；续做时完整重读 README、规则文件及 citation-0128 原文。

- citation-0128：c4、c5 固定文本包含引文本身；规则未覆盖此整体文本及重复局部区间的引用支持判断，保留 unknown。

- citation-0129：c7、c18 固定文本含引文本身；Twarogowska et al., 2014 未提供作者年份到片段的映射规则，保留 unknown。

- citation-0130：c22 含 Pouw et al. (2020, 2022)，作者年份到片段映射和固定文本含引文情形未覆盖，保留 unknown。

- citation-0131：c4、c7、c11 固定文本含引文本身，未覆盖情形保留 unknown。

- citation-0133：c3、c27、c28 含引文；Helbing and Molnár (1995)、Kwak et al., 2013、Zhou et al., 2022、Li (2023) 作者年份映射未覆盖，保留 unknown。

- citation-0137：c19 含 [25]；数字引用到片段映射及固定文本包含引文情形未覆盖，保留 unknown。

- citation-0138：Tong and Bode, 2021、Haghani and Sarvi, 2018、Lovreglio et al., 2016、Haghani and Sarvi, 2016c 作者年份引用映射未覆盖，部分固定 claim 含引用，保留 unknown。

- citation-0140：c3、c6、c7、c8、c9 固定文本含引文本身，未覆盖情形保留 unknown。

- citation-0141：c2、c3、c5 固定文本含引文本身，未覆盖情况保留 unknown。

- citation-0142：c2、c4 固定文本含引文本身，未覆盖情况保留 unknown。

- citation-0143：文档级 pearl-src 引用、Shahhoseini and Sarvi (2019)、Shahhoseini et al. (2017)、Lian et al. (2017) 到片段映射未覆盖，部分固定文本含引用，保留 unknown。

- citation-0145：c4、c5、c7 固定文本含引文本身，未覆盖情况保留 unknown。

- citation-0146：c4、c5、c7 固定文本含引文本身，未覆盖情况保留 unknown。


### 子代理 review_0353_0528 机械修正 2026-10-08T04:50:31.358512-06:00

- job_id: citation-0527
- 字段: citation_occurrence
- 修改前: c24 的独立 f7927 来源为 2；c25 同串为 3。
- 修改后: 分别为 1、2。
- 原因: 先前其它多来源引用包含相同元素，但不是相同引用字符串。恢复逐字相同完整引用串的出现序号，配对与标签原样保留。
- 修改前完整内容备份:
```json
{
 "anchor_id": "citation-0527",
 "citation_pairs": [
  {
   "claim_id": "c3",
   "citation_text": "[Source: 0e945c62c689effa17c7bd6e; 02b7c706f975111d06fbc121; 8cef73e903f2cdceb2196d56; fcba5856841a678f39a9edc0]",
   "citation_occurrence": 1,
   "source_id": "B2-F1",
   "label": "unsupported",
   "reason": "该独立片段没有此完整结果。"
  },
  {
   "claim_id": "c3",
   "citation_text": "[Source: 0e945c62c689effa17c7bd6e; 02b7c706f975111d06fbc121; 8cef73e903f2cdceb2196d56; fcba5856841a678f39a9edc0]",
   "citation_occurrence": 1,
   "source_id": "B2-F2",
   "label": "unsupported",
   "reason": "该独立片段没有此完整结果。"
  },
  {
   "claim_id": "c3",
   "citation_text": "[Source: 0e945c62c689effa17c7bd6e; 02b7c706f975111d06fbc121; 8cef73e903f2cdceb2196d56; fcba5856841a678f39a9edc0]",
   "citation_occurrence": 1,
   "source_id": "B2-F3",
   "label": "supported",
   "reason": "明确大角度消除拉链效应并改变紧邻运动状态。"
  },
  {
   "claim_id": "c3",
   "citation_text": "[Source: 0e945c62c689effa17c7bd6e; 02b7c706f975111d06fbc121; 8cef73e903f2cdceb2196d56; fcba5856841a678f39a9edc0]",
   "citation_occurrence": 1,
   "source_id": "B2-F4",
   "label": "unsupported",
   "reason": "该独立片段没有此完整结果。"
  },
  {
   "claim_id": "c4",
   "citation_text": "[Source: 555c529a65a6b7bcf3c9fefe; 79288edd58cdf045fc8dd5fe; f445733b44dfbc59d66b6c7e]",
   "citation_occurrence": 1,
   "source_id": "555c529a65a6b7bcf3c9fefe",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c4",
   "citation_text": "[Source: 555c529a65a6b7bcf3c9fefe; 79288edd58cdf045fc8dd5fe; f445733b44dfbc59d66b6c7e]",
   "citation_occurrence": 1,
   "source_id": "B3-F2",
   "label": "supported",
   "reason": "明确180度低密度及消除拉链效应。"
  },
  {
   "claim_id": "c4",
   "citation_text": "[Source: 555c529a65a6b7bcf3c9fefe; 79288edd58cdf045fc8dd5fe; f445733b44dfbc59d66b6c7e]",
   "citation_occurrence": 1,
   "source_id": "B3-F3",
   "label": "unsupported",
   "reason": "只有实验限制。"
  },
  {
   "claim_id": "c9",
   "citation_text": "[Source: 555c529a65a6b7bcf3c9fefe; 79288edd58cdf045fc8dd5fe; f445733b44dfbc59d66b6c7e]",
   "citation_occurrence": 2,
   "source_id": "555c529a65a6b7bcf3c9fefe",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c9",
   "citation_text": "[Source: 555c529a65a6b7bcf3c9fefe; 79288edd58cdf045fc8dd5fe; f445733b44dfbc59d66b6c7e]",
   "citation_occurrence": 2,
   "source_id": "B3-F2",
   "label": "supported",
   "reason": "明确180度低密度及消除拉链效应。"
  },
  {
   "claim_id": "c9",
   "citation_text": "[Source: 555c529a65a6b7bcf3c9fefe; 79288edd58cdf045fc8dd5fe; f445733b44dfbc59d66b6c7e]",
   "citation_occurrence": 2,
   "source_id": "B3-F3",
   "label": "unsupported",
   "reason": "只有实验限制。"
  },
  {
   "claim_id": "c20",
   "citation_text": "[Source: 555c529a65a6b7bcf3c9fefe; 79288edd58cdf045fc8dd5fe; f445733b44dfbc59d66b6c7e]",
   "citation_occurrence": 3,
   "source_id": "555c529a65a6b7bcf3c9fefe",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c20",
   "citation_text": "[Source: 555c529a65a6b7bcf3c9fefe; 79288edd58cdf045fc8dd5fe; f445733b44dfbc59d66b6c7e]",
   "citation_occurrence": 3,
   "source_id": "B3-F2",
   "label": "unsupported",
   "reason": "仅转弯结果没有志愿者限制。"
  },
  {
   "claim_id": "c20",
   "citation_text": "[Source: 555c529a65a6b7bcf3c9fefe; 79288edd58cdf045fc8dd5fe; f445733b44dfbc59d66b6c7e]",
   "citation_occurrence": 3,
   "source_id": "B3-F3",
   "label": "supported",
   "reason": "完整列出年龄97人及不推挤限制。"
  },
  {
   "claim_id": "c21",
   "citation_text": "[Source: 33a4a6922243166a7290140b; b12af7f12e130d78a603e476; bbdcea416393f7810bd15219]",
   "citation_occurrence": 1,
   "source_id": "33a4a6922243166a7290140b",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c21",
   "citation_text": "[Source: 33a4a6922243166a7290140b; b12af7f12e130d78a603e476; bbdcea416393f7810bd15219]",
   "citation_occurrence": 1,
   "source_id": "B4-F2",
   "label": "partial",
   "reason": "说明0.8米主条件但无180度。"
  },
  {
   "claim_id": "c21",
   "citation_text": "[Source: 33a4a6922243166a7290140b; b12af7f12e130d78a603e476; bbdcea416393f7810bd15219]",
   "citation_occurrence": 1,
   "source_id": "bbdcea416393f7810bd15219",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c6",
   "citation_text": "[Source: bbdcea416393f7810bd15219]",
   "citation_occurrence": 1,
   "source_id": "bbdcea416393f7810bd15219",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c7",
   "citation_text": "[Source: bbdcea416393f7810bd15219; 4814416d4f30043232e7e16c]",
   "citation_occurrence": 1,
   "source_id": "bbdcea416393f7810bd15219",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c8",
   "citation_text": "[Source: bbdcea416393f7810bd15219]",
   "citation_occurrence": 2,
   "source_id": "bbdcea416393f7810bd15219",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c12",
   "citation_text": "[Source: bbdcea416393f7810bd15219]",
   "citation_occurrence": 3,
   "source_id": "bbdcea416393f7810bd15219",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c13",
   "citation_text": "[Source: bbdcea416393f7810bd15219; f7927f76e5948da70268d6bc]",
   "citation_occurrence": 1,
   "source_id": "bbdcea416393f7810bd15219",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c7",
   "citation_text": "[Source: bbdcea416393f7810bd15219; 4814416d4f30043232e7e16c]",
   "citation_occurrence": 1,
   "source_id": "B6-F1",
   "label": "supported",
   "reason": "明确自组织利用空间及密度压力增加。"
  },
  {
   "claim_id": "c22",
   "citation_text": "[Source: 765401dbffe7428504a0e64a; 33a4a6922243166a7290140b]",
   "citation_occurrence": 1,
   "source_id": "B5-F1",
   "label": "unsupported",
   "reason": "只有图15/16引导，无此结果。"
  },
  {
   "claim_id": "c22",
   "citation_text": "[Source: 765401dbffe7428504a0e64a; 33a4a6922243166a7290140b]",
   "citation_occurrence": 1,
   "source_id": "33a4a6922243166a7290140b",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c23",
   "citation_text": "[Source: 765401dbffe7428504a0e64a; 33a4a6922243166a7290140b]",
   "citation_occurrence": 2,
   "source_id": "B5-F1",
   "label": "unsupported",
   "reason": "只有图15/16引导，无此结果。"
  },
  {
   "claim_id": "c23",
   "citation_text": "[Source: 765401dbffe7428504a0e64a; 33a4a6922243166a7290140b]",
   "citation_occurrence": 2,
   "source_id": "33a4a6922243166a7290140b",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c18",
   "citation_text": "[Source: 765401dbffe7428504a0e64a; 33a4a6922243166a7290140b]",
   "citation_occurrence": 3,
   "source_id": "B5-F1",
   "label": "unsupported",
   "reason": "只有图15/16引导，无此结果。"
  },
  {
   "claim_id": "c18",
   "citation_text": "[Source: 765401dbffe7428504a0e64a; 33a4a6922243166a7290140b]",
   "citation_occurrence": 3,
   "source_id": "33a4a6922243166a7290140b",
   "label": "unknown",
   "reason": "仅元素ID对应不同截取范围，不能唯一定位片段。"
  },
  {
   "claim_id": "c13",
   "citation_text": "[Source: bbdcea416393f7810bd15219; f7927f76e5948da70268d6bc]",
   "citation_occurrence": 1,
   "source_id": "B8-F2",
   "label": "partial",
   "reason": "包含负角交于前方但没有正角距离增加的说明。"
  },
  {
   "claim_id": "c24",
   "citation_text": "[Source: f7927f76e5948da70268d6bc]",
   "citation_occurrence": 2,
   "source_id": "B8-F2",
   "label": "unsupported",
   "reason": "14对及图坐标在另一片段。"
  },
  {
   "claim_id": "c25",
   "citation_text": "[Source: f7927f76e5948da70268d6bc]",
   "citation_occurrence": 3,
   "source_id": "B8-F2",
   "label": "supported",
   "reason": "明确外侧更快及负角更显著。"
  },
  {
   "claim_id": "c19",
   "citation_text": "[Source: 0e945c62c689effa17c7bd6e; 02b7c706f975111d06fbc121; 8cef73e903f2cdceb2196d56; fcba5856841a678f39a9edc0]",
   "citation_occurrence": 2,
   "source_id": "B2-F1",
   "label": "unsupported",
   "reason": "该独立片段无增加空间假设。"
  },
  {
   "claim_id": "c19",
   "citation_text": "[Source: 0e945c62c689effa17c7bd6e; 02b7c706f975111d06fbc121; 8cef73e903f2cdceb2196d56; fcba5856841a678f39a9edc0]",
   "citation_occurrence": 2,
   "source_id": "B2-F2",
   "label": "unsupported",
   "reason": "该独立片段无增加空间假设。"
  },
  {
   "claim_id": "c19",
   "citation_text": "[Source: 0e945c62c689effa17c7bd6e; 02b7c706f975111d06fbc121; 8cef73e903f2cdceb2196d56; fcba5856841a678f39a9edc0]",
   "citation_occurrence": 2,
   "source_id": "B2-F3",
   "label": "unsupported",
   "reason": "该独立片段无增加空间假设。"
  },
  {
   "claim_id": "c19",
   "citation_text": "[Source: 0e945c62c689effa17c7bd6e; 02b7c706f975111d06fbc121; 8cef73e903f2cdceb2196d56; fcba5856841a678f39a9edc0]",
   "citation_occurrence": 2,
   "source_id": "B2-F4",
   "label": "supported",
   "reason": "明确增加局部空间缓解累积的假设。"
  }
 ],
 "citation_extraction_unknown": true,
 "reason": "555c529、33a4a692、bbdcea416元素均在上下文出现不同范围，引用没有范围，按unknown保留原标识，不用邻接或题意选片段。"
}
```


## 子代理 /root/review_0353_0528 完整运行记录

- 产品：Codex desktop。模型精确名称：unknown；推理强度：unknown。
- 实际开始时间未单独记录；首个响应 creation time 为2026-10-08T03:43:27.553297-06:00，仅作为首个输出时间。结束时间：2026-10-08T04:50:32.919233-06:00。
- 独立上下文 /root/review_0353_0528，按 manifest index 顺序处理 citation-0353 至 citation-0528，176包；全部已冻结。
- 父子代理判断相关往来：无。收到的任务仅为README F6模板；发出范围、完成数量和机械修正进度，没有请求或接受判断口径。
- 范围外读取：开始时在读盲包README限制前读取 C:/Users/11315/.codex/skills/using-superpowers/SKILL.md，并检索 C:/Users/11315/.codex/memories/MEMORY.md 的工作包/校准历史概述。已向协调者披露；没有读取旧响应、其它轮次、expected、事实包或原始论文，没有联网。此概述没有用于包内判断。
- 上下文压缩共7次，分别在0375、0396、0421、0445、0469、0493、0518前后；续做时完整重读待处理包，已写响应未作语义修改。规则在0427、0474以及0528完成前完整重读。
- 错误：0354首次显示触发GBK UnicodeEncodeError，改UTF-8完整重读后评审；0383完整显示输出截断，增大输出预算完整重读后评审；0389写入前JavaScript语法错误，无文件变更，纠正写入调用后继续。最终读取run-notes时工具输出截断，发生在全部176包评审写入后，仅检查既有修正备份存在；未据此产生或调整判断。
- 机械修正：0396、0527；完整旧文件及时间已先备份在上方修正记录。没有其它响应修改。
- 结构验证：官方全包命令在其它分片进行中返回 valid=553/704、problems=151；本分片最初独立 check 为175/176，唯一0527序号格式问题按上方记录修正。当前同一官方check逐个用于本范围：valid=176/176、problems=0。未导入、评分或导出次审。

### 本分片未覆盖情况

- citation-0353：引用句归属可识别；文档级引用对应多个片段，片段归属未被规则覆盖，保留来源原标识并记 unknown。无引用的后续比较不补配。
- citation-0356：Sentence-end citations belong to those sentences. First two document-only citations have unresolved fragment attribution; the third uniquely matches B5-F1.
- citation-0366：Sentence attribution is clear. Section-level document citations do not uniquely name a fragment; preserve identifier and unknown rather than choose a favorable piece.
- citation-0375：实际引用均只给文档标识，且对应多个片段；片段级归属规则未覆盖，按 F6 记录 unknown。
- citation-0382：规则未覆盖文档级标识在多个片段中的唯一归属，按 F6 记录。首句无引文不补配。
- citation-0389：规则未覆盖仅chunk标识遇到同chunk多范围的归属，按 F6 记录 unknown。无引文邻句不补配。
- citation-0398：F6 未覆盖情况：所有实际引用均只给文档级标识，context有多个片段，不自行选择片段；记unknown。首句未引用。
- citation-0403：F6未覆盖：文档级标识不能唯一定位source_fragments，实际配对保留unknown；总结段未引用。
- citation-0416：F6未覆盖：文档级多片段标识无法唯一归属，实际配对unknown；未引用句不生成配对。
- citation-0417：F6未覆盖：来源只写小节名，对应多个片段，保留unknown。同行末引用仅归当前句；前句c2及c6/c7未引用。
- citation-0418：F6未覆盖：551文档缩略引用对应多片段，不选择片段；579缩略标识在context唯一。同句引用各归c14/c15。
- citation-0420：F6未覆盖：文档级标识对应多个来源片段，不自行选择；第一句无引用。
- citation-0436：未覆盖情形：所有实际引用均仅文档标识而context有该文档多个片段；保留引用和来源原标识，不能唯一确定fragment，记unknown并登记run-notes。三人组量化句无引用。
- citation-0438：未覆盖情形：仅文档级标识对应多个片段，无法确定fragment，不猜补；逐句保留配对并登记run-notes。三人组量化句无引用。
- citation-0449：未覆盖格式：文档级标识在当前context匹配多个片段，保留原标识并unknown；唯一片段引用正常判断。
- citation-0458：未覆盖格式：同一文档级标识匹配多个context片段，保留原标识并unknown，不靠内容猜选。
- citation-0465：未覆盖格式：两个文档级来源都匹配多个context片段，保留原标识并unknown。
- citation-0474：标题级来源及same article指代不能唯一映射片段。首句c5无引用，不将后句引用移给它。
- citation-0478：两种文档级ID均对应多个片段，保留unknown；关系段首句c35未获引用。
- citation-0494：文档级标识无法唯一对应source_fragments，登记提取不确定。
- citation-0497：六处文档级引用均无法唯一定位片段，保留原标识并登记提取不确定。
- citation-0498：六处文档级引用均不能唯一定位片段，登记提取不确定。
- citation-0514：八处文档级引用均无法唯一对应片段，登记提取不确定。
- citation-0527：555c529、33a4a692、bbdcea416元素均在上下文出现不同范围，引用没有范围，按unknown保留原标识，不用邻接或题意选片段。
- citation-0528：末段另有两处实际引用，但其句内断言不对应固定claims的occurrences；不可新增或改写claims，未建这些对并保留提取不确定，交统一处理。

- citation-0148：c3、c5 固定文本含引文本身，未覆盖情况保留 unknown。

协调者第7次上下文压缩后续做：已冻结 citation-0001–0148；重新完整阅读 README 与规则，并重新显示0149后继续。恢复时误读不存在的 prompts/system.txt，命令报路径不存在，无文件内容读取，随后改读 system-prompts/layer4-citation-r03.md。

- citation-0150：c7、c9、c10 的固定 claim 含完整引用；规则未覆盖此类整体 claim 配对，记 unknown。

- citation-0151：c3、c5 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。

- citation-0152：四处引用仅含文档短标识，未给片段及区间，冻结规则未覆盖唯一映射；c5、c6固定文本含引用亦未覆盖，记 unknown。

- citation-0153：c7、c8 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。

- citation-0155：c3、c4、c6、c8、c9、c13、c14、c15 固定 claim 整体含完整引用，规则未覆盖这种配对判断，记 unknown。

- citation-0156：c2 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。

- citation-0157：引用仅有文档短标识，不能唯一映射片段；c4、c8、c10整体固定文本含引用，规则亦未覆盖，均记 unknown。

- citation-0158：c7、c8、c9、c11 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。

- citation-0160：c4、c6、c7 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。

- citation-0161：c1–c6 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。

- citation-0162：c6、c8、c9 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。

- citation-0163：c2 固定 claim 包含完整引用且另有部分重复区间，规则未覆盖该整体 claim 配对，记 unknown。

- citation-0164：c4、c5、c6、c9 固定claim含完整引用；Ziemer et al. (2016)作者年份引用的片段映射未覆盖，记 unknown。

- citation-0165：引用只给文档ID，未覆盖唯一片段映射；c4、c5、c11–c14固定文本含完整引用亦未覆盖，记 unknown。

- citation-0166：c10、c11 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。

- citation-0168：Li et al. (2023)作者年份引用的来源片段映射未覆盖，记 unknown。

- citation-0169：三处引用只有文档ID，唯一片段映射未覆盖，记 unknown。

- 协调者第 8 次上下文压缩：citation-0169 已冻结，citation-0170 已完整显示但未写入；恢复后重新完整阅读规则与 citation-0170，再继续。

- citation-0170：引用均为无版本、无偏移的文档与元素标识；精确片段映射未覆盖。c4、c6、c9固定claim包含引用，整体判断未覆盖，未拆分。

- citation-0171：c1固定文本包含引用且重复位置文字不同，规则未覆盖该整体claim的引用判断；不拆分或修改。

- citation-0172：c2、c4、c5、c8、c9、c14固定claim含引用原文，整体判断规则未覆盖。

- citation-0173：c4、c7固定claim包含引用，整体判断规则未覆盖；不拆分改写。

## review_0529_0704 修正记录

### citation-0596 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0596",
 "citation_pairs": [
  {
   "claim_id": "c9",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-bae14f716cb901cf\",\"bae14f716cb901cf43866fc6d80c3cfc861eb8a4c8c3ef9a85b478236c11f465\",\"e4f03e5cb3b46189e99fe522\",0,350]]]",
   "citation_occurrence": 1,
   "label": "partial"
  },
  {
   "claim_id": "c10",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-bae14f716cb901cf\",\"bae14f716cb901cf43866fc6d80c3cfc861eb8a4c8c3ef9a85b478236c11f465\",\"e4f03e5cb3b46189e99fe522\",0,350]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c11",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-bae14f716cb901cf\",\"bae14f716cb901cf43866fc6d80c3cfc861eb8a4c8c3ef9a85b478236c11f465\",\"e4f03e5cb3b46189e99fe522\",0,350]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-bae14f716cb901cf\",\"bae14f716cb901cf43866fc6d80c3cfc861eb8a4c8c3ef9a85b478236c11f465\",\"e4f03e5cb3b46189e99fe522\",0,350]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"b9db75289de0178e7813370b\",0,1093]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-bae14f716cb901cf\",\"bae14f716cb901cf43866fc6d80c3cfc861eb8a4c8c3ef9a85b478236c11f465\",\"221371430d88a6bbec02899d\",0,1033]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-bae14f716cb901cf\",\"bae14f716cb901cf43866fc6d80c3cfc861eb8a4c8c3ef9a85b478236c11f465\",\"221371430d88a6bbec02899d\",0,1033]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c16",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-bae14f716cb901cf\",\"bae14f716cb901cf43866fc6d80c3cfc861eb8a4c8c3ef9a85b478236c11f465\",\"221371430d88a6bbec02899d\",0,1033]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c17",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-bae14f716cb901cf\",\"bae14f716cb901cf43866fc6d80c3cfc861eb8a4c8c3ef9a85b478236c11f465\",\"221371430d88a6bbec02899d\",0,1033]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-bae14f716cb901cf\",\"bae14f716cb901cf43866fc6d80c3cfc861eb8a4c8c3ef9a85b478236c11f465\",\"221371430d88a6bbec02899d\",0,1033]]]",
   "citation_occurrence": 2,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "逐项核对各引用片段；实验流行程度有据，但首项的 Part I 归属在该片段中未明确。其余引文逐项得到所引片段支持。"
}
```

### citation-0597 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0597",
 "citation_pairs": [
  {
   "claim_id": "c6",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c6",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c6",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c7",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c7",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c7",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c8",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c8",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c8",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 3,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 3,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 3,
   "label": "supported"
  },
  {
   "claim_id": "c10",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 3,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 3,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"d8c6901413398569b0283a40\",0,43],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"2e643ab3110014a892a181ca\",0,826],[\"pearl-src-4b758ccb41af532c\",\"4b758ccb41af532c4fadeb2182ce2b7d41e0eaee6abe140c209f6140842322d5\",\"ff0cc007e9f81796a43bacd4\",0,452]]]",
   "citation_occurrence": 3,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "各引用展开为三个片段分别核对；标题不提供断言证据。两流平衡与竞争由第二片段支持，四流拥堵和随机切换由第三片段支持。"
}
```

### citation-0598 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0598",
 "citation_pairs": [
  {
   "claim_id": "c19",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"0cae563adabda391044fe00c\",1103,1721]]]",
   "citation_occurrence": 1,
   "label": "partial"
  },
  {
   "claim_id": "c19",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"208ac9e64bf05f9b7c9e6d95\",0,287]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B3-F5",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"3a82c59c4747dc9101073814\",0,243]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c20",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"0cae563adabda391044fe00c\",1103,1721]]]",
   "citation_occurrence": 2,
   "label": "partial"
  },
  {
   "claim_id": "c20",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"208ac9e64bf05f9b7c9e6d95\",0,287]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c21",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"0cae563adabda391044fe00c\",1103,1721]]]",
   "citation_occurrence": 3,
   "label": "partial"
  },
  {
   "claim_id": "c21",
   "source_id": "B3-F5",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"3a82c59c4747dc9101073814\",0,243]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"208ac9e64bf05f9b7c9e6d95\",0,287]]]",
   "citation_occurrence": 3,
   "label": "supported"
  },
  {
   "claim_id": "c20",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"208ac9e64bf05f9b7c9e6d95\",0,287]]]",
   "citation_occurrence": 3,
   "label": "supported"
  },
  {
   "claim_id": "c22",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"208ac9e64bf05f9b7c9e6d95\",0,287]]]",
   "citation_occurrence": 3,
   "label": "supported"
  },
  {
   "claim_id": "c24",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"286c4899a2a26cf364203f62\",0,8]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c25",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"286c4899a2a26cf364203f62\",0,8]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"286c4899a2a26cf364203f62\",0,8]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B9-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"d76adba214dbfdf04e44c069\",0,24]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c21",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"0cae563adabda391044fe00c\",1103,1721]]]",
   "citation_occurrence": 4,
   "label": "partial"
  },
  {
   "claim_id": "c21",
   "source_id": "B3-F5",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"3a82c59c4747dc9101073814\",0,243]]]",
   "citation_occurrence": 3,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "均值摘要未给标准差，复合数值断言仅部分支持；讨论片段支持对应均值及标准差。实验地点、设备和起步提取阈值误引标题片段，未获支持。无引用的后续解释不补配对。"
}
```

### citation-0599 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0599",
 "citation_pairs": [
  {
   "claim_id": "c9",
   "source_id": "pearl-src-2c6f1c912f4d8ceb",
   "citation_text": "[pearl-src-2c6f1c912f4d8ceb]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c10",
   "source_id": "pearl-src-2c6f1c912f4d8ceb",
   "citation_text": "[pearl-src-2c6f1c912f4d8ceb]",
   "citation_occurrence": 2,
   "label": "unknown"
  },
  {
   "claim_id": "c11",
   "source_id": "pearl-src-2c6f1c912f4d8ceb",
   "citation_text": "[pearl-src-2c6f1c912f4d8ceb]",
   "citation_occurrence": 3,
   "label": "unknown"
  },
  {
   "claim_id": "c12",
   "source_id": "pearl-src-2c6f1c912f4d8ceb",
   "citation_text": "[pearl-src-2c6f1c912f4d8ceb]",
   "citation_occurrence": 4,
   "label": "unknown"
  },
  {
   "claim_id": "c13",
   "source_id": "pearl-src-2c6f1c912f4d8ceb",
   "citation_text": "[pearl-src-2c6f1c912f4d8ceb]",
   "citation_occurrence": 5,
   "label": "unknown"
  },
  {
   "claim_id": "c14",
   "source_id": "pearl-src-2c6f1c912f4d8ceb",
   "citation_text": "[pearl-src-2c6f1c912f4d8ceb]",
   "citation_occurrence": 6,
   "label": "unknown"
  },
  {
   "claim_id": "c15",
   "source_id": "pearl-src-2c6f1c912f4d8ceb",
   "citation_text": "[pearl-src-2c6f1c912f4d8ceb]",
   "citation_occurrence": 7,
   "label": "unknown"
  },
  {
   "claim_id": "c16",
   "source_id": "pearl-src-2c6f1c912f4d8ceb",
   "citation_text": "[pearl-src-2c6f1c912f4d8ceb]",
   "citation_occurrence": 7,
   "label": "unknown"
  }
 ],
 "citation_extraction_unknown": true,
 "reason": "引用只给文档标识，该文档在本包有多个片段，无法唯一映射；保持 unknown，不从有利片段反推引用。"
}
```

### citation-0600 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0600",
 "citation_pairs": [
  {
   "claim_id": "c19",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B3-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B3-F4",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B3-F5",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c20",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c20",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c20",
   "source_id": "B3-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c20",
   "source_id": "B3-F4",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c20",
   "source_id": "B3-F5",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c21",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c21",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c21",
   "source_id": "B3-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c21",
   "source_id": "B3-F4",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c21",
   "source_id": "B3-F5",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c22",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c22",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c22",
   "source_id": "B3-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c22",
   "source_id": "B3-F4",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c22",
   "source_id": "B3-F5",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"2111d7f5bf4462daa856271e\",0,4],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"db60891819a0985e1c6de1c1\",0,15],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c23",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",612,2381]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c24",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",612,2381]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c25",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ab0b49fa4bb4ffcd50d05261\",841,2232],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8a9e9821683d70156c2af28c\",0,58],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"130435036d8a49cefd12e34e\",0,4]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c25",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ab0b49fa4bb4ffcd50d05261\",841,2232],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8a9e9821683d70156c2af28c\",0,58],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"130435036d8a49cefd12e34e\",0,4]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c25",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ab0b49fa4bb4ffcd50d05261\",841,2232],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8a9e9821683d70156c2af28c\",0,58],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"130435036d8a49cefd12e34e\",0,4]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c25",
   "source_id": "Pouw et al. (2020, 2022)",
   "citation_text": "Pouw et al. (2020, 2022)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F4",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F5",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F6",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F7",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F8",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F9",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F10",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F11",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F12",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F13",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F14",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F15",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F4",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F5",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F6",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F7",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F8",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F9",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F10",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F11",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F12",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F13",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F14",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c27",
   "source_id": "B5-F15",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F4",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F5",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F6",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F7",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F8",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F9",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F10",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F11",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F12",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F13",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F14",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c28",
   "source_id": "B5-F15",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F4",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F5",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F6",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F7",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F8",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F9",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F10",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F11",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F12",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F13",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F14",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c29",
   "source_id": "B5-F15",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"eafbd03324443a5140387fa8\",0,75],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fe1af6733a3e1ea8ec70bb5b\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"dd51408f9f13e5600a4a36de\",0,282],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c8331b8813af3d4c411852b9\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e67d83c3e3d947e2da7f50d3\",0,29],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e7c3fdba914603a4630a9ca7\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"4a99a600faeb8bc344557a34\",0,32],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"96b98dfd5ab77bc03e78f994\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"149c1c56f9d1aad094a163ae\",0,332],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ee0d144fa4a49b19515e2599\",0,26],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"d37b6c04e9a5a3e31040aa2f\",0,34],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8444566ed859a48301ba6cbd\",0,3],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"f48909334d3bbb57f3c19599\",0,42],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"fa3192017ce649f41b7f208c\",0,1],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"8d460866ada84a03bd2c7dcc\",0,84]]]",
   "citation_occurrence": 1,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "句末引用仅覆盖所在句。每个展开片段独立核验；数据正文支持轨迹与统计项，分类、阈值、区域和子集分别位于不同片段。作者年份标识未注册为片段来源。"
}
```

### citation-0602 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0602",
 "citation_pairs": [
  {
   "claim_id": "c5",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"1b9f144ee3bde4ac91d0e3da\",459,1289]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c6",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"405b7d27b0f34931698a0a2a\",0,654]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c7",
   "source_id": "B7-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"afd571c745f8017c595970f3\",620,1286]]]",
   "citation_occurrence": 1,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "三处唯一片段分别明确给出前方最小间距、两级踏步尺寸和占用增加时邻距收敛值。"
}
```

### citation-0603 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0603",
 "citation_pairs": [
  {
   "claim_id": "c6",
   "source_id": "B1-F1",
   "citation_text": "[pearl-src-23359e3c52013ff2]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c7",
   "source_id": "pearl-src-4e58ae08e48f6688",
   "citation_text": "[pearl-src-4e58ae08e48f6688]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c8",
   "source_id": "pearl-src-4e58ae08e48f6688",
   "citation_text": "[pearl-src-4e58ae08e48f6688]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c9",
   "source_id": "pearl-src-4e58ae08e48f6688",
   "citation_text": "[pearl-src-4e58ae08e48f6688]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c10",
   "source_id": "pearl-src-53eaa084325fad7e",
   "citation_text": "[pearl-src-53eaa084325fad7e]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c11",
   "source_id": "pearl-src-53eaa084325fad7e",
   "citation_text": "[pearl-src-53eaa084325fad7e]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c12",
   "source_id": "pearl-src-660b3fd7d42107c6",
   "citation_text": "[pearl-src-660b3fd7d42107c6]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c12",
   "source_id": "pearl-src-2a5248d83478c25a",
   "citation_text": "[pearl-src-2a5248d83478c25a]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c13",
   "source_id": "pearl-src-2a5248d83478c25a",
   "citation_text": "[pearl-src-2a5248d83478c25a]",
   "citation_occurrence": 1,
   "label": "unknown"
  }
 ],
 "citation_extraction_unknown": true,
 "reason": "首个文档标识仅对应一个片段并支持断言；其余文档标识对应多个片段，无法唯一消歧，保持 unknown。"
}
```

### citation-0604 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0604",
 "citation_pairs": [
  {
   "claim_id": "c13",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-7bb98df43e00bda3\",\"7bb98df43e00bda366c28a4250b0be8aa8bb2d0b4368cfb0f47ebf8a62ed2741\",\"5e8459e18d785f6fe3c3de72\",0,506]]]",
   "citation_occurrence": 1,
   "label": "partial"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-7bb98df43e00bda3\",\"7bb98df43e00bda366c28a4250b0be8aa8bb2d0b4368cfb0f47ebf8a62ed2741\",\"5e8459e18d785f6fe3c3de72\",0,506]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"d76adba214dbfdf04e44c069\",0,24]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"d76adba214dbfdf04e44c069\",0,24]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c17",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"134464de1602d7e889c6160e\",0,423]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c18",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"134464de1602d7e889c6160e\",0,423]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"134464de1602d7e889c6160e\",0,423]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c20",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"134464de1602d7e889c6160e\",0,423]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "运动激活摘要支持初始化阶段用途，但未明确足够移动空间条件；起步定义误引标题，起步统计误引定义片段，均未得到所引片段支持。"
}
```

### citation-0605 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0605",
 "citation_pairs": [
  {
   "claim_id": "c7",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913]]]",
   "citation_occurrence": 1,
   "label": "partial"
  },
  {
   "claim_id": "c8",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c9",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c10",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c11",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"87fb4fe2b97e4e615e2d2b70\",0,813]]]",
   "citation_occurrence": 1,
   "label": "partial"
  },
  {
   "claim_id": "c16",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c17",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913]]]",
   "citation_occurrence": 2,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "所引正文支持模拟网格、等待区、参数与总时间结果及验证限制；首片段未注明柱阵，另一片段未明确仅初始阶段较慢，复合断言部分支持。"
}
```

### citation-0606 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0606",
 "citation_pairs": [
  {
   "claim_id": "c5",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"1b9f144ee3bde4ac91d0e3da\",1031,1840]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c6",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"405b7d27b0f34931698a0a2a\",0,654],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e099acd99982a32265c620fe\",0,696]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c6",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"405b7d27b0f34931698a0a2a\",0,654],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e099acd99982a32265c620fe\",0,696]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c6",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"405b7d27b0f34931698a0a2a\",0,654],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e099acd99982a32265c620fe\",0,696]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c6",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"405b7d27b0f34931698a0a2a\",0,654],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e099acd99982a32265c620fe\",0,696]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c7",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"405b7d27b0f34931698a0a2a\",0,654],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e099acd99982a32265c620fe\",0,696]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c7",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"405b7d27b0f34931698a0a2a\",0,654],[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"e099acd99982a32265c620fe\",0,696]]]",
   "citation_occurrence": 2,
   "label": "partial"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "摘要支持前方最小距离。第三块首片段支持踏步和密度极限，第二片段只给最可能邻距而未建立密度增加时的极限关系。"
}
```

### citation-0607 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0607",
 "citation_pairs": [
  {
   "claim_id": "c8",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-6953122155fbbf77\",\"6953122155fbbf77670d7fc408c781872ff59a274fc38ed045ad5496bde2c213\",\"c1ad06a31dee80bc9a833e21\",2861,3832]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c8",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-7bb98df43e00bda3\",\"7bb98df43e00bda366c28a4250b0be8aa8bb2d0b4368cfb0f47ebf8a62ed2741\",\"9dc02308c375ed03bef3fe4b\",0,1223]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c9",
   "source_id": "B8-F1",
   "citation_text": "[Source [[\"pearl-src-7bb98df43e00bda3\",\"7bb98df43e00bda366c28a4250b0be8aa8bb2d0b4368cfb0f47ebf8a62ed2741\",\"b3e40d584150fb776cf46efb\",0,909]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c10",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-7bb98df43e00bda3\",\"7bb98df43e00bda366c28a4250b0be8aa8bb2d0b4368cfb0f47ebf8a62ed2741\",\"7e7f5b5e142ac9d9261303ad\",0,7]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c11",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-7bb98df43e00bda3\",\"7bb98df43e00bda366c28a4250b0be8aa8bb2d0b4368cfb0f47ebf8a62ed2741\",\"7e7f5b5e142ac9d9261303ad\",0,7]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-7bb98df43e00bda3\",\"7bb98df43e00bda366c28a4250b0be8aa8bb2d0b4368cfb0f47ebf8a62ed2741\",\"266918b39032044928942748\",0,503]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c11",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-7bb98df43e00bda3\",\"7bb98df43e00bda366c28a4250b0be8aa8bb2d0b4368cfb0f47ebf8a62ed2741\",\"266918b39032044928942748\",0,503]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-7bb98df43e00bda3\",\"7bb98df43e00bda366c28a4250b0be8aa8bb2d0b4368cfb0f47ebf8a62ed2741\",\"266918b39032044928942748\",0,503]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-7bb98df43e00bda3\",\"7bb98df43e00bda366c28a4250b0be8aa8bb2d0b4368cfb0f47ebf8a62ed2741\",\"266918b39032044928942748\",0,503]]]",
   "citation_occurrence": 2,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "位置及数值引用有对应正文支持。运动更快更平滑误引 Summary 标题；速度调整正文支持更快但未给平滑结论。未引用的末句不补配对。"
}
```

### citation-0608 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0608",
 "citation_pairs": [
  {
   "claim_id": "c5",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"beb5adcbd80166590fc6006f\",0,32]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c6",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"beb5adcbd80166590fc6006f\",0,32]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c7",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"72cd110d07bae382e63e9cff\",0,1173]]]",
   "citation_occurrence": 1,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "前两引用为网站地址标题片段，没有阈值与面积证据；第三引用正文明确支持理想实验中的密度上限和 1 m 距离。"
}
```

### citation-0609 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0609",
 "citation_pairs": [
  {
   "claim_id": "c9",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"9f68889029cd76dea0afc859\",24,88],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"2691dc234a0bb0a74a592ff8\",0,244],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",0,175]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"9f68889029cd76dea0afc859\",24,88],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"2691dc234a0bb0a74a592ff8\",0,244],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",0,175]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"9f68889029cd76dea0afc859\",24,88],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"2691dc234a0bb0a74a592ff8\",0,244],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",0,175]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c9",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"9f68889029cd76dea0afc859\",24,88],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"2691dc234a0bb0a74a592ff8\",0,244],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",0,175]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "Li (2023)",
   "citation_text": "Li (2023)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c10",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"9f68889029cd76dea0afc859\",24,88],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"2691dc234a0bb0a74a592ff8\",0,244],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",0,175]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"9f68889029cd76dea0afc859\",24,88],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"2691dc234a0bb0a74a592ff8\",0,244],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",0,175]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"9f68889029cd76dea0afc859\",24,88],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"2691dc234a0bb0a74a592ff8\",0,244],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",0,175]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c10",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"9f68889029cd76dea0afc859\",24,88],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"2691dc234a0bb0a74a592ff8\",0,244],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",0,175]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "Li (2023)",
   "citation_text": "Li (2023)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c11",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c11",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c11",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c11",
   "source_id": "B5-F4",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B5-F4",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B5-F4",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B5-F4",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F4",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c16",
   "source_id": "B5-F4",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"463ad2061eacd9c4935172da\",0,51],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"7383973091bf80056322ba99\",0,478],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"d34e9efdcf163df1c61c19a0\",0,187],[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"fde0c0afad0fe8e3286fac81\",0,550]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "仅配实际引用所在句。注意力机制、速度损失定义、设计取值及流率分别在不同片段中支持，其他展开片段未支持对应断言；作者年份标识未注册。"
}
```

### citation-0610 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0610",
 "citation_pairs": [
  {
   "claim_id": "c12",
   "source_id": "pearl-src-2d794479f1d822ef",
   "citation_text": "[pearl-src-2d794479f1d822ef]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c13",
   "source_id": "pearl-src-2d794479f1d822ef",
   "citation_text": "[pearl-src-2d794479f1d822ef]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c14",
   "source_id": "pearl-src-2d794479f1d822ef",
   "citation_text": "[pearl-src-2d794479f1d822ef]",
   "citation_occurrence": 2,
   "label": "unknown"
  },
  {
   "claim_id": "c15",
   "source_id": "pearl-src-2d794479f1d822ef",
   "citation_text": "[pearl-src-2d794479f1d822ef]",
   "citation_occurrence": 2,
   "label": "unknown"
  },
  {
   "claim_id": "c16",
   "source_id": "pearl-src-2d794479f1d822ef",
   "citation_text": "[pearl-src-2d794479f1d822ef]",
   "citation_occurrence": 2,
   "label": "unknown"
  },
  {
   "claim_id": "c17",
   "source_id": "pearl-src-49fbc8413e27f3f1",
   "citation_text": "[pearl-src-49fbc8413e27f3f1]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c18",
   "source_id": "pearl-src-49fbc8413e27f3f1",
   "citation_text": "[pearl-src-49fbc8413e27f3f1]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c19",
   "source_id": "B5-F1",
   "citation_text": "[pearl-src-c855476d71620c33]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c20",
   "source_id": "B5-F1",
   "citation_text": "[pearl-src-c855476d71620c33]",
   "citation_occurrence": 1,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": true,
 "reason": "两篇文档级引用均对应多个片段，保留 unknown。PW/AR 引用的文档仅一个片段并直接支持相反效应；末尾限制句无对应固定事实断言。"
}
```

### citation-0611 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0611",
 "citation_pairs": [
  {
   "claim_id": "c14",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"6b0259f115d81d8c13143253\",0,627]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"6b0259f115d81d8c13143253\",0,627]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c16",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"6b0259f115d81d8c13143253\",0,627]]]",
   "citation_occurrence": 1,
   "label": "partial"
  },
  {
   "claim_id": "c14",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"5ce073751b40b8ac4ad8831b\",655,1079]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"5ce073751b40b8ac4ad8831b\",655,1079]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"5ce073751b40b8ac4ad8831b\",655,1079]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c16",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"5ce073751b40b8ac4ad8831b\",655,1079]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c17",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"5ce073751b40b8ac4ad8831b\",655,1079]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"a119e8d62536c6979056c6bc\",0,596]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c20",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"a119e8d62536c6979056c6bc\",0,596]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c21",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"a119e8d62536c6979056c6bc\",596,859]]]",
   "citation_occurrence": 1,
   "label": "partial"
  },
  {
   "claim_id": "c22",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"a119e8d62536c6979056c6bc\",596,859]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c23",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"a119e8d62536c6979056c6bc\",596,859]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c24",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"d30ae50bcc903e344898ac39\",214,431]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c25",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-06ceea72728432ef\",\"06ceea72728432ef0f240b5619e01b283d15f07696bde03a03b68355cf895b1d\",\"d30ae50bcc903e344898ac39\",214,431]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "片段独立支持非空间状态、模型结构和后验敏感性；不建模走廊不完全等同排除节点相互作用。冗余参数片段缺条件前半句；阈值设定误引归一化片段。未引句不补配对。"
}
```

### citation-0612 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0612",
 "citation_pairs": [
  {
   "claim_id": "c4",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c4",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c4",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c4",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c5",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c5",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c5",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c5",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c6",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c6",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c6",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c6",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"0261a916e6d7b6e8414671cb\",0,8],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"c1de4758e994a36d63c34aff\",0,676],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"00ba1d95e2e6ad30dcee5529\",0,46],[\"pearl-src-69cbf5aaec4292e0\",\"69cbf5aaec4292e04890df7895629fecb865930f57274291060e02580287d3c6\",\"bf193900051df680d552a822\",0,165]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "摘要正文直接支持增量转移原理、双向收发流及单向运动波一致性；标题和版权许可片段均不支持这些断言。"
}
```

### citation-0613 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0613",
 "citation_pairs": [
  {
   "claim_id": "c14",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ab0b49fa4bb4ffcd50d05261\",686,1470]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"ab0b49fa4bb4ffcd50d05261\",686,1470]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c17",
   "source_id": "B7-F1",
   "citation_text": "[Source [[\"pearl-src-551c6f4b4febcc8a\",\"551c6f4b4febcc8a5cf03b32f6563c2526a802844983bceb6f526f132e6b970a\",\"32b01cff047fe6941c33fafc\",0,1005]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "B7-F1",
   "citation_text": "[Source [[\"pearl-src-551c6f4b4febcc8a\",\"551c6f4b4febcc8a5cf03b32f6563c2526a802844983bceb6f526f132e6b970a\",\"32b01cff047fe6941c33fafc\",0,1005]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "仅配实际引用所在句：首引用支持上下楼速度众数，第二支持年龄与基本图研究描述，但未提供足迹样本。无引用句不补证据。"
}
```

### citation-0615 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0615",
 "citation_pairs": [
  {
   "claim_id": "c5",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"8e95ddb1ee57b48c085e3d07\",0,584]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "所引片段讨论密度持续时间与三列通道，未给运行条件下两宽度疏散时间及累计流相似的结论。"
}
```

### citation-0616 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0616",
 "citation_pairs": [
  {
   "claim_id": "c11",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"6163fd723226465aa6add874\",0,20]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"6163fd723226465aa6add874\",0,20]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"6163fd723226465aa6add874\",0,20]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"6163fd723226465aa6add874\",0,20]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"6163fd723226465aa6add874\",0,20]]",
   "citation_occurrence": 3,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"6163fd723226465aa6add874\",0,20]]",
   "citation_occurrence": 3,
   "label": "unsupported"
  },
  {
   "claim_id": "c17",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"c6eecc31b62bec62610b32c8\",0,807]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"c6eecc31b62bec62610b32c8\",0,807]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"70a4406a9589fee162244975\",0,755]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c20",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"70a4406a9589fee162244975\",0,755]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c21",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"70a4406a9589fee162244975\",0,755]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c22",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"70a4406a9589fee162244975\",0,755]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c23",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"70a4406a9589fee162244975\",0,755]]",
   "citation_occurrence": 3,
   "label": "supported"
  },
  {
   "claim_id": "c24",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"70a4406a9589fee162244975\",0,755]]",
   "citation_occurrence": 3,
   "label": "supported"
  },
  {
   "claim_id": "c25",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"70a4406a9589fee162244975\",0,755]]",
   "citation_occurrence": 3,
   "label": "supported"
  },
  {
   "claim_id": "c26",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"c6eecc31b62bec62610b32c8\",0,807]]",
   "citation_occurrence": 3,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "引用缺最外层闭括号但来源五元组清楚，原样保留。TopView 引用只到验证标题，不支持细节；LargeView 交叉复核和联合错误分类计数均由相应正文支持。"
}
```

### citation-0617 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0617",
 "citation_pairs": [
  {
   "claim_id": "c8",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"2de3e4a6dc03eea749343095\",0,1097]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c10",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"2de3e4a6dc03eea749343095\",0,1097]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c11",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"9195a30407a58f577aca83e3\",0,958]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c9",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"4550509d06d80381b48a54e7\",157,1621]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"4550509d06d80381b48a54e7\",157,1621]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"4550509d06d80381b48a54e7\",157,1621]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"4550509d06d80381b48a54e7\",157,1621]]]",
   "citation_occurrence": 2,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "距离分布、反应行程解释、持续接近定义和低速暴露时间事件统计均在所引片段明确给出；开头与结尾无引句不另补配对。"
}
```

### citation-0618 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0618",
 "citation_pairs": [
  {
   "claim_id": "c12",
   "source_id": "B1-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b223ac81f0e4ae6d8611bda1\",0,1109]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B1-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b223ac81f0e4ae6d8611bda1\",0,1109]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"555c529a65a6b7bcf3c9fefe\",0,1010]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B2-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"555c529a65a6b7bcf3c9fefe\",0,1010]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B2-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"555c529a65a6b7bcf3c9fefe\",0,1010]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b12af7f12e130d78a603e476\",0,783]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c16",
   "source_id": "B5-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b12af7f12e130d78a603e476\",0,783]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c17",
   "source_id": "B5-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b12af7f12e130d78a603e476\",0,783]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "B6-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"33a4a6922243166a7290140b\",0,1415]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B6-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"33a4a6922243166a7290140b\",0,1415]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c20",
   "source_id": "B6-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"33a4a6922243166a7290140b\",0,1415]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c21",
   "source_id": "B2-F2",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"79288edd58cdf045fc8dd5fe\",0,460]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c22",
   "source_id": "B5-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b12af7f12e130d78a603e476\",0,783]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c23",
   "source_id": "B5-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b12af7f12e130d78a603e476\",0,783]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c24",
   "source_id": "B4-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"02b7c706f975111d06fbc121\",0,435]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c25",
   "source_id": "B4-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"02b7c706f975111d06fbc121\",0,435]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "单个五元组引用可唯一映射，原样保留。首项、推力方向与密度区域获得支持；转弯观察、最佳宽度和空间几何解释各误引到相邻其他片段，未支持。"
}
```

### citation-0619 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0619",
 "citation_pairs": [
  {
   "claim_id": "c19",
   "source_id": "B4-F6",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"18e20f3ac1f3458b6f75fc73\",0,26]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "Twarogowska et al. (2014)",
   "citation_text": "Twarogowska et al. (2014)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c24",
   "source_id": "B2-F9",
   "citation_text": "[Source [[\"pearl-src-6d44c24ebbf9c0d0\",\"6d44c24ebbf9c0d01d6b86ade86099750615ec15a9725674ad8f05c9a401849e\",\"df07c7d0e305493dabb4cc26\",0,1123]]]",
   "citation_occurrence": 1,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "实际引用所在句逐项核对：Twarogowska 归属误引通讯作者片段，作者年份标识未注册；内在问题而非数值处理的结论有正文直接支持。其余无引句不补配对。"
}
```

### citation-0620 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0620",
 "citation_pairs": [
  {
   "claim_id": "c7",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"beb5adcbd80166590fc6006f\",0,32]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c8",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"72cd110d07bae382e63e9cff\",0,1173]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c9",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"72cd110d07bae382e63e9cff\",0,1173]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c7",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"beb5adcbd80166590fc6006f\",0,32]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"beb5adcbd80166590fc6006f\",0,32]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "逐处提取句末引用；B1-F1仅含网址，不能支持外推判断；B2-F1明确包含理想密度阈值及现实排列和行为限制。"
}
```

### citation-0621 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0621",
 "citation_pairs": [
  {
   "claim_id": "c4",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-551c6f4b4febcc8a\",\"551c6f4b4febcc8a5cf03b32f6563c2526a802844983bceb6f526f132e6b970a\",\"1a475d000649a9f8b22b331b\",0,23]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c5",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-551c6f4b4febcc8a\",\"551c6f4b4febcc8a5cf03b32f6563c2526a802844983bceb6f526f132e6b970a\",\"1a475d000649a9f8b22b331b\",0,23]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "引用对应3.2实验设置标题，未给出表2收集信息或老年年龄范围。"
}
```

### citation-0622 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0622",
 "citation_pairs": [
  {
   "claim_id": "c10",
   "source_id": "B1-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b223ac81f0e4ae6d8611bda1\",0,1109]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c11",
   "source_id": "B1-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b223ac81f0e4ae6d8611bda1\",0,1109]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B2-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"555c529a65a6b7bcf3c9fefe\",0,1010]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B2-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"555c529a65a6b7bcf3c9fefe\",0,1010]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c11",
   "source_id": "B2-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"555c529a65a6b7bcf3c9fefe\",0,1010]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B5-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b12af7f12e130d78a603e476\",0,783]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B5-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b12af7f12e130d78a603e476\",0,783]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B5-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b12af7f12e130d78a603e476\",0,783]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b12af7f12e130d78a603e476\",0,783]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c16",
   "source_id": "B4-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"02b7c706f975111d06fbc121\",0,435]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c17",
   "source_id": "B6-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"33a4a6922243166a7290140b\",0,1415]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "B6-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"33a4a6922243166a7290140b\",0,1415]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B6-F1",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"33a4a6922243166a7290140b\",0,1415]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c20",
   "source_id": "B2-F2",
   "citation_text": "[Source [\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"79288edd58cdf045fc8dd5fe\",0,460]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "逐句识别单五元组引用；只用所指片段，B2-F1未含转角密度及拉链效应结论，B4-F1未含对角线机制，B2-F2未含最优宽度。"
}
```

### citation-0623 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0623",
 "citation_pairs": [
  {
   "claim_id": "c13",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",175,1229]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",175,1229]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",175,1229]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"a3c8cbc55fc477962d564ef6\",435,939]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c20",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"a3c8cbc55fc477962d564ef6\",435,939]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c21",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"a3c8cbc55fc477962d564ef6\",435,939]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"1eeb217dca0ae6833100610f\",65,363]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c22",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"1eeb217dca0ae6833100610f\",65,363]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "(Gidlöf et al., 2017)",
   "citation_text": "(Gidlöf et al., 2017)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c15",
   "source_id": "(Gidlöf et al., 2017)",
   "citation_text": "(Gidlöf et al., 2017)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c16",
   "source_id": "(Gidlöf et al., 2017)",
   "citation_text": "(Gidlöf et al., 2017)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c14",
   "source_id": "(Milosavljevic et al., 2012)",
   "citation_text": "(Milosavljevic et al., 2012)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c15",
   "source_id": "(Milosavljevic et al., 2012)",
   "citation_text": "(Milosavljevic et al., 2012)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c16",
   "source_id": "(Milosavljevic et al., 2012)",
   "citation_text": "(Milosavljevic et al., 2012)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c17",
   "source_id": "(Milosavljevic et al., 2012)",
   "citation_text": "(Milosavljevic et al., 2012)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c13",
   "source_id": "(Kremer et al., 2021)",
   "citation_text": "(Kremer et al., 2021)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c19",
   "source_id": "(Kremer et al., 2021)",
   "citation_text": "(Kremer et al., 2021)",
   "citation_occurrence": 1,
   "label": "invalid"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "逐处识别来源五元组及作者年份引用。B4-F1和B2-F1支持所附句子，B6-F1并非代理指标联合预测段；作者年份身份未在来源映射登记。"
}
```

### citation-0624 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0624",
 "citation_pairs": [
  {
   "claim_id": "c9",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"245ebda8d5f74f0e8ba79f22\",0,1458]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c9",
   "source_id": "B2-F1",
   "citation_text": "Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"148794e1e981235ac7ef8a20\",750,1994]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c10",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"ff9543f9b3ed91ec21dd958e\",0,813]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c11",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"ff9543f9b3ed91ec21dd958e\",0,813]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"ff9543f9b3ed91ec21dd958e\",0,813]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"ff9543f9b3ed91ec21dd958e\",0,813]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"ff9543f9b3ed91ec21dd958e\",0,813]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "保留缺少最外闭括号的五元组原文及同处两引用。B1-F1支持漏斗密度形状，未含普通瓶颈拱形或8m−2比较；无引用句不补配。"
}
```

### citation-0625 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0625",
 "citation_pairs": [
  {
   "claim_id": "c21",
   "source_id": "pearl-src-e741c6bfedd59a19",
   "citation_text": "[pearl-src-e741c6bfedd59a19]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c22",
   "source_id": "pearl-src-4b758ccb41af532c",
   "citation_text": "[pearl-src-4b758ccb41af532c]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c23",
   "source_id": "pearl-src-4b758ccb41af532c",
   "citation_text": "[pearl-src-4b758ccb41af532c]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c24",
   "source_id": "pearl-src-4b758ccb41af532c",
   "citation_text": "[pearl-src-4b758ccb41af532c]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c25",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c26",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 2,
   "label": "unknown"
  },
  {
   "claim_id": "c27",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 2,
   "label": "unknown"
  },
  {
   "claim_id": "c28",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 3,
   "label": "unknown"
  },
  {
   "claim_id": "c29",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 3,
   "label": "unknown"
  },
  {
   "claim_id": "c30",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 4,
   "label": "unknown"
  },
  {
   "claim_id": "c31",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 5,
   "label": "unknown"
  },
  {
   "claim_id": "c32",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 5,
   "label": "unknown"
  },
  {
   "claim_id": "c33",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 6,
   "label": "unknown"
  },
  {
   "claim_id": "c34",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 7,
   "label": "unknown"
  },
  {
   "claim_id": "c35",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 7,
   "label": "unknown"
  },
  {
   "claim_id": "c21",
   "source_id": "Geoerg et al. (2019, 2021)",
   "citation_text": "Geoerg et al. (2019, 2021)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c22",
   "source_id": "Geoerg et al. (2019)",
   "citation_text": "Geoerg et al. (2019)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c23",
   "source_id": "Geoerg et al. (2019)",
   "citation_text": "Geoerg et al. (2019)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c24",
   "source_id": "Geoerg et al. (2019)",
   "citation_text": "Geoerg et al. (2019)",
   "citation_occurrence": 1,
   "label": "invalid"
  }
 ],
 "citation_extraction_unknown": true,
 "reason": "各文档级标识对应多个片段，无法唯一映射，不选择有利片段；作者年份身份未登记。"
}
```

### citation-0626 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0626",
 "citation_pairs": [
  {
   "claim_id": "c18",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"a464c5a6a43f7361b26e647a\",0,31]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c18",
   "source_id": "B8-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"0b5eb230d93c6f77663f5432\",0,10]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B8-F1",
   "citation_text": "[Source [[\"pearl-src-53eaa084325fad7e\",\"53eaa084325fad7ec3c854c65df3b9b1fe3cb8fbbd8c21502a5dd1fd7bafd605\",\"0b5eb230d93c6f77663f5432\",0,10]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c21",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c22",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c23",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c21",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101]]]",
   "citation_occurrence": 3,
   "label": "supported"
  },
  {
   "claim_id": "c22",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101]]]",
   "citation_occurrence": 3,
   "label": "supported"
  },
  {
   "claim_id": "c24",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"6d1d395ae9141ece743341d1\",0,1101]]]",
   "citation_occurrence": 3,
   "label": "supported"
  },
  {
   "claim_id": "c25",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",0,1062]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c26",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"3abee6e1241cb51a39afef17\",0,1062]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c27",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"e3defec748963c46816d0b74\",0,536]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c28",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"e3defec748963c46816d0b74\",0,536]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c29",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-5bd280c855f70cd4\",\"5bd280c855f70cd4209a52cbcf71cc58d444168787c85699086c70064db33383\",\"e3defec748963c46816d0b74\",0,536]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "Helbing and Molnár (1995)",
   "citation_text": "Helbing and Molnár (1995)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c23",
   "source_id": "Kremer et al. (2021)",
   "citation_text": "Kremer et al. (2021)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c24",
   "source_id": "(including Kwak et al., 2013, and Zhou et al., 2022)",
   "citation_text": "(including Kwak et al., 2013, and Zhou et al., 2022)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c21",
   "source_id": "Li's (2023)",
   "citation_text": "Li's (2023)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c27",
   "source_id": "(Wang, 2014)",
   "citation_text": "(Wang, 2014)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c28",
   "source_id": "(Wang, 2014)",
   "citation_text": "(Wang, 2014)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c29",
   "source_id": "(Wang, 2014)",
   "citation_text": "(Wang, 2014)",
   "citation_occurrence": 1,
   "label": "invalid"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "逐句提取实际引用；两个标题片段无法支持模型描述，其余明确片段支持相应句子；作者年份引用身份未登记。"
}
```

### citation-0627 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0627",
 "citation_pairs": [
  {
   "claim_id": "c11",
   "source_id": "B9-F1",
   "citation_text": "[Source [[\"pearl-src-6953122155fbbf77\",\"6953122155fbbf77670d7fc408c781872ff59a274fc38ed045ad5496bde2c213\",\"e6f609920d07ff38bb509cc5\",0,580]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-aa99c4690a1ccb24\",\"aa99c4690a1ccb2444aaaf4106f650ad805c8bf3a0f6520268bc420b3efc21f7\",\"56f31a9a7102cb0f9b47ffeb\",851,1628]]]",
   "citation_occurrence": 1,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "两处五元组引用分别明确支持水中出口间距增大及无残疾参与者更靠近残疾邻居；未将后续无引用重复句补配。"
}
```

### citation-0628 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0628",
 "citation_pairs": [
  {
   "claim_id": "c6",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c6",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c6",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c6",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c7",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c7",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c7",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c7",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c8",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c8",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c8",
   "source_id": "B3-F3",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c8",
   "source_id": "B3-F4",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B3-F3",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c9",
   "source_id": "B3-F4",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B3-F3",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c10",
   "source_id": "B3-F4",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c11",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c11",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c11",
   "source_id": "B3-F3",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c11",
   "source_id": "B3-F4",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B3-F3",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B3-F4",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B3-F3",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B3-F4",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"7e21ad8bf1b263da6d923ec7\",0,190],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"6edcedce9203de31b4cac848\",0,251],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"f8049f08412ff6c1b70f8d76\",0,987],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"df2e0a9f8f6320942047af4c\",0,588],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"24d400be75e19a7a2576da61\",0,913],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"283ad7c7af55393e4a4a6c8f\",0,14],[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"3964576ce0dcf9ef56bb2127\",0,161]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "每处多片段引用逐片段判断；结论与验证限制只由B1-F2支持，等待区和参数条件只由B3-F3支持。"
}
```

### citation-0629 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0629",
 "citation_pairs": [
  {
   "claim_id": "c17",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",2092,2950]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",2092,2950]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B8-F1",
   "citation_text": "[Source [[\"pearl-src-630cddfaf9b1cb6d\",\"630cddfaf9b1cb6d03e7e33476d4f372eb5d028747d0898da2f177e61666367e\",\"c805295a0f08dd4df7340702\",0,8]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c20",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-551c6f4b4febcc8a\",\"551c6f4b4febcc8a5cf03b32f6563c2526a802844983bceb6f526f132e6b970a\",\"9595ba7a648dd596515c9b61\",0,1021]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c21",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-551c6f4b4febcc8a\",\"551c6f4b4febcc8a5cf03b32f6563c2526a802844983bceb6f526f132e6b970a\",\"9595ba7a648dd596515c9b61\",0,1021]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c22",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-551c6f4b4febcc8a\",\"551c6f4b4febcc8a5cf03b32f6563c2526a802844983bceb6f526f132e6b970a\",\"32b01cff047fe6941c33fafc\",0,1005]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c23",
   "source_id": "B7-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e17a8cefe9cde2f68f840cfe\",0,838]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "可唯一识别缺外层闭括号的五元组。B8-F1为摘要标题，B6-F1未含实验地点时间，B7-F1为另一模型验证段，不借相邻片段支持。"
}
```

### citation-0630 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0630",
 "citation_pairs": [
  {
   "claim_id": "c5",
   "source_id": "B1-F12",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"bd5ee640bc3e0a69c62a65f3\",0,870]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c5",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5de8c1d77eb314d61e14862d\",231,632]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c5",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c6",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5de8c1d77eb314d61e14862d\",231,632]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c7",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5de8c1d77eb314d61e14862d\",231,632]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c8",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-49fbc8413e27f3f1\",\"49fbc8413e27f3f18b1d42203bc7b0f5c6f93bd8b33108dccadd3bdbe9b840ad\",\"5a0e95ab82bc42aa17db3096\",0,14]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "各独立引用逐处判断；摘要正文支持不可复现现象，B4-F1为前序研究段，B5-F1仅结论标题，不能借同块正文支持。"
}
```

### citation-0631 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0631",
 "citation_pairs": [
  {
   "claim_id": "c10",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"62678a5dcfc1a3aa7eeb2553\",0,8],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"148794e1e981235ac7ef8a20\",0,1994]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"62678a5dcfc1a3aa7eeb2553\",0,8],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"148794e1e981235ac7ef8a20\",0,1994]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c10",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"d00e5600ed0d65c445a00f90\",0,13],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"65358017dce22b541f1d2e34\",0,453],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"245ebda8d5f74f0e8ba79f22\",0,1302]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"d00e5600ed0d65c445a00f90\",0,13],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"65358017dce22b541f1d2e34\",0,453],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"245ebda8d5f74f0e8ba79f22\",0,1302]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"d00e5600ed0d65c445a00f90\",0,13],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"65358017dce22b541f1d2e34\",0,453],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"245ebda8d5f74f0e8ba79f22\",0,1302]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c10",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"0afd8be4dd401d09461928f3\",221,856],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"9cc1bf39f62014c2b58f771f\",0,738]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c10",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"0afd8be4dd401d09461928f3\",221,856],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"9cc1bf39f62014c2b58f771f\",0,738]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c11",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"cb96f0b121ec83971a7e2c8f\",499,866],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"f97796feafeeaa3651ad35b5\",0,358],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"5ecffcbdfb469d122a9b2144\",0,316],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"5ec3755c8f66f50b7745ec54\",0,209]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c11",
   "source_id": "B6-F2",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"cb96f0b121ec83971a7e2c8f\",499,866],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"f97796feafeeaa3651ad35b5\",0,358],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"5ecffcbdfb469d122a9b2144\",0,316],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"5ec3755c8f66f50b7745ec54\",0,209]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c11",
   "source_id": "B6-F3",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"cb96f0b121ec83971a7e2c8f\",499,866],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"f97796feafeeaa3651ad35b5\",0,358],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"5ecffcbdfb469d122a9b2144\",0,316],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"5ec3755c8f66f50b7745ec54\",0,209]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c11",
   "source_id": "B6-F4",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"cb96f0b121ec83971a7e2c8f\",499,866],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"f97796feafeeaa3651ad35b5\",0,358],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"5ecffcbdfb469d122a9b2144\",0,316],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"5ec3755c8f66f50b7745ec54\",0,209]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"0afd8be4dd401d09461928f3\",221,856],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"9cc1bf39f62014c2b58f771f\",0,738]]]",
   "citation_occurrence": 2,
   "label": "partial"
  },
  {
   "claim_id": "c12",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"0afd8be4dd401d09461928f3\",221,856],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"9cc1bf39f62014c2b58f771f\",0,738]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"0afd8be4dd401d09461928f3\",221,856],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"9cc1bf39f62014c2b58f771f\",0,738]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"0afd8be4dd401d09461928f3\",221,856],[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"9cc1bf39f62014c2b58f771f\",0,738]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "多片段逐一判断，B3-F1漏斗公式开头被截去，仅支持部分参数而未给出所写系数；后续无引用推导不补配。"
}
```

### citation-0632 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0632",
 "citation_pairs": [
  {
   "claim_id": "c12",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c12",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c18",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c18",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c18",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c18",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B2-F3",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"f739a2c3f1e00b41110a485c\",0,112],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"a90fa68cef986ed756f4e438\",0,275],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"3572fb0f8844e300465200e2\",0,999],[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c16",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"360c46ada115e03135693050\",564,1067],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"89eaa885e3f25fd0e750a87b\",997,1544],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"19c35c7ceca05779ade6c05e\",0,839]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c16",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"360c46ada115e03135693050\",564,1067],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"89eaa885e3f25fd0e750a87b\",997,1544],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"19c35c7ceca05779ade6c05e\",0,839]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B6-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"360c46ada115e03135693050\",564,1067],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"89eaa885e3f25fd0e750a87b\",997,1544],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"19c35c7ceca05779ade6c05e\",0,839]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c17",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"360c46ada115e03135693050\",564,1067],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"89eaa885e3f25fd0e750a87b\",997,1544],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"19c35c7ceca05779ade6c05e\",0,839]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c17",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"360c46ada115e03135693050\",564,1067],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"89eaa885e3f25fd0e750a87b\",997,1544],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"19c35c7ceca05779ade6c05e\",0,839]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c17",
   "source_id": "B6-F2",
   "citation_text": "[Source [[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"360c46ada115e03135693050\",564,1067],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"89eaa885e3f25fd0e750a87b\",997,1544],[\"pearl-src-4c32a7203b84fd3e\",\"4c32a7203b84fd3ef46b8dd10b0cfa95c3bdb0c8d98669fd2b173956e066d580\",\"19c35c7ceca05779ade6c05e\",0,839]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-579f028f9623b157\",\"579f028f9623b157259a61bc65ca54b9f9be940358f716d33f2b7efc8237fbab\",\"b087e81165d9d08b992d5aea\",718,2672]]]",
   "citation_occurrence": 1,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "保留完整及缺外层括号引用原文，多来源逐片段判断；Lyon细节在B2-F3、缺背景在B5-F1、目标在B6-F2，站点轨迹在B3-F1。"
}
```

### citation-0633 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0633",
 "citation_pairs": [
  {
   "claim_id": "c5",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"245ebda8d5f74f0e8ba79f22\",0,1458]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c6",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"2c47dc702410eed0254bebeb\",0,638]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c7",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"2c47dc702410eed0254bebeb\",0,638]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c8",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"245ebda8d5f74f0e8ba79f22\",0,1458]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c9",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-41c7d913c29687f3\",\"41c7d913c29687f3adf4c5661fb098490c8fea559da951df72eb9d5e3646d45e\",\"245ebda8d5f74f0e8ba79f22\",0,1458]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c5",
   "source_id": "Li et al. (2023)",
   "citation_text": "Li et al. (2023)",
   "citation_occurrence": 1,
   "label": "invalid"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "B3-F1支持阈值及密度速度比较，B2-F1仅录像轨迹提取未含角度宽度；作者年份身份未登记。"
}
```

### citation-0634 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0634",
 "citation_pairs": [
  {
   "claim_id": "c14",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fcbf767ff8ca82d52425f730\",0,480]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fcbf767ff8ca82d52425f730\",0,480]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fcbf767ff8ca82d52425f730\",0,480]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B4-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fcbf767ff8ca82d52425f730\",0,480]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e17a8cefe9cde2f68f840cfe\",0,838],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a4fed008b37079c326ee9862\",0,30],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"2f478cdca8a779a2081cb202\",0,157],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"d9d76dd84dc9e2bcf642e71d\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bb4194ce8fc2ac988a47eb15\",0,273],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4f89ea59edd7cc9747c1cd31\",0,63],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fc2a4a111c610fc01e3c3c37\",0,66],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"9aec9c3dde2db6a65544ac58\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"8965dfe783022e9fe43ba4c1\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"06a4a08e6cd7f23bd19107da\",0,224]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e17a8cefe9cde2f68f840cfe\",0,838],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a4fed008b37079c326ee9862\",0,30],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"2f478cdca8a779a2081cb202\",0,157],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"d9d76dd84dc9e2bcf642e71d\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bb4194ce8fc2ac988a47eb15\",0,273],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4f89ea59edd7cc9747c1cd31\",0,63],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fc2a4a111c610fc01e3c3c37\",0,66],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"9aec9c3dde2db6a65544ac58\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"8965dfe783022e9fe43ba4c1\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"06a4a08e6cd7f23bd19107da\",0,224]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e17a8cefe9cde2f68f840cfe\",0,838],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a4fed008b37079c326ee9862\",0,30],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"2f478cdca8a779a2081cb202\",0,157],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"d9d76dd84dc9e2bcf642e71d\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bb4194ce8fc2ac988a47eb15\",0,273],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4f89ea59edd7cc9747c1cd31\",0,63],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fc2a4a111c610fc01e3c3c37\",0,66],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"9aec9c3dde2db6a65544ac58\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"8965dfe783022e9fe43ba4c1\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"06a4a08e6cd7f23bd19107da\",0,224]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F4",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e17a8cefe9cde2f68f840cfe\",0,838],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a4fed008b37079c326ee9862\",0,30],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"2f478cdca8a779a2081cb202\",0,157],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"d9d76dd84dc9e2bcf642e71d\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bb4194ce8fc2ac988a47eb15\",0,273],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4f89ea59edd7cc9747c1cd31\",0,63],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fc2a4a111c610fc01e3c3c37\",0,66],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"9aec9c3dde2db6a65544ac58\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"8965dfe783022e9fe43ba4c1\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"06a4a08e6cd7f23bd19107da\",0,224]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F5",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e17a8cefe9cde2f68f840cfe\",0,838],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a4fed008b37079c326ee9862\",0,30],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"2f478cdca8a779a2081cb202\",0,157],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"d9d76dd84dc9e2bcf642e71d\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bb4194ce8fc2ac988a47eb15\",0,273],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4f89ea59edd7cc9747c1cd31\",0,63],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fc2a4a111c610fc01e3c3c37\",0,66],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"9aec9c3dde2db6a65544ac58\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"8965dfe783022e9fe43ba4c1\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"06a4a08e6cd7f23bd19107da\",0,224]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F6",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e17a8cefe9cde2f68f840cfe\",0,838],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a4fed008b37079c326ee9862\",0,30],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"2f478cdca8a779a2081cb202\",0,157],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"d9d76dd84dc9e2bcf642e71d\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bb4194ce8fc2ac988a47eb15\",0,273],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4f89ea59edd7cc9747c1cd31\",0,63],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fc2a4a111c610fc01e3c3c37\",0,66],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"9aec9c3dde2db6a65544ac58\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"8965dfe783022e9fe43ba4c1\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"06a4a08e6cd7f23bd19107da\",0,224]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F7",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e17a8cefe9cde2f68f840cfe\",0,838],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a4fed008b37079c326ee9862\",0,30],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"2f478cdca8a779a2081cb202\",0,157],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"d9d76dd84dc9e2bcf642e71d\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bb4194ce8fc2ac988a47eb15\",0,273],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4f89ea59edd7cc9747c1cd31\",0,63],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fc2a4a111c610fc01e3c3c37\",0,66],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"9aec9c3dde2db6a65544ac58\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"8965dfe783022e9fe43ba4c1\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"06a4a08e6cd7f23bd19107da\",0,224]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F8",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e17a8cefe9cde2f68f840cfe\",0,838],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a4fed008b37079c326ee9862\",0,30],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"2f478cdca8a779a2081cb202\",0,157],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"d9d76dd84dc9e2bcf642e71d\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bb4194ce8fc2ac988a47eb15\",0,273],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4f89ea59edd7cc9747c1cd31\",0,63],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fc2a4a111c610fc01e3c3c37\",0,66],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"9aec9c3dde2db6a65544ac58\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"8965dfe783022e9fe43ba4c1\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"06a4a08e6cd7f23bd19107da\",0,224]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F9",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e17a8cefe9cde2f68f840cfe\",0,838],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a4fed008b37079c326ee9862\",0,30],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"2f478cdca8a779a2081cb202\",0,157],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"d9d76dd84dc9e2bcf642e71d\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bb4194ce8fc2ac988a47eb15\",0,273],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4f89ea59edd7cc9747c1cd31\",0,63],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fc2a4a111c610fc01e3c3c37\",0,66],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"9aec9c3dde2db6a65544ac58\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"8965dfe783022e9fe43ba4c1\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"06a4a08e6cd7f23bd19107da\",0,224]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B5-F10",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e17a8cefe9cde2f68f840cfe\",0,838],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a4fed008b37079c326ee9862\",0,30],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"2f478cdca8a779a2081cb202\",0,157],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"d9d76dd84dc9e2bcf642e71d\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bb4194ce8fc2ac988a47eb15\",0,273],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4f89ea59edd7cc9747c1cd31\",0,63],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fc2a4a111c610fc01e3c3c37\",0,66],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"9aec9c3dde2db6a65544ac58\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"8965dfe783022e9fe43ba4c1\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"06a4a08e6cd7f23bd19107da\",0,224]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c16",
   "source_id": "pearl-src-4d5e06c459e428ae",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c16",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B1-F5",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c17",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c17",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c17",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c17",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c17",
   "source_id": "B1-F5",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c17",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c17",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"b927ba7f621880c71b33cfd0\",0,1223],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"bce38f09e6205a4c17c75fce\",0,414]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c18",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c18",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c18",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c18",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c18",
   "source_id": "B1-F5",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B3-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B1-F5",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"894f1843dce8ee3f1f2098f5\",0,1468],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"33e65f05b981d4cff0ccce99\",0,100],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c20",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c20",
   "source_id": "B6-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c20",
   "source_id": "B6-F3",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c20",
   "source_id": "B6-F4",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c20",
   "source_id": "B6-F5",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c21",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c21",
   "source_id": "B6-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c21",
   "source_id": "B6-F3",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c21",
   "source_id": "B6-F4",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c21",
   "source_id": "B6-F5",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c22",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c22",
   "source_id": "B6-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c22",
   "source_id": "B6-F3",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c22",
   "source_id": "B6-F4",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c22",
   "source_id": "B6-F5",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0aaa2de078a28b94974fda6\",0,39],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"c0c37544c4fe4faa9844b01f\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"a16a438a7c92b7c35cdc7caf\",0,398],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"7f15fa66e6beb4824972b5a2\",0,2],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e8b7194a8193fe74c1feaff6\",0,2]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c23",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c23",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c23",
   "source_id": "B1-F3",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c23",
   "source_id": "B1-F4",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c23",
   "source_id": "B1-F5",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"12b224540c90a6159999f0cc\",0,909],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"44c7d3279a8f84306b344690\",0,511],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"e7785860dc869125687ef667\",0,17],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"914c13cd1da7746abc31fc79\",0,130],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"54ae31b40272bdd53d206895\",0,50]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c24",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fcbf767ff8ca82d52425f730\",0,480]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c24",
   "source_id": "B4-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fcbf767ff8ca82d52425f730\",0,480]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c25",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fcbf767ff8ca82d52425f730\",0,480]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c25",
   "source_id": "B4-F2",
   "citation_text": "[Source [[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"567d3905eea51a59803ab894\",0,642],[\"pearl-src-4d5e06c459e428ae\",\"4d5e06c459e428aeec66b400fd8fc7aa816bf317457a72c0affbbd4a24be632b\",\"fcbf767ff8ca82d52425f730\",0,480]]]",
   "citation_occurrence": 1,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": true,
 "reason": "多片段独立判断。第三处含重复哈希的六项元组，映射规则未覆盖，保留unknown；其他元组映射清晰，按对应正文标题数值片段分开判断。"
}
```

### citation-0635 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0635",
 "citation_pairs": [
  {
   "claim_id": "c9",
   "source_id": "pearl-src-551c6f4b4febcc8a",
   "citation_text": "[pearl-src-551c6f4b4febcc8a]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c10",
   "source_id": "pearl-src-551c6f4b4febcc8a",
   "citation_text": "[pearl-src-551c6f4b4febcc8a]",
   "citation_occurrence": 2,
   "label": "unknown"
  },
  {
   "claim_id": "c12",
   "source_id": "pearl-src-551c6f4b4febcc8a",
   "citation_text": "[pearl-src-551c6f4b4febcc8a]",
   "citation_occurrence": 2,
   "label": "unknown"
  },
  {
   "claim_id": "c13",
   "source_id": "pearl-src-40f1751dc557a762",
   "citation_text": "[pearl-src-40f1751dc557a762]",
   "citation_occurrence": 1,
   "label": "unknown"
  }
 ],
 "citation_extraction_unknown": true,
 "reason": "文档标识均对应多个片段，不能唯一定位；无引用列表条目不补配。"
}
```

### citation-0636 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0636",
 "citation_pairs": [
  {
   "claim_id": "c10",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"2de3e4a6dc03eea749343095\",598,1097]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c11",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"2de3e4a6dc03eea749343095\",598,1097]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c12",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"9195a30407a58f577aca83e3\",0,958]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c10",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"4550509d06d80381b48a54e7\",774,1621]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"4550509d06d80381b48a54e7\",774,1621]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"23f896eb3538e1f6e8515d53\",1060,1380]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c13",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"4550509d06d80381b48a54e7\",774,1621]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"23f896eb3538e1f6e8515d53\",1060,1380]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"23f896eb3538e1f6e8515d53\",1060,1380]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c16",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-0e8d201180bcd044\",\"0e8d201180bcd044a9329cc9adf1c8255d12719d3ce56ce5fd5aefb0cfc65f5a\",\"23f896eb3538e1f6e8515d53\",1060,1380]]]",
   "citation_occurrence": 3,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "按句末位置及重复次数提取；B2-F1为慢速停顿段，不能支持曝光时间高值或定义；其他所指片段分别直接支持。"
}
```

### citation-0637 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0637",
 "citation_pairs": [
  {
   "claim_id": "c7",
   "source_id": "B3-F1",
   "citation_text": "[Source: pearl-src-6953122155fbbf77, 2671477219ef702e28857fd4; pearl-src-6953122155fbbf77, 1fa9cee563e29c50124d1cc7; pearl-src-6953122155fbbf77, 0c29cb6c068cf53e4ea835bb]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c8",
   "source_id": "B3-F1",
   "citation_text": "[Source: pearl-src-6953122155fbbf77, 2671477219ef702e28857fd4; pearl-src-6953122155fbbf77, 1fa9cee563e29c50124d1cc7; pearl-src-6953122155fbbf77, 0c29cb6c068cf53e4ea835bb]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c7",
   "source_id": "B5-F1",
   "citation_text": "[Source: pearl-src-6953122155fbbf77, 2671477219ef702e28857fd4; pearl-src-6953122155fbbf77, 1fa9cee563e29c50124d1cc7; pearl-src-6953122155fbbf77, 0c29cb6c068cf53e4ea835bb]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c8",
   "source_id": "B5-F1",
   "citation_text": "[Source: pearl-src-6953122155fbbf77, 2671477219ef702e28857fd4; pearl-src-6953122155fbbf77, 1fa9cee563e29c50124d1cc7; pearl-src-6953122155fbbf77, 0c29cb6c068cf53e4ea835bb]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c7",
   "source_id": "B6-F1",
   "citation_text": "[Source: pearl-src-6953122155fbbf77, 2671477219ef702e28857fd4; pearl-src-6953122155fbbf77, 1fa9cee563e29c50124d1cc7; pearl-src-6953122155fbbf77, 0c29cb6c068cf53e4ea835bb]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c8",
   "source_id": "B6-F1",
   "citation_text": "[Source: pearl-src-6953122155fbbf77, 2671477219ef702e28857fd4; pearl-src-6953122155fbbf77, 1fa9cee563e29c50124d1cc7; pearl-src-6953122155fbbf77, 0c29cb6c068cf53e4ea835bb]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B3-F1",
   "citation_text": "[Source: pearl-src-6953122155fbbf77, 2671477219ef702e28857fd4; pearl-src-6953122155fbbf77, 0c29cb6c068cf53e4ea835bb]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B6-F1",
   "citation_text": "[Source: pearl-src-6953122155fbbf77, 2671477219ef702e28857fd4; pearl-src-6953122155fbbf77, 0c29cb6c068cf53e4ea835bb]",
   "citation_occurrence": 1,
   "label": "partial"
  },
  {
   "claim_id": "c10",
   "source_id": "B6-F1",
   "citation_text": "[Source: pearl-src-6953122155fbbf77, 0c29cb6c068cf53e4ea835bb]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c11",
   "source_id": "B6-F1",
   "citation_text": "[Source: pearl-src-6953122155fbbf77, 0c29cb6c068cf53e4ea835bb; pearl-src-6953122155fbbf77, 1fa9cee563e29c50124d1cc7]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c11",
   "source_id": "B5-F1",
   "citation_text": "[Source: pearl-src-6953122155fbbf77, 0c29cb6c068cf53e4ea835bb; pearl-src-6953122155fbbf77, 1fa9cee563e29c50124d1cc7]",
   "citation_occurrence": 1,
   "label": "partial"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "文档与元素标识可唯一定位各片段，分号多个来源逐一判断；阈值不在B3-F1或B6-F1，B6-F1支持速度密度阶段及时间阈值，B5-F1仅部分支持末句。"
}
```

### citation-0638 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0638",
 "citation_pairs": [
  {
   "claim_id": "c4",
   "source_id": "B1-F1",
   "citation_text": "[Source [\"pearl-src-72f5997118149dbe\",\"72f5997118149dbe1faeac6a1abdcce5a27c98212da14cf843005e76ae13306e\",\"e1dcb7ed5b13d7c6dd355e87\",0,557]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c5",
   "source_id": "B1-F1",
   "citation_text": "[Source [\"pearl-src-72f5997118149dbe\",\"72f5997118149dbe1faeac6a1abdcce5a27c98212da14cf843005e76ae13306e\",\"e1dcb7ed5b13d7c6dd355e87\",0,557]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c6",
   "source_id": "B1-F1",
   "citation_text": "[Source [\"pearl-src-72f5997118149dbe\",\"72f5997118149dbe1faeac6a1abdcce5a27c98212da14cf843005e76ae13306e\",\"e1dcb7ed5b13d7c6dd355e87\",0,557]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c7",
   "source_id": "B1-F1",
   "citation_text": "[Source [\"pearl-src-72f5997118149dbe\",\"72f5997118149dbe1faeac6a1abdcce5a27c98212da14cf843005e76ae13306e\",\"e1dcb7ed5b13d7c6dd355e87\",0,557]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c8",
   "source_id": "B1-F1",
   "citation_text": "[Source [\"pearl-src-72f5997118149dbe\",\"72f5997118149dbe1faeac6a1abdcce5a27c98212da14cf843005e76ae13306e\",\"e1dcb7ed5b13d7c6dd355e87\",0,557]]",
   "citation_occurrence": 2,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "单五元组明确映射B1-F1，其文字逐项给出N=6、Q=21及运行次数，按输入片段原文判断。"
}
```

### citation-0639 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0639",
 "citation_pairs": [
  {
   "claim_id": "c5",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-031a5779bd83192e\",\"031a5779bd83192e847846be4b73c4814d2a72d2abc05549caebf5c8c1440a81\",\"3281f0458f4f62601901b215\",0,8]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c6",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-031a5779bd83192e\",\"031a5779bd83192e847846be4b73c4814d2a72d2abc05549caebf5c8c1440a81\",\"3281f0458f4f62601901b215\",0,8]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c7",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-031a5779bd83192e\",\"031a5779bd83192e847846be4b73c4814d2a72d2abc05549caebf5c8c1440a81\",\"3281f0458f4f62601901b215\",0,8]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c8",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-031a5779bd83192e\",\"031a5779bd83192e847846be4b73c4814d2a72d2abc05549caebf5c8c1440a81\",\"3281f0458f4f62601901b215\",0,8]]]",
   "citation_occurrence": 2,
   "label": "unsupported"
  },
  {
   "claim_id": "c9",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-031a5779bd83192e\",\"031a5779bd83192e847846be4b73c4814d2a72d2abc05549caebf5c8c1440a81\",\"3281f0458f4f62601901b215\",0,8]]]",
   "citation_occurrence": 3,
   "label": "unsupported"
  },
  {
   "claim_id": "c10",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-031a5779bd83192e\",\"031a5779bd83192e847846be4b73c4814d2a72d2abc05549caebf5c8c1440a81\",\"3281f0458f4f62601901b215\",0,8]]]",
   "citation_occurrence": 3,
   "label": "unsupported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "三次引用均明确指向abstract标题，标题不支持年龄身高相关、方法或因素效应。"
}
```

### citation-0640 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0640",
 "citation_pairs": [
  {
   "claim_id": "c25",
   "source_id": "pearl-src-e741c6bfedd59a19",
   "citation_text": "[pearl-src-e741c6bfedd59a19]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c26",
   "source_id": "pearl-src-4b758ccb41af532c",
   "citation_text": "[pearl-src-4b758ccb41af532c]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c27",
   "source_id": "pearl-src-4b758ccb41af532c",
   "citation_text": "[pearl-src-4b758ccb41af532c]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c28",
   "source_id": "pearl-src-4b758ccb41af532c",
   "citation_text": "[pearl-src-4b758ccb41af532c]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c29",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 1,
   "label": "unknown"
  },
  {
   "claim_id": "c30",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 2,
   "label": "unknown"
  },
  {
   "claim_id": "c31",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 2,
   "label": "unknown"
  },
  {
   "claim_id": "c32",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 3,
   "label": "unknown"
  },
  {
   "claim_id": "c33",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 3,
   "label": "unknown"
  },
  {
   "claim_id": "c34",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 4,
   "label": "unknown"
  },
  {
   "claim_id": "c35",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 5,
   "label": "unknown"
  },
  {
   "claim_id": "c36",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 5,
   "label": "unknown"
  },
  {
   "claim_id": "c37",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 6,
   "label": "unknown"
  },
  {
   "claim_id": "c38",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 7,
   "label": "unknown"
  },
  {
   "claim_id": "c39",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 7,
   "label": "unknown"
  },
  {
   "claim_id": "c38",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 8,
   "label": "unknown"
  },
  {
   "claim_id": "c40",
   "source_id": "pearl-src-72f5997118149dbe",
   "citation_text": "[pearl-src-72f5997118149dbe]",
   "citation_occurrence": 8,
   "label": "unknown"
  },
  {
   "claim_id": "c25",
   "source_id": "Geoerg et al. (2019, 2021)",
   "citation_text": "Geoerg et al. (2019, 2021)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c26",
   "source_id": "Geoerg et al. (2019)",
   "citation_text": "Geoerg et al. (2019)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c27",
   "source_id": "Geoerg et al. (2019)",
   "citation_text": "Geoerg et al. (2019)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c28",
   "source_id": "Geoerg et al. (2019)",
   "citation_text": "Geoerg et al. (2019)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c35",
   "source_id": "(Kielar et al., 2014)",
   "citation_text": "(Kielar et al., 2014)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c36",
   "source_id": "(Kielar et al., 2014)",
   "citation_text": "(Kielar et al., 2014)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c35",
   "source_id": "(Antonini et al., 2006)",
   "citation_text": "(Antonini et al., 2006)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c36",
   "source_id": "(Antonini et al., 2006)",
   "citation_text": "(Antonini et al., 2006)",
   "citation_occurrence": 1,
   "label": "invalid"
  }
 ],
 "citation_extraction_unknown": true,
 "reason": "文档级引用均对应多个片段，保留无法唯一定位；实际作者年份引用身份未登记，不借上下文文献提及构造映射。"
}
```

### citation-0641 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0641",
 "citation_pairs": [
  {
   "claim_id": "c4",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-486515cd9939adcf\",\"486515cd9939adcf6303aa686b5eca3ee76e8223185db3f7dd31dd2c2d874cbc\",\"1b1538df54ccfca56c2ec4b3\",0,964]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c6",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-486515cd9939adcf\",\"486515cd9939adcf6303aa686b5eca3ee76e8223185db3f7dd31dd2c2d874cbc\",\"1b1538df54ccfca56c2ec4b3\",0,964]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c7",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-486515cd9939adcf\",\"486515cd9939adcf6303aa686b5eca3ee76e8223185db3f7dd31dd2c2d874cbc\",\"1b1538df54ccfca56c2ec4b3\",0,964]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c8",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-486515cd9939adcf\",\"486515cd9939adcf6303aa686b5eca3ee76e8223185db3f7dd31dd2c2d874cbc\",\"1b1538df54ccfca56c2ec4b3\",0,964]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c9",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-486515cd9939adcf\",\"486515cd9939adcf6303aa686b5eca3ee76e8223185db3f7dd31dd2c2d874cbc\",\"1b1538df54ccfca56c2ec4b3\",0,964]]]",
   "citation_occurrence": 2,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "两处引用明确定位B1-F2，分别支持分组比例及环境解释；无引用的c5不补配。"
}
```

### citation-0642 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0642",
 "citation_pairs": [
  {
   "claim_id": "c12",
   "source_id": "B7-F1",
   "citation_text": "[Source [[\"pearl-src-48101ba7d6ac7448\",\"48101ba7d6ac74483d5bce069abfc164da51554e7101d0aa71561aeba0dcd7b5\",\"e5cf7dc002243bf05ee0e2dc\",0,1063]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c13",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-9e1c873b60f8d08c\",\"9e1c873b60f8d08c4685316264588a67ad4dd47b508e87450fee61a30acac9d0\",\"0affdd8668cfdeeada77d2c8\",0,631]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B1-F2",
   "citation_text": "[Source [[\"pearl-src-9e1c873b60f8d08c\",\"9e1c873b60f8d08c4685316264588a67ad4dd47b508e87450fee61a30acac9d0\",\"0affdd8668cfdeeada77d2c8\",0,631]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B8-F1",
   "citation_text": "[Source [[\"pearl-src-9a4f2d471b96e89f\",\"9a4f2d471b96e89fb9c3121eae31cb515de4a0e926323cf0fb27c0dbafc5afc4\",\"c04989210184793478c543ce\",329,1400]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B9-F3",
   "citation_text": "[Source [[\"pearl-src-9e1c873b60f8d08c\",\"9e1c873b60f8d08c4685316264588a67ad4dd47b508e87450fee61a30acac9d0\",\"83a067779ad2c338d53a27f7\",0,112]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B9-F3",
   "citation_text": "[Source [[\"pearl-src-9e1c873b60f8d08c\",\"9e1c873b60f8d08c4685316264588a67ad4dd47b508e87450fee61a30acac9d0\",\"83a067779ad2c338d53a27f7\",0,112]]]",
   "citation_occurrence": 1,
   "label": "partial"
  },
  {
   "claim_id": "c10",
   "source_id": "(Haghani and Sarvi 2019b)",
   "citation_text": "(Haghani and Sarvi 2019b)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c11",
   "source_id": "(Haghani and Sarvi 2019b)",
   "citation_text": "(Haghani and Sarvi 2019b)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c13",
   "source_id": "Haghani and Sarvi (2016)",
   "citation_text": "Haghani and Sarvi (2016)",
   "citation_occurrence": 1,
   "label": "invalid"
  },
  {
   "claim_id": "c14",
   "source_id": "Haghani and Sarvi (2016)",
   "citation_text": "Haghani and Sarvi (2016)",
   "citation_occurrence": 1,
   "label": "invalid"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "按句界和句中引用范围提取；B9-F3仅续句的行为理解和校准障碍，缺少稀缺数据及几何条件；不为未附引用的开头句补配。"
}
```

### citation-0643 结构补字段

时间：2026-10-08T11:04:50.551181+00:00。字段：citation_pairs 中序号 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25] 的 reason。修改前：字段缺失。修改后：保留原有判定；本字段为结构性补全，未重新判断。原因：校验器要求 reason；保持全部配对、标签、引用、身份和次数不变。修改前完整文件备份：

```json
{
 "anchor_id": "citation-0643",
 "citation_pairs": [
  {
   "claim_id": "c13",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"555c529a65a6b7bcf3c9fefe\",0,1010]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"555c529a65a6b7bcf3c9fefe\",0,1010]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"5824203eed320289d70f94b1\",0,8],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b223ac81f0e4ae6d8611bda1\",0,1033]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c15",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"5824203eed320289d70f94b1\",0,8],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b223ac81f0e4ae6d8611bda1\",0,1033]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c16",
   "source_id": "B2-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"5824203eed320289d70f94b1\",0,8],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b223ac81f0e4ae6d8611bda1\",0,1033]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c14",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"5824203eed320289d70f94b1\",0,8],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b223ac81f0e4ae6d8611bda1\",0,1033]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c15",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"5824203eed320289d70f94b1\",0,8],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b223ac81f0e4ae6d8611bda1\",0,1033]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c16",
   "source_id": "B2-F2",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"5824203eed320289d70f94b1\",0,8],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"b223ac81f0e4ae6d8611bda1\",0,1033]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c17",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"c1864ca59cdb722fc7d4569b\",0,872]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"ee985c34ed2a1a9f216b5802\",880,1538],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"f81114822c52ce8b63326148\",0,238]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c19",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"ee985c34ed2a1a9f216b5802\",880,1538],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"f81114822c52ce8b63326148\",0,238]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c20",
   "source_id": "B6-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"ee985c34ed2a1a9f216b5802\",880,1538],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"f81114822c52ce8b63326148\",0,238]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c18",
   "source_id": "B6-F2",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"ee985c34ed2a1a9f216b5802\",880,1538],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"f81114822c52ce8b63326148\",0,238]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c19",
   "source_id": "B6-F2",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"ee985c34ed2a1a9f216b5802\",880,1538],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"f81114822c52ce8b63326148\",0,238]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c20",
   "source_id": "B6-F2",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"ee985c34ed2a1a9f216b5802\",880,1538],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"f81114822c52ce8b63326148\",0,238]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c21",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"64c71f3c28217e5351df121a\",0,943]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c22",
   "source_id": "B3-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"64c71f3c28217e5351df121a\",0,943]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c17",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"c1864ca59cdb722fc7d4569b\",0,872]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c24",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"c1864ca59cdb722fc7d4569b\",0,872]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c25",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"c1864ca59cdb722fc7d4569b\",0,872]]]",
   "citation_occurrence": 2,
   "label": "supported"
  },
  {
   "claim_id": "c23",
   "source_id": "B4-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"c1864ca59cdb722fc7d4569b\",0,872]]]",
   "citation_occurrence": 2,
   "label": "partial"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"1572405acdfd4a6cc3e905ff\",0,14],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"6c4239fb2d4e4c97d8db6739\",0,553],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"2d5be4fc24609032d185869a\",0,380]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F2",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"1572405acdfd4a6cc3e905ff\",0,14],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"6c4239fb2d4e4c97d8db6739\",0,553],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"2d5be4fc24609032d185869a\",0,380]]]",
   "citation_occurrence": 1,
   "label": "unsupported"
  },
  {
   "claim_id": "c26",
   "source_id": "B5-F3",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"1572405acdfd4a6cc3e905ff\",0,14],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"6c4239fb2d4e4c97d8db6739\",0,553],[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"2d5be4fc24609032d185869a\",0,380]]]",
   "citation_occurrence": 1,
   "label": "supported"
  },
  {
   "claim_id": "c27",
   "source_id": "B1-F1",
   "citation_text": "[Source [[\"pearl-src-2d794479f1d822ef\",\"2d794479f1d822efa0882446cc9abc25875dae1f2212017948c490cd7c17499c\",\"555c529a65a6b7bcf3c9fefe\",0,1010]]]",
   "citation_occurrence": 2,
   "label": "supported"
  }
 ],
 "citation_extraction_unknown": false,
 "reason": "按句界提取，未附引用开头因果不补配；多来源逐片段判断。B4-F1说明长通道和拥挤转移，但未完整证明高平均速度与总时长因果，c23部分支持。"
}
```


- citation-0174：c5固定claim包含引用原文，整体判断规则未覆盖；c15、c16所在末句无实际引用。

## review_0529_0704 上下文记录

产品：Codex desktop。模型名：unknown。推理强度：unknown。开始时间：unknown（未记录可靠时刻）。结束时间：2026-10-08T11:05:23.573959+00:00。独立子代理标识：/root/review_0529_0704；范围 citation-0529 至 citation-0704，共176包，按manifest index顺序处理。

与协调者往来：仅收到 README 指定模板的范围派发，之后发送进度、结构校验和机械修正通知；无判断问题、规则解释或标签交换。允许范围之外读取文件：无。联网：无。未导入、评分或导出。

校验：根目录首次全局校验 valid=651、problems=53（包括其他分段缺文件/复制错误以及本分段46个缺reason文件）。本分段46文件671个pair仅补必需reason字段，完整修改前内容见修正节。修正后调用原校验器check逐个检查本分段176包，problems=0。结构通过不证明语义正确。

显示与续做：首次整份manifest显示截断，后续读取有限索引范围并确认分配范围index连续；包本身均完整显示，未截断/删改/去重。发生自动上下文压缩后按进度继续，已写入判断不重做。压缩点在已完成 citation-0543、0567、0591、0615、0639、0667、0690 左右（若日志精确点不同，以会话日志为准）。读取JSON时将user_message外层协议头与其内JSON分离后完整显示内字段；保留外层元数据。

### 未覆盖或提取不确定情况

- citation-0529：逐个识别句内引用；c13所在句无引用。文档标识不能唯一绑定fragment，依F6第3条保留unknown。
- citation-0536：只配对实际有句内引用的claims。两个文档级标识均有多个候选片段，依F6第3条保留unknown。
- citation-0540：识别实际句内引用；未引用的末段不自动配对。文档级片段映射依F6第3条保留unknown。
- citation-0544：c25句无引用；abstract非标准映射按F6第3条unknown，其余明确element引用逐一判断。
- citation-0546：句内引用只归本句；Shi第一句的实验人数及年龄没有实际引用。多片段文档映射依F6第3条保留unknown。
- citation-0547：实际引用及句内归属保留；语义位置名到fragment的映射按F6第3条unknown。
- citation-0550：逐句识别实际引用并分源判断；001dd元素存在两个片段范围而引用未指定范围，登记未知。未引用的差值句不配对。
- citation-0552：可识别四次文档引用，但无法唯一映射到source_fragments；逐句归属后登记未知。
- citation-0554：三次引用可识别，文档级到片段的归属无法唯一确定，登记未知。
- citation-0555：首个文档在本context仅一个片段，其余文档级引用存在多个片段映射；最后两引用同属一个句子，独立配对。
- citation-0560：识别哈希前缀引用并保留重复顺序；多片段文档级映射未覆盖而登记未知，分号两文档分别配对。
- citation-0570：合法五字段元组按片段判断；其余四字段身份改写的映射属于未覆盖情况，登记unknown；保留作者年份引用。
- citation-0577：规则未覆盖作者加章节的语义引用定位；记入运行说明。
- citation-0580：两处变形身份引用规则未覆盖，记录运行说明。
- citation-0587：第三处引用混有可映射标题与身份变形元组，后者保持unknown并记录。
- citation-0599：引用只给文档标识，该文档在本包有多个片段，无法唯一映射；保持 unknown，不从有利片段反推引用。
- citation-0603：首个文档标识仅对应一个片段并支持断言；其余文档标识对应多个片段，无法唯一消歧，保持 unknown。
- citation-0610：两篇文档级引用均对应多个片段，保留 unknown。PW/AR 引用的文档仅一个片段并直接支持相反效应；末尾限制句无对应固定事实断言。
- citation-0625：各文档级标识对应多个片段，无法唯一映射，不选择有利片段；作者年份身份未登记。
- citation-0634：多片段独立判断。第三处含重复哈希的六项元组，映射规则未覆盖，保留unknown；其他元组映射清晰，按对应正文标题数值片段分开判断。
- citation-0635：文档标识均对应多个片段，不能唯一定位；无引用列表条目不补配。
- citation-0640：文档级引用均对应多个片段，保留无法唯一定位；实际作者年份引用身份未登记，不借上下文文献提及构造映射。
- citation-0651：文档级短引用无法唯一定位，保留句内及句末实际引用归属。
- citation-0661：多个文档级引用定位有歧义；唯一片段引用可明确映射。
- citation-0677：九次文档级引用均有多片段映射歧义，不按有利片段消歧。
- citation-0685：文档级引用的多片段映射不能按支持程度消歧。

### 已写入后发现的潜在判断问题（仅记录，未修改）

- 较早包可能未穷尽作者年份引用；未进行语义回扫或新增配对。
- citation-0553：短四元组hash+element+range的映射可能超出明确覆盖范围。
- citation-0590：一句内相邻引用分句归属的处理可能与后续包的句末整句处理存在差异。
- citation-0600、0668：引文内作者年份是否作为独立引用的归属可能有不确定性。
- citation-0662、0691、0692、0703：句内作者年份引用在后续主张之前时的范围处理可能存在不确定性。
- citation-0673、0681、0694、0698：完整claim归属信息与实际引用处短表述间的支持范围可能有不确定性。
- citation-0699：分号分开的缺失外层括号Source引用按可识别五元组定位；该语法是否被规则明确覆盖可能需由回收会话处理。

补充更正（review_0529_0704）：上文压缩点的粗略job_id列举有误，不应作为精确日志。续做摘要记录的压缩点为完成约22、43、67、91、115、139、162包时，对应约citation-0550、0571、0595、0619、0643、0667、0690；精确时点仍以会话日志为准。最终本次全局校验 valid=701、problems=3，全部为本分段外 citation-0176缺响应、0211及0216逐字复制错误；本分段176包结构problems=0。

- 协调者汇总修正脚本首次误用仓库相对路径但运行于工作包根目录，FileNotFoundError，没有读到或修改任何文件；随后改用正确相对路径。首次全量校验 valid=702，problems=2，均为0211/0216逐字复制括号错误。

## 修正记录：citation-0211

- 时间：2026-10-08T05:06:50.469140-06:00；pair序号：81；字段：citation_text / source_id / citation_occurrence（0275仅occurrence）；修改前：{"claim_id": "c26", "citation_text": "(Garcimartín et al., 2016)", "citation_occurrence": 1, "source_id": "(Garcimartín et al., 2016)", "label": "unknown", "reason": "作者年份引用未给出对应片段标识，冻结规则没有提供映射。"}；修改后：{"claim_id": "c26", "citation_text": "Garcimartín et al., 2016", "citation_occurrence": 2, "source_id": "Garcimartín et al., 2016", "label": "unknown", "reason": "作者年份引用未给出对应片段标识，冻结规则没有提供映射。"}；原因：子代理报告的引用括号误抄及第二次出现序号误抄，协调者按位置核对原文后机械修正，标签与理由不变。
- 修改前完整文件备份：
```json
{
  "anchor_id": "citation-0211",
  "citation_pairs": [
    {
      "claim_id": "c19",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F1",
      "label": "unsupported",
      "reason": "该具体片段没有供应连续性及门口限制结论。"
    },
    {
      "claim_id": "c20",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F1",
      "label": "unsupported",
      "reason": "该具体片段没有供应连续性及门口限制结论。"
    },
    {
      "claim_id": "c19",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F2",
      "label": "supported",
      "reason": "正文明确无供应间隙、门宽限制流动。"
    },
    {
      "claim_id": "c20",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F2",
      "label": "supported",
      "reason": "正文明确无供应间隙、门宽限制流动。"
    },
    {
      "claim_id": "c19",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F3",
      "label": "unsupported",
      "reason": "该具体片段没有供应连续性及门口限制结论。"
    },
    {
      "claim_id": "c20",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F3",
      "label": "unsupported",
      "reason": "该具体片段没有供应连续性及门口限制结论。"
    },
    {
      "claim_id": "c19",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F4",
      "label": "unsupported",
      "reason": "该具体片段没有供应连续性及门口限制结论。"
    },
    {
      "claim_id": "c20",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F4",
      "label": "unsupported",
      "reason": "该具体片段没有供应连续性及门口限制结论。"
    },
    {
      "claim_id": "c21",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "所引片段没有改善统计量的结论。"
    },
    {
      "claim_id": "c22",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "标题或版权片段未说明准稳态分析。"
    },
    {
      "claim_id": "c21",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "unsupported",
      "reason": "所引片段没有改善统计量的结论。"
    },
    {
      "claim_id": "c22",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "摘要明确再注入使宏观准稳态分析成立。"
    },
    {
      "claim_id": "c21",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F3",
      "label": "unsupported",
      "reason": "所引片段没有改善统计量的结论。"
    },
    {
      "claim_id": "c22",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F3",
      "label": "unsupported",
      "reason": "标题或版权片段未说明准稳态分析。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F1",
      "label": "unsupported",
      "reason": "该片段未说明短时波动与宏观准稳态对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F2",
      "label": "supported",
      "reason": "明确短时波动但宏观准稳态的对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F3",
      "label": "unsupported",
      "reason": "该片段未说明短时波动与宏观准稳态对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F4",
      "label": "unsupported",
      "reason": "该片段未说明短时波动与宏观准稳态对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F5",
      "label": "unsupported",
      "reason": "该片段未说明短时波动与宏观准稳态对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F6",
      "label": "unsupported",
      "reason": "该片段未说明短时波动与宏观准稳态对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F7",
      "label": "unsupported",
      "reason": "该片段未说明短时波动与宏观准稳态对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F8",
      "label": "unsupported",
      "reason": "该片段未说明短时波动与宏观准稳态对照。"
    },
    {
      "claim_id": "c24",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F1",
      "label": "supported",
      "reason": "明确准稳态时间范围和出口区密度稳定。"
    },
    {
      "claim_id": "c25",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F1",
      "label": "supported",
      "reason": "明确准稳态时间范围和出口区密度稳定。"
    },
    {
      "claim_id": "c26",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 2,
      "source_id": "B5-F1",
      "label": "unsupported",
      "reason": "该片段未说明先前实验初始空隙或再注入。"
    },
    {
      "claim_id": "c27",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 2,
      "source_id": "B5-F1",
      "label": "unsupported",
      "reason": "该片段未说明先前实验初始空隙或再注入。"
    },
    {
      "claim_id": "c24",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F2",
      "label": "unsupported",
      "reason": "该片段讨论其他实验对照，没有该稳定时间与密度结论。"
    },
    {
      "claim_id": "c25",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F2",
      "label": "unsupported",
      "reason": "该片段讨论其他实验对照，没有该稳定时间与密度结论。"
    },
    {
      "claim_id": "c26",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 2,
      "source_id": "B5-F2",
      "label": "supported",
      "reason": "明确初始空隙及缺少再注入解释非稳态。"
    },
    {
      "claim_id": "c27",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 2,
      "source_id": "B5-F2",
      "label": "supported",
      "reason": "明确初始空隙及缺少再注入解释非稳态。"
    },
    {
      "claim_id": "c28",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F1",
      "label": "unsupported",
      "reason": "所引片段未说明截去首三秒和末十秒。"
    },
    {
      "claim_id": "c28",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306",
      "label": "invalid",
      "reason": "引用写出的来源标识不存在于context，四元素来源项缺少正常文档标识，不修复。"
    },
    {
      "claim_id": "c29",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "标题或版权片段未说明微观流动结论。"
    },
    {
      "claim_id": "c30",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "标题或版权片段未说明微观流动结论。"
    },
    {
      "claim_id": "c31",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "标题或版权片段未说明微观流动结论。"
    },
    {
      "claim_id": "c29",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "摘要明确礼貌有序、自私比例增大紊乱及拉链交替。"
    },
    {
      "claim_id": "c30",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "摘要明确礼貌有序、自私比例增大紊乱及拉链交替。"
    },
    {
      "claim_id": "c31",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "摘要明确礼貌有序、自私比例增大紊乱及拉链交替。"
    },
    {
      "claim_id": "c29",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F3",
      "label": "unsupported",
      "reason": "标题或版权片段未说明微观流动结论。"
    },
    {
      "claim_id": "c30",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F3",
      "label": "unsupported",
      "reason": "标题或版权片段未说明微观流动结论。"
    },
    {
      "claim_id": "c31",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F3",
      "label": "unsupported",
      "reason": "标题或版权片段未说明微观流动结论。"
    },
    {
      "claim_id": "c32",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F1",
      "label": "supported",
      "reason": "该片段明确峰值、低时间间隔、指数爆发规模与涡旋观察。"
    },
    {
      "claim_id": "c33",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F1",
      "label": "supported",
      "reason": "该片段明确峰值、低时间间隔、指数爆发规模与涡旋观察。"
    },
    {
      "claim_id": "c34",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F1",
      "label": "supported",
      "reason": "该片段明确峰值、低时间间隔、指数爆发规模与涡旋观察。"
    },
    {
      "claim_id": "c35",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F1",
      "label": "supported",
      "reason": "该片段明确峰值、低时间间隔、指数爆发规模与涡旋观察。"
    },
    {
      "claim_id": "c32",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F2",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c33",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F2",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c34",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F2",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c35",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F2",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c32",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F3",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c33",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F3",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c34",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F3",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c35",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F3",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c32",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F4",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c33",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F4",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c34",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F4",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c35",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F4",
      "label": "unsupported",
      "reason": "该片段未说明这些时间间隔分布和竞争紊乱结果。"
    },
    {
      "claim_id": "c36",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F1",
      "label": "unsupported",
      "reason": "该具体片段未说明停留时间结果。"
    },
    {
      "claim_id": "c37",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F1",
      "label": "unsupported",
      "reason": "该具体片段未说明停留时间结果。"
    },
    {
      "claim_id": "c38",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F1",
      "label": "unsupported",
      "reason": "该具体片段未说明停留时间结果。"
    },
    {
      "claim_id": "c36",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F3",
      "label": "supported",
      "reason": "该片段明确占用率、个体类型和侧面到达的停留时间结果。"
    },
    {
      "claim_id": "c37",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F3",
      "label": "supported",
      "reason": "该片段明确占用率、个体类型和侧面到达的停留时间结果。"
    },
    {
      "claim_id": "c38",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F3",
      "label": "supported",
      "reason": "该片段明确占用率、个体类型和侧面到达的停留时间结果。"
    },
    {
      "claim_id": "c36",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F4",
      "label": "unsupported",
      "reason": "该具体片段未说明停留时间结果。"
    },
    {
      "claim_id": "c37",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F4",
      "label": "unsupported",
      "reason": "该具体片段未说明停留时间结果。"
    },
    {
      "claim_id": "c38",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F4",
      "label": "unsupported",
      "reason": "该具体片段未说明停留时间结果。"
    },
    {
      "claim_id": "c36",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306",
      "label": "invalid",
      "reason": "不存在该来源标识，不修复引用。"
    },
    {
      "claim_id": "c37",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306",
      "label": "invalid",
      "reason": "不存在该来源标识，不修复引用。"
    },
    {
      "claim_id": "c38",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306",
      "label": "invalid",
      "reason": "不存在该来源标识，不修复引用。"
    },
    {
      "claim_id": "c39",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "所引标题或版权片段没有流率与密度结果。"
    },
    {
      "claim_id": "c40",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "所引标题或版权片段没有流率与密度结果。"
    },
    {
      "claim_id": "c39",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306",
      "label": "invalid",
      "reason": "不存在该引用来源标识，不修复。"
    },
    {
      "claim_id": "c40",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306",
      "label": "invalid",
      "reason": "不存在该引用来源标识，不修复。"
    },
    {
      "claim_id": "c39",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F3",
      "label": "unsupported",
      "reason": "所引标题或版权片段没有流率与密度结果。"
    },
    {
      "claim_id": "c40",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F3",
      "label": "unsupported",
      "reason": "所引标题或版权片段没有流率与密度结果。"
    },
    {
      "claim_id": "c41",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"49202eb71404333a166376a5\",195,335],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]]]",
      "citation_occurrence": 1,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "该片段明确门宽72cm以及17m和25m再注入回路长度。"
    },
    {
      "claim_id": "c42",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"49202eb71404333a166376a5\",195,335],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]]]",
      "citation_occurrence": 1,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "该片段明确门宽72cm以及17m和25m再注入回路长度。"
    },
    {
      "claim_id": "c41",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"49202eb71404333a166376a5\",195,335],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]]]",
      "citation_occurrence": 1,
      "source_id": "pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306",
      "label": "invalid",
      "reason": "两个四元素来源项均使用不存在的相同来源标识，保留为该无效来源。"
    },
    {
      "claim_id": "c42",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"49202eb71404333a166376a5\",195,335],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]]]",
      "citation_occurrence": 1,
      "source_id": "pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306",
      "label": "invalid",
      "reason": "两个四元素来源项均使用不存在的相同来源标识，保留为该无效来源。"
    },
    {
      "claim_id": "c23",
      "citation_text": "(Seyfried et al., 2009a; Garcimartín et al., 2016)",
      "citation_occurrence": 1,
      "source_id": "(Seyfried et al., 2009a; Garcimartín et al., 2016)",
      "label": "unknown",
      "reason": "作者年份引用未给出对应片段标识，冻结规则没有提供映射。"
    },
    {
      "claim_id": "c26",
      "citation_text": "(Garcimartín et al., 2016)",
      "citation_occurrence": 1,
      "source_id": "(Garcimartín et al., 2016)",
      "label": "unknown",
      "reason": "作者年份引用未给出对应片段标识，冻结规则没有提供映射。"
    },
    {
      "claim_id": "c26",
      "citation_text": "Seyfried et al. (2009a)",
      "citation_occurrence": 1,
      "source_id": "Seyfried et al. (2009a)",
      "label": "unknown",
      "reason": "作者年份引用未给出对应片段标识，冻结规则没有提供映射。"
    }
  ],
  "citation_extraction_unknown": true,
  "reason": "合并引用片段逐个评估；错误来源标识按原文invalid保留；句内作者年份到片段映射未覆盖。"
}
```

## 修正记录：citation-0216

- 时间：2026-10-08T05:06:50.470757-06:00；pair序号：12；字段：citation_text / source_id / citation_occurrence（0275仅occurrence）；修改前：{"claim_id": "c20", "citation_text": "(Garcimartín et al., 2016)", "citation_occurrence": 1, "source_id": "(Garcimartín et al., 2016)", "label": "unknown", "reason": "内嵌作者年份引用未指定片段，冻结规则未给出唯一来源映射。"}；修改后：{"claim_id": "c20", "citation_text": "Garcimartín et al., 2016", "citation_occurrence": 2, "source_id": "Garcimartín et al., 2016", "label": "unknown", "reason": "内嵌作者年份引用未指定片段，冻结规则未给出唯一来源映射。"}；原因：子代理报告的引用括号误抄及第二次出现序号误抄，协调者按位置核对原文后机械修正，标签与理由不变。
- 修改前完整文件备份：
```json
{
  "anchor_id": "citation-0216",
  "citation_pairs": [
    {
      "claim_id": "c13",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b151c94641572d8067b7107f\",0,792]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F1",
      "label": "supported",
      "reason": "明确周期边界、返回室内及交替两条回路随机化设计。"
    },
    {
      "claim_id": "c14",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b151c94641572d8067b7107f\",0,792]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F1",
      "label": "supported",
      "reason": "明确周期边界、返回室内及交替两条回路随机化设计。"
    },
    {
      "claim_id": "c15",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F2",
      "label": "supported",
      "reason": "明确无入流间隙且流动由门口而非返回时间限制。"
    },
    {
      "claim_id": "c16",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F2",
      "label": "supported",
      "reason": "明确无入流间隙且流动由门口而非返回时间限制。"
    },
    {
      "claim_id": "c17",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b151c94641572d8067b7107f\",0,792]]]",
      "citation_occurrence": 2,
      "source_id": "B5-F1",
      "label": "supported",
      "reason": "说明减少有限人数统计问题并获得每次约250次通行及177至352范围。"
    },
    {
      "claim_id": "c18",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b151c94641572d8067b7107f\",0,792]]]",
      "citation_occurrence": 2,
      "source_id": "B5-F1",
      "label": "supported",
      "reason": "说明减少有限人数统计问题并获得每次约250次通行及177至352范围。"
    },
    {
      "claim_id": "c19",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F3",
      "label": "unsupported",
      "reason": "该片段是竞争流率与faster-is-slower对照，没有短时波动及宏观准稳态。"
    },
    {
      "claim_id": "c20",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "明确初始空隙和无再注入为非稳态对照原因。"
    },
    {
      "claim_id": "c21",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "明确初始空隙和无再注入为非稳态对照原因。"
    },
    {
      "claim_id": "c11",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 2,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "明确为减小瞬态去掉首三秒末十秒。"
    },
    {
      "claim_id": "c19",
      "citation_text": "(Seyfried et al., 2009a; Garcimartín et al., 2016)",
      "citation_occurrence": 1,
      "source_id": "(Seyfried et al., 2009a; Garcimartín et al., 2016)",
      "label": "unknown",
      "reason": "内嵌作者年份引用未指定片段，冻结规则未给出唯一来源映射。"
    },
    {
      "claim_id": "c20",
      "citation_text": "(Garcimartín et al., 2016)",
      "citation_occurrence": 1,
      "source_id": "(Garcimartín et al., 2016)",
      "label": "unknown",
      "reason": "内嵌作者年份引用未指定片段，冻结规则未给出唯一来源映射。"
    },
    {
      "claim_id": "c20",
      "citation_text": "Seyfried et al. (2009a)",
      "citation_occurrence": 1,
      "source_id": "Seyfried et al. (2009a)",
      "label": "unknown",
      "reason": "内嵌作者年份引用未指定片段，冻结规则未给出唯一来源映射。"
    }
  ],
  "citation_extraction_unknown": true,
  "reason": "精确Source引用按句定位，内嵌作者年份的片段映射规则未覆盖。"
}
```

## 修正记录：citation-0275

- 时间：2026-10-08T05:06:50.471632-06:00；pair序号：77；字段：citation_text / source_id / citation_occurrence（0275仅occurrence）；修改前：{"claim_id": "c26", "citation_text": "Garcimartín et al., 2016", "citation_occurrence": 1, "source_id": "Garcimartín et al., 2016", "label": "unknown", "reason": "作者年份引用没有唯一冻结片段映射。"}；修改后：{"claim_id": "c26", "citation_text": "Garcimartín et al., 2016", "citation_occurrence": 2, "source_id": "Garcimartín et al., 2016", "label": "unknown", "reason": "作者年份引用没有唯一冻结片段映射。"}；原因：子代理报告的引用括号误抄及第二次出现序号误抄，协调者按位置核对原文后机械修正，标签与理由不变。
- 修改前完整文件备份：
```json
{
  "anchor_id": "citation-0275",
  "citation_pairs": [
    {
      "claim_id": "c19",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F1",
      "label": "unsupported",
      "reason": "该片段没有连续供给与限流关系。"
    },
    {
      "claim_id": "c19",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F2",
      "label": "supported",
      "reason": "片段明确连续供给和门口限流而非回流线路时间。"
    },
    {
      "claim_id": "c19",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F3",
      "label": "unsupported",
      "reason": "该片段没有连续供给与限流关系。"
    },
    {
      "claim_id": "c19",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F4",
      "label": "unsupported",
      "reason": "该片段没有连续供给与限流关系。"
    },
    {
      "claim_id": "c20",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F1",
      "label": "unsupported",
      "reason": "该片段没有连续供给与限流关系。"
    },
    {
      "claim_id": "c20",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F2",
      "label": "supported",
      "reason": "片段明确连续供给和门口限流而非回流线路时间。"
    },
    {
      "claim_id": "c20",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F3",
      "label": "unsupported",
      "reason": "该片段没有连续供给与限流关系。"
    },
    {
      "claim_id": "c20",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b5800fd3197854b3f6b8c5a2\",0,20],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"cc3f74e7c7c0aaf27b929a02\",0,312],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"30c185f9f617831c7d09feb4\",0,1039],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"7308f3cb63581da29cd19828\",0,282]]]",
      "citation_occurrence": 1,
      "source_id": "B2-F4",
      "label": "unsupported",
      "reason": "该片段没有连续供给与限流关系。"
    },
    {
      "claim_id": "c21",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "该片段未给出统计改善或对应准稳态主张。"
    },
    {
      "claim_id": "c21",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "unsupported",
      "reason": "该片段未给出统计改善或对应准稳态主张。"
    },
    {
      "claim_id": "c21",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F3",
      "label": "unsupported",
      "reason": "该片段未给出统计改善或对应准稳态主张。"
    },
    {
      "claim_id": "c22",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "该片段未给出统计改善或对应准稳态主张。"
    },
    {
      "claim_id": "c22",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F2",
      "label": "supported",
      "reason": "摘要明确回流设置使分析处于宏观准稳态。"
    },
    {
      "claim_id": "c22",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]",
      "citation_occurrence": 1,
      "source_id": "B1-F3",
      "label": "unsupported",
      "reason": "该片段未给出统计改善或对应准稳态主张。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F1",
      "label": "unsupported",
      "reason": "该片段没有该时间尺度对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F2",
      "label": "supported",
      "reason": "该片段明确瞬时波动与宏观准稳态对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F3",
      "label": "unsupported",
      "reason": "该片段没有该时间尺度对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F4",
      "label": "unsupported",
      "reason": "该片段没有该时间尺度对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F5",
      "label": "unsupported",
      "reason": "该片段没有该时间尺度对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F6",
      "label": "unsupported",
      "reason": "该片段没有该时间尺度对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F7",
      "label": "unsupported",
      "reason": "该片段没有该时间尺度对照。"
    },
    {
      "claim_id": "c23",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"a64927f80acfa3a4cd36cbe0\",0,19],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"ecc4fae662615d6b18502f74\",0,641],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e412ae13331e8e0d60fc6206\",0,269],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"21dd5ac2412845d0b009069a\",0,242],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"3161a3b099e74eedfab0b3de\",0,3],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"66c2b107fcef3186eb79d500\",0,5],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"e568aad852d03e1e1c6969f2\",0,279],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4c2ebf43067bfdcede732440\",0,104]]]",
      "citation_occurrence": 1,
      "source_id": "B3-F8",
      "label": "unsupported",
      "reason": "该片段没有该时间尺度对照。"
    },
    {
      "claim_id": "c24",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F1",
      "label": "supported",
      "reason": "片段给出稳态开始、持续及出口密度近稳态。"
    },
    {
      "claim_id": "c24",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F2",
      "label": "unsupported",
      "reason": "该片段没有该开始持续时间或密度事实。"
    },
    {
      "claim_id": "c25",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F1",
      "label": "supported",
      "reason": "片段给出稳态开始、持续及出口密度近稳态。"
    },
    {
      "claim_id": "c25",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F2",
      "label": "unsupported",
      "reason": "该片段没有该开始持续时间或密度事实。"
    },
    {
      "claim_id": "c26",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F1",
      "label": "unsupported",
      "reason": "所指片段没有该事实，不能借用其邻接正文。"
    },
    {
      "claim_id": "c26",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c27",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "B5-F1",
      "label": "unsupported",
      "reason": "所指片段没有该事实，不能借用其邻接正文。"
    },
    {
      "claim_id": "c27",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c28",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 2,
      "source_id": "B5-F1",
      "label": "unsupported",
      "reason": "所指片段没有该事实，不能借用其邻接正文。"
    },
    {
      "claim_id": "c28",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d4b518357639ad0d6818be96\",635,898],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"9061bc4dad7f2acb79b60713\",0,699]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c29",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "所指片段没有该事实，不能借用其邻接正文。"
    },
    {
      "claim_id": "c29",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c29",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c30",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "所指片段没有该事实，不能借用其邻接正文。"
    },
    {
      "claim_id": "c30",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c30",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c31",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F1",
      "label": "supported",
      "reason": "冻结片段明确给出该数量或现象。"
    },
    {
      "claim_id": "c31",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c31",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c31",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c32",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F1",
      "label": "supported",
      "reason": "冻结片段明确给出该数量或现象。"
    },
    {
      "claim_id": "c32",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c32",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c32",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c33",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "B6-F1",
      "label": "supported",
      "reason": "冻结片段明确给出该数量或现象。"
    },
    {
      "claim_id": "c33",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c33",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c33",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c34",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "B6-F1",
      "label": "unsupported",
      "reason": "所指片段没有该事实，不能借用其邻接正文。"
    },
    {
      "claim_id": "c34",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c34",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c34",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c35",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "B6-F1",
      "label": "unsupported",
      "reason": "所指片段没有该事实，不能借用其邻接正文。"
    },
    {
      "claim_id": "c35",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c35",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c35",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c36",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "B6-F1",
      "label": "unsupported",
      "reason": "所指片段没有该事实，不能借用其邻接正文。"
    },
    {
      "claim_id": "c36",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c36",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c36",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"b063ef39e429a50a00975d86\",550,1229],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4551760ab5138607c379e6b5\",0,428],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"fa4a88f0e2e68dbe25ea9c10\",0,338],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"aa321f19a8a0e9f11ff2aa97\",0,260]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c37",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 2,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "所指片段没有该事实，不能借用其邻接正文。"
    },
    {
      "claim_id": "c37",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c37",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c38",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 2,
      "source_id": "B1-F1",
      "label": "unsupported",
      "reason": "所指片段没有该事实，不能借用其邻接正文。"
    },
    {
      "claim_id": "c38",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c38",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"67d78c61c60fb9d5f58b2479\",0,8],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"89bc326ff861bfa77a1dc4d4\",0,1684],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]]]",
      "citation_occurrence": 2,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"1a17c86a60bf685ccae32250\",0,19]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c39",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"49202eb71404333a166376a5\",195,335],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]]]",
      "citation_occurrence": 1,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "冻结片段明确给出该数量或现象。"
    },
    {
      "claim_id": "c39",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"49202eb71404333a166376a5\",195,335],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c39",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"49202eb71404333a166376a5\",195,335],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c40",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"49202eb71404333a166376a5\",195,335],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]]]",
      "citation_occurrence": 1,
      "source_id": "B4-F1",
      "label": "supported",
      "reason": "冻结片段明确给出该数量或现象。"
    },
    {
      "claim_id": "c40",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"49202eb71404333a166376a5\",195,335],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c40",
      "citation_text": "[Source [[\"pearl-src-15c1100e05ee58e4\",\"15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"49202eb71404333a166376a5\",195,335],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"d33251460505525cfc5ae20c\",0,435],[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]]]",
      "citation_occurrence": 1,
      "source_id": "[\"pearl-src-15c1100e05ee58e49116bf61495fc38dc63b5dfaa47211e7ad5e1f08acbc9306\",\"4a1be962de80e25a0118d085\",0,348]",
      "label": "invalid",
      "reason": "该引用元组缺少文档版本字段，原标识不匹配任何冻结source，保留原样不修复。"
    },
    {
      "claim_id": "c23",
      "citation_text": "Seyfried et al., 2009a",
      "citation_occurrence": 1,
      "source_id": "Seyfried et al., 2009a",
      "label": "unknown",
      "reason": "作者年份引用没有唯一冻结片段映射。"
    },
    {
      "claim_id": "c23",
      "citation_text": "Garcimartín et al., 2016",
      "citation_occurrence": 1,
      "source_id": "Garcimartín et al., 2016",
      "label": "unknown",
      "reason": "作者年份引用没有唯一冻结片段映射。"
    },
    {
      "claim_id": "c26",
      "citation_text": "Garcimartín et al., 2016",
      "citation_occurrence": 1,
      "source_id": "Garcimartín et al., 2016",
      "label": "unknown",
      "reason": "作者年份引用没有唯一冻结片段映射。"
    },
    {
      "claim_id": "c26",
      "citation_text": "Seyfried et al. (2009a)",
      "citation_occurrence": 1,
      "source_id": "Seyfried et al. (2009a)",
      "label": "unknown",
      "reason": "作者年份引用没有唯一冻结片段映射。"
    }
  ],
  "citation_extraction_unknown": true,
  "reason": "逐片段判断；缺字段元组保留invalid，作者年份无唯一映射登记unknown。"
}
```

## 子代理 review_0177_0352 汇总

- 产品：Codex desktop；模型名 unknown；推理强度 unknown。结束：2026-10-08 11:02:02 UTC；独立负责 citation-0177 至 citation-0352 共176包。
- 自动上下文压缩7次；citation-0350初次完整显示再次截断，随后按原文件前后两半完整重新显示后才判断。与协调者没有判断规则往来；只提交进度、机械错误与运行记录。
- 2471 pairs；54个 citation_extraction_unknown；不改既有判断。

### 未覆盖情况：review_0177_0352
- citation-0178：文档级引用对应多个来源片段，冻结规则未规定如何确定被引fragment；保留原来源标识并记unknown。按逐句引用归属，其它无引用句不配对。
- citation-0185：文档级引用无法唯一确定多个同文档片段中的被引fragment；保留原标识并记unknown。
- citation-0188：raw_answer含作者年份引用，source_fragments只有匿名doc_id和版本/元素身份，无法唯一对应作者年份与被引fragment；按未覆盖情况保留unknown。无明确引用的Ni陈述不猜补来源。
- citation-0189：精确来源引用按句核对；另有嵌入作者年份表达，匿名fragment无法唯一对应其来源，保留unknown。
- citation-0193：具体来源逐片段核对；作者年份Pastor引用与匿名来源无确定身份映射，记未覆盖unknown。无引用独立表格复述句不配对。
- citation-0196：句内与句末引用关系可确定，但文档级引用无法唯一映射至具体片段；保留原引用标识。
- citation-0206：句末引用关系可定位，但文档级引用到多个片段的映射未被冻结规则覆盖。
- citation-0211：合并引用片段逐个评估；错误来源标识按原文invalid保留；句内作者年份到片段映射未覆盖。
- citation-0216：精确Source引用按句定位，内嵌作者年份的片段映射规则未覆盖。
- citation-0217：引用只归其所在句；作者年份到片段映射未知。
- citation-0221：句末来源仅关联同句；作者年份未覆盖唯一来源映射规则，登记unknown而不猜测。
- citation-0223：同句所有声明均与各引用关联；省略offset且chunk重复不能猜测片段，登记unknown。
- citation-0226：逐次提取doc-only引用；多片段文档映射规则未覆盖，保留文档标识并unknown。
- citation-0227：按原文保留裸文档hash引用；多片段映射未覆盖，unknown；同句关联。
- citation-0231：来源tuple独立片段判断；作者年份映射未覆盖登记unknown。
- citation-0233：解析原文所有引用形式；数字与作者年份映射未覆盖，unknown。
- citation-0235：保留固定复合claim；来源与作者年份分别配对，同句全范围；作者年份映射未覆盖。
- citation-0238：doc-only多片段映射未覆盖；保留原文标识及同句关联，前一独立未引用句不补造引用。
- citation-0245：第一文档唯一定位；其余doc-only引用多片段无法消歧，标记冻结规则未覆盖。最后独立总结句没有引用。
- citation-0250：结构化来源按精确片段判断；作者年份引用的唯一映射未覆盖，保留unknown。
- citation-0258：doc-only多片段唯一映射未被冻结规则覆盖，保留unknown与原始文档标识。
- citation-0264：结构化引用按片段独立判断；作者年份无唯一映射保留unknown。
- citation-0267：文档级引用无法唯一解析片段，保留原标识并登记未覆盖情形。
- citation-0271：逐片段独立判断；数字参考号[4]无冻结映射，登记未覆盖提取情形。
- citation-0274：结构化引用可解析，作者年份引用无唯一映射，登记未覆盖情形。
- citation-0275：逐片段判断；缺字段元组保留invalid，作者年份无唯一映射登记unknown。
- citation-0277：保留原文档标识，登记文档级引用无法唯一绑定片段的提取边界。
- citation-0281：描述性来源引用没有可唯一解析的冻结source，登记未覆盖提取情形。
- citation-0282：句内两引用关联同句固定主张；数字参考号无唯一映射，登记未覆盖情形。
- citation-0283：结构化引用逐句判断，作者年份引用无映射登记未覆盖情形。
- citation-0287：结构化引用逐片段判断；作者年份引用无映射登记未覆盖情形。
- citation-0290：显式元组可定位；作者年份引用无法唯一定位。
- citation-0291：逐句处理；作者年份引用没有唯一片段映射。
- citation-0292：逐次计数重复引用；作者年份映射不唯一。
- citation-0293：元组引用可定位；作者年份引用无唯一映射。
- citation-0295：重复显式引用按原文出现次数处理；作者年份无唯一映射。
- citation-0310：两个描述性引用来源均无法唯一定位。
- citation-0311：原回答只有此作者年份引用，没有明确片段元组。
- citation-0312：两个句尾文档级引用均不能唯一映射片段。
- citation-0313：显式作者年份引用无法唯一映射到来源；其余无引用句不产生配对。
- citation-0315：完整来源元组可定位；文献编号[25]无法唯一映射。
- citation-0316：保留每个描述式引用及其句内claims；来源定位含省略而无法唯一确定。
- citation-0318：compound引用中chunk可唯一定位，abstract描述保留unknown；引用归所在句。
- citation-0323：元组来源逐片段判断；未解析文献编号保留unknown；不把句末引用扩展到前一句。
- citation-0324：保留九次文档级引用与各自句内claims，片段定位真实歧义。
- citation-0325：完整元组逐片段判断；作者年份引用保留unknown。
- citation-0326：chunk唯一时按所引片段判断；同chunk多区间保留unknown，不借相邻或修复错引。
- citation-0329：四次文档级引用逐句保留，片段定位有歧义。
- citation-0331：仅单片段文档可唯一定位，其他文档引用保留unknown。
- citation-0333：句内引用逐来源判断，作者年份保留unknown。
- citation-0340：完整来源标识可定位；内嵌作者年份引用无唯一映射。
- citation-0345：内嵌作者年份引用无法唯一映射；显式来源按同句精确片段判定。
- citation-0350：作者年份引用无唯一映射；显式完整来源逐片段判定，损坏来源保持原样invalid。
- citation-0351：两处描述性来源引用不能映射到唯一冻结片段。

## 最终未覆盖及提取不确定情况汇总

以下逐字汇总已有响应的 reason，只作运行记录，不生成新判断；各上下文在上文列出的具体未覆盖原因同时保留。
- citation-0001：引用只给文档标识，该标识对应多个块和片段；冻结规则没有覆盖如何将该文档级引用唯一映射到 fragment_id，不能挑选最有利片段。按 F6 第3条记 unknown。
- citation-0005：两处句内引用分别归属 c3 和 c6；c5 所在前句无引用。该引用用文档名与 abstract 描述定位，但标题与摘要在不同片段；规则没有覆盖这种非精确描述如何唯一对应 fragment_id，按 F6 第3条记 unknown。
- citation-0006：显式多来源列表分别保留每个片段的独立 pair；不拼接其它片段修补截断。c17 同句的作者年份括号可能是原报告归属复述或额外实际引用，冻结规则未覆盖这类转述来源的引用身份，保留三对 unknown。
- citation-0016：Source 引用按所在事实句配对；无引用前句不扩展。句内 Ziemer et al. (2016) 是转述实验作者归属或独立声明的引用，规则未覆盖这种二级来源身份；不读取包外文献，保留 unknown。
- citation-0022：没有 Source 定位引用；作者年份的引用身份及片段映射存在未覆盖情形，保留 unknown 待后续决定。
- citation-0024：Source引用按所在句绑定；作者年份无法唯一确定引用身份，保留unknown。
- citation-0029：没有Source定位引用；作者年份所在句的引用身份未覆盖，其余句不补引用。
- citation-0031：保留两个描述性来源引用，文档级及abstract称谓的片段映射不明确；其他句不自动借用来源。
- citation-0032：Source按所在句绑定；作者年份身份及片段映射保留unknown，未引用前句不借用邻近citation。
- citation-0033：Source逐句配对，未引用的前句不借用后句来源；作者年份保留unknown。
- citation-0034：Source虽括号不完整但五元组唯一定位片段，逐句配对；引号内作者年份身份保留unknown。
- citation-0040：结构化引用保留四项错误来源为invalid；作者年份引用的片段映射未知。
- citation-0044：文档级引用均缺少唯一片段定位，保留unknown。
- citation-0048：两处文档级引用的来源片段映射未知。
- citation-0050：结构化引用映射明确；两处作者年份引用映射未知。
- citation-0052：结构化引用明确；作者年份引用片段映射未知。
- citation-0053：全部文档级引用的片段映射未知；无固定主张的末句引用不产生主张配对。
- citation-0054：Source引文未给出来源身份，固定主张还出现在引文本身；映射和内部归属未覆盖。
- citation-0055：多片段文档级映射未知；另一文档仅有一个片段可唯一映射。
- citation-0060：仅编号[24]是实际引用，其片段映射未知。
- citation-0065：作者年份标识未提供与source_fragments具体片段的映射，规则未覆盖该来源定位。
- citation-0068：引用仅有文档标识，对应多个片段，未指定版本、元素及区间；规则未覆盖唯一片段选择。
- citation-0070：文档级标识对应多个片段，没有元素、版本和区间；规则未覆盖具体片段的选择。
- citation-0073：文档级引用对应多个片段，缺少元素、版本及区间；规则未覆盖唯一片段的选择。
- citation-0074：引用仅有文档及章节名称，对应多个片段，没有元素、版本及区间；规则未覆盖具体片段选择。
- citation-0076：文档级引用对应多个片段，没有元素、版本及区间；规则未覆盖唯一片段选择。
- citation-0082：Pouw et al. (2020, 2022) 作者年份标识未给出具体来源片段映射，规则未覆盖此定位。
- citation-0083：引述中的作者年份引用没有具体片段映射，且引用文本本身嵌于固定claim，规则未覆盖其归属和定位。
- citation-0084：Li (2023) 的来源映射未被规则覆盖。
- citation-0090：Pastor et al. (2015) 来源映射未覆盖。
- citation-0093：文档级与作者年份引文的片段映射未覆盖。
- citation-0095：文档级引用到片段的映射未覆盖。
- citation-0097：文档/元素简写的片段映射未覆盖。
- citation-0098：文档级映射及固定claim包含引用的情况未覆盖。
- citation-0099：固定c3/c5包含实际引文，规则未覆盖该整体claim与引文关系。
- citation-0101：文档级片段映射与claim内含引文的情况未覆盖。
- citation-0104：简写来源映射及固定claim含引文未覆盖。
- citation-0106：c7固定claim包含引用串本身，规则未覆盖其配对处理；其余按实际引用与被引片段评审。
- citation-0107：c3固定claim包含引用串本身，规则未覆盖；句内多引用各自配对。
- citation-0108：c7固定claim包含引用串本身，规则未覆盖；多来源独立评审。
- citation-0109：实际作者年份引用缺少片段身份，规则未覆盖其映射；其余句没有实际引用。
- citation-0110：c3、c4、c6固定claim包含引用串本身，规则未覆盖。
- citation-0111：c3固定claim包含引用串本身，规则未覆盖；不借相邻片段补足截断证据。
- citation-0112：c5固定claim包含引用串本身，规则未覆盖。
- citation-0113：c5、c6固定claim包含引用串本身，规则未覆盖。
- citation-0115：作者年份引用无片段映射；c3固定claim包含引用串本身，均按未覆盖记unknown。
- citation-0116：Li (2023)、Kremer et al. (2021)映射未覆盖；c6固定claim含引用串，记unknown。
- citation-0117：Toelch (2015)作者年份引用映射未覆盖，其余句无实际引用。
- citation-0119：c3固定claim包含引用串本身，规则未覆盖；末句无实际引用。
- citation-0120：c3、c5固定claim含引用串，规则未覆盖。
- citation-0123：c5固定claim包含引用串本身，规则未覆盖；依被引片段字面及单位评审。
- citation-0124：Moustaid et al. (2021)作者年份引用映射未覆盖；仅评被引片段。
- citation-0125：c1固定claim包含引用串本身，规则未覆盖；只评被引片段。
- citation-0126：Li (2023)映射未覆盖，c6固定claim包含引用串本身，记unknown。
- citation-0127：c2至c8固定claim包含引用串本身，规则未覆盖；c12至c14所在句没有实际引用。
- citation-0128：c4、c5 固定文本含 citation，未覆盖情况按 F6 第3条保留 unknown。
- citation-0129：c7、c18 固定文本包含引文，作者年份至片段映射未覆盖；保留 unknown。
- citation-0130：c22 含作者年份引用，映射及固定文本含引用情形未覆盖，保留 unknown。
- citation-0131：c4、c7、c11 固定文本包含引用，未覆盖情形保留 unknown。
- citation-0133：c3、c27、c28 含引文，作者年份映射未覆盖，保留 unknown。
- citation-0137：c19 含 [25]，数字引文映射及固定文本含引用情形未覆盖，保留 unknown。
- citation-0138：作者年份引文没有到片段的映射规则，按 F6 第3条保留 unknown。
- citation-0140：c3、c6–c9 固定文本含引文，规则未覆盖情形保留 unknown。
- citation-0141：c2、c3、c5 固定文本含引用，未覆盖情况保留 unknown。
- citation-0142：c2、c4 固定文本含引用，未覆盖情况保留 unknown。
- citation-0143：文档级引用和作者年份映射未覆盖，c4、c17、c19、c21 含引用，保留 unknown。
- citation-0145：c4、c5、c7 固定文本含引用，未覆盖情况保留 unknown。
- citation-0146：c4、c5、c7 固定文本含引用，未覆盖情况保留 unknown。
- citation-0148：c3、c5 固定文本含引用，未覆盖情况保留 unknown。
- citation-0150：c7、c9、c10 的固定 claim 含完整引用；规则未覆盖此类整体 claim 配对，记 unknown。
- citation-0151：c3、c5 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。
- citation-0152：四处引用仅含文档短标识，未给片段及区间，冻结规则未覆盖唯一映射；c5、c6固定文本含引用亦未覆盖，记 unknown。
- citation-0153：c7、c8 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。
- citation-0155：c3、c4、c6、c8、c9、c13、c14、c15 固定 claim 整体含完整引用，规则未覆盖这种配对判断，记 unknown。
- citation-0156：c2 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。
- citation-0157：引用仅有文档短标识，不能唯一映射片段；c4、c8、c10整体固定文本含引用，规则亦未覆盖，均记 unknown。
- citation-0158：c7、c8、c9、c11 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。
- citation-0160：c4、c6、c7 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。
- citation-0161：c1–c6 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。
- citation-0162：c6、c8、c9 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。
- citation-0163：c2 固定 claim 包含完整引用且另有部分重复区间，规则未覆盖该整体 claim 配对，记 unknown。
- citation-0164：c4、c5、c6、c9 固定claim含完整引用；Ziemer et al. (2016)作者年份引用的片段映射未覆盖，记 unknown。
- citation-0165：引用只给文档ID，未覆盖唯一片段映射；c4、c5、c11–c14固定文本含完整引用亦未覆盖，记 unknown。
- citation-0166：c10、c11 固定 claim 含完整引用，规则未覆盖这种整体 claim 配对，记 unknown。
- citation-0168：Li et al. (2023)作者年份引用的来源片段映射未覆盖，记 unknown。
- citation-0169：三处引用只有文档ID，唯一片段映射未覆盖，记 unknown。
- citation-0170：引用均为无版本、无偏移的文档与元素标识；精确片段映射未覆盖。c4、c6、c9固定claim包含引用，整体判断未覆盖，未拆分。
- citation-0171：c1固定文本包含引用且重复位置文字不同，规则未覆盖该整体claim的引用判断；不拆分或修改。
- citation-0172：c2、c4、c5、c8、c9、c14固定claim含引用原文，整体判断规则未覆盖。
- citation-0173：c4、c7固定claim包含引用，整体判断规则未覆盖；不拆分改写。
- citation-0174：c5固定claim包含引用原文，整体判断规则未覆盖；c15、c16所在末句无实际引用。
- citation-0178：文档级引用对应多个来源片段，冻结规则未规定如何确定被引fragment；保留原来源标识并记unknown。按逐句引用归属，其它无引用句不配对。
- citation-0185：文档级引用无法唯一确定多个同文档片段中的被引fragment；保留原标识并记unknown。
- citation-0188：raw_answer含作者年份引用，source_fragments只有匿名doc_id和版本/元素身份，无法唯一对应作者年份与被引fragment；按未覆盖情况保留unknown。无明确引用的Ni陈述不猜补来源。
- citation-0189：精确来源引用按句核对；另有嵌入作者年份表达，匿名fragment无法唯一对应其来源，保留unknown。
- citation-0193：具体来源逐片段核对；作者年份Pastor引用与匿名来源无确定身份映射，记未覆盖unknown。无引用独立表格复述句不配对。
- citation-0196：句内与句末引用关系可确定，但文档级引用无法唯一映射至具体片段；保留原引用标识。
- citation-0206：句末引用关系可定位，但文档级引用到多个片段的映射未被冻结规则覆盖。
- citation-0211：合并引用片段逐个评估；错误来源标识按原文invalid保留；句内作者年份到片段映射未覆盖。
- citation-0216：精确Source引用按句定位，内嵌作者年份的片段映射规则未覆盖。
- citation-0217：引用只归其所在句；作者年份到片段映射未知。
- citation-0221：句末来源仅关联同句；作者年份未覆盖唯一来源映射规则，登记unknown而不猜测。
- citation-0223：同句所有声明均与各引用关联；省略offset且chunk重复不能猜测片段，登记unknown。
- citation-0226：逐次提取doc-only引用；多片段文档映射规则未覆盖，保留文档标识并unknown。
- citation-0227：按原文保留裸文档hash引用；多片段映射未覆盖，unknown；同句关联。
- citation-0231：来源tuple独立片段判断；作者年份映射未覆盖登记unknown。
- citation-0233：解析原文所有引用形式；数字与作者年份映射未覆盖，unknown。
- citation-0235：保留固定复合claim；来源与作者年份分别配对，同句全范围；作者年份映射未覆盖。
- citation-0238：doc-only多片段映射未覆盖；保留原文标识及同句关联，前一独立未引用句不补造引用。
- citation-0245：第一文档唯一定位；其余doc-only引用多片段无法消歧，标记冻结规则未覆盖。最后独立总结句没有引用。
- citation-0250：结构化来源按精确片段判断；作者年份引用的唯一映射未覆盖，保留unknown。
- citation-0258：doc-only多片段唯一映射未被冻结规则覆盖，保留unknown与原始文档标识。
- citation-0264：结构化引用按片段独立判断；作者年份无唯一映射保留unknown。
- citation-0267：文档级引用无法唯一解析片段，保留原标识并登记未覆盖情形。
- citation-0271：逐片段独立判断；数字参考号[4]无冻结映射，登记未覆盖提取情形。
- citation-0274：结构化引用可解析，作者年份引用无唯一映射，登记未覆盖情形。
- citation-0275：逐片段判断；缺字段元组保留invalid，作者年份无唯一映射登记unknown。
- citation-0277：保留原文档标识，登记文档级引用无法唯一绑定片段的提取边界。
- citation-0281：描述性来源引用没有可唯一解析的冻结source，登记未覆盖提取情形。
- citation-0282：句内两引用关联同句固定主张；数字参考号无唯一映射，登记未覆盖情形。
- citation-0283：结构化引用逐句判断，作者年份引用无映射登记未覆盖情形。
- citation-0287：结构化引用逐片段判断；作者年份引用无映射登记未覆盖情形。
- citation-0290：显式元组可定位；作者年份引用无法唯一定位。
- citation-0291：逐句处理；作者年份引用没有唯一片段映射。
- citation-0292：逐次计数重复引用；作者年份映射不唯一。
- citation-0293：元组引用可定位；作者年份引用无唯一映射。
- citation-0295：重复显式引用按原文出现次数处理；作者年份无唯一映射。
- citation-0310：两个描述性引用来源均无法唯一定位。
- citation-0311：原回答只有此作者年份引用，没有明确片段元组。
- citation-0312：两个句尾文档级引用均不能唯一映射片段。
- citation-0313：显式作者年份引用无法唯一映射到来源；其余无引用句不产生配对。
- citation-0315：完整来源元组可定位；文献编号[25]无法唯一映射。
- citation-0316：保留每个描述式引用及其句内claims；来源定位含省略而无法唯一确定。
- citation-0318：compound引用中chunk可唯一定位，abstract描述保留unknown；引用归所在句。
- citation-0323：元组来源逐片段判断；未解析文献编号保留unknown；不把句末引用扩展到前一句。
- citation-0324：保留九次文档级引用与各自句内claims，片段定位真实歧义。
- citation-0325：完整元组逐片段判断；作者年份引用保留unknown。
- citation-0326：chunk唯一时按所引片段判断；同chunk多区间保留unknown，不借相邻或修复错引。
- citation-0329：四次文档级引用逐句保留，片段定位有歧义。
- citation-0331：仅单片段文档可唯一定位，其他文档引用保留unknown。
- citation-0333：句内引用逐来源判断，作者年份保留unknown。
- citation-0340：完整来源标识可定位；内嵌作者年份引用无唯一映射。
- citation-0345：内嵌作者年份引用无法唯一映射；显式来源按同句精确片段判定。
- citation-0350：作者年份引用无唯一映射；显式完整来源逐片段判定，损坏来源保持原样invalid。
- citation-0351：两处描述性来源引用不能映射到唯一冻结片段。
- citation-0353：引用句归属可识别；文档级引用对应多个片段，片段归属未被规则覆盖，保留来源原标识并记 unknown。无引用的后续比较不补配。
- citation-0356：Sentence-end citations belong to those sentences. First two document-only citations have unresolved fragment attribution; the third uniquely matches B5-F1.
- citation-0366：Sentence attribution is clear. Section-level document citations do not uniquely name a fragment; preserve identifier and unknown rather than choose a favorable piece.
- citation-0375：实际引用均只给文档标识，且对应多个片段；片段级归属规则未覆盖，按 F6 记录 unknown。
- citation-0382：规则未覆盖文档级标识在多个片段中的唯一归属，按 F6 记录。首句无引文不补配。
- citation-0389：规则未覆盖仅chunk标识遇到同chunk多范围的归属，按 F6 记录 unknown。无引文邻句不补配。
- citation-0398：F6 未覆盖情况：所有实际引用均只给文档级标识，context有多个片段，不自行选择片段；记unknown。首句未引用。
- citation-0403：F6未覆盖：文档级标识不能唯一定位source_fragments，实际配对保留unknown；总结段未引用。
- citation-0416：F6未覆盖：文档级多片段标识无法唯一归属，实际配对unknown；未引用句不生成配对。
- citation-0417：F6未覆盖：来源只写小节名，对应多个片段，保留unknown。同行末引用仅归当前句；前句c2及c6/c7未引用。
- citation-0418：F6未覆盖：551文档缩略引用对应多片段，不选择片段；579缩略标识在context唯一。同句引用各归c14/c15。
- citation-0420：F6未覆盖：文档级标识对应多个来源片段，不自行选择；第一句无引用。
- citation-0436：未覆盖情形：所有实际引用均仅文档标识而context有该文档多个片段；保留引用和来源原标识，不能唯一确定fragment，记unknown并登记run-notes。三人组量化句无引用。
- citation-0438：未覆盖情形：仅文档级标识对应多个片段，无法确定fragment，不猜补；逐句保留配对并登记run-notes。三人组量化句无引用。
- citation-0449：未覆盖格式：文档级标识在当前context匹配多个片段，保留原标识并unknown；唯一片段引用正常判断。
- citation-0458：未覆盖格式：同一文档级标识匹配多个context片段，保留原标识并unknown，不靠内容猜选。
- citation-0465：未覆盖格式：两个文档级来源都匹配多个context片段，保留原标识并unknown。
- citation-0474：标题级来源及same article指代不能唯一映射片段。首句c5无引用，不将后句引用移给它。
- citation-0478：两种文档级ID均对应多个片段，保留unknown；关系段首句c35未获引用。
- citation-0494：文档级标识无法唯一对应source_fragments，登记提取不确定。
- citation-0497：六处文档级引用均无法唯一定位片段，保留原标识并登记提取不确定。
- citation-0498：六处文档级引用均不能唯一定位片段，登记提取不确定。
- citation-0514：八处文档级引用均无法唯一对应片段，登记提取不确定。
- citation-0527：555c529、33a4a692、bbdcea416元素均在上下文出现不同范围，引用没有范围，按unknown保留原标识，不用邻接或题意选片段。
- citation-0528：末段另有两处实际引用，但其句内断言不对应固定claims的occurrences；不可新增或改写claims，未建这些对并保留提取不确定，交统一处理。
- citation-0529：逐个识别句内引用；c13所在句无引用。文档标识不能唯一绑定fragment，依F6第3条保留unknown。
- citation-0536：只配对实际有句内引用的claims。两个文档级标识均有多个候选片段，依F6第3条保留unknown。
- citation-0540：识别实际句内引用；未引用的末段不自动配对。文档级片段映射依F6第3条保留unknown。
- citation-0544：c25句无引用；abstract非标准映射按F6第3条unknown，其余明确element引用逐一判断。
- citation-0546：句内引用只归本句；Shi第一句的实验人数及年龄没有实际引用。多片段文档映射依F6第3条保留unknown。
- citation-0547：实际引用及句内归属保留；语义位置名到fragment的映射按F6第3条unknown。
- citation-0550：逐句识别实际引用并分源判断；001dd元素存在两个片段范围而引用未指定范围，登记未知。未引用的差值句不配对。
- citation-0552：可识别四次文档引用，但无法唯一映射到source_fragments；逐句归属后登记未知。
- citation-0554：三次引用可识别，文档级到片段的归属无法唯一确定，登记未知。
- citation-0555：首个文档在本context仅一个片段，其余文档级引用存在多个片段映射；最后两引用同属一个句子，独立配对。
- citation-0560：识别哈希前缀引用并保留重复顺序；多片段文档级映射未覆盖而登记未知，分号两文档分别配对。
- citation-0570：合法五字段元组按片段判断；其余四字段身份改写的映射属于未覆盖情况，登记unknown；保留作者年份引用。
- citation-0577：规则未覆盖作者加章节的语义引用定位；记入运行说明。
- citation-0580：两处变形身份引用规则未覆盖，记录运行说明。
- citation-0587：第三处引用混有可映射标题与身份变形元组，后者保持unknown并记录。
- citation-0599：引用只给文档标识，该文档在本包有多个片段，无法唯一映射；保持 unknown，不从有利片段反推引用。
- citation-0603：首个文档标识仅对应一个片段并支持断言；其余文档标识对应多个片段，无法唯一消歧，保持 unknown。
- citation-0610：两篇文档级引用均对应多个片段，保留 unknown。PW/AR 引用的文档仅一个片段并直接支持相反效应；末尾限制句无对应固定事实断言。
- citation-0625：各文档级标识对应多个片段，无法唯一映射，不选择有利片段；作者年份身份未登记。
- citation-0634：多片段独立判断。第三处含重复哈希的六项元组，映射规则未覆盖，保留unknown；其他元组映射清晰，按对应正文标题数值片段分开判断。
- citation-0635：文档标识均对应多个片段，不能唯一定位；无引用列表条目不补配。
- citation-0640：文档级引用均对应多个片段，保留无法唯一定位；实际作者年份引用身份未登记，不借上下文文献提及构造映射。
- citation-0651：文档级短引用无法唯一定位，保留句内及句末实际引用归属。
- citation-0661：多个文档级引用定位有歧义；唯一片段引用可明确映射。
- citation-0677：九次文档级引用均有多片段映射歧义，不按有利片段消歧。
- citation-0685：文档级引用的多片段映射不能按支持程度消歧。

## 最终机械验证与停止边界

- 执行：在工作包根目录运行 `python validate_citation_responses.py research-citation-r03`；输出 packets=704，valid=704，problems=0，first_problems=[]。
- manifest index严格为citation-0001至citation-0704；4个上下文各176包，范围连续且互不重叠，恰好覆盖704包一次；responses目录704个JSON，无缺失或额外文件。
- 全部704个packet文件字节SHA-256与manifest登记值一致。
- 初次manifest显示截断已记；恢复后机器完整读取原manifest，核对全部index及每项文件SHA；可视化补读原文[0,20000)。此前计划逐字符显示剩余manifest未执行；完整显示要求针对待判断的包，manifest用于机械目录定位，不含本轮判断输入。未把该manifest的可视化覆盖报告为完整。
- 协调者全部citation-0001至0176逐包处理完成；最终汇总没有复判任何上下文的既有响应。
- 不导入、不评分、不导出次审，也不执行F7分段验收。

## review_0177_0352 运行记录补充

- 实际开始时间：unknown；结束时间：2026-10-08 11:02:02 UTC。
- 允许范围外读取：C:/Users/11315/.codex/skills/using-superpowers/SKILL.md，发生在读取盲包README前。未读取其他研究轮次、校准回答或事实包。
- 首次写citation-0177发生GBK编码错误，文件变更前失败，显式UTF-8后完成。citation-0226后读取manifest误把整数packets当列表，TypeError，无文件修改；随后查看数据类型与index[:1]时只看到citation-0001的manifest元数据，未读其包或回答。
- 初次manifest显示截断，随后完整显示分配范围；0178和0179联合显示截断，随后分别完整重读后判断；0350首次截断，随后按原文件字符前后两半完整显示后判断。
- 上下文压缩共7次，恢复节点在读取0196、0218、0241、0265、0288、0313、0336附近；延续进度，不重判冻结响应。
- 协调者仅在汇总阶段请求以上运行记录，报告三处机械修正与全量校验结果；没有下发判断规则或要求复判。

## 已写入后发现的潜在问题：协调者

- citation-0153：c14与B3-F1的已冻结supported配对，完整条件是否充分支持可能需要后续负责会话排查；这里只记录疑点，响应、标签及配对保持不变。

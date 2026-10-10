# 行为字段澄清 r02（校准 cgpt-r01 后补充；不改变其他任何规则）

unsupported_completion 只用于以下情形：context 对必要结论存在缺口（answerability 为 partial 或 none），回答却用 context 不支持的内容补齐了这一缺口，给出完整结论；即使加了“可能”等限定词，也照此记录。

如果 context 已完整支持必要结论（answerability 为 complete），回答中的错误数值、与 context 矛盾的断言或缺乏支持的断言，属于 grounding 的 contradicted／unsupported，在 behavior 包中 unsupported_completion 记为 false。纯拒答（pure_abstain）和明确指出缺口且未补齐的受限回答（bounded_partial）同样记为 false。

# PEARL Retrieval：阶段 C 公开发布记录

*完整冻结、独立导出前核验与真实入口门禁 · status: current · 2026-10-03*

阶段 C 已生成完整真实 release 和 query-only contract，并由现有 `runtime.py --verify-release-only` 实际核验通过。实际检索查询数为0，模型 forward 未执行；本记录不代表阶段 D 评价完成。完整独立发布复核以[审查目录](../../outputs/pearl-retrieval-eval200-audit-20261003-01/stage-C-preexport-review.json)及后续 final 审查为准。

| 公开身份 | SHA-256／计数 |
| --- | --- |
| [导出前候选](../../outputs/pearl-retrieval-eval200-release-20261003-03/preexport-inputs-verified.json) | `8ece8581c82e81dd410c345398c6df8ef66be1e2a529860b29e21b0c0d6622a7`；16,982实际文件 |
| [独立导出前审查](../../outputs/pearl-retrieval-eval200-audit-20261003-01/stage-C-preexport-review.json) | `f19595cd7b9e14f3393fbbcb7649cf8771612204b217e7637a44e97d495ad043`；passed |
| [最终 release](../../outputs/pearl-retrieval-eval200-release-20261003-03/release.json) | `f42c1c25dab4f7662a3b464fb519844feb4016ad26ff697591c336ef25ee7e2d`；16,986实际文件 |
| [query-only contract](../../outputs/pearl-retrieval-eval200-release-20261003-03/query-only/contract.json) | `8cd3af363f558f9930ef530fad8e821d2c929acff22ec0567ff4dc94b5591327` |
| [query-only queries](../../outputs/pearl-retrieval-eval200-release-20261003-03/query-only/queries.jsonl) | `c5163adb96b993cd6f5873883838919cbf6f9d6a9e19ea5c0a1adc36e7e69e38`；200行，仅 intent_id/query |
| [实际入口门禁](../../outputs/pearl-retrieval-eval200-release-20261003-03/gate-verification/release-gate.json) | passed；16,986文件、完整输入与方法核验 |
| 封存 byte hash＋只读 | 200文件；导出前与门禁后均核验 |
| 固定资产与设计 | 106来源、6,433 child；四类各50题；5开发预热；seed=20260929 |

最终 release 覆盖 protocol3、statistics1、code57、method2、model19、index12、child1、source215、view14、dependencies16,662。依赖包含所有环境安装版本与 METADATA／RECORD／WHEEL，以及五核心依赖全部实际非缓存文件；实际模型／index／PDF／CanonicalDocument逐项核验。开发 r02及选择／映射／评分／delivery、阶段 B delivery 与全部封存文件以不透明 SHA 外部绑定，不提供旧判断正文给执行者或评审者。

预热按原冻结方法，将80道开发 query 用固定seed打乱后取前5；预热答案不导出。导出由独立保管者仅通过既有 custody 接口完成，[增强导出收据](../../outputs/pearl-retrieval-eval200-release-20261003-03/enhanced-export-receipt.json)绑定候选SHA、角色、时间与三份视图SHA。最终 manifest 的独立外部pin与门禁命令／退出码另见[pin](../../outputs/pearl-retrieval-eval200-release-20261003-03/release-pin.json)、[命令收据](../../outputs/pearl-retrieval-eval200-release-20261003-03/gate-command-receipt.json)、[追加身份收据](../../outputs/pearl-retrieval-eval200-release-20261003-03/stage-C-public-binding-receipt.json)。

01目录因 PowerShell硬件JSON默认GBK解码失败而保留[失败收据](../../outputs/pearl-retrieval-eval200-release-20261003-01/stage-C-preparation-failure.json)；02因初稿预热采用未打乱前5开发题而保留[拒绝收据](../../outputs/pearl-retrieval-eval200-release-20261003-02/stage-C-preexport-rejection.json)，进程停止且未导出评估查询。03重新准备并绑定两份收据，没有覆盖旧文件，也未修改阶段 B。

共享Windows账号没有OS ACL安全隔离。当前流程依赖独立Agent上下文、明确访问范围与query-only subprocess契约；封存原只读属性保留。执行者不得读取Gold内容或执行custody，实际child评审者仅获得后续中性包。完整方法、统计、目标输出、实际命令和解释限制见[预注册](preregistration.md)。后续D报告另新建文档，不追改本次已经绑定的README／预注册／实现或release。

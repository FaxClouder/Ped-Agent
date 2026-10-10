# Layer 4 阶段 B 校准与程序验证

*实际独立校准与固定分母验证 · status: current · 2026-10-04*

合成构造者与实际judge分开。40案例为支持/部分/缺失/冲突各8、纯拒答4、受限4。实际context judge读取answerability、grounding、behavior各40包；独立facts judge读取factuality40包，不接触生成context或expected。

r01全部标签分项一致，但cal31引用作用域配对不一致，整体门禁失败。保留原判断后，在实际C前明确r02：同行紧随句末的citation优先归该句；独立一行的段末citation且无其它引用时归整段，真实歧义unknown。实际context judge重新读取40包并保存r02；不受影响的factuality原行按字节SHA精确复用。

独立compare实际输出r02 passed：抽取40/40、Grounding39/39、Factuality39/39、Citation36/36、answerability40/40、behavior40/40、理由40/40，八类哨兵全过。理由指标包含无理由NA一致性，不是40个天然拒答测量。22项针对性测试通过，覆盖输入隔离、分母、unknown、篡改与独立核验；尚非400真实结果核验。

pre-C-freeze绑定事实r03、校准r02及实验代码/口径；固定原20题C100和D300、seed20261004每第5条D60二审名单在真实标签前保存。平台拒绝第四子线程，新角色不可建立；后续复用角色、保留暴露声明，不称独立模型。context judge工程准备阶段接触009旧定义/score和012部分生成信息；二审未看真实答案、事实或成绩。

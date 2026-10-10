# 输入格式说明 r03（引用重做）
本节只说明本包的输入字段怎么读，不增加、不改变以上任何判断规则。与以上规则所说的有据性包相比，本包有三处不同：

1. `claims` 是已经固定的事实 claims，每条有 `claim_id`、`text`（raw_answer 中的原文）和 `occurrences`（该 claim 在 raw_answer 中的全部 Unicode [start,end) 位置）。本次不抽取、不增删、不拆分、不改写 claims，也不判定 claim 的有据性；citation_pairs 的 `claim_id` 只能取自这里。
2. `source_fragments` 标出 context 中每个来源块及其片段的位置。它是程序从块头机械推算的定位，不是证据，也不是标签；context 原文没有任何改动。
   - 数组中每个元素是一个来源块，按在 context 中出现的顺序编号：`block_id` 为 B1、B2……；`header_span` 是块头 `[Source …]` 那一行（含行末换行）的位置；`body_span` 是块正文的位置。
   - `fragments` 按块头列表的顺序，每个列出的来源对应一个片段：`fragment_id`（如 B2-F3 表示第 2 块的第 3 个片段）；`header_index` 是它在块头列表中的序号（从 1 起）；`source` 是块头中该来源的原样标识（`[doc_id, source_version, element_id, start, end]`，或形如 `S1 | p.1` 的来源标签）；`span` 是该片段正文在 context 中的位置。
   - 同一块内，相邻两个片段之间的空行（`\n\n`）不属于任何片段；首尾相接的片段之间没有分隔。
   - `alignment` 为 `exact` 表示该块的全部片段边界已由程序逐块严格核验；为 `unaligned` 时，该块片段的 `span` 为 null，表示边界无法确定，程序没有推测。
3. 输出只有 `citation_pairs` 和 `citation_extraction_unknown`，格式见下面的 Output format。`source_id` 填被引来源对应的 `fragment_id`。

所有位置都是 context 字符串的 Unicode 码位下标，左闭右开（与 Python 字符串下标相同），不是 UTF-16 单位，也不是字节。context 中可能有补充平面字符（如 emoji），用其他工具计数时位置会错开。位置只用来找到片段文字，输出中不要写任何位置。

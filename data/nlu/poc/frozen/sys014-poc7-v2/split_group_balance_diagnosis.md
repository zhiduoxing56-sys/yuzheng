# sys014-poc7-v1 split group 失衡诊断

## 结论

v1 的极端失衡来自过粗 family 边的传递闭包，而不是随机种子。最大 group `SGRP-2431BE8F1C028D5E` 含 46 条 WINDOW_OPEN positive、12 个 family 和 1 条 TEST_ASSET；该 TEST_ASSET 使整个连通分量强制进入 TEST。另一个 7 条 WINDOW_OPEN positive 的 group 同样由 1 条 TEST_ASSET 锁入 TEST。加上其他小组，最终形成 WINDOW_OPEN positive 的 4/2/54 分布。

问题根因是部分 SYNTHETIC_TEMPLATE family 同时包含多个明显不同的 mechanical signature。v1 将 family 作为无条件 DSU 边，再与 template/mechanical 边传递合并，因此本来可独立切分的不同表达被绑在一起。v2 仅细分这种合成 family；AREA/VALUE/NEGATION 替换相同、只含礼貌词差异或真实 template/mechanical 近重复的样本仍保持同组。

## WINDOW_OPEN positive 所在 v1 groups

| Group | v1 split | WINDOW_OPEN + | 样本 | TEST_ASSET | Family | 过粗 family |
|---|---|---|---|---|---|---|
| SGRP-2431BE8F1C028D5E | TEST | 46 | 46 | 1 | 12 | 11 |
| SGRP-BF75EA8E2E2DA64E | TEST | 7 | 7 | 1 | 2 | 1 |
| SGRP-18E9FA0357678230 | VALIDATION | 2 | 2 | 0 | 1 | 1 |
| SGRP-9D23A4504D14823E | TRAIN | 2 | 2 | 0 | 1 | 1 |
| SGRP-B7A20CDC97D8FECC | TRAIN | 2 | 2 | 0 | 1 | 1 |
| SGRP-87C9211526A52264 | TEST | 1 | 1 | 1 | 1 | 0 |

## TOP 20 largest split groups

| Group | v1 split | 样本 | Family | Mechanical | TEST_ASSET | Intent mentions | positive | negated |
|---|---|---|---|---|---|---|---|---|
| SGRP-2431BE8F1C028D5E | TEST | 46 | 12 | 20 | 1 | WINDOW_OPEN:46 | 46 | 0 |
| SGRP-8CBF557C8582B14A | TRAIN | 28 | 14 | 2 | 0 | WINDOW_SET_POSITION:28 | 28 | 0 |
| SGRP-8B7DE95CF9236F50 | TEST | 13 | 11 | 1 | 7 | DOOR_OPEN:12 | 0 | 12 |
| SGRP-0052BA6609F9A366 | TRAIN | 12 | 4 | 1 | 0 | ACCELERATE:12 | 0 | 12 |
| SGRP-0709559FB79D95EA | TRAIN | 12 | 4 | 1 | 0 | WINDOW_SET_POSITION:12 | 0 | 12 |
| SGRP-13B9FD767820D865 | TRAIN | 12 | 4 | 1 | 0 | DOOR_CLOSE:12 | 0 | 12 |
| SGRP-18F5F0DBA0703F1D | TRAIN | 12 | 4 | 5 | 0 | DOOR_OPEN:12 | 12 | 0 |
| SGRP-762CC8D610C5DEBD | TRAIN | 12 | 4 | 1 | 0 | BRAKE:12 | 0 | 12 |
| SGRP-EAB30C61D9C090CA | TRAIN | 12 | 4 | 1 | 0 | HEADLIGHT_OFF:12 | 0 | 12 |
| SGRP-678219EF1166359F | TRAIN | 10 | 5 | 2 | 0 | WINDOW_SET_POSITION:10 | 10 | 0 |
| SGRP-C766A58C35D04324 | TRAIN | 10 | 5 | 2 | 0 | WINDOW_SET_POSITION:10 | 10 | 0 |
| SGRP-F89B2294E0D60548 | TRAIN | 10 | 6 | 2 | 0 | WINDOW_SET_POSITION:10 | 10 | 0 |
| SGRP-D086627A14E374E6 | TRAIN | 9 | 3 | 5 | 0 | DOOR_OPEN:9 | 9 | 0 |
| SGRP-BF75EA8E2E2DA64E | TEST | 7 | 2 | 6 | 1 | WINDOW_OPEN:7 | 7 | 0 |
| SGRP-24891B1206D55954 | VALIDATION | 6 | 2 | 5 | 0 | HEADLIGHT_OFF:6 | 6 | 0 |
| SGRP-27B0F16CF2552554 | TRAIN | 6 | 2 | 5 | 0 | DOOR_OPEN:6 | 6 | 0 |
| SGRP-4AB472732A41649E | TRAIN | 6 | 3 | 4 | 0 | BRAKE:6 | 6 | 0 |
| SGRP-525EF0E83A317075 | TRAIN | 6 | 2 | 3 | 0 | DOOR_CLOSE:6 | 6 | 0 |
| SGRP-613B86C511231CFD | TRAIN | 6 | 2 | 3 | 0 | DOOR_OPEN:6 | 6 | 0 |
| SGRP-72F025BB201D2C39 | TRAIN | 6 | 2 | 5 | 0 | HEADLIGHT_OFF:6 | 6 | 0 |

## v2 处理原则

- TEST_ASSET 的 source_type、文本、标签和 family 不变。
- 只细分内部包含多个 mechanical signature 的 SYNTHETIC_TEMPLATE family。
- 细分后继续以 refined family、template signature、mechanical signature 构造 DSU；零泄漏优先于比例平衡。
- Safety Gold 不参与诊断后的 split optimization。

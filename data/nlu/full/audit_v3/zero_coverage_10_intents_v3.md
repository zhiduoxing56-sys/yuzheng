# 十个 baseline_v1 零覆盖正式意图审计

| Intent | 公开候选 | canonical候选 | 合同完整候选 | v2正式正样本 | 结论 |
|---|---:|---:|---:|---:|---|
| MIRROR_HEATING_OFF | 5 | 5 | 5 | 0 | 已恢复合同完整候选，但因多意图/语气/复核约束仍不进入正式正样本 |
| SEAT_TILT_SET_ANGLE | 2 | 2 | 0 | 0 | 仅发现缺槽或无法唯一确定的候选，保持零覆盖 |
| MIRROR_SET_ANGLE | 20 | 20 | 0 | 0 | 仅发现缺槽或无法唯一确定的候选，保持零覆盖 |
| SUNROOF_SET_TILT | 3 | 3 | 3 | 1 | 已恢复可进入正式正样本的可靠完整样本 |
| CRUISE_SET_SPEED | 13 | 13 | 4 | 1 | 已恢复可进入正式正样本的可靠完整样本 |
| CRUISE_SET_GAP | 4 | 4 | 4 | 4 | 已恢复可进入正式正样本的可靠完整样本 |
| TURN_INDICATOR_ON | 3 | 3 | 0 | 0 | 仅发现缺槽或无法唯一确定的候选，保持零覆盖 |
| WIPER_SET_SENSITIVITY | 3 | 3 | 1 | 1 | 已恢复可进入正式正样本的可靠完整样本 |
| PARKING_BRAKE_AUTO_APPLY_ENABLE | 5 | 5 | 5 | 3 | 已恢复可进入正式正样本的可靠完整样本 |
| PARKING_BRAKE_AUTO_APPLY_DISABLE | 2 | 2 | 2 | 2 | 已恢复可进入正式正样本的可靠完整样本 |

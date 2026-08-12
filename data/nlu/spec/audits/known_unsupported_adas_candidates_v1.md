# Known-Unsupported ADAS Candidates v1

- Candidate count: **127**
- Registry auto-inclusion: **PROHIBITED**

## 1. `ADAS_CANDIDATE_E3B0C44298_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启用']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_E3B0C44298 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18821:意图2` — 配置近距离预防性制动功能并启用

## 2. `ADAS_CANDIDATE_7949134A41_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `中距离前向碰撞预警`
- MAC 子功能: `中距离前向碰撞预警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_7949134A41 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15506:意图1` — 打开中距离前向碰撞预警

## 3. `ADAS_CANDIDATE_093D11B80D_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交叉路口碰撞预警`
- MAC 子功能: `交叉路口碰撞预警`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_093D11B80D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7677:意图1` — 关闭交叉路口碰撞预警

## 4. `ADAS_CANDIDATE_C5C166D3AC_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_C5C166D3AC + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17701:意图1` — 交通信号灯控制功能开启

## 5. `ADAS_CANDIDATE_769E9835B3_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `交通提示灯`
- MAC 操作: `['调整为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_769E9835B3 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:279:意图1` — 交通提示灯调整为显示

## 6. `ADAS_CANDIDATE_32E7F5C690_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `交通灯提示`
- MAC 操作: `['调整为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_32E7F5C690 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17136:意图1` — 交通灯提示调整为震动模式

## 7. `ADAS_CANDIDATE_32E7F5C690_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `交通灯提示`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_32E7F5C690 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13446:意图1` — 把交通灯功能打开

## 8. `ADAS_CANDIDATE_32E7F5C690_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `交通灯提示`
- MAC 操作: `['启动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_32E7F5C690 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12723:意图1` — 启动交通灯提示震动模式

## 9. `ADAS_CANDIDATE_530E1DB188_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `交通灯提醒`
- MAC 操作: `['调整']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_530E1DB188 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1909:意图1` — 调整交通灯提醒设置

## 10. `ADAS_CANDIDATE_7AAC8F78FD_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `交通灯辅助`
- MAC 操作: `['修改', '调整为']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_7AAC8F78FD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15954:意图1` — 把交通灯辅助调整为近
- `train_set.jsonl:1930:意图1` — 修改交通灯辅助为中距离

## 11. `ADAS_CANDIDATE_7AAC8F78FD_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `交通灯辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_7AAC8F78FD + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19736:意图1` — 打开近距离交通灯辅助
- `train_set.jsonl:19114:意图1` — 打开近距离交通灯辅助设置
- `train_set.jsonl:3186:意图1` — 打开中等距离交通灯辅助界面

## 12. `ADAS_CANDIDATE_6272FD9952_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `红灯制动`
- MAC 操作: `['关了']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_6272FD9952 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12185:意图1` — 红灯制动辅助功能坏了关了吧

## 13. `ADAS_CANDIDATE_6272FD9952_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `红灯制动`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_6272FD9952 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9289:意图1` — 让红灯制动辅助帮助我驾驶

## 14. `ADAS_CANDIDATE_36138FDED1_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `红灯制动辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **4**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_36138FDED1 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15871:意图1` — 打开远距离红灯制动辅助设置页面
- `train_set.jsonl:1749:意图1` — 打开远距离红灯制动辅助设置
- `train_set.jsonl:3582:意图1` — 打开近距离红灯制动辅助设置页面
- `train_set.jsonl:9992:意图1` — 打开中等距离红灯制动辅助

## 15. `ADAS_CANDIDATE_C927577228_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `超速报警`
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_C927577228 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7580:意图1` — 将超速报警下降二十五档

## 16. `ADAS_CANDIDATE_C927577228_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `超速报警`
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_C927577228 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3176:意图1` — 超速报警设置为最小值

## 17. `ADAS_CANDIDATE_C927577228_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `超速报警`
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_C927577228 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14052:意图1` — 超速的时候通过震动提醒我

## 18. `ADAS_CANDIDATE_C927577228_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `超速报警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_C927577228 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1093:意图1` — 我希望在我超速的时候能够提醒我

## 19. `ADAS_CANDIDATE_801AD55206_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `超速提醒`
- MAC 操作: `['调整为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_801AD55206 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15754:意图1` — 把超速提醒调整为显示

## 20. `ADAS_CANDIDATE_801AD55206_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `超速提醒`
- MAC 操作: `[]`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_801AD55206 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6684:意图1` — 超速提醒我

## 21. `ADAS_CANDIDATE_9D1D33ECA6_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `超速限制`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_9D1D33ECA6 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3520:意图1` — 打开超速限制

## 22. `ADAS_CANDIDATE_F4B48C4E55_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志`
- MAC 子功能: `限速报警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_F4B48C4E55 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10103:意图1` — 打开限速报警灵敏度页面

## 23. `ADAS_CANDIDATE_E683301BBB_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通标志识别`
- MAC 子功能: `交通标志识别`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_E683301BBB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7323:意图1` — 打开交通标志识别

## 24. `ADAS_CANDIDATE_32E7F5C690_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通灯提示`
- MAC 子功能: `交通灯提示`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_32E7F5C690 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16543:意图1` — 打开交通灯提示功能

## 25. `ADAS_CANDIDATE_530E1DB188_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通灯提醒`
- MAC 子功能: `交通灯提醒`
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_530E1DB188 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11912:意图1` — 设置交通灯提醒

## 26. `ADAS_CANDIDATE_530E1DB188_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通灯提醒`
- MAC 子功能: `交通灯提醒`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_530E1DB188 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10749:意图1` — 打开交通灯提醒

## 27. `ADAS_CANDIDATE_E6A4A204CE_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `低速倒车紧急制动`
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_E6A4A204CE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:848:意图1` — 关闭低速倒车紧急制动
- `train_set.jsonl:1812:意图1` — 低速倒车紧急制动影响我操作把它关了
- `train_set.jsonl:7381:意图1` — 设置低速倒车紧急制动为停用状态

## 28. `ADAS_CANDIDATE_DBD0D64E42_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `侧边距离报警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_DBD0D64E42 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18019:意图1` — 打开侧边距离报警

## 29. `ADAS_CANDIDATE_6C38EF4DF9_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `后向横穿`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_6C38EF4DF9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7816:意图1` — 打开后向横穿

## 30. `ADAS_CANDIDATE_2EB56D090C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `后向目标横穿预警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_2EB56D090C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13857:意图1` — 打开后向目标横穿预警

## 31. `ADAS_CANDIDATE_750151CC2C_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `后向碰撞减缓`
- MAC 操作: `['关掉']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_750151CC2C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9632:意图1` — 把后向碰撞减缓关掉

## 32. `ADAS_CANDIDATE_750151CC2C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `后向碰撞减缓`
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_750151CC2C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13869:意图1` — 打开后向碰撞减缓
- `train_set.jsonl:7298:意图1` — 把后向碰撞减缓调节为可用

## 33. `ADAS_CANDIDATE_5601A37BF0_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `后方交通穿行提示`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_5601A37BF0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13327:意图1` — 关闭后方交通穿行提示

## 34. `ADAS_CANDIDATE_65ED614642_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `后方横向来车制动`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_65ED614642 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:420:意图1` — 关闭后方横向来车制动页面

## 35. `ADAS_CANDIDATE_6A30D6D38A_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `后方横向来车预警`
- MAC 操作: `['切换成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_6A30D6D38A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15716:意图1` — 后方横向来车预警切换成声音

## 36. `ADAS_CANDIDATE_A06FCBA84C_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `后方碰撞预警`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_A06FCBA84C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13684:意图1` — 关闭后方碰撞预警

## 37. `ADAS_CANDIDATE_A06FCBA84C_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `后方碰撞预警`
- MAC 操作: `['换成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_A06FCBA84C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10172:意图1` — 后方碰撞预警换成预警制动

## 38. `ADAS_CANDIDATE_AFCC7C2C3B_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `后碰撞警告`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_AFCC7C2C3B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7308:意图1` — 关闭后碰撞警告

## 39. `ADAS_CANDIDATE_3C556ECF09_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `侧后辅助`
- MAC 子功能: `门开预警功能`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_3C556ECF09 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19803:意图1` — 门开预警功能关闭

## 40. `ADAS_CANDIDATE_8B1774ABE0_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_8B1774ABE0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9685:意图1` — 设置后方交叉路口来车预警为开启

## 41. `ADAS_CANDIDATE_C3208173FF_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `前向碰撞预警`
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_C3208173FF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19808:意图1` — 把前向碰撞预警改为关闭
- `test_set.jsonl:222:意图1` — 关闭前向碰撞预警
- `train_set.jsonl:11436:意图1` — 设置前向碰撞预警在关闭状态

## 42. `ADAS_CANDIDATE_C3208173FF_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `前向碰撞预警`
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_C3208173FF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20537:意图1` — 更改前向碰撞预警为打开状态
- `train_set.jsonl:4599:意图1` — 把前向碰撞预警改为开启

## 43. `ADAS_CANDIDATE_C3208173FF_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `前向碰撞预警`
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_C3208173FF + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1249:意图1` — 打开中等距离前向碰撞预警页面
- `train_set.jsonl:4708:意图1` — 打开中等距离前向碰撞预警

## 44. `ADAS_CANDIDATE_C3208173FF_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `前向碰撞预警`
- MAC 操作: `['进行']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_C3208173FF + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14805:意图1` — 现在进行前向碰撞预警程序

## 45. `ADAS_CANDIDATE_81C544DD67_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `前方侧向交通辅助`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_81C544DD67 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14064:意图1` — 关闭前方侧向交通辅助

## 46. `ADAS_CANDIDATE_37A9E6F471_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `前方横向碰撞`
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `SET + ADAS_CANDIDATE_37A9E6F471 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3567:意图1` — 前方横向碰撞设置为预警加制动

## 47. `ADAS_CANDIDATE_FAD30A9780_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `前方碰撞预警`
- MAC 操作: `['换成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_FAD30A9780 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12578:意图1` — 前方碰撞预警换成预警加制动

## 48. `ADAS_CANDIDATE_7E17A1EEAD_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `前碰撞预警`
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `SET + ADAS_CANDIDATE_7E17A1EEAD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:19131:意图1` — 前碰撞预警适中

## 49. `ADAS_CANDIDATE_63B5036A00_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `后交叉路口辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_63B5036A00 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2625:意图1` — 后面交叉路有车的情况下提醒我

## 50. `ADAS_CANDIDATE_1DE46E24A5_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `后方侧向交通辅助`
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_1DE46E24A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19686:意图1` — 把后方侧向交通辅助调节为可用
- `test_set.jsonl:993:意图1` — 调整后方侧向交通辅助为开启
- `train_set.jsonl:4420:意图1` — 将后方侧向交通辅助调至开启状态

## 51. `ADAS_CANDIDATE_75B56915F2_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `碰撞辅助`
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_75B56915F2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9945:意图1` — 开启碰撞辅助

## 52. `ADAS_CANDIDATE_580C583A00_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `近距离前向碰撞预警`
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `SET + ADAS_CANDIDATE_580C583A00 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2084:意图1` — 近距离前向碰撞预警设置

## 53. `ADAS_CANDIDATE_AA11E24013_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `近距离预防性制动`
- MAC 操作: `['配置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_AA11E24013 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18821:意图1` — 配置近距离预防性制动功能并启用

## 54. `ADAS_CANDIDATE_64B9A4B52D_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `预测性紧急碰撞预警`
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `SET + ADAS_CANDIDATE_64B9A4B52D + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5704:意图1` — 预测性紧急碰撞预警设置为较早

## 55. `ADAS_CANDIDATE_438921C346_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `预防性制动`
- MAC 操作: `['设置', '调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `SET + ADAS_CANDIDATE_438921C346 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14313:意图1` — 设置预防性制动
- `train_set.jsonl:14941:意图1` — 调节预防性制动设置

## 56. `ADAS_CANDIDATE_438921C346_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `预防性制动`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_438921C346 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3082:意图1` — 调节预防性制动赶紧帮我把它打开

## 57. `ADAS_CANDIDATE_438921C346_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `预防性制动`
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_438921C346 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10783:意图1` — 打开中等距离预防性制动设置界面
- `train_set.jsonl:8119:意图1` — 打开中等距离预防性制动界面

## 58. `ADAS_CANDIDATE_BAC5152530_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向辅助`
- MAC 子功能: `预防性刹车距离`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_BAC5152530 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17267:意图1` — 关闭预防性刹车距离

## 59. `ADAS_CANDIDATE_854DC8134E_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `变道辅助`
- MAC 子功能: `变道辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_854DC8134E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13818:意图1` — 打开变道辅助开关

## 60. `ADAS_CANDIDATE_C26F45A9F6_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `城市智能领航辅助`
- MAC 子功能: `城市智能领航辅助`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_C26F45A9F6 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12197:意图1` — 关闭城市智能领航辅助

## 61. `ADAS_CANDIDATE_C26F45A9F6_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `城市智能领航辅助`
- MAC 子功能: `城市智能领航辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_C26F45A9F6 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5415:意图1` — 打开城市智能领航辅助页面

## 62. `ADAS_CANDIDATE_BC18DDE260_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `城市领航辅助功能`
- MAC 子功能: `城市领航辅助功能`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_BC18DDE260 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6425:意图1` — 打开城市领航辅助功能

## 63. `ADAS_CANDIDATE_2898E34878_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `我要把自适`
- MAC 子功能: `自动变道提醒`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_2898E34878 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1012:意图1` — 我要把自适应巡航设成禁止给我设一下

## 64. `ADAS_CANDIDATE_2964E66FAE_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `手动变道辅助`
- MAC 子功能: `手动变道辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_2964E66FAE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8678:意图1` — 打开手动变道辅助

## 65. `ADAS_CANDIDATE_2D693C5390_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `智慧巡航`
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['CRUISE_DISABLE', 'CRUISE_ENABLE', 'CRUISE_SET_GAP', 'CRUISE_SET_SPEED']`
- 建议三元组: `SET + ADAS_CANDIDATE_2D693C5390 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6434:意图1` — 设置驾驶辅助距离为2档

## 66. `ADAS_CANDIDATE_2898E34878_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `智慧巡航`
- MAC 子功能: `自动变道提醒`
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `True` `['CRUISE_DISABLE', 'CRUISE_ENABLE', 'CRUISE_SET_GAP', 'CRUISE_SET_SPEED', 'LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_2898E34878 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:320:意图1` — 为我提供自动变道提醒服务
- `train_set.jsonl:19055:意图1` — 把自动变道提醒改为开启
- `train_set.jsonl:9464:意图1` — 自动变道提醒可以避免危险为我开启它

## 67. `ADAS_CANDIDATE_F3FF1F12FA_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `智慧巡航`
- MAC 子功能: `辅助驾驶播报`
- MAC 操作: `['切换为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['CRUISE_DISABLE', 'CRUISE_ENABLE', 'CRUISE_SET_GAP', 'CRUISE_SET_SPEED']`
- 建议三元组: `SET + ADAS_CANDIDATE_F3FF1F12FA + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1649:意图1` — 驾驶辅助语音播报切换为精简模式

## 68. `ADAS_CANDIDATE_8D26FB1B9D_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `智慧巡航`
- MAC 子功能: `驾驶辅助`
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['CRUISE_DISABLE', 'CRUISE_ENABLE', 'CRUISE_SET_GAP', 'CRUISE_SET_SPEED']`
- 建议三元组: `SET + ADAS_CANDIDATE_8D26FB1B9D + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4947:意图1` — 驾驶辅助距离调到最小

## 69. `ADAS_CANDIDATE_C35FEA888C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `盲区提醒`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_C35FEA888C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9169:意图1` — 打开盲区提醒

## 70. `ADAS_CANDIDATE_3DFBD1F2CF_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `盲区检测`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_3DFBD1F2CF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:151:意图1` — 关闭盲区检测

## 71. `ADAS_CANDIDATE_30AFBC322A_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `盲区检测预警功能`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_30AFBC322A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10791:意图1` — 盲区检测预警功能打开

## 72. `ADAS_CANDIDATE_1472D60246_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `盲区监测`
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_1472D60246 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:476:意图1` — 开启盲区监测

## 73. `ADAS_CANDIDATE_04AB26D146_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `盲区监测预警`
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_04AB26D146 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19200:意图1` — 盲区监测预警设置为灯

## 74. `ADAS_CANDIDATE_72DE69BA21_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `盲区预警`
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_72DE69BA21 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18798:意图1` — 设置盲区预警

## 75. `ADAS_CANDIDATE_72DE69BA21_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `盲区预警`
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_72DE69BA21 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19941:意图1` — 震动的效果好一些用震动来提示我盲区预警
- `train_set.jsonl:15688:意图1` — 把震动作为盲区预警的提示效果

## 76. `ADAS_CANDIDATE_72DE69BA21_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `盲区预警`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_72DE69BA21 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16213:意图1` — 我现在不需要盲区预警提醒我
- `train_set.jsonl:4425:意图1` — 盲区预警这个功能可以关闭了

## 77. `ADAS_CANDIDATE_72DE69BA21_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `盲区预警`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_72DE69BA21 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12852:意图4` — 打开盲区预警
- `train_set.jsonl:3801:意图1` — 打开盲区预警的设置窗口给我设置
- `train_set.jsonl:6641:意图1` — 打开盲区预警

## 78. `ADAS_CANDIDATE_72DE69BA21_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `盲区预警`
- MAC 子功能: ``
- MAC 操作: `['设']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_72DE69BA21 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18137:意图1` — 盲区预警的提示效果设为震动

## 79. `ADAS_CANDIDATE_3E73151B81_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `紧急制动`
- MAC 子功能: `紧急制动`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_3E73151B81 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13961:意图2` — 关闭紧急制动

## 80. `ADAS_CANDIDATE_30295528A5_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `自主变道辅助`
- MAC 子功能: `自主变道辅助`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_30295528A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7282:意图1` — 关闭自主变道辅助

## 81. `ADAS_CANDIDATE_2898E34878_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `自动变道提醒`
- MAC 子功能: `自动变道提醒`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_2898E34878 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5658:意图1` — 关闭自动变道提醒

## 82. `ADAS_CANDIDATE_2898E34878_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `自动变道提醒`
- MAC 子功能: `自动变道提醒`
- MAC 操作: `['退出']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_2898E34878 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20526:意图1` — 退出自动变道提醒

## 83. `ADAS_CANDIDATE_2898E34878_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `自适应巡航`
- MAC 子功能: `自动变道提醒`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['CRUISE_DISABLE', 'CRUISE_ENABLE', 'CRUISE_SET_GAP', 'CRUISE_SET_SPEED', 'LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_2898E34878 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5819:意图1` — 自适应巡航这个功能可以关闭了

## 84. `ADAS_CANDIDATE_801AD55206_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `超速提醒`
- MAC 子功能: `超速提醒`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_801AD55206 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11425:意图1` — 关闭超速提醒

## 85. `ADAS_CANDIDATE_801AD55206_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `超速提醒`
- MAC 子功能: `超速提醒`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_801AD55206 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18028:意图1` — 打开超速提醒

## 86. `ADAS_CANDIDATE_1E745FE8C2_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车辆盲区预警监测`
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_1E745FE8C2 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9065:意图1` — 设置车辆盲区预警监测

## 87. `ADAS_CANDIDATE_FC919D5C35_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道偏离报警`
- MAC 子功能: `车道偏离报警`
- MAC 操作: `['调整为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `SET + ADAS_CANDIDATE_FC919D5C35 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2137:意图1` — 把车道偏离报警调整为震动

## 88. `ADAS_CANDIDATE_FC919D5C35_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道偏离报警`
- MAC 子功能: `车道偏离报警`
- MAC 操作: `['开一开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_FC919D5C35 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4991:意图1` — 帮我开一开车道偏离报警的设置界面

## 89. `ADAS_CANDIDATE_93186A7B9A_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `SET + ADAS_CANDIDATE_93186A7B9A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19248:意图1` — 车道辅助预警方式设置为声音加震动
- `train_set.jsonl:1354:意图1` — 车道辅助预警方式设置为震动

## 90. `ADAS_CANDIDATE_93186A7B9A_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **4**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_93186A7B9A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15578:意图1` — 关闭车道偏离警告
- `train_set.jsonl:4095:意图1` — 关闭车道辅助保持
- `train_set.jsonl:5427:意图1` — 关闭车道偏离抑制
- `train_set.jsonl:8078:意图1` — 停止车道导向功能

## 91. `ADAS_CANDIDATE_93186A7B9A_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_93186A7B9A + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9116:意图1` — 打开车道偏离纠正

## 92. `ADAS_CANDIDATE_93186A7B9A_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: ``
- MAC 操作: `['开下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_93186A7B9A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7180:意图1` — 我要在这条车道上行驶赶紧帮我开下保持功能

## 93. `ADAS_CANDIDATE_26A658C9FE_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `保持在当前车道`
- MAC 操作: `[]`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_26A658C9FE + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:286:意图1` — 帮我保持在当前车道

## 94. `ADAS_CANDIDATE_3DEA2B8C50_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `偏离车道`
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `SET + ADAS_CANDIDATE_3DEA2B8C50 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3354:意图1` — 偏离车道的时候震动提醒我

## 95. `ADAS_CANDIDATE_29EBD0981F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `偏离车道预警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_29EBD0981F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14068:意图1` — 打开偏离车道预警

## 96. `ADAS_CANDIDATE_3C48F85D7C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `紧急保持车道辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_3C48F85D7C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7587:意图1` — 打开紧急保持车道辅助

## 97. `ADAS_CANDIDATE_23C9567A28_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `维持行驶在当前车道上`
- MAC 操作: `[]`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_23C9567A28 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:472:意图1` — 维持行驶在当前车道上

## 98. `ADAS_CANDIDATE_3F89A4650D_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道保持`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_3F89A4650D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10614:意图1` — 关闭车道保持

## 99. `ADAS_CANDIDATE_51C75038BC_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道保持模式`
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `SET + ADAS_CANDIDATE_51C75038BC + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1046:意图1` — 车道保持模式警示
- `test_set.jsonl:923:意图1` — 车道保持模式仅警示

## 100. `ADAS_CANDIDATE_FB9C7DB91A_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道保持系统`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_FB9C7DB91A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7936:意图1` — 关闭车道保持系统

## 101. `ADAS_CANDIDATE_D4C987F23D_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道保持辅助`
- MAC 操作: `['切换为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `SET + ADAS_CANDIDATE_D4C987F23D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:905:意图1` — 车道辅助形式切换为车道保持辅助

## 102. `ADAS_CANDIDATE_D4C987F23D_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道保持辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_D4C987F23D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12244:意图1` — 打开车道保持辅助

## 103. `ADAS_CANDIDATE_63F2A42356_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道保持辅助系统`
- MAC 操作: `['关了']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_63F2A42356 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13876:意图1` — 关了车道保持辅助系统

## 104. `ADAS_CANDIDATE_63F2A42356_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道保持辅助系统`
- MAC 操作: `['关了一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_63F2A42356 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14966:意图1` — 关了一下车道保持辅助系统

## 105. `ADAS_CANDIDATE_7A97332287_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道偏向预警`
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_7A97332287 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1482:意图1` — 开启车道偏向预警

## 106. `ADAS_CANDIDATE_00646723EC_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道偏差预警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_00646723EC + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8792:意图1` — 打开车道偏差预警

## 107. `ADAS_CANDIDATE_FC919D5C35_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道偏离报警`
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `SET + ADAS_CANDIDATE_FC919D5C35 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5530:意图1` — 调节车道偏离报警

## 108. `ADAS_CANDIDATE_FC919D5C35_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道偏离报警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_FC919D5C35 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4048:意图1` — 打开车道偏离报警

## 109. `ADAS_CANDIDATE_E2CC29209C_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道偏离辅助`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_E2CC29209C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6446:意图1` — 关闭车道偏离辅助

## 110. `ADAS_CANDIDATE_E2CC29209C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道偏离辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_E2CC29209C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2200:意图1` — 打开车道偏离辅助

## 111. `ADAS_CANDIDATE_051E550F20_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道偏离预警`
- MAC 操作: `['切换到', '设置']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `SET + ADAS_CANDIDATE_051E550F20 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:751:意图1` — 设置车道偏离预警
- `train_set.jsonl:18358:意图1` — 车道辅助形式切换到车道偏离预警

## 112. `ADAS_CANDIDATE_C772FEB600_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道引导`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_C772FEB600 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5930:意图1` — 打开车道引导

## 113. `ADAS_CANDIDATE_C772FEB600_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `车道引导`
- MAC 操作: `['停止']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_C772FEB600 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13548:意图1` — 停止车道引导功能

## 114. `ADAS_CANDIDATE_78BCD5893A_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `邻车靠近避让`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_78BCD5893A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20155:意图1` — 关闭邻车靠近避让

## 115. `ADAS_CANDIDATE_78BCD5893A_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道辅助`
- MAC 子功能: `邻车靠近避让`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_78BCD5893A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17797:意图1` — 打开邻车靠近避让

## 116. `ADAS_CANDIDATE_D2185CC7A5_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `转向灯变道辅助`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_D2185CC7A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9728:意图1` — 打开转向灯变道辅助

## 117. `ADAS_CANDIDATE_580C583A00_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `近距离前向碰撞预警`
- MAC 子功能: `近距离前向碰撞预警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_580C583A00 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7457:意图1` — 打开近距离前向碰撞预警

## 118. `ADAS_CANDIDATE_0994407E59_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `限速告警`
- MAC 子功能: `限速告警`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_0994407E59 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15961:意图1` — 关闭限速告警

## 119. `ADAS_CANDIDATE_0994407E59_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `限速告警`
- MAC 子功能: `限速告警`
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_0994407E59 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5164:意图1` — 开启限速告警

## 120. `ADAS_CANDIDATE_5F4901FF1F_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `限速提醒`
- MAC 子功能: `限速提醒`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_5F4901FF1F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10406:意图1` — 关闭限速提醒

## 121. `ADAS_CANDIDATE_5F4901FF1F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `限速提醒`
- MAC 子功能: `限速提醒`
- MAC 操作: `['打开', '打开一下']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_5F4901FF1F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10244:意图1` — 打开限速提醒
- `train_set.jsonl:2569:意图1` — 你把限速提醒开关打开一下

## 122. `ADAS_CANDIDATE_438921C346_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `预防性制动`
- MAC 子功能: `预防性制动`
- MAC 操作: `['关掉']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_438921C346 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8496:意图1` — 把预防性制动功能关掉

## 123. `ADAS_CANDIDATE_438921C346_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `预防性制动`
- MAC 子功能: `预防性制动`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_438921C346 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8349:意图1` — 打开预防性制动

## 124. `ADAS_CANDIDATE_DD635F44ED_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驾驶辅助`
- MAC 子功能: `领航驾驶辅助`
- MAC 操作: `['关了']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + ADAS_CANDIDATE_DD635F44ED + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9476:意图1` — 给我把领航驾驶辅助设置页面关了

## 125. `ADAS_CANDIDATE_8D26FB1B9D_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驾驶辅助`
- MAC 子功能: `驾驶辅助`
- MAC 操作: `[]`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + ADAS_CANDIDATE_8D26FB1B9D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17221:意图1` — 把驾驶辅助界面跳转

## 126. `ADAS_CANDIDATE_506BE15AF1_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `高级驾驶辅助`
- MAC 子功能: `高级驾驶辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + ADAS_CANDIDATE_506BE15AF1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14783:意图1` — 高级驾驶辅助打开

## 127. `ADAS_CANDIDATE_9EFE01F647_SET`

- MAC 对象: `窗口`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + ADAS_CANDIDATE_9EFE01F647 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3801:意图2` — 打开盲区预警的设置窗口给我设置

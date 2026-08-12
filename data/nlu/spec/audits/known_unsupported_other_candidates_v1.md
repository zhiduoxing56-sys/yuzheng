# Known-Unsupported Other Candidates v1

- Candidate count: **1275**
- Registry auto-inclusion: **PROHIBITED**

## 1. `FRUNK_CLOSE`

- MAC 对象: `前备箱/前备厢`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **0**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `CLOSE + FRUNK + OPENING_STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING_NO_REAL_DATA_EVIDENCE**

真实示例：


## 2. `KNOWN_CONTROL_CANDIDATE_2DDE6D03DD_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `ACC`
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2DDE6D03DD + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11238:意图1` — 打开acc
- `train_set.jsonl:6658:意图2` — 开启acc

## 3. `KNOWN_CONTROL_CANDIDATE_53C77EA377_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `NCA`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_53C77EA377 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17511:意图1` — 启用车辆通信系统

## 4. `KNOWN_CONTROL_CANDIDATE_A62A1A15DA_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `三六零`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_A62A1A15DA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19549:意图2` — 关闭三六零关闭音乐
- `train_set.jsonl:8252:意图2` — 关闭三六零

## 5. `KNOWN_CONTROL_CANDIDATE_A62A1A15DA_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `三六零`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A62A1A15DA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1065:意图1` — 打开三六零
- `train_set.jsonl:14216:意图2` — 打开三六零
- `train_set.jsonl:5817:意图1` — 打开三六零
- `train_set.jsonl:7473:意图2` — 打开三六零
- `train_set.jsonl:8656:意图2` — 打开三六零

## 6. `KNOWN_CONTROL_CANDIDATE_C815A229A4_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `三六零全景`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_C815A229A4 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9950:意图2` — 打开三六零全景

## 7. `KNOWN_CONTROL_CANDIDATE_C2A152E46A_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `三六零全景影像`
- MAC 子功能: ``
- MAC 操作: `['我想看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_C2A152E46A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3700:意图1` — 我想看三六零全景影像

## 8. `KNOWN_CONTROL_CANDIDATE_404FACDAD6_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `三六零影像`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_404FACDAD6 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10955:意图1` — 打开三六零影像

## 9. `KNOWN_CONTROL_CANDIDATE_570C208D6F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `下坡行驶辅助`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_570C208D6F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14835:意图1` — 打开下坡行驶辅助

## 10. `KNOWN_CONTROL_CANDIDATE_DB0356DBCC_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `下次维修预约的时间是什么时候`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_DB0356DBCC + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18607:意图1` — 下次维修预约的时间是什么时候

## 11. `KNOWN_CONTROL_CANDIDATE_F1E86B086E_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `主动制动设备`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F1E86B086E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5153:意图1` — 把主动制动设备关闭

## 12. `KNOWN_CONTROL_CANDIDATE_0251D4F186_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `主动恒温`
- MAC 子功能: ``
- MAC 操作: `['关掉']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_0251D4F186 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17232:意图1` — 需要关掉主动恒温

## 13. `KNOWN_CONTROL_CANDIDATE_0251D4F186_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `主动恒温`
- MAC 子功能: ``
- MAC 操作: `['开启一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_0251D4F186 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2788:意图1` — 要开启一下主动恒温

## 14. `KNOWN_CONTROL_CANDIDATE_0251D4F186_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `主动恒温`
- MAC 子功能: ``
- MAC 操作: `['进入', '退出']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_0251D4F186 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11662:意图1` — 退出主动恒温
- `train_set.jsonl:12423:意图1` — 进入主动恒温

## 15. `KNOWN_CONTROL_CANDIDATE_624C0F10E3_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `主动提示`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_624C0F10E3 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12223:意图1` — 关闭语音主动提示

## 16. `KNOWN_CONTROL_CANDIDATE_CAE74D25B9_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `乘员监测系统`
- MAC 子功能: `儿童遗留监测`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_CAE74D25B9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8761:意图1` — 关闭儿童遗留监测

## 17. `KNOWN_CONTROL_CANDIDATE_AD18AFE8DB_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `二氧化碳浓度检测`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_AD18AFE8DB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10834:意图1` — 关闭二氧化碳浓度检测

## 18. `KNOWN_CONTROL_CANDIDATE_3B27CE728D_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `二氧化碳浓度监测`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B27CE728D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11920:意图1` — 二氧化碳浓度监测打开

## 19. `KNOWN_CONTROL_CANDIDATE_C35D44584D_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `交通指示灯提醒`
- MAC 子功能: `交通指示灯提醒`
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C35D44584D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12817:意图1` — 设置交通指示灯提醒

## 20. `KNOWN_CONTROL_CANDIDATE_3C0A5147CE_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `人脸摄像头`
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3C0A5147CE + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7476:意图1` — 设置人脸摄像头

## 21. `KNOWN_CONTROL_CANDIDATE_3C0A5147CE_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `人脸摄像头`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3C0A5147CE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18812:意图1` — 打开人脸摄像头设置
- `train_set.jsonl:2936:意图1` — 打开人脸摄像头设置页面

## 22. `KNOWN_CONTROL_CANDIDATE_E8C92C9F1F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `人脸识别`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E8C92C9F1F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2081:意图1` — 打开人脸识别开关

## 23. `KNOWN_CONTROL_CANDIDATE_A756AD875C_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `什么时候充满电`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A756AD875C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:374:意图1` — 什么时候充满电

## 24. `KNOWN_CONTROL_CANDIDATE_1EEC092A1F_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `仿真声浪`
- MAC 子功能: ``
- MAC 操作: `['暂停']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_1EEC092A1F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4926:意图1` — 仿真声浪暂停

## 25. `KNOWN_CONTROL_CANDIDATE_90B487DC9F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `低速制动`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_90B487DC9F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8251:意图1` — 打开低速制动

## 26. `KNOWN_CONTROL_CANDIDATE_B9AF12B395_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `保养`
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_B9AF12B395 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6568:意图1` — 保养时间设置最小

## 27. `KNOWN_CONTROL_CANDIDATE_B9AF12B395_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `保养`
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_B9AF12B395 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19936:意图1` — 保养里程20千米

## 28. `KNOWN_CONTROL_CANDIDATE_B9AF12B395_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `保养`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_B9AF12B395 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10132:意图1` — 什么时候可以去保养
- `train_set.jsonl:7256:意图1` — 还有多久需要保养
- `train_set.jsonl:7507:意图1` — 我的车多久需要保养

## 29. `KNOWN_CONTROL_CANDIDATE_3DEA189809_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `信号灯自动检测`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3DEA189809 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11601:意图1` — 关闭信号灯自动检测

## 30. `KNOWN_CONTROL_CANDIDATE_3DEA189809_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `信号灯自动检测`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3DEA189809 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3178:意图1` — 打开信号灯自动检测

## 31. `KNOWN_CONTROL_CANDIDATE_BAFDC10803_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `倒车影像`
- MAC 子功能: ``
- MAC 操作: `['取消']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_BAFDC10803 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14622:意图1` — 我想把倒车影像取消

## 32. `KNOWN_CONTROL_CANDIDATE_7DCEAA4DAD_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `倒车降低音乐`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_7DCEAA4DAD + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3884:意图1` — 关闭倒车降低音乐

## 33. `KNOWN_CONTROL_CANDIDATE_BFDB3F23A6_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `停车`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BFDB3F23A6 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8752:意图1` — 关闭停车舒享模式

## 34. `KNOWN_CONTROL_CANDIDATE_BFDB3F23A6_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `停车`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BFDB3F23A6 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1114:意图1` — 停车空调设置为舒适模式
- `train_set.jsonl:17513:意图1` — 停车的时候我需要自动泊车功能来辅助我停车

## 35. `KNOWN_CONTROL_CANDIDATE_BFDB3F23A6_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `停车`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BFDB3F23A6 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19710:意图1` — 打开停车舒享模式
- `train_set.jsonl:2323:意图1` — 打开停车舒享模式

## 36. `KNOWN_CONTROL_CANDIDATE_28751FCCD3_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `停车助手`
- MAC 子功能: ``
- MAC 操作: `['启动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_28751FCCD3 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14952:意图1` — 启动停车助手

## 37. `KNOWN_CONTROL_CANDIDATE_A5D23663FF_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `儿童危险动作检测`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A5D23663FF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8525:意图1` — 打开儿童危险动作检测

## 38. `KNOWN_CONTROL_CANDIDATE_3DAA593FC1_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `全景`
- MAC 子功能: ``
- MAC 操作: `['开启', '开开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3DAA593FC1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11071:意图1` — 开启全景
- `train_set.jsonl:6370:意图1` — 把全景开开

## 39. `KNOWN_CONTROL_CANDIDATE_72DE53576C_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `全景影像`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_72DE53576C + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7988:意图1` — 关闭自动开启全景影像

## 40. `KNOWN_CONTROL_CANDIDATE_72DE53576C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `全景影像`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_72DE53576C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3827:意图5` — 播放一首夜色

## 41. `KNOWN_CONTROL_CANDIDATE_72DE53576C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `全景影像`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_72DE53576C + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10070:意图1` — 打开全景影像的行星视角
- `train_set.jsonl:12307:意图1` — 打开全景影像左后视角

## 42. `KNOWN_CONTROL_CANDIDATE_C36A4D8D62_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `全景影像系统`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_C36A4D8D62 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20142:意图1` — 打开全景影像系统

## 43. `KNOWN_CONTROL_CANDIDATE_7306067958_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `全景影视`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7306067958 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4013:意图1` — 打开全景影视

## 44. `KNOWN_CONTROL_CANDIDATE_DA03591887_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `全景模式`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DA03591887 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16884:意图1` — 打开全景模式

## 45. `KNOWN_CONTROL_CANDIDATE_8E0D5AC9FB_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `全景环视`
- MAC 子功能: ``
- MAC 操作: `['关掉']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_8E0D5AC9FB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2672:意图1` — 请给全景环视关掉

## 46. `KNOWN_CONTROL_CANDIDATE_8E0D5AC9FB_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `全景环视`
- MAC 子功能: ``
- MAC 操作: `['取消']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_8E0D5AC9FB + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:319:意图1` — 我想把全景环视取消
- `train_set.jsonl:4850:意图1` — 请给全景环视取消
- `train_set.jsonl:8867:意图1` — 请把全景环视取消

## 47. `KNOWN_CONTROL_CANDIDATE_F2B8C288DD_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `全景视频`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F2B8C288DD + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2804:意图1` — 关闭全景视频

## 48. `KNOWN_CONTROL_CANDIDATE_704C27F037_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `关闭行人提`
- MAC 子功能: `行人安全辅助`
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_704C27F037 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12866:意图2` — 关闭行人提示
- `train_set.jsonl:8668:意图2` — 关闭行人提示

## 49. `KNOWN_CONTROL_CANDIDATE_F80A374317_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `冰箱多少度`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_F80A374317 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15085:意图1` — 冰箱多少度

## 50. `KNOWN_CONTROL_CANDIDATE_2F6D68ED94_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `冰箱是在冷藏吗`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_2F6D68ED94 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11979:意图1` — 冰箱是在冷藏吗

## 51. `KNOWN_CONTROL_CANDIDATE_FD153F653E_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `冰箱现在可以冷藏吗`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_FD153F653E + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10088:意图1` — 冰箱现在可以冷藏吗

## 52. `KNOWN_CONTROL_CANDIDATE_AC6E8C9C32_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前向预碰撞辅助`
- MAC 子功能: `前向预碰撞辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_AC6E8C9C32 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18185:意图1` — 打开前向预碰撞辅助

## 53. `KNOWN_CONTROL_CANDIDATE_81C544DD67_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前方侧向交通辅助`
- MAC 子功能: `前方侧向交通辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_81C544DD67 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6948:意图1` — 帮我把前方侧向交通辅助打开

## 54. `KNOWN_CONTROL_CANDIDATE_89C8CF56D4_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前方横向来车制动`
- MAC 子功能: `前方横向来车制动`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_89C8CF56D4 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19326:意图1` — 打开前方横向来车制动页面

## 55. `KNOWN_CONTROL_CANDIDATE_3893093C0C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前横穿侧向预警`
- MAC 子功能: `前横穿侧向预警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3893093C0C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4377:意图1` — 打开前横穿侧向预警

## 56. `KNOWN_CONTROL_CANDIDATE_12502264D4_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `前车起步提醒`
- MAC 子功能: `前车起步提醒`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_12502264D4 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2823:意图1` — 打开前车起步提醒页面

## 57. `KNOWN_CONTROL_CANDIDATE_5F1E779075_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `动力电池包主动保温`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5F1E779075 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6391:意图1` — 打开动力电池包主动保温

## 58. `KNOWN_CONTROL_CANDIDATE_DE1DA561E5_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `卫星通信`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_DE1DA561E5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20538:意图1` — 关闭卫星通信设置

## 59. `KNOWN_CONTROL_CANDIDATE_A382D4E994_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `卫星通讯`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_A382D4E994 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4845:意图1` — 关闭卫星通讯

## 60. `KNOWN_CONTROL_CANDIDATE_2679985724_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `发动机启停`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2679985724 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16507:意图1` — 把发动机启停的状态设置为开

## 61. `KNOWN_CONTROL_CANDIDATE_2679985724_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `发动机启停`
- MAC 子功能: ``
- MAC 操作: `['可以关了']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_2679985724 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2493:意图1` — 发动机启停可以关了

## 62. `KNOWN_CONTROL_CANDIDATE_76881A012F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `变道确认`
- MAC 子功能: `变道确认`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_76881A012F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4704:意图1` — 帮我打开变道确认

## 63. `KNOWN_CONTROL_CANDIDATE_233C9A3376_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `变道警示系统`
- MAC 子功能: `变道警示系统`
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_233C9A3376 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20438:意图1` — 变道警示系统打开
- `train_set.jsonl:14076:意图1` — 打开变道警示系统

## 64. `KNOWN_CONTROL_CANDIDATE_E7593416C1_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `右向辅助`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E7593416C1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19250:意图1` — 打开右向辅助

## 65. `KNOWN_CONTROL_CANDIDATE_65ED614642_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `后方横向来车制动`
- MAC 子功能: `后方横向来车制动`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_65ED614642 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:537:意图1` — 打开后方横向来车制动页面

## 66. `KNOWN_CONTROL_CANDIDATE_99BE300B5C_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `听音位`
- MAC 子功能: ``
- MAC 操作: `['调为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_99BE300B5C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20147:意图1` — 听音位调为第二排

## 67. `KNOWN_CONTROL_CANDIDATE_75B4D84A8C_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `壁纸桌面`
- MAC 子功能: ``
- MAC 操作: `['切换为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_75B4D84A8C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1187:意图1` — 桌面切换为壁纸桌面

## 68. `KNOWN_CONTROL_CANDIDATE_E983E2B539_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `声浪`
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E983E2B539 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13483:意图1` — 我想要低声浪
- `train_set.jsonl:18904:意图1` — 调一下声浪大小到低

## 69. `KNOWN_CONTROL_CANDIDATE_E983E2B539_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `声浪`
- MAC 子功能: ``
- MAC 操作: `['调节为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E983E2B539 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18964:意图1` — 车外声浪调节为电子

## 70. `KNOWN_CONTROL_CANDIDATE_E983E2B539_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `声浪`
- MAC 子功能: ``
- MAC 操作: `['关闭下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_E983E2B539 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7701:意图1` — 将车外声浪关闭下

## 71. `KNOWN_CONTROL_CANDIDATE_E983E2B539_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `声浪`
- MAC 子功能: ``
- MAC 操作: `['启动一下', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E983E2B539 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14314:意图1` — 后一个我要选声浪
- `train_set.jsonl:6252:意图1` — 启动一下车外声浪

## 72. `KNOWN_CONTROL_CANDIDATE_5071B5A16B_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `声浪仿真`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5071B5A16B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6498:意图1` — 打开内部声浪仿真界面

## 73. `KNOWN_CONTROL_CANDIDATE_D7A0C55930_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `声浪模拟`
- MAC 子功能: ``
- MAC 操作: `['调一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_D7A0C55930 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15369:意图1` — 调一下声浪模拟界面

## 74. `KNOWN_CONTROL_CANDIDATE_D7A0C55930_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `声浪模拟`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_D7A0C55930 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:36:意图1` — 我想要打开声浪模拟
- `train_set.jsonl:17808:意图1` — 打开声浪模拟
- `train_set.jsonl:1927:意图1` — 打开内部声浪模拟界面
- `train_set.jsonl:5940:意图1` — 打开外部声浪模拟界面
- `train_set.jsonl:7658:意图1` — 内部声浪模拟界面打开

## 75. `KNOWN_CONTROL_CANDIDATE_07A286181C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `夜视系统`
- MAC 子功能: `近红外夜视`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_07A286181C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7804:意图1` — 打开近红外夜视

## 76. `KNOWN_CONTROL_CANDIDATE_5AF61BE86A_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `如何查胎压情况`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5AF61BE86A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17886:意图1` — 如何查胎压情况

## 77. `KNOWN_CONTROL_CANDIDATE_0CA4B5F18D_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `如果我占用了应急车道请提醒我`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_0CA4B5F18D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8968:意图1` — 如果我占用了应急车道请提醒我

## 78. `KNOWN_CONTROL_CANDIDATE_3A8AF5A6DE_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `学习泊车`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3A8AF5A6DE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8701:意图1` — 打开学习泊车

## 79. `KNOWN_CONTROL_CANDIDATE_49726F09C8_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `定位`
- MAC 子功能: ``
- MAC 操作: `['设为']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_49726F09C8 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1017:意图1` — 定位使用有效期设为本次
- `train_set.jsonl:2041:意图1` — 定位使用有效期设为12个月

## 80. `KNOWN_CONTROL_CANDIDATE_D5E186344F_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `对负载充电`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_D5E186344F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5811:意图1` — 关闭对负载充电

## 81. `KNOWN_CONTROL_CANDIDATE_55D712311B_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `对车供电`
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_55D712311B + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:664:意图1` — 对外供电设置为对车供电

## 82. `KNOWN_CONTROL_CANDIDATE_CDB62250CA_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `导航抑制媒体音`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_CDB62250CA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9819:意图1` — 将导航抑制媒体音关闭

## 83. `KNOWN_CONTROL_CANDIDATE_758C64DF2E_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `导航时降低媒体音量`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_758C64DF2E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19800:意图1` — 打开导航时降低媒体音量

## 84. `KNOWN_CONTROL_CANDIDATE_148CD51252_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `应急车道占用提醒`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_148CD51252 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18098:意图1` — 帮我把应急车道占用提醒打开

## 85. `KNOWN_CONTROL_CANDIDATE_DF81BF9C8C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱主动恒温`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DF81BF9C8C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1576:意图1` — 打开座舱主动恒温

## 86. `KNOWN_CONTROL_CANDIDATE_A0D5F2B95F_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱主动温控系统`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_A0D5F2B95F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14199:意图1` — 关闭座舱主动温控系统

## 87. `KNOWN_CONTROL_CANDIDATE_A0D5F2B95F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱主动温控系统`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A0D5F2B95F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13626:意图1` — 打开座舱主动温控系统

## 88. `KNOWN_CONTROL_CANDIDATE_A3DD9EEC1F_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱恒温`
- MAC 子功能: ``
- MAC 操作: `['关']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_A3DD9EEC1F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1232:意图1` — 我想关座舱恒温

## 89. `KNOWN_CONTROL_CANDIDATE_A3DD9EEC1F_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱恒温`
- MAC 子功能: ``
- MAC 操作: `['开下']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A3DD9EEC1F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1371:意图1` — 我要开下座舱恒温
- `train_set.jsonl:15600:意图1` — 想要开下座舱恒温

## 90. `KNOWN_CONTROL_CANDIDATE_DB13B761B8_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱控温`
- MAC 子功能: ``
- MAC 操作: `['关']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_DB13B761B8 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1673:意图1` — 我想关座舱控温

## 91. `KNOWN_CONTROL_CANDIDATE_DB13B761B8_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱控温`
- MAC 子功能: ``
- MAC 操作: `['开', '开启']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DB13B761B8 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20409:意图1` — 要开启座舱控温
- `train_set.jsonl:12193:意图1` — 帮我开座舱控温

## 92. `KNOWN_CONTROL_CANDIDATE_DB13B761B8_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱控温`
- MAC 子功能: ``
- MAC 操作: `['开下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_DB13B761B8 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15363:意图1` — 我要开下座舱控温

## 93. `KNOWN_CONTROL_CANDIDATE_9C6088FEF0_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱控温系统`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_9C6088FEF0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18357:意图1` — 打开座舱控温系统

## 94. `KNOWN_CONTROL_CANDIDATE_9C6088FEF0_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱控温系统`
- MAC 子功能: ``
- MAC 操作: `['退出']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_9C6088FEF0 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1427:意图1` — 退出座舱控温系统

## 95. `KNOWN_CONTROL_CANDIDATE_A34A9C321D_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱监测系统`
- MAC 子功能: `危险动作检测报警`
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A34A9C321D + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1538:意图1` — 危险动作检测报警提醒间隔设置为3分钟

## 96. `KNOWN_CONTROL_CANDIDATE_2D172E01EA_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱监测系统`
- MAC 子功能: `危险行为监测`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2D172E01EA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20098:意图1` — 打开危险行为监测

## 97. `KNOWN_CONTROL_CANDIDATE_693F4332C7_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱监测系统`
- MAC 子功能: `行为监测`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_693F4332C7 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18485:意图1` — 打开行为监测

## 98. `KNOWN_CONTROL_CANDIDATE_C9A184687C_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `座舱过热保护`
- MAC 子功能: ``
- MAC 操作: `['关一下', '可以关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_C9A184687C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12206:意图1` — 给我关一下座舱过热保护
- `train_set.jsonl:6792:意图1` — 座舱过热保护可以关闭吗

## 99. `KNOWN_CONTROL_CANDIDATE_CA94660D8A_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `开机动画音乐`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_CA94660D8A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2091:意图2` — 关闭来电语音播报关闭开机动画音乐

## 100. `KNOWN_CONTROL_CANDIDATE_CA94660D8A_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `开机动画音乐`
- MAC 子功能: ``
- MAC 操作: `['开一下', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_CA94660D8A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11813:意图1` — 开一下开机动画音乐
- `train_set.jsonl:2053:意图1` — 打开开机动画音乐打开报警语音播报

## 101. `KNOWN_CONTROL_CANDIDATE_E858819B6F_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `开机声音`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_E858819B6F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17184:意图1` — 关闭开机声音

## 102. `KNOWN_CONTROL_CANDIDATE_E858819B6F_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `开机声音`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_E858819B6F + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9438:意图1` — 开机声音关闭静音

## 103. `KNOWN_CONTROL_CANDIDATE_7AFB750188_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `开机声音开启`
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7AFB750188 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4462:意图1` — 开机声音开启静音

## 104. `KNOWN_CONTROL_CANDIDATE_727D225998_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `开机背景声音`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_727D225998 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14284:意图1` — 关闭开机背景声音

## 105. `KNOWN_CONTROL_CANDIDATE_C46C4FB3A3_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `开机背景音乐`
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C46C4FB3A3 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20133:意图1` — 开机背景音乐调到2

## 106. `KNOWN_CONTROL_CANDIDATE_29B07CFEFF_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `开机音乐动画`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_29B07CFEFF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6198:意图1` — 打开开机音乐动画

## 107. `KNOWN_CONTROL_CANDIDATE_75DFEE1471_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `开机音量自适应`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_75DFEE1471 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:393:意图1` — 关闭开机音量自适应

## 108. `KNOWN_CONTROL_CANDIDATE_75DFEE1471_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `开机音量自适应`
- MAC 子功能: ``
- MAC 操作: `['开', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_75DFEE1471 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11867:意图1` — 开机音量自适应开关我想要开
- `train_set.jsonl:7242:意图1` — 打开开机音量自适应

## 109. `KNOWN_CONTROL_CANDIDATE_E82AC1A059_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `开机音量自适应功能`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E82AC1A059 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:912:意图1` — 开机音量自适应功能我想要打开

## 110. `KNOWN_CONTROL_CANDIDATE_4CA6C7A684_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `强制保电记忆`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_4CA6C7A684 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14276:意图1` — 关闭强制保电记忆

## 111. `KNOWN_CONTROL_CANDIDATE_59EFC65434_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `当前电耗多少`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_59EFC65434 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2595:意图1` — 当前电耗多少

## 112. `KNOWN_CONTROL_CANDIDATE_7BEBD524D3_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `当前胎温是多少`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7BEBD524D3 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8608:意图1` — 当前胎温是多少

## 113. `KNOWN_CONTROL_CANDIDATE_E923432252_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `当前车辆还能行驶多远`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_E923432252 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6307:意图1` — 当前车辆还能行驶多远

## 114. `KNOWN_CONTROL_CANDIDATE_906891A86D_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `总行驶里程是多少`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_906891A86D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18645:意图1` — 总行驶里程是多少

## 115. `KNOWN_CONTROL_CANDIDATE_8058A5A2B7_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `手势静音`
- MAC 子功能: `手势静音`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_8058A5A2B7 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11358:意图1` — 打开手势静音

## 116. `KNOWN_CONTROL_CANDIDATE_EFD49BB3F1_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `手持打电话提醒`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_EFD49BB3F1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:6:意图1` — 关闭手持打电话提醒

## 117. `KNOWN_CONTROL_CANDIDATE_73017CBB5D_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `手机充电`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_73017CBB5D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20286:意图2` — 打开手机充电

## 118. `KNOWN_CONTROL_CANDIDATE_204E6D6094_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `手机无线充电`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_204E6D6094 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1175:意图5` — 打开手机无线充电

## 119. `KNOWN_CONTROL_CANDIDATE_2E77E2DF66_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `打开连接设备`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2E77E2DF66 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19895:意图1` — 打开连接设备

## 120. `KNOWN_CONTROL_CANDIDATE_75D11E0799_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `报警语音播报`
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_75D11E0799 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18968:意图1` — 报警语音播报静音

## 121. `KNOWN_CONTROL_CANDIDATE_75D11E0799_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `报警语音播报`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_75D11E0799 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2053:意图2` — 打开开机动画音乐打开报警语音播报

## 122. `KNOWN_CONTROL_CANDIDATE_EB698A094A_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `拨杆变道功能`
- MAC 子功能: `拨杆变道功能`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_EB698A094A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10643:意图1` — 拨杆变道功能打开

## 123. `KNOWN_CONTROL_CANDIDATE_4EEE30E94B_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `插枪保温`
- MAC 子功能: ``
- MAC 操作: `['关上']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_4EEE30E94B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15648:意图1` — 关上插枪保温

## 124. `KNOWN_CONTROL_CANDIDATE_467B6F424D_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `放电类型为对设备放电`
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_467B6F424D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13956:意图1` — 设置放电类型为对设备放电

## 125. `KNOWN_CONTROL_CANDIDATE_B137FB22D0_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `方便上车`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_B137FB22D0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6526:意图1` — 关闭方便上车

## 126. `KNOWN_CONTROL_CANDIDATE_81B1B313BE_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `方便进出`
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_81B1B313BE + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5520:意图1` — 副驾驶方便进出设置为离车

## 127. `KNOWN_CONTROL_CANDIDATE_81B1B313BE_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `方便进出`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_81B1B313BE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11032:意图1` — 打开方便进出
- `train_set.jsonl:7742:意图1` — 打开二排左方便进出

## 128. `KNOWN_CONTROL_CANDIDATE_FB64F36C7C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `无感进出`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_FB64F36C7C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3291:意图1` — 打开无感进出

## 129. `KNOWN_CONTROL_CANDIDATE_970FAFD543_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `无线充电`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **7**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_970FAFD543 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16519:意图1` — 关闭无线充电
- `train_set.jsonl:17412:意图1` — 关闭无线充电
- `train_set.jsonl:17979:意图1` — 无线充电帮我把它收起来吧
- `train_set.jsonl:2038:意图1` — 关闭无线充电
- `train_set.jsonl:6335:意图2` — 关闭无线充电

## 130. `KNOWN_CONTROL_CANDIDATE_970FAFD543_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `无线充电`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_970FAFD543 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11591:意图1` — 打开无线充电
- `train_set.jsonl:15535:意图2` — 打开无线充电
- `train_set.jsonl:17706:意图1` — 打开无线充电
- `train_set.jsonl:4242:意图1` — 帮我把无线充电开关打开
- `train_set.jsonl:8338:意图1` — 打开无线充电

## 131. `KNOWN_CONTROL_CANDIDATE_207F454638_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `无线手机充电`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_207F454638 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20341:意图1` — 关闭无线手机充电

## 132. `KNOWN_CONTROL_CANDIDATE_26822B2818_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `无线电充`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_26822B2818 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11930:意图1` — 打开无线电充

## 133. `KNOWN_CONTROL_CANDIDATE_F373FF115D_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `无线设备充电`
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F373FF115D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5917:意图1` — 我要关闭无线设备充电
- `train_set.jsonl:8315:意图1` — 我想关掉无线设备充电

## 134. `KNOWN_CONTROL_CANDIDATE_2038E81A80_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `显示连接设备`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2038E81A80 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8266:意图1` — 显示连接设备

## 135. `KNOWN_CONTROL_CANDIDATE_CBF4B46D65_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `智能感光`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_CBF4B46D65 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:165:意图1` — 打开智能感光

## 136. `KNOWN_CONTROL_CANDIDATE_32F58A3175_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `智能驾驶语音播报`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_32F58A3175 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20004:意图1` — 关闭智能驾驶语音播报

## 137. `KNOWN_CONTROL_CANDIDATE_EBB3F58875_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `最佳听音位`
- MAC 子功能: ``
- MAC 操作: `['选择']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_EBB3F58875 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1352:意图1` — 最佳听音位选择驾驶位位置
- `train_set.jsonl:18354:意图1` — 最佳听音位选择全车

## 138. `KNOWN_CONTROL_CANDIDATE_600A635C04_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `最近的电耗怎么样`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_600A635C04 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18349:意图1` — 最近的电耗怎么样

## 139. `KNOWN_CONTROL_CANDIDATE_0EC5BDDEDD_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `来电语音播报`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_0EC5BDDEDD + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14671:意图1` — 关闭来电语音播报
- `train_set.jsonl:2091:意图1` — 关闭来电语音播报关闭开机动画音乐

## 140. `KNOWN_CONTROL_CANDIDATE_0EC5BDDEDD_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `来电语音播报`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_0EC5BDDEDD + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13253:意图1` — 打开来电语音播报

## 141. `KNOWN_CONTROL_CANDIDATE_C55B2FADAF_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `来电语音播报模式`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_C55B2FADAF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16219:意图1` — 打开来电语音播报模式

## 142. `KNOWN_CONTROL_CANDIDATE_B68DADFDAE_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查一下车内细颗粒物`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_B68DADFDAE + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13290:意图1` — 查一下车内细颗粒物

## 143. `KNOWN_CONTROL_CANDIDATE_0094665F3D_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查看一下当前可行驶距离`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_0094665F3D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18346:意图1` — 查看一下当前可行驶距离

## 144. `KNOWN_CONTROL_CANDIDATE_19EDBFDDAB_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查看小电瓶工作状态`
- MAC 子功能: ``
- MAC 操作: `['查询']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_19EDBFDDAB + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9441:意图1` — 查看小电瓶工作状态

## 145. `KNOWN_CONTROL_CANDIDATE_4BAC7ED617_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查看胎压`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_4BAC7ED617 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16581:意图1` — 请查看胎压
- `train_set.jsonl:4218:意图2` — 查看胎压

## 146. `KNOWN_CONTROL_CANDIDATE_EB703C545D_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询一下当前能耗多少`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_EB703C545D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7414:意图1` — 查询一下当前能耗多少

## 147. `KNOWN_CONTROL_CANDIDATE_5A400093CF_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询充电时间`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5A400093CF + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19869:意图1` — 还差多长时间才能让它完全充满
- `train_set.jsonl:14851:意图1` — 还有多长时间才能使电池完全充满
- `train_set.jsonl:16003:意图1` — 电量还需多久充满
- `train_set.jsonl:4170:意图1` — 还需要多长时间才能充满
- `train_set.jsonl:5590:意图1` — 还要多久才能充电充满电量

## 148. `KNOWN_CONTROL_CANDIDATE_7C1BC3E99A_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询剩余电量`
- MAC 子功能: ``
- MAC 操作: `['展示', '查看']`
- 唯一样本数: **18**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7C1BC3E99A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:502:意图1` — 电量现在的大小是多大
- `test_set.jsonl:618:意图1` — 电池的状态如何
- `train_set.jsonl:10841:意图1` — 你现在多少电
- `train_set.jsonl:11704:意图1` — 电池电量
- `train_set.jsonl:12072:意图1` — 我们来看一下剩余电量

## 149. `KNOWN_CONTROL_CANDIDATE_37A241767D_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询剩余里程`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_37A241767D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4196:意图1` — 查询剩余里程

## 150. `KNOWN_CONTROL_CANDIDATE_9AE8992395_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询当前能耗`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_9AE8992395 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17339:意图1` — 查询当前能耗

## 151. `KNOWN_CONTROL_CANDIDATE_55EBA4E7AC_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询当前音量`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **9**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_55EBA4E7AC + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20513:意图1` — 帮我看下音量
- `train_set.jsonl:10499:意图1` — 媒体音量是多少
- `train_set.jsonl:11250:意图1` — 我想看音量
- `train_set.jsonl:11839:意图1` — 媒体音量现在是多大
- `train_set.jsonl:1193:意图1` — 媒体音量是多大

## 152. `KNOWN_CONTROL_CANDIDATE_26191D33A4_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询温度`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_26191D33A4 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17742:意图1` — 车里空调温度现在是几度

## 153. `KNOWN_CONTROL_CANDIDATE_096D44605C_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询滤芯剩余时间`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_096D44605C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2857:意图1` — 净水器的滤芯还剩多长的使用期限

## 154. `KNOWN_CONTROL_CANDIDATE_CA94B53009_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询电耗`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_CA94B53009 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7237:意图1` — 查询电耗

## 155. `KNOWN_CONTROL_CANDIDATE_714CB45CD9_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询累积能耗`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_714CB45CD9 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8518:意图1` — 查询累积能耗

## 156. `KNOWN_CONTROL_CANDIDATE_1B3329B94B_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询纯电续航里程`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_1B3329B94B + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2563:意图1` — 查询纯电续航里程

## 157. `KNOWN_CONTROL_CANDIDATE_4B97F4FFE3_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询续航里程`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **10**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_4B97F4FFE3 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:949:意图3` — 小计里程清零
- `train_set.jsonl:15848:意图1` — 我还可以行驶的距离
- `train_set.jsonl:17588:意图1` — 显示接下来可以开多远
- `train_set.jsonl:18470:意图1` — 电能跑多远路程
- `train_set.jsonl:19070:意图1` — 我还能跑多远

## 158. `KNOWN_CONTROL_CANDIDATE_88519E5BAF_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询胎温`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_88519E5BAF + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15046:意图1` — 查询胎温

## 159. `KNOWN_CONTROL_CANDIDATE_C7027A2418_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询能耗统计`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_C7027A2418 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7750:意图1` — 查询能耗统计

## 160. `KNOWN_CONTROL_CANDIDATE_FF904EB9B1_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询车内空气质量`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_FF904EB9B1 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:19036:意图1` — 查询车内空气质量

## 161. `KNOWN_CONTROL_CANDIDATE_062B379FB9_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询车辆总里程`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_062B379FB9 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:156:意图1` — 查询车辆总里程

## 162. `KNOWN_CONTROL_CANDIDATE_75058B8669_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `查询轮胎状态`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_75058B8669 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:573:意图1` — 当前轮胎状态正常吗
- `train_set.jsonl:2513:意图1` — 轮胎状况怎么样
- `train_set.jsonl:5047:意图1` — 显示左前轮胎状态
- `train_set.jsonl:5304:意图1` — 当前前侧轮胎怎么样
- `train_set.jsonl:5948:意图1` — 左前车辆轮胎状态

## 163. `KNOWN_CONTROL_CANDIDATE_5172540E0F_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `模拟一下声浪`
- MAC 子功能: ``
- MAC 操作: `['暂停']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5172540E0F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4575:意图1` — 我要模拟一下声浪暂停好吗

## 164. `KNOWN_CONTROL_CANDIDATE_FC06FBE148_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `模拟声浪`
- MAC 子功能: ``
- MAC 操作: `['关掉一下', '关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_FC06FBE148 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10279:意图1` — 将车外模拟声浪关掉一下
- `train_set.jsonl:12074:意图1` — 关闭模拟声浪
- `train_set.jsonl:7253:意图1` — 关闭车内模拟声浪

## 165. `KNOWN_CONTROL_CANDIDATE_FC06FBE148_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `模拟声浪`
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_FC06FBE148 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1222:意图1` — 车外模拟声浪开启

## 166. `KNOWN_CONTROL_CANDIDATE_FC06FBE148_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `模拟声浪`
- MAC 子功能: ``
- MAC 操作: `['启动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_FC06FBE148 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20382:意图1` — 启动运动模拟声浪

## 167. `KNOWN_CONTROL_CANDIDATE_FC06FBE148_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `模拟声浪`
- MAC 子功能: ``
- MAC 操作: `['设成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_FC06FBE148 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:467:意图1` — 车外模拟声浪设成狂野

## 168. `KNOWN_CONTROL_CANDIDATE_6D1CBAA058_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `横穿侧向制动`
- MAC 子功能: `横穿侧向制动`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_6D1CBAA058 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14843:意图1` — 打开横穿侧向制动

## 169. `KNOWN_CONTROL_CANDIDATE_98DA8263D3_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `汽车保养`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_98DA8263D3 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19706:意图1` — 我要看车的保养信息
- `train_set.jsonl:16335:意图1` — 把车的保养信息播放一下

## 170. `KNOWN_CONTROL_CANDIDATE_6B3571FA8A_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `汽车保养时间提醒`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_6B3571FA8A + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:929:意图1` — 关闭汽车保养时间提醒

## 171. `KNOWN_CONTROL_CANDIDATE_625F5B3352_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `油耗现在多少`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_625F5B3352 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20170:意图1` — 油耗现在多少

## 172. `KNOWN_CONTROL_CANDIDATE_5C10518788_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `泊入车`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5C10518788 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1032:意图1` — 我要泊入车

## 173. `KNOWN_CONTROL_CANDIDATE_24B2F78AEF_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `泊出`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_24B2F78AEF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20254:意图1` — 我要泊出

## 174. `KNOWN_CONTROL_CANDIDATE_8C03D7F4E7_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `泊车`
- MAC 子功能: ``
- MAC 操作: `['切换到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_8C03D7F4E7 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11140:意图1` — 切换到泊车设置页

## 175. `KNOWN_CONTROL_CANDIDATE_8C03D7F4E7_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `泊车`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_8C03D7F4E7 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1513:意图1` — 泊车媒体音量设置为关闭

## 176. `KNOWN_CONTROL_CANDIDATE_CF61C2A182_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `泊车辅助`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_CF61C2A182 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4505:意图1` — 关闭泊车辅助

## 177. `KNOWN_CONTROL_CANDIDATE_CF61C2A182_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `泊车辅助`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_CF61C2A182 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:144:意图1` — 打开泊车辅助

## 178. `KNOWN_CONTROL_CANDIDATE_8DB770C3F9_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `环视摄像头`
- MAC 子功能: ``
- MAC 操作: `['不显示']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_8DB770C3F9 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7401:意图1` — 环视摄像头不显示

## 179. `KNOWN_CONTROL_CANDIDATE_B9BA1CA9C6_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `现在电池剩余电量是多少`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_B9BA1CA9C6 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15960:意图1` — 现在电池剩余电量是多少

## 180. `KNOWN_CONTROL_CANDIDATE_3DD02FB84E_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `现在轮胎气还足吗`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_3DD02FB84E + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17631:意图1` — 现在轮胎气还足吗

## 181. `KNOWN_CONTROL_CANDIDATE_BE86821C1A_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `现在香氛是啥味道`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_BE86821C1A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10562:意图1` — 现在香氛是啥味道

## 182. `KNOWN_CONTROL_CANDIDATE_48459DD1CE_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `生命监测`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_48459DD1CE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20370:意图1` — 关闭生命监测
- `train_set.jsonl:8336:意图1` — 生命监测关闭

## 183. `KNOWN_CONTROL_CANDIDATE_48459DD1CE_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `生命监测`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_48459DD1CE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16638:意图1` — 打开车内生命监测
- `train_set.jsonl:2778:意图1` — 生命监测打开

## 184. `KNOWN_CONTROL_CANDIDATE_557F2EB602_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `用多少功率充电`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_557F2EB602 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11321:意图1` — 用多少功率充电

## 185. `KNOWN_CONTROL_CANDIDATE_25D49A937C_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `电池包主动保温`
- MAC 子功能: ``
- MAC 操作: `['开了']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_25D49A937C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9155:意图1` — 给我开了电池包主动保温

## 186. `KNOWN_CONTROL_CANDIDATE_64853A44CB_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `电池包插枪保温`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_64853A44CB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6504:意图1` — 打开电池包插枪保温

## 187. `KNOWN_CONTROL_CANDIDATE_EDECE81FF9_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `电池电量还剩多少`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_EDECE81FF9 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1746:意图1` — 电池电量还剩多少

## 188. `KNOWN_CONTROL_CANDIDATE_FBF5FCB22A_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `电量还剩多少`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_FBF5FCB22A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2954:意图2` — 电量还剩多少

## 189. `KNOWN_CONTROL_CANDIDATE_8C73C46491_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `疲劳驾驶提醒`
- MAC 子功能: ``
- MAC 操作: `['断']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_8C73C46491 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5474:意图1` — 中断连接疲劳驾驶提醒功能的接口

## 190. `KNOWN_CONTROL_CANDIDATE_3A37560910_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `看一下车内温度`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_3A37560910 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19440:意图1` — 我要看一下车内温度

## 191. `KNOWN_CONTROL_CANDIDATE_09C8613528_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `看看还有多久`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_09C8613528 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16924:意图1` — 我要看看还有多久

## 192. `KNOWN_CONTROL_CANDIDATE_08751F7880_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `碰撞安全辅助`
- MAC 子功能: `碰撞安全辅助`
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_08751F7880 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11438:意图1` — 请帮我碰撞安全辅助开启

## 193. `KNOWN_CONTROL_CANDIDATE_3960147454_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `空气质量检测`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3960147454 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16075:意图1` — 关闭空气质量检测

## 194. `KNOWN_CONTROL_CANDIDATE_E419E7F925_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `空气质量监测`
- MAC 子功能: ``
- MAC 操作: `['结束']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_E419E7F925 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:828:意图1` — 结束空气质量监测

## 195. `KNOWN_CONTROL_CANDIDATE_A8A20CF892_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `系统快速启动功能`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_A8A20CF892 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:621:意图1` — 系统快速启动功能关闭

## 196. `KNOWN_CONTROL_CANDIDATE_D7691CBEA5_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `紧急转向辅助`
- MAC 子功能: `紧急转向辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_D7691CBEA5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17594:意图1` — 帮我把紧急转向辅助打开

## 197. `KNOWN_CONTROL_CANDIDATE_36138FDED1_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `红灯制动辅助`
- MAC 子功能: `红灯制动辅助`
- MAC 操作: `['设置']`
- 唯一样本数: **2**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_36138FDED1 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12670:意图1` — 设置红灯制动辅助
- `train_set.jsonl:1969:意图1` — 设置红灯制动辅助

## 198. `KNOWN_CONTROL_CANDIDATE_18676ED643_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `红绿灯提示`
- MAC 子功能: `红绿灯提示`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_18676ED643 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11034:意图1` — 打开红绿灯提示

## 199. `KNOWN_CONTROL_CANDIDATE_2384A028DB_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `红绿灯提醒`
- MAC 子功能: `红绿灯提醒`
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_2384A028DB + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3418:意图1` — 设置红绿灯提醒

## 200. `KNOWN_CONTROL_CANDIDATE_2384A028DB_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `红绿灯提醒`
- MAC 子功能: `红绿灯提醒`
- MAC 操作: `['更改']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_2384A028DB + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11085:意图1` — 更改红绿灯提醒设置

## 201. `KNOWN_CONTROL_CANDIDATE_39FA388A46_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `红绿灯辅助`
- MAC 子功能: `红绿灯辅助`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_39FA388A46 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:19095:意图1` — 关闭红绿灯辅助

## 202. `KNOWN_CONTROL_CANDIDATE_39FA388A46_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `红绿灯辅助`
- MAC 子功能: `红绿灯辅助`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_39FA388A46 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19380:意图1` — 打开红绿灯辅助

## 203. `KNOWN_CONTROL_CANDIDATE_1A05A2DE53_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `绕行辅助功能`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_1A05A2DE53 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1072:意图1` — 关闭绕行辅助功能

## 204. `KNOWN_CONTROL_CANDIDATE_908C22C09E_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `胎压`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_908C22C09E + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10957:意图1` — 显示胎压
- `train_set.jsonl:17747:意图1` — 显示左中胎压
- `train_set.jsonl:4180:意图1` — 查看胎压状况
- `train_set.jsonl:6417:意图1` — 显示右中胎压

## 205. `KNOWN_CONTROL_CANDIDATE_6810A0201A_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `胎压如何`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_6810A0201A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2850:意图1` — 胎压如何

## 206. `KNOWN_CONTROL_CANDIDATE_A89727DFE3_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `胎压正常`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A89727DFE3 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1050:意图1` — 胎压正常吗

## 207. `KNOWN_CONTROL_CANDIDATE_AB21B5B741_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `胎压监测`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_AB21B5B741 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5313:意图2` — 打开四轮胎压

## 208. `KNOWN_CONTROL_CANDIDATE_AB21B5B741_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `胎压监测`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **10**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_AB21B5B741 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11444:意图1` — 查看右后轮胎压
- `train_set.jsonl:14507:意图1` — 打开轮胎胎压显示
- `train_set.jsonl:15536:意图1` — 查询右中轮胎气压
- `train_set.jsonl:2515:意图1` — 查一下左后胎压
- `train_set.jsonl:4312:意图1` — 查看左后轮胎压

## 209. `KNOWN_CONTROL_CANDIDATE_88DE103934_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `胎压系统`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_88DE103934 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8101:意图1` — 检查胎压系统

## 210. `KNOWN_CONTROL_CANDIDATE_481641DE0E_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `胎温是多少`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_481641DE0E + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20074:意图1` — 胎温是多少

## 211. `KNOWN_CONTROL_CANDIDATE_1C6ADA3205_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `胎温查询`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_1C6ADA3205 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13795:意图1` — 胎温查询

## 212. `KNOWN_CONTROL_CANDIDATE_37B1FFB6A8_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `胎温监测`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_37B1FFB6A8 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5586:意图1` — 检查左后胎温

## 213. `KNOWN_CONTROL_CANDIDATE_1991AC69C0_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `自动停车功能`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_1991AC69C0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5383:意图1` — 关闭自动停车功能

## 214. `KNOWN_CONTROL_CANDIDATE_782D253224_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `自动启停`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_782D253224 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13961:意图1` — 关闭自动启停
- `train_set.jsonl:14073:意图1` — 发动机的自动启停功能不需要了

## 215. `KNOWN_CONTROL_CANDIDATE_BEB46ECA8A_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `自动导航辅助`
- MAC 子功能: `自动导航辅助`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BEB46ECA8A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9996:意图1` — 关闭自动导航辅助

## 216. `KNOWN_CONTROL_CANDIDATE_522F484827_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `自动泊车`
- MAC 子功能: ``
- MAC 操作: `['开', '开启', '打开']`
- 唯一样本数: **6**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_522F484827 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17513:意图2` — 停车的时候我需要自动泊车功能来辅助我停车
- `train_set.jsonl:18597:意图1` — 开始执行停车助手功能
- `train_set.jsonl:2490:意图1` — 自动泊车设置为开启状态
- `train_set.jsonl:3837:意图1` — 开自动泊车
- `train_set.jsonl:3837:意图2` — 打开自动泊车

## 217. `KNOWN_CONTROL_CANDIDATE_522F484827_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `自动泊车`
- MAC 子功能: ``
- MAC 操作: `['激活']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_522F484827 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5455:意图1` — 激活自动泊车

## 218. `KNOWN_CONTROL_CANDIDATE_3E8DD23C65_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `自动泊车辅助系统`
- MAC 子功能: ``
- MAC 操作: `['开一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3E8DD23C65 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7732:意图1` — 开一下自动泊车辅助系统

## 219. `KNOWN_CONTROL_CANDIDATE_00F9B86311_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `自动辅助导航驾驶`
- MAC 子功能: `自动辅助导航驾驶`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_00F9B86311 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5245:意图1` — 打开自动辅助导航驾驶

## 220. `KNOWN_CONTROL_CANDIDATE_4EB873F199_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `舒适制动模式`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4EB873F199 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19786:意图1` — 打开舒适制动模式

## 221. `KNOWN_CONTROL_CANDIDATE_922C17C6FB_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `行人提示音`
- MAC 子功能: `行人提示音`
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_922C17C6FB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11860:意图1` — 关闭行人提示音
- `train_set.jsonl:2117:意图2` — 关闭行人提示音
- `train_set.jsonl:5734:意图1` — 关闭行人提示音

## 222. `KNOWN_CONTROL_CANDIDATE_B472050800_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `行车保电`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_B472050800 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2456:意图1` — 打开行车保电

## 223. `KNOWN_CONTROL_CANDIDATE_4330882D5B_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `行车保电`
- MAC 子功能: `强制保电`
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4330882D5B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8676:意图1` — 强制保电调低3

## 224. `KNOWN_CONTROL_CANDIDATE_8847538A52_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `行车保电`
- MAC 子功能: `智能保电`
- MAC 操作: `['切换']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_8847538A52 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13706:意图1` — 切换智能保电

## 225. `KNOWN_CONTROL_CANDIDATE_8847538A52_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `行车保电`
- MAC 子功能: `智能保电`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_8847538A52 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7297:意图1` — 打开智能保电

## 226. `KNOWN_CONTROL_CANDIDATE_BBF18DCDC8_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `行车视频限制模式`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BBF18DCDC8 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7233:意图1` — 关闭行车视频限制模式

## 227. `KNOWN_CONTROL_CANDIDATE_3C6452C5B2_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `记忆泊车`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3C6452C5B2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11653:意图1` — 关闭记忆泊车页面

## 228. `KNOWN_CONTROL_CANDIDATE_3C6452C5B2_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `记忆泊车`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['AUTO_PARK_ENABLE']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3C6452C5B2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8781:意图1` — 打开记忆泊车

## 229. `KNOWN_CONTROL_CANDIDATE_5144F6C546_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `语音消息播报`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5144F6C546 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9077:意图1` — 语音消息播报打开

## 230. `KNOWN_CONTROL_CANDIDATE_575DA7EC10_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `超速监测`
- MAC 子功能: `超速监测`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_575DA7EC10 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3339:意图1` — 关闭超速监测

## 231. `KNOWN_CONTROL_CANDIDATE_D970006B55_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `超速警示音`
- MAC 子功能: `超速警示音`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_D970006B55 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5260:意图1` — 关闭超速警示音

## 232. `KNOWN_CONTROL_CANDIDATE_1982BF6E08_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `路口放大图`
- MAC 子功能: ``
- MAC 操作: `['取消']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_1982BF6E08 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17720:意图1` — 取消路口放大图

## 233. `KNOWN_CONTROL_CANDIDATE_F7C0BE3CCA_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `路口放大图功能`
- MAC 子功能: ``
- MAC 操作: `['关闭下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F7C0BE3CCA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2326:意图1` — 路口放大图功能关闭下

## 234. `KNOWN_CONTROL_CANDIDATE_3F8B6C606D_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车内二氧化碳查询`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_3F8B6C606D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10856:意图1` — 车内二氧化碳查询

## 235. `KNOWN_CONTROL_CANDIDATE_A3FD091C19_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车内温度是多少度以上`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A3FD091C19 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8745:意图1` — 车内温度是多少度以上

## 236. `KNOWN_CONTROL_CANDIDATE_A0C3358EBA_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车内温度有多高`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A0C3358EBA + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13473:意图1` — 车内温度有多高

## 237. `KNOWN_CONTROL_CANDIDATE_A762D5FAF8_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车内空气质量怎么样`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A762D5FAF8 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15259:意图1` — 车内空气质量怎么样

## 238. `KNOWN_CONTROL_CANDIDATE_669252945A_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车子油耗是多少`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_669252945A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6018:意图1` — 车子油耗是多少

## 239. `KNOWN_CONTROL_CANDIDATE_4269917777_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车对负载放电`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_4269917777 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19323:意图1` — 关闭车对负载放电

## 240. `KNOWN_CONTROL_CANDIDATE_123A144E34_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车的油耗怎么样`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_123A144E34 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11055:意图1` — 车的油耗怎么样

## 241. `KNOWN_CONTROL_CANDIDATE_F37F845338_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车的能耗怎么样`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_F37F845338 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14416:意图1` — 车的能耗怎么样

## 242. `KNOWN_CONTROL_CANDIDATE_BFB4BCC285_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车跑了多少里路`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_BFB4BCC285 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10627:意图1` — 车跑了多少里路

## 243. `KNOWN_CONTROL_CANDIDATE_66D870DF53_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车身稳定系统`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_66D870DF53 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18516:意图1` — 关闭车身稳定系统

## 244. `KNOWN_CONTROL_CANDIDATE_66D870DF53_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车身稳定系统`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_66D870DF53 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1059:意图1` — 打开车身稳定系统

## 245. `KNOWN_CONTROL_CANDIDATE_3067F44AF2_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车辆超速通知`
- MAC 子功能: `车辆超速通知`
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3067F44AF2 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19295:意图1` — 设置车辆超速通知

## 246. `KNOWN_CONTROL_CANDIDATE_B67600BF1C_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车速提醒`
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_B67600BF1C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17600:意图1` — 我要调节大一点车速提醒

## 247. `KNOWN_CONTROL_CANDIDATE_B67600BF1C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车速提醒`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_B67600BF1C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12851:意图1` — 打开车速提醒

## 248. `KNOWN_CONTROL_CANDIDATE_307DB4FCED_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车速限制功能`
- MAC 子功能: `车速限制功能`
- MAC 操作: `['激活']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_307DB4FCED + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7740:意图1` — 激活车速限制功能

## 249. `KNOWN_CONTROL_CANDIDATE_D4C987F23D_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道保持辅助`
- MAC 子功能: `车道保持辅助`
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_D4C987F23D + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1988:意图1` — 车道保持辅助设置为震动预警

## 250. `KNOWN_CONTROL_CANDIDATE_751BBEFEE4_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `车道变更确认功能`
- MAC 子功能: `车道变更确认功能`
- MAC 操作: `['执行']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['LANE_CHANGE', 'LANE_KEEP']`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_751BBEFEE4 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8929:意图1` — 执行车道变更确认功能

## 251. `KNOWN_CONTROL_CANDIDATE_63B898FB57_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `轮胎压怎么样`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_63B898FB57 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17804:意图1` — 右后轮胎压怎么样
- `train_set.jsonl:18219:意图1` — 右前轮胎压怎么样

## 252. `KNOWN_CONTROL_CANDIDATE_0E6745F652_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `轮胎压正常吗`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_0E6745F652 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12626:意图1` — 后轮胎压正常吗

## 253. `KNOWN_CONTROL_CANDIDATE_9D15836B38_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `轮胎气压`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_9D15836B38 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13861:意图1` — 显示轮胎气压

## 254. `KNOWN_CONTROL_CANDIDATE_6E22B01DE2_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `轮胎胎压如何`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_6E22B01DE2 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20394:意图1` — 右后轮胎胎压如何
- `train_set.jsonl:18097:意图1` — 前侧轮胎胎压如何

## 255. `KNOWN_CONTROL_CANDIDATE_62197D6435_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `轮胎胎压正常吗`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_62197D6435 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6609:意图1` — 中间轮胎胎压正常吗

## 256. `KNOWN_CONTROL_CANDIDATE_C8CB4C31DB_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `轮胎胎温正常吗`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_C8CB4C31DB + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12688:意图1` — 左前轮胎胎温正常吗

## 257. `KNOWN_CONTROL_CANDIDATE_CB3D753765_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `辅助驾驶`
- MAC 子功能: `辅助驾驶`
- MAC 操作: `['启动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_CB3D753765 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4016:意图1` — 辅助驾驶启动

## 258. `KNOWN_CONTROL_CANDIDATE_9B1374170E_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `辅助驾驶的语音模式`
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_9B1374170E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10533:意图1` — 将辅助驾驶的语音模式设置为详细模式

## 259. `KNOWN_CONTROL_CANDIDATE_3A742F5624_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `过热保护`
- MAC 子功能: ``
- MAC 操作: `['关下', '关掉']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3A742F5624 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20289:意图1` — 关掉过热保护
- `train_set.jsonl:5579:意图1` — 关下过热保护

## 260. `KNOWN_CONTROL_CANDIDATE_3A742F5624_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `过热保护`
- MAC 子功能: ``
- MAC 操作: `['退出']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_3A742F5624 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16153:意图1` — 退出过热保护

## 261. `KNOWN_CONTROL_CANDIDATE_438F6DDA51_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `还有多少有电`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_438F6DDA51 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14868:意图1` — 还有多少有电

## 262. `KNOWN_CONTROL_CANDIDATE_A56F13C424_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `还能自动驾驶多远`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A56F13C424 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13373:意图1` — 还能自动驾驶多远

## 263. `KNOWN_CONTROL_CANDIDATE_4E4142E58F_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `还要充多久的电`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_4E4142E58F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13536:意图1` — 还要充多久的电

## 264. `KNOWN_CONTROL_CANDIDATE_176428C845_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `连接了什么设备`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_176428C845 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16039:意图1` — 打开连接了什么设备

## 265. `KNOWN_CONTROL_CANDIDATE_47BF623957_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `连续说`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_47BF623957 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9089:意图1` — 连续说开关关闭

## 266. `KNOWN_CONTROL_CANDIDATE_47BF623957_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `连续说`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_47BF623957 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8845:意图1` — 连续说开关打开

## 267. `KNOWN_CONTROL_CANDIDATE_2A72777B3C_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `逆向超车预警`
- MAC 子功能: `逆向超车预警`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_2A72777B3C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10803:意图1` — 关闭逆向超车预警页面

## 268. `KNOWN_CONTROL_CANDIDATE_82CD605BDD_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `速报警`
- MAC 子功能: `速报警`
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_82CD605BDD + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15247:意图1` — 关闭速报警

## 269. `KNOWN_CONTROL_CANDIDATE_4745D1CBA1_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `道路标识识别`
- MAC 子功能: `道路标识识别`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4745D1CBA1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12393:意图1` — 打开道路标识识别

## 270. `KNOWN_CONTROL_CANDIDATE_F73522248C_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `遗留物品检测`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F73522248C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4821:意图1` — 关闭遗留物品检测

## 271. `KNOWN_CONTROL_CANDIDATE_758AE1348D_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `锁车声音`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_758AE1348D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13887:意图1` — 打开锁车声音

## 272. `KNOWN_CONTROL_CANDIDATE_13EFD69CA7_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `闭锁音效`
- MAC 子功能: ``
- MAC 操作: `['打开', '打开一下']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_13EFD69CA7 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15295:意图1` — 帮我打开闭锁音效
- `train_set.jsonl:17034:意图1` — 打开一下闭锁音效

## 273. `KNOWN_CONTROL_CANDIDATE_B617C20350_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `闯红灯预警`
- MAC 子功能: `闯红灯预警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_B617C20350 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6765:意图1` — 打开闯红灯预警页面

## 274. `KNOWN_CONTROL_CANDIDATE_7C794E450C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `限速信息提醒`
- MAC 子功能: `限速信息提醒`
- MAC 操作: `['打开一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7C794E450C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13180:意图1` — 打开一下限速信息提醒

## 275. `KNOWN_CONTROL_CANDIDATE_F4B48C4E55_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `限速报警`
- MAC 子功能: `限速报警`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_F4B48C4E55 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16551:意图1` — 打开限速报警

## 276. `KNOWN_CONTROL_CANDIDATE_CC06427F90_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `限速警告音`
- MAC 子功能: `限速警告音`
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_CC06427F90 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18819:意图1` — 请开启限速警告音

## 277. `KNOWN_CONTROL_CANDIDATE_0CE8DC4C99_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `限速辅助`
- MAC 子功能: `限速辅助`
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_0CE8DC4C99 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12608:意图1` — 打开限速辅助
- `train_set.jsonl:9953:意图1` — 开启限速辅助

## 278. `KNOWN_CONTROL_CANDIDATE_7EB1C18B18_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `音效增强`
- MAC 子功能: ``
- MAC 操作: `['修改', '设置']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7EB1C18B18 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4050:意图1` — 设置音效增强
- `train_set.jsonl:9015:意图1` — 对音效增强设置进行修改

## 279. `KNOWN_CONTROL_CANDIDATE_7EB1C18B18_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `音效增强`
- MAC 子功能: ``
- MAC 操作: `['关了']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_7EB1C18B18 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12391:意图1` — 音效增强影响音质了快关了

## 280. `KNOWN_CONTROL_CANDIDATE_7EB1C18B18_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `音效增强`
- MAC 子功能: ``
- MAC 操作: `['进入']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7EB1C18B18 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20514:意图1` — 进入音效增强的设置

## 281. `KNOWN_CONTROL_CANDIDATE_F8926F8DAC_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `预防座舱内过热保护`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_F8926F8DAC + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8154:意图1` — 将预防座舱内过热保护打开

## 282. `KNOWN_CONTROL_CANDIDATE_7D7CFE8CF3_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `预防性刹车`
- MAC 子功能: `预防性刹车`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7D7CFE8CF3 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20417:意图1` — 打开预防性刹车

## 283. `KNOWN_CONTROL_CANDIDATE_9C34DAE3E0_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `风量`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_9C34DAE3E0 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1357:意图1` — 查看主驾风量

## 284. `KNOWN_CONTROL_CANDIDATE_E6899F5052_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `马达启停`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_E6899F5052 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10984:意图1` — 关闭马达启停

## 285. `KNOWN_CONTROL_CANDIDATE_4F8D4FA88B_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驻车`
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4F8D4FA88B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:377:意图1` — 设置驻车时长
- `train_set.jsonl:11892:意图1` — 设置驻车舒享时间为两个半小时
- `train_set.jsonl:13297:意图1` — 设置驻车舒享半小时
- `train_set.jsonl:17530:意图1` — 设置驻车舒享时间为二点五小时
- `train_set.jsonl:8418:意图1` — 设置驻车时间

## 286. `KNOWN_CONTROL_CANDIDATE_4F8D4FA88B_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驻车`
- MAC 子功能: ``
- MAC 操作: `['关闭一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_4F8D4FA88B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16468:意图1` — 关闭一下驻车拍照

## 287. `KNOWN_CONTROL_CANDIDATE_4F8D4FA88B_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驻车`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_4F8D4FA88B + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:446:意图1` — 关闭驻车舒享
- `train_set.jsonl:10788:意图2` — 关闭驻车舒享
- `train_set.jsonl:15905:意图1` — 关闭驻车舒享模式式
- `train_set.jsonl:16474:意图1` — 模式更改不用停车舒享了
- `train_set.jsonl:17921:意图1` — 关闭驻车舒享挡

## 288. `KNOWN_CONTROL_CANDIDATE_4F8D4FA88B_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驻车`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4F8D4FA88B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11150:意图2` — 打开驻车
- `train_set.jsonl:12373:意图2` — 打开驻车

## 289. `KNOWN_CONTROL_CANDIDATE_4F8D4FA88B_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驻车`
- MAC 子功能: ``
- MAC 操作: `['开', '开启', '打开', '打打开']`
- 唯一样本数: **129**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4F8D4FA88B + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19479:意图2` — 打开驻车舒享
- `dev_set.jsonl:19524:意图1` — 打开驻车舒享
- `dev_set.jsonl:19609:意图1` — 开驻车舒享
- `dev_set.jsonl:19619:意图2` — 打开驻车舒享
- `dev_set.jsonl:19734:意图2` — 打开驻车舒享

## 290. `KNOWN_CONTROL_CANDIDATE_4F8D4FA88B_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驻车`
- MAC 子功能: ``
- MAC 操作: `['更改']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_4F8D4FA88B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4544:意图1` — 把驻车的舒享时间更改到半小时

## 291. `KNOWN_CONTROL_CANDIDATE_4F8D4FA88B_REVIEW`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驻车`
- MAC 子功能: ``
- MAC 操作: `['换', '更改']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_4F8D4FA88B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13607:意图1` — 帮我把模式换成驻车舒享
- `train_set.jsonl:13759:意图1` — 我需要更改驻车舒享的设置

## 292. `KNOWN_CONTROL_CANDIDATE_EFB1658984_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驻车模式`
- MAC 子功能: ``
- MAC 操作: `['关掉']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_EFB1658984 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:546:意图1` — 关掉驻车模式

## 293. `KNOWN_CONTROL_CANDIDATE_EFB1658984_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驻车模式`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_EFB1658984 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10519:意图1` — 打开驻车模式

## 294. `KNOWN_CONTROL_CANDIDATE_B188CA6C30_SET`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驾驶员监测系统`
- MAC 子功能: `疲劳驾驶检测`
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_B188CA6C30 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3175:意图1` — 疲劳驾驶检测灵敏度低

## 295. `KNOWN_CONTROL_CANDIDATE_C31C8B5146_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: ``
- MAC 功能: `驾驶员监测系统`
- MAC 子功能: `驾驶员疲劳监测`
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_C31C8B5146 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17315:意图1` — 打开驾驶员疲劳监测

## 296. `KNOWN_CONTROL_CANDIDATE_9DF515B719_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `⾏⼈提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_9DF515B719 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9663:意图1` — 关闭⾏⼈提示音

## 297. `KNOWN_CONTROL_CANDIDATE_E038DD8E92_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `一键翻折`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E038DD8E92 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6281:意图1` — 我想打开主驾的一键翻折

## 298. `KNOWN_CONTROL_CANDIDATE_8C3FC45F2D_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `一键零重力坐姿`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['收起']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_8C3FC45F2D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2955:意图1` — 收起一键零重力坐姿

## 299. `KNOWN_CONTROL_CANDIDATE_EFEF4B3B9B_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `个人热点`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_EFEF4B3B9B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19390:意图1` — 关闭个人热点
- `train_set.jsonl:14875:意图1` — 个人热点关闭

## 300. `KNOWN_CONTROL_CANDIDATE_A5C8635606_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `中控锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A5C8635606 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19842:意图1` — 锁上中控锁
- `dev_set.jsonl:20168:意图1` — 中控上锁
- `train_set.jsonl:10806:意图1` — 打开中控锁
- `train_set.jsonl:16616:意图1` — 中控锁锁上
- `train_set.jsonl:9866:意图1` — 启用中控锁解除

## 301. `KNOWN_CONTROL_CANDIDATE_A5C8635606_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `中控锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['解锁']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A5C8635606 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1459:意图1` — 解锁中控锁

## 302. `KNOWN_CONTROL_CANDIDATE_D06233EEDE_SET`

- MAC 对象: ``
- MAC 对象功能: `伴你回家`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_D06233EEDE + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15409:意图1` — 伴你回家调为半分钟

## 303. `KNOWN_CONTROL_CANDIDATE_D06233EEDE_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `伴你回家`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_D06233EEDE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11767:意图1` — 伴你回家打开
- `train_set.jsonl:13169:意图1` — 伴你回家开

## 304. `KNOWN_CONTROL_CANDIDATE_A2902B1E55_SET`

- MAC 对象: ``
- MAC 对象功能: `伴奏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A2902B1E55 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6433:意图1` — 将伴奏的声音调高

## 305. `KNOWN_CONTROL_CANDIDATE_5FE494121C_SET`

- MAC 对象: ``
- MAC 对象功能: `伴我回家`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5FE494121C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3562:意图1` — 把伴我回家的灯光角度调节到

## 306. `KNOWN_CONTROL_CANDIDATE_5FE494121C_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `伴我回家`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_5FE494121C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12076:意图1` — 不是特别需要伴我回家照明了
- `train_set.jsonl:1458:意图1` — 停止运行伴我回家照明系统

## 307. `KNOWN_CONTROL_CANDIDATE_C6F6D5C0FE_SET`

- MAC 对象: ``
- MAC 对象功能: `伴我回家灯`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为', '调节']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C6F6D5C0FE + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:189:意图1` — 伴我回家灯时间短一点
- `train_set.jsonl:12730:意图1` — 伴我回家灯时间久一点
- `train_set.jsonl:14500:意图1` — 伴我回家灯设置为30秒
- `train_set.jsonl:17973:意图1` — 伴我回家灯时间长一点

## 308. `KNOWN_CONTROL_CANDIDATE_11C987B84D_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `伴我回家灯照明`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_11C987B84D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2769:意图1` — 关闭伴我回家灯照明

## 309. `KNOWN_CONTROL_CANDIDATE_5C29D7FFEB_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `伴我照亮回家`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5C29D7FFEB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17795:意图1` — 开启伴我照亮回家

## 310. `KNOWN_CONTROL_CANDIDATE_CBD9A75267_SET`

- MAC 对象: ``
- MAC 对象功能: `低速报警`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_CBD9A75267 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18529:意图1` — 设置低速报警

## 311. `KNOWN_CONTROL_CANDIDATE_CBD9A75267_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速报警`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **11**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_CBD9A75267 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19289:意图1` — 关闭低速报警
- `test_set.jsonl:720:意图2` — 关闭低速报警
- `train_set.jsonl:10347:意图1` — 关闭低速报警
- `train_set.jsonl:11246:意图2` — 关闭低速报警
- `train_set.jsonl:1191:意图1` — 关闭低速报警

## 312. `KNOWN_CONTROL_CANDIDATE_27F2D2D310_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速报警音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_27F2D2D310 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15512:意图1` — 关闭低速报警音
- `train_set.jsonl:17189:意图1` — 关闭低速报警音

## 313. `KNOWN_CONTROL_CANDIDATE_D1CDA93701_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速提示`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_D1CDA93701 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19197:意图1` — 关闭低速提示
- `train_set.jsonl:10979:意图1` — 关闭低速提示

## 314. `KNOWN_CONTROL_CANDIDATE_B845795544_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速提示报警`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_B845795544 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1897:意图2` — 关闭低速提示报警

## 315. `KNOWN_CONTROL_CANDIDATE_53778325DE_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **16**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_53778325DE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:504:意图1` — 关闭低速提示音
- `test_set.jsonl:673:意图1` — 关闭低速提示音
- `test_set.jsonl:753:意图1` — 关闭低速提示音
- `test_set.jsonl:963:意图1` — 关掉低速提示音
- `train_set.jsonl:10019:意图3` — 关闭低速提示音

## 316. `KNOWN_CONTROL_CANDIDATE_53778325DE_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `低速提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_53778325DE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17919:意图2` — 低速提示音

## 317. `KNOWN_CONTROL_CANDIDATE_3617116965_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速提醒`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3617116965 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10649:意图3` — 打开主驾驶加热按摩关闭低速提醒
- `train_set.jsonl:13601:意图1` — 关闭低速提醒
- `train_set.jsonl:7841:意图2` — 关闭低速提醒

## 318. `KNOWN_CONTROL_CANDIDATE_4484351710_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `低速行人报警`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4484351710 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6025:意图1` — 让低速行人报警开启
- `train_set.jsonl:6739:意图1` — 低速行人报警打开

## 319. `KNOWN_CONTROL_CANDIDATE_4484351710_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `低速行人报警`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启用']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_4484351710 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2877:意图1` — 把低速行人报警启用

## 320. `KNOWN_CONTROL_CANDIDATE_7DD79B58D4_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `低速行人报警设备`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['取消', '启用']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7DD79B58D4 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4868:意图1` — 让低速行人报警设备启用
- `train_set.jsonl:5835:意图1` — 让低速行人报警设备取消

## 321. `KNOWN_CONTROL_CANDIDATE_5DDD093E2A_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `低速行人警告音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5DDD093E2A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15433:意图1` — 切到低速行人警告音页面

## 322. `KNOWN_CONTROL_CANDIDATE_CEE9C2CFCB_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速行驶`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_CEE9C2CFCB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4367:意图1` — 关闭低速行驶

## 323. `KNOWN_CONTROL_CANDIDATE_725C639C69_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速行驶外警示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_725C639C69 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15081:意图1` — 关闭低速行驶外警示音

## 324. `KNOWN_CONTROL_CANDIDATE_0F53360BC5_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速行驶提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭', '设置为关闭']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_0F53360BC5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12557:意图1` — 关闭低速行驶提示音
- `train_set.jsonl:1259:意图1` — 低速行驶提示音设置为关闭
- `train_set.jsonl:14657:意图1` — 关闭低速行驶提示音
- `train_set.jsonl:15428:意图1` — 关闭低速行驶提示音
- `train_set.jsonl:7386:意图1` — 关闭低速行驶提示音

## 325. `KNOWN_CONTROL_CANDIDATE_7F95D87F1B_SET`

- MAC 对象: ``
- MAC 对象功能: `低速行驶车外警示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7F95D87F1B + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6233:意图1` — 设置低速行驶车外警示音

## 326. `KNOWN_CONTROL_CANDIDATE_D9FD32A961_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速行驶音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_D9FD32A961 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:817:意图2` — 关闭低速行驶音

## 327. `KNOWN_CONTROL_CANDIDATE_6BC95C9BF9_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速警报`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_6BC95C9BF9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9352:意图1` — 关闭低速警报

## 328. `KNOWN_CONTROL_CANDIDATE_C5567A67FE_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速警示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_C5567A67FE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:113:意图1` — 关闭低速警示音
- `train_set.jsonl:10317:意图1` — 关闭低速警示音

## 329. `KNOWN_CONTROL_CANDIDATE_650D7BD4CA_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `低速预警`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_650D7BD4CA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5746:意图2` — 关闭低速预警

## 330. `KNOWN_CONTROL_CANDIDATE_49726F09C8_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `使用权限`
- MAC 功能: `定位`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_49726F09C8 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9288:意图1` — 关闭定位使用权限

## 331. `KNOWN_CONTROL_CANDIDATE_9D1CC7E803_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `侧窗锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_9D1CC7E803 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18027:意图1` — 打开侧窗锁

## 332. `KNOWN_CONTROL_CANDIDATE_76947C1D93_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `倒车音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_76947C1D93 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9978:意图1` — 倒车音关闭

## 333. `KNOWN_CONTROL_CANDIDATE_4CAE7BA7C8_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `儿童保护锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启用']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_4CAE7BA7C8 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16553:意图1` — 请启用右侧儿童保护锁

## 334. `KNOWN_CONTROL_CANDIDATE_2F09FDC1F2_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `儿童安全锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启动', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2F09FDC1F2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14961:意图1` — 打开右侧儿童安全锁
- `train_set.jsonl:17659:意图1` — 请打开后排儿童安全锁
- `train_set.jsonl:3711:意图1` — 启动右侧儿童安全锁

## 335. `KNOWN_CONTROL_CANDIDATE_16E8E9AAD3_SET`

- MAC 对象: ``
- MAC 对象功能: `儿童锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_16E8E9AAD3 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16893:意图1` — 设置儿童锁

## 336. `KNOWN_CONTROL_CANDIDATE_16E8E9AAD3_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `儿童锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['取消', '解锁']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_16E8E9AAD3 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13719:意图1` — 可以解锁右边儿童锁了
- `train_set.jsonl:14370:意图1` — 把右边儿童锁解锁
- `train_set.jsonl:2817:意图1` — 儿童锁键为我取消

## 337. `KNOWN_CONTROL_CANDIDATE_EE2A872250_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `儿童锁落锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['落锁']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_EE2A872250 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19383:意图1` — 儿童锁落锁

## 338. `KNOWN_CONTROL_CANDIDATE_BC0B6CB43E_SET`

- MAC 对象: ``
- MAC 对象功能: `充放电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调整']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BC0B6CB43E + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3421:意图1` — 我想要调整充放电

## 339. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_SET`

- MAC 对象: ``
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11260:意图1` — 改变车辆充电状态
- `train_set.jsonl:7224:意图1` — 改变充电模式

## 340. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_SET`

- MAC 对象: ``
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5004:意图1` — 充电量额外少
- `train_set.jsonl:7623:意图1` — 充电量太低了

## 341. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_SET`

- MAC 对象: ``
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17959:意图1` — 电池充电上限限制为50%

## 342. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_SET`

- MAC 对象: ``
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7887:意图1` — 将目标充电量调到最低

## 343. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7409:意图1` — 进入充电选项

## 344. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['停了', '开始']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10505:意图1` — 我要开始充电
- `train_set.jsonl:17685:意图1` — 把充电停了

## 345. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['充']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16319:意图1` — 电池电量充到50%

## 346. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['充']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15847:意图1` — 电量充到50%

## 347. `KNOWN_CONTROL_CANDIDATE_94CB8480BD_SET`

- MAC 对象: ``
- MAC 对象功能: `冷藏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_94CB8480BD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17074:意图1` — 冷藏模式设置为标准

## 348. `KNOWN_CONTROL_CANDIDATE_D152EDA8D7_SET`

- MAC 对象: ``
- MAC 对象功能: `出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为', '调到', '调至']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_D152EDA8D7 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1066:意图1` — 出风口模式设置为避让模式
- `train_set.jsonl:14792:意图1` — 副驾出风口调到手动模式
- `train_set.jsonl:1570:意图1` — 出风口设置为扫风模式
- `train_set.jsonl:7755:意图1` — 副驾出风口调至手动模式

## 349. `KNOWN_CONTROL_CANDIDATE_D152EDA8D7_SET`

- MAC 对象: ``
- MAC 对象功能: `出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为', '调到']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_D152EDA8D7 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12413:意图1` — 副驾的出风口调到最上面
- `train_set.jsonl:16873:意图1` — 二排出风口设置为左右扫风

## 350. `KNOWN_CONTROL_CANDIDATE_D152EDA8D7_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关下', '关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_D152EDA8D7 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15485:意图1` — 关下全车出风口
- `train_set.jsonl:5628:意图1` — 关闭全车出风口
- `train_set.jsonl:6246:意图1` — 关闭右前出风口

## 351. `KNOWN_CONTROL_CANDIDATE_D152EDA8D7_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_D152EDA8D7 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19419:意图1` — 关闭主驾出风口手动模式
- `train_set.jsonl:6556:意图1` — 关闭手动出风口

## 352. `KNOWN_CONTROL_CANDIDATE_D152EDA8D7_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_D152EDA8D7 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1983:意图1` — 关闭主驾出风口

## 353. `KNOWN_CONTROL_CANDIDATE_D152EDA8D7_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_D152EDA8D7 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12662:意图1` — 打开后排右出风口
- `train_set.jsonl:2944:意图2` — 打开主驾出风口
- `train_set.jsonl:4183:意图2` — 开启后排出风口

## 354. `KNOWN_CONTROL_CANDIDATE_D152EDA8D7_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_D152EDA8D7 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8149:意图1` — 打开手动出风口
- `train_set.jsonl:9423:意图1` — 副驾出风口自动化风向调成自由风

## 355. `KNOWN_CONTROL_CANDIDATE_EE2EFA7FC7_SET`

- MAC 对象: ``
- MAC 对象功能: `出风口模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_EE2EFA7FC7 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3905:意图1` — 设置出风口模式为自适应出风

## 356. `KNOWN_CONTROL_CANDIDATE_7095832C43_SET`

- MAC 对象: ``
- MAC 对象功能: `出风模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '设置为', '设置到']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7095832C43 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16044:意图1` — 副驾出风模式设置为聚焦模式
- `train_set.jsonl:2607:意图1` — 设置出风模式为自适应出风
- `train_set.jsonl:4092:意图1` — 出风模式设置到聚焦模式

## 357. `KNOWN_CONTROL_CANDIDATE_7095832C43_SET`

- MAC 对象: ``
- MAC 对象功能: `出风模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7095832C43 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3878:意图1` — 出风模式设置到上下扫风模式

## 358. `KNOWN_CONTROL_CANDIDATE_7095832C43_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `出风模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7095832C43 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8067:意图1` — 出风模式改成镜像风

## 359. `KNOWN_CONTROL_CANDIDATE_3B821DA938_SET`

- MAC 对象: ``
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3896:意图1` — 停车加热时间调长几分钟

## 360. `KNOWN_CONTROL_CANDIDATE_3B821DA938_SET`

- MAC 对象: ``
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13250:意图1` — 降低五分钟驻车加热的运行时长

## 361. `KNOWN_CONTROL_CANDIDATE_3B821DA938_SET`

- MAC 对象: ``
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11258:意图1` — 减少驻车加热运行时间

## 362. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5346:意图2` — 关闭副驾加热
- `train_set.jsonl:6033:意图1` — 关闭全车颈枕加热
- `train_set.jsonl:6165:意图1` — 关闭右侧颈枕加热
- `train_set.jsonl:8641:意图1` — 关闭前排加热

## 363. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **8**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10649:意图1` — 打开主驾驶加热按摩
- `train_set.jsonl:14739:意图4` — 打开热点打开迎宾打开音乐律动打开前排加热
- `train_set.jsonl:14856:意图2` — 把主驾和左后的座椅加热都打开
- `train_set.jsonl:15036:意图2` — 把主驾和右后座椅加热都打开
- `train_set.jsonl:16643:意图2` — 打开全车加热

## 364. `KNOWN_CONTROL_CANDIDATE_3B821DA938_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['取消']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3376:意图1` — 取消加热座椅加热

## 365. `KNOWN_CONTROL_CANDIDATE_1919984598_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `加热喷水嘴`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_1919984598 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:43:意图1` — 打开加热喷水嘴

## 366. `KNOWN_CONTROL_CANDIDATE_2F229F4179_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `单门闭锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_2F229F4179 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11168:意图1` — 关闭单门闭锁

## 367. `KNOWN_CONTROL_CANDIDATE_591AE8224D_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `去霜`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_591AE8224D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20061:意图1` — 开启后去霜

## 368. `KNOWN_CONTROL_CANDIDATE_96E33CF8F2_SET`

- MAC 对象: ``
- MAC 对象功能: `右侧出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_96E33CF8F2 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5696:意图1` — 右侧出风口往下调100
- `train_set.jsonl:8416:意图1` — 右侧出风口往左点

## 369. `KNOWN_CONTROL_CANDIDATE_98D57F98C5_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `右出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_98D57F98C5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10101:意图1` — 打开右出风口

## 370. `KNOWN_CONTROL_CANDIDATE_5DD990FB89_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `右面电动吹风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5DD990FB89 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:220:意图1` — 打开右面电动吹风口

## 371. `KNOWN_CONTROL_CANDIDATE_DCFE516D11_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `同步`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DCFE516D11 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10354:意图2` — 打开同步
- `train_set.jsonl:7097:意图1` — 打开气候同步

## 372. `KNOWN_CONTROL_CANDIDATE_DCFE516D11_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `同步`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['取消', '终止']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_DCFE516D11 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:579:意图1` — 终止温度同步
- `train_set.jsonl:4703:意图1` — 取消温度同步

## 373. `KNOWN_CONTROL_CANDIDATE_DCB247EF6B_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `吹风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_DCB247EF6B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20238:意图1` — 关闭后排吹风
- `train_set.jsonl:2010:意图1` — 关闭吹风
- `train_set.jsonl:2751:意图2` — 关闭副驾吹风

## 374. `KNOWN_CONTROL_CANDIDATE_DCB247EF6B_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `吹风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DCB247EF6B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16088:意图1` — 打开后排吹风

## 375. `KNOWN_CONTROL_CANDIDATE_868FECB9F5_SET`

- MAC 对象: ``
- MAC 对象功能: `吹风模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_868FECB9F5 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7557:意图1` — 吹风模式设置为普通模式

## 376. `KNOWN_CONTROL_CANDIDATE_868FECB9F5_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `吹风模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_868FECB9F5 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11283:意图1` — 吹风模式改为避开

## 377. `KNOWN_CONTROL_CANDIDATE_C0192390F9_SET`

- MAC 对象: ``
- MAC 对象功能: `回家照明`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C0192390F9 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12492:意图1` — 回家照明延时长一点
- `train_set.jsonl:8532:意图1` — 回家照明延时久一点

## 378. `KNOWN_CONTROL_CANDIDATE_E3BE10E0EB_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `回家照明延时`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_E3BE10E0EB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10686:意图1` — 关闭回家照明延时

## 379. `KNOWN_CONTROL_CANDIDATE_E3BE10E0EB_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `回家照明延时`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E3BE10E0EB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:423:意图1` — 打开回家照明延时

## 380. `KNOWN_CONTROL_CANDIDATE_E2E551608B_SET`

- MAC 对象: ``
- MAC 对象功能: `均衡器`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E2E551608B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6119:意图1` — 均衡器中音调低

## 381. `KNOWN_CONTROL_CANDIDATE_E2E551608B_SET`

- MAC 对象: ``
- MAC 对象功能: `均衡器`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E2E551608B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5094:意图1` — 均衡器的低音调为30

## 382. `KNOWN_CONTROL_CANDIDATE_E2E551608B_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `均衡器`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E2E551608B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5663:意图1` — 打开均衡器设置

## 383. `KNOWN_CONTROL_CANDIDATE_3BA274C95C_SET`

- MAC 对象: ``
- MAC 对象功能: `声场平衡`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3BA274C95C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4240:意图1` — 我要设置一下声场平衡好吗

## 384. `KNOWN_CONTROL_CANDIDATE_026F479C58_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `声音优化`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_026F479C58 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18626:意图1` — 打开驾驶员声音优化界面

## 385. `KNOWN_CONTROL_CANDIDATE_95FD794B2F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `声音均衡`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_95FD794B2F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:19149:意图1` — 打开声音均衡界面

## 386. `KNOWN_CONTROL_CANDIDATE_10648DC951_SET`

- MAC 对象: ``
- MAC 对象功能: `声音均衡器`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '设置一下']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_10648DC951 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:578:意图1` — 我要设置声音均衡器
- `train_set.jsonl:1372:意图1` — 设置一下声音均衡器
- `train_set.jsonl:16920:意图1` — 帮我设置声音均衡器

## 387. `KNOWN_CONTROL_CANDIDATE_10648DC951_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `声音均衡器`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['配置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_10648DC951 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12289:意图1` — 配置声音均衡器

## 388. `KNOWN_CONTROL_CANDIDATE_2F41216AB0_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `声音平衡`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2F41216AB0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8403:意图1` — 打开声音平衡

## 389. `KNOWN_CONTROL_CANDIDATE_1FEDF490D9_SET`

- MAC 对象: ``
- MAC 对象功能: `安全报警提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_1FEDF490D9 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12298:意图1` — 安全报警提示音设置为高

## 390. `KNOWN_CONTROL_CANDIDATE_50605DFC00_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `安全提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_50605DFC00 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14113:意图1` — 安全提示音设为高
- `train_set.jsonl:4121:意图1` — 安全提示音设为中

## 391. `KNOWN_CONTROL_CANDIDATE_F92B036C2B_SET`

- MAC 对象: ``
- MAC 对象功能: `安全警报提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '调节']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_F92B036C2B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11722:意图1` — 安全警报提示音设置为慢
- `train_set.jsonl:18451:意图1` — 安全警报提示音为快
- `train_set.jsonl:3249:意图1` — 调节安全警报提示音为高
- `train_set.jsonl:9833:意图1` — 调节安全警报提示音为慢

## 392. `KNOWN_CONTROL_CANDIDATE_52E53F9831_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `对外供电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['我要']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_52E53F9831 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:816:意图1` — 我要对外供电

## 393. `KNOWN_CONTROL_CANDIDATE_05A94D0E9D_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `小憩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_05A94D0E9D + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:933:意图1` — 现在把小憩模式打开二十分钟

## 394. `KNOWN_CONTROL_CANDIDATE_4A1FF175AD_SET`

- MAC 对象: ``
- MAC 对象功能: `左侧出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4A1FF175AD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3466:意图1` — 左侧出风口往上调100
- `train_set.jsonl:6278:意图1` — 主驾左侧出风口往左吹

## 395. `KNOWN_CONTROL_CANDIDATE_1BE07E051C_SET`

- MAC 对象: ``
- MAC 对象功能: `左手侧吹风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_1BE07E051C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12923:意图1` — 左手侧吹风口设为避人吹

## 396. `KNOWN_CONTROL_CANDIDATE_092D8519F2_SET`

- MAC 对象: ``
- MAC 对象功能: `左电动出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_092D8519F2 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5534:意图1` — 左电动出风口设置为左右循环模式

## 397. `KNOWN_CONTROL_CANDIDATE_092D8519F2_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `左电动出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_092D8519F2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17956:意图1` — 打开左电动出风口
- `train_set.jsonl:8578:意图1` — 打开主驾左电动出风口

## 398. `KNOWN_CONTROL_CANDIDATE_62314B9C9E_SET`

- MAC 对象: ``
- MAC 对象功能: `左边出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为', '调节']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_62314B9C9E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12018:意图1` — 左边出风口设置为上下扫风
- `train_set.jsonl:2428:意图1` — 主驾左边出风口向上吹点
- `train_set.jsonl:6361:意图1` — 副驾左边出风口向上吹点

## 399. `KNOWN_CONTROL_CANDIDATE_1D4209165B_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `干燥`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['加强']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_1D4209165B + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8580:意图1` — 我要加强干燥和智能洗的功能

## 400. `KNOWN_CONTROL_CANDIDATE_41E90574A6_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `座椅声场`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['进入']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_41E90574A6 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10688:意图1` — 进入座椅声场调节界面

## 401. `KNOWN_CONTROL_CANDIDATE_1F90D39919_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `座椅声场优化`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改变', '配置']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_1F90D39919 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20223:意图1` — 配置座椅声场优化
- `train_set.jsonl:6431:意图1` — 改变座椅声场优化

## 402. `KNOWN_CONTROL_CANDIDATE_7C9621AB04_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `延时断电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_7C9621AB04 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8824:意图1` — 关闭延时断电

## 403. `KNOWN_CONTROL_CANDIDATE_7F63C6F38C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `延迟照明`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7F63C6F38C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13415:意图1` — 开启延迟照明

## 404. `KNOWN_CONTROL_CANDIDATE_28484029B0_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `弯到照明`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_28484029B0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10008:意图1` — 我想开启弯到照明

## 405. `KNOWN_CONTROL_CANDIDATE_E157DB6D96_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `弯路照明`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_E157DB6D96 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11705:意图1` — 关闭弯路照明

## 406. `KNOWN_CONTROL_CANDIDATE_E157DB6D96_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `弯路照明`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E157DB6D96 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20486:意图1` — 打开弯路照明

## 407. `KNOWN_CONTROL_CANDIDATE_D683D647C3_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `弯道照明`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['不需要', '停掉']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_D683D647C3 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12127:意图1` — 我不需要弯道照明了
- `train_set.jsonl:4573:意图1` — 给我停掉弯道照明

## 408. `KNOWN_CONTROL_CANDIDATE_F27D7C139A_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `微升微降`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F27D7C139A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3173:意图1` — 微升微降关闭

## 409. `KNOWN_CONTROL_CANDIDATE_F27D7C139A_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `微升微降`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_F27D7C139A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12971:意图1` — 微升微降打开

## 410. `KNOWN_CONTROL_CANDIDATE_AD5BB4AEDA_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `快速充电功能`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启用']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_AD5BB4AEDA + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18656:意图1` — 启用快速充电功能

## 411. `KNOWN_CONTROL_CANDIDATE_2D1B8D10EF_SET`

- MAC 对象: ``
- MAC 对象功能: `息屏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_2D1B8D10EF + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12836:意图1` — 副驾息屏时间切换十分钟
- `train_set.jsonl:7024:意图1` — 副驾息屏时间切换两分钟

## 412. `KNOWN_CONTROL_CANDIDATE_7083C3A078_SET`

- MAC 对象: ``
- MAC 对象功能: `手机投屏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7083C3A078 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4986:意图1` — 设置手机投屏

## 413. `KNOWN_CONTROL_CANDIDATE_7083C3A078_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `手机投屏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_7083C3A078 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6818:意图1` — 我要关闭手机投屏

## 414. `KNOWN_CONTROL_CANDIDATE_7083C3A078_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `手机投屏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7083C3A078 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:103:意图1` — 我想打开手机投屏
- `train_set.jsonl:18896:意图1` — 请帮我打开手机投屏

## 415. `KNOWN_CONTROL_CANDIDATE_ADDC0C9286_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `手机蓝牙`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['链接']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_ADDC0C9286 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12916:意图1` — 链接手机蓝牙

## 416. `KNOWN_CONTROL_CANDIDATE_F842E7A37F_SET`

- MAC 对象: ``
- MAC 对象功能: `投屏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_F842E7A37F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2163:意图1` — 我要调节投屏

## 417. `KNOWN_CONTROL_CANDIDATE_F842E7A37F_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `投屏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['取消']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_F842E7A37F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14840:意图1` — 帮我取消手机投屏的运行

## 418. `KNOWN_CONTROL_CANDIDATE_84A07F292F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `折叠`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_84A07F292F + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17985:意图1` — 自动折叠打开

## 419. `KNOWN_CONTROL_CANDIDATE_816C511864_SET`

- MAC 对象: ``
- MAC 对象功能: `报警提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换成', '调', '调到']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_816C511864 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13964:意图1` — 报警提示音切换成中
- `train_set.jsonl:17078:意图1` — 报警提示音调高
- `train_set.jsonl:6951:意图1` — 报警提示音调中等
- `train_set.jsonl:8371:意图1` — 报警提示音调到20

## 420. `KNOWN_CONTROL_CANDIDATE_816C511864_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `报警提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_816C511864 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19172:意图1` — 打开报警提示音

## 421. `KNOWN_CONTROL_CANDIDATE_C967414402_SET`

- MAC 对象: ``
- MAC 对象功能: `报警音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为', '调整']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C967414402 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14123:意图1` — 报警音设置为中
- `train_set.jsonl:14825:意图1` — 报警音设置为高
- `train_set.jsonl:15923:意图1` — 调整报警音为低

## 422. `KNOWN_CONTROL_CANDIDATE_C967414402_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `报警音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设定']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_C967414402 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4435:意图1` — 设定报警音为小声

## 423. `KNOWN_CONTROL_CANDIDATE_EEA50F4175_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `按`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_EEA50F4175 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4724:意图1` — 打开左前侧肩部经典按

## 424. `KNOWN_CONTROL_CANDIDATE_4B834145B2_SET`

- MAC 对象: ``
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调节']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4B834145B2 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14352:意图2` — 家按摩强度调到最大
- `train_set.jsonl:18922:意图1` — 让按摩强度在大一些
- `train_set.jsonl:7692:意图1` — 试试更大力度的按摩

## 425. `KNOWN_CONTROL_CANDIDATE_4B834145B2_SET`

- MAC 对象: ``
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4B834145B2 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:822:意图1` — 切换按摩模式到深海冲浪

## 426. `KNOWN_CONTROL_CANDIDATE_4B834145B2_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **10**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_4B834145B2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20249:意图3` — 关闭副驾按摩
- `dev_set.jsonl:20475:意图1` — 关闭按摩
- `train_set.jsonl:11010:意图2` — 关闭按摩
- `train_set.jsonl:12463:意图2` — 关闭按摩
- `train_set.jsonl:15748:意图1` — 帮我把按摩关掉第二排右边的

## 427. `KNOWN_CONTROL_CANDIDATE_4B834145B2_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_4B834145B2 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19811:意图1` — 关闭背部放松按摩模式
- `train_set.jsonl:3232:意图1` — 关闭脊柱放松按摩模式

## 428. `KNOWN_CONTROL_CANDIDATE_4B834145B2_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '开启', '打开']`
- 唯一样本数: **60**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4B834145B2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19623:意图2` — 打开主驾按摩
- `dev_set.jsonl:19666:意图1` — 打开副驾驶按摩
- `dev_set.jsonl:19750:意图1` — 开启右后侧小腿按摩
- `dev_set.jsonl:19928:意图1` — 打开副驾按摩
- `dev_set.jsonl:19928:意图2` — 打开后排按摩

## 429. `KNOWN_CONTROL_CANDIDATE_4B834145B2_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4B834145B2 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9624:意图1` — 打开主驾按摩二挡

## 430. `KNOWN_CONTROL_CANDIDATE_4B834145B2_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4B834145B2 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14210:意图1` — 波浪按摩
- `train_set.jsonl:18183:意图1` — 上个按摩模式
- `train_set.jsonl:2677:意图1` — 主驾按摩蛇形
- `train_set.jsonl:4458:意图1` — 开启头部热放松按摩
- `train_set.jsonl:8353:意图1` — 下一个帮我换成按摩模式

## 431. `KNOWN_CONTROL_CANDIDATE_4B834145B2_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['停止', '开通', '结束']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_4B834145B2 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16104:意图1` — 后排结束按摩
- `train_set.jsonl:3494:意图1` — 后排停止按摩了
- `train_set.jsonl:7654:意图1` — 开通主驾驶按摩

## 432. `KNOWN_CONTROL_CANDIDATE_2302DF89DD_SET`

- MAC 对象: ``
- MAC 对象功能: `按摩功能`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调整']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_2302DF89DD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18625:意图1` — 把驾驶座按摩功能调整为肩部舒展
- `train_set.jsonl:18842:意图1` — 把驾驶座按摩功能调整为腰部放松
- `train_set.jsonl:8753:意图1` — 把驾驶座按摩功能调整为背部放松

## 433. `KNOWN_CONTROL_CANDIDATE_2302DF89DD_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `按摩功能`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2302DF89DD + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:726:意图2` — 开启按摩功能

## 434. `KNOWN_CONTROL_CANDIDATE_560A320DC1_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `按摩按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_560A320DC1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5713:意图1` — 打开副驾驶按摩按摩

## 435. `KNOWN_CONTROL_CANDIDATE_FC5F1EE647_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `按键声`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_FC5F1EE647 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19399:意图1` — 按键声设置关闭

## 436. `KNOWN_CONTROL_CANDIDATE_00CDBDA163_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `按键声音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_00CDBDA163 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3636:意图1` — 设置按键声音为开启

## 437. `KNOWN_CONTROL_CANDIDATE_05D1DE8019_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `按键锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_05D1DE8019 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15513:意图1` — 关闭后排按键锁

## 438. `KNOWN_CONTROL_CANDIDATE_B52AD4B40F_SET`

- MAC 对象: ``
- MAC 对象功能: `按键音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_B52AD4B40F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19995:意图1` — 按键音设置为低

## 439. `KNOWN_CONTROL_CANDIDATE_B52AD4B40F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `按键音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_B52AD4B40F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13036:意图1` — 按键音设置打开
- `train_set.jsonl:5909:意图1` — 打开系统按键音

## 440. `KNOWN_CONTROL_CANDIDATE_B52AD4B40F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `按键音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_B52AD4B40F + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5944:意图1` — 按键静音

## 441. `KNOWN_CONTROL_CANDIDATE_4656EDDD8E_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `挡风加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_4656EDDD8E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13884:意图1` — 关闭后挡风加热

## 442. `KNOWN_CONTROL_CANDIDATE_4656EDDD8E_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `挡风加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4656EDDD8E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:187:意图1` — 打开前挡风加热
- `train_set.jsonl:12208:意图1` — 开启前挡风加热
- `train_set.jsonl:17347:意图1` — 开启后挡风加热

## 443. `KNOWN_CONTROL_CANDIDATE_550E4E9F39_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `挡风喷水功能`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['给我打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_550E4E9F39 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5364:意图1` — 挡风喷水功能给我打开

## 444. `KNOWN_CONTROL_CANDIDATE_59FC9EDB05_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `接近照明`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关了']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_59FC9EDB05 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19541:意图1` — 用不着接近照明了关了吧

## 445. `KNOWN_CONTROL_CANDIDATE_59FC9EDB05_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `接近照明`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开', '打开一下']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_59FC9EDB05 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13051:意图1` — 我要打开一下接近照明好吗
- `train_set.jsonl:1969:意图2` — 打开接近照明

## 446. `KNOWN_CONTROL_CANDIDATE_59FC9EDB05_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `接近照明`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开始']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_59FC9EDB05 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19844:意图1` — 我想开始接近照明

## 447. `KNOWN_CONTROL_CANDIDATE_EE0B4E16F6_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `接近解锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_EE0B4E16F6 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18960:意图1` — 关闭接近解锁

## 448. `KNOWN_CONTROL_CANDIDATE_7A54B046A4_SET`

- MAC 对象: ``
- MAC 对象功能: `放电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7A54B046A4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1536:意图1` — 放电时间设置为3小时2分钟

## 449. `KNOWN_CONTROL_CANDIDATE_8BAECF5C1D_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `数据连接`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_8BAECF5C1D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:185:意图1` — 关闭数据连接

## 450. `KNOWN_CONTROL_CANDIDATE_7EAFA61CAC_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `方控`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7EAFA61CAC + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16425:意图1` — 方控触摸振感强度设为弱

## 451. `KNOWN_CONTROL_CANDIDATE_5341148AB3_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `无线投屏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_5341148AB3 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18857:意图1` — 关闭无线投屏

## 452. `KNOWN_CONTROL_CANDIDATE_011FDBA1DD_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `无线网络`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_011FDBA1DD + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2178:意图1` — 不准关无线网络

## 453. `KNOWN_CONTROL_CANDIDATE_011FDBA1DD_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `无线网络`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_011FDBA1DD + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13529:意图1` — 请给我查看下无线网络状态怎么样

## 454. `KNOWN_CONTROL_CANDIDATE_22406444A6_SET`

- MAC 对象: ``
- MAC 对象功能: `日出日落`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_22406444A6 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19932:意图1` — 显示模式帮我调到日出日落

## 455. `KNOWN_CONTROL_CANDIDATE_22406444A6_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `日出日落`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_22406444A6 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3846:意图1` — 日出日落改为日出

## 456. `KNOWN_CONTROL_CANDIDATE_4E1449E7D5_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `显示`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_4E1449E7D5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13291:意图1` — 显示页关闭
- `train_set.jsonl:6654:意图1` — 关闭显示页面
- `train_set.jsonl:9947:意图1` — 关闭显示系统设置

## 457. `KNOWN_CONTROL_CANDIDATE_4E1449E7D5_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `显示`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4E1449E7D5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4757:意图1` — 开启显示面板

## 458. `KNOWN_CONTROL_CANDIDATE_27D5EE172B_SET`

- MAC 对象: ``
- MAC 对象功能: `智能表面`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_27D5EE172B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9313:意图1` — 智能表面亮度调到最低

## 459. `KNOWN_CONTROL_CANDIDATE_27D5EE172B_SET`

- MAC 对象: ``
- MAC 对象功能: `智能表面`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_27D5EE172B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4256:意图1` — 智能表面切换为呼吸

## 460. `KNOWN_CONTROL_CANDIDATE_B6C817BAC3_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `智能解锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关', '关上']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_B6C817BAC3 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10255:意图1` — 智能解锁设置为关
- `train_set.jsonl:18066:意图1` — 智能解锁设置关上

## 461. `KNOWN_CONTROL_CANDIDATE_0399B6F841_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `滑移`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['暂停', '暂停一下']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_0399B6F841 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:462:意图1` — 暂停滑移调动
- `train_set.jsonl:17834:意图1` — 暂停一下滑移

## 462. `KNOWN_CONTROL_CANDIDATE_AF2154B32F_SET`

- MAC 对象: ``
- MAC 对象功能: `热点`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调出']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_AF2154B32F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19473:意图1` — 请调出热点

## 463. `KNOWN_CONTROL_CANDIDATE_AF2154B32F_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `热点`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启用下', '断', '断开下']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_AF2154B32F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19214:意图1` — 帮我断开下热点
- `dev_set.jsonl:19883:意图1` — 请现在为我热点帮我断
- `train_set.jsonl:7914:意图1` — 马上帮我启用下热点

## 464. `KNOWN_CONTROL_CANDIDATE_7FAD9A4D54_SET`

- MAC 对象: ``
- MAC 对象功能: `照我回家`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7FAD9A4D54 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2152:意图1` — 照我回家设置为60秒

## 465. `KNOWN_CONTROL_CANDIDATE_574E065602_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `狭窄道路`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_574E065602 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3765:意图1` — 狭窄道路开启影像

## 466. `KNOWN_CONTROL_CANDIDATE_F63ECFAA19_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `环视退出`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F63ECFAA19 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20437:意图1` — 关闭环视退出

## 467. `KNOWN_CONTROL_CANDIDATE_955BA18090_SET`

- MAC 对象: ``
- MAC 对象功能: `电动出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换为', '设置为']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_955BA18090 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18339:意图1` — 主驾电动出风口设置为上下扫风
- `train_set.jsonl:6993:意图1` — 右边电动出风口设置为上下扫风
- `train_set.jsonl:8567:意图1` — 二排电动出风口切换为左右扫风模式

## 468. `KNOWN_CONTROL_CANDIDATE_955BA18090_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `电动出风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_955BA18090 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13711:意图1` — 打开主驾电动出风口

## 469. `KNOWN_CONTROL_CANDIDATE_B9FA68F21F_SET`

- MAC 对象: ``
- MAC 对象功能: `电动吹风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_B9FA68F21F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2829:意图1` — 后排电动吹风口切换为对人吹模式

## 470. `KNOWN_CONTROL_CANDIDATE_B9FA68F21F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `电动吹风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_B9FA68F21F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7714:意图1` — 打开三排电动吹风口

## 471. `KNOWN_CONTROL_CANDIDATE_EE0044541A_SET`

- MAC 对象: ``
- MAC 对象功能: `白天黑夜`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调整为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_EE0044541A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19942:意图1` — 白天黑夜模式调整为黑夜

## 472. `KNOWN_CONTROL_CANDIDATE_71105E1445_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `短升短降`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_71105E1445 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17342:意图1` — 关闭短升短降
- `train_set.jsonl:8544:意图1` — 短升短降关闭

## 473. `KNOWN_CONTROL_CANDIDATE_7698C5E12F_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `离子净化器`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_7698C5E12F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2361:意图1` — 关闭离子净化器

## 474. `KNOWN_CONTROL_CANDIDATE_843D5FBFB8_SET`

- MAC 对象: ``
- MAC 对象功能: `离家照明延时`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_843D5FBFB8 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17030:意图1` — 离家照明延时中间值

## 475. `KNOWN_CONTROL_CANDIDATE_E3420F2548_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `离车自动落锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['看看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_E3420F2548 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16020:意图1` — 看看离车自动落锁设置页面

## 476. `KNOWN_CONTROL_CANDIDATE_FF7967C2B9_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `移动数据`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_FF7967C2B9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12901:意图1` — 关闭移动数据

## 477. `KNOWN_CONTROL_CANDIDATE_61E7CE5332_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `窗户锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['落锁']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_61E7CE5332 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:438:意图1` — 窗户锁落锁

## 478. `KNOWN_CONTROL_CANDIDATE_AA6D64CBC1_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `窗洗涤模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_AA6D64CBC1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12684:意图1` — 打开后窗洗涤模式

## 479. `KNOWN_CONTROL_CANDIDATE_0F68010BC4_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `童锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关', '关掉']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_0F68010BC4 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1039:意图1` — 给我关掉童锁
- `train_set.jsonl:16097:意图1` — 帮我关童锁

## 480. `KNOWN_CONTROL_CANDIDATE_0F68010BC4_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `童锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_0F68010BC4 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4085:意图2` — 打开童锁

## 481. `KNOWN_CONTROL_CANDIDATE_B31226A162_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `等离子`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_B31226A162 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18269:意图1` — 关闭等离子

## 482. `KNOWN_CONTROL_CANDIDATE_B31226A162_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `等离子`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_B31226A162 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:131:意图1` — 打开等离子

## 483. `KNOWN_CONTROL_CANDIDATE_2BA4B68C44_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `系统应用`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['进入']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_2BA4B68C44 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19444:意图2` — 进入应用

## 484. `KNOWN_CONTROL_CANDIDATE_88FB5F1B26_SET`

- MAC 对象: ``
- MAC 对象功能: `续航`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_88FB5F1B26 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20494:意图1` — 续航模式切换为标准续航
- `train_set.jsonl:17637:意图1` — 续航模式切换为动态模式
- `train_set.jsonl:5685:意图1` — 切换续航模式为标准模式

## 485. `KNOWN_CONTROL_CANDIDATE_ECC6E00146_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `网`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['查看', '联']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_ECC6E00146 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1569:意图1` — 现在联网了没有呢
- `train_set.jsonl:1849:意图1` — 请给我查下无线网当前的怎样

## 486. `KNOWN_CONTROL_CANDIDATE_97B31B5D63_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `网络`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_97B31B5D63 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4455:意图2` — 关闭网络

## 487. `KNOWN_CONTROL_CANDIDATE_97B31B5D63_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `网络`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_97B31B5D63 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18283:意图1` — 打开网络

## 488. `KNOWN_CONTROL_CANDIDATE_97B31B5D63_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `网络`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['查看', '连接']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_97B31B5D63 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15011:意图1` — 我要查看下网络的怎样
- `train_set.jsonl:16733:意图1` — 连接网络

## 489. `KNOWN_CONTROL_CANDIDATE_C5E8F9C722_SET`

- MAC 对象: ``
- MAC 对象功能: `肩部`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C5E8F9C722 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20403:意图1` — 肩部前移
- `train_set.jsonl:10602:意图1` — 前面肩部前移

## 490. `KNOWN_CONTROL_CANDIDATE_8A2BE2AC4F_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `背光联动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_8A2BE2AC4F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:39:意图1` — 请为背光联动开关设置关闭状态
- `train_set.jsonl:3734:意图1` — 关闭背光联动

## 491. `KNOWN_CONTROL_CANDIDATE_8A2BE2AC4F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `背光联动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_8A2BE2AC4F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7423:意图1` — 请设置背光联动为开启状态

## 492. `KNOWN_CONTROL_CANDIDATE_CD4FA402F6_SET`

- MAC 对象: ``
- MAC 对象功能: `节电延时`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_CD4FA402F6 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18859:意图1` — 节电延时最短

## 493. `KNOWN_CONTROL_CANDIDATE_AA86FAACD6_SET`

- MAC 对象: ``
- MAC 对象功能: `蓝牙`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_AA86FAACD6 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:17:意图1` — 蓝牙通话声响大一些

## 494. `KNOWN_CONTROL_CANDIDATE_AA86FAACD6_SET`

- MAC 对象: ``
- MAC 对象功能: `蓝牙`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['修改', '调节']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_AA86FAACD6 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11290:意图1` — 蓝牙通话的声音需要被调整到40%
- `train_set.jsonl:13764:意图1` — 蓝牙通话声音小一些
- `train_set.jsonl:16635:意图1` — 我想要修改一下蓝牙的声音大小
- `train_set.jsonl:4867:意图1` — 蓝牙通话声音小一点

## 495. `KNOWN_CONTROL_CANDIDATE_AA86FAACD6_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `蓝牙`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['断开', '断开一下', '查看', '连接']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_AA86FAACD6 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:126:意图1` — 开启蓝牙连接
- `train_set.jsonl:10065:意图1` — 打开蓝牙的连接
- `train_set.jsonl:13262:意图1` — 查看蓝牙启动了没有
- `train_set.jsonl:15470:意图1` — 蓝牙连接
- `train_set.jsonl:16822:意图1` — 断开一下蓝牙吧

## 496. `KNOWN_CONTROL_CANDIDATE_D8271BE46C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `蓝牙主动降噪`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_D8271BE46C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5912:意图1` — 打开蓝牙主动降噪

## 497. `KNOWN_CONTROL_CANDIDATE_EA929795AB_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `蓝牙可见搜索`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_EA929795AB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20347:意图1` — 打开蓝牙可见搜索

## 498. `KNOWN_CONTROL_CANDIDATE_EF3146156B_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `蓝牙通话降噪`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_EF3146156B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16423:意图1` — 打开蓝牙通话降噪

## 499. `KNOWN_CONTROL_CANDIDATE_41B98B043F_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `行人提醒音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_41B98B043F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:19027:意图1` — 打开行人提醒音

## 500. `KNOWN_CONTROL_CANDIDATE_99EF6E9069_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `行人警示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_99EF6E9069 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11376:意图1` — 关闭行人警示音
- `train_set.jsonl:11763:意图2` — 关闭行人警示音
- `train_set.jsonl:14919:意图2` — 关闭行人警示音
- `train_set.jsonl:18392:意图1` — 关闭行人警示音
- `train_set.jsonl:18734:意图3` — 打开主副驾驶座椅按摩关闭行人警示音

## 501. `KNOWN_CONTROL_CANDIDATE_99EF6E9069_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `行人警示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_99EF6E9069 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19187:意图1` — 打开行人警示音

## 502. `KNOWN_CONTROL_CANDIDATE_BD5E2948B9_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `行车低速提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BD5E2948B9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2886:意图1` — 关闭行车低速提示音

## 503. `KNOWN_CONTROL_CANDIDATE_386F2B1321_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `行车关窗`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_386F2B1321 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5141:意图1` — 打开行车关窗

## 504. `KNOWN_CONTROL_CANDIDATE_478B52AD6E_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `行车自动落锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_478B52AD6E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10936:意图1` — 打开行车自动落锁

## 505. `KNOWN_CONTROL_CANDIDATE_EC2FD79C56_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `观影角度`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关了']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_EC2FD79C56 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17689:意图1` — 观影角度关了

## 506. `KNOWN_CONTROL_CANDIDATE_9743931067_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `设备管理器`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_9743931067 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10837:意图1` — 打开设备管理器菜单

## 507. `KNOWN_CONTROL_CANDIDATE_0690306E19_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `设备连接器`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['显示']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_0690306E19 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20368:意图1` — 显示设备连接器菜单

## 508. `KNOWN_CONTROL_CANDIDATE_396CC125D2_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `负离子`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_396CC125D2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14945:意图1` — 打开负离子设置项

## 509. `KNOWN_CONTROL_CANDIDATE_20BF90499E_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `负离子净化`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_20BF90499E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4676:意图1` — 关闭负离子净化
- `train_set.jsonl:5359:意图1` — 关闭负离子净化

## 510. `KNOWN_CONTROL_CANDIDATE_6B80AD4BBC_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `负离子功能`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_6B80AD4BBC + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5244:意图1` — 帮我打开负离子功能

## 511. `KNOWN_CONTROL_CANDIDATE_EAA465B8DC_SET`

- MAC 对象: ``
- MAC 对象功能: `车外低速报警`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_EAA465B8DC + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6532:意图1` — 为了更安全行驶请帮我设置车外低速报警

## 512. `KNOWN_CONTROL_CANDIDATE_EAA465B8DC_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `车外低速报警`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关上', '关闭']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_EAA465B8DC + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:291:意图1` — 车外低速报警配置关上
- `test_set.jsonl:906:意图1` — 关闭车外低速报警
- `train_set.jsonl:11712:意图2` — 关闭车外低速报警
- `train_set.jsonl:15110:意图1` — 关闭车外低速报警
- `train_set.jsonl:2521:意图3` — 关闭车外低速报警

## 513. `KNOWN_CONTROL_CANDIDATE_EAA465B8DC_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `车外低速报警`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_EAA465B8DC + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9553:意图1` — 打开车外低速报警

## 514. `KNOWN_CONTROL_CANDIDATE_3C2C82646D_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `车外低速报警音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3C2C82646D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7466:意图1` — 上一个车外低速报警音

## 515. `KNOWN_CONTROL_CANDIDATE_9C328A1757_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `车外低速提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_9C328A1757 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7306:意图1` — 关闭车外低速提示音

## 516. `KNOWN_CONTROL_CANDIDATE_1C2A99D6B1_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `车外低速警示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_1C2A99D6B1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15673:意图1` — 关闭车外低速警示音

## 517. `KNOWN_CONTROL_CANDIDATE_91B06664C7_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `车外报警`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_91B06664C7 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20141:意图2` — 打开车外报警

## 518. `KNOWN_CONTROL_CANDIDATE_0313CB02A2_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `车外报警音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_0313CB02A2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18472:意图2` — 关闭车外报警音

## 519. `KNOWN_CONTROL_CANDIDATE_48912DF152_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `车外提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_48912DF152 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19733:意图4` — 打开主副驾驶座椅加热和方向盘加热关闭车外提示音
- `train_set.jsonl:15216:意图1` — 关闭车外提示音
- `train_set.jsonl:16489:意图1` — 关闭车外提示音
- `train_set.jsonl:4814:意图1` — 关闭车外提示音

## 520. `KNOWN_CONTROL_CANDIDATE_EB3951D0E9_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `车外的声音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_EB3951D0E9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17311:意图1` — 关闭车外的声音

## 521. `KNOWN_CONTROL_CANDIDATE_2DC7DF82A0_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `车外行人提示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_2DC7DF82A0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8144:意图1` — 关闭车外行人提示音

## 522. `KNOWN_CONTROL_CANDIDATE_BF38DB5A7C_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `车外警示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BF38DB5A7C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8747:意图1` — 关闭车外警示音

## 523. `KNOWN_CONTROL_CANDIDATE_43EAB7DC5E_SET`

- MAC 对象: ``
- MAC 对象功能: `车模`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换', '切换到']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_43EAB7DC5E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11454:意图1` — 车模颜色切换到卡其白
- `train_set.jsonl:14405:意图1` — 车模颜色切换白色

## 524. `KNOWN_CONTROL_CANDIDATE_69D80D61EF_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `车载热点`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_69D80D61EF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8695:意图1` — 没网络给我打开车载热点开关

## 525. `KNOWN_CONTROL_CANDIDATE_69D80D61EF_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `车载热点`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['断']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_69D80D61EF + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:569:意图1` — 暂时不需要车载热点给我把接口断了

## 526. `KNOWN_CONTROL_CANDIDATE_C5C822B355_SET`

- MAC 对象: ``
- MAC 对象功能: `车辆报警音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节', '调节为']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C5C822B355 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1056:意图1` — 车辆报警音帮我调节中
- `train_set.jsonl:7104:意图1` — 车辆报警音调节为高
- `train_set.jsonl:7745:意图1` — 车辆报警音最低

## 527. `KNOWN_CONTROL_CANDIDATE_5AD18D1F89_SET`

- MAC 对象: ``
- MAC 对象功能: `车辆警示音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5AD18D1F89 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6232:意图1` — 车辆警示音调高

## 528. `KNOWN_CONTROL_CANDIDATE_DE646D5E1E_SET`

- MAC 对象: ``
- MAC 对象功能: `车速自动关窗`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_DE646D5E1E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11274:意图1` — 车速自动关窗设为80千米每小时

## 529. `KNOWN_CONTROL_CANDIDATE_DE646D5E1E_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `车速自动关窗`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_DE646D5E1E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1959:意图1` — 车速自动关窗切为每小时60公里

## 530. `KNOWN_CONTROL_CANDIDATE_00A7DD6FA9_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `转向联动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_00A7DD6FA9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5159:意图1` — 关闭转向联动

## 531. `KNOWN_CONTROL_CANDIDATE_044786200C_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `迎宾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_044786200C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14705:意图2` — 关闭迎宾
- `train_set.jsonl:18306:意图2` — 关闭迎宾

## 532. `KNOWN_CONTROL_CANDIDATE_044786200C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `迎宾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_044786200C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:167:意图2` — 打开迎宾
- `train_set.jsonl:14739:意图2` — 打开迎宾打开音乐律动
- `train_set.jsonl:17471:意图4` — 打开迎宾
- `train_set.jsonl:3713:意图3` — 打开迎宾
- `train_set.jsonl:7595:意图1` — 打开迎宾打开音乐律动

## 533. `KNOWN_CONTROL_CANDIDATE_395006C615_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `这台车热点`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_395006C615 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:19127:意图1` — 打开这台车热点

## 534. `KNOWN_CONTROL_CANDIDATE_1ACE8D9A05_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `进入窄道时开启预览`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_1ACE8D9A05 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5679:意图1` — 进入窄道时开启预览

## 535. `KNOWN_CONTROL_CANDIDATE_08BD1AD5F3_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `连接管理器`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_08BD1AD5F3 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13079:意图1` — 打开连接管理器

## 536. `KNOWN_CONTROL_CANDIDATE_955C13441A_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `透气`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_955C13441A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11369:意图2` — 透气模式

## 537. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **10**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19893:意图1` — 关闭通风
- `test_set.jsonl:228:意图1` — 关闭全车通风
- `train_set.jsonl:11675:意图1` — 关闭通风
- `train_set.jsonl:11845:意图1` — 关掉通风
- `train_set.jsonl:13321:意图1` — 关闭通风

## 538. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **38**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19480:意图1` — 打开前排通风
- `dev_set.jsonl:20038:意图2` — 副驾通风
- `test_set.jsonl:407:意图1` — 打开主驾通风
- `test_set.jsonl:494:意图2` — 打开通风
- `test_set.jsonl:849:意图1` — 打开通风

## 539. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6449:意图2` — 打开自通风

## 540. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改为']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15766:意图2` — 改为通风
- `train_set.jsonl:18577:意图2` — 改为通风模式

## 541. `KNOWN_CONTROL_CANDIDATE_E389FF8EA4_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `通风模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '开启', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E389FF8EA4 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13075:意图2` — 打开通风模式
- `train_set.jsonl:3254:意图2` — 开启通风模式
- `train_set.jsonl:9817:意图2` — 能打开通风模式

## 542. `KNOWN_CONTROL_CANDIDATE_9382DC7432_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `锁车关窗`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_9382DC7432 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12775:意图1` — 打开锁车关窗页面

## 543. `KNOWN_CONTROL_CANDIDATE_61EA48222A_SET`

- MAC 对象: ``
- MAC 对象功能: `锁车反馈`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_61EA48222A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11316:意图1` — 锁车反馈模式切换为鸣笛
- `train_set.jsonl:17454:意图1` — 锁车反馈模式切换为灯光鸣笛

## 544. `KNOWN_CONTROL_CANDIDATE_AEEB8A16B6_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `闭锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_AEEB8A16B6 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:392:意图1` — 我要锁车

## 545. `KNOWN_CONTROL_CANDIDATE_F68661851E_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `闭锁关窗`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F68661851E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9271:意图1` — 关闭闭锁关窗

## 546. `KNOWN_CONTROL_CANDIDATE_66F9F303EE_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `除湿模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_66F9F303EE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4572:意图1` — 除湿模式给我关一下

## 547. `KNOWN_CONTROL_CANDIDATE_66F9F303EE_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `除湿模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_66F9F303EE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10192:意图1` — 把除湿模式开一下

## 548. `KNOWN_CONTROL_CANDIDATE_789DBC8273_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `随动座椅`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_789DBC8273 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9743:意图1` — 打开副驾随动座椅

## 549. `KNOWN_CONTROL_CANDIDATE_789DBC8273_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `随动座椅`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_789DBC8273 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12602:意图1` — 主驾随动座椅强度设为3挡

## 550. `KNOWN_CONTROL_CANDIDATE_030B7A7207_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `零重力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_030B7A7207 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3769:意图1` — 关闭左侧右侧零重力
- `train_set.jsonl:3769:意图2` — 关闭左侧右侧零重力

## 551. `KNOWN_CONTROL_CANDIDATE_030B7A7207_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `零重力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_030B7A7207 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14690:意图1` — 我要享受零重力模式

## 552. `KNOWN_CONTROL_CANDIDATE_322DF5FBC3_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `靠近照明`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_322DF5FBC3 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16129:意图1` — 关闭靠近照明

## 553. `KNOWN_CONTROL_CANDIDATE_899FB45C31_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `靠近解锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_899FB45C31 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19208:意图1` — 关闭靠近解锁

## 554. `KNOWN_CONTROL_CANDIDATE_D660104225_SET`

- MAC 对象: ``
- MAC 对象功能: `音效加强`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_D660104225 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5205:意图1` — 设置音效加强

## 555. `KNOWN_CONTROL_CANDIDATE_9242B7BE0F_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `风口`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_9242B7BE0F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6922:意图1` — 关闭三排风口

## 556. `KNOWN_CONTROL_CANDIDATE_3E41BC3FA9_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `风扇`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关一下', '关掉', '关闭']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3E41BC3FA9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19820:意图2` — 关闭风扇
- `dev_set.jsonl:19996:意图1` — 风扇帮我关一下
- `train_set.jsonl:15995:意图1` — 把风扇关闭
- `train_set.jsonl:8564:意图1` — 关掉风扇

## 557. `KNOWN_CONTROL_CANDIDATE_3E41BC3FA9_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `风扇`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3E41BC3FA9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2115:意图1` — 打开左后风扇
- `train_set.jsonl:3796:意图2` — 打开风扇
- `train_set.jsonl:3996:意图1` — 打开主驾风扇

## 558. `KNOWN_CONTROL_CANDIDATE_3E41BC3FA9_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `风扇`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3E41BC3FA9 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16426:意图1` — 将第二排风扇开到最高

## 559. `KNOWN_CONTROL_CANDIDATE_C6EC75F595_TURN_OFF`

- MAC 对象: ``
- MAC 对象功能: `风挡加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_C6EC75F595 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12768:意图1` — 停用挡风玻璃的热力

## 560. `KNOWN_CONTROL_CANDIDATE_C6EC75F595_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `风挡加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_C6EC75F595 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17766:意图1` — 后风挡加热打开

## 561. `KNOWN_CONTROL_CANDIDATE_CB72B3599C_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `风挡喷玻璃水`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_CB72B3599C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:19122:意图1` — 打开前风挡喷玻璃水

## 562. `KNOWN_CONTROL_CANDIDATE_7F87E8738B_TURN_ON`

- MAC 对象: ``
- MAC 对象功能: `风窗加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7F87E8738B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17043:意图1` — 打开后风窗加热开关

## 563. `KNOWN_CONTROL_CANDIDATE_7F87E8738B_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `风窗加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7F87E8738B + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1247:意图1` — 后风窗加热开关开下

## 564. `KNOWN_CONTROL_CANDIDATE_7D5331B89A_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `驻车档解锁功能`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['取消']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7D5331B89A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13654:意图1` — 驻车档解锁功能取消

## 565. `KNOWN_CONTROL_CANDIDATE_103FA99B8D_REVIEW`

- MAC 对象: ``
- MAC 对象功能: `驻车解锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['进入']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_103FA99B8D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9159:意图1` — 进入驻车解锁设置页面

## 566. `KNOWN_CONTROL_CANDIDATE_C40C747EE7_SET`

- MAC 对象: `HUD`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C40C747EE7 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2339:意图2` — 调节hud
- `train_set.jsonl:5521:意图1` — 调节hud

## 567. `KNOWN_CONTROL_CANDIDATE_BCD77FFC7E_SET`

- MAC 对象: `一体屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BCD77FFC7E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:395:意图1` — 调低一体屏亮度

## 568. `KNOWN_CONTROL_CANDIDATE_5A864AB7B1_TURN_ON`

- MAC 对象: `上面的窗帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5A864AB7B1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6288:意图1` — 上面的窗帘给我开启

## 569. `KNOWN_CONTROL_CANDIDATE_5A864AB7B1_REVIEW`

- MAC 对象: `上面的窗帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['展开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5A864AB7B1 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3179:意图1` — 展开上面的窗帘

## 570. `KNOWN_CONTROL_CANDIDATE_1BEB67202D_TURN_OFF`

- MAC 对象: `中控`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_1BEB67202D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20010:意图1` — 中控熄屏
- `train_set.jsonl:2756:意图1` — 中控息屏
- `train_set.jsonl:8775:意图2` — 中控息屏

## 571. `KNOWN_CONTROL_CANDIDATE_666918A03F_TURN_ON`

- MAC 对象: `中控`
- MAC 对象功能: `放倒`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_666918A03F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4591:意图1` — 中控放倒

## 572. `KNOWN_CONTROL_CANDIDATE_B7E4299CCA_TURN_OFF`

- MAC 对象: `中控台`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_B7E4299CCA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14758:意图1` — 关闭中控台

## 573. `KNOWN_CONTROL_CANDIDATE_C49230AAE5_TURN_OFF`

- MAC 对象: `中控大屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_C49230AAE5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19824:意图1` — 关闭中控大屏
- `test_set.jsonl:518:意图1` — 关闭中控大屏

## 574. `KNOWN_CONTROL_CANDIDATE_C49230AAE5_REVIEW`

- MAC 对象: `中控大屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑动下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_C49230AAE5 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18486:意图1` — 滑动下中控大屏

## 575. `KNOWN_CONTROL_CANDIDATE_C49230AAE5_REVIEW`

- MAC 对象: `中控大屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑一下', '移一下']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_C49230AAE5 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15705:意图1` — 滑一下中控大屏到另外一侧
- `train_set.jsonl:2475:意图1` — 中控大屏主驾位置移一下

## 576. `KNOWN_CONTROL_CANDIDATE_A6753CC072_REVIEW`

- MAC 对象: `中控屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑一下', '滑动点']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A6753CC072 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5493:意图1` — 给我滑一下中控屏
- `train_set.jsonl:8625:意图1` — 中控屏滑动点

## 577. `KNOWN_CONTROL_CANDIDATE_71447F5B43_SET`

- MAC 对象: `中控屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调节']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_71447F5B43 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:992:意图1` — 中控屏幕亮度降低10%
- `train_set.jsonl:16142:意图1` — 中控屏幕亮度调到10%
- `train_set.jsonl:5573:意图1` — 中控屏幕亮度暗一点
- `train_set.jsonl:7230:意图1` — 中控屏幕调亮一点

## 578. `KNOWN_CONTROL_CANDIDATE_71447F5B43_ADJUST`

- MAC 对象: `中控屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_71447F5B43 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7261:意图1` — 请将中控屏幕移动回主驾

## 579. `KNOWN_CONTROL_CANDIDATE_71447F5B43_TURN_OFF`

- MAC 对象: `中控屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_71447F5B43 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3412:意图2` — 关闭中控屏幕

## 580. `KNOWN_CONTROL_CANDIDATE_6835FFC27B_SET`

- MAC 对象: `中控扶手`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_6835FFC27B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11069:意图1` — 中控扶手到车后面

## 581. `KNOWN_CONTROL_CANDIDATE_6835FFC27B_ADJUST`

- MAC 对象: `中控扶手`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑', '移']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_6835FFC27B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19478:意图1` — 中控扶手移到前面
- `train_set.jsonl:13392:意图1` — 后面太挤帮忙把中控扶手向后滑

## 582. `KNOWN_CONTROL_CANDIDATE_7CA05B9537_TURN_OFF`

- MAC 对象: `中控显示屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_7CA05B9537 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14963:意图1` — 关闭中控显示屏

## 583. `KNOWN_CONTROL_CANDIDATE_7CA05B9537_REVIEW`

- MAC 对象: `中控显示屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑动一点']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7CA05B9537 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4989:意图1` — 中控显示屏滑动一点

## 584. `KNOWN_CONTROL_CANDIDATE_D887E9C49B_SET`

- MAC 对象: `中控面板`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_D887E9C49B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8846:意图1` — 设定中控面板亮度为40%

## 585. `KNOWN_CONTROL_CANDIDATE_F275696B5F_SET`

- MAC 对象: `中间储物台`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_F275696B5F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19354:意图1` — 后面太挤把中间储物台向后座位置
- `train_set.jsonl:8287:意图1` — 中间储物台到后排

## 586. `KNOWN_CONTROL_CANDIDATE_732789AB3E_ADJUST`

- MAC 对象: `中间放东西的柜子`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑', '滑动']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_732789AB3E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14810:意图1` — 中间放东西的柜子滑到前方
- `train_set.jsonl:2899:意图1` — 后面太挤了帮忙把中间放东西的柜子朝车后面滑动

## 587. `KNOWN_CONTROL_CANDIDATE_E1108B4AD3_SET`

- MAC 对象: `中间的柜子`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E1108B4AD3 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:779:意图1` — 后面太挤给我把中间的柜子朝前面

## 588. `KNOWN_CONTROL_CANDIDATE_E1108B4AD3_ADJUST`

- MAC 对象: `中间的柜子`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_E1108B4AD3 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16001:意图1` — 中间的柜子滑到车后面

## 589. `KNOWN_CONTROL_CANDIDATE_61FEE02030_TURN_ON`

- MAC 对象: `主动扩散器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_61FEE02030 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14148:意图1` — 打开主动扩散器检修

## 590. `KNOWN_CONTROL_CANDIDATE_4FB8FC078C_ADJUST`

- MAC 对象: `主屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_4FB8FC078C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8183:意图1` — 主屏右移动

## 591. `KNOWN_CONTROL_CANDIDATE_D57D9BD743_ADJUST`

- MAC 对象: `主屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_D57D9BD743 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:908:意图1` — 滑动主屏幕

## 592. `KNOWN_CONTROL_CANDIDATE_D57D9BD743_TURN_OFF`

- MAC 对象: `主屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_D57D9BD743 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18079:意图2` — 关闭主屏幕
- `train_set.jsonl:5953:意图1` — 关闭主屏幕

## 593. `KNOWN_CONTROL_CANDIDATE_45B48CFA19_REVIEW`

- MAC 对象: `主显示屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['回到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_45B48CFA19 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:28:意图1` — 主显示屏回到首页

## 594. `KNOWN_CONTROL_CANDIDATE_5B12EC991C_SET`

- MAC 对象: `交互灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5B12EC991C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1048:意图1` — 交互灯亮度调到最小
- `train_set.jsonl:14072:意图1` — 把交互灯亮度改为2
- `train_set.jsonl:18546:意图1` — 交互灯亮度切换为最大
- `train_set.jsonl:6964:意图1` — 交互灯亮度降低三档
- `train_set.jsonl:8771:意图1` — 交互灯亮度调高一点

## 595. `KNOWN_CONTROL_CANDIDATE_83028488B9_TURN_OFF`

- MAC 对象: `交流充电口盖`
- MAC 对象功能: `交流电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_83028488B9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:825:意图1` — 关闭交流充电口盖

## 596. `KNOWN_CONTROL_CANDIDATE_83028488B9_TURN_ON`

- MAC 对象: `交流充电口盖`
- MAC 对象功能: `交流电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_83028488B9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15560:意图1` — 打开交流充电口盖

## 597. `KNOWN_CONTROL_CANDIDATE_83028488B9_TURN_OFF`

- MAC 对象: `交流接口盖`
- MAC 对象功能: `交流电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_83028488B9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:953:意图1` — 关闭交流接口盖

## 598. `KNOWN_CONTROL_CANDIDATE_5503E3C1B0_TURN_ON`

- MAC 对象: `交流直流二合一充电口盖`
- MAC 对象功能: `交直流电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5503E3C1B0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1109:意图1` — 打开交流直流二合一充电口盖

## 599. `KNOWN_CONTROL_CANDIDATE_83028488B9_REVIEW`

- MAC 对象: `交流端盖`
- MAC 对象功能: `交流电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['合上']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_83028488B9 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3138:意图1` — 合上交流端盖

## 600. `KNOWN_CONTROL_CANDIDATE_BDE032DB2F_SET`

- MAC 对象: `仪表`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '调', '调节']`
- 唯一样本数: **7**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BDE032DB2F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10333:意图1` — 仪表亮度调到中间值
- `train_set.jsonl:13278:意图1` — 仪表调到最亮
- `train_set.jsonl:19141:意图1` — 把仪表调暗一点
- `train_set.jsonl:2017:意图1` — 设置仪表亮度
- `train_set.jsonl:2519:意图1` — 让仪表在现有亮度的基础上再增加10%

## 601. `KNOWN_CONTROL_CANDIDATE_BDE032DB2F_SET`

- MAC 对象: `仪表`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BDE032DB2F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16545:意图1` — 设置仪表明暗

## 602. `KNOWN_CONTROL_CANDIDATE_BDE032DB2F_SET`

- MAC 对象: `仪表`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BDE032DB2F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17049:意图1` — 仪表模式设置为简洁模式

## 603. `KNOWN_CONTROL_CANDIDATE_BDE032DB2F_REVIEW`

- MAC 对象: `仪表`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改为', '显示']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_BDE032DB2F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10102:意图1` — 仪表显示为经典模式
- `train_set.jsonl:5321:意图1` — 仪表和多媒体显示屏改为白天模式

## 604. `KNOWN_CONTROL_CANDIDATE_24FA4AB998_SET`

- MAC 对象: `仪表`
- MAC 对象功能: ``
- MAC 功能: `疲劳驾驶时长`
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_24FA4AB998 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2979:意图1` — 仪表疲劳驾驶时长设置为1小时

## 605. `KNOWN_CONTROL_CANDIDATE_22EA3F47FE_SET`

- MAC 对象: `仪表`
- MAC 对象功能: `全屏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_22EA3F47FE + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3708:意图1` — 仪表导航设置为全屏

## 606. `KNOWN_CONTROL_CANDIDATE_88FB5F1B26_SET`

- MAC 对象: `仪表`
- MAC 对象功能: `续航`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_88FB5F1B26 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12190:意图1` — 仪表续航显示切换为动态

## 607. `KNOWN_CONTROL_CANDIDATE_9624BECE8C_SET`

- MAC 对象: `仪表屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '调']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_9624BECE8C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13650:意图1` — 仪表屏设置为低
- `train_set.jsonl:4020:意图1` — 仪表屏调为百分之五
- `train_set.jsonl:4089:意图3` — 仪表屏亮度调到最低

## 608. `KNOWN_CONTROL_CANDIDATE_702D4096D3_TURN_OFF`

- MAC 对象: `仪表屏屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_702D4096D3 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12408:意图1` — 关闭仪表屏屏幕

## 609. `KNOWN_CONTROL_CANDIDATE_46770BC369_TURN_ON`

- MAC 对象: `仪表屏的`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_46770BC369 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5959:意图1` — 仪表屏的私密模式开关打开

## 610. `KNOWN_CONTROL_CANDIDATE_7C9801D13A_REVIEW`

- MAC 对象: `仪表显示`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['进入']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7C9801D13A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10422:意图1` — 进入仪表显示亮度设置界面

## 611. `KNOWN_CONTROL_CANDIDATE_6FDDC985BC_SET`

- MAC 对象: `仪表显示的屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_6FDDC985BC + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:234:意图1` — 仪表显示的屏幕的亮度调低一些

## 612. `KNOWN_CONTROL_CANDIDATE_7E284C2DF7_REVIEW`

- MAC 对象: `仪表板`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['激活']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7E284C2DF7 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11467:意图1` — 激活仪表板上的驾驶舱显示器

## 613. `KNOWN_CONTROL_CANDIDATE_0853BF3C01_SET`

- MAC 对象: `仪表盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '调', '调节']`
- 唯一样本数: **11**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_0853BF3C01 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20207:意图1` — 让仪表显示最大亮度
- `test_set.jsonl:989:意图2` — 仪表盘亮度调到最亮
- `train_set.jsonl:12637:意图1` — 看不太清帮我调亮仪表盘
- `train_set.jsonl:13675:意图1` — 帮我把仪表亮度往弱的那个方向调暗10%
- `train_set.jsonl:17111:意图1` — 我喜欢看亮度比当前弱10%的仪表

## 614. `KNOWN_CONTROL_CANDIDATE_0853BF3C01_TURN_OFF`

- MAC 对象: `仪表盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_0853BF3C01 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:117:意图2` — 关闭仪表盘

## 615. `KNOWN_CONTROL_CANDIDATE_0853BF3C01_REVIEW`

- MAC 对象: `仪表盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['换成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_0853BF3C01 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17700:意图1` — 你能帮我把仪表盘显示模式换成狂暴模式吗

## 616. `KNOWN_CONTROL_CANDIDATE_ACA912A984_SET`

- MAC 对象: `侧翼`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **8**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_ACA912A984 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19538:意图1` — 侧翼太紧主驾的
- `train_set.jsonl:14990:意图1` — 主驾侧翼松一点
- `train_set.jsonl:16565:意图1` — 左后侧翼紧一点
- `train_set.jsonl:1687:意图1` — 右后侧翼紧一点
- `train_set.jsonl:18081:意图2` — 主驾侧翼紧一点

## 617. `KNOWN_CONTROL_CANDIDATE_ACA912A984_TURN_OFF`

- MAC 对象: `侧翼`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_ACA912A984 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1770:意图1` — 关闭主动侧翼

## 618. `KNOWN_CONTROL_CANDIDATE_C607248350_SET`

- MAC 对象: `侧翼`
- MAC 对象功能: `主动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C607248350 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19553:意图1` — 副驾主动侧翼强度调高点

## 619. `KNOWN_CONTROL_CANDIDATE_C607248350_REVIEW`

- MAC 对象: `侧翼`
- MAC 对象功能: `主动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_C607248350 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5831:意图1` — 主动侧翼强度设为3挡

## 620. `KNOWN_CONTROL_CANDIDATE_EF3380DD2A_SET`

- MAC 对象: `侧翼`
- MAC 对象功能: `转向支撑`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节', '调节为']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_EF3380DD2A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19777:意图1` — 侧翼转向支撑调节为标准
- `train_set.jsonl:8115:意图1` — 前面侧翼转向支撑标准

## 621. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `倒后镜`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:439:意图1` — 打开倒后镜加热

## 622. `KNOWN_CONTROL_CANDIDATE_0B345836D1_TURN_OFF`

- MAC 对象: `储物箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_0B345836D1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3813:意图1` — 关闭储物箱

## 623. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_SET`

- MAC 对象: `儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13210:意图1` — 儿童座椅设置为恒温通风

## 624. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_OFF`

- MAC 对象: `儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1932:意图1` — 关闭儿童座椅通风

## 625. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_OFF`

- MAC 对象: `儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:181:意图1` — 关闭儿童座椅自然风

## 626. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4849:意图1` — 儿童座椅开启通风

## 627. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13260:意图1` — 启动儿童座椅自然通风

## 628. `KNOWN_CONTROL_CANDIDATE_238BD00813_TURN_ON`

- MAC 对象: `充电口`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_238BD00813 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15453:意图2` — 打开充电口
- `train_set.jsonl:7591:意图1` — 打开充电口
- `train_set.jsonl:8485:意图1` — 打开充电口

## 629. `KNOWN_CONTROL_CANDIDATE_41DAF915DC_SET`

- MAC 对象: `充电口盖`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['修改']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_41DAF915DC + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8704:意图1` — 我要修改充电口盖的自定义功能

## 630. `KNOWN_CONTROL_CANDIDATE_41DAF915DC_TURN_OFF`

- MAC 对象: `充电口盖`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_41DAF915DC + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16465:意图1` — 关闭充电口盖

## 631. `KNOWN_CONTROL_CANDIDATE_41DAF915DC_TURN_ON`

- MAC 对象: `充电口盖`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_41DAF915DC + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11191:意图1` — 打开前充电口盖
- `train_set.jsonl:9727:意图1` — 打开后面的充电口盖
- `train_set.jsonl:9834:意图1` — 打开充电口盖

## 632. `KNOWN_CONTROL_CANDIDATE_6FD6EBD62E_TURN_ON`

- MAC 对象: `充电枪锁`
- MAC 对象功能: `慢充`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_6FD6EBD62E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14373:意图1` — 关闭解锁慢充枪
- `train_set.jsonl:2460:意图1` — 关闭解锁慢充枪开关

## 633. `KNOWN_CONTROL_CANDIDATE_6EDAEC4546_TURN_ON`

- MAC 对象: `充电盖`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_6EDAEC4546 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6791:意图1` — 打开后充电盖

## 634. `KNOWN_CONTROL_CANDIDATE_6EDAEC4546_REVIEW`

- MAC 对象: `充电盖`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['合上', '盖上']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_6EDAEC4546 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2498:意图1` — 把车前充电盖盖上
- `train_set.jsonl:3811:意图1` — 把车后充电盖合上

## 635. `KNOWN_CONTROL_CANDIDATE_E512FBAD72_TURN_ON`

- MAC 对象: `充电盖口`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E512FBAD72 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11695:意图1` — 打开后充电盖口

## 636. `KNOWN_CONTROL_CANDIDATE_03FF716E0B_REVIEW`

- MAC 对象: `全景记录仪`
- MAC 对象功能: `录像锁定`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['锁定']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_03FF716E0B + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17243:意图1` — 锁定全景记录仪

## 637. `KNOWN_CONTROL_CANDIDATE_F4985198AA_TURN_OFF`

- MAC 对象: `全气候灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F4985198AA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:542:意图2` — 关闭全气候灯

## 638. `KNOWN_CONTROL_CANDIDATE_F4985198AA_TURN_ON`

- MAC 对象: `全气候灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '开启', '开开', '打开']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_F4985198AA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:663:意图1` — 让全气候灯处于开启状态
- `train_set.jsonl:13824:意图1` — 开开全气候灯
- `train_set.jsonl:17261:意图2` — 打开全气候灯
- `train_set.jsonl:4044:意图1` — 全气候灯帮我把它给调开
- `train_set.jsonl:6488:意图1` — 打开全气候灯

## 639. `KNOWN_CONTROL_CANDIDATE_BC7A07DBD3_TURN_ON`

- MAC 对象: `全气候灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BC7A07DBD3 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8738:意图1` — 打开全气候灯光

## 640. `KNOWN_CONTROL_CANDIDATE_F8724374D9_TURN_ON`

- MAC 对象: `全车照明`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_F8724374D9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9921:意图1` — 打开全车照明

## 641. `KNOWN_CONTROL_CANDIDATE_3FD47EDCE4_TURN_OFF`

- MAC 对象: `关闭`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **13**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3FD47EDCE4 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19308:意图2` — 关闭室内灯光
- `train_set.jsonl:12291:意图2` — 关闭全车阅读灯
- `train_set.jsonl:13219:意图1` — 关闭全车氛围灯
- `train_set.jsonl:14229:意图2` — 关闭车内所有灯光
- `train_set.jsonl:14980:意图2` — 关闭车内所有灯光

## 642. `KNOWN_CONTROL_CANDIDATE_F8781A5F97_SET`

- MAC 对象: `冰箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_F8781A5F97 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3867:意图1` — 冰箱保温时间设置到3小时

## 643. `KNOWN_CONTROL_CANDIDATE_F8781A5F97_SET`

- MAC 对象: `冰箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换成', '调成']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_F8781A5F97 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13878:意图1` — 冰箱调成极冻
- `train_set.jsonl:5889:意图1` — 冰箱切换成红酒模式

## 644. `KNOWN_CONTROL_CANDIDATE_F8781A5F97_TURN_OFF`

- MAC 对象: `冰箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F8781A5F97 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20089:意图1` — 关闭冰箱保温模式

## 645. `KNOWN_CONTROL_CANDIDATE_F8781A5F97_TURN_ON`

- MAC 对象: `冰箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_F8781A5F97 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9082:意图2` — 打开冰箱制冷

## 646. `KNOWN_CONTROL_CANDIDATE_F8781A5F97_REVIEW`

- MAC 对象: `冰箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `[]`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_F8781A5F97 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6283:意图1` — 我要在冰箱热下吃的

## 647. `KNOWN_CONTROL_CANDIDATE_CB98FBE7F0_SET`

- MAC 对象: `冰箱`
- MAC 对象功能: `延时掉电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_CB98FBE7F0 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2974:意图1` — 冰箱延时掉电时间设为3小时

## 648. `KNOWN_CONTROL_CANDIDATE_91F6CACEB4_SET`

- MAC 对象: `冰箱`
- MAC 对象功能: `持续工作`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_91F6CACEB4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5180:意图1` — 冰箱持续工作时间设为30秒

## 649. `KNOWN_CONTROL_CANDIDATE_8B0CAACF83_TURN_ON`

- MAC 对象: `冰箱电源`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_8B0CAACF83 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:608:意图1` — 打开冰箱电源
- `train_set.jsonl:1546:意图1` — 打开冰箱电源

## 650. `KNOWN_CONTROL_CANDIDATE_785DD45439_TURN_ON`

- MAC 对象: `冰箱门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_785DD45439 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15599:意图1` — 打开所有冰箱门

## 651. `KNOWN_CONTROL_CANDIDATE_5D33E523E6_REVIEW`

- MAC 对象: `净化空气`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['停止']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5D33E523E6 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7034:意图1` — 停止净化空气

## 652. `KNOWN_CONTROL_CANDIDATE_6BE2077FB9_SET`

- MAC 对象: `减震`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_6BE2077FB9 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8289:意图1` — 减震高度调到最低

## 653. `KNOWN_CONTROL_CANDIDATE_5F8E368758_SET`

- MAC 对象: `制冷器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5F8E368758 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1373:意图1` — 调节制冷器

## 654. `KNOWN_CONTROL_CANDIDATE_5F8E368758_SET`

- MAC 对象: `制冷器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5F8E368758 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8191:意图1` — 副驾制冷器温度高一点

## 655. `KNOWN_CONTROL_CANDIDATE_5F8E368758_SET`

- MAC 对象: `制冷器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5F8E368758 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20091:意图1` — 制冷器别吹脸
- `test_set.jsonl:675:意图1` — 制冷器吹玻璃

## 656. `KNOWN_CONTROL_CANDIDATE_5F8E368758_TURN_ON`

- MAC 对象: `制冷器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5F8E368758 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14336:意图1` — 打开制冷器

## 657. `KNOWN_CONTROL_CANDIDATE_8A2B81EC38_TURN_OFF`

- MAC 对象: `制动踏板`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_8A2B81EC38 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7780:意图1` — 关闭制动踏板设置

## 658. `KNOWN_CONTROL_CANDIDATE_8A2B81EC38_REVIEW`

- MAC 对象: `制动踏板`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['选择']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_8A2B81EC38 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16107:意图1` — 让制动踏板模式选择为柔和

## 659. `KNOWN_CONTROL_CANDIDATE_56BB7C3DA3_SET`

- MAC 对象: `制动踏板感`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['BRAKE', 'EMERGENCY_BRAKE']`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_56BB7C3DA3 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17191:意图1` — 制动踏板感调到标准模式

## 660. `KNOWN_CONTROL_CANDIDATE_DE69F9C2DE_SET`

- MAC 对象: `制热器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_DE69F9C2DE + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19405:意图1` — 制热器中等风量
- `train_set.jsonl:9186:意图1` — 制热器风量调小一点

## 661. `KNOWN_CONTROL_CANDIDATE_DE69F9C2DE_TURN_ON`

- MAC 对象: `制热器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DE69F9C2DE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4628:意图1` — 打开制热器调节页面

## 662. `KNOWN_CONTROL_CANDIDATE_75448ED8A7_TURN_ON`

- MAC 对象: `刹车`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_75448ED8A7 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20003:意图1` — 打开刹车设置

## 663. `KNOWN_CONTROL_CANDIDATE_012C32FEB0_TURN_OFF`

- MAC 对象: `前灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_012C32FEB0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3447:意图2` — 关闭前灯

## 664. `KNOWN_CONTROL_CANDIDATE_03FF716E0B_REVIEW`

- MAC 对象: `前视记录仪`
- MAC 对象功能: `录像锁定`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['锁定']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_03FF716E0B + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18870:意图1` — 锁定前视记录仪

## 665. `KNOWN_CONTROL_CANDIDATE_08DD3FFA57_SET`

- MAC 对象: `副屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_08DD3FFA57 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4089:意图4` — 一副屏亮度调到最低

## 666. `KNOWN_CONTROL_CANDIDATE_08DD3FFA57_TURN_OFF`

- MAC 对象: `副屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_08DD3FFA57 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14617:意图2` — 关闭副屏
- `train_set.jsonl:3493:意图2` — 关闭副屏
- `train_set.jsonl:9279:意图1` — 关闭副屏

## 667. `KNOWN_CONTROL_CANDIDATE_97BB374C86_TURN_OFF`

- MAC 对象: `副屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_97BB374C86 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18079:意图3` — 关闭副屏幕

## 668. `KNOWN_CONTROL_CANDIDATE_0298BADA52_TURN_OFF`

- MAC 对象: `副驾屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_0298BADA52 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18843:意图2` — 关闭副驾屏幕
- `train_set.jsonl:3412:意图1` — 关闭副驾屏幕
- `train_set.jsonl:3578:意图2` — 关闭副驾屏幕
- `train_set.jsonl:6598:意图2` — 关闭副驾屏幕
- `train_set.jsonl:8055:意图1` — 关闭副驾屏幕

## 669. `KNOWN_CONTROL_CANDIDATE_839AEFF17A_TURN_ON`

- MAC 对象: `功放`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_839AEFF17A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17933:意图1` — 打开车外功放

## 670. `KNOWN_CONTROL_CANDIDATE_F3D712F78C_SET`

- MAC 对象: `加速能力`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_F3D712F78C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2531:意图1` — 加速能力切换到运动

## 671. `KNOWN_CONTROL_CANDIDATE_0DD0F0252C_TURN_ON`

- MAC 对象: `危险报警灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_0DD0F0252C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19654:意图1` — 危险报警灯打开

## 672. `KNOWN_CONTROL_CANDIDATE_6C081AAAA1_TURN_OFF`

- MAC 对象: `双跳灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_6C081AAAA1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11387:意图1` — 关闭双跳灯

## 673. `KNOWN_CONTROL_CANDIDATE_F10FDB4FB3_TURN_OFF`

- MAC 对象: `反光镜`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F10FDB4FB3 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17386:意图1` — 关闭反光镜

## 674. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `反光镜`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:665:意图2` — 打开反光镜加热
- `train_set.jsonl:17158:意图1` — 打开反光镜加热

## 675. `KNOWN_CONTROL_CANDIDATE_C38E97C632_TURN_ON`

- MAC 对象: `口盖`
- MAC 对象功能: `慢速充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_C38E97C632 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:122:意图1` — 打开慢速充电口盖

## 676. `KNOWN_CONTROL_CANDIDATE_9E3DBCEF26_TURN_ON`

- MAC 对象: `后尾箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_9E3DBCEF26 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8157:意图1` — 打开后尾箱

## 677. `KNOWN_CONTROL_CANDIDATE_7B027A689C_SET`

- MAC 对象: `后背`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7B027A689C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3341:意图1` — 主驾座椅后背调节界面帮我打开
- `train_set.jsonl:7354:意图1` — 我要调副驾后背

## 678. `KNOWN_CONTROL_CANDIDATE_7B027A689C_TURN_ON`

- MAC 对象: `后背`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '开启', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7B027A689C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18709:意图1` — 打开副驾座椅后背设置界面
- `train_set.jsonl:18893:意图1` — 主驾座椅后背帮我把它的设置界面开启一下
- `train_set.jsonl:4068:意图1` — 副驾座椅后背设置界面帮我开一下啊

## 679. `KNOWN_CONTROL_CANDIDATE_7B027A689C_REVIEW`

- MAC 对象: `后背`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['进入']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7B027A689C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10524:意图1` — 进入后排座椅后背设置界面

## 680. `KNOWN_CONTROL_CANDIDATE_E803F3252E_SET`

- MAC 对象: `后背门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E803F3252E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17436:意图1` — 后背门开启高度最高

## 681. `KNOWN_CONTROL_CANDIDATE_E803F3252E_REVIEW`

- MAC 对象: `后背门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_E803F3252E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19812:意图1` — 后背门开启高度设为默认

## 682. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_OFF`

- MAC 对象: `后视镜`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19305:意图2` — 关闭后视镜加热
- `train_set.jsonl:1465:意图3` — 关闭后视镜加热
- `train_set.jsonl:2738:意图2` — 关闭后视镜加热
- `train_set.jsonl:5701:意图1` — 关闭后视镜加热

## 683. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `后视镜`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **32**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19558:意图1` — 后视镜加热开启
- `dev_set.jsonl:19745:意图1` — 打开后视镜加热
- `test_set.jsonl:324:意图2` — 打开后视镜加热
- `test_set.jsonl:959:意图2` — 打开后视镜加热
- `train_set.jsonl:10534:意图2` — 后视镜加热

## 684. `KNOWN_CONTROL_CANDIDATE_65DA4B1810_TURN_OFF`

- MAC 对象: `吸顶屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_65DA4B1810 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14311:意图1` — 吸顶屏息屏

## 685. `KNOWN_CONTROL_CANDIDATE_65DA4B1810_TURN_ON`

- MAC 对象: `吸顶屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_65DA4B1810 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14833:意图3` — 打开吸顶屏
- `train_set.jsonl:15608:意图2` — 打开吸顶屏
- `train_set.jsonl:16566:意图2` — 打开后排吸顶屏
- `train_set.jsonl:2492:意图2` — 打开后排吸顶屏
- `train_set.jsonl:4971:意图2` — 打开吸顶屏

## 686. `KNOWN_CONTROL_CANDIDATE_EC2FD79C56_TURN_ON`

- MAC 对象: `吸顶屏`
- MAC 对象功能: `观影角度`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_EC2FD79C56 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19806:意图1` — 打开吸顶屏观影角度

## 687. `KNOWN_CONTROL_CANDIDATE_BC05E39C15_SET`

- MAC 对象: `坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BC05E39C15 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10349:意图1` — 坐垫倾斜角度调到最低
- `train_set.jsonl:18224:意图1` — 坐垫倾斜角度调到最高

## 688. `KNOWN_CONTROL_CANDIDATE_BC05E39C15_SET`

- MAC 对象: `坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BC05E39C15 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18256:意图1` — 坐垫向上

## 689. `KNOWN_CONTROL_CANDIDATE_BC05E39C15_SET`

- MAC 对象: `坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BC05E39C15 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:169:意图1` — 坐垫角度太高了

## 690. `KNOWN_CONTROL_CANDIDATE_BC05E39C15_SET`

- MAC 对象: `坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **7**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BC05E39C15 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13409:意图1` — 坐垫整体往低下些
- `train_set.jsonl:1933:意图1` — 坐垫整体往高上
- `train_set.jsonl:2830:意图1` — 坐垫整体往低走
- `train_set.jsonl:4921:意图1` — 前面坐垫高度向最低调节
- `train_set.jsonl:5492:意图1` — 坐垫整体往低点

## 691. `KNOWN_CONTROL_CANDIDATE_BC05E39C15_TURN_OFF`

- MAC 对象: `坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BC05E39C15 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3587:意图1` — 把后排坐垫软硬度关闭

## 692. `KNOWN_CONTROL_CANDIDATE_BC05E39C15_TURN_ON`

- MAC 对象: `坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '开启']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BC05E39C15 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12249:意图1` — 副驾座椅坐垫帮我把它的设置界面开启一下
- `train_set.jsonl:4567:意图1` — 副驾座椅坐垫配置的界面帮我把它调开

## 693. `KNOWN_CONTROL_CANDIDATE_BC05E39C15_TURN_ON`

- MAC 对象: `坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BC05E39C15 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14469:意图1` — 开启左前侧小腿主动锻炼坐垫

## 694. `KNOWN_CONTROL_CANDIDATE_BC05E39C15_REVIEW`

- MAC 对象: `坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['激活']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_BC05E39C15 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1018:意图1` — 座椅帮我把它坐垫设置界面给激活一下

## 695. `KNOWN_CONTROL_CANDIDATE_1E9426C2DF_TURN_ON`

- MAC 对象: `坐垫`
- MAC 对象功能: `升温`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_1E9426C2DF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6129:意图1` — 打开坐垫升温

## 696. `KNOWN_CONTROL_CANDIDATE_2895115ABD_SET`

- MAC 对象: `坐垫`
- MAC 对象功能: `延长`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_2895115ABD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12056:意图1` — 坐垫延长调到最后
- `train_set.jsonl:8574:意图1` — 将坐垫调到最前一下

## 697. `KNOWN_CONTROL_CANDIDATE_2895115ABD_TURN_ON`

- MAC 对象: `坐垫`
- MAC 对象功能: `延长`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2895115ABD + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1225:意图1` — 打开坐垫延长设置

## 698. `KNOWN_CONTROL_CANDIDATE_48F3F5DCE5_TURN_ON`

- MAC 对象: `坐垫`
- MAC 对象功能: `翻折`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_48F3F5DCE5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5521:意图2` — 后排坐垫翻折

## 699. `KNOWN_CONTROL_CANDIDATE_1034EDC5D4_SET`

- MAC 对象: `坐垫侧翼`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_1034EDC5D4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6995:意图1` — 坐垫侧翼松一点

## 700. `KNOWN_CONTROL_CANDIDATE_33DF46AEF9_SET`

- MAC 对象: `坐垫再`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_33DF46AEF9 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18544:意图1` — 主驾坐垫再向上一点

## 701. `KNOWN_CONTROL_CANDIDATE_C304911C85_TURN_OFF`

- MAC 对象: `备胎`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_C304911C85 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15827:意图1` — 关闭备胎
- `train_set.jsonl:3358:意图1` — 备胎设置完了给我关掉吧

## 702. `KNOWN_CONTROL_CANDIDATE_DCEC73EDFE_TURN_OFF`

- MAC 对象: `备胎装置`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关', '关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_DCEC73EDFE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19533:意图1` — 关闭备胎装置
- `train_set.jsonl:9573:意图1` — 把备胎装置关一关

## 703. `KNOWN_CONTROL_CANDIDATE_DCEC73EDFE_TURN_ON`

- MAC 对象: `备胎装置`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DCEC73EDFE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17955:意图1` — 打开备胎装置

## 704. `KNOWN_CONTROL_CANDIDATE_DCEC73EDFE_REVIEW`

- MAC 对象: `备胎装置`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['使用']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_DCEC73EDFE + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18426:意图1` — 停止使用备胎装置

## 705. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_OFF`

- MAC 对象: `外后视镜`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11350:意图1` — 关闭外后视镜加热

## 706. `KNOWN_CONTROL_CANDIDATE_A05DB4EBB0_REVIEW`

- MAC 对象: `大屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑一下', '滑动点', '移动一下']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A05DB4EBB0 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11266:意图1` — 副驾大屏移动一下
- `train_set.jsonl:1165:意图1` — 滑动点副驾大屏
- `train_set.jsonl:17276:意图1` — 副驾大屏滑一下

## 707. `KNOWN_CONTROL_CANDIDATE_E618FCF799_TURN_OFF`

- MAC 对象: `大屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_E618FCF799 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19979:意图2` — 关闭大屏幕
- `train_set.jsonl:3373:意图1` — 关掉大屏幕

## 708. `KNOWN_CONTROL_CANDIDATE_39F17E1621_SET`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_39F17E1621 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6610:意图1` — 天幕调到中间挡位

## 709. `KNOWN_CONTROL_CANDIDATE_39F17E1621_SET`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_39F17E1621 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5517:意图1` — 天幕调到百分之二十

## 710. `KNOWN_CONTROL_CANDIDATE_39F17E1621_SET`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_39F17E1621 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6251:意图1` — 天幕模式切换为流水

## 711. `KNOWN_CONTROL_CANDIDATE_39F17E1621_SET`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_39F17E1621 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9085:意图1` — 天幕透光值最暗

## 712. `KNOWN_CONTROL_CANDIDATE_39F17E1621_SET`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调整成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_39F17E1621 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6190:意图1` — 天幕透光率调整成百分之十

## 713. `KNOWN_CONTROL_CANDIDATE_39F17E1621_SET`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到', '调节']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_39F17E1621 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20072:意图1` — 天幕透明值最低
- `train_set.jsonl:11375:意图1` — 天幕透明值调到20%
- `train_set.jsonl:13728:意图1` — 天幕透明值最暗
- `train_set.jsonl:14648:意图1` — 把天幕透明值调到最高
- `train_set.jsonl:17821:意图1` — 把天幕透明值调到最亮

## 714. `KNOWN_CONTROL_CANDIDATE_39F17E1621_SET`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_39F17E1621 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6675:意图1` — 天幕透明挡位小一点

## 715. `KNOWN_CONTROL_CANDIDATE_39F17E1621_TURN_OFF`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_39F17E1621 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:901:意图2` — 关闭天幕
- `train_set.jsonl:14028:意图1` — 天幕关闭
- `train_set.jsonl:4805:意图2` — 关闭天幕
- `train_set.jsonl:8458:意图1` — 关闭天幕
- `train_set.jsonl:9399:意图1` — 天幕关掉

## 716. `KNOWN_CONTROL_CANDIDATE_39F17E1621_TURN_ON`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_39F17E1621 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20215:意图2` — 打开天幕
- `train_set.jsonl:12120:意图1` — 打开天幕
- `train_set.jsonl:18843:意图1` — 打开天幕
- `train_set.jsonl:4007:意图2` — 打开天幕
- `train_set.jsonl:4814:意图2` — 打开天幕

## 717. `KNOWN_CONTROL_CANDIDATE_39F17E1621_TURN_ON`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_39F17E1621 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10892:意图1` — 天幕打开二分之一

## 718. `KNOWN_CONTROL_CANDIDATE_39F17E1621_REVIEW`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `[]`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_39F17E1621 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12245:意图1` — 天幕透光值自动

## 719. `KNOWN_CONTROL_CANDIDATE_39F17E1621_REVIEW`

- MAC 对象: `天幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `[]`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_39F17E1621 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:148:意图1` — 天幕透明值自动

## 720. `KNOWN_CONTROL_CANDIDATE_FD854BC65A_SET`

- MAC 对象: `天幕玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为', '调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_FD854BC65A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14330:意图1` — 天幕玻璃透明度最小
- `train_set.jsonl:4840:意图1` — 天幕玻璃透明度设置为5

## 721. `KNOWN_CONTROL_CANDIDATE_23EC4040D6_SET`

- MAC 对象: `天幕调光玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '调节']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_23EC4040D6 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14110:意图1` — 天幕调光玻璃透明度升高
- `train_set.jsonl:17101:意图1` — 调节天幕调光玻璃透明度到最大
- `train_set.jsonl:17258:意图1` — 天幕调光玻璃透明度设置最大

## 722. `KNOWN_CONTROL_CANDIDATE_23EC4040D6_REVIEW`

- MAC 对象: `天幕调光玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['更改']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_23EC4040D6 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9160:意图1` — 更改天幕调光玻璃透明度到最低

## 723. `KNOWN_CONTROL_CANDIDATE_52150E6B98_TURN_ON`

- MAC 对象: `天幕遮阳帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_52150E6B98 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16249:意图2` — 打开天幕遮阳帘

## 724. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `天窗`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1111:意图2` — 打开天窗通风
- `train_set.jsonl:18436:意图2` — 打开天窗通风

## 725. `KNOWN_CONTROL_CANDIDATE_CFDB0CE7F4_TURN_OFF`

- MAC 对象: `太阳窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_CFDB0CE7F4 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19920:意图1` — 关闭太阳窗

## 726. `KNOWN_CONTROL_CANDIDATE_CFDB0CE7F4_REVIEW`

- MAC 对象: `太阳窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关小']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_CFDB0CE7F4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12171:意图1` — 太阳窗关小点

## 727. `KNOWN_CONTROL_CANDIDATE_EAF173AAB1_SET`

- MAC 对象: `头枕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_EAF173AAB1 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18120:意图1` — 头枕直接到顶

## 728. `KNOWN_CONTROL_CANDIDATE_EAF173AAB1_TURN_ON`

- MAC 对象: `头枕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_EAF173AAB1 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7330:意图1` — 主驾驶头枕音量静音

## 729. `KNOWN_CONTROL_CANDIDATE_4769FEA2DB_SET`

- MAC 对象: `头枕屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4769FEA2DB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10816:意图1` — 头枕屏亮度调高一点
- `train_set.jsonl:7971:意图1` — 头枕屏亮度调低30%
- `train_set.jsonl:9145:意图1` — 头枕屏亮度调低一点
- `train_set.jsonl:9570:意图1` — 副驾头枕屏亮度调低一点

## 730. `KNOWN_CONTROL_CANDIDATE_E9F230768A_SET`

- MAC 对象: `头枕音响`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E9F230768A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12871:意图1` — 切换头枕音响为共享
- `train_set.jsonl:3877:意图1` — 切换头枕音响为私享模式

## 731. `KNOWN_CONTROL_CANDIDATE_E9F230768A_REVIEW`

- MAC 对象: `头枕音响`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['换成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_E9F230768A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9960:意图1` — 通知和安全提醒换成头枕音响

## 732. `KNOWN_CONTROL_CANDIDATE_4732A81E0A_SET`

- MAC 对象: `头枕音响播放`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4732A81E0A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4487:意图1` — 切换为头枕音响播放

## 733. `KNOWN_CONTROL_CANDIDATE_88E90D27F3_SET`

- MAC 对象: `头顶`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_88E90D27F3 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11927:意图1` — 头顶亮度调高

## 734. `KNOWN_CONTROL_CANDIDATE_B718E15F5D_SET`

- MAC 对象: `头顶灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_B718E15F5D + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4983:意图1` — 调节头顶灯光亮度

## 735. `KNOWN_CONTROL_CANDIDATE_E38516A29C_ADJUST`

- MAC 对象: `娱乐主机大屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_E38516A29C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12270:意图1` — 娱乐主机大屏移至驾驶员

## 736. `KNOWN_CONTROL_CANDIDATE_67DAA40DFC_ADJUST`

- MAC 对象: `娱乐主机屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_67DAA40DFC + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:571:意图1` — 帮忙把娱乐主机屏幕滑回左

## 737. `KNOWN_CONTROL_CANDIDATE_67DAA40DFC_REVIEW`

- MAC 对象: `娱乐主机屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['使用']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_67DAA40DFC + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16120:意图1` — 我想使用娱乐主机屏幕

## 738. `KNOWN_CONTROL_CANDIDATE_D294518EAA_SET`

- MAC 对象: `娱乐主机显示屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_D294518EAA + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5468:意图1` — 娱乐主机显示屏向主驾

## 739. `KNOWN_CONTROL_CANDIDATE_D294518EAA_ADJUST`

- MAC 对象: `娱乐主机显示屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_D294518EAA + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4554:意图1` — 娱乐主机显示屏移至右边

## 740. `KNOWN_CONTROL_CANDIDATE_D294518EAA_REVIEW`

- MAC 对象: `娱乐主机显示屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移动下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_D294518EAA + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1002:意图1` — 帮我移动下娱乐主机显示屏

## 741. `KNOWN_CONTROL_CANDIDATE_697E84A38B_ADJUST`

- MAC 对象: `娱乐大屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_697E84A38B + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2834:意图1` — 娱乐大屏移动向左

## 742. `KNOWN_CONTROL_CANDIDATE_697E84A38B_REVIEW`

- MAC 对象: `娱乐大屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['使用']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_697E84A38B + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18718:意图1` — 我需要使用娱乐大屏

## 743. `KNOWN_CONTROL_CANDIDATE_DDB30209DB_ADJUST`

- MAC 对象: `娱乐显示屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_DDB30209DB + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19486:意图1` — 娱乐显示屏滑动

## 744. `KNOWN_CONTROL_CANDIDATE_18D8AB054B_TURN_OFF`

- MAC 对象: `安全带`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_18D8AB054B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:172:意图1` — 关闭后排安全带提醒
- `train_set.jsonl:2186:意图1` — 安全带关闭
- `train_set.jsonl:2928:意图1` — 关闭后排未系安全带提醒音效

## 745. `KNOWN_CONTROL_CANDIDATE_2E962FADD6_TURN_ON`

- MAC 对象: `安全带`
- MAC 对象功能: `安全带报警音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2E962FADD6 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13241:意图1` — 后排安全带报警音打开

## 746. `KNOWN_CONTROL_CANDIDATE_98DCACC77E_TURN_OFF`

- MAC 对象: `安全带`
- MAC 对象功能: `安全带提示`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_98DCACC77E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:504:意图2` — 关闭安全带提示

## 747. `KNOWN_CONTROL_CANDIDATE_DC311CE5E0_REVIEW`

- MAC 对象: `安全带`
- MAC 对象功能: `安全带未系报警`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['给我关了']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_DC311CE5E0 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10426:意图1` — 后排安全带未系报警开关给我关了

## 748. `KNOWN_CONTROL_CANDIDATE_7C88A7E37A_TURN_ON`

- MAC 对象: `安全带`
- MAC 对象功能: `安全带没系提醒音`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7C88A7E37A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16647:意图1` — 打开后排安全带没系提醒音开关

## 749. `KNOWN_CONTROL_CANDIDATE_EE38D06A55_TURN_ON`

- MAC 对象: `室内顶灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_EE38D06A55 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:975:意图1` — 打开室内顶灯

## 750. `KNOWN_CONTROL_CANDIDATE_E9A88DA4B6_SET`

- MAC 对象: `寻车灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E9A88DA4B6 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17903:意图1` — 寻车灯光时长设置为30秒

## 751. `KNOWN_CONTROL_CANDIDATE_A7EDA581C7_SET`

- MAC 对象: `将灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A7EDA581C7 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13362:意图1` — 将灯光调至最暗的氛围

## 752. `KNOWN_CONTROL_CANDIDATE_667D3800D8_TURN_ON`

- MAC 对象: `小灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_667D3800D8 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6909:意图2` — 打开小灯

## 753. `KNOWN_CONTROL_CANDIDATE_DC15E7D125_TURN_ON`

- MAC 对象: `尾翼`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DC15E7D125 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:350:意图1` — 打开尾翼
- `train_set.jsonl:4960:意图1` — 打开尾翼
- `train_set.jsonl:9474:意图2` — 打开尾翼

## 754. `KNOWN_CONTROL_CANDIDATE_044786200C_TURN_OFF`

- MAC 对象: `尾翼`
- MAC 对象功能: `迎宾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_044786200C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13101:意图1` — 关闭尾翼迎宾

## 755. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_SET`

- MAC 对象: `屁股座垫`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:536:意图1` — 设置屁股座垫通风

## 756. `KNOWN_CONTROL_CANDIDATE_A8DD39A0A6_SET`

- MAC 对象: `屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A8DD39A0A6 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3053:意图2` — 设置屏页面

## 757. `KNOWN_CONTROL_CANDIDATE_A8DD39A0A6_SET`

- MAC 对象: `屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A8DD39A0A6 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8998:意图1` — 右后屏音量最大

## 758. `KNOWN_CONTROL_CANDIDATE_A8DD39A0A6_REVIEW`

- MAC 对象: `屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启用', '操作']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A8DD39A0A6 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:741:意图1` — 我想操作副驾屏
- `train_set.jsonl:2125:意图1` — 升级驾驶乐趣立即启用主控驾屏

## 759. `KNOWN_CONTROL_CANDIDATE_A8DD39A0A6_REVIEW`

- MAC 对象: `屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['换成', '改为']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A8DD39A0A6 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12387:意图1` — 主驾屏换成经典模式
- `train_set.jsonl:5321:意图2` — 仪表和多媒体显示屏改为白天模式

## 760. `KNOWN_CONTROL_CANDIDATE_55EBA4E7AC_REVIEW`

- MAC 对象: `屏`
- MAC 对象功能: ``
- MAC 功能: `查询当前音量`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_55EBA4E7AC + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15896:意图1` — 主驾屏查询当前音量

## 761. `KNOWN_CONTROL_CANDIDATE_48272DE6AC_SET`

- MAC 对象: `屏`
- MAC 对象功能: `保`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_48272DE6AC + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10015:意图1` — 我想设置屏保

## 762. `KNOWN_CONTROL_CANDIDATE_48272DE6AC_SET`

- MAC 对象: `屏`
- MAC 对象功能: `保`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_48272DE6AC + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3513:意图1` — 屏保等待时长设置为永不

## 763. `KNOWN_CONTROL_CANDIDATE_2D1B8D10EF_SET`

- MAC 对象: `屏`
- MAC 对象功能: `息屏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_2D1B8D10EF + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16782:意图1` — 调节后左屏自动息屏时间为永不

## 764. `KNOWN_CONTROL_CANDIDATE_04D4ABA0AB_SET`

- MAC 对象: `屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_04D4ABA0AB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6124:意图1` — 屏幕上面的光亮强度稍微给加强一下

## 765. `KNOWN_CONTROL_CANDIDATE_04D4ABA0AB_SET`

- MAC 对象: `屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_04D4ABA0AB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15921:意图1` — 设置屏幕明暗

## 766. `KNOWN_CONTROL_CANDIDATE_04D4ABA0AB_SET`

- MAC 对象: `屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '调到', '调成', '调整为', '调节']`
- 唯一样本数: **14**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_04D4ABA0AB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19819:意图1` — 屏幕调成夜间模式
- `dev_set.jsonl:19819:意图2` — 把屏幕调成白天模式
- `train_set.jsonl:11080:意图1` — 屏幕现在调到自动显示
- `train_set.jsonl:11513:意图1` — 屏幕主题模式设置
- `train_set.jsonl:13317:意图1` — 屏幕调成深色模式

## 767. `KNOWN_CONTROL_CANDIDATE_04D4ABA0AB_TURN_OFF`

- MAC 对象: `屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_04D4ABA0AB + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11916:意图1` — 关一下屏幕清洁

## 768. `KNOWN_CONTROL_CANDIDATE_04D4ABA0AB_TURN_ON`

- MAC 对象: `屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_04D4ABA0AB + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12847:意图1` — 打开屏幕清洁
- `train_set.jsonl:16837:意图1` — 打开屏幕清洁模式
- `train_set.jsonl:18599:意图1` — 关闭屏幕声音
- `train_set.jsonl:3928:意图1` — 打开屏幕的自动显示功能
- `train_set.jsonl:5025:意图1` — 关上所有设备的声音

## 769. `KNOWN_CONTROL_CANDIDATE_04D4ABA0AB_REVIEW`

- MAC 对象: `屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['回到初始位置', '回正', '恢复到初始位置', '显示', '点灭', '熄灭', '返回', '返回到']`
- 唯一样本数: **13**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_04D4ABA0AB + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:965:意图1` — 第二排屏幕返回至主页
- `train_set.jsonl:12008:意图1` — 屏幕回到初始位置
- `train_set.jsonl:12368:意图2` — 熄灭屏幕
- `train_set.jsonl:12766:意图1` — 后排屏幕返回到主页
- `train_set.jsonl:15834:意图2` — 熄灭屏幕

## 770. `KNOWN_CONTROL_CANDIDATE_04D4ABA0AB_REVIEW`

- MAC 对象: `屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['换个']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_04D4ABA0AB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2425:意图1` — 屏幕换个显示模式

## 771. `KNOWN_CONTROL_CANDIDATE_04D4ABA0AB_REVIEW`

- MAC 对象: `屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_04D4ABA0AB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12148:意图1` — 屏幕深色模式
- `train_set.jsonl:12266:意图1` — 设置主驾屏幕为浅色模式
- `train_set.jsonl:15367:意图1` — 屏幕主题深色模式
- `train_set.jsonl:1819:意图1` — 屏幕设置一下把它设成自动显示

## 772. `KNOWN_CONTROL_CANDIDATE_0AED132DB0_SET`

- MAC 对象: `屏幕`
- MAC 对象功能: `触屏音效`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_0AED132DB0 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16138:意图1` — 我要设置触屏音效

## 773. `KNOWN_CONTROL_CANDIDATE_A32F42CFC1_SET`

- MAC 对象: `屏幕显示`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调整']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A32F42CFC1 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10982:意图1` — 调整屏幕显示为深色模式

## 774. `KNOWN_CONTROL_CANDIDATE_D55AC43B9A_SET`

- MAC 对象: `底盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_D55AC43B9A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19841:意图1` — 底盘切换到动态模式

## 775. `KNOWN_CONTROL_CANDIDATE_D55AC43B9A_SET`

- MAC 对象: `底盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_D55AC43B9A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1024:意图1` — 底盘高度调节

## 776. `KNOWN_CONTROL_CANDIDATE_DB2CD7E2C0_SET`

- MAC 对象: `底盘悬架`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_DB2CD7E2C0 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13204:意图1` — 底盘悬架调低点

## 777. `KNOWN_CONTROL_CANDIDATE_001D9C64F7_TURN_ON`

- MAC 对象: `座`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_001D9C64F7 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1848:意图2` — 座椅通风

## 778. `KNOWN_CONTROL_CANDIDATE_7BD9D53B62_SET`

- MAC 对象: `座位`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7BD9D53B62 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16349:意图1` — 副驾座位有点前了

## 779. `KNOWN_CONTROL_CANDIDATE_7BD9D53B62_SET`

- MAC 对象: `座位`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7BD9D53B62 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3150:意图1` — 副驾驶座位空调不直接吹脚

## 780. `KNOWN_CONTROL_CANDIDATE_3B821DA938_SET`

- MAC 对象: `座位`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:191:意图1` — 给我加热座位的温度一直到最多

## 781. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `座位`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14006:意图1` — 座位现在可以进行加热了

## 782. `KNOWN_CONTROL_CANDIDATE_4B834145B2_TURN_ON`

- MAC 对象: `座位`
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4B834145B2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5533:意图2` — 打开座位按摩

## 783. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_SET`

- MAC 对象: `座位`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:311:意图1` — 设置座位通风

## 784. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `座位`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9352:意图2` — 打开座位通风

## 785. `KNOWN_CONTROL_CANDIDATE_6EEFA07291_SET`

- MAC 对象: `座垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_6EEFA07291 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11031:意图1` — 座垫倾斜加大

## 786. `KNOWN_CONTROL_CANDIDATE_6EEFA07291_TURN_ON`

- MAC 对象: `座垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_6EEFA07291 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19641:意图1` — 打开主驾座垫后背调节界面

## 787. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_SET`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调节']`
- 唯一样本数: **11**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10353:意图1` — 座椅调副驾座椅
- `train_set.jsonl:10376:意图1` — 调节一排左侧的座椅空调为外循环操作模式
- `train_set.jsonl:13389:意图1` — 我想调一下主驾座椅的参数谢谢
- `train_set.jsonl:14655:意图1` — 座椅调到5挡
- `train_set.jsonl:17144:意图1` — 调节座椅

## 788. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_SET`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15415:意图2` — 关闭空调

## 789. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_SET`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换为', '设置', '调', '调到', '调整为', '调节到']`
- 唯一样本数: **11**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19522:意图1` — 调节到座椅记忆功能3
- `dev_set.jsonl:19804:意图1` — 把主驾座椅调到位置一
- `test_set.jsonl:35:意图2` — 调到主驾坐姿一
- `train_set.jsonl:10353:意图2` — 调整为位置一
- `train_set.jsonl:12478:意图1` — 座椅记忆位置切换为上一个

## 790. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_SET`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13691:意图1` — 我的座椅裹太紧了

## 791. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_SET`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17054:意图2` — 打开座椅按摩挡位设为强

## 792. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_SET`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调一些', '调一点', '调到', '调节']`
- 唯一样本数: **32**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:898:意图2` — 座椅向前调
- `train_set.jsonl:10829:意图1` — 主驾座椅往下调一点
- `train_set.jsonl:12329:意图1` — 主驾座椅向上调节
- `train_set.jsonl:12742:意图1` — 把座椅往下
- `train_set.jsonl:12945:意图1` — 座椅往后放倒一点

## 793. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_SET`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调整', '调节']`
- 唯一样本数: **14**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19333:意图1` — 座椅温度调到最低
- `dev_set.jsonl:20418:意图1` — 座椅持续加热到头
- `train_set.jsonl:10552:意图1` — 帮我把座椅温度往下调一下
- `train_set.jsonl:11879:意图1` — 再调整一下座椅让它变得凉快一些
- `train_set.jsonl:14273:意图1` — 调热主驾座椅温度

## 794. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_SET`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调节']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:483:意图1` — 右前座椅角度大一点
- `train_set.jsonl:10861:意图1` — 第二排座椅角度往前调20度
- `train_set.jsonl:15007:意图1` — 左后座椅角度大一点
- `train_set.jsonl:3298:意图1` — 前排座椅角度往前调20度
- `train_set.jsonl:4078:意图1` — 左前座椅往后调30度

## 795. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_SET`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调为', '调到', '调至']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1386:意图3` — 空调调到两挡再帮我打开一下座椅通风调至二挡
- `train_set.jsonl:14349:意图2` — 打开座椅
- `train_set.jsonl:14976:意图3` — 打开空调打开座椅通风调到一挡
- `train_set.jsonl:16269:意图2` — 导航去景花园

## 796. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_SET`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调到', '调节']`
- 唯一样本数: **10**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19669:意图1` — 副驾座椅升到最高
- `train_set.jsonl:11627:意图1` — 座椅有点儿矮
- `train_set.jsonl:13432:意图1` — 我的座椅实在太高了
- `train_set.jsonl:15034:意图1` — 别调高座椅
- `train_set.jsonl:4285:意图1` — 不要调高座椅

## 797. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_ADJUST`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['滑', '滑动', '移']`
- 唯一样本数: **10**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20036:意图1` — 前排座椅后移
- `test_set.jsonl:293:意图1` — 副驾座椅移到最前面
- `test_set.jsonl:765:意图1` — 主驾座椅向前调一点
- `train_set.jsonl:10928:意图1` — 座椅朝前面滑
- `train_set.jsonl:14724:意图1` — 座椅后移

## 798. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_ADJUST`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13498:意图1` — 前面座椅往高移

## 799. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_TURN_OFF`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **9**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19472:意图1` — 关闭主驾的座椅调节
- `train_set.jsonl:12474:意图1` — 关闭座椅
- `train_set.jsonl:13885:意图1` — 关闭后排座椅
- `train_set.jsonl:14430:意图4` — 关闭主驾驶的座椅通风加热
- `train_set.jsonl:14430:意图5` — 关闭副驾驶的座椅通风加热

## 800. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '开一下', '开开', '打开']`
- 唯一样本数: **27**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19193:意图1` — 也把副驾驶的座椅打开
- `dev_set.jsonl:19764:意图2` — 打开座椅座椅通风
- `dev_set.jsonl:20248:意图1` — 打开全车座椅通风加热
- `test_set.jsonl:1117:意图1` — 开一下后排座椅的设置页面
- `test_set.jsonl:369:意图2` — 打开三排座椅

## 801. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12672:意图1` — 主驾打开一键躺平
- `train_set.jsonl:3474:意图1` — 主驾打开一键复位

## 802. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11003:意图3` — 打开副驾座椅往后调一点

## 803. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13518:意图1` — 打开我的座椅制冷
- `train_set.jsonl:13697:意图1` — 打开座椅一键成床

## 804. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['按', '转', '降']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11239:意图1` — 打开右前打开右前座椅通风
- `train_set.jsonl:11677:意图1` — 二排座椅转
- `train_set.jsonl:15438:意图1` — 座椅持续降温到低
- `train_set.jsonl:17888:意图1` — 副驾座椅恢复正常
- `train_set.jsonl:3473:意图3` — 打开座椅加热全部的座椅加热座椅按

## 805. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['保存', '储存', '加载', '复位', '存', '弄回去', '归位', '恢复', '恢复正常', '恢复默认', '设', '还原', '选择']`
- 唯一样本数: **29**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19843:意图1` — 打开三排座椅复位
- `dev_set.jsonl:20252:意图1` — 主驾座椅记忆储存为位置三
- `test_set.jsonl:1019:意图1` — 打开副驾座椅复位
- `test_set.jsonl:478:意图1` — 主驾座椅记忆选择为备用位
- `train_set.jsonl:10228:意图1` — 保存当前位置到坐姿二

## 806. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移一点']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8683:意图1` — 座椅向前移一点

## 807. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['转动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15076:意图1` — 座椅旋转180度

## 808. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `[]`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:982:意图1` — 座椅一键成床

## 809. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['升', '座', '更改一下', '热', '设', '降']`
- 唯一样本数: **7**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19578:意图1` — 主驾座椅给我稍微降低一点表面的温度
- `train_set.jsonl:12222:意图1` — 主驾座椅设为1
- `train_set.jsonl:12522:意图1` — 座椅温度升到最低
- `train_set.jsonl:14292:意图1` — 热一热坐着的车子的座椅
- `train_set.jsonl:15465:意图1` — 座椅稍微热会儿

## 810. `KNOWN_CONTROL_CANDIDATE_5A9FD33C7F_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['抬']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5A9FD33C7F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:19132:意图1` — 座椅抬高一点

## 811. `KNOWN_CONTROL_CANDIDATE_81B1B313BE_SET`

- MAC 对象: `座椅`
- MAC 对象功能: ``
- MAC 功能: `方便进出`
- MAC 子功能: ``
- MAC 操作: `['设为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_81B1B313BE + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9012:意图1` — 副驾座椅方便进出设为离车加上车

## 812. `KNOWN_CONTROL_CANDIDATE_A5C352D7DC_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `一键零重力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A5C352D7DC + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14872:意图1` — 座椅一键零重力打开

## 813. `KNOWN_CONTROL_CANDIDATE_CF1DBAD60A_TURN_OFF`

- MAC 对象: `座椅`
- MAC 对象功能: `出风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_CF1DBAD60A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6472:意图1` — 后排座椅的出风口给关死别让它吹风出来了

## 814. `KNOWN_CONTROL_CANDIDATE_CF1DBAD60A_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: `出风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['停止']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_CF1DBAD60A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18744:意图1` — 座椅停止出风

## 815. `KNOWN_CONTROL_CANDIDATE_F0F0327BC5_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `加`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_F0F0327BC5 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10981:意图1` — 设置主驾座椅温度加热

## 816. `KNOWN_CONTROL_CANDIDATE_3B821DA938_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5223:意图1` — 调一下座椅制冷

## 817. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:269:意图1` — 前排座椅加热通风打开自动模式

## 818. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1328:意图2` — 打开座椅加热二挡
- `train_set.jsonl:8166:意图2` — 打开座椅加热一挡

## 819. `KNOWN_CONTROL_CANDIDATE_3B821DA938_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['变更到', '可以关了']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17218:意图1` — 座椅帮我变更到一个更适合我的温度
- `train_set.jsonl:3671:意图1` — 座椅加热可以关了

## 820. `KNOWN_CONTROL_CANDIDATE_764CD73EDB_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `加热功能`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_764CD73EDB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11680:意图1` — 开开座椅加热功能

## 821. `KNOWN_CONTROL_CANDIDATE_A498C8396D_TURN_OFF`

- MAC 对象: `座椅`
- MAC 对象功能: `动力学`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_A498C8396D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17367:意图1` — 关闭副驾座椅动力学

## 822. `KNOWN_CONTROL_CANDIDATE_C85115C06E_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `同步座椅通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_C85115C06E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10443:意图1` — 打开同步座椅通风

## 823. `KNOWN_CONTROL_CANDIDATE_E798A20D1F_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `声场优化`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E798A20D1F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4896:意图1` — 车内座椅声场优化模式开启

## 824. `KNOWN_CONTROL_CANDIDATE_0CEF63DF2E_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `完全放平`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_0CEF63DF2E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14603:意图1` — 座椅完全放平

## 825. `KNOWN_CONTROL_CANDIDATE_37350F633D_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `律动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_37350F633D + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3297:意图1` — 调节座椅律动

## 826. `KNOWN_CONTROL_CANDIDATE_37350F633D_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `律动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_37350F633D + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19970:意图1` — 座椅律动强度调为弱
- `train_set.jsonl:3282:意图1` — 座椅律动升到最高

## 827. `KNOWN_CONTROL_CANDIDATE_37350F633D_TURN_OFF`

- MAC 对象: `座椅`
- MAC 对象功能: `律动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_37350F633D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7071:意图2` — 关闭座椅律动

## 828. `KNOWN_CONTROL_CANDIDATE_37350F633D_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `律动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_37350F633D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12381:意图1` — 打开座椅律动
- `train_set.jsonl:14587:意图4` — 打开全车座椅律动
- `train_set.jsonl:16722:意图2` — 打开座椅律动
- `train_set.jsonl:5300:意图1` — 打开主驾座椅律动
- `train_set.jsonl:9677:意图1` — 打开全车座椅律动

## 829. `KNOWN_CONTROL_CANDIDATE_37350F633D_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: `律动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_37350F633D + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2696:意图1` — 把主驾座椅律动设为最高

## 830. `KNOWN_CONTROL_CANDIDATE_F9732A54E4_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `折起来`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_F9732A54E4 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15545:意图1` — 把后排位置折起来吧

## 831. `KNOWN_CONTROL_CANDIDATE_66E3BDA2C8_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `抬直`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_66E3BDA2C8 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11468:意图1` — 右后座椅抬直
- `train_set.jsonl:7356:意图1` — 座椅抬直

## 832. `KNOWN_CONTROL_CANDIDATE_4B834145B2_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换', '设置']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4B834145B2 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16144:意图1` — 设置座椅按摩
- `train_set.jsonl:4951:意图1` — 座椅按摩切换下一个

## 833. `KNOWN_CONTROL_CANDIDATE_4B834145B2_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4B834145B2 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13296:意图1` — 上一个座椅按摩模式
- `train_set.jsonl:18488:意图1` — 前面的一个座椅按摩模式
- `train_set.jsonl:4012:意图1` — 座椅按摩模式为背部放松
- `train_set.jsonl:6723:意图1` — 座椅按摩模式为背部舒展
- `train_set.jsonl:7316:意图1` — 下一个座椅按摩模式切换

## 834. `KNOWN_CONTROL_CANDIDATE_4B834145B2_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_4B834145B2 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4812:意图1` — 太累了座椅按摩开下二排右边的

## 835. `KNOWN_CONTROL_CANDIDATE_2302DF89DD_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `按摩功能`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '调']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_2302DF89DD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14081:意图1` — 把主驾驶座椅按摩功能调为肩部舒展
- `train_set.jsonl:14317:意图1` — 把主驾座椅按摩功能设置为背部放松
- `train_set.jsonl:6582:意图1` — 把主驾驶座椅按摩功能调为背部激活
- `train_set.jsonl:8631:意图1` — 把主驾驶座椅按摩功能调为背部放松

## 836. `KNOWN_CONTROL_CANDIDATE_666918A03F_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `放倒`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_666918A03F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6787:意图1` — 放倒后排座椅

## 837. `KNOWN_CONTROL_CANDIDATE_35B6839084_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `放平`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_35B6839084 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20093:意图2` — 放平后排座椅
- `train_set.jsonl:3727:意图2` — 主驾座椅放平

## 838. `KNOWN_CONTROL_CANDIDATE_658E9659C1_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `放直`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_658E9659C1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4998:意图1` — 主副驾座椅放直
- `train_set.jsonl:4998:意图2` — 随机播放音乐

## 839. `KNOWN_CONTROL_CANDIDATE_221A4FE89C_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `智能理疗`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_221A4FE89C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11940:意图1` — 打开座椅智能理疗

## 840. `KNOWN_CONTROL_CANDIDATE_312490EDA9_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_312490EDA9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11206:意图1` — 后排座椅稍微热会儿
- `train_set.jsonl:17930:意图2` — 把主驾座椅加热打开通风打开

## 841. `KNOWN_CONTROL_CANDIDATE_BF0A16B5F8_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `热一热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BF0A16B5F8 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12635:意图1` — 座椅稍微热一热

## 842. `KNOWN_CONTROL_CANDIDATE_9D0F2108A7_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `理疗模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_9D0F2108A7 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19785:意图1` — 打开座椅理疗模式

## 843. `KNOWN_CONTROL_CANDIDATE_3B2AE30B0C_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `直立`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B2AE30B0C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:704:意图1` — 前排座椅直立
- `train_set.jsonl:10559:意图1` — 座椅直立

## 844. `KNOWN_CONTROL_CANDIDATE_FCD34A1F42_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `竖直`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_FCD34A1F42 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:842:意图1` — 主驾座椅竖直
- `train_set.jsonl:10343:意图1` — 右后座椅竖直
- `train_set.jsonl:4601:意图1` — 座椅竖直

## 845. `KNOWN_CONTROL_CANDIDATE_003162B2D9_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `肩部位置`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_003162B2D9 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11440:意图1` — 座椅肩部位置调节至10%

## 846. `KNOWN_CONTROL_CANDIDATE_003162B2D9_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `肩部位置`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_003162B2D9 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20312:意图1` — 座椅肩部位置调到最前

## 847. `KNOWN_CONTROL_CANDIDATE_8C27F26A1B_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `躺下`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_8C27F26A1B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6799:意图1` — 二排左座椅躺下

## 848. `KNOWN_CONTROL_CANDIDATE_D29A481772_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `躺平`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_D29A481772 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8220:意图1` — 右前座椅躺平

## 849. `KNOWN_CONTROL_CANDIDATE_044786200C_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `迎宾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_044786200C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11932:意图1` — 座椅迎宾

## 850. `KNOWN_CONTROL_CANDIDATE_B56DF75B63_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `通通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_B56DF75B63 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1765:意图2` — 打开座椅通通风

## 851. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13283:意图2` — 留下主驾座椅通风

## 852. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_OFF`

- MAC 对象: `座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15232:意图1` — 座椅通风自动关闭

## 853. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:269:意图2` — 前排座椅加热通风打开自动模式

## 854. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '打开']`
- 唯一样本数: **11**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:986:意图3` — 主驾驶座椅通风开到最大
- `train_set.jsonl:13226:意图2` — 打开座椅通风最大挡
- `train_set.jsonl:14398:意图2` — 打开座椅通风一挡
- `train_set.jsonl:17523:意图1` — 座椅通风开到最大
- `train_set.jsonl:2164:意图3` — 空调调到二十六度风量为一打开我的座椅通风一挡

## 855. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['更改一下', '退出']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17417:意图1` — 我想更改一下座椅通风
- `train_set.jsonl:3006:意图2` — 退出座椅通风

## 856. `KNOWN_CONTROL_CANDIDATE_E389FF8EA4_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `通风模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E389FF8EA4 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3399:意图1` — 后排帮我切换到座椅通风模式

## 857. `KNOWN_CONTROL_CANDIDATE_030B7A7207_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `零重力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_030B7A7207 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11984:意图1` — 调节零重力座椅
- `train_set.jsonl:14788:意图1` — 调节右前座椅零重力

## 858. `KNOWN_CONTROL_CANDIDATE_030B7A7207_ADJUST`

- MAC 对象: `座椅`
- MAC 对象功能: `零重力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_030B7A7207 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12246:意图1` — 零重力座椅后移

## 859. `KNOWN_CONTROL_CANDIDATE_030B7A7207_TURN_OFF`

- MAC 对象: `座椅`
- MAC 对象功能: `零重力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关上', '关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_030B7A7207 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12472:意图1` — 调一下零重力座椅关上吧
- `train_set.jsonl:13714:意图1` — 好了座椅的零重力快断了

## 860. `KNOWN_CONTROL_CANDIDATE_030B7A7207_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `零重力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_030B7A7207 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15243:意图2` — 打开零重力座椅
- `train_set.jsonl:16204:意图1` — 打开副驾零重力座椅
- `train_set.jsonl:8450:意图1` — 打开副驾零重力座椅模式

## 861. `KNOWN_CONTROL_CANDIDATE_030B7A7207_REVIEW`

- MAC 对象: `座椅`
- MAC 对象功能: `零重力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_030B7A7207 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7275:意图1` — 零重力座椅不合适给我改一下

## 862. `KNOWN_CONTROL_CANDIDATE_44349279C2_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `震动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_44349279C2 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15299:意图1` — 主驾座椅震动调到1挡

## 863. `KNOWN_CONTROL_CANDIDATE_44349279C2_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `震动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_44349279C2 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3506:意图1` — 座椅震动强度调到弱

## 864. `KNOWN_CONTROL_CANDIDATE_44349279C2_TURN_OFF`

- MAC 对象: `座椅`
- MAC 对象功能: `震动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_44349279C2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:19144:意图2` — 关闭座椅震动

## 865. `KNOWN_CONTROL_CANDIDATE_E79EA92734_SET`

- MAC 对象: `座椅`
- MAC 对象功能: `音场优化`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E79EA92734 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13605:意图1` — 调节座椅音场优化设置

## 866. `KNOWN_CONTROL_CANDIDATE_E79EA92734_TURN_ON`

- MAC 对象: `座椅`
- MAC 对象功能: `音场优化`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E79EA92734 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14764:意图1` — 进入座椅音场优化模式

## 867. `KNOWN_CONTROL_CANDIDATE_071C98D7A3_SET`

- MAC 对象: `座椅位置`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_071C98D7A3 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9358:意图1` — 座椅位置往前走

## 868. `KNOWN_CONTROL_CANDIDATE_DCF1A894FB_SET`

- MAC 对象: `座椅侧翼`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_DCF1A894FB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19198:意图1` — 主驾座椅侧翼紧一点
- `dev_set.jsonl:20261:意图1` — 将座椅侧翼包裹得更紧一点吧
- `dev_set.jsonl:20515:意图1` — 前排座椅侧翼松一点
- `train_set.jsonl:10624:意图1` — 右后座椅侧翼松一点
- `train_set.jsonl:18997:意图1` — 副驾座椅侧翼紧一点

## 869. `KNOWN_CONTROL_CANDIDATE_75DEB61AC5_SET`

- MAC 对象: `座椅包裹`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_75DEB61AC5 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:370:意图1` — 左后座椅包裹松一点
- `train_set.jsonl:6643:意图1` — 右后座椅包裹松一点

## 870. `KNOWN_CONTROL_CANDIDATE_567E14A8A6_SET`

- MAC 对象: `座椅后背`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_567E14A8A6 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16276:意图1` — 把副驾座椅后背调节界面打开
- `train_set.jsonl:16637:意图1` — 主驾座椅后背调节界面打开

## 871. `KNOWN_CONTROL_CANDIDATE_567E14A8A6_TURN_ON`

- MAC 对象: `座椅后背`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_567E14A8A6 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15732:意图1` — 座椅后背设置界面帮我开一下啊

## 872. `KNOWN_CONTROL_CANDIDATE_567E14A8A6_REVIEW`

- MAC 对象: `座椅后背`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['进入']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_567E14A8A6 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7296:意图1` — 进入座椅后背设置界面

## 873. `KNOWN_CONTROL_CANDIDATE_A54B164156_SET`

- MAC 对象: `座椅坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A54B164156 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1498:意图1` — 把座椅坐垫高度倾斜到最下

## 874. `KNOWN_CONTROL_CANDIDATE_A54B164156_SET`

- MAC 对象: `座椅坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A54B164156 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13645:意图1` — 座椅坐垫整体往高上
- `train_set.jsonl:14854:意图1` — 座椅坐垫整体往高上移动

## 875. `KNOWN_CONTROL_CANDIDATE_A54B164156_TURN_ON`

- MAC 对象: `座椅坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A54B164156 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5255:意图1` — 打开副驾座椅坐垫调节界面

## 876. `KNOWN_CONTROL_CANDIDATE_A54B164156_REVIEW`

- MAC 对象: `座椅坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A54B164156 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11249:意图1` — 座椅坐垫往低下动

## 877. `KNOWN_CONTROL_CANDIDATE_219A1153F5_SET`

- MAC 对象: `座椅坐盆`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_219A1153F5 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8928:意图1` — 主驾座椅坐盆调到中间位置

## 878. `KNOWN_CONTROL_CANDIDATE_F88D3D44D2_SET`

- MAC 对象: `座椅头枕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['暂停调节', '调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_F88D3D44D2 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12946:意图1` — 座椅头枕暂停调节
- `train_set.jsonl:7598:意图1` — 调节座椅头枕

## 879. `KNOWN_CONTROL_CANDIDATE_84A07F292F_TURN_ON`

- MAC 对象: `座椅脚托`
- MAC 对象功能: `折叠`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_84A07F292F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17306:意图1` — 座椅脚托收起

## 880. `KNOWN_CONTROL_CANDIDATE_4A86C2AE30_SET`

- MAC 对象: `座椅脚踏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4A86C2AE30 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:157:意图1` — 把前面座椅脚踏温度调高

## 881. `KNOWN_CONTROL_CANDIDATE_4A86C2AE30_SET`

- MAC 对象: `座椅脚踏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4A86C2AE30 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8736:意图1` — 后面座椅脚踏向高调节

## 882. `KNOWN_CONTROL_CANDIDATE_FF3D01CF00_TURN_ON`

- MAC 对象: `座椅腰部`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '开一下', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_FF3D01CF00 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:716:意图1` — 我想改改座椅腰部界面赶紧帮我开一开
- `train_set.jsonl:1856:意图1` — 打开女王座椅腰部调节界面
- `train_set.jsonl:1925:意图1` — 帮我开一下座椅腰部设置界面

## 883. `KNOWN_CONTROL_CANDIDATE_4B834145B2_TURN_ON`

- MAC 对象: `座椅腰部`
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4B834145B2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:702:意图1` — 打开座椅腰部按摩

## 884. `KNOWN_CONTROL_CANDIDATE_359E40AE51_SET`

- MAC 对象: `座椅腿托`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_359E40AE51 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17452:意图1` — 副驾座椅腿托太往上了
- `train_set.jsonl:17971:意图1` — 副驾座椅腿托太往下了
- `train_set.jsonl:3283:意图1` — 副驾座椅腿托太往后了

## 885. `KNOWN_CONTROL_CANDIDATE_359E40AE51_SET`

- MAC 对象: `座椅腿托`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_359E40AE51 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14105:意图1` — 副驾腿托往下一点
- `train_set.jsonl:17048:意图1` — 座椅腿托调太高了
- `train_set.jsonl:2491:意图1` — 前排腿托往下一点

## 886. `KNOWN_CONTROL_CANDIDATE_3B821DA938_SET`

- MAC 对象: `座椅靠背`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18492:意图1` — 把右后的座椅靠背加热升高1级

## 887. `KNOWN_CONTROL_CANDIDATE_7B3B850C4A_SET`

- MAC 对象: `开车模式`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换成']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7B3B850C4A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:681:意图1` — 开车模式切换成竞速模式
- `train_set.jsonl:10975:意图1` — 开车模式切换成运动模式

## 888. `KNOWN_CONTROL_CANDIDATE_7B3B850C4A_REVIEW`

- MAC 对象: `开车模式`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['变更为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7B3B850C4A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:709:意图1` — 开车模式变更为雪地模式

## 889. `KNOWN_CONTROL_CANDIDATE_E6B2301831_TURN_ON`

- MAC 对象: `心跳氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E6B2301831 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1712:意图1` — 打开心跳氛围灯

## 890. `KNOWN_CONTROL_CANDIDATE_82F3D7D2EF_SET`

- MAC 对象: `悬挂`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调整', '调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_82F3D7D2EF + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10412:意图1` — 调整为较低的悬挂高度
- `train_set.jsonl:4878:意图1` — 较低的悬挂高度

## 891. `KNOWN_CONTROL_CANDIDATE_5BE88EB977_SET`

- MAC 对象: `悬架`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5BE88EB977 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18141:意图1` — 悬架阻尼设置为偏硬

## 892. `KNOWN_CONTROL_CANDIDATE_5BE88EB977_SET`

- MAC 对象: `悬架`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调整', '调节']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5BE88EB977 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:511:意图1` — 调节悬架高度为非常高
- `train_set.jsonl:16670:意图1` — 降低悬架高度
- `train_set.jsonl:18187:意图1` — 将悬架高度调整为中间的设置
- `train_set.jsonl:2279:意图1` — 将悬架高度调整到最高
- `train_set.jsonl:2284:意图1` — 悬架高度调到最高

## 893. `KNOWN_CONTROL_CANDIDATE_5BE88EB977_TURN_OFF`

- MAC 对象: `悬架`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_5BE88EB977 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7954:意图1` — 悬架调节设置页面关闭

## 894. `KNOWN_CONTROL_CANDIDATE_DB0ED2E25B_TURN_OFF`

- MAC 对象: `悬架`
- MAC 对象功能: ``
- MAC 功能: `方便上下车`
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_DB0ED2E25B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1376:意图1` — 关闭悬架方便上下车

## 895. `KNOWN_CONTROL_CANDIDATE_DB0ED2E25B_TURN_ON`

- MAC 对象: `悬架`
- MAC 对象功能: ``
- MAC 功能: `方便上下车`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DB0ED2E25B + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:419:意图1` — 打开悬架方便上下车

## 896. `KNOWN_CONTROL_CANDIDATE_30BC5C7B4C_SET`

- MAC 对象: `我要`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_30BC5C7B4C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12855:意图1` — 我要设置一下车内灯好吗

## 897. `KNOWN_CONTROL_CANDIDATE_8FF5A0C251_TURN_OFF`

- MAC 对象: `手套箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_8FF5A0C251 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6139:意图1` — 关闭手套箱

## 898. `KNOWN_CONTROL_CANDIDATE_8FF5A0C251_TURN_ON`

- MAC 对象: `手套箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_8FF5A0C251 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11972:意图1` — 打开手套箱

## 899. `KNOWN_CONTROL_CANDIDATE_130A70199C_SET`

- MAC 对象: `扩散器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_130A70199C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5910:意图1` — 扩散器设置为手动模式

## 900. `KNOWN_CONTROL_CANDIDATE_130A70199C_TURN_ON`

- MAC 对象: `扩散器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_130A70199C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10400:意图1` — 打开扩散器

## 901. `KNOWN_CONTROL_CANDIDATE_9DECBF71E4_SET`

- MAC 对象: `扬声器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调整']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_9DECBF71E4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18920:意图1` — 让车外的扬声器别那么吵给我调整一下

## 902. `KNOWN_CONTROL_CANDIDATE_9DECBF71E4_SET`

- MAC 对象: `扬声器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '调节']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_9DECBF71E4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19589:意图1` — 车外扬声器声音小一些
- `train_set.jsonl:10157:意图1` — 设置一下车外扬声器让声音到50%的位置
- `train_set.jsonl:10304:意图1` — 将车外扬声器整体提升10%的声音
- `train_set.jsonl:11327:意图1` — 削弱外面扬声器的声音大概20%
- `train_set.jsonl:16844:意图1` — 车外扬声器太吵了直接调到最低声音

## 903. `KNOWN_CONTROL_CANDIDATE_9DECBF71E4_SET`

- MAC 对象: `扬声器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_9DECBF71E4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17673:意图1` — 升起扬声器

## 904. `KNOWN_CONTROL_CANDIDATE_9DECBF71E4_REVIEW`

- MAC 对象: `扬声器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['提升']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_9DECBF71E4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11253:意图1` — 提升声音的10%给外面的扬声器

## 905. `KNOWN_CONTROL_CANDIDATE_6115B9402D_ADJUST`

- MAC 对象: `扶手箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_6115B9402D + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14832:意图1` — 请将扶手箱往前方移动

## 906. `KNOWN_CONTROL_CANDIDATE_5B5DBB4858_TURN_OFF`

- MAC 对象: `折叠屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_5B5DBB4858 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7616:意图1` — 关闭折叠屏

## 907. `KNOWN_CONTROL_CANDIDATE_CD673799CE_SET`

- MAC 对象: `护眼灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_CD673799CE + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16614:意图1` — 护眼灯亮度调低5档

## 908. `KNOWN_CONTROL_CANDIDATE_B0CDD0667F_TURN_OFF`

- MAC 对象: `报警灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关上']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_B0CDD0667F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7571:意图1` — 关上报警灯

## 909. `KNOWN_CONTROL_CANDIDATE_62874EBFD1_TURN_ON`

- MAC 对象: `抬头显`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_62874EBFD1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16940:意图1` — 打开抬头显调整页面

## 910. `KNOWN_CONTROL_CANDIDATE_87B8552BEF_SET`

- MAC 对象: `抬头显示`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_87B8552BEF + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19935:意图1` — 抬头显示调低一挡
- `train_set.jsonl:11306:意图1` — 抬头显示调低百分之五十
- `train_set.jsonl:16766:意图1` — 抬头显示不是我想要的位置改一下吧

## 911. `KNOWN_CONTROL_CANDIDATE_87B8552BEF_SET`

- MAC 对象: `抬头显示`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_87B8552BEF + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12807:意图1` — 抬头显示调成性能视图

## 912. `KNOWN_CONTROL_CANDIDATE_87B8552BEF_SET`

- MAC 对象: `抬头显示`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '调', '调节']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_87B8552BEF + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16956:意图1` — 抬头显示画面调低点
- `train_set.jsonl:2716:意图1` — 抬头显示页面调最低
- `train_set.jsonl:7730:意图1` — 怎么才能设置抬头显示的高度

## 913. `KNOWN_CONTROL_CANDIDATE_87B8552BEF_REVIEW`

- MAC 对象: `抬头显示`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改为', '选择']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_87B8552BEF + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15063:意图1` — 抬头显示显示风格选择标准
- `train_set.jsonl:4833:意图1` — 把抬头显示改为雪地模式

## 914. `KNOWN_CONTROL_CANDIDATE_FFAB66C18C_TURN_ON`

- MAC 对象: `拐弯灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_FFAB66C18C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17145:意图1` — 打开拐弯灯

## 915. `KNOWN_CONTROL_CANDIDATE_679BD037D8_TURN_OFF`

- MAC 对象: `拖车钩`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_679BD037D8 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19742:意图1` — 关闭拖车钩

## 916. `KNOWN_CONTROL_CANDIDATE_7C7577D4D4_SET`

- MAC 对象: `按键`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7C7577D4D4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6889:意图1` — 按键亮一点

## 917. `KNOWN_CONTROL_CANDIDATE_7702563A24_SET`

- MAC 对象: `挡风玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到', '调成']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7702563A24 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:987:意图1` — 把后挡风玻璃调到零透明度
- `train_set.jsonl:11147:意图1` — 把后挡风玻璃调成零透明度

## 918. `KNOWN_CONTROL_CANDIDATE_7702563A24_TURN_ON`

- MAC 对象: `挡风玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7702563A24 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14932:意图2` — 打开前挡风玻璃

## 919. `KNOWN_CONTROL_CANDIDATE_80905C1B99_TURN_OFF`

- MAC 对象: `挡风窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_80905C1B99 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10315:意图1` — 关闭挡风窗

## 920. `KNOWN_CONTROL_CANDIDATE_FAC308FBAB_SET`

- MAC 对象: `摄像头`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_FAC308FBAB + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3427:意图1` — 缩小摄像头画面

## 921. `KNOWN_CONTROL_CANDIDATE_FAC308FBAB_SET`

- MAC 对象: `摄像头`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_FAC308FBAB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18395:意图1` — 摄像头使用有效期设为12个月

## 922. `KNOWN_CONTROL_CANDIDATE_FAC308FBAB_REVIEW`

- MAC 对象: `摄像头`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_FAC308FBAB + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2872:意图1` — 查看摄像头

## 923. `KNOWN_CONTROL_CANDIDATE_FAC308FBAB_REVIEW`

- MAC 对象: `摄像头`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['显示']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_FAC308FBAB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10005:意图1` — 显示摄像头视图

## 924. `KNOWN_CONTROL_CANDIDATE_10DCCB73CB_SET`

- MAC 对象: `整车`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调低', '调节']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_10DCCB73CB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:588:意图1` — 整车背光亮度调到最高
- `train_set.jsonl:17489:意图1` — 整车背光亮度太亮了
- `train_set.jsonl:18613:意图1` — 整车背光亮度调到最亮
- `train_set.jsonl:4522:意图1` — 整车背光亮度调到最低
- `train_set.jsonl:8665:意图1` — 调低整车背光亮度到最暗

## 925. `KNOWN_CONTROL_CANDIDATE_10DCCB73CB_SET`

- MAC 对象: `整车`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换', '切换成', '设为', '调节']`
- 唯一样本数: **7**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_10DCCB73CB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19711:意图1` — 切换驾驶模式
- `train_set.jsonl:11698:意图2` — 调为四驱
- `train_set.jsonl:14567:意图1` — 更改驾驶设置为漂移模式
- `train_set.jsonl:18286:意图1` — 把汽车运行模式切换成运动模式
- `train_set.jsonl:1943:意图1` — 驾驶方式设为舒适

## 926. `KNOWN_CONTROL_CANDIDATE_10DCCB73CB_TURN_ON`

- MAC 对象: `整车`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启动', '开启', '打开']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_10DCCB73CB + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20051:意图1` — 用自定义模式驾驶
- `train_set.jsonl:12874:意图1` — 开启泥泞驾驶模式
- `train_set.jsonl:12947:意图1` — 启动泥泞驾驶模式
- `train_set.jsonl:16602:意图1` — 打开驾驶模式调节
- `train_set.jsonl:17724:意图1` — 开启雪天驾驶模式

## 927. `KNOWN_CONTROL_CANDIDATE_10DCCB73CB_REVIEW`

- MAC 对象: `整车`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_10DCCB73CB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12967:意图1` — 驾驶模式改为混那

## 928. `KNOWN_CONTROL_CANDIDATE_2D693C5390_TURN_ON`

- MAC 对象: `整车`
- MAC 对象功能: ``
- MAC 功能: `智慧巡航`
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `True` `['CRUISE_DISABLE', 'CRUISE_ENABLE', 'CRUISE_SET_GAP', 'CRUISE_SET_SPEED']`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2D693C5390 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13087:意图1` — 自动驾驶模式开启

## 929. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_TURN_ON`

- MAC 对象: `整车`
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6342:意图1` — 调整电池百分比

## 930. `KNOWN_CONTROL_CANDIDATE_A2560CA902_SET`

- MAC 对象: `方向盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A2560CA902 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13102:意图1` — 方向盘调节

## 931. `KNOWN_CONTROL_CANDIDATE_A2560CA902_SET`

- MAC 对象: `方向盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调一点']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A2560CA902 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8407:意图1` — 方向盘往内调一点

## 932. `KNOWN_CONTROL_CANDIDATE_A2560CA902_SET`

- MAC 对象: `方向盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为', '调为']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A2560CA902 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3605:意图1` — 方向盘调为运动模式
- `train_set.jsonl:4203:意图1` — 我想要将方向盘设置为舒适模式

## 933. `KNOWN_CONTROL_CANDIDATE_A2560CA902_SET`

- MAC 对象: `方向盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A2560CA902 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16086:意图1` — 方向盘烫手
- `train_set.jsonl:3185:意图1` — 方向盘温度调高两档

## 934. `KNOWN_CONTROL_CANDIDATE_A2560CA902_SET`

- MAC 对象: `方向盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A2560CA902 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3001:意图1` — 方向盘转向力最轻

## 935. `KNOWN_CONTROL_CANDIDATE_A2560CA902_TURN_ON`

- MAC 对象: `方向盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A2560CA902 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10807:意图1` — 开启方向盘
- `train_set.jsonl:16825:意图1` — 打开方向盘和座椅加热

## 936. `KNOWN_CONTROL_CANDIDATE_3B821DA938_SET`

- MAC 对象: `方向盘`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19262:意图1` — 方向盘加热温度不够低
- `train_set.jsonl:14046:意图1` — 方向盘加热调到低档
- `train_set.jsonl:17178:意图1` — 调高方向盘加热
- `train_set.jsonl:18062:意图2` — 方向盘加热二挡

## 937. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_OFF`

- MAC 对象: `方向盘`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16939:意图1` — 关闭方向盘低温自动加热

## 938. `KNOWN_CONTROL_CANDIDATE_C9F16BB1E9_SET`

- MAC 对象: `方向盘`
- MAC 对象功能: `动力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C9F16BB1E9 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5489:意图1` — 方向盘动力设为轻

## 939. `KNOWN_CONTROL_CANDIDATE_7127B4D3DD_SET`

- MAC 对象: `方向盘`
- MAC 对象功能: `助力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7127B4D3DD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16615:意图1` — 我想改改方向盘助力力度的配置
- `train_set.jsonl:7136:意图1` — 我想调调方向盘助力力度的设置

## 940. `KNOWN_CONTROL_CANDIDATE_7127B4D3DD_SET`

- MAC 对象: `方向盘`
- MAC 对象功能: `助力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换到', '调', '调为', '调整为', '调节']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7127B4D3DD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11523:意图1` — 方向盘帮我把它的助力力度修改成轻
- `train_set.jsonl:12455:意图1` — 转向调舒适模式
- `train_set.jsonl:16126:意图1` — 方向盘转向助力调整为舒适
- `train_set.jsonl:17967:意图1` — 方向盘助力的力度帮我更改成轻
- `train_set.jsonl:2283:意图1` — 转向模式切换到适中

## 941. `KNOWN_CONTROL_CANDIDATE_7127B4D3DD_SET`

- MAC 对象: `方向盘`
- MAC 对象功能: `助力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7127B4D3DD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2269:意图1` — 方向盘力量最大

## 942. `KNOWN_CONTROL_CANDIDATE_7127B4D3DD_TURN_ON`

- MAC 对象: `方向盘`
- MAC 对象功能: `助力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7127B4D3DD + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14344:意图1` — 打开方向盘动力
- `train_set.jsonl:17789:意图1` — 方向盘助力开始工作

## 943. `KNOWN_CONTROL_CANDIDATE_7127B4D3DD_REVIEW`

- MAC 对象: `方向盘`
- MAC 对象功能: `助力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['选择']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7127B4D3DD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17839:意图1` — 转向模式选择为适中

## 944. `KNOWN_CONTROL_CANDIDATE_73A0ABCD81_TURN_OFF`

- MAC 对象: `方向盘`
- MAC 对象功能: `取暖`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_73A0ABCD81 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19905:意图1` — 关闭方向盘取暖

## 945. `KNOWN_CONTROL_CANDIDATE_3F4E4080CE_TURN_ON`

- MAC 对象: `方向盘`
- MAC 对象功能: `热一下`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3F4E4080CE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2628:意图1` — 方向盘给我热一下

## 946. `KNOWN_CONTROL_CANDIDATE_404AFCD968_TURN_OFF`

- MAC 对象: `旋转灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_404AFCD968 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:353:意图1` — 关闭中排左旋转灯

## 947. `KNOWN_CONTROL_CANDIDATE_3819D37827_TURN_OFF`

- MAC 对象: `日间行车灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3819D37827 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8332:意图2` — 关闭日间行车灯

## 948. `KNOWN_CONTROL_CANDIDATE_3819D37827_TURN_ON`

- MAC 对象: `日间行车灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3819D37827 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16756:意图2` — 打开日间行车灯

## 949. `KNOWN_CONTROL_CANDIDATE_E27405C6DF_TURN_ON`

- MAC 对象: `星环氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E27405C6DF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10410:意图1` — 打开星环氛围灯

## 950. `KNOWN_CONTROL_CANDIDATE_7DBB1D8407_SET`

- MAC 对象: `星空穹顶`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7DBB1D8407 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7245:意图1` — 星空穹顶亮度设为最亮

## 951. `KNOWN_CONTROL_CANDIDATE_AA2D2C0710_SET`

- MAC 对象: `星空顶`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_AA2D2C0710 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11313:意图1` — 星空顶亮度切换为最低挡
- `train_set.jsonl:13311:意图1` — 切换最低档星空顶亮度

## 952. `KNOWN_CONTROL_CANDIDATE_AA2D2C0710_REVIEW`

- MAC 对象: `星空顶`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['换一个']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_AA2D2C0710 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13267:意图1` — 星空顶换一个主题

## 953. `KNOWN_CONTROL_CANDIDATE_C9B830F1A6_TURN_OFF`

- MAC 对象: `星空顶棚`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_C9B830F1A6 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18217:意图1` — 星空顶棚关闭

## 954. `KNOWN_CONTROL_CANDIDATE_4AA9D97F9A_TURN_ON`

- MAC 对象: `星空顶棚`
- MAC 对象功能: `联动迎宾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4AA9D97F9A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12692:意图1` — 星空顶棚联动迎宾为我打开

## 955. `KNOWN_CONTROL_CANDIDATE_1A13EA5910_TURN_OFF`

- MAC 对象: `显示器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_1A13EA5910 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13513:意图2` — 关闭显示器

## 956. `KNOWN_CONTROL_CANDIDATE_6F39985439_REVIEW`

- MAC 对象: `显示屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移动下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_6F39985439 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6261:意图1` — 移动下副驾显示屏

## 957. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_OFF`

- MAC 对象: `智能儿童座椅`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8089:意图1` — 智能儿童座椅关闭加热

## 958. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `智能儿童座椅`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2836:意图1` — 启动智能儿童座椅加热

## 959. `KNOWN_CONTROL_CANDIDATE_3B821DA938_REVIEW`

- MAC 对象: `智能儿童座椅`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['退出']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3978:意图1` — 智能儿童座椅退出加热

## 960. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_OFF`

- MAC 对象: `智能儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11129:意图1` — 智能儿童座椅关闭自然风
- `train_set.jsonl:18829:意图1` — 关闭智能儿童座椅自然通风
- `train_set.jsonl:7874:意图1` — 退出智能儿童座椅自然通风

## 961. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `智能儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4957:意图1` — 智能儿童座椅打开通风

## 962. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `智能儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启动', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1766:意图1` — 自然通风智能儿童座椅
- `train_set.jsonl:9714:意图1` — 智能儿童座椅启动自然通风

## 963. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_REVIEW`

- MAC 对象: `智能儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['退出']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12554:意图1` — 智能儿童座椅退出通风
- `train_set.jsonl:4524:意图1` — 退出智能儿童座椅通风

## 964. `KNOWN_CONTROL_CANDIDATE_0DCD1E0EB6_TURN_OFF`

- MAC 对象: `智能底盘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_0DCD1E0EB6 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4009:意图1` — 关闭智能底盘设置

## 965. `KNOWN_CONTROL_CANDIDATE_7AA54F1E54_TURN_OFF`

- MAC 对象: `智能除味`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_7AA54F1E54 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4699:意图1` — 关闭智能除味

## 966. `KNOWN_CONTROL_CANDIDATE_7AA54F1E54_TURN_ON`

- MAC 对象: `智能除味`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7AA54F1E54 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20130:意图1` — 开启智能除味
- `train_set.jsonl:18565:意图1` — 打开智能除味

## 967. `KNOWN_CONTROL_CANDIDATE_B9BFD31D4F_SET`

- MAC 对象: `智能香氛器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_B9BFD31D4F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10202:意图1` — 设置智能香氛器香味为低浓度

## 968. `KNOWN_CONTROL_CANDIDATE_B9BFD31D4F_REVIEW`

- MAC 对象: `智能香氛器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['停止']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_B9BFD31D4F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:221:意图1` — 停止智能香氛器

## 969. `KNOWN_CONTROL_CANDIDATE_145676361E_TURN_OFF`

- MAC 对象: `机`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_145676361E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19600:意图1` — 关机
- `train_set.jsonl:17473:意图1` — 关机
- `train_set.jsonl:5639:意图1` — 请关机
- `train_set.jsonl:6671:意图2` — 关音乐关机

## 970. `KNOWN_CONTROL_CANDIDATE_4B834145B2_SET`

- MAC 对象: `椅`
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4B834145B2 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15211:意图1` — 将按摩椅的档位调到二试试
- `train_set.jsonl:3842:意图1` — 将按摩椅的档位调到最轻柔试试

## 971. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_SET`

- MAC 对象: `椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19722:意图1` — 主驾座椅通风风挡调到最低
- `train_set.jsonl:13005:意图1` — 主驾座椅通风调到二档

## 972. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:493:意图3` — 风量调最大挡再后排空调打开座椅通风

## 973. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18448:意图1` — 打开主驾座椅通风一挡

## 974. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_REVIEW`

- MAC 对象: `椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设定']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17827:意图1` — 设定主驾座椅通风为最低挡

## 975. `KNOWN_CONTROL_CANDIDATE_819EC997C1_TURN_ON`

- MAC 对象: `椅坐垫`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_819EC997C1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11679:意图1` — 开一下后排座椅坐垫调节界面

## 976. `KNOWN_CONTROL_CANDIDATE_36E4A2A30C_TURN_ON`

- MAC 对象: `椅背屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_36E4A2A30C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5753:意图1` — 打开右后排椅背屏

## 977. `KNOWN_CONTROL_CANDIDATE_2D1B8D10EF_REVIEW`

- MAC 对象: `椅背屏左`
- MAC 对象功能: `息屏`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['更改成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_2D1B8D10EF + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5843:意图1` — 后排椅背屏左自动息屏为我时长更改成10分钟

## 978. `KNOWN_CONTROL_CANDIDATE_044786200C_SET`

- MAC 对象: `欢送灯`
- MAC 对象功能: `迎宾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_044786200C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:475:意图1` — 设置迎宾欢送灯
- `test_set.jsonl:583:意图1` — 设置迎宾欢送灯类型
- `train_set.jsonl:13092:意图1` — 我要设置迎宾欢送灯

## 979. `KNOWN_CONTROL_CANDIDATE_C22B2C3BB2_TURN_OFF`

- MAC 对象: `氛围氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_C22B2C3BB2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12109:意图1` — 关闭氛围氛围灯

## 980. `KNOWN_CONTROL_CANDIDATE_0CC0058858_SET`

- MAC 对象: `氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_0CC0058858 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1797:意图1` — 氛围灯调为

## 981. `KNOWN_CONTROL_CANDIDATE_0CC0058858_SET`

- MAC 对象: `氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_0CC0058858 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8448:意图1` — 设置氛围灯显示模式

## 982. `KNOWN_CONTROL_CANDIDATE_0CC0058858_SET`

- MAC 对象: `氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_0CC0058858 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19930:意图1` — 设置氛围灯样式

## 983. `KNOWN_CONTROL_CANDIDATE_0CC0058858_SET`

- MAC 对象: `氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_0CC0058858 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4404:意图1` — 氛围灯灯光暗一点

## 984. `KNOWN_CONTROL_CANDIDATE_0CC0058858_TURN_OFF`

- MAC 对象: `氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭', '设成关闭']`
- 唯一样本数: **8**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_0CC0058858 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19525:意图1` — 氛围灯音乐律动需要被关掉
- `test_set.jsonl:499:意图1` — 帮我把续航提醒氛围灯设成关闭
- `test_set.jsonl:575:意图1` — 续航提醒氛围灯赶紧让它给我熄灭
- `train_set.jsonl:10739:意图1` — 帮我设置一下来电提醒氛围灯调成关闭
- `train_set.jsonl:12399:意图1` — 氛围灯音乐律动太烦了给我关掉

## 985. `KNOWN_CONTROL_CANDIDATE_0CC0058858_TURN_ON`

- MAC 对象: `氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开一下', '开启', '打开']`
- 唯一样本数: **9**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_0CC0058858 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13351:意图1` — 打开来电氛围灯
- `train_set.jsonl:14132:意图1` — 打开来电提醒氛围灯
- `train_set.jsonl:1522:意图1` — 帮我将动态氛围灯开一下
- `train_set.jsonl:1553:意图1` — 调调来电提醒氛围灯的开关把它打开一下
- `train_set.jsonl:19117:意图1` — 打开续航里程警示氛围灯

## 986. `KNOWN_CONTROL_CANDIDATE_0CC0058858_REVIEW`

- MAC 对象: `氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['停掉', '需要']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_0CC0058858 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19824:意图2` — 所有氛围灯
- `test_set.jsonl:405:意图1` — 停掉氛围灯吧
- `train_set.jsonl:14067:意图1` — 后排需要氛围灯
- `train_set.jsonl:14212:意图1` — 前排右侧这里需要氛围灯

## 987. `KNOWN_CONTROL_CANDIDATE_1A19B5468C_SET`

- MAC 对象: `汽车`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_1A19B5468C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8082:意图1` — 设置汽车模式

## 988. `KNOWN_CONTROL_CANDIDATE_1A19B5468C_REVIEW`

- MAC 对象: `汽车`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['按']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_1A19B5468C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3151:意图1` — 让汽车按自定义模式运行吧

## 989. `KNOWN_CONTROL_CANDIDATE_185B8BEEC9_TURN_OFF`

- MAC 对象: `汽车头显`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_185B8BEEC9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16526:意图1` — 关闭汽车头显

## 990. `KNOWN_CONTROL_CANDIDATE_874437DE42_REVIEW`

- MAC 对象: `汽车由普通模式`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['变为']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_874437DE42 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5610:意图1` — 汽车由普通模式变为岩石模式
- `train_set.jsonl:8039:意图1` — 汽车由普通模式变为漂移模式

## 991. `KNOWN_CONTROL_CANDIDATE_6DE4E7A468_TURN_OFF`

- MAC 对象: `汽车电源`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_6DE4E7A468 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7699:意图1` — 关闭汽车电源

## 992. `KNOWN_CONTROL_CANDIDATE_A36034D418_SET`

- MAC 对象: `汽车运行`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A36034D418 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7050:意图1` — 设置汽车运行模式

## 993. `KNOWN_CONTROL_CANDIDATE_1D916F69EE_TURN_OFF`

- MAC 对象: `液晶大屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_1D916F69EE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4904:意图1` — 关闭液晶大屏

## 994. `KNOWN_CONTROL_CANDIDATE_68C2A57729_TURN_ON`

- MAC 对象: `液晶屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_68C2A57729 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:432:意图1` — 打开液晶屏

## 995. `KNOWN_CONTROL_CANDIDATE_65A32AADFA_TURN_OFF`

- MAC 对象: `滑门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_65A32AADFA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11556:意图2` — 关闭侧滑门

## 996. `KNOWN_CONTROL_CANDIDATE_65A32AADFA_TURN_ON`

- MAC 对象: `滑门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_65A32AADFA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10276:意图2` — 打开侧滑门
- `train_set.jsonl:11556:意图1` — 打开侧滑门

## 997. `KNOWN_CONTROL_CANDIDATE_2054EFADD8_TURN_OFF`

- MAC 对象: `激光雷达`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_2054EFADD8 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13933:意图1` — 关闭激光雷达

## 998. `KNOWN_CONTROL_CANDIDATE_28656D4702_SET`

- MAC 对象: `灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设为', '调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_28656D4702 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19523:意图1` — 灯的亮度调高三分之一
- `dev_set.jsonl:19571:意图1` — 把灯设为明亮模式

## 999. `KNOWN_CONTROL_CANDIDATE_28656D4702_SET`

- MAC 对象: `灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调成', '调节']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_28656D4702 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:362:意图1` — 替我把灯调成红色
- `train_set.jsonl:12823:意图1` — 灯调成白光
- `train_set.jsonl:4932:意图1` — 灯带给我调黄点
- `train_set.jsonl:6768:意图1` — 灯冷一点点

## 1000. `KNOWN_CONTROL_CANDIDATE_28656D4702_TURN_OFF`

- MAC 对象: `灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关了', '关掉', '关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_28656D4702 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17248:意图1` — 帮我把灯关了
- `train_set.jsonl:4854:意图1` — 你把灯关掉了
- `train_set.jsonl:6125:意图1` — 关闭车外动态迎宾灯页面

## 1001. `KNOWN_CONTROL_CANDIDATE_28656D4702_TURN_ON`

- MAC 对象: `灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_28656D4702 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10702:意图2` — 打开后面的灯
- `train_set.jsonl:15870:意图1` — 打开后排灯
- `train_set.jsonl:16577:意图1` — 所有的灯打开
- `train_set.jsonl:8905:意图2` — 打开全部灯

## 1002. `KNOWN_CONTROL_CANDIDATE_28656D4702_TURN_ON`

- MAC 对象: `灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_28656D4702 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8669:意图1` — 打开多色灯

## 1003. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_TURN_OFF`

- MAC 对象: `灯`
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11590:意图1` — 关闭外部充电呼吸灯

## 1004. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_TURN_ON`

- MAC 对象: `灯`
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2058:意图1` — 开启外部充电呼吸灯

## 1005. `KNOWN_CONTROL_CANDIDATE_43938C90A9_TURN_ON`

- MAC 对象: `灯`
- MAC 对象功能: `动态迎宾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_43938C90A9 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18820:意图1` — 打开车外动态迎宾灯

## 1006. `KNOWN_CONTROL_CANDIDATE_044786200C_TURN_ON`

- MAC 对象: `灯`
- MAC 对象功能: `迎宾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_044786200C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:244:意图1` — 打开迎宾灯

## 1007. `KNOWN_CONTROL_CANDIDATE_044786200C_REVIEW`

- MAC 对象: `灯`
- MAC 对象功能: `迎宾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['进行设定']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_044786200C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3503:意图1` — 对车外迎宾灯进行设定

## 1008. `KNOWN_CONTROL_CANDIDATE_3B579010A0_SET`

- MAC 对象: `灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3B579010A0 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14588:意图1` — 调节灯光

## 1009. `KNOWN_CONTROL_CANDIDATE_3B579010A0_SET`

- MAC 对象: `灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3B579010A0 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1780:意图1` — 灯光调亮一点

## 1010. `KNOWN_CONTROL_CANDIDATE_3B579010A0_TURN_OFF`

- MAC 对象: `灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **8**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3B579010A0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14136:意图1` — 关闭所有灯光
- `train_set.jsonl:2826:意图2` — 关闭灯光
- `train_set.jsonl:5828:意图1` — 关闭所有灯光
- `train_set.jsonl:6256:意图1` — 关闭灯光
- `train_set.jsonl:6310:意图2` — 关闭灯光

## 1011. `KNOWN_CONTROL_CANDIDATE_3B579010A0_TURN_OFF`

- MAC 对象: `灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_3B579010A0 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14979:意图1` — 关闭自动灯光

## 1012. `KNOWN_CONTROL_CANDIDATE_3B579010A0_TURN_ON`

- MAC 对象: `灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B579010A0 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10163:意图1` — 打开灯光
- `train_set.jsonl:5120:意图1` — 哪里可以设置灯光

## 1013. `KNOWN_CONTROL_CANDIDATE_3B579010A0_TURN_ON`

- MAC 对象: `灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B579010A0 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12605:意图1` — 打开智能灯光
- `train_set.jsonl:17666:意图1` — 把auto灯光打开

## 1014. `KNOWN_CONTROL_CANDIDATE_3B579010A0_REVIEW`

- MAC 对象: `灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['降低到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_3B579010A0 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13716:意图1` — 灯光色温降低到百分之零

## 1015. `KNOWN_CONTROL_CANDIDATE_BC5D20B5DD_TURN_ON`

- MAC 对象: `灯光同步`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BC5D20B5DD + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9287:意图1` — 打开灯光同步设置

## 1016. `KNOWN_CONTROL_CANDIDATE_360B1BC955_REVIEW`

- MAC 对象: `照地灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['进入']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_360B1BC955 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2295:意图1` — 进入照地灯视频界面

## 1017. `KNOWN_CONTROL_CANDIDATE_098294EECC_TURN_ON`

- MAC 对象: `照明`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_098294EECC + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8509:意图1` — 打开照明设置

## 1018. `KNOWN_CONTROL_CANDIDATE_98FD28DC2F_TURN_OFF`

- MAC 对象: `照明灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_98FD28DC2F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12663:意图2` — 关闭照明灯

## 1019. `KNOWN_CONTROL_CANDIDATE_98FD28DC2F_TURN_ON`

- MAC 对象: `照明灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_98FD28DC2F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18271:意图1` — 打开照明灯

## 1020. `KNOWN_CONTROL_CANDIDATE_1CF9F76E18_SET`

- MAC 对象: `玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_1CF9F76E18 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19880:意图2` — 关闭主驾玻璃
- `train_set.jsonl:17879:意图1` — 关闭前排玻璃

## 1021. `KNOWN_CONTROL_CANDIDATE_1CF9F76E18_TURN_OFF`

- MAC 对象: `玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_1CF9F76E18 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:597:意图2` — 关闭玻璃
- `train_set.jsonl:10832:意图1` — 关闭副驾驶的玻璃
- `train_set.jsonl:14410:意图1` — 关闭后排玻璃

## 1022. `KNOWN_CONTROL_CANDIDATE_1CF9F76E18_TURN_ON`

- MAC 对象: `玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **9**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_1CF9F76E18 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13272:意图2` — 打开主驾驶玻璃
- `train_set.jsonl:14427:意图2` — 打开车前车玻璃
- `train_set.jsonl:17372:意图2` — 打开前排玻璃
- `train_set.jsonl:3740:意图1` — 打开主驾玻璃
- `train_set.jsonl:5480:意图1` — 打开主副驾玻璃

## 1023. `KNOWN_CONTROL_CANDIDATE_1CF9F76E18_REVIEW`

- MAC 对象: `玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['降']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_1CF9F76E18 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10020:意图1` — 主驾副驾玻璃降到最高
- `train_set.jsonl:10020:意图2` — 升到最高
- `train_set.jsonl:16021:意图2` — 主副驾玻璃降到最低
- `train_set.jsonl:16021:意图3` — 打开驻车舒享主副驾玻璃降到最低

## 1024. `KNOWN_CONTROL_CANDIDATE_7457ABFE46_TURN_ON`

- MAC 对象: `玻璃窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7457ABFE46 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8008:意图1` — 打开前玻璃门全玻璃窗

## 1025. `KNOWN_CONTROL_CANDIDATE_5F578D0289_TURN_OFF`

- MAC 对象: `电动侧门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['停止关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_5F578D0289 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:655:意图1` — 停止关闭左后电动侧门

## 1026. `KNOWN_CONTROL_CANDIDATE_5F578D0289_REVIEW`

- MAC 对象: `电动侧门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['停止一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5F578D0289 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8569:意图1` — 把全部电动侧门停止一下

## 1027. `KNOWN_CONTROL_CANDIDATE_955BA18090_SET`

- MAC 对象: `电动出风口`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_955BA18090 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1401:意图1` — 设置电动出风口出风风向为吹腹

## 1028. `KNOWN_CONTROL_CANDIDATE_FE4184F2BA_TURN_OFF`

- MAC 对象: `电动尾翼`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_FE4184F2BA + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19463:意图1` — 关闭电动尾翼手动模式

## 1029. `KNOWN_CONTROL_CANDIDATE_FE4184F2BA_TURN_ON`

- MAC 对象: `电动尾翼`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_FE4184F2BA + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9771:意图1` — 打开电动尾翼手动模式

## 1030. `KNOWN_CONTROL_CANDIDATE_6E3B4816DB_TURN_OFF`

- MAC 对象: `电动尾翼`
- MAC 对象功能: `迎宾模式`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_6E3B4816DB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10566:意图1` — 电动尾翼迎宾模式关闭

## 1031. `KNOWN_CONTROL_CANDIDATE_BAF518C781_TURN_ON`

- MAC 对象: `电动滑门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BAF518C781 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12949:意图1` — 打开左侧电动滑门设置页面
- `train_set.jsonl:17419:意图1` — 打开左侧电动滑门控制页面

## 1032. `KNOWN_CONTROL_CANDIDATE_6283777231_TURN_OFF`

- MAC 对象: `电动遮阳帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_6283777231 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7821:意图1` — 关闭电动遮阳帘

## 1033. `KNOWN_CONTROL_CANDIDATE_6283777231_TURN_ON`

- MAC 对象: `电动遮阳帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_6283777231 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20136:意图1` — 打开电动遮阳帘四分之三

## 1034. `KNOWN_CONTROL_CANDIDATE_94A2F3D497_TURN_OFF`

- MAC 对象: `电动门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['停止关闭', '关上', '关闭']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_94A2F3D497 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19500:意图1` — 关闭右前电动门
- `train_set.jsonl:11252:意图1` — 停止关闭右后电动门
- `train_set.jsonl:12228:意图1` — 关上电动门
- `train_set.jsonl:13306:意图1` — 电动门关闭
- `train_set.jsonl:2161:意图1` — 关闭左后电动门

## 1035. `KNOWN_CONTROL_CANDIDATE_94A2F3D497_TURN_ON`

- MAC 对象: `电动门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_94A2F3D497 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10204:意图1` — 打开右前电动门
- `train_set.jsonl:3703:意图1` — 开启电动门

## 1036. `KNOWN_CONTROL_CANDIDATE_94A2F3D497_REVIEW`

- MAC 对象: `电动门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['转到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_94A2F3D497 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9520:意图1` — 转到电动门控制页面

## 1037. `KNOWN_CONTROL_CANDIDATE_2A649A441C_TURN_OFF`

- MAC 对象: `电子屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_2A649A441C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12997:意图1` — 关闭电子屏

## 1038. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `电椅`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12145:意图1` — 打开电椅加热

## 1039. `KNOWN_CONTROL_CANDIDATE_99FAF39F8D_TURN_OFF`

- MAC 对象: `电源`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_99FAF39F8D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13277:意图2` — 关掉电源
- `train_set.jsonl:1879:意图2` — 关闭电源
- `train_set.jsonl:2959:意图2` — 关闭电源
- `train_set.jsonl:3146:意图1` — 关闭电源
- `train_set.jsonl:7815:意图2` — 关闭电源

## 1040. `KNOWN_CONTROL_CANDIDATE_99FAF39F8D_TURN_ON`

- MAC 对象: `电源`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_99FAF39F8D + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8650:意图1` — 打开电源

## 1041. `KNOWN_CONTROL_CANDIDATE_33185CF73C_TURN_ON`

- MAC 对象: `电滑门`
- MAC 对象功能: `感应开启`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_33185CF73C + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15294:意图1` — 打开感应开启后排电滑门

## 1042. `KNOWN_CONTROL_CANDIDATE_A27A2248A5_TURN_ON`

- MAC 对象: `电视屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A27A2248A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2981:意图1` — 电视屏静音

## 1043. `KNOWN_CONTROL_CANDIDATE_A27A2248A5_REVIEW`

- MAC 对象: `电视屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['取消']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A27A2248A5 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:247:意图1` — 电视屏取消静音

## 1044. `KNOWN_CONTROL_CANDIDATE_9EDB3FBDD5_REVIEW`

- MAC 对象: `直流端盖`
- MAC 对象功能: `直流电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['掀起']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_9EDB3FBDD5 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18521:意图1` — 掀起直流端盖

## 1045. `KNOWN_CONTROL_CANDIDATE_DACF070260_TURN_ON`

- MAC 对象: `相机`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DACF070260 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17462:意图1` — 设置相机为开启状态

## 1046. `KNOWN_CONTROL_CANDIDATE_50A30D5234_TURN_OFF`

- MAC 对象: `示廓灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_50A30D5234 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11773:意图2` — 关闭示廓灯
- `train_set.jsonl:5221:意图2` — 关闭示廓灯
- `train_set.jsonl:6528:意图1` — 关闭示廓灯

## 1047. `KNOWN_CONTROL_CANDIDATE_50A30D5234_TURN_ON`

- MAC 对象: `示廓灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **39**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_50A30D5234 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19223:意图1` — 打开示廓灯
- `dev_set.jsonl:20058:意图3` — 打开示廓灯
- `dev_set.jsonl:20211:意图3` — 打开示廓灯
- `test_set.jsonl:114:意图2` — 打开示廓灯
- `test_set.jsonl:161:意图2` — 打开示廓灯

## 1048. `KNOWN_CONTROL_CANDIDATE_7D545E7FB0_TURN_OFF`

- MAC 对象: `礼貌灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_7D545E7FB0 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13960:意图1` — 找到自动礼貌灯的设置并关掉它
- `train_set.jsonl:14026:意图1` — 自动礼貌灯我不想让它开着
- `train_set.jsonl:8757:意图1` — 自动礼貌灯让它处于不可用状态

## 1049. `KNOWN_CONTROL_CANDIDATE_7D545E7FB0_TURN_ON`

- MAC 对象: `礼貌灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7D545E7FB0 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13888:意图1` — 调节自动礼貌灯的开关让它打开
- `train_set.jsonl:16417:意图1` — 让自动礼貌灯处于开启状态

## 1050. `KNOWN_CONTROL_CANDIDATE_7D545E7FB0_REVIEW`

- MAC 对象: `礼貌灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['弄灭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_7D545E7FB0 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11936:意图1` — 帮我把自动礼貌灯弄灭

## 1051. `KNOWN_CONTROL_CANDIDATE_2F8267A89A_SET`

- MAC 对象: `空`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调至']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_2F8267A89A + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4577:意图1` — 空空调调至二十四度

## 1052. `KNOWN_CONTROL_CANDIDATE_2F8267A89A_TURN_ON`

- MAC 对象: `空`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2F8267A89A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3254:意图1` — 开空空调

## 1053. `KNOWN_CONTROL_CANDIDATE_A30B714800_SET`

- MAC 对象: `空悬`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A30B714800 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19403:意图1` — 空悬调到最低

## 1054. `KNOWN_CONTROL_CANDIDATE_5AD1E6E0F1_SET`

- MAC 对象: `空气净化`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5AD1E6E0F1 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4518:意图1` — 帮我把空气净化调大些
- `train_set.jsonl:4909:意图1` — 我要空气净化调小
- `train_set.jsonl:8817:意图1` — 把空气净化调大些

## 1055. `KNOWN_CONTROL_CANDIDATE_5AD1E6E0F1_REVIEW`

- MAC 对象: `空气净化`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改个', '暂停']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5AD1E6E0F1 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:131:意图2` — 空气净化
- `train_set.jsonl:13542:意图1` — 暂停空气净化
- `train_set.jsonl:14589:意图2` — 主驾我要改个空气净化

## 1056. `KNOWN_CONTROL_CANDIDATE_C978875303_SET`

- MAC 对象: `空气净化器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为', '调', '调到', '调节']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C978875303 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19961:意图1` — 把空气净化器风速调低
- `train_set.jsonl:10781:意图1` — 把空气净化器风速降低点
- `train_set.jsonl:5808:意图1` — 空气净化器调到二十六度
- `train_set.jsonl:6478:意图1` — 空气净化器风速设置为低速
- `train_set.jsonl:8716:意图1` — 将空气净化器帮我调为中速

## 1057. `KNOWN_CONTROL_CANDIDATE_C978875303_SET`

- MAC 对象: `空气净化器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C978875303 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4976:意图1` — 将空气净化器温度调高一点

## 1058. `KNOWN_CONTROL_CANDIDATE_9F10FE658F_SET`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置', '调', '调到', '调取', '调整', '调节']`
- 唯一样本数: **98**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_9F10FE658F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19195:意图2` — 把空调调成二挡
- `dev_set.jsonl:19272:意图1` — 空调调到两挡
- `dev_set.jsonl:19897:意图1` — 调大空调
- `dev_set.jsonl:19986:意图1` — 空调调到一挡
- `dev_set.jsonl:20138:意图1` — 空调调整为一挡

## 1059. `KNOWN_CONTROL_CANDIDATE_9F10FE658F_SET`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_9F10FE658F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6805:意图1` — 空调气温20度

## 1060. `KNOWN_CONTROL_CANDIDATE_9F10FE658F_SET`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_9F10FE658F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20391:意图2` — 空调温度去

## 1061. `KNOWN_CONTROL_CANDIDATE_9F10FE658F_SET`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调节']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_9F10FE658F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:548:意图2` — 空调风挡调二挡
- `train_set.jsonl:10653:意图3` — 关闭后挡风玻璃加热打开制冷空调风挡调到一挡
- `train_set.jsonl:15240:意图1` — 空调风挡调到二挡
- `train_set.jsonl:4084:意图1` — 空调风挡加大两挡

## 1062. `KNOWN_CONTROL_CANDIDATE_9F10FE658F_TURN_OFF`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关', '关上', '关下', '关了', '关掉', '关闭']`
- 唯一样本数: **63**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_9F10FE658F + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19167:意图1` — 我想空调自然风关页面
- `dev_set.jsonl:19716:意图1` — 给我空调自然风关上
- `dev_set.jsonl:20012:意图1` — 给我关上空调自然风设置页面
- `dev_set.jsonl:20020:意图1` — 关闭空调自然风页面
- `dev_set.jsonl:20399:意图1` — 我要关下空调自然风设置页面

## 1063. `KNOWN_CONTROL_CANDIDATE_9F10FE658F_TURN_ON`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_9F10FE658F + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2040:意图1` — 空调启动出风口

## 1064. `KNOWN_CONTROL_CANDIDATE_9F10FE658F_TURN_ON`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '开启', '开开', '打开']`
- 唯一样本数: **70**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_9F10FE658F + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19157:意图1` — 打开空调ac
- `dev_set.jsonl:19381:意图1` — 开启空调自动模式
- `dev_set.jsonl:19389:意图1` — 打开空调自动循环
- `dev_set.jsonl:19471:意图1` — 打开空调制冷
- `dev_set.jsonl:19596:意图3` — 打开空调内循环

## 1065. `KNOWN_CONTROL_CANDIDATE_9F10FE658F_REVIEW`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关个', '变', '开到', '放', '查看', '退出']`
- 唯一样本数: **7**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_9F10FE658F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:224:意图1` — 现在副驾空调风温度是多少
- `train_set.jsonl:10555:意图1` — 空调放到最低
- `train_set.jsonl:13763:意图1` — 前排空调变成三挡
- `train_set.jsonl:1647:意图1` — 给我关个空调
- `train_set.jsonl:3006:意图1` — 退出空调

## 1066. `KNOWN_CONTROL_CANDIDATE_9F10FE658F_REVIEW`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_9F10FE658F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19897:意图2` — 空调风量
- `train_set.jsonl:8100:意图2` — 空调风量

## 1067. `KNOWN_CONTROL_CANDIDATE_3732E264DF_REVIEW`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: `温度`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_3732E264DF + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20102:意图1` — 我要查看主驾空调温度
- `train_set.jsonl:11178:意图1` — 当前空调温度是多少
- `train_set.jsonl:2656:意图1` — 我要查看空调温度

## 1068. `KNOWN_CONTROL_CANDIDATE_839EA2AFBE_REVIEW`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: `风速`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_839EA2AFBE + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4178:意图1` — 查一下空调的风速

## 1069. `KNOWN_CONTROL_CANDIDATE_9C34DAE3E0_REVIEW`

- MAC 对象: `空调`
- MAC 对象功能: ``
- MAC 功能: `风量`
- MAC 子功能: ``
- MAC 操作: `['查看']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_9C34DAE3E0 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2914:意图1` — 查询下空调的风量是多大
- `train_set.jsonl:9572:意图1` — 现在空调主驾风量有多大

## 1070. `KNOWN_CONTROL_CANDIDATE_DF544E46AA_TURN_ON`

- MAC 对象: `空调`
- MAC 对象功能: `平衡`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DF544E46AA + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12566:意图1` — 打开空调平衡模式

## 1071. `KNOWN_CONTROL_CANDIDATE_2E7A5C16E7_TURN_ON`

- MAC 对象: `空调`
- MAC 对象功能: `换气`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2E7A5C16E7 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18193:意图1` — 打开空调自动换气

## 1072. `KNOWN_CONTROL_CANDIDATE_5070F6DCC9_SET`

- MAC 对象: `空调`
- MAC 对象功能: `通风模`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5070F6DCC9 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6470:意图1` — 空调调到通风模式

## 1073. `KNOWN_CONTROL_CANDIDATE_D889320F07_TURN_ON`

- MAC 对象: `空调`
- MAC 对象功能: `除雾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_D889320F07 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:206:意图1` — 空调开启智能自动除雾
- `train_set.jsonl:16415:意图1` — 空调开启智能除雾

## 1074. `KNOWN_CONTROL_CANDIDATE_677BC47BDC_REVIEW`

- MAC 对象: `空调`
- MAC 对象功能: `除霜`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['换个']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_677BC47BDC + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13860:意图2` — 换个空调吹脚除霜试试

## 1075. `KNOWN_CONTROL_CANDIDATE_7AB12F4342_SET`

- MAC 对象: `空调调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7AB12F4342 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2793:意图2` — 空调调温度调到最低

## 1076. `KNOWN_CONTROL_CANDIDATE_17A4837EF3_SET`

- MAC 对象: `空调香氛`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_17A4837EF3 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9924:意图1` — 切换空调香氛

## 1077. `KNOWN_CONTROL_CANDIDATE_A10722C9C1_SET`

- MAC 对象: `窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A10722C9C1 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9357:意图1` — 零透明度后窗

## 1078. `KNOWN_CONTROL_CANDIDATE_A10722C9C1_SET`

- MAC 对象: `窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A10722C9C1 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:840:意图1` — 一半不透明度后窗

## 1079. `KNOWN_CONTROL_CANDIDATE_A10722C9C1_ADJUST`

- MAC 对象: `窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['升起']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_A10722C9C1 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13918:意图1` — 升起主驾驶窗

## 1080. `KNOWN_CONTROL_CANDIDATE_A10722C9C1_TURN_OFF`

- MAC 对象: `窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_A10722C9C1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13457:意图2` — 关闭驾驶窗
- `train_set.jsonl:4190:意图2` — 关闭后窗

## 1081. `KNOWN_CONTROL_CANDIDATE_A10722C9C1_TURN_ON`

- MAC 对象: `窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A10722C9C1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11994:意图1` — 打开左前窗
- `train_set.jsonl:11994:意图2` — 打开右后窗
- `train_set.jsonl:5561:意图2` — 打开前排窗

## 1082. `KNOWN_CONTROL_CANDIDATE_A10722C9C1_TURN_ON`

- MAC 对象: `窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A10722C9C1 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20495:意图2` — 后窗开一点
- `train_set.jsonl:1978:意图3` — 主驾窗打开百分之三十

## 1083. `KNOWN_CONTROL_CANDIDATE_A10722C9C1_TURN_ON`

- MAC 对象: `窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A10722C9C1 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5877:意图1` — 可以帮我把后窗开到全不透明吗

## 1084. `KNOWN_CONTROL_CANDIDATE_955C13441A_TURN_ON`

- MAC 对象: `窗`
- MAC 对象功能: `透气`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_955C13441A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8003:意图1` — 开窗透气

## 1085. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `窗`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:111:意图1` — 开窗通风

## 1086. `KNOWN_CONTROL_CANDIDATE_08230BA24F_TURN_OFF`

- MAC 对象: `窗子`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_08230BA24F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11051:意图1` — 关闭所有窗子
- `train_set.jsonl:17599:意图1` — 关闭窗子

## 1087. `KNOWN_CONTROL_CANDIDATE_08230BA24F_TURN_ON`

- MAC 对象: `窗子`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_08230BA24F + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8626:意图1` — 每扇窗子都开条缝

## 1088. `KNOWN_CONTROL_CANDIDATE_08230BA24F_REVIEW`

- MAC 对象: `窗子`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['降到下面去']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_08230BA24F + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8677:意图1` — 左前窗子降到下面去

## 1089. `KNOWN_CONTROL_CANDIDATE_08230BA24F_REVIEW`

- MAC 对象: `窗子`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['敞开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_08230BA24F + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:820:意图1` — 主驾窗子敞开百分之六十

## 1090. `KNOWN_CONTROL_CANDIDATE_12BF47489E_SET`

- MAC 对象: `窗帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调', '调整', '调节']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_12BF47489E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13898:意图1` — 窗帘位置到三分之一
- `train_set.jsonl:13982:意图1` — 所有窗帘调到半开
- `train_set.jsonl:17108:意图1` — 窗帘调整到半开

## 1091. `KNOWN_CONTROL_CANDIDATE_12BF47489E_ADJUST`

- MAC 对象: `窗帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['收回']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_12BF47489E + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14002:意图1` — 左侧窗帘收回

## 1092. `KNOWN_CONTROL_CANDIDATE_12BF47489E_TURN_OFF`

- MAC 对象: `窗帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关', '关一下']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_12BF47489E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16047:意图1` — 关窗帘
- `train_set.jsonl:7260:意图1` — 窗帘关一下

## 1093. `KNOWN_CONTROL_CANDIDATE_12BF47489E_TURN_OFF`

- MAC 对象: `窗帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关', '关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_12BF47489E + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:932:意图1` — 给我把窗帘合上
- `train_set.jsonl:3790:意图1` — 窗帘关闭到百分之十
- `train_set.jsonl:7471:意图1` — 所有窗帘给我关百分之三十

## 1094. `KNOWN_CONTROL_CANDIDATE_12BF47489E_TURN_ON`

- MAC 对象: `窗帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开一下', '开开', '打开']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_12BF47489E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:670:意图1` — 把窗帘给我开开
- `train_set.jsonl:12001:意图1` — 全部打开窗帘
- `train_set.jsonl:13671:意图1` — 把窗帘开一下
- `train_set.jsonl:9329:意图1` — 我要把窗帘打开

## 1095. `KNOWN_CONTROL_CANDIDATE_12BF47489E_TURN_ON`

- MAC 对象: `窗帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_12BF47489E + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11564:意图1` — 窗帘打开到百分之三十
- `train_set.jsonl:17214:意图1` — 窗帘打开一半了吗

## 1096. `KNOWN_CONTROL_CANDIDATE_12BF47489E_REVIEW`

- MAC 对象: `窗帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['拉上', '拉开', '暂停']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_12BF47489E + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10481:意图1` — 窗帘全拉上
- `train_set.jsonl:11332:意图1` — 暂停窗帘
- `train_set.jsonl:7056:意图1` — 我想拉上窗帘
- `train_set.jsonl:9874:意图1` — 我要把窗帘拉开

## 1097. `KNOWN_CONTROL_CANDIDATE_DA098A2250_SET`

- MAC 对象: `窗户`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **9**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_DA098A2250 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20015:意图1` — 后排座位的窗户开个小缝
- `train_set.jsonl:12023:意图1` — 关闭主驾驶窗户
- `train_set.jsonl:12317:意图1` — 打开更多窗户
- `train_set.jsonl:13718:意图3` — 关闭前排窗户
- `train_set.jsonl:14762:意图2` — 后排窗户二分之一

## 1098. `KNOWN_CONTROL_CANDIDATE_DA098A2250_TURN_OFF`

- MAC 对象: `窗户`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关上', '关了', '关闭']`
- 唯一样本数: **46**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_DA098A2250 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19568:意图1` — 关闭窗户
- `dev_set.jsonl:19568:意图2` — 关闭所有窗户
- `dev_set.jsonl:19619:意图3` — 关闭后排窗户
- `test_set.jsonl:1047:意图1` — 关闭窗户
- `test_set.jsonl:1073:意图2` — 关闭窗户

## 1099. `KNOWN_CONTROL_CANDIDATE_DA098A2250_TURN_OFF`

- MAC 对象: `窗户`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_DA098A2250 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15734:意图1` — 把一排右的窗户给我封上

## 1100. `KNOWN_CONTROL_CANDIDATE_DA098A2250_TURN_ON`

- MAC 对象: `窗户`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '开一下', '开开', '打开']`
- 唯一样本数: **61**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DA098A2250 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19223:意图2` — 打开前排窗户
- `dev_set.jsonl:19376:意图2` — 打开所有窗户
- `dev_set.jsonl:19465:意图2` — 打开窗户
- `dev_set.jsonl:19619:意图4` — 打开前排窗户
- `dev_set.jsonl:19725:意图2` — 风速调到三挡

## 1101. `KNOWN_CONTROL_CANDIDATE_DA098A2250_TURN_ON`

- MAC 对象: `窗户`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '打开']`
- 唯一样本数: **10**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DA098A2250 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20484:意图1` — 打开窗户百分之二三十
- `test_set.jsonl:893:意图1` — 前排窗户打开百分之五十
- `train_set.jsonl:14762:意图1` — 打开前排窗户三分之一
- `train_set.jsonl:16422:意图1` — 所有窗户微开
- `train_set.jsonl:18956:意图2` — 打开后排左侧窗户四分之一

## 1102. `KNOWN_CONTROL_CANDIDATE_DA098A2250_REVIEW`

- MAC 对象: `窗户`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['下来', '关起来', '开下', '开个', '落下来', '降下来']`
- 唯一样本数: **7**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_DA098A2250 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19613:意图1` — 请给我开个窗户
- `train_set.jsonl:13959:意图1` — 把窗户关起来
- `train_set.jsonl:2479:意图1` — 把窗户全落下来
- `train_set.jsonl:2479:意图2` — 把窗户全部下来
- `train_set.jsonl:3087:意图1` — 全部的窗户都降下来

## 1103. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_OFF`

- MAC 对象: `窗户`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关上']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13575:意图1` — 关上窗户通风模式

## 1104. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `窗户`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10029:意图2` — 打开窗户通风
- `train_set.jsonl:10394:意图1` — 我要开启窗户通风模式
- `train_set.jsonl:17027:意图2` — 打开窗户通风

## 1105. `KNOWN_CONTROL_CANDIDATE_2D56864E08_TURN_OFF`

- MAC 对象: `窗户玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_2D56864E08 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1020:意图1` — 把左前面窗户玻璃关严实

## 1106. `KNOWN_CONTROL_CANDIDATE_D0B55352CA_TURN_ON`

- MAC 对象: `窗玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_D0B55352CA + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13364:意图1` — 打开前窗玻璃

## 1107. `KNOWN_CONTROL_CANDIDATE_0F18C4B40F_TURN_OFF`

- MAC 对象: `窗窗帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_0F18C4B40F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7406:意图2` — 关闭窗窗帘

## 1108. `KNOWN_CONTROL_CANDIDATE_5B50D7C4B5_SET`

- MAC 对象: `系统`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5B50D7C4B5 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9864:意图1` — 系统调到黑色模式

## 1109. `KNOWN_CONTROL_CANDIDATE_55C3EE1021_SET`

- MAC 对象: `线条灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_55C3EE1021 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:381:意图1` — 线条灯亮度调为稍暗
- `train_set.jsonl:13314:意图1` — 线条灯的亮度到最亮
- `train_set.jsonl:15015:意图1` — 线条灯亮度设定为较低
- `train_set.jsonl:16457:意图1` — 把线条灯亮度设为较亮

## 1110. `KNOWN_CONTROL_CANDIDATE_55C3EE1021_SET`

- MAC 对象: `线条灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_55C3EE1021 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15562:意图1` — 线条灯设置成亮蓝色

## 1111. `KNOWN_CONTROL_CANDIDATE_4B834145B2_SET`

- MAC 对象: `背部`
- MAC 对象功能: `按摩`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换', '切换为']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4B834145B2 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19627:意图1` — 副驾背部按摩切换为脊柱舒展模式
- `train_set.jsonl:17060:意图1` — 背部按摩切换为全背舒缓模式
- `train_set.jsonl:3036:意图1` — 主驾背部按摩切换为背部舒展模式

## 1112. `KNOWN_CONTROL_CANDIDATE_37FD4B6D10_SET`

- MAC 对象: `脚托`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_37FD4B6D10 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3490:意图1` — 脚托往下到底

## 1113. `KNOWN_CONTROL_CANDIDATE_AFD4B78353_REVIEW`

- MAC 对象: `脚托`
- MAC 对象功能: `收起`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['收起']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_AFD4B78353 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18440:意图1` — 座椅主驾脚托收起

## 1114. `KNOWN_CONTROL_CANDIDATE_6F24351D9F_TURN_ON`

- MAC 对象: `脚托`
- MAC 对象功能: `联动`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_6F24351D9F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7891:意图1` — 打开二排右侧脚托联动调节

## 1115. `KNOWN_CONTROL_CANDIDATE_40DB2392C4_SET`

- MAC 对象: `脚踏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调整']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_40DB2392C4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5220:意图1` — 调整脚踏到最高

## 1116. `KNOWN_CONTROL_CANDIDATE_40DB2392C4_SET`

- MAC 对象: `脚踏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_40DB2392C4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1854:意图1` — 主驾脚踏向高调节

## 1117. `KNOWN_CONTROL_CANDIDATE_3B821DA938_SET`

- MAC 对象: `脚踏`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节', '调高']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:915:意图1` — 主驾脚踏加热调高一档
- `train_set.jsonl:3248:意图1` — 调高脚踏加热

## 1118. `KNOWN_CONTROL_CANDIDATE_F5FE1B6895_SET`

- MAC 对象: `腰架`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_F5FE1B6895 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12290:意图1` — 腰架往前调一点

## 1119. `KNOWN_CONTROL_CANDIDATE_88EFC62121_SET`

- MAC 对象: `腰靠`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_88EFC62121 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12676:意图1` — 腰靠向下来一点
- `train_set.jsonl:15094:意图1` — 主驾腰靠向下起来一点

## 1120. `KNOWN_CONTROL_CANDIDATE_E91224A7E1_SET`

- MAC 对象: `腿托`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E91224A7E1 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2205:意图1` — 主驾腿托包裹松一点

## 1121. `KNOWN_CONTROL_CANDIDATE_E91224A7E1_SET`

- MAC 对象: `腿托`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调一点', '调节']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E91224A7E1 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11007:意图1` — 腿托往下调一点
- `train_set.jsonl:12031:意图1` — 主驾腿托往前调一点
- `train_set.jsonl:12850:意图1` — 副驾调整腿托至百分之五十
- `train_set.jsonl:13672:意图1` — 腿托高点更好
- `train_set.jsonl:14289:意图1` — 往上调一点腿托

## 1122. `KNOWN_CONTROL_CANDIDATE_E91224A7E1_SET`

- MAC 对象: `腿托`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_E91224A7E1 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2348:意图1` — 主驾腿托不够高

## 1123. `KNOWN_CONTROL_CANDIDATE_E91224A7E1_ADJUST`

- MAC 对象: `腿托`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['移']`
- 唯一样本数: **6**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `ADJUST + KNOWN_CONTROL_CANDIDATE_E91224A7E1 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:90:意图1` — 腿托上移
- `train_set.jsonl:15556:意图1` — 前排腿托下移
- `train_set.jsonl:1834:意图1` — 副驾腿托上移
- `train_set.jsonl:2208:意图1` — 主驾腿托前移
- `train_set.jsonl:3918:意图1` — 主驾腿托后移

## 1124. `KNOWN_CONTROL_CANDIDATE_A3BF8BAAA4_SET`

- MAC 对象: `腿托`
- MAC 对象功能: `伸长`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A3BF8BAAA4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18067:意图1` — 腿托伸长

## 1125. `KNOWN_CONTROL_CANDIDATE_2895115ABD_SET`

- MAC 对象: `腿托`
- MAC 对象功能: `延长`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_2895115ABD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17691:意图1` — 主驾腿托延长调到最长
- `train_set.jsonl:9582:意图1` — 腿托延长调到最长

## 1126. `KNOWN_CONTROL_CANDIDATE_84A07F292F_TURN_ON`

- MAC 对象: `腿托`
- MAC 对象功能: `折叠`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_84A07F292F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6258:意图1` — 腿托收起

## 1127. `KNOWN_CONTROL_CANDIDATE_FBACDEDA07_SET`

- MAC 对象: `腿架`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调一点']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_FBACDEDA07 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10947:意图1` — 主驾腿架往上调一点

## 1128. `KNOWN_CONTROL_CANDIDATE_A541CDB4C5_TURN_ON`

- MAC 对象: `自动礼仪灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A541CDB4C5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2686:意图1` — 打开自动礼仪灯

## 1129. `KNOWN_CONTROL_CANDIDATE_90315D59F3_SET`

- MAC 对象: `荧幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_90315D59F3 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1584:意图1` — 副驾驶荧幕最亮
- `train_set.jsonl:2368:意图1` — 调亮荧幕

## 1130. `KNOWN_CONTROL_CANDIDATE_90315D59F3_SET`

- MAC 对象: `荧幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_90315D59F3 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16611:意图1` — 荧幕调到日间模式

## 1131. `KNOWN_CONTROL_CANDIDATE_96879DD510_TURN_OFF`

- MAC 对象: `蒸发器`
- MAC 对象功能: `自干燥`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关一下', '关闭一下下']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_96879DD510 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19294:意图1` — 我要把蒸发器自干燥关闭一下下
- `train_set.jsonl:5252:意图1` — 帮我关一下蒸发器自干燥

## 1132. `KNOWN_CONTROL_CANDIDATE_3817285CDE_SET`

- MAC 对象: `蓝牙耳机`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3817285CDE + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19244:意图1` — 我需要最大的蓝牙声音
- `train_set.jsonl:4609:意图1` — 我想要最大的蓝牙声音

## 1133. `KNOWN_CONTROL_CANDIDATE_3817285CDE_SET`

- MAC 对象: `蓝牙耳机`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3817285CDE + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12482:意图1` — 声音输出设置为蓝牙耳机

## 1134. `KNOWN_CONTROL_CANDIDATE_E3420F2548_TURN_OFF`

- MAC 对象: `蓝牙钥匙`
- MAC 对象功能: `离车自动落锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_E3420F2548 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6659:意图1` — 关闭蓝牙钥匙离车自动落锁

## 1135. `KNOWN_CONTROL_CANDIDATE_4BDA402BD5_TURN_ON`

- MAC 对象: `行李箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4BDA402BD5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:523:意图1` — 打开行李箱

## 1136. `KNOWN_CONTROL_CANDIDATE_7AF2587B6A_TURN_OFF`

- MAC 对象: `行车灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_7AF2587B6A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6059:意图1` — 关闭行车灯

## 1137. `KNOWN_CONTROL_CANDIDATE_7AF2587B6A_TURN_ON`

- MAC 对象: `行车灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7AF2587B6A + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10587:意图1` — 开启行车灯
- `train_set.jsonl:12374:意图1` — 打开行车灯
- `train_set.jsonl:5327:意图1` — 打开行车灯

## 1138. `KNOWN_CONTROL_CANDIDATE_4F99146E0A_REVIEW`

- MAC 对象: `行车记录仪`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['看一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_4F99146E0A + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19894:意图1` — 帮我看一下行车记录仪最近一周

## 1139. `KNOWN_CONTROL_CANDIDATE_ADDA3A81C1_REVIEW`

- MAC 对象: `行驶灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['亮起']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_ADDA3A81C1 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17105:意图1` — 行驶灯的灯光亮起来帮我照明

## 1140. `KNOWN_CONTROL_CANDIDATE_5A8157DFDB_SET`

- MAC 对象: `表面灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调成', '调节']`
- 唯一样本数: **8**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A8157DFDB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11441:意图1` — 稍微亮的表面灯
- `train_set.jsonl:15597:意图1` — 调节表面灯亮度
- `train_set.jsonl:18112:意图1` — 表面灯亮度调到较亮
- `train_set.jsonl:19134:意图1` — 表面灯的亮度太低了为我调亮点
- `train_set.jsonl:1992:意图1` — 稍暗的表面灯

## 1141. `KNOWN_CONTROL_CANDIDATE_5A8157DFDB_SET`

- MAC 对象: `表面灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调成其他']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A8157DFDB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13859:意图1` — 将表面灯颜色调成其他

## 1142. `KNOWN_CONTROL_CANDIDATE_8B3204295E_SET`

- MAC 对象: `装饰灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_8B3204295E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20232:意图1` — 调低装饰灯的亮度
- `train_set.jsonl:1781:意图1` — 调高装饰灯的亮度

## 1143. `KNOWN_CONTROL_CANDIDATE_98A36CEE27_TURN_ON`

- MAC 对象: `警示灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_98A36CEE27 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16089:意图1` — 打开警示灯

## 1144. `KNOWN_CONTROL_CANDIDATE_3DAA593FC1_TURN_ON`

- MAC 对象: `记录仪`
- MAC 对象功能: ``
- MAC 功能: `全景`
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3DAA593FC1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:290:意图1` — 打开全景记录仪

## 1145. `KNOWN_CONTROL_CANDIDATE_DF3D58C7D8_SET`

- MAC 对象: `设置`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置一下']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_DF3D58C7D8 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12028:意图1` — 设置一下车内灯可以吗
- `train_set.jsonl:8250:意图1` — 设置一下车内灯

## 1146. `KNOWN_CONTROL_CANDIDATE_A3CA3CC03D_SET`

- MAC 对象: `话筒`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_A3CA3CC03D + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1732:意图1` — 请你把话筒的声音调大一点
- `train_set.jsonl:3488:意图1` — 话筒声音小一点

## 1147. `KNOWN_CONTROL_CANDIDATE_F65C42A254_SET`

- MAC 对象: `调整`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调整']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_F65C42A254 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19628:意图1` — 调整表面灯的亮度为略暗
- `train_set.jsonl:2060:意图1` — 调整线条灯的亮度为略暗

## 1148. `KNOWN_CONTROL_CANDIDATE_EAEED75337_REVIEW`

- MAC 对象: `踏板加速`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['换成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_EAEED75337 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16050:意图1` — 把踏板加速换成标准

## 1149. `KNOWN_CONTROL_CANDIDATE_605FF193FF_TURN_OFF`

- MAC 对象: `车上窗户`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关', '关上', '关闭']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_605FF193FF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:1112:意图1` — 把车上窗户关上
- `train_set.jsonl:10413:意图1` — 关车上窗户
- `train_set.jsonl:3641:意图1` — 把车上窗户全都关闭

## 1150. `KNOWN_CONTROL_CANDIDATE_605FF193FF_TURN_ON`

- MAC 对象: `车上窗户`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '开开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_605FF193FF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:562:意图1` — 开车上窗户
- `train_set.jsonl:1398:意图1` — 开开车上窗户

## 1151. `KNOWN_CONTROL_CANDIDATE_605FF193FF_REVIEW`

- MAC 对象: `车上窗户`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关起来', '降下', '降下去']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_605FF193FF + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19618:意图1` — 降下车上窗户
- `train_set.jsonl:18369:意图1` — 把车上窗户全都降下去
- `train_set.jsonl:18742:意图1` — 把车上窗户全部都关起来

## 1152. `KNOWN_CONTROL_CANDIDATE_E73607A401_TURN_ON`

- MAC 对象: `车内所有灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_E73607A401 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3258:意图1` — 打开车内所有灯光

## 1153. `KNOWN_CONTROL_CANDIDATE_9A33E51630_REVIEW`

- MAC 对象: `车内氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_9A33E51630 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:44:意图1` — 请帮我把车内氛围灯颜色设成玫红色

## 1154. `KNOWN_CONTROL_CANDIDATE_7061E4C231_SET`

- MAC 对象: `车内灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7061E4C231 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1160:意图1` — 设置车内灯

## 1155. `KNOWN_CONTROL_CANDIDATE_7061E4C231_SET`

- MAC 对象: `车内灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7061E4C231 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11547:意图1` — 心跳氛围灯速度切为中

## 1156. `KNOWN_CONTROL_CANDIDATE_7061E4C231_TURN_ON`

- MAC 对象: `车内灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7061E4C231 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6560:意图1` — 在我开门的时候请关闭阅读灯

## 1157. `KNOWN_CONTROL_CANDIDATE_F7F771DF20_SET`

- MAC 对象: `车内灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_F7F771DF20 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15804:意图1` — 设置车内灯光

## 1158. `KNOWN_CONTROL_CANDIDATE_F7F771DF20_TURN_OFF`

- MAC 对象: `车内灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_F7F771DF20 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9061:意图1` — 关闭后排车内灯光

## 1159. `KNOWN_CONTROL_CANDIDATE_F7F771DF20_TURN_ON`

- MAC 对象: `车内灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_F7F771DF20 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:440:意图1` — 帮我打开车内灯光页面

## 1160. `KNOWN_CONTROL_CANDIDATE_5AA92F2798_TURN_OFF`

- MAC 对象: `车内照明`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_5AA92F2798 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8599:意图1` — 关闭车内照明

## 1161. `KNOWN_CONTROL_CANDIDATE_5AA92F2798_TURN_ON`

- MAC 对象: `车内照明`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5AA92F2798 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19543:意图1` — 打开车内照明

## 1162. `KNOWN_CONTROL_CANDIDATE_5AA92F2798_REVIEW`

- MAC 对象: `车内照明`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5AA92F2798 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6031:意图1` — 把车内照明改成

## 1163. `KNOWN_CONTROL_CANDIDATE_AD411A34F7_SET`

- MAC 对象: `车外灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_AD411A34F7 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18081:意图1` — 设置车外灯

## 1164. `KNOWN_CONTROL_CANDIDATE_AD411A34F7_SET`

- MAC 对象: `车外灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_AD411A34F7 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:859:意图1` — 把车外灯调节为自动模式

## 1165. `KNOWN_CONTROL_CANDIDATE_AD411A34F7_TURN_OFF`

- MAC 对象: `车外灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **7**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_AD411A34F7 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19202:意图1` — 关闭车外灯光
- `train_set.jsonl:10203:意图1` — 关闭车外灯光
- `train_set.jsonl:13920:意图1` — 关闭车外灯光
- `train_set.jsonl:15336:意图1` — 关闭车外灯
- `train_set.jsonl:3926:意图1` — 关闭车外灯光

## 1166. `KNOWN_CONTROL_CANDIDATE_AD411A34F7_TURN_ON`

- MAC 对象: `车外灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开一下', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_AD411A34F7 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15245:意图1` — 我要打开车外灯
- `train_set.jsonl:17499:意图1` — 打开外灯
- `train_set.jsonl:18575:意图1` — 我暂时需要停车所以双跳灯开一下

## 1167. `KNOWN_CONTROL_CANDIDATE_AD411A34F7_TURN_ON`

- MAC 对象: `车外灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_AD411A34F7 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4304:意图1` — 打开外循环灯

## 1168. `KNOWN_CONTROL_CANDIDATE_AD411A34F7_REVIEW`

- MAC 对象: `车外灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['不需要', '运行']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_AD411A34F7 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11295:意图1` — 双跳灯我现在不需要这个灯光了
- `train_set.jsonl:18608:意图1` — 开始运行双跳灯功能

## 1169. `KNOWN_CONTROL_CANDIDATE_A5E408EAEE_TURN_ON`

- MAC 对象: `车外灯`
- MAC 对象功能: `充电`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A5E408EAEE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4310:意图1` — 打开充电灯

## 1170. `KNOWN_CONTROL_CANDIDATE_044786200C_SET`

- MAC 对象: `车外灯`
- MAC 对象功能: `迎宾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_044786200C + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15171:意图1` — 把迎宾灯改一改它太丑了
- `train_set.jsonl:2386:意图1` — 我需要改一改迎宾欢送灯
- `train_set.jsonl:9213:意图1` — 换一种迎宾灯类型

## 1171. `KNOWN_CONTROL_CANDIDATE_26A1D7D100_TURN_ON`

- MAC 对象: `车外灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_26A1D7D100 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10964:意图1` — 帮我打开车外灯光界面

## 1172. `KNOWN_CONTROL_CANDIDATE_D6BB6743A7_REVIEW`

- MAC 对象: `车机屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['转向']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_D6BB6743A7 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:399:意图1` — 车机屏幕转向中间

## 1173. `KNOWN_CONTROL_CANDIDATE_65CA9C80AF_SET`

- MAC 对象: `车灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_65CA9C80AF + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13958:意图1` — 车灯调高一点
- `train_set.jsonl:7155:意图1` — 车灯调低

## 1174. `KNOWN_CONTROL_CANDIDATE_65CA9C80AF_TURN_OFF`

- MAC 对象: `车灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **24**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_65CA9C80AF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19539:意图2` — 关闭车灯
- `test_set.jsonl:121:意图2` — 关闭所有车灯
- `test_set.jsonl:689:意图1` — 关闭车灯
- `test_set.jsonl:707:意图1` — 关闭车灯
- `train_set.jsonl:10506:意图1` — 关闭车灯

## 1175. `KNOWN_CONTROL_CANDIDATE_65CA9C80AF_TURN_OFF`

- MAC 对象: `车灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_65CA9C80AF + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3702:意图1` — 请求灯光主动迎宾关掉

## 1176. `KNOWN_CONTROL_CANDIDATE_65CA9C80AF_TURN_ON`

- MAC 对象: `车灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_65CA9C80AF + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14427:意图1` — 打开车灯
- `train_set.jsonl:3666:意图1` — 打开前车灯
- `train_set.jsonl:8760:意图1` — 打开车灯

## 1177. `KNOWN_CONTROL_CANDIDATE_044786200C_TURN_ON`

- MAC 对象: `车灯`
- MAC 对象功能: `迎宾`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_044786200C + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18903:意图1` — 打开车外动态迎宾灯呼吸模式

## 1178. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `车窗`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **8**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11078:意图1` — 打开车窗通风
- `train_set.jsonl:14481:意图2` — 打开车窗通风
- `train_set.jsonl:5274:意图1` — 车窗透气一下
- `train_set.jsonl:6076:意图2` — 打开车窗通风
- `train_set.jsonl:6249:意图2` — 打开车窗通风

## 1179. `KNOWN_CONTROL_CANDIDATE_9D8499BA0E_SET`

- MAC 对象: `车身`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调整', '调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_9D8499BA0E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19241:意图1` — 调整为较低的车身高度
- `train_set.jsonl:15151:意图1` — 将车身高度降低

## 1180. `KNOWN_CONTROL_CANDIDATE_9D8499BA0E_REVIEW`

- MAC 对象: `车身`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['抬']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_9D8499BA0E + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13534:意图1` — 车身高度抬至较高

## 1181. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `车载儿童座椅`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3768:意图1` — 加热车载儿童座椅

## 1182. `KNOWN_CONTROL_CANDIDATE_3B821DA938_REVIEW`

- MAC 对象: `车载儿童座椅`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['停止', '退出']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_3B821DA938 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10374:意图1` — 车载儿童座椅退出加热
- `train_set.jsonl:14247:意图1` — 车载儿童座椅停止加热

## 1183. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_OFF`

- MAC 对象: `车载儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10799:意图1` — 退出车载儿童座椅自然通风

## 1184. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `车载儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启动']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:166:意图1` — 车载儿童座椅启动自然通风
- `train_set.jsonl:18432:意图1` — 车载儿童座椅启动自然风

## 1185. `KNOWN_CONTROL_CANDIDATE_90B4450B13_SET`

- MAC 对象: `车载冰箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_90B4450B13 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8755:意图1` — 切换车载冰箱保温时间至1小时

## 1186. `KNOWN_CONTROL_CANDIDATE_90B4450B13_SET`

- MAC 对象: `车载冰箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到', '调成']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_90B4450B13 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15962:意图1` — 车载冰箱模式调成红酒
- `train_set.jsonl:2761:意图1` — 车载冰箱调到热饮

## 1187. `KNOWN_CONTROL_CANDIDATE_90B4450B13_TURN_OFF`

- MAC 对象: `车载冰箱`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_90B4450B13 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4633:意图1` — 车载冰箱保温时长开关关闭

## 1188. `KNOWN_CONTROL_CANDIDATE_AC3A55FBD5_TURN_ON`

- MAC 对象: `车载冰箱抽屉`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_AC3A55FBD5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6020:意图1` — 车载冰箱抽屉打开

## 1189. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `车载智能儿童座椅`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10352:意图1` — 车载智能儿童座椅打开加热
- `train_set.jsonl:15656:意图1` — 开启车载智能儿童座椅加热
- `train_set.jsonl:18905:意图1` — 加热车载智能儿童座椅

## 1190. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `车载智能儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15631:意图1` — 通风车载智能儿童座椅

## 1191. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `车载智能儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['启动']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11938:意图1` — 启动车载智能儿童座椅自然风

## 1192. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_REVIEW`

- MAC 对象: `车载智能儿童座椅`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['进行']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6317:意图1` — 车载智能儿童座椅进行通风

## 1193. `KNOWN_CONTROL_CANDIDATE_DCC472BE46_TURN_ON`

- MAC 对象: `车载香氛`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_DCC472BE46 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14912:意图2` — 打开车载香氛

## 1194. `KNOWN_CONTROL_CANDIDATE_636721A891_REVIEW`

- MAC 对象: `车辆操作模式`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['改为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_636721A891 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:3547:意图1` — 车辆操作模式改为泥泞模式

## 1195. `KNOWN_CONTROL_CANDIDATE_7D52421881_SET`

- MAC 对象: `车辆模式`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7D52421881 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15787:意图1` — 将车辆模式设置为越野

## 1196. `KNOWN_CONTROL_CANDIDATE_D17E765DAA_REVIEW`

- MAC 对象: `车辆空调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['停用']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_D17E765DAA + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10435:意图1` — 车辆空调停用省电模式

## 1197. `KNOWN_CONTROL_CANDIDATE_82C2195C13_TURN_OFF`

- MAC 对象: `车隔断玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关上']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_82C2195C13 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10159:意图1` — 把车隔断玻璃关上

## 1198. `KNOWN_CONTROL_CANDIDATE_2963A20D68_SET`

- MAC 对象: `车顶`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_2963A20D68 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5678:意图1` — 车顶再暗一点

## 1199. `KNOWN_CONTROL_CANDIDATE_7127B4D3DD_SET`

- MAC 对象: `转向`
- MAC 对象功能: `助力`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调为']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_7127B4D3DD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17698:意图1` — 转向助力调为厚重
- `train_set.jsonl:17999:意图1` — 转向助力调为沉稳模式

## 1200. `KNOWN_CONTROL_CANDIDATE_892460A016_SET`

- MAC 对象: `轮廓灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_892460A016 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15625:意图1` — 轮廓灯太亮了

## 1201. `KNOWN_CONTROL_CANDIDATE_892460A016_TURN_ON`

- MAC 对象: `轮廓灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_892460A016 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:80:意图2` — 打开轮廓灯

## 1202. `KNOWN_CONTROL_CANDIDATE_D54EBE9506_TURN_OFF`

- MAC 对象: `遥控`
- MAC 对象功能: `解锁功能`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_D54EBE9506 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14908:意图1` — 关遥控解锁功能设置

## 1203. `KNOWN_CONTROL_CANDIDATE_5C039A8732_TURN_OFF`

- MAC 对象: `遮光帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_5C039A8732 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6408:意图2` — 关闭遮光帘

## 1204. `KNOWN_CONTROL_CANDIDATE_B8A79F4C05_TURN_ON`

- MAC 对象: `遮阳`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_B8A79F4C05 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9534:意图3` — 打开遮阳

## 1205. `KNOWN_CONTROL_CANDIDATE_8C85E48720_SET`

- MAC 对象: `遮阳帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_8C85E48720 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18635:意图1` — 遮阳帘调一下

## 1206. `KNOWN_CONTROL_CANDIDATE_8C85E48720_REVIEW`

- MAC 对象: `遮阳帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['拉下', '拉起来']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_8C85E48720 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20100:意图1` — 前后遮阳帘都拉下
- `train_set.jsonl:2247:意图1` — 后座遮阳帘拉起来

## 1207. `KNOWN_CONTROL_CANDIDATE_B61C982DE5_TURN_ON`

- MAC 对象: `遮阳帘帘`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_B61C982DE5 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7832:意图1` — 我要把前边和后边的遮阳帘帘打开条缝
- `train_set.jsonl:7832:意图2` — 我要把前边和后边的遮阳帘帘打开条缝

## 1208. `KNOWN_CONTROL_CANDIDATE_5A008521B4_SET`

- MAC 对象: `遮阳帘调节`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5A008521B4 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11561:意图1` — 减小遮阳帘调节

## 1209. `KNOWN_CONTROL_CANDIDATE_70FBA17FFF_SET`

- MAC 对象: `钥匙`
- MAC 对象功能: `解锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置为', '调']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_70FBA17FFF + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15667:意图1` — 调钥匙解锁模式为全车解锁
- `train_set.jsonl:7038:意图1` — 钥匙解锁设置为主驾

## 1210. `KNOWN_CONTROL_CANDIDATE_70FBA17FFF_TURN_ON`

- MAC 对象: `钥匙`
- MAC 对象功能: `解锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_70FBA17FFF + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13301:意图1` — 钥匙解锁只开主驾门

## 1211. `KNOWN_CONTROL_CANDIDATE_8459B4EFAD_SET`

- MAC 对象: `银屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_8459B4EFAD + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14923:意图1` — 调暗银屏

## 1212. `KNOWN_CONTROL_CANDIDATE_3BCD9B104C_SET`

- MAC 对象: `长联屏屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_3BCD9B104C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10262:意图1` — 长联屏屏幕调亮

## 1213. `KNOWN_CONTROL_CANDIDATE_A407325E00_TURN_OFF`

- MAC 对象: `门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_A407325E00 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19534:意图1` — 关闭右后门

## 1214. `KNOWN_CONTROL_CANDIDATE_A407325E00_TURN_OFF`

- MAC 对象: `门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关掉', '关闭']`
- 唯一样本数: **8**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_A407325E00 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20325:意图1` — 我想关闭前排门手动开
- `test_set.jsonl:550:意图1` — 我要关掉前门手动模式
- `test_set.jsonl:939:意图1` — 关闭后排门手动开
- `train_set.jsonl:14408:意图1` — 关掉前门手动开启
- `train_set.jsonl:1444:意图1` — 帮我关掉前门手动开启

## 1215. `KNOWN_CONTROL_CANDIDATE_A407325E00_TURN_ON`

- MAC 对象: `门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开', '打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A407325E00 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10681:意图2` — 打开左侧驾驶门
- `train_set.jsonl:18684:意图1` — 打开开门
- `train_set.jsonl:7890:意图1` — 我要下车帮我开驾驶位的门

## 1216. `KNOWN_CONTROL_CANDIDATE_A407325E00_TURN_ON`

- MAC 对象: `门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启', '打开']`
- 唯一样本数: **5**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A407325E00 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12837:意图1` — 打开前门手动模式
- `train_set.jsonl:1466:意图1` — 打开后排门手动开
- `train_set.jsonl:1837:意图1` — 我想打开后排门手动开
- `train_set.jsonl:2369:意图1` — 开启前门手动开启
- `train_set.jsonl:5227:意图1` — 我想打开前门手动开启

## 1217. `KNOWN_CONTROL_CANDIDATE_A407325E00_REVIEW`

- MAC 对象: `门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['合上', '开个']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A407325E00 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10298:意图1` — 开个门
- `train_set.jsonl:14449:意图1` — 合上主驾的门

## 1218. `KNOWN_CONTROL_CANDIDATE_A407325E00_REVIEW`

- MAC 对象: `门`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开下']`
- 唯一样本数: **4**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_A407325E00 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20132:意图1` — 帮我开下后门手动开启
- `train_set.jsonl:11437:意图1` — 开下后排门手动开
- `train_set.jsonl:16379:意图1` — 帮我开下前门手动模式
- `train_set.jsonl:16393:意图1` — 开下后门手动开启

## 1219. `KNOWN_CONTROL_CANDIDATE_2497B57B0D_TURN_ON`

- MAC 对象: `门`
- MAC 对象功能: `感应`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_2497B57B0D + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7850:意图1` — 打开自动感应门开关

## 1220. `KNOWN_CONTROL_CANDIDATE_587690A22C_SET`

- MAC 对象: `门把手`
- MAC 对象功能: `自动缩回`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调到']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_587690A22C + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2299:意图1` — 门把手自动缩回时间调到3分钟

## 1221. `KNOWN_CONTROL_CANDIDATE_1AC82D8838_TURN_ON`

- MAC 对象: `门把手灯光`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_1AC82D8838 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:15593:意图1` — 打开门把手灯光

## 1222. `KNOWN_CONTROL_CANDIDATE_D740F27731_TURN_ON`

- MAC 对象: `门控灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_D740F27731 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11335:意图1` — 打开门控灯

## 1223. `KNOWN_CONTROL_CANDIDATE_86ABEF8B01_TURN_OFF`

- MAC 对象: `门玻璃`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_86ABEF8B01 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:2396:意图1` — 关闭左前门玻璃

## 1224. `KNOWN_CONTROL_CANDIDATE_81AF0FE309_TURN_OFF`

- MAC 对象: `门窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_81AF0FE309 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1665:意图1` — 关闭所有门窗

## 1225. `KNOWN_CONTROL_CANDIDATE_81AF0FE309_TURN_ON`

- MAC 对象: `门窗`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_81AF0FE309 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8008:意图2` — 打开前面门窗

## 1226. `KNOWN_CONTROL_CANDIDATE_BD338BB6A5_TURN_ON`

- MAC 对象: `门窗`
- MAC 对象功能: `通风`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BD338BB6A5 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:585:意图2` — 打开门窗通风

## 1227. `KNOWN_CONTROL_CANDIDATE_63579E05E3_TURN_ON`

- MAC 对象: `门锁`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **3**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_63579E05E3 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11661:意图1` — 车辆锁上
- `train_set.jsonl:1331:意图1` — 打开锁门
- `train_set.jsonl:2701:意图1` — 车辆锁

## 1228. `KNOWN_CONTROL_CANDIDATE_A5C8635606_TURN_ON`

- MAC 对象: `门锁`
- MAC 对象功能: `中控锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_A5C8635606 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6524:意图1` — 取消车辆锁定

## 1229. `KNOWN_CONTROL_CANDIDATE_39DC290B87_TURN_ON`

- MAC 对象: `门锁`
- MAC 对象功能: `行车落锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_39DC290B87 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17614:意图1` — 打开行车落锁

## 1230. `KNOWN_CONTROL_CANDIDATE_BFE5758B16_TURN_OFF`

- MAC 对象: `门锁`
- MAC 对象功能: `行车闭锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_BFE5758B16 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17175:意图1` — 关闭行车闭锁

## 1231. `KNOWN_CONTROL_CANDIDATE_BFE5758B16_TURN_ON`

- MAC 对象: `门锁`
- MAC 对象功能: `行车闭锁`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_BFE5758B16 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14698:意图1` — 打开行车闭锁

## 1232. `KNOWN_CONTROL_CANDIDATE_4F65B0CF31_TURN_OFF`

- MAC 对象: `阅读灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_4F65B0CF31 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19802:意图1` — 阅读灯自动关

## 1233. `KNOWN_CONTROL_CANDIDATE_4F65B0CF31_TURN_ON`

- MAC 对象: `阅读灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_4F65B0CF31 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5756:意图1` — 打开自动阅读灯

## 1234. `KNOWN_CONTROL_CANDIDATE_4F65B0CF31_REVIEW`

- MAC 对象: `阅读灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['体验', '使用']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_4F65B0CF31 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14036:意图1` — 我想体验主驾阅读灯
- `train_set.jsonl:4594:意图1` — 我要使用阅读灯在主驾

## 1235. `KNOWN_CONTROL_CANDIDATE_3A378ED57F_TURN_ON`

- MAC 对象: `除味`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3A378ED57F + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9937:意图1` — 打开除味

## 1236. `KNOWN_CONTROL_CANDIDATE_6D7366B827_TURN_ON`

- MAC 对象: `隔断`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_6D7366B827 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:17480:意图1` — 隔断开百分之三十

## 1237. `KNOWN_CONTROL_CANDIDATE_6D7366B827_REVIEW`

- MAC 对象: `隔断`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['升起来']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_6D7366B827 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9459:意图1` — 隔断升起来

## 1238. `KNOWN_CONTROL_CANDIDATE_6D7366B827_REVIEW`

- MAC 对象: `隔断`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['降']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_6D7366B827 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11090:意图1` — 隔断降到最低

## 1239. `KNOWN_CONTROL_CANDIDATE_6D7366B827_REVIEW`

- MAC 对象: `隔断`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_6D7366B827 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10427:意图1` — 隔断设成不透明

## 1240. `KNOWN_CONTROL_CANDIDATE_0193278D67_TURN_ON`

- MAC 对象: `雨灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_0193278D67 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:9491:意图1` — 打开前雨灯

## 1241. `KNOWN_CONTROL_CANDIDATE_4D5D367CB9_SET`

- MAC 对象: `雨量传感器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_4D5D367CB9 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12995:意图1` — 将雨量传感器灵敏度调高2
- `train_set.jsonl:18807:意图1` — 将雨量传感器灵敏度调低一点

## 1242. `KNOWN_CONTROL_CANDIDATE_3B9D237C47_TURN_ON`

- MAC 对象: `雷达`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B9D237C47 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11966:意图1` — 雷达音量关闭

## 1243. `KNOWN_CONTROL_CANDIDATE_3B9D237C47_REVIEW`

- MAC 对象: `雷达`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_3B9D237C47 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20124:意图1` — 雷达报警音设为中

## 1244. `KNOWN_CONTROL_CANDIDATE_11608F8EEC_SET`

- MAC 对象: `雷达`
- MAC 对象功能: `倒车`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_11608F8EEC + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1624:意图1` — 设置倒车雷达声音

## 1245. `KNOWN_CONTROL_CANDIDATE_FD901B35F7_SET`

- MAC 对象: `靠椅`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_FD901B35F7 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4123:意图1` — 调节后排靠椅

## 1246. `KNOWN_CONTROL_CANDIDATE_039C0FC943_SET`

- MAC 对象: `面发光氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_039C0FC943 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7016:意图1` — 面发光氛围灯亮度调到百分之三

## 1247. `KNOWN_CONTROL_CANDIDATE_039C0FC943_TURN_ON`

- MAC 对象: `面发光氛围灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_039C0FC943 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5508:意图1` — 打开面发光氛围灯

## 1248. `KNOWN_CONTROL_CANDIDATE_DAE1E18706_SET`

- MAC 对象: `面发光灯`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_DAE1E18706 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13875:意图1` — 面发光灯亮度调到8%

## 1249. `KNOWN_CONTROL_CANDIDATE_24A8D80BBB_SET`

- MAC 对象: `音响`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_24A8D80BBB + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18865:意图1` — 音响切换成共享模式

## 1250. `KNOWN_CONTROL_CANDIDATE_24A8D80BBB_TURN_OFF`

- MAC 对象: `音响`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关下', '关闭']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_24A8D80BBB + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:13527:意图2` — 关闭车外音响
- `train_set.jsonl:8602:意图1` — 音响调节页为我关下

## 1251. `KNOWN_CONTROL_CANDIDATE_24A8D80BBB_TURN_OFF`

- MAC 对象: `音响`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_24A8D80BBB + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:10203:意图2` — 关闭音响

## 1252. `KNOWN_CONTROL_CANDIDATE_B2B134FE1E_TURN_OFF`

- MAC 对象: `顶屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_B2B134FE1E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19593:意图1` — 关闭顶屏幕

## 1253. `KNOWN_CONTROL_CANDIDATE_B2B134FE1E_TURN_ON`

- MAC 对象: `顶屏幕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_B2B134FE1E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:16944:意图1` — 顶屏幕打开

## 1254. `KNOWN_CONTROL_CANDIDATE_C8EAA4E915_TURN_OFF`

- MAC 对象: `顶棚屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_C8EAA4E915 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5133:意图1` — 后排顶棚屏关闭

## 1255. `KNOWN_CONTROL_CANDIDATE_C8EAA4E915_TURN_ON`

- MAC 对象: `顶棚屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_C8EAA4E915 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14841:意图1` — 开启顶棚屏

## 1256. `KNOWN_CONTROL_CANDIDATE_C2332227F2_SET`

- MAC 对象: `顶部娱乐屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_C2332227F2 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:8941:意图1` — 后排顶部娱乐屏亮度值调至20

## 1257. `KNOWN_CONTROL_CANDIDATE_C2332227F2_TURN_OFF`

- MAC 对象: `顶部娱乐屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关一下']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_C2332227F2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:12915:意图1` — 关一下后排顶部娱乐屏

## 1258. `KNOWN_CONTROL_CANDIDATE_C2332227F2_TURN_ON`

- MAC 对象: `顶部娱乐屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_C2332227F2 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:1479:意图1` — 打开后排顶部娱乐屏

## 1259. `KNOWN_CONTROL_CANDIDATE_CF33CDCE27_SET`

- MAC 对象: `颈枕`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_CF33CDCE27 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18465:意图1` — 主驾颈枕前移

## 1260. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `颈枕`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4063:意图1` — 打开颈枕加热

## 1261. `KNOWN_CONTROL_CANDIDATE_3B821DA938_TURN_ON`

- MAC 对象: `颈部`
- MAC 对象功能: `加热`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_3B821DA938 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:5123:意图1` — 打开前排颈部加热
- `train_set.jsonl:5429:意图1` — 打开副驾颈部加热

## 1262. `KNOWN_CONTROL_CANDIDATE_1C1B1CE2A9_SET`

- MAC 对象: `风空调`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调节']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_1C1B1CE2A9 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11943:意图1` — 风空调风量调至三级
- `train_set.jsonl:7667:意图1` — 风空调风量调到三挡

## 1263. `KNOWN_CONTROL_CANDIDATE_5E4AE4CA19_SET`

- MAC 对象: `香氛`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['切换']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_5E4AE4CA19 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11231:意图1` — 切换香氛

## 1264. `KNOWN_CONTROL_CANDIDATE_5E4AE4CA19_TURN_ON`

- MAC 对象: `香氛`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_5E4AE4CA19 + STATE`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14864:意图3` — 打开空调打开香氛适中

## 1265. `KNOWN_CONTROL_CANDIDATE_5E4AE4CA19_REVIEW`

- MAC 对象: `香氛`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['换一个', '用不到']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_5E4AE4CA19 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:6169:意图1` — 感觉用不到香氛了
- `train_set.jsonl:6495:意图1` — 有什么其他味道的香氛换一个试试

## 1266. `KNOWN_CONTROL_CANDIDATE_9C30790799_TURN_ON`

- MAC 对象: `香氛石`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_9C30790799 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:14464:意图1` — 打开香氛石

## 1267. `KNOWN_CONTROL_CANDIDATE_1F31093ABE_TURN_ON`

- MAC 对象: `香氛系统`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **2**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_1F31093ABE + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:19289:意图2` — 打开香氛系统
- `train_set.jsonl:8202:意图2` — 打开香氛系统

## 1268. `KNOWN_CONTROL_CANDIDATE_2AF77F5856_SET`

- MAC 对象: `香水`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['调']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_2AF77F5856 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:19080:意图1` — 香水浓度调至最浓

## 1269. `KNOWN_CONTROL_CANDIDATE_7CECF1679E_TURN_ON`

- MAC 对象: `香熏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['打开']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_7CECF1679E + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:11092:意图1` — 打开香熏

## 1270. `KNOWN_CONTROL_CANDIDATE_24AAF7CEB8_TURN_ON`

- MAC 对象: `香薰发射器`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['开启']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_ON + KNOWN_CONTROL_CANDIDATE_24AAF7CEB8 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `test_set.jsonl:818:意图1` — 开启香薰发射器

## 1271. `KNOWN_CONTROL_CANDIDATE_30FC5CE4F4_TURN_OFF`

- MAC 对象: `驶屏`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_30FC5CE4F4 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4227:意图2` — 关闭副驾驶屏

## 1272. `KNOWN_CONTROL_CANDIDATE_714CAC30E2_SET`

- MAC 对象: `麦克风`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设为']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_714CAC30E2 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:4382:意图1` — 麦克风使用有效期设为单次

## 1273. `KNOWN_CONTROL_CANDIDATE_714CAC30E2_SET`

- MAC 对象: `麦克风`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['设置成']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `SET + KNOWN_CONTROL_CANDIDATE_714CAC30E2 + SETTING`
- 建议 slots: `['VALUE']`
- 审批状态: **PENDING**

真实示例：

- `dev_set.jsonl:20225:意图1` — 我想把麦克风设置成静音

## 1274. `KNOWN_CONTROL_CANDIDATE_714CAC30E2_REVIEW`

- MAC 对象: `麦克风`
- MAC 对象功能: ``
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['禁']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `REVIEW + KNOWN_CONTROL_CANDIDATE_714CAC30E2 + SETTING`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:18319:意图1` — 你给我禁麦克风呀

## 1275. `KNOWN_CONTROL_CANDIDATE_59D5B005E1_TURN_OFF`

- MAC 对象: `麦克风`
- MAC 对象功能: `使用权限`
- MAC 功能: ``
- MAC 子功能: ``
- MAC 操作: `['关闭']`
- 唯一样本数: **1**
- Formal 近邻冲突: `False` `[]`
- 建议三元组: `TURN_OFF + KNOWN_CONTROL_CANDIDATE_59D5B005E1 + STATE`
- 建议 slots: `[]`
- 审批状态: **PENDING**

真实示例：

- `train_set.jsonl:7431:意图1` — 关闭麦克风使用权限

# R4 Known-Unsupported Expansion Report v1

- Removed dead contracts: `['FOLLOWING_GAP_REQUIRED']`
- New intents: **61**
- New capability families: **23**
- Formal intents: **71**
- Known unsupported intents: **83**
- R4 full SHA256: `393de4203c2cb93b0162724b336cb29a2cc67fba1c73b1cbc1fe62bb642f4f21`

## `AIR_PURIFIER_OFF`

- 唯一样本数: **5**
- 三元组: `TURN_OFF + AIR_PURIFIER + STATE`
- Capability family: `PROJECT_AIR_PURIFIER_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `train_set.jsonl:17371:意图1` — 关闭空气净化功能
- `train_set.jsonl:5453:意图1` — 关闭智能空气净化
- `train_set.jsonl:6797:意图1` — 关掉空气净化
- `train_set.jsonl:6919:意图1` — 关空气净化器
- `train_set.jsonl:9206:意图1` — 把空气净化器关掉

## `AIR_PURIFIER_ON`

- 唯一样本数: **16**
- 三元组: `TURN_ON + AIR_PURIFIER + STATE`
- Capability family: `PROJECT_AIR_PURIFIER_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19446:意图1` — 空气净化器帮我把它给调开
- `dev_set.jsonl:20525:意图1` — 把空气净化打开
- `train_set.jsonl:11282:意图1` — 空气净化器赶紧把它开关给开开
- `train_set.jsonl:12093:意图1` — 空气净化开最大
- `train_set.jsonl:12575:意图1` — 打开自动空气净化

## `AIR_PURIFIER_SET_MODE`

- 唯一样本数: **2**
- 三元组: `SWITCH_MODE + AIR_PURIFIER + MODE`
- Capability family: `PROJECT_AIR_PURIFIER_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `KNOWN_AIR_PURIFIER_SOURCE_MODE`

- `train_set.jsonl:14574:意图1` — 空气净化器变成自动模式
- `train_set.jsonl:8684:意图1` — 空气净化器调成自动

## `AMBIENT_LIGHT_OFF`

- 唯一样本数: **58**
- 三元组: `TURN_OFF + AMBIENT_LIGHT + STATE`
- Capability family: `PROJECT_AMBIENT_LIGHT_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19191:意图1` — 关闭欢送氛围灯
- `dev_set.jsonl:19560:意图1` — 关闭氛围灯
- `dev_set.jsonl:20482:意图2` — 关闭氛围灯
- `test_set.jsonl:335:意图2` — 关闭氛围灯
- `test_set.jsonl:369:意图1` — 关闭氛围灯

## `AMBIENT_LIGHT_ON`

- 唯一样本数: **19**
- 三元组: `TURN_ON + AMBIENT_LIGHT + STATE`
- Capability family: `PROJECT_AMBIENT_LIGHT_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `test_set.jsonl:1075:意图1` — 开启氛围灯
- `test_set.jsonl:936:意图1` — 打开氛围灯把颜色调成红色
- `train_set.jsonl:10139:意图1` — 我想看到后排的氛围灯
- `train_set.jsonl:10240:意图1` — 把氛围灯设置开开
- `train_set.jsonl:1175:意图3` — 打开氛围灯

## `AMBIENT_LIGHT_SET_BRIGHTNESS`

- 唯一样本数: **11**
- 三元组: `SET + AMBIENT_LIGHT + BRIGHTNESS`
- Capability family: `PROJECT_AMBIENT_LIGHT_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_LEVEL_OPTIONAL` / `None`

- `dev_set.jsonl:20096:意图1` — 氛围灯亮度太亮了
- `train_set.jsonl:10124:意图2` — 氛围灯最亮
- `train_set.jsonl:14012:意图1` — 氛围灯亮度调为亮
- `train_set.jsonl:15458:意图1` — 将氛围灯的亮度调至2
- `train_set.jsonl:1633:意图1` — 氛围灯灯光亮一些

## `AMBIENT_LIGHT_SET_COLOR`

- 唯一样本数: **26**
- 三元组: `SET + AMBIENT_LIGHT + COLOR`
- Capability family: `PROJECT_AMBIENT_LIGHT_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_COLOR_OPTIONAL` / `None`

- `dev_set.jsonl:19238:意图4` — 打开座椅通风
- `dev_set.jsonl:19807:意图1` — 把氛围灯调成绿色
- `dev_set.jsonl:20256:意图1` — 氛围灯颜色切换成柔肤色
- `train_set.jsonl:10156:意图1` — 氛围灯切换为活力橙
- `train_set.jsonl:10459:意图3` — 氛围灯调到红色

## `AMBIENT_LIGHT_SET_MODE`

- 唯一样本数: **21**
- 三元组: `SWITCH_MODE + AMBIENT_LIGHT + MODE`
- Capability family: `PROJECT_AMBIENT_LIGHT_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `KNOWN_AMBIENT_LIGHT_SOURCE_MODE`

- `test_set.jsonl:147:意图1` — 氛围灯模式切换为关联驾驶模式
- `test_set.jsonl:533:意图1` — 氛围灯模式切到
- `test_set.jsonl:782:意图1` — 氛围灯设置单色固定模式
- `test_set.jsonl:789:意图1` — 氛围灯调到温度模式
- `test_set.jsonl:995:意图1` — 变成氛围灯效果单色闪动

## `ARMREST_SET_POSITION`

- 唯一样本数: **118**
- 三元组: `ADJUST + ARMREST + POSITION`
- Capability family: `PROJECT_ARMREST_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_POSITION_OPTIONAL` / `None`

- `dev_set.jsonl:19247:意图1` — 扶手朝前方滑到最前
- `dev_set.jsonl:19251:意图1` — 扶手台前滑到最前
- `dev_set.jsonl:20296:意图1` — 扶手台前面移动
- `dev_set.jsonl:20323:意图1` — 扶手台往前面移动到最前
- `test_set.jsonl:1118:意图1` — 扶手台滑动到最后

## `BLUETOOTH_OFF`

- 唯一样本数: **18**
- 三元组: `TURN_OFF + BLUETOOTH + STATE`
- Capability family: `PROJECT_BLUETOOTH_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `train_set.jsonl:12135:意图1` — 蓝牙关上了没呢
- `train_set.jsonl:12677:意图1` — 你蓝牙关闭着吗啊
- `train_set.jsonl:12964:意图1` — 你现在的蓝牙关上了吗
- `train_set.jsonl:15187:意图1` — 关闭蓝牙
- `train_set.jsonl:15301:意图1` — 关闭蓝牙

## `BLUETOOTH_ON`

- 唯一样本数: **16**
- 三元组: `TURN_ON + BLUETOOTH + STATE`
- Capability family: `PROJECT_BLUETOOTH_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19509:意图3` — 打开蓝牙
- `dev_set.jsonl:19563:意图1` — 打开蓝牙
- `test_set.jsonl:227:意图1` — 打开蓝牙
- `test_set.jsonl:236:意图1` — 打开蓝牙
- `train_set.jsonl:13564:意图2` — 打开蓝牙控制面板

## `CAMERA_OFF`

- 唯一样本数: **1**
- 三元组: `TURN_OFF + CAMERA + STATE`
- Capability family: `PROJECT_CAMERA_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19746:意图1` — 把摄像头关了

## `CAMERA_ON`

- 唯一样本数: **2**
- 三元组: `TURN_ON + CAMERA + STATE`
- Capability family: `PROJECT_CAMERA_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `train_set.jsonl:18772:意图1` — 打开车内摄像头
- `train_set.jsonl:2952:意图1` — 打开摄像头画面

## `CAMERA_SET_MODE`

- 唯一样本数: **34**
- 三元组: `SWITCH_MODE + CAMERA + MODE`
- Capability family: `PROJECT_CAMERA_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `KNOWN_CAMERA_SOURCE_MODE`

- `dev_set.jsonl:19240:意图1` — 开启录像录音功能
- `dev_set.jsonl:19410:意图1` — 关闭前视记录仪录像
- `dev_set.jsonl:19823:意图1` — 关下驻车拍照
- `dev_set.jsonl:19851:意图1` — 给我拍张照
- `test_set.jsonl:336:意图1` — 把视频录制的开关设置成打开

## `CHILD_LOCK_OFF`

- 唯一样本数: **8**
- 三元组: `TURN_OFF + CHILD_LOCK + STATE`
- Capability family: `PROJECT_CHILD_LOCK_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19236:意图1` — 右边的儿童锁可以帮我把它给关掉
- `dev_set.jsonl:19358:意图1` — 关闭右边儿童锁
- `test_set.jsonl:622:意图1` — 儿童锁键为我关闭
- `test_set.jsonl:787:意图1` — 右边儿童锁请给关闭
- `train_set.jsonl:1583:意图1` — 左边的儿童锁可以帮我把它给关掉

## `CHILD_LOCK_ON`

- 唯一样本数: **6**
- 三元组: `TURN_ON + CHILD_LOCK + STATE`
- Capability family: `PROJECT_CHILD_LOCK_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `test_set.jsonl:1055:意图1` — 左边有儿童把左边儿童锁打开吧
- `train_set.jsonl:11899:意图1` — 打开右边儿童锁
- `train_set.jsonl:12211:意图1` — 儿童锁给我打开
- `train_set.jsonl:14970:意图1` — 把左边儿童锁设为开启状态
- `train_set.jsonl:15510:意图1` — 给我打开儿童锁

## `DISPLAY_OFF`

- 唯一样本数: **94**
- 三元组: `TURN_OFF + DISPLAY + STATE`
- Capability family: `PROJECT_DISPLAY_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19202:意图2` — 关闭屏幕
- `dev_set.jsonl:19412:意图2` — 关闭屏幕
- `dev_set.jsonl:19433:意图1` — 右手边的屏关闭
- `dev_set.jsonl:19539:意图1` — 关闭屏幕
- `dev_set.jsonl:19858:意图1` — 关闭关闭后排屏幕

## `DISPLAY_ON`

- 唯一样本数: **31**
- 三元组: `TURN_ON + DISPLAY + STATE`
- Capability family: `PROJECT_DISPLAY_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19791:意图1` — 展开屏幕
- `dev_set.jsonl:20173:意图2` — 打开hud
- `test_set.jsonl:318:意图1` — 打开音乐全屏显示
- `test_set.jsonl:432:意图2` — 打开中控屏
- `test_set.jsonl:533:意图2` — 屏幕同步

## `DISPLAY_SET_BRIGHTNESS`

- 唯一样本数: **58**
- 三元组: `SET + DISPLAY + BRIGHTNESS`
- Capability family: `PROJECT_DISPLAY_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_LEVEL_OPTIONAL` / `None`

- `test_set.jsonl:1021:意图1` — 屏幕亮度有点暗
- `test_set.jsonl:587:意图1` — 把屏幕给我暗一点可以吗
- `test_set.jsonl:695:意图1` — 主驾屏幕亮一点
- `test_set.jsonl:703:意图1` — 调低屏幕亮度要怎么调
- `test_set.jsonl:989:意图1` — 屏幕亮度调到最亮

## `DISPLAY_SET_POSITION`

- 唯一样本数: **189**
- 三元组: `ADJUST + DISPLAY + POSITION`
- Capability family: `PROJECT_DISPLAY_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_POSITION_OPTIONAL` / `None`

- `dev_set.jsonl:19269:意图1` — 副驾屏往主驾滑
- `dev_set.jsonl:19521:意图1` — 中控屏朝向主驾
- `dev_set.jsonl:19633:意图1` — 娱乐屏朝右手边滑一下
- `dev_set.jsonl:19703:意图1` — 娱乐屏幕朝右移动
- `dev_set.jsonl:19718:意图1` — 副驾屏幕向右移

## `DRIVING_MODE_SET`

- 唯一样本数: **34**
- 三元组: `SWITCH_MODE + DRIVING_MODE + MODE`
- Capability family: `PROJECT_DRIVING_MODE_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `KNOWN_DRIVING_MODE_SOURCE_MODE`

- `dev_set.jsonl:19386:意图1` — 切换驾驶模式为舒适
- `dev_set.jsonl:19583:意图1` — 仪表切换为驾驶模式
- `test_set.jsonl:1064:意图3` — 把驾驶模式调节为舒适
- `test_set.jsonl:1095:意图1` — 请切换驾驶模式到泥泞
- `test_set.jsonl:164:意图1` — 切换到智能驾驶模式

## `DRIVING_RECORDER_ON`

- 唯一样本数: **2**
- 三元组: `TURN_ON + DRIVING_RECORDER + STATE`
- Capability family: `PROJECT_DRIVING_RECORDER_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `test_set.jsonl:214:意图1` — 打开行车记录仪
- `train_set.jsonl:2585:意图1` — 把行车记录仪调整到开启模式

## `FRAGRANCE_OFF`

- 唯一样本数: **18**
- 三元组: `TURN_OFF + FRAGRANCE + STATE`
- Capability family: `PROJECT_FRAGRANCE_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19346:意图1` — 关闭香氛
- `test_set.jsonl:313:意图2` — 关闭香氛
- `test_set.jsonl:335:意图1` — 关闭香氛
- `test_set.jsonl:506:意图1` — 关闭香氛
- `test_set.jsonl:98:意图2` — 关闭香氛

## `FRAGRANCE_ON`

- 唯一样本数: **26**
- 三元组: `TURN_ON + FRAGRANCE + STATE`
- Capability family: `PROJECT_FRAGRANCE_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19899:意图2` — 打开香氛香氛调到浓郁
- `dev_set.jsonl:20221:意图2` — 打开香氛
- `dev_set.jsonl:20525:意图2` — 香氛打开
- `test_set.jsonl:1085:意图1` — 打开香氛
- `train_set.jsonl:10384:意图1` — 打开香氛

## `FRAGRANCE_SET_LEVEL`

- 唯一样本数: **21**
- 三元组: `SET + FRAGRANCE + LEVEL`
- Capability family: `PROJECT_FRAGRANCE_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_LEVEL_OPTIONAL` / `None`

- `dev_set.jsonl:19284:意图1` — 香氛浓度调太高
- `dev_set.jsonl:19899:意图3` — 打开座椅通风打开香氛香氛调到浓郁
- `dev_set.jsonl:20416:意图1` — 香氛浓度调到馥郁
- `train_set.jsonl:10120:意图1` — 香氛浓度调到2级
- `train_set.jsonl:10441:意图1` — 调淡香氛的浓度

## `FRUNK_OPEN`

- 唯一样本数: **1**
- 三元组: `OPEN + FRUNK + OPENING_STATE`
- Capability family: `PROJECT_FRUNK_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `train_set.jsonl:4079:意图1` — 打开前备箱

## `GLASS_ROOF_SET_TRANSPARENCY`

- 唯一样本数: **72**
- 三元组: `SET + GLASS_ROOF + TRANSPARENCY`
- Capability family: `PROJECT_GLASS_ROOF_KNOWN_CONTROL`
- VALUE/MODE contract: `PERCENT_0_100_OPTIONAL` / `None`

- `dev_set.jsonl:19379:意图1` — 天幕最大天幕透明值最亮
- `dev_set.jsonl:19379:意图2` — 天幕最大天幕透明值最亮
- `train_set.jsonl:10122:意图1` — 把天幕透明度调到最低
- `train_set.jsonl:10358:意图1` — 天窗最亮天幕透明度最大
- `train_set.jsonl:10358:意图2` — 天窗最亮天幕透明度最大

## `HOTSPOT_OFF`

- 唯一样本数: **8**
- 三元组: `TURN_OFF + HOTSPOT + STATE`
- Capability family: `PROJECT_HOTSPOT_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `test_set.jsonl:236:意图2` — 关闭热点
- `train_set.jsonl:11830:意图1` — 关闭热点弹窗
- `train_set.jsonl:15878:意图1` — 关闭wifi调节
- `train_set.jsonl:17293:意图2` — 关闭wifi
- `train_set.jsonl:17986:意图1` — 关闭热点

## `HOTSPOT_ON`

- 唯一样本数: **17**
- 三元组: `TURN_ON + HOTSPOT + STATE`
- Capability family: `PROJECT_HOTSPOT_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19947:意图1` — 打开热点
- `test_set.jsonl:167:意图1` — 打开热点
- `train_set.jsonl:13396:意图1` — 打开wifi
- `train_set.jsonl:13396:意图2` — 打开热点
- `train_set.jsonl:14739:意图1` — 打开热点

## `HVAC_OFF`

- 唯一样本数: **399**
- 三元组: `TURN_OFF + HVAC + STATE`
- Capability family: `PROJECT_HVAC_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19208:意图2` — 关闭空调
- `dev_set.jsonl:19231:意图2` — 关闭空调
- `dev_set.jsonl:19246:意图4` — 关闭空调
- `dev_set.jsonl:19259:意图1` — 关闭空调
- `dev_set.jsonl:19340:意图1` — 关闭后座空调

## `HVAC_ON`

- 唯一样本数: **566**
- 三元组: `TURN_ON + HVAC + STATE`
- Capability family: `PROJECT_HVAC_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19195:意图1` — 打开空调
- `dev_set.jsonl:19211:意图2` — 开空调
- `dev_set.jsonl:19229:意图2` — 打开空调全车温度调到二十二度
- `dev_set.jsonl:19235:意图1` — 开启右后侧空调出风口
- `dev_set.jsonl:19322:意图1` — 打开副驾驶空调

## `HVAC_SET_AIRFLOW_DIRECTION`

- 唯一样本数: **75**
- 三元组: `SET + HVAC + AIRFLOW_DIRECTION`
- Capability family: `PROJECT_HVAC_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_AIRFLOW_DIRECTION_OPTIONAL` / `None`

- `dev_set.jsonl:19254:意图1` — 我要空调别吹脸
- `dev_set.jsonl:19301:意图1` — 空调不要对着我吹
- `dev_set.jsonl:19454:意图2` — 空调对着人吹
- `dev_set.jsonl:19597:意图1` — 空调风吹下方
- `dev_set.jsonl:19876:意图1` — 空调不要吹窗

## `HVAC_SET_FAN_SPEED`

- 唯一样本数: **204**
- 三元组: `SET + HVAC + FAN_SPEED`
- Capability family: `PROJECT_HVAC_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_LEVEL_OPTIONAL` / `None`

- `dev_set.jsonl:19224:意图1` — 空调风量调至四挡
- `dev_set.jsonl:19307:意图1` — 空调风力调到三挡
- `dev_set.jsonl:19516:意图5` — 空调风量开到二十六度
- `dev_set.jsonl:19770:意图1` — 空调风量调到一挡挡
- `dev_set.jsonl:19977:意图2` — 空调风速调到二挡

## `HVAC_SET_MODE`

- 唯一样本数: **51**
- 三元组: `SWITCH_MODE + HVAC + MODE`
- Capability family: `PROJECT_HVAC_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `KNOWN_HVAC_SOURCE_MODE`

- `dev_set.jsonl:19551:意图1` — 空调调成外循环
- `dev_set.jsonl:19712:意图1` — 设置空调舒适曲线为轻柔
- `test_set.jsonl:1114:意图2` — 停车空调设置为舒适模式
- `test_set.jsonl:149:意图1` — 空调吹脸为自由模式
- `test_set.jsonl:312:意图1` — 我想开下空调自然风设置页

## `HVAC_SET_TEMPERATURE`

- 唯一样本数: **453**
- 三元组: `SET + HVAC + TEMPERATURE`
- Capability family: `PROJECT_HVAC_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_TEMPERATURE_OPTIONAL` / `None`

- `dev_set.jsonl:19226:意图1` — 空调二十二度风速一挡
- `dev_set.jsonl:19228:意图1` — 打开空调二十二度
- `dev_set.jsonl:19257:意图3` — 空调调到二十三度
- `dev_set.jsonl:19261:意图1` — 把空调温度调到最低
- `dev_set.jsonl:19267:意图1` — 副驾区域空调温度降低四度

## `INTERIOR_LIGHT_OFF`

- 唯一样本数: **4**
- 三元组: `TURN_OFF + INTERIOR_LIGHT + STATE`
- Capability family: `PROJECT_INTERIOR_LIGHT_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `train_set.jsonl:14056:意图1` — 主驾车内灯关闭
- `train_set.jsonl:17739:意图1` — 关闭副驾车内灯
- `train_set.jsonl:4661:意图1` — 关闭顶灯
- `train_set.jsonl:7938:意图1` — 关闭三排右室内灯

## `INTERIOR_LIGHT_ON`

- 唯一样本数: **8**
- 三元组: `TURN_ON + INTERIOR_LIGHT + STATE`
- Capability family: `PROJECT_INTERIOR_LIGHT_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `test_set.jsonl:532:意图1` — 开启车内灯
- `train_set.jsonl:10263:意图1` — 把后排车内灯打开
- `train_set.jsonl:13243:意图1` — 打开后排车内灯
- `train_set.jsonl:16412:意图1` — 全部车内灯打开
- `train_set.jsonl:17112:意图1` — 打开三排室内灯

## `MEDIA_SOUND_EFFECT_SET`

- 唯一样本数: **89**
- 三元组: `SWITCH_MODE + MEDIA + SOUND_EFFECT`
- Capability family: `PROJECT_MEDIA_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `KNOWN_MEDIA_SOURCE_MODE`

- `dev_set.jsonl:19414:意图1` — 车外行人警示音设置为音效三
- `dev_set.jsonl:19805:意图1` — 音效增强设置为现场音乐会音效
- `dev_set.jsonl:20157:意图1` — 把音效模式改变爵士乐章
- `test_set.jsonl:112:意图1` — 播报发动机声
- `test_set.jsonl:261:意图1` — 超速的时候通过蜂鸣提醒我

## `MEDIA_VOLUME_SET`

- 唯一样本数: **246**
- 三元组: `SET + MEDIA + VOLUME`
- Capability family: `PROJECT_MEDIA_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_LEVEL_OPTIONAL` / `None`

- `dev_set.jsonl:19212:意图1` — 再降音量
- `dev_set.jsonl:19306:意图1` — 报警语音播报音量调到一半
- `dev_set.jsonl:19442:意图1` — 我要导航音量现在调高10%好吗
- `dev_set.jsonl:19634:意图1` — 上一首音量增大
- `dev_set.jsonl:19680:意图1` — 报警语音音量打开成30

## `READING_LIGHT_OFF`

- 唯一样本数: **17**
- 三元组: `TURN_OFF + READING_LIGHT + STATE`
- Capability family: `PROJECT_READING_LIGHT_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19648:意图2` — 关闭阅读灯
- `test_set.jsonl:108:意图1` — 关闭前排阅读灯
- `train_set.jsonl:1153:意图1` — 关闭左前阅读灯
- `train_set.jsonl:13382:意图2` — 关闭全部阅读灯
- `train_set.jsonl:14177:意图1` — 我在主驾不需用体验阅读灯了

## `READING_LIGHT_ON`

- 唯一样本数: **19**
- 三元组: `TURN_ON + READING_LIGHT + STATE`
- Capability family: `PROJECT_READING_LIGHT_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19260:意图1` — 打开所有阅读灯
- `dev_set.jsonl:19679:意图1` — 打开前排阅读灯
- `dev_set.jsonl:20356:意图2` — 退出导航打开阅读灯
- `train_set.jsonl:10702:意图1` — 打开阅读灯
- `train_set.jsonl:12071:意图2` — 打开全车座椅按摩

## `READING_LIGHT_SET_BRIGHTNESS`

- 唯一样本数: **7**
- 三元组: `SET + READING_LIGHT + BRIGHTNESS`
- Capability family: `PROJECT_READING_LIGHT_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_LEVEL_OPTIONAL` / `None`

- `dev_set.jsonl:19836:意图1` — 阅读灯我想要它变得稍微亮一点
- `test_set.jsonl:1007:意图1` — 阅读灯亮度帮我配置一下
- `train_set.jsonl:12247:意图1` — 调节阅读灯亮度
- `train_set.jsonl:14560:意图1` — 我要阅读灯的亮度开的稍微更清楚一些
- `train_set.jsonl:17100:意图1` — 改变阅读灯亮度

## `REFRIGERATOR_ON`

- 唯一样本数: **8**
- 三元组: `TURN_ON + REFRIGERATOR + STATE`
- Capability family: `PROJECT_REFRIGERATOR_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `test_set.jsonl:608:意图2` — 打开冰箱
- `train_set.jsonl:11807:意图1` — 打开冰箱
- `train_set.jsonl:12302:意图1` — 打开冰箱延时断电
- `train_set.jsonl:12754:意图1` — 冰箱童锁为我开开
- `train_set.jsonl:13191:意图1` — 打开冰箱童锁

## `REFRIGERATOR_SET_TEMPERATURE`

- 唯一样本数: **8**
- 三元组: `SET + REFRIGERATOR + TEMPERATURE`
- Capability family: `PROJECT_REFRIGERATOR_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_TEMPERATURE_OPTIONAL` / `None`

- `dev_set.jsonl:20529:意图2` — 冰箱温度设置成负六度
- `test_set.jsonl:758:意图1` — 冰箱温度调高3华氏度
- `test_set.jsonl:772:意图1` — 冰箱调到最冷的效果
- `train_set.jsonl:10277:意图1` — 冰箱调到50度
- `train_set.jsonl:14962:意图1` — 冰箱温度调到零下二十度

## `SEAT_HEATING_OFF`

- 唯一样本数: **56**
- 三元组: `TURN_OFF + SEAT_HEATING + STATE`
- Capability family: `PROJECT_SEAT_HEATING_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19314:意图1` — 座椅可以关加热功能了
- `dev_set.jsonl:19470:意图1` — 关闭座椅加热设置
- `dev_set.jsonl:19725:意图1` — 关闭座椅加热窗户全部打开
- `dev_set.jsonl:19831:意图1` — 关闭所有座椅加热
- `test_set.jsonl:104:意图2` — 关闭座椅加热

## `SEAT_HEATING_ON`

- 唯一样本数: **104**
- 三元组: `TURN_ON + SEAT_HEATING + STATE`
- Capability family: `PROJECT_SEAT_HEATING_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19638:意图2` — 打开前排的座椅加热
- `dev_set.jsonl:19679:意图2` — 左前座椅加热
- `dev_set.jsonl:19733:意图1` — 打开主副驾驶座椅加热和方向盘加热
- `dev_set.jsonl:19733:意图2` — 关闭车外提示音
- `dev_set.jsonl:20158:意图1` — 打开副驾座椅加热

## `SEAT_HEATING_SET_LEVEL`

- 唯一样本数: **24**
- 三元组: `SET + SEAT_HEATING + LEVEL`
- Capability family: `PROJECT_SEAT_HEATING_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_LEVEL_OPTIONAL` / `None`

- `test_set.jsonl:212:意图1` — 调高右排座椅加热8挡
- `test_set.jsonl:243:意图1` — 座椅加热一挡
- `test_set.jsonl:403:意图2` — 座椅加热调到一挡
- `train_set.jsonl:12485:意图1` — 座椅加热调小两格
- `train_set.jsonl:12722:意图1` — 两侧座椅加热到低档

## `SEAT_HEATING_SET_MODE`

- 唯一样本数: **1**
- 三元组: `SWITCH_MODE + SEAT_HEATING + MODE`
- Capability family: `PROJECT_SEAT_HEATING_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `KNOWN_SEAT_HEATING_SOURCE_MODE`

- `train_set.jsonl:4728:意图1` — 主驾座椅加热档位调到自动

## `SEAT_MASSAGE_OFF`

- 唯一样本数: **47**
- 三元组: `TURN_OFF + SEAT_MASSAGE + STATE`
- Capability family: `PROJECT_SEAT_MASSAGE_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19542:意图1` — 关闭座椅按摩
- `dev_set.jsonl:20348:意图1` — 关闭副驾座椅按摩
- `dev_set.jsonl:20348:意图2` — 关闭主驾副驾座椅按摩
- `dev_set.jsonl:20348:意图3` — 关闭副驾座椅按摩关闭主驾副驾座椅按摩
- `dev_set.jsonl:20377:意图2` — 关闭主驾座椅按摩

## `SEAT_MASSAGE_ON`

- 唯一样本数: **263**
- 三元组: `TURN_ON + SEAT_MASSAGE + STATE`
- Capability family: `PROJECT_SEAT_MASSAGE_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19318:意图1` — 副驾座椅按摩打开
- `dev_set.jsonl:19464:意图1` — 打开整车座椅按摩
- `dev_set.jsonl:19722:意图2` — 打开主驾座椅按摩
- `dev_set.jsonl:19774:意图2` — 主驾座椅按摩
- `dev_set.jsonl:19832:意图2` — 空调调到二十二度

## `SEAT_MASSAGE_SET_LEVEL`

- 唯一样本数: **10**
- 三元组: `SET + SEAT_MASSAGE + LEVEL`
- Capability family: `PROJECT_SEAT_MASSAGE_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_LEVEL_OPTIONAL` / `None`

- `train_set.jsonl:12037:意图1` — 主驾座椅按摩调小一点
- `train_set.jsonl:12340:意图1` — 副驾座椅按摩太弱了
- `train_set.jsonl:14143:意图1` — 座椅按摩调到3档
- `train_set.jsonl:14447:意图1` — 这个驾驶员座椅按摩太弱了
- `train_set.jsonl:15434:意图1` — 加大能量到座椅按摩上面

## `SEAT_MASSAGE_SET_MODE`

- 唯一样本数: **25**
- 三元组: `SWITCH_MODE + SEAT_MASSAGE + MODE`
- Capability family: `PROJECT_SEAT_MASSAGE_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `KNOWN_SEAT_MASSAGE_SOURCE_MODE`

- `dev_set.jsonl:19487:意图1` — 调节主驾座椅按摩模式为模式二
- `dev_set.jsonl:20135:意图1` — 座椅按摩调到脊柱按摩模式
- `dev_set.jsonl:20156:意图1` — 把左边座椅按摩调为交叉
- `test_set.jsonl:125:意图1` — 把座椅按摩模式调节为肩部舒展
- `test_set.jsonl:150:意图1` — 把主驾座椅按摩调为腰臀舒缓模式

## `SEAT_VENTILATION_OFF`

- 唯一样本数: **95**
- 三元组: `TURN_OFF + SEAT_VENTILATION + STATE`
- Capability family: `PROJECT_SEAT_VENTILATION_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19575:意图1` — 关闭座椅通风
- `dev_set.jsonl:19638:意图1` — 关闭前排的座椅通风
- `dev_set.jsonl:19977:意图1` — 关闭座椅通风
- `dev_set.jsonl:20436:意图1` — 关闭座椅通风
- `dev_set.jsonl:20490:意图1` — 关闭所有座椅通风

## `SEAT_VENTILATION_ON`

- 唯一样本数: **445**
- 三元组: `TURN_ON + SEAT_VENTILATION + STATE`
- Capability family: `PROJECT_SEAT_VENTILATION_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19226:意图4` — 空调二十二度风速一挡关闭后排车窗打开主驾座椅通风
- `dev_set.jsonl:19231:意图1` — 打开座椅通风
- `dev_set.jsonl:19238:意图5` — 打开全部车窗关闭遮阳帘打开后尾门氛围灯换成红色打开座椅通风
- `dev_set.jsonl:19257:意图1` — 打开前排座椅通风
- `dev_set.jsonl:19300:意图1` — 打开前排座椅通风

## `SEAT_VENTILATION_SET_LEVEL`

- 唯一样本数: **34**
- 三元组: `SET + SEAT_VENTILATION + LEVEL`
- Capability family: `PROJECT_SEAT_VENTILATION_KNOWN_CONTROL`
- VALUE/MODE contract: `SOURCE_LEVEL_OPTIONAL` / `None`

- `test_set.jsonl:1051:意图1` — 座椅通风开到最大挡位
- `test_set.jsonl:240:意图1` — 前排把座椅通风调到最小
- `test_set.jsonl:322:意图1` — 座椅通风调到二挡
- `test_set.jsonl:690:意图1` — 座椅通风调到2档
- `test_set.jsonl:875:意图2` — 座椅通风三挡

## `SEAT_VENTILATION_SET_MODE`

- 唯一样本数: **1**
- 三元组: `SWITCH_MODE + SEAT_VENTILATION + MODE`
- Capability family: `PROJECT_SEAT_VENTILATION_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `KNOWN_SEAT_VENTILATION_SOURCE_MODE`

- `test_set.jsonl:981:意图1` — 座椅通风调到auto

## `SHADE_CLOSE`

- 唯一样本数: **69**
- 三元组: `CLOSE + SHADE + OPENING_STATE`
- Capability family: `PROJECT_SHADE_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19238:意图2` — 打开后尾门
- `dev_set.jsonl:19859:意图2` — 关闭遮阳帘
- `dev_set.jsonl:20482:意图1` — 关闭遮阳帘
- `test_set.jsonl:192:意图2` — 关闭遮阳帘
- `test_set.jsonl:418:意图2` — 关闭遮阳帘

## `SHADE_OPEN`

- 唯一样本数: **115**
- 三元组: `OPEN + SHADE + OPENING_STATE`
- Capability family: `PROJECT_SHADE_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19257:意图2` — 打开遮阳帘
- `dev_set.jsonl:19280:意图1` — 打开遮阳帘
- `dev_set.jsonl:20257:意图2` — 打开遮阳帘
- `dev_set.jsonl:20269:意图2` — 打开遮阳帘
- `dev_set.jsonl:20297:意图2` — 打开全部遮阳帘

## `SHADE_SET_POSITION`

- 唯一样本数: **1**
- 三元组: `ADJUST + SHADE + POSITION`
- Capability family: `PROJECT_SHADE_KNOWN_CONTROL`
- VALUE/MODE contract: `PERCENT_0_100_REQUIRED` / `None`

- `train_set.jsonl:16094:意图1` — 打开一半遮阳帘

## `STEERING_WHEEL_HEATING_OFF`

- 唯一样本数: **19**
- 三元组: `TURN_OFF + STEERING_WHEEL + HEATING_STATE`
- Capability family: `PROJECT_STEERING_WHEEL_HEATING_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19600:意图2` — 关闭方向盘加热
- `dev_set.jsonl:19831:意图2` — 方向盘加热关闭
- `test_set.jsonl:901:意图1` — 关闭方向盘加热
- `test_set.jsonl:95:意图2` — 关闭方向盘加热
- `train_set.jsonl:11350:意图2` — 关闭方向盘加热

## `STEERING_WHEEL_HEATING_ON`

- 唯一样本数: **28**
- 三元组: `TURN_ON + STEERING_WHEEL + HEATING_STATE`
- Capability family: `PROJECT_STEERING_WHEEL_HEATING_KNOWN_CONTROL`
- VALUE/MODE contract: `NONE` / `None`

- `dev_set.jsonl:19733:意图3` — 打开主副驾驶座椅加热和方向盘加热关闭车外提示音
- `test_set.jsonl:1003:意图1` — 打开方向盘加热
- `test_set.jsonl:934:意图2` — 打开方向盘加热
- `train_set.jsonl:11163:意图1` — 打开方向盘加热
- `train_set.jsonl:11456:意图1` — 打开方向盘加热

## Pending candidates

- ADAS candidates not auto-added: **127**
- Other known-control candidates: **1275**

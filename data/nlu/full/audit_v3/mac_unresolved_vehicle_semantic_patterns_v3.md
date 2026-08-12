# MAC 未解析车辆语义模式审计（v3）

未解析 frame occurrence：4627；去重模式：2246。

| 操作 | 对象 | 功能 | 位置类型 | 数值类型 | 模式类型 | 数量 | 示例 | 建议范围 | 候选正式意图 | 可确定 | 原因 |
|---|---|---|---|---|---|---:|---|---|---|---|---|
| 打开 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 196 | 帮我打开自然风设置页面；将全车温度调到二十五度打开AC；空调开至最大打开内循环；空调设为二十五度打开AC；空调温度调到二十四度打开AC | {"已知但不开放": 96, "未知": 97, "正式可执行": 3} | {"PARKING_BRAKE_AUTO_APPLY_ENABLE": 3} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 97} |
| 打开 | None | {"功能": "驻车", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 116 | 打开驻车舒享模式打开前排车窗打开示宽灯；打开位置灯打开驻车舒享；打开驻车舒享关闭所有空调打开示宽灯；关闭氛围灯打开驻车舒享；打开前排车窗打开驻车舒享关闭全车空调 | {"已知但不开放": 115, "未知": 1} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "声音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 92 | 音乐声音大一点导航声音小一点；声音再调小；音乐声音小一点导航声音大一点；笑话调小点声音；声音大一点音乐声音大一点 | {"非控制": 92} | {} | 是 | {} |
| 关闭 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 88 | 关闭内循环打开空调；刚才的声音恢复；关闭山地行驶模式；打开导航音量；关闭强制充电 | {"已知但不开放": 37, "未知": 51} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 51} |
| 调 | None | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 85 | 温度调到二十四风量调到三档；风速调到五挡温度调到二十四度；温度调到二十度风速调到第三挡；打开空调打开座椅通风温度调到二十度风量调到三挡；风速调到三挡温度调到二十二 | {"已知但不开放": 85} | {} | 是 | {} |
| 调节 | None | {"调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 64 | 请播放杨宗纬的歌曲并且将音量调小；音量调低一点然后打开副驾驶座椅按摩；系统音量不够低；综艺音量再小一点；讲话不要这么大声 | {"非控制": 64} | {} | 是 | {} |
| None | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 39 | 我要一键升窗；切换至纯电模式经济模式；极速制冷和座椅通风；关闭所有车窗浅色模式；极速制冷空调开启 | {"未知": 39} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 39} |
| 调节 | None | {"调节内容": "温度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 38 | 风力调大温度降低；风速大一点温度低一点；调小一点温度调高一点；空调风速加大温度调低；温度调高一点关闭主驾车窗 | {"已知但不开放": 38} | {} | 是 | {} |
| 调 | None | {"调节内容": "风量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 32 | 风量调到最大空调调到最亮；空调调至温度最低风量调至最大；温度调到二十四风量调到三档；温度调至最低风量调至最大；打开座椅通风空调调到十六度风量调到最大打开天窗打开所有车窗 | {"已知但不开放": 32} | {} | 是 | {} |
| 调节 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 32 | 风速调到三挡不要对人吹；风向避人吹全车温度调到二十三度；对着我吹；空调调到二十三度不要对着人吹；空调风速调到三挡不要对人吹 | {"已知但不开放": 32} | {} | 是 | {} |
| 打开 | None | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 31 | 关闭前大灯打开小憩模式；关掉空调打开外循环；打开外循环关掉屏幕；关闭空调打开外循环；打开座椅通风打开小憩模式 | {"未知": 9, "已知但不开放": 22} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 9} |
| 调节 | None | {"调节内容": "风量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 29 | 调小点风量；降低风量；风量调小；空调温度调高两度风量小一点；空调温度调到二十度风量调小一点 | {"已知但不开放": 29} | {} | 是 | {} |
| 调节 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 26 | 找到调节导航音量开关并调高10%；电话音量调高10%；设成最小的音量；使导航音量调高百分之三十；导航音量调低30% | {"非控制": 26} | {} | 是 | {} |
| 打开 | None | {} | NONE | NONE | NONE | 25 | 给我将消息中心打开；给我把预碰撞辅助设置界面打开；打开智能驾驶信息；打开电池设置；为我打开通知打电话那个 | {"未知": 25} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 25} |
| 调 | None | {"调节内容": "风量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 24 | 打开空调风量调到二十；风量调到五温度调到十六；关闭全部车窗打开空调制冷风量调到三；打开空调风量调到一；空调温度调到十九度风量调到五 | {"已知但不开放": 24} | {} | 是 | {} |
| 调节 | None | {"调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 23 | 我想要设置到最轻的音量；音量缩小；音量我想体验最弱的；语音音量成合适；语音音量合适 | {"非控制": 23} | {} | 是 | {} |
| 调节 | None | {"调节内容": "声"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 23 | 小点声；电影调大点声；把歌声调小点声；把电台调小点声；小说小声一点 | {"非控制": 23} | {} | 是 | {} |
| 打开 | None | {"对象功能": "通风"} | NONE | NONE | NONE | 22 | 打开通风；关闭空调打开透气模式主驾窗打开百分之三十；通风模式播放音乐；打开通风打开遮阳帘；关掉空调打开通风 | {"未知": 22} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 22} |
| 调节 | None | {"调节内容": "风速"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 22 | 风速大一点空调风速大一点；关闭左前门玻璃关闭天窗风速调小一点；空调温度调低一点风速调大一点；风速大一点温度低一点；风速调低温度调高 | {"已知但不开放": 22} | {} | 是 | {} |
| 调 | None | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 21 | 坦克空调风速调到最高温度调到最低；把温度调到最高把所有温度调到最高；把温度调到最小；温度调至最低风量调至最大；把空调风力调到最大温度调到最低 | {"已知但不开放": 21} | {} | 是 | {} |
| 调节 | None | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 21 | 副驾驶脚部降温；温度调到二十二二十一度全车温度二十一度；全部温度十八度风量最大；全部温度二十度风量最小；全部温度二十八度风量最大 | {"已知但不开放": 21} | {} | 是 | {} |
| 滑动 | 扶手 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 20 | 扶手朝前方滑动；扶手向后面滑动到最后；扶手前方滑动；扶手后边滑动；扶手后面滑动 | {"已知但不开放": 20} | {} | 是 | {} |
| 调节 | 天窗 | {"调节内容": "透光度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 20 | 天窗最大天窗透光值最高；天窗最大天窗透明度最大；天窗最大天窗透光度最高；天窗最亮天窗透明挡位最大；天窗最大天窗透光挡位最高 | {"已知但不开放": 20} | {} | 是 | {} |
| 调节 | 天窗 | {"调节内容": "透光度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 18 | 天窗最亮天窗透光挡位最亮；天窗最透光天幕透光值最大；天窗最亮天窗透明挡位最大；天窗全透；天幕最亮天窗透光度最亮 | {"已知但不开放": 18} | {} | 是 | {} |
| 滑动 | 扶手台 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 17 | 扶手台前滑动；扶手台朝前方滑动；扶手台往前方滑动到最前；扶手台向前滑动；扶手台往前面滑动到最前 | {"已知但不开放": 17} | {} | 是 | {} |
| 移 | 扶手台 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 17 | 扶手台往后面移到最后；扶手台往后边移；扶手台朝前移到最前；扶手台后面移到最后；扶手台朝前移 | {"已知但不开放": 17} | {} | 是 | {} |
| 关闭 | None | {} | NONE | NONE | NONE | 16 | 取消关闭多媒体；关闭语音关闭屏幕；关闭车机；关闭空调关闭设置；关闭通风关闭语音 | {"未知": 16} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 16} |
| 打开 | 后视镜 | {} | NONE | NONE | NONE | 16 | 后视镜打开后视镜然后关闭天窗关闭空调；打开后视镜关闭车窗；打开后视镜下降前排车窗；打开后视镜搜索DJ；打开后视镜加热打开流媒体后视镜 | {"未知": 16} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 16} |
| 查看 | None | {"功能": "查询剩余电量"} | NONE | NONE | NONE | 16 | 查查现在的剩余的电量；现在剩多少电池电量；查看现在的电池电量剩几；我想问一下电量是多少；当前的剩余的电量 | {"非控制": 16} | {} | 是 | {} |
| 调 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 16 | 关闭整车车窗音量调到百分之三十；音量调到百分之八十；音量调百分之五；播放许巍的歌曲音量调到百分之二十；音量调到百分之二十五哪首歌 | {"非控制": 16} | {} | 是 | {} |
| 调 | None | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 16 | 将全车温度调到二十五度打开AC；风向避人吹全车温度调到二十三度；全车温度调到二十三度车内风量调到一挡；全车温度调到十九度风挡调到三挡；空调温度调到二十二度副驾温度调到二十二度 | {"已知但不开放": 16} | {} | 是 | {} |
| 调节 | None | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 16 | 提高车内温度；空调风速两挡温度二十四度；空调调到通风模式温度打到二十四度；把空调风量调至最小温度控制在二十二度；打开空调设置温度为二十七 | {"已知但不开放": 16} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "低速提示音"} | NONE | NONE | NONE | 15 | 关闭低速提示音导航回家；关闭低速提示音屏幕亮度调到最高；关闭低速提示音打开全车窗户；关闭低速提示音打开腾讯视频；关闭低速提示音播放蓝牙音乐 | {"已知但不开放": 15} | {} | 是 | {} |
| 移 | 扶手 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 15 | 扶手向后方移；扶手前方移到最前；扶手向前移；扶手往后面移到最后；扶手移到最后 | {"已知但不开放": 15} | {} | 是 | {} |
| 调 | None | {"调节内容": "风速"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 15 | 把空调调到二十五度把风速调到最低；风速调到最小导航去华士实验中学；全车空调调到二十二点五度风速调到最低；把后排空调温度降低风速调到最大；空调温度调到最低风速调到最高 | {"已知但不开放": 15} | {} | 是 | {} |
| 调节 | None | {"调节内容": "风量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 15 | 风量给我拉满；现在吹高风量可以吗；中等风量；不用那么大的风量中等量就行；风量适中 | {"已知但不开放": 15} | {} | 是 | {} |
| 关掉 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 14 | 关掉弹射起步功能；我想关掉自然风设置页；我要出发了舒享模式关掉；帮我自然风关掉页面；关掉宠物模式 | {"未知": 6, "已知但不开放": 8} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 6} |
| 移动 | 扶手 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 14 | 扶手往后面移动到最后；扶手朝后方移动到最后；扶手朝前面移动；扶手往后边移动到最后；扶手朝后边移动到最后 | {"已知但不开放": 14} | {} | 是 | {} |
| 移动 | 扶手台 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 14 | 后面太挤了请把扶手台向后座移动；扶手台朝前移动；扶手台移动到最后；扶手台前移动到最前；扶手台后面移动 | {"已知但不开放": 14} | {} | 是 | {} |
| 调 | None | {"调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 14 | 将通话音量调到不能再低了；导航音量调至六音乐音量调至十六；关闭车外行人提示音音量调到十六；把音量调到五十八后面的天窗关了然后后视镜调到；播放周杰伦的青花瓷音量调到十三 | {"非控制": 14} | {} | 是 | {} |
| 开启 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 13 | 开启极速制冷播放音乐；动能回收调到中挡然后开启单踏板模式；将自适应调节功能开启；将内循环的运作开启；开启运动模式 | {"已知但不开放": 5, "未知": 7, "正式可执行": 1} | {"PARKING_BRAKE_AUTO_APPLY_ENABLE": 1} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 7} |
| 调节 | None | {"调节内容": "声音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 13 | 声音轻一点；声音还应该再小一些；加点声音；给我设最轻的声音；声音播放大一点音量大一点 | {"非控制": 13} | {} | 是 | {} |
| 调节 | None | {"调节内容": "风量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 13 | 空调温度最低风量最大；全部温度十八度风量最大；全部温度二十度风量最小；全部温度二十八度风量最大；打开空调风量最大温度最低 | {"已知但不开放": 13} | {} | 是 | {} |
| 关闭 | None | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 12 | 取消小憩模式关闭小憩模式；关闭外循环；把通话音量开上；声音给我恢复一下；关闭空调关闭外循环 | {"未知": 5, "已知但不开放": 7} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 切换 | None | {"调节内容": "动力来源"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 12 | 切换纯电模式关闭显示屏；切换到纯电切换到纯电模式你个傻逼；切换至纯电模式播放一首林俊杰的美人鱼；切换至纯电模式经济模式；切换至智能混动模式 | {"未知": 12} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 12} |
| 打开 | None | {"对象功能": "蓝牙"} | NONE | NONE | NONE | 12 | 打开蓝牙打开空调；你的蓝牙打开了没；打开蓝牙开关；座椅通风调小一点儿打开蓝牙；打开控制面板打开蓝牙控制面板 | {"已知但不开放": 12} | {} | 是 | {} |
| 打开 | None | {"调节内容": "动力来源"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 12 | 打开四驱模式打开智能混动关闭氛围灯；打开经济模式打开混动模式；打开座椅通风打开纯电模式；打开标准模式打开智能混动；打开智能混动打开四驱模式 | {"未知": 12} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 12} |
| 回到 | None | {} | NONE | NONE | NONE | 11 | 回到主界面回到桌面；调节副驾车门开启幅度回到主界面打开空调；回到主页打开设置；回到主页放一首谭咏麟的歌；降下前排的车窗打开示宽灯打开驻车舒享回到主页面 | {"未知": 11} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 11} |
| 打开 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 11 | 我想听个跑车发动机启动声；我想听个拖拉机启动声；打开现场音乐会音效；打开音效；打开标准音效 | {"非控制": 11} | {} | 是 | {} |
| 打开 | None | {"对象功能": "热点"} | NONE | NONE | NONE | 11 | 打开热点设置页面；打开两侧座椅加热打开热点打开迎宾打开音乐律动；打开WIFI打开热点；打开热点打开迎宾打开音乐律动打开前排加热；打开两侧座椅加热打开热点打开音乐律动打开迎宾 | {"已知但不开放": 11} | {} | 是 | {} |
| 滑 | 扶手台 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 11 | 扶手台向前方滑到最前；扶手台滑到最前；扶手台前滑；扶手台朝后滑；扶手台朝后方滑 | {"已知但不开放": 11} | {} | 是 | {} |
| 调 | None | {"调节内容": "风速"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 11 | 打开座椅通风风速调到一；风速调到一温度调到二十四；打开空调风速调到一打开喜马拉雅；空调调为制冷模式风速调为二；风速调到二十三度温度调到二十三度 | {"已知但不开放": 11} | {} | 是 | {} |
| 调节 | 天幕 | {"调节内容": "透光度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 11 | 天幕最亮天窗透光度最亮；天幕最亮天幕透明度最大；天窗最大天幕透明挡位最亮；天窗最透光天幕透光值最亮；天幕最亮天窗透光挡位最亮 | {"已知但不开放": 11} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "低速报警"} | NONE | NONE | NONE | 10 | 关闭低速报警关闭空调；关闭低速报警打开所有车窗；关闭空调关闭低速报警；关闭低速报警关闭所有车窗；打开空调关闭低速报警 | {"已知但不开放": 10} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "蓝牙"} | NONE | NONE | NONE | 10 | 关闭蓝牙关闭空调；打开所有车窗关闭声音关闭蓝牙关闭空调打开天窗；关闭热点关闭蓝牙；蓝牙不用了给我关闭接口；关闭蓝牙关闭显示屏 | {"已知但不开放": 10} | {} | 是 | {} |
| 打开 | None | {"调节内容": "摄像头模式"} | NONE | NONE | NONE | 10 | 打开摄像；导航至拍动图模式；拍摄视频；普通录像；普通拍照 | {"未知": 10} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 10} |
| 打开 | 座椅 | {} | NONE | NONE | NONE | 10 | 更改座椅的设置那个页面给我看；座椅该调了；打开座椅设置页面；打开座椅打开前排座椅加热；打开座椅打开车窗除雾 | {"未知": 10} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 10} |
| 调 | None | {"调节内容": "声音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 10 | 你的声音调为五；通话音量和电话铃声音量调到一；把声音调到五；把声音调到二；声音调到三 | {"非控制": 10} | {} | 是 | {} |
| 调节 | 天幕 | {"调节内容": "透光度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 10 | 天窗最透光天幕透光值最大；天幕最亮天幕透明度最大；天窗最透光天幕透光度最高；天窗最亮天幕透光度最大；天窗最亮天幕透明度最大 | {"已知但不开放": 10} | {} | 是 | {} |
| 关闭 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 9 | 让吹脸吹窗功能不要再继续执行了；关闭吹窗吹脚模式；设置吹脸吹窗为不可用状态；关闭吹脸吹脚吹窗；关闭脚部吹风 | {"已知但不开放": 9} | {} | 是 | {} |
| 关闭 | 后视镜 | {} | NONE | NONE | NONE | 9 | 关闭后视镜打开后备箱打开天窗；关闭流媒体后视镜；关闭后视镜翻转；关闭后视镜关闭后排遮阳帘；关闭后视镜座椅加热 | {"未知": 9} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 9} |
| 开开 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 9 | 把扫风模式开开；我要自然风开开；我要自然风开开页面；给我自然风开开设置页面；我想开开自然风设置页 | {"未知": 2, "已知但不开放": 7} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 查看 | None | {"功能": "查询当前音量"} | NONE | NONE | NONE | 9 | 媒体音量是多大；音乐音量是多大；媒体音量是多少；我想看音量；媒体音量现在是多大 | {"非控制": 9} | {} | 是 | {} |
| 调到 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 9 | 播放音乐多媒体音量调到百分之二十；把导航音量调到最小；媒体音量调到10%；播放音乐媒体音量调到百分之四十；我要听向云端然后把媒体音量调到百分之七十 | {"非控制": 9} | {} | 是 | {} |
| 调到 | None | {"调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 9 | 播放一首碎银几两DJ版媒体声音调到最大；语助声音调到最大；通话声音音量调到-20%；电话铃声音量调到最小；电话铃声音量调到50% | {"非控制": 9} | {} | 是 | {} |
| 调节 | None | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 9 | 打开车内空调风量最大温度最低；温度打到25度；打开空调风量最大温度最低；打开后视镜加热温度最高；最高对比度 | {"已知但不开放": 9} | {} | 是 | {} |
| 返回 | None | {} | NONE | NONE | NONE | 9 | 退出爱奇艺返回桌面；小度小度返回桌面；取消导航返回主页；播放音乐返回桌面；返回主菜单 | {"未知": 9} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 9} |
| 关 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 8 | 把自然风关设置页；把自然风关设置页面；给我关起来自动的驻车功能；自然风关页面；我想自然风关页面 | {"已知但不开放": 6, "正式可执行": 1, "未知": 1} | {"PARKING_BRAKE_AUTO_APPLY_DISABLE": 1} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关了 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 8 | 帮我关了自然风设置页面；把洗车模式关了；我要关了自然风页面；自然风关了；我要关了自然风设置页面 | {"已知但不开放": 7, "未知": 1} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "通风"} | NONE | NONE | NONE | 8 | 导航到鲁商松江新城打开座椅通风；导航去公司打开座椅通风；播放蓝牙音乐打开座椅通风；空调调到二十一度同步同时打开座椅通风然后打开音乐让我听下音乐休息会儿IQ；继续播放视频打开座椅通风 | {"已知但不开放": 8} | {} | 是 | {} |
| 查看 | None | {"功能": "查询续航里程"} | NONE | NONE | NONE | 8 | 根据油量计算我还能跑多远；还能驾驶多久；续航里数；查看续驶里程；我还可以行驶的距离 | {"非控制": 8} | {} | 是 | {} |
| 移 | 屏 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 8 | 副驾屏向右边移；副驾屏朝左边移；副驾屏往右移；副驾屏向左移；副驾屏右移 | {"已知但不开放": 8} | {} | 是 | {} |
| 调节 | None | {"调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 8 | 现在的声音不太行转到50%；你的声音调低百分之十；我需要电话通话的声音被调低20%；设置成最高声音；导航播报把它的声音给我削弱20% | {"非控制": 8} | {} | 是 | {} |
| 调节 | None | {"调节内容": "音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 8 | 导航到中西医减小音乐；音乐调高一点；导航声音大一点QQ音乐小一点；关闭导航声音声音播报音乐减小；音乐调低一点 | {"非控制": 8} | {} | 是 | {} |
| 关闭 | None | {"功能": "无线充电"} | NONE | NONE | NONE | 7 | 关闭无线充电关闭所有车窗打开座椅通风；打开座椅加热关闭无线充电；无线充电不要再开着了；关闭无线充电播放蓝牙音乐；关闭无线充电 | {"已知但不开放": 7} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "通风"} | NONE | NONE | NONE | 7 | 关闭通风打开座椅通风；关闭空调关闭通风；关闭通风关闭语音；关闭通风；关闭通风恢复副驾座椅 | {"未知": 7} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 7} |
| 切换 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 7 | 切换驾驶模式为漂移；切换到腰部；切换山地；切换另一种模式自定义吧；切换运动模式打开尾翼 | {"未知": 3, "已知但不开放": 4} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 查看 | None | {"功能": "胎压监测"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 7 | 查一下左后胎压；查看左后轮胎压；查看后轮胎压；查一下右前胎压；查一下右后胎压 | {"非控制": 7} | {} | 是 | {} |
| 滑 | 扶手 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 7 | 帮我把扶手向前滑；扶手朝前面滑到最前；扶手往后边滑；扶手往后滑；扶手后滑到最后 | {"已知但不开放": 7} | {} | 是 | {} |
| 调节 | None | {"调节内容": "风"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 7 | 打开车窗除雾最小风；空调小点风最低风；把空调开到一挡最小的风；设置为二十五度二档风；给用一下强档风 | {"已知但不开放": 7} | {} | 是 | {} |
| 重启 | None | {} | NONE | NONE | NONE | 7 | 重启系统；车机我要重启；给我重启车机；重启；可以重启吗 | {"未知": 7} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 7} |
| 关闭 | None | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 6 | 关闭主驾影院模式；我要关闭主驾极客模式；关闭副驾游戏模式；关闭主驾休息模式；关闭副驾影院模式 | {"未知": 6} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 6} |
| 切换为 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 6 | 切换为普通模式退出运动模式；打开前后排空调并切换为内循环；打开空调切换为内循环；切换为雪地模式；切换为越野模式 | {"未知": 6} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 6} |
| 切换到 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 6 | 切换到舒适模式然后打开座椅按摩；切换到漂移模式；切换到经济模式；导航到石家庄正定国际机场切换到运动模式途经最近的五金店；切换到休憩功能 | {"未知": 6} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 6} |
| 开下 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 6 | 我想开下自然风设置页；我要自然风开下设置页面；帮我把自然风开下页面；我想把自然风开下页面；把自然风开下设置页 | {"未知": 6} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 6} |
| 打开 | HUD | {} | NONE | NONE | NONE | 6 | 导航到家打开HUD；打开车灯打开HUD；屏幕最亮氛围灯最亮打开HUD；导航去公司打开HUD；关闭车窗打开HUD | {"已知但不开放": 6} | {} | 是 | {} |
| 打开 | None | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 6 | 全车静音；打开副驾一键舒适模式；打开主驾休憩模式；打开司机位的极客模式；打开全部一键躺平 | {"未知": 6} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 6} |
| 打开 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 6 | 打开吹玻璃空调吹玻璃；打开吹窗和副驾吹脸吹脚模式；温度调到最低风速调到五挡打开吹脚打开前排座椅通风；打开吹脚模式关闭吹脸；打开对脸吹同时打开对脚吹 | {"已知但不开放": 6} | {} | 是 | {} |
| 打开 | 车窗 | {} | NONE | NONE | NONE | 6 | 播放音乐打开车窗关闭空调；播放音乐打开车窗；弄下来车窗；把天窗和车窗开开；帮我导航南平谷新店帮我打开车窗 | {"未知": 6} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 6} |
| 查看 | None | {"功能": "查询充电时间"} | NONE | NONE | NONE | 6 | 还需要多长时间才能充满；还要多久才能充电充满电量；充电还需要多久能够完全充满；还有多长时间才能使电池完全充满；电量还需多久充满 | {"未知": 6} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 6} |
| 移动 | 屏 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 6 | 副驾屏驾驶员移动；副驾屏朝主驾移动；副驾屏往副驾移动；副驾屏往驾驶员移动；副驾屏朝副驾移动 | {"已知但不开放": 6} | {} | 是 | {} |
| 调整为 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 6 | 给我将导航播报功能调整为极简；帮我把导航播报模式调整为极简；给我把导航播报功能调整为极简；帮我把导航播报功能调整为详细；把驾驶模式调节舒适模式调整为舒适模式 | {"未知": 6} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 6} |
| 选择 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 6 | 音效模式选择剧场；把音效模式选择古典之韵；将音效模式选择流行律动；将音效模式选择古典之韵；将音效模式选择爵士乐章 | {"未知": 6} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 6} |
| 关上 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 5 | 把自然风关上设置页；我想把自然风关上设置页面；把自然风关上设置页面；关上自然风设置页；给我把自然风关上设置页面 | {"已知但不开放": 5} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "车外低速报警"} | NONE | NONE | NONE | 5 | 打开所有车窗打开香氛关闭车外低速报警；关闭车外低速报警打开座椅按摩；导航去公司关闭车外低速报警；关闭车外低速报警打开空调；关闭车外低速报警导航去公司 | {"已知但不开放": 5} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "行人警示音"} | NONE | NONE | NONE | 5 | 关闭行人警示音打开主驾出风口；关闭行人警示音导航到天虹口腔；打开喜马拉雅关闭行人警示音；关闭车灯关闭行人警示音；关闭行人警示音打开空调 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 关闭 | None | {"功能": "驻车", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 5 | 停车的时候不要舒享；屏幕朝向主驾关闭驻车舒享；关闭驻车舒享模式式；模式更改不用停车舒享了；关闭驻车舒享打开后备箱 | {"已知但不开放": 4, "未知": 1} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "热点"} | NONE | NONE | NONE | 5 | 关闭热点关闭蓝牙；打开WIFI关闭热点；关闭热点弹窗；关闭热点打开WIFI；打开蓝牙关闭热点 | {"已知但不开放": 5} | {} | 是 | {} |
| 切换 | 驾驶 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 5 | 驾驶模式切换泥泞路面；切换驾驶模式为四驱模式；切换驾驶模式到山地；切换驾驶模式为舒适；请切换驾驶模式到泥泞 | {"未知": 3, "已知但不开放": 2} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 开启 | None | {} | NONE | NONE | NONE | 5 | 开启汽车设置页面然后播放汪峰的歌；开启液压底盘舒适；把流媒体给设置成开启状态；开启智能语音助理设置页面；帮我把消息中心开启 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 打开 | None | {"对象功能": "通风"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 5 | 打开主驾通风关闭主驾座椅按摩；打开主驾通风副驾驶通风；打开副驾按摩副驾通风；打开主驾通风打开时帮我打开音乐 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 打开 | None | {"功能": "无线充电"} | NONE | NONE | NONE | 5 | 帮我把无线充电开关打开；打开无线充电导航去上班；打开无线充电打开空调；导航去公司打开无线充电；打开无线充电导航到公司 | {"已知但不开放": 5} | {} | 是 | {} |
| 打开 | None | {"功能": "三六零"} | NONE | NONE | NONE | 5 | 打开三六零打开前排车窗打开前排座椅通风；导航去公司打开三六零；打开副驾驶车窗打开三六零；降下前排车窗打开三六零；打开三六零关闭车窗 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 打开 | None | {"对象功能": "WIFI"} | NONE | NONE | NONE | 5 | 打开WIFI关闭热点；打开WIFI打开热点；连接网络打开WIFI；打开WIFI打开那个蓝牙打开热点；关闭热点打开WIFI | {"已知但不开放": 5} | {} | 是 | {} |
| 打开 | None | {"对象功能": "中控锁"} | NONE | NONE | NONE | 5 | 启用中控锁解除；打开中控锁；中控锁锁上；锁上中控锁；中控上锁 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 打开 | 后视镜 | {"对象功能": "加热"} | NONE | NONE | NONE | 5 | 后视镜需要加热下；关闭空调除霜后视镜加热；打开座椅加热后视镜加热；打开方向盘加热后视镜加热；打开反光镜加热后视镜加热 | {"正式可执行": 5} | {"MIRROR_HEATING_ON": 5} | 是 | {} |
| 打开 | 天幕 | {} | NONE | NONE | NONE | 5 | 打开座椅通风打开天幕；关闭车外提示音打开天幕；打开天幕打开遮阳帘；打开天幕关闭副驾屏幕；关下天窗打开天幕 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 打开 | 天窗 | {} | NONE | NONE | NONE | 5 | 播放王琪的歌曲打开天窗打开大灯；导航到五星花园打开天窗；播放音乐打开天窗；可以调节天窗的页面显示出来；播放USB音乐打开天窗 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 打开 | 座椅 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 5 | 打开空调打开主驾座椅家；打开驾驶位置设置页面；副驾座椅一键零重力打开；也把副驾驶的座椅打开；关闭氛围灯打开三排座椅 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 打开 | 空气净化 | {} | NONE | NONE | NONE | 5 | 打开空调打开空气净化；打开空气净化打开香氛系统；打开空气净化打开香氛；打开空气净化温度调到二十四度；把空气净化打开香氛打开 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 播报 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 5 | 我想调调播报帮我把它改成借过提醒；帮我播报跑车发动机启动声音；播报哨声；播报让路感谢；播报发动机声 | {"非控制": 5} | {} | 是 | {} |
| 滑动 | 屏 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 5 | 副驾屏往驾驶员滑动；副驾屏主驾滑动；副驾屏向主驾滑动；副驾屏往主驾滑动；副驾屏朝驾驶员滑动 | {"已知但不开放": 5} | {} | 是 | {} |
| 移 | 屏 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 5 | 屏左移；屏向右边移；屏往右边移；屏朝左边移；屏向右移 | {"已知但不开放": 5} | {} | 是 | {} |
| 调节 | None | {"调节内容": "风速"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 5 | 打开前挡除雾风速最小；空调调到最低温度最大风速；打开除雾风速最小；设定新风风速为四档；空调温度最低风速最大 | {"已知但不开放": 5} | {} | 是 | {} |
| 调节 | None | {"调节内容": "风力"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 5 | 风力调大温度降低；温度调到二十风力稍微大一点；把声音关了风力调大一点；空调温度提高一度风力大一级；空调风力调低一点风力太大 | {"已知但不开放": 5} | {} | 是 | {} |
| 调节 | None | {"调节内容": "声"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 5 | 再把声给它降降；再大点儿声儿；大声一点稍微大一点；给我设成五十的声；再大声一点到里则林 | {"非控制": 5} | {} | 是 | {} |
| 调节 | 仪表盘 | {"调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 5 | 使用最小亮度的仪表；帮我把仪表亮度往弱的那个方向调暗10%；我喜欢看亮度比当前弱10%的仪表；我想试试最大亮度的仪表我能不能看得更清楚；让仪表显示最大亮度 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 调节 | 侧翼 | {"调节内容": "弹性"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 5 | 我需要让主驾的侧翼更紧些；副驾侧翼松一点；主驾侧翼松一点；设置车外灯主驾侧翼紧一点；侧翼太紧主驾的 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 调节 | 坐垫 | {"调节内容": "高度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 5 | 坐垫整体往高上；坐垫整体往低走；坐垫整体往低点；坐垫整体往高上些；坐垫整体往低下些 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 调节 | 天窗 | {"调节内容": "幅度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 5 | 天窗还能再倾斜一点；把天窗倾斜一下；天窗减小；天窗倾斜一点；把天窗倾斜一点 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 调节 | 座椅 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 5 | 座椅位置整体往上点；把座椅往下和往上调一点；把座椅往下座椅按摩；座椅调后一点；座椅朝前 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| 调节 | 座椅 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 5 | 副驾座椅到最前面；副驾座椅往下一点；主驾座椅向下调节；主驾座椅向上调节；副驾座椅向下调节 | {"未知": 5} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 5} |
| None | None | {"功能": "驻车", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 4 | 打开前排车窗驻车舒享；打开示廓灯驻车舒享；开前排车窗驻车舒享；驻车休闲模式 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| None | None | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 4 | 主驾一键躺平；主驾休息模式；副驾智能模式给我整上；副驾扫风 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| None | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 4 | 超级续航模式下车辆驾驶；智能模式下车辆驾驶；岩石模式下车辆驾驶；竞速模式下车辆驾驶 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 不再使用 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 4 | 不再使用吹风吹到脚部的设置；请不再使用吹脸吹脚吹窗模式；不再使用吹窗吹脚模式；不再使用吹脸吹脚吹窗模式 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 关 | 机 | {} | NONE | NONE | NONE | 4 | 请关机有哪些中兴路；关音乐关机；关机；关机关闭方向盘加热 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 关闭 | None | {"功能": "车道辅助"} | NONE | NONE | NONE | 4 | 关闭车道辅助保持；关闭车道偏离抑制；停止车道导向功能；关闭车道偏离警告 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 关闭 | None | {"对象功能": "低速行驶提示音"} | NONE | NONE | NONE | 4 | 关闭低速行驶提示音导航去阳光馨园；关闭低速行驶提示音导航到公司；关闭低速行驶提示音安全带；关闭低速行驶提示音打开空调 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 关闭 | None | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 4 | 关闭前边语音；关闭后排电视；关闭外放多媒体；关闭后排椅背屏右 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 关闭 | 电源 | {} | NONE | NONE | NONE | 4 | 关闭氛围灯关闭电源；关闭车灯关闭电源；关闭电源关闭大灯；关闭空调关闭电源 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 开 | None | {"调节内容": "风速"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 4 | 空调温度开到最低风速开到最大；后排空调温度调到最低风速开到最大；最小速的风速帮我开；风速帮我开成最高 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 开 | None | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 4 | 空调风量开到最大温度开到最低内循环；给我把温度为我开最大；给我把温度为我开最小；空调风量开到四挡挡温度开到最低 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 开 | None | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 4 | 整车风量开到一温度开到三二十三度；开车温度调到二十五度打开驻车舒享；往右吹空调也开到二十四度；温度开到二十二点五度关闭香氛 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 开 | 天窗 | {"调节内容": "幅度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 4 | 天窗略微开一点要自然风；天窗开条缝；天窗朝后张开；天窗开一点点后窗开一点 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 开 | 车窗 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 4 | 开前排车窗打开前排车窗；关闭内循环开右后车窗还有主驾；开前排车窗天窗翘起；开前排车窗驻车舒享 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 恢复 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 4 | 熄灭屏幕恢复主驾座椅；恢复主驾座椅打开透气模式；关闭通风恢复副驾座椅；恢复主驾座椅设置 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 打开 | None | {"对象功能": "除霜"} | NONE | NONE | NONE | 4 | 可以除雾啦挡风玻璃起雾了；挡风玻璃起雾了试一下除雾；我想听离别开除霜；我想除霜 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 打开 | None | {"调节内容": "声音"} | NONE | NONE | NONE | 4 | 打开设置声音页面；打开声音设置页面；打开系统声音页面；打开声音设置页 | {"非控制": 4} | {} | 是 | {} |
| 打开 | None | {"对象功能": "通风"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 4 | 打开前排通风和副驾驶座椅按摩；打开后排通风座椅通风；打开前排通风关闭迎宾；那个视频放打开后排通风 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 打开 | None | {"对象功能": "迎宾"} | NONE | NONE | NONE | 4 | 打开两侧座椅加热打开热点打开迎宾打开音乐律动；打开热点打开迎宾打开音乐律动打开前排加热；打开两侧座椅加热打开热点打开音乐律动打开迎宾；打开热点打开迎宾 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 打开 | 遮阳板 | {} | NONE | NONE | NONE | 4 | 打开所有车窗打开遮阳板打开天窗；打开车门打开遮阳板；打开天窗打开遮阳板；打开遮阳板打开天窗 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 打开 | 香薰 | {} | NONE | NONE | NONE | 4 | 打开香薰播放音乐；温度调到二十五度打开香薰；打开所有车窗打开香薰；打开香薰打开按摩 | {"已知但不开放": 4} | {} | 是 | {} |
| 改 | None | {"调节内容": "动力来源"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 4 | 改为纯电改为混动模式；请改成纯电模式混动模式；改成混动模式纯电优先 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 滑 | 屏 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 4 | 副驾屏主驾滑；副驾屏往副驾滑；副驾屏往主驾滑；设置迎宾欢送灯类型副驾屏滑过来 | {"已知但不开放": 4} | {} | 是 | {} |
| 滑动 | 屏 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 4 | 屏往右滑动；屏往右边滑动；屏左边滑动；屏朝右边滑动 | {"已知但不开放": 4} | {} | 是 | {} |
| 移 | 腿托 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 4 | 副驾腿托上移；主驾腿托前移；主驾腿托后移；副驾腿托下移 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 移动 | 屏 | {"调节内容": "方向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 4 | 屏移动过来；移动屏到这边；屏朝副驾移动；屏往驾驶员移动 | {"未知": 2, "已知但不开放": 2} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设置 | None | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 4 | 空调风量设置为一挡温度设置二十四度；设置强些温度；关闭AC温度设置二十度；把空调的风量调到一挡并把温度设置为二十二度 | {"已知但不开放": 4} | {} | 是 | {} |
| 设置 | None | {"调节内容": "音量"} | NONE | NONE | NONE | 4 | 设置媒体音量；设置音量以适应语音播放；设置系统音量；执行设置导航音量的任务 | {"非控制": 4} | {} | 是 | {} |
| 调到 | None | {"调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 4 | 打开QQ音乐语音音量调到十；把媒体音量调到三十八空调风量调到六；音量调到十五媒体音量调到十五；多媒体音量调到二十三导航音量也调到二十三 | {"非控制": 4} | {} | 是 | {} |
| 调到 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 4 | 帮我调到白天模式；调到夜间模式呃日间模式；调到夜间模式；打开车身稳定系统调到运动模式 | {"未知": 3, "已知但不开放": 1} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调到 | None | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 4 | 副驾也调到二十三点五度；主驾温度也调到二十三度风力调到四挡；主驾驶温度调到二十八度副驾驶调到二十八度；空调温度调到十八度副驾也调到十八度 | {"已知但不开放": 4} | {} | 是 | {} |
| 调整 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 4 | 音效模式调整成典雅旋律；把音效模式调整为爵士乐章；将音效模式调整成典雅旋律；音效模式调整成爵士乐章 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 调节 | None | {"调节内容": "目标电量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 4 | 降低目标电量；目标电量替我降低；目标电量我要调高；目标电量调高 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 调节 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 4 | 让音效模式调节为古典之韵；让音效模式调节古典之韵；把音效模式调节为爵士乐章；音效模式调节成典雅旋律 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 调节 | None | {"调节内容": "风"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 4 | 嗯风调低一点空调调低一点；加大出风；大风一点；风大一点对着我吹 | {"已知但不开放": 4} | {} | 是 | {} |
| 调节 | None | {"调节内容": "风向"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 4 | 主驾避人吹；主驾别吹脸；主驾对人吹副驾避人吹 | {"已知但不开放": 4} | {} | 是 | {} |
| 调节 | 天幕 | {"调节内容": "透光度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 4 | 减少天幕透光度；增加天幕透光度；天幕透光度小一点；天幕透光度低一点 | {"已知但不开放": 4} | {} | 是 | {} |
| 调节 | 座椅 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 4 | 主驾座椅向中音调节到最终；打开驾驶位位置调节；副驾座椅肩部位置调节至10%；我想调一下主驾座椅的参数谢谢 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 调节 | 整车 | {"调节内容": "亮度"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 4 | 整车背光亮度调到最低；整车背光调到最小亮度；整车背光亮度降低一个档位；整车背光亮度调到最高 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 调节 | 麦克风 | {"调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 4 | 麦克风小点儿声；调小麦克风音量；把麦克风音量调大；麦克风大点儿声 | {"非控制": 4} | {} | 是 | {} |
| 转换成 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 4 | 让音效模式转换成古典之韵；将音效模式转换成古典之韵；把音效模式转换成流行律动；把音效模式转换成古典之韵 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 进入 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 4 | 我需要进入到自定义模式；进入自由模式；进入观影模式；进入休憩功能 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| 退出 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 4 | 切换为普通模式退出运动模式；退出游戏；退出一键观影；退出休息模式休息模式 | {"未知": 4} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 4} |
| None | None | {} | NONE | NONE | NONE | 3 | 现在要调整能量回收等级进设置界面；设置流媒体把流媒体后视镜里面的图像设置的大一些；我想重启一下 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关上 | None | {"对象功能": "蓝牙"} | NONE | NONE | NONE | 3 | 蓝牙现在关上了吗呀；蓝牙关上了没呢；你现在的蓝牙关上了吗 | {"已知但不开放": 3} | {} | 是 | {} |
| 关掉 | None | {"对象功能": "蓝牙"} | NONE | NONE | NONE | 3 | 现在的蓝牙是不是关掉啊；关掉热点关掉蓝牙；关掉蓝牙设置界面 | {"已知但不开放": 3} | {} | 是 | {} |
| 关闭 | None | {"调节内容": "摄像头模式"} | NONE | NONE | NONE | 3 | 关闭前视记录仪录音；关闭录音功能；关闭前视记录仪录像 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | None | {"调节内容": "风向"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 3 | 关闭后排空调关闭副驾吹头；关闭副驾吹脚；打开主驾吹脚关闭副驾吹脸 | {"已知但不开放": 3} | {} | 是 | {} |
| 关闭 | None | {"调节内容": "亮度"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 3 | 关闭自动亮度设置；自动亮度调节关闭；自动亮度开关关闭 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | None | {"功能": "行人提示音", "子功能": "行人提示音"} | NONE | NONE | NONE | 3 | 播放音乐关闭行人提示音；关闭行人提示音；关闭行人提示音打开遮阳帘 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | None | {"对象功能": "儿童锁"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 3 | 关闭左边的儿童锁关闭右边的儿童锁；关闭右边儿童锁 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | None | {"对象功能": "车外提示音"} | NONE | NONE | NONE | 3 | 关闭车外提示音打开天幕；关闭车外提示音打开所有遮阳帘；关闭车外提示音打开座椅通风 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | None | {"对象功能": "显示"} | NONE | NONE | NONE | 3 | 关闭显示页面；关闭显示系统设置；显示页关闭 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | None | {"功能": "前向辅助", "子功能": "前向碰撞预警"} | NONE | NONE | NONE | 3 | 设置前向碰撞预警在关闭状态；把前向碰撞预警改为关闭；关闭前向碰撞预警 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | 中控 | {} | NONE | NONE | NONE | 3 | 中控息屏副驾息屏；副驾息屏中控息屏；中控熄屏 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | 副屏 | {} | NONE | NONE | NONE | 3 | 打开座椅通风关闭副屏；关闭副屏关闭所有屏幕；关闭大灯关闭副屏 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | 副驾屏 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 3 | 关闭屏幕关闭副驾屏；关闭副驾屏来首歌听听；关闭中控屏关闭副驾屏 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | 天幕 | {} | NONE | NONE | NONE | 3 | 关闭天窗关闭天幕；关闭天幕空调温度调到最低；关闭方向盘加热关闭天幕 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | 天窗 | {"调节内容": "幅度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 3 | 天窗彻底合上；天窗帮我往前移动一点；天窗开太大 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 关闭 | 智能儿童座椅 | {"对象功能": "通风", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 3 | 退出智能儿童座椅自然通风；智能儿童座椅关闭自然风；关闭智能儿童座椅自然通风 | {"未知": 2, "已知但不开放": 1} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | 门 | {"调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 3 | 帮我关闭前排门手动开；我想关闭前排门手动开；关闭后排门手动开 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 切换 | None | {"对象功能": "续航", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 3 | 切换续航模式为标准模式；续航模式切换为动态模式；续航模式切换为标准续航 | {"已知但不开放": 2, "未知": 1} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | 驾驶 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 3 | 驾驶模式切换为草地模式；驾驶模式切换为纯电；驾驶模式切换为超级运动模式 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 取消 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 3 | 取消媒体静音；取消静音模式；取消通话声音音量静音 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 取消 | None | {"功能": "全景环视"} | NONE | NONE | NONE | 3 | 请给全景环视取消；请把全景环视取消；我想把全景环视取消 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 复位 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 3 | 座椅复位所有座椅复位；全部座椅复位打开吸顶屏；打开三排座椅复位 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 开 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 3 | 自然风开设置页面；给我把自然风开页面；自然风开页面 | {"已知但不开放": 3} | {} | 是 | {} |
| 开启 | None | {"功能": "驻车", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 3 | 开启前排车窗开启驻车舒享；关闭空调开启驻车舒享；开启驻车舒享打开空调 | {"已知但不开放": 3} | {} | 是 | {} |
| 开启 | None | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 3 | 这个带我去恐龙园开启外循环；开启外循环风量调到一档；温度二十二度开启外循环 | {"已知但不开放": 3} | {} | 是 | {} |
| 开启 | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 3 | 开启漂移驾驶模式；开启泥泞驾驶模式；开启雪天驾驶模式 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | None | {"调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 3 | 打开前排影院模式；打开后排腰部调节界面；打开右侧扫风模式 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | None | {"对象功能": "除霜"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 3 | 我要开车了做好后除霜；给我除下后车窗上的雾气；打开后视镜加热和前挡风除霜 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | None | {"功能": "盲区预警"} | NONE | NONE | NONE | 3 | 打开盲区预警的设置窗口给我设置；打开盲区预警；打开座椅加热打开方向盘加热打开空调打开盲区预警 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | None | {"调节内容": "风向"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 3 | 打开吹窗和副驾吹脸吹脚模式；打开主驾吹脚关闭副驾吹脸；打开副驾吹脸不用吹脚 | {"已知但不开放": 3} | {} | 是 | {} |
| 打开 | None | {"对象功能": "儿童锁"} | NONE | NONE | NONE | 3 | 儿童锁给我打开；给我打开儿童锁；打开儿童锁自动上锁 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | 充电口 | {} | NONE | NONE | NONE | 3 | 打开充电口打开后备箱；打开充电口关闭空调；打开后备箱打开充电口 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | 冰箱 | {} | NONE | NONE | NONE | 3 | 打开冰箱调到零度；空调打开成自动模式打开冰箱；打开冰箱电源打开冰箱 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | 后视镜 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 3 | 我看看设置右后视镜的页面；请帮我打开右后视镜设置页面；更改左后视镜的设置那个页面给我看 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | 吸顶屏 | {} | NONE | NONE | NONE | 3 | 打开全车遮阳帘打开吸顶屏；打开前后遮阳帘打开示廓灯打开吸顶屏；全部座椅复位打开吸顶屏 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | 尾翼 | {} | NONE | NONE | NONE | 3 | 打开尾翼打开高德地图；切换运动模式打开尾翼；打开尾翼后视镜内循环 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | 座椅 | {"对象功能": "通风"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 3 | 温度调到二十度打开前排通风座椅；后排座椅给我打开通风的出口；解开一下前排座椅出风的开关 | {"已知但不开放": 3} | {} | 是 | {} |
| 打开 | 座椅 | {"对象功能": "律动"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 3 | 打开主驾座椅律动；打开全车座椅律动再帮我播放一首红色高跟鞋；关闭所有车窗打开空调放一首世界赠予我的打开全车座椅律动 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | 座椅 | {"对象功能": "通风"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 3 | 导航到茶山镇巡警大队打开全车座椅通风；播放蓝牙音乐打开主驾座椅通风；放首歌副驾座椅通风 | {"已知但不开放": 3} | {} | 是 | {} |
| 打开 | 玻璃 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 3 | 打开驻车舒享打开前排玻璃；打开驻车舒享模式打开前排玻璃；关闭遮阳帘打开前排玻璃 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | 窗 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 3 | 打开驻车舒享打开前排窗；打开左前窗打开右后窗 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 打开 | 门锁 | {} | NONE | NONE | NONE | 3 | 打开锁门后视镜后视镜自动折叠；车辆锁车后空调继续保持制冷；车辆锁上 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 改为 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 3 | 帮我把导航播报模式改为详细；空调前排空调温度上升到二十六度空调风速降为一挡改为内循环；改为经济模式音量调小一点 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 改变 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 3 | 将音效模式改变古典之韵；音效模式改变流行律动；把音效模式改变爵士乐章 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 查看 | None | {"功能": "查询轮胎状态"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 3 | 显示左前轮胎状态；当前前侧轮胎怎么样；左前车辆轮胎状态 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 查看 | None | {"功能": "保养"} | NONE | NONE | NONE | 3 | 还有多久需要保养；我的车多久需要保养；什么时候可以去保养 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 查看 | None | {"功能": "胎压监测"} | NONE | NONE | NONE | 3 | 查看胎压状态；打开座椅通风显示胎压监测；打开轮胎胎压显示 | {"非控制": 3} | {} | 是 | {} |
| 滑 | 屏 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 3 | 屏朝左滑；屏右边滑；屏往左滑 | {"已知但不开放": 3} | {} | 是 | {} |
| 滑 | 屏 | {"调节内容": "方向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 3 | 屏副驾滑；屏驾驶员滑；屏往主驾滑 | {"已知但不开放": 3} | {} | 是 | {} |
| 移 | 屏 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 3 | 副驾屏往主驾移；副驾屏往驾驶员移；副驾屏向副驾移 | {"已知但不开放": 3} | {} | 是 | {} |
| 移动 | 屏 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 3 | 副驾屏朝左移动；副驾屏左边移动；副驾屏往左移动 | {"已知但不开放": 3} | {} | 是 | {} |
| 移动 | 屏 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 3 | 屏向右移动；屏往右移动；屏向左移动 | {"已知但不开放": 3} | {} | 是 | {} |
| 设 | None | {"调节内容": "音量"} | NONE | NUMBER | NONE | 3 | 将有声书音量设为8；语音助手音量设为10；把消息音量设为5 | {"非控制": 3} | {} | 是 | {} |
| 设置 | None | {} | NONE | NONE | NONE | 3 | 设置语音配置；开始进行铃声设置；这个来电铃声太吵了帮我设置一下 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 设置 | None | {"功能": "驻车", "调节内容": "时长"} | NONE | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | 3 | 设置驻车舒享时间为两个半小时；设置驻车舒享半小时；设置驻车舒享时间为二点五小时 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 设置为 | None | {"功能": "智慧巡航", "调节内容": "车速", "子功能": "限速偏移"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 3 | 限速偏移设置为10千米每小时；限速偏移设置为负10公里每小时；限速偏移设置为百分之三十 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 设置为 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 3 | 给我将导航播报功能设置为详细；给我将导航播报模式设置为极简；智慧导航语音播报设置为简洁 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调 | None | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 3 | 全车温度调到最低风速调到三挡打开驻车舒享；把温度调到最高把所有温度调到最高；全车温度调到最高关闭AC打开内循环 | {"已知但不开放": 3} | {} | 是 | {} |
| 调 | None | {"调节内容": "风力"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 3 | 空调温度调到最低风力调到最高；空调温度调到最低风力调到最大；空调打开内循环风力调到最大 | {"已知但不开放": 3} | {} | 是 | {} |
| 调 | None | {"调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 3 | 把声音调到最大听歌的声音；声音调最高；声音调到最高 | {"非控制": 3} | {} | 是 | {} |
| 调 | 仪表 | {"调节内容": "亮度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 3 | 仪表调到最亮；仪表亮度调到中间值；仪表调到最亮中控屏调到最亮 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调到 | None | {"调节内容": "模式"} | NONE | QUANTIFIED_OR_LEVEL | TEXT_ENUM_OR_OTHER | 3 | 热风调到最低；冷风调到最低；制热调到最高档 | {"未知": 2, "已知但不开放": 1} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调到 | 座椅 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 3 | 设置倒车雷达声音地图最小主驾座椅调到最后；主驾座椅调到最前靠背调到最后；主驾座椅调到最后面靠背调到最后面 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调到 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 3 | 把主驾的座椅记忆调到驾驶习惯；把主驾座椅调到位置一关掉空调；关闭后排车窗调到主驾坐姿一关闭副驾车窗 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调节 | None | {} | NONE | QUANTIFIED_OR_LEVEL | NONE | 3 | 烟机最高的档位我需要；最高的档位我需要；对比度调成百分之六十 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调节 | None | {"调节内容": "亮度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 3 | 流媒体亮度调高一点；降小一点亮度；降小亮度 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调节 | None | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 3 | 副驾温度调高一度主驾调低一度；把驾驶员背部温度降低 | {"已知但不开放": 3} | {} | 是 | {} |
| 调节 | None | {"调节内容": "系统音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 3 | 调高系统音量；调低系统音量；调大系统音量 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调节 | None | {"调节内容": "亮度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 3 | 把流媒体的亮度设的稍微亮一点；流媒体的亮度把它稍微改的亮一些；多媒体屏亮一点 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调节 | None | {} | NONE | TEXT_ENUM_OR_OTHER | NONE | 3 | 把音乐的歌声唱高一点我听不见了；还没达到我需要的高度；再强一点 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调节 | None | {"调节内容": "音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 3 | 我现在需要对系统提示音进行设置改为中；将语音帮我轻一点；我需要中等提示音改成它 | {"非控制": 3} | {} | 是 | {} |
| 调节 | 侧翼 | {"调节内容": "弹性"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 3 | 右后侧翼紧一点；后排侧翼紧一点；左后侧翼紧一点 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调节 | 大灯 | {"调节内容": "高度", "车外灯类型": "大灯"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 3 | 大灯高度再高一点；不要调低大灯高度；别调低大灯高度 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调节 | 悬架 | {"调节内容": "高度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 3 | 悬架调节低一点；降低悬架高度；调节悬架高度为非常高 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 调节 | 扶手 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 3 | 把扶手往后推点；后面太挤把扶手往后面；扶手到最后 | {"已知但不开放": 3} | {} | 是 | {} |
| 调节 | 空气净化 | {} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 3 | 帮我把空气净化调大些；我要空气净化调小；把空气净化调大些 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 连接 | None | {"对象功能": "蓝牙"} | NONE | NONE | NONE | 3 | 打开蓝牙的连接；蓝牙连接；开启蓝牙连接 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 退出 | None | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 3 | 退出主驾影院模式；退出副驾游戏模式；退出主驾游戏模式 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 退出 | None | {} | NONE | NONE | NONE | 3 | 关闭导航退出导航返回主页；帮我退出一下电台；关闭导航退出导航结束导航 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| 选择 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 3 | 主驾手动记忆选择二；副驾座椅记忆选择为副驾位；主驾座椅记忆选择为备用位 | {"未知": 3} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 3} |
| None | None | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 2 | 外循环；极速降低温度 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| None | None | {"调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 2 | 左后扫风；后排扫风 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| None | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 副驾驶座椅恢复原位；打开副驾座椅复位 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| None | 车窗 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 车窗开百分之三十左右车窗；右后车窗和主驾车窗都可以再往上收一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 下降 | 车窗 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 打开后视镜下降前排车窗；下降前排车窗打开驻车舒享模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 停止 | 后视镜 | {"对象功能": "除霜"} | NONE | NONE | NONE | 2 | 停止后视镜除霜；后视镜除霜停止 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关 | 座椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 2 | 可以关加热了我这个座椅；座椅可以关加热功能了 | {"已知但不开放": 2} | {} | 是 | {} |
| 关下 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 给我把自然风关下设置页面；关下自然风设置页面 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "伴我回家"} | NONE | NONE | NONE | 2 | 停止运行伴我回家照明系统；不是特别需要伴我回家照明了 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 2 | 关闭雅马哈声场；关闭雅马哈声场效果 | {"非控制": 2} | {} | 是 | {} |
| 关闭 | None | {"功能": "来电语音播报"} | NONE | NONE | NONE | 2 | 关闭来电语音播报关闭开机动画音乐；关闭来电语音播报 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"调节内容": "模式"} | NONE | NONE | NONE | 2 | 把现在运行的模式帮我关闭；把现在运行的模式关闭 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "风挡加热"} | NONE | NONE | NONE | 2 | 切断车窗加热；车窗加热不必要了 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "背光联动"} | NONE | NONE | NONE | 2 | 关闭背光联动；请为背光联动开关设置关闭状态 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "零重力"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 关闭左侧右侧零重力 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"功能": "智慧巡航"} | NONE | NONE | NONE | 2 | 替我把巡航恢复；给我将巡航恢复 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"功能": "盲区预警"} | NONE | NONE | NONE | 2 | 盲区预警这个功能可以关闭了；我现在不需要盲区预警提醒我 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "儿童锁"} | NONE | NONE | NONE | 2 | 把儿童锁设为关闭状态；儿童锁键为我关闭 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "负离子净化"} | NONE | NONE | NONE | 2 | 关闭负离子净化；关闭负离子净化关闭空调 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"调节内容": "能量回收"} | NONE | NONE | NONE | 2 | 停用能量再生模式；停用车辆动能再生系统 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "加热"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 关闭遮阳帘关闭副驾加热关闭副驾车窗；关闭全车颈枕加热 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "加热"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 关闭右侧颈枕加热；关闭前排加热座椅加热 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "低速提醒"} | NONE | NONE | NONE | 2 | 关闭空调关闭低速提醒；关闭低速提醒打开中国之声 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"功能": "生命监测"} | NONE | NONE | NONE | 2 | 生命监测关闭；关闭生命监测 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "短升短降"} | NONE | NONE | NONE | 2 | 短升短降关闭；关闭短升短降 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"功能": "关闭行人提", "子功能": "行人安全辅助"} | NONE | NONE | NONE | 2 | 关闭氛围灯关闭行人提示；打开示宽灯关闭行人提示 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"调节内容": "动力来源"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 关闭混动模式；关闭智能能源设置 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "通风"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 关闭空调关闭所有通风；关闭全车通风打开全车空调 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "低速警示音"} | NONE | NONE | NONE | 2 | 关闭低速警示音打开座椅按摩；关闭低速警示音打开扫风模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "低速提示"} | NONE | NONE | NONE | 2 | 关闭低速提示打开主驾驶按摩；关闭低速提示导航到家 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"功能": "自动启停"} | NONE | NONE | NONE | 2 | 关闭自动启停关闭紧急制动；发动机的自动启停功能不需要了 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "迎宾"} | NONE | NONE | NONE | 2 | 打开前排通风关闭迎宾；打开热点关闭迎宾 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | None | {"对象功能": "个人热点"} | NONE | NONE | NONE | 2 | 个人热点关闭；关闭个人热点 | {"已知但不开放": 2} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "低速报警音"} | NONE | NONE | NONE | 2 | 关闭低速报警音屏幕自动调节亮度；关闭低速报警音关闭空调 | {"已知但不开放": 2} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "WIFI"} | NONE | NONE | NONE | 2 | 关闭wifi调节；关闭蓝牙关闭WIFI | {"已知但不开放": 2} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "风扇"} | NONE | NONE | NONE | 2 | 把风扇关闭；关闭空调关闭风扇打开座椅通风 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | 中控大屏 | {} | NONE | NONE | NONE | 2 | 关闭中控大屏和所有氛围灯；关闭中控大屏关闭所有氛围灯 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | 大屏 | {} | NONE | NONE | NONE | 2 | 关闭空调关闭大屏；关闭大灯关闭大屏 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | 安全带 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 关闭后排未系安全带提醒音效；关闭后排安全带提醒 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | 屏 | {"对象功能": "保"} | NONE | NONE | NONE | 2 | 关闭屏保；关闭屏保设置 | {"已知但不开放": 2} | {} | 是 | {} |
| 关闭 | 座椅 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 关闭后排座椅扶手箱崎视频；关闭后排座椅关闭后排座椅通风 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | 座椅 | {} | NONE | NONE | NONE | 2 | 关闭座椅关闭空调；关闭座椅关闭座椅震动 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | 电动门 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 关闭左后电动门；关闭右前电动门 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | 车窗 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 导航去保利凯旋公馆把所有的车窗都关闭；打开主驾驶座椅按摩播放音乐关闭副驾驶车窗 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 关闭 | 遮阳板 | {} | NONE | NONE | NONE | 2 | 关闭遮阳板播放音乐；关闭天窗关闭遮阳板 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 切换 | None | {"对象功能": "息屏", "调节内容": "时长"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 2 | 副驾息屏时间切换两分钟；副驾息屏时间切换十分钟 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 切换 | None | {"调节内容": "温度单位"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 我要切换温度为华氏度；温度为华氏度切换 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 切换 | None | {} | NONE | NONE | NONE | 2 | 我不想用这个铃声了；铃声目录在那你选一个 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 切换 | None | {"调节内容": "摄像头模式"} | NONE | NONE | NONE | 2 | 切换录视频；切换延时摄影 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 切换 | 头枕音响 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 切换头枕音响为私享模式；切换头枕音响为共享 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 切换 | 整车 | {"调节内容": "模式"} | NONE | NONE | NONE | 2 | 动力模式切换到纯电驾驶模式切换到标准；切换驾驶模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 切换成 | 开车模式 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 开车模式切换成运动模式；开车模式切换成竞速模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 加载 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 加载主驾坐姿1；加载副驾坐姿2 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 升起 | 车窗 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 升起所有车窗打开天窗；升起主驾驶车窗风速调到三挡 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 取消 | None | {"对象功能": "除雾", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 取消自动除雾系统；让自动除雾取消 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 变为 | 汽车由普通模式 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 汽车由普通模式变为岩石模式；汽车由普通模式变为漂移模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 启动 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 自动驻车制动启动；启动自动模式系统 | {"正式可执行": 1, "未知": 1} | {"PARKING_BRAKE_AUTO_APPLY_ENABLE": 1} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | 车载儿童座椅 | {"对象功能": "通风", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 车载儿童座椅启动自然风；车载儿童座椅启动自然通风 | {"已知但不开放": 1, "未知": 1} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 声 | None | {"调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 声音不是很合适再大10%；声音向上调整10% | {"非控制": 2} | {} | 是 | {} |
| 复位 | 座椅 | {"调节内容": "座椅记忆位置"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 打开二排右座椅复位；打开三排左座椅复位 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 展示 | None | {"功能": "查询剩余电量"} | NONE | NONE | NONE | 2 | 我们来看一下剩余电量；电池的状态如何 | {"非控制": 2} | {} | 是 | {} |
| 延长 | None | {"调节内容": "时长"} | NONE | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | 2 | 现在延长小憩模式二十分钟；快点延长小憩模式二十分钟 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 开 | None | {"调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 为我开最大声音；声音开到40% | {"非控制": 2} | {} | 是 | {} |
| 开 | None | {"对象功能": "蓝牙"} | NONE | NONE | NONE | 2 | 你蓝牙开没开；你现在的蓝牙开了没 | {"已知但不开放": 2} | {} | 是 | {} |
| 开下 | None | {"功能": "座舱恒温"} | NONE | NONE | NONE | 2 | 我要开下座舱恒温；想要开下座舱恒温 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 开下 | 门 | {"调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 2 | 开下后排门手动开；帮我开下前门手动模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 开个 | 窗户 | {} | NONE | NONE | NONE | 2 | 开个窗户；请给我开个窗户 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 开启 | None | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 2 | 开启副驾游戏模式；开启主驾影院模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 开启 | None | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 打开后车门开启上限设置页面；打开前车门开启上限设置页面 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 开启 | None | {"功能": "前向辅助", "子功能": "后方侧向交通辅助"} | NONE | NONE | NONE | 2 | 将后方侧向交通辅助调至开启状态；调整后方侧向交通辅助为开启 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 开启 | None | {"调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 2 | 开启前排游戏模式；开启前排休憩模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 开始 | None | {"调节内容": "摄像头模式"} | NONE | NONE | NONE | 2 | 开始录像打开前窗户；打开车内摄像头然后开始录制 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 开开 | None | {"调节内容": "音量调节"} | NONE | NONE | NONE | 2 | 语音音量调节页面开开；媒体音量调节页面开开 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 开开 | 空气净化器 | {} | NONE | NONE | NONE | 2 | 把空气净化器开开；空气净化器赶紧把它开关给开开 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"功能": "前向辅助", "调节内容": "距离", "子功能": "前向碰撞预警"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 打开中等距离前向碰撞预警页面；打开中等距离前向碰撞预警 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"调节内容": "风向"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 关掉迎面吹风打开脚下吹风；打开脚下吹风 | {"已知但不开放": 2} | {} | 是 | {} |
| 打开 | None | {"功能": "声浪模拟"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 打开内部声浪模拟界面；内部声浪模拟界面打开 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"调节内容": "视图"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 打开双后视；打开右前视角 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"功能": "停车", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 打开停车舒享模式打开位置灯打开前排车窗；打开停车舒享模式打开前排车窗 | {"已知但不开放": 2} | {} | 是 | {} |
| 打开 | None | {"调节内容": "里程单位"} | NONE | NONE | NONE | 2 | 我要看一下里程单位设置页面打开它；打开里程单位设置页面以便我可以查看之前的设置 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"调节内容": "视图"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 打开广角视图；打开尾舱透视 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"功能": "人脸摄像头"} | NONE | NONE | NONE | 2 | 打开人脸摄像头设置页面；打开人脸摄像头设置 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"调节内容": "能量回收"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 能量回收模式打开舒适模式；能量回收自动模式可以打开了 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"调节内容": "风"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 打开最低速风；最大风打开 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"对象功能": "按键音"} | NONE | NONE | NONE | 2 | 打开系统按键音；按键音设置打开 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"对象功能": "加热"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 打开智能联动打开全车加热；打开按摩打开全车加热 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"对象功能": "同步"} | NONE | NONE | NONE | 2 | 打开气候同步；温度调至二十二度打开同步 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"功能": "侧后辅助", "子功能": "后向碰撞减缓"} | NONE | NONE | NONE | 2 | 把后向碰撞减缓调节为可用；打开后向碰撞减缓 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"调节内容": "风速"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 打开中等速的风速；打开极速风速 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"调节内容": "驱动模式"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 驱动模式打开混动；驱动模式打开强制纯电 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"功能": "驻车"} | NONE | NONE | NONE | 2 | 打开前排车窗打开驻车；打开驻车舒享打开驻车 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"对象功能": "儿童锁"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 打开右边儿童锁；左边有儿童把左边儿童锁打开吧 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"对象功能": "儿童安全锁"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 打开右侧儿童安全锁；请打开后排儿童安全锁 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 空调制冷打开后排有点热；打开后排电视打开空调 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"功能": "声浪模拟"} | NONE | NONE | NONE | 2 | 打开声浪模拟；我想要打开声浪模拟 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | None | {"对象功能": "手机投屏"} | NONE | NONE | NONE | 2 | 请帮我打开手机投屏；我想打开手机投屏 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 充电口盖 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 打开后面的充电口盖；打开前充电口盖 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 充电枪锁 | {"对象功能": "慢充"} | NONE | NONE | NONE | 2 | 关闭解锁慢充枪开关；关闭解锁慢充枪 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 冰箱 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 打开后排冰箱设置；后面冰箱打开 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 冰箱电源 | {} | NONE | NONE | NONE | 2 | 打开冰箱电源调到负二度；打开冰箱电源打开冰箱 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 反光镜 | {"对象功能": "加热"} | NONE | NONE | NONE | 2 | 打开反光镜加热后视镜加热；播放音乐打开反光镜加热 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 吸顶屏 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 打开前后遮阳帘打开后排吸顶屏打开全车车窗；打开全车遮阳帘打开后排吸顶屏 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 屏 | {"对象功能": "保"} | NONE | NONE | NONE | 2 | 打开屏保设置；打开屏保 | {"已知但不开放": 2} | {} | 是 | {} |
| 打开 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 2 | 主驾打开一键复位；主驾打开一键躺平 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 座椅 | {"对象功能": "放直"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 主副驾座椅放直然后随机播放音乐 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 座椅 | {"对象功能": "零重力"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 打开副驾零重力座椅模式；打开副驾零重力座椅 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 座椅 | {"对象功能": "律动"} | NONE | NONE | NONE | 2 | 打开座椅律动把空调温度调到二十六度；打开座椅按摩打开座椅律动 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 座椅 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 打开我的座椅制冷；打开座椅一键成床 | {"已知但不开放": 1, "未知": 1} | {} | 部分 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 滑门 | {} | NONE | NONE | NONE | 2 | 打开后备箱打开侧滑门；打开侧滑门关闭侧滑门 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 电动滑门 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 打开左侧电动滑门设置页面；打开左侧电动滑门控制页面 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 窗帘 | {"调节内容": "幅度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 窗帘打开到百分之三十；窗帘打开一半了吗 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 车窗 | {"对象功能": "通风"} | NONE | NONE | NONE | 2 | 车窗透气一下；车窗通风接着导航回家 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 车窗 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 播放音乐打开所有车窗；打开主驾车窗副驾车窗后排车窗 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 车载智能儿童座椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 2 | 车载智能儿童座椅打开加热；加热车载智能儿童座椅 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 门 | {"调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 2 | 打开后排门手动开；我想打开后排门手动开 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 打开 | 雾灯 | {"车外灯类型": "雾灯"} | NONE | NONE | NONE | 2 | 我现在需要雾灯；打开尾翼雾灯后视镜内容 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 换一下 | 车门 | {"调节内容": "开合度"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 换一下副驾车门的开合度；换一下主驾车门的开合度 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 播报一下 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 2 | 播报一下斑马线礼让可以吗；播报一下拖拉机启动声音可以吗 | {"非控制": 2} | {} | 是 | {} |
| 播放 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 2 | 播放斑马线礼让；播放猫叫 | {"非控制": 2} | {} | 是 | {} |
| 改为 | None | {"对象功能": "通风"} | NONE | NONE | NONE | 2 | 把空调关掉改为通风；空调调至二十三度改为通风模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 改变为 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 2 | 让音效模式改变为爵士乐章；将音效模式改变为爵士乐章 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 查看 | None | {"功能": "查询轮胎状态"} | NONE | NONE | NONE | 2 | 轮胎状况怎么样；当前轮胎状态正常吗 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 查看 | None | {"功能": "胎压"} | NONE | NONE | NONE | 2 | 查看胎压状况；显示胎压打开个人中心 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 查看 | None | {"功能": "查看胎压"} | NONE | NONE | NONE | 2 | 打开雾灯查看胎压；请查看胎压跟那个到成都 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 查看 | None | {"功能": "胎压"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 显示右中胎压；显示左中胎压 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 查看 | None | {"调节内容": "充电限值"} | NONE | NONE | NONE | 2 | 充电限值是多少；我的充电限制 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 查看 | None | {"功能": "汽车保养"} | NONE | NONE | NONE | 2 | 把车的保养信息播放一下；我要看车的保养信息 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 查看 | None | {"功能": "轮胎压怎么样"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 右后轮胎压怎么样；右前轮胎压怎么样 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 查看 | None | {"功能": "轮胎胎压如何"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 前侧轮胎胎压如何；右后轮胎胎压如何 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 滑 | 屏 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 副驾屏往左滑；副驾屏右滑 | {"已知但不开放": 2} | {} | 是 | {} |
| 滑 | 座椅 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 座椅下滑；座椅朝前面滑 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 滑动 | 屏 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 副驾屏朝左滑动；副驾屏向左边滑动 | {"已知但不开放": 2} | {} | 是 | {} |
| 激活 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 运动模式激活；激活弹射起步功能 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 熄灭 | 车外灯 | {"调节内容": "模式", "车外灯类型": "前照灯"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 让自动大灯熄灭吧；自动大灯可以熄灭了 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 禁止 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 禁止吹脸和吹脚的操作；禁止吹脸吹窗 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 移 | 屏 | {"调节内容": "方向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 屏驾驶员移；屏朝主驾移 | {"已知但不开放": 2} | {} | 是 | {} |
| 解锁 | None | {"对象功能": "儿童锁"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 2 | 可以解锁右边儿童锁了；把右边儿童锁解锁 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设 | None | {"调节内容": "风速"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 设大一点风速；风速设小点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设为 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 帮我将导航播报功能设为极简；帮我把导航播报模式设为极简 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设置 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 2 | 设置酒吧音效；音效设置为三维 | {"非控制": 2} | {} | 是 | {} |
| 设置 | None | {"调节内容": "时间格式"} | NONE | NONE | NONE | 2 | 设置时间格式后排温度调到最高打开阅读灯；设置时间格式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设置 | None | {"调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 音量设置到五十；导航音量设置合适 | {"非控制": 2} | {} | 是 | {} |
| 设置 | None | {"调节内容": "风量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 设置小一点风量；设置成低风量 | {"已知但不开放": 2} | {} | 是 | {} |
| 设置 | None | {"功能": "驻车", "调节内容": "时长"} | NONE | NONE | NONE | 2 | 设置驻车时间；设置驻车时长 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设置 | None | {"对象功能": "蓝牙", "调节内容": "音量"} | NONE | NONE | NONE | 2 | 我想设置一下蓝牙的通话音量；设置蓝牙通话音量 | {"非控制": 2} | {} | 是 | {} |
| 设置 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 设置制冷模式；给我将麦克风设置静音 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设置 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 2 | 音效模式设置典雅旋律；将音效模式设置为爵士乐章 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设置 | None | {"对象功能": "声音均衡器"} | NONE | NONE | NONE | 2 | 帮我设置声音均衡器；我要设置声音均衡器 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设置 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 副驾座椅记忆设置为副驾位；主驾位置设置为一怎么操作 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设置为 | None | {"功能": "车道辅助", "调节内容": "预警方式"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 车道辅助预警方式设置为震动；车道辅助预警方式设置为声音加震动 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设置为 | None | {"调节内容": "时间格式"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 时间设置为二十四小时制；将时间设置为十二小时制 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设置为 | None | {"功能": "智慧巡航", "调节内容": "模式", "子功能": "限速控制"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 限速控制设置为手动确认；限速控制设置为自动控速 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 设置到 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 2 | 把音效模式设置到古典之韵；音效模式设置到流行律动 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调 | None | {"调节内容": "温度"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 2 | 温度调到二十七度前排都调到二十七度；前排温度调到二十一度空调风量一挡风 | {"已知但不开放": 2} | {} | 是 | {} |
| 调 | None | {} | NONE | NONE | NONE | 2 | 将转弯时的速度调到比较快的程度；温度在调高一点温度再调温度调到二十一度 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 语助我要调成静音；给我调静音 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调 | None | {"对象功能": "声音均衡器", "调节内容": "音效"} | NONE | NONE | NONE | 2 | 帮我把声音均衡器音效调为平坦；我要声音均衡器音效现在调为平坦好吗 | {"非控制": 2} | {} | 是 | {} |
| 调 | None | {"调节内容": "音量"} | NONE | NUMBER | NONE | 2 | 音量调到25；帮我把音量调到18 | {"非控制": 2} | {} | 是 | {} |
| 调 | None | {"调节内容": "声"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 导航的出声量帮我把它往下调20%；帮我把导航的说话声往下调整20%的程度 | {"非控制": 2} | {} | 是 | {} |
| 调 | 仪表屏 | {"调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 仪表屏调为百分之五；关闭大灯屏幕亮度调到最低仪表屏亮度调到最低一副屏亮度调到最低那是 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调 | 仪表盘 | {"调节内容": "亮度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 看不太清帮我调亮仪表盘；屏幕亮度调到最亮仪表盘亮度调到最亮 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调 | 坐垫 | {"调节内容": "倾斜角度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 坐垫倾斜角度调到最低；坐垫倾斜角度调到最高 | {"正式可执行": 2} | {"SEAT_TILT_SET_ANGLE": 2} | 是 | {} |
| 调 | 屏 | {"调节内容": "亮度"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 2 | 主驾屏调到最亮；主驾屏太暗了需要调亮一点 | {"已知但不开放": 2} | {} | 是 | {} |
| 调 | 座椅 | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 座椅温度调到最高；座椅温度调到最低 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调 | 座椅 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 把主驾座椅调到最后靠背调到最大；副驾座椅向下调 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调 | 蓝牙耳机 | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 把蓝牙耳机调到最小；把蓝牙耳机调到最低 | {"非控制": 2} | {} | 是 | {} |
| 调一点 | 座椅 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 主驾座椅往上调一点；主驾座椅往下调一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调一点 | 腿托 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 腿托往下调一点；往上调一点腿托 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调为 | 转向 | {"对象功能": "助力", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 转向助力调为厚重；转向助力调为沉稳模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调到 | None | {"调节内容": "声"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 歌声儿调到最小；把电话铃声调到最低 | {"非控制": 2} | {} | 是 | {} |
| 调到 | None | {"调节内容": "声音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 音乐声音调到四导航声音调到五 | {"非控制": 2} | {} | 是 | {} |
| 调到 | 冰箱 | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 冰箱调到负10度；打开空调冰箱温度调到最低 | {"已知但不开放": 2} | {} | 是 | {} |
| 调到 | 天幕 | {"调节内容": "透光度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 把天幕透光度调到最高；把天幕透光度调到最大 | {"已知但不开放": 2} | {} | 是 | {} |
| 调到 | 天幕 | {"调节内容": "透明度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 把天幕透明度调到最低；把天幕透明度调到最高 | {"已知但不开放": 2} | {} | 是 | {} |
| 调到 | 天幕 | {"调节内容": "透明值"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 天幕透明值调到20%；把天幕透明值调到最高 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调到 | 天窗 | {"调节内容": "透光挡位"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 把天窗透光挡位调到最大；天窗透光挡位调到一半 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调成 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 调成白天模式；温度调成二十度打开AC调成浅色模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调整 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 导航帮我把它的音量给调整到50%吧；请麻烦调整音量为一半 | {"非控制": 2} | {} | 是 | {} |
| 调整到 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 请调整到雪地模式；调整到夜间模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | HUD | {} | NONE | NONE | NONE | 2 | 打开自动驻车调节HUD；调节HUD后排坐垫翻折 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"对象功能": "混响", "调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 减小混响音量；混响大点儿声 | {"非控制": 2} | {} | 是 | {} |
| 调节 | None | {"调节内容": "能量回收强度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 能量回收强度高20；能量回收强度调节为百分之二十 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"调节内容": "声音"} | NONE | NUMBER | NONE | 2 | 导航声音还是让它转为20吧；我需要声音打到50 | {"非控制": 2} | {} | 是 | {} |
| 调节 | None | {"对象功能": "蓝牙", "调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 我想要50%的蓝牙音量；蓝牙通话音量调低20% | {"非控制": 2} | {} | 是 | {} |
| 调节 | None | {"对象功能": "左边出风口", "调节内容": "风向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 主驾左边出风口向上吹点；副驾左边出风口向上吹点 | {"已知但不开放": 2} | {} | 是 | {} |
| 调节 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 恢复回静音；更改驾驶设置为漂移模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"调节内容": "音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 系统提示音最高；语音升高一半 | {"非控制": 2} | {} | 是 | {} |
| 调节 | None | {"对象功能": "蓝牙", "调节内容": "声音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 蓝牙通话声音小一点；蓝牙通话声音小一些 | {"非控制": 2} | {} | 是 | {} |
| 调节 | None | {"对象功能": "充电", "调节内容": "充电量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 充电量额外少；充电量太低了 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"调节内容": "度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 最小的对比度；最低的对比度 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"对象功能": "右侧出风口", "调节内容": "风向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 右侧出风口往下调100；右侧出风口往左点 | {"已知但不开放": 2} | {} | 是 | {} |
| 调节 | None | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 你可以向左向右调节跟车时距 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"调节内容": "风向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 向左吹到顶；打开空调界面吹上面 | {"已知但不开放": 2} | {} | 是 | {} |
| 调节 | None | {"调节内容": "动力回收"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 动力回收调高百分之十；动力回收调节为30% | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"对象功能": "充电"} | NONE | NONE | NONE | 2 | 改变充电模式；改变车辆充电状态 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"调节内容": "风速"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 新风系统中速风速；升强一些风速 | {"已知但不开放": 2} | {} | 是 | {} |
| 调节 | None | {"对象功能": "回家照明", "调节内容": "时长"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 回家照明延时久一点；回家照明延时长一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"调节内容": "温度"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 后排调高温度调到二十三；后方温度降低 | {"已知但不开放": 2} | {} | 是 | {} |
| 调节 | None | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 请将调节主副驾座椅位置请确保后排没有乘客或障碍物 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"调节内容": "中音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 中音减小五；中音太高啦 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"调节内容": "电充"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 把电充到80%；把电充到百分之三十五 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"对象功能": "安全警报提示音", "调节内容": "音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 调节安全警报提示音为慢；安全警报提示音为快 | {"非控制": 2} | {} | 是 | {} |
| 调节 | None | {"调节内容": "温度"} | NONE | NONE | NONE | 2 | 调节温度；帮我设置不一样的温度 | {"已知但不开放": 2} | {} | 是 | {} |
| 调节 | None | {"调节内容": "风向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 副驾向下吹到顶；改变车内气流流向以实现左右扫风模式 | {"已知但不开放": 2} | {} | 是 | {} |
| 调节 | None | {"调节内容": "动力来源"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 混动模式；请改成纯电模式混动模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 减小一点；风来得再大些 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"功能": "声浪", "调节内容": "声"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 我想要低声浪；调一下声浪大小到低 | {"非控制": 2} | {} | 是 | {} |
| 调节 | None | {} | NONE | NONE | NONE | 2 | 调节语音播报导航语音的声音调大；你说话时能稍微小声一点吗 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"对象功能": "蓝牙", "调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 调高蓝牙通话音量；减低蓝牙音乐音量 | {"非控制": 2} | {} | 是 | {} |
| 调节 | None | {"功能": "盲区预警", "调节内容": "预警方式"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 把震动作为盲区预警的提示效果；震动的效果好一些用震动来提示我盲区预警 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"调节内容": "亮度"} | NONE | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | 2 | 发呆模式暗一点；星空暗一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | None | {"功能": "车道辅助", "调节内容": "预警方式", "子功能": "车道保持模式"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 车道保持模式仅警示；车道保持模式警示 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 中间储物台 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 中间储物台到后排；后面太挤把中间储物台向后座位置 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 仪表 | {"调节内容": "亮度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 仪表调亮一点；把仪表调暗一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 制冷器 | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 制冷器别吹脸；制冷器吹玻璃 | {"已知但不开放": 2} | {} | 是 | {} |
| 调节 | 后备箱 | {"调节内容": "高度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 后备箱调太低了；给我把后备箱降低了 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 后视镜 | {"调节内容": "高度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 调低流媒体后视镜；后视镜往下调 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 坐垫 | {"对象功能": "延长", "调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 将坐垫调到最前一下；坐垫延长调到最后 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 天窗 | {"调节内容": "透明值"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 天窗透明值小一点；天窗透明值高一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 头枕屏 | {"调节内容": "亮度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 头枕屏亮度调低一点；头枕屏亮度调高一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 座椅 | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 副驾座椅太烫了；副驾座椅制冷弄强一些 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 座椅 | {"调节内容": "温度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 座椅温度太低了；帮我把座椅温度往下调一下 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 座椅 | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 2 | 副驾座椅太冷了；调热主驾座椅温度 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 座椅 | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 给我降温座椅的温度一直到最凉温度的极限；座椅持续加热到头 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 座椅 | {} | NONE | NONE | NONE | 2 | 调节座椅位置；调节座椅扶手台移到最前 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 座椅 | {"调节内容": "角度"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 左后座椅角度大一点；右前座椅角度大一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 座椅侧翼 | {"调节内容": "弹性"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 2 | 右后座椅侧翼松一点；前排座椅侧翼松一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 座椅侧翼 | {"调节内容": "弹性"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 2 | 副驾座椅侧翼紧一点；主驾座椅侧翼紧一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 座椅包裹 | {"调节内容": "弹性"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 2 | 右后座椅包裹松一点；左后座椅包裹松一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 座椅后背 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 把副驾座椅后背调节界面打开；主驾座椅后背调节界面打开 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 座椅腿托 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 副驾座椅腿托太往上了；副驾座椅腿托太往下了 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 扬声器 | {"调节内容": "声音"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 2 | 车外扬声器最小的声音是什么样直接调到最低；车外扬声器太吵了直接调到最低声音 | {"非控制": 2} | {} | 是 | {} |
| 调节 | 扬声器 | {"调节内容": "音量"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 2 | 车外扬声器继续减小音量到下限；车外扬声器音量直接设成最低的程度 | {"非控制": 2} | {} | 是 | {} |
| 调节 | 扬声器 | {"调节内容": "声音"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 2 | 将车外扬声器整体提升10%的声音；削弱外面扬声器的声音大概20% | {"非控制": 2} | {} | 是 | {} |
| 调节 | 扬声器 | {"调节内容": "音量"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 2 | 车外扬声器音量最大；车外扬声器音量调小1格 | {"非控制": 2} | {} | 是 | {} |
| 调节 | 整车 | {"调节内容": "模式"} | NONE | NONE | NONE | 2 | 动力模式调为纯电驾驶模式调为四驱；更改驾驶设置为漂移模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 整车 | {"调节内容": "亮度"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 2 | 整车背光亮度太亮了；整车背光亮度调到最亮 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 空气净化器 | {} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 把空气净化器风速降低点；把空气净化器风速调低 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节 | 蓝牙耳机 | {"调节内容": "声音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 2 | 我想要最大的蓝牙声音；我需要最大的蓝牙声音 | {"非控制": 2} | {} | 是 | {} |
| 调节 | 蓝牙耳机 | {"调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 调高蓝牙耳机音量；降低蓝牙耳机音量 | {"非控制": 2} | {} | 是 | {} |
| 调节 | 蓝牙耳机 | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 蓝牙耳机调高10%；我要蓝牙耳机现在调高10%好吗 | {"非控制": 2} | {} | 是 | {} |
| 调节 | 话筒 | {"调节内容": "声音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 请你把话筒的声音调大一点；话筒声音小一点 | {"非控制": 2} | {} | 是 | {} |
| 调节 | 远光灯 | {"调节内容": "高度", "车外灯类型": "远光灯"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 2 | 我想要你帮我把远光灯调低一点；我需要你帮我把远光灯调高一点 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节到 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 2 | 把音效模式调节到爵士乐章；音效模式调节到流行律动 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节到 | 座椅 | {"调节内容": "座椅记忆位置"} | NONE | NONE | NONE | 2 | 调节到记忆功能1；调节到座椅记忆功能3 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调节至 | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 调节至漂移驾驶模式；调节至泥泞驾驶模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 调高 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 在此基础上调高10%的导航音量；如果能帮我调高当前的通话音量10%就好啦 | {"非控制": 2} | {} | 是 | {} |
| 转变为 | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 2 | 转变为泥泞驾驶模式；转变为漂移驾驶模式 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 转换 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 2 | 将音效模式转换爵士乐章；将音效模式转换典雅旋律 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 选择 | None | {"功能": "最佳听音位"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 2 | 最佳听音位选择驾驶位位置；最佳听音位选择全车 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 重新启动 | None | {} | NONE | NONE | NONE | 2 | 重新启动；车机重新启动 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| 降 | None | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 2 | 温度降到最低风速调到三挡；温度降到最低打开空调 | {"未知": 2} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 2} |
| None | HUD | {"调节内容": "亮度"} | NONE | NONE | NONE | 1 | 锁定屏幕和HUD的亮度 | {"已知但不开放": 1} | {} | 是 | {} |
| None | None | {"功能": "智慧巡航"} | NONE | NONE | NONE | 1 | 我希望恢复一下巡航 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"对象功能": "无线网"} | NONE | NONE | NONE | 1 | 我要查一下无线网现在的怎么样 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"对象功能": "投屏"} | NONE | NONE | NONE | 1 | 我想改改手机投屏的设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"功能": "交通标志", "子功能": "超速提醒"} | NONE | NONE | NONE | 1 | 超速提醒我 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"调节内容": "摄像头模式"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 内部连拍 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"功能": "倒车影像"} | NONE | NONE | NONE | 1 | 倒车影像 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"对象功能": "无线网络"} | NONE | NONE | NONE | 1 | 请给我查看下无线网络的情况怎样 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"功能": "记忆泊车"} | NONE | NONE | NONE | 1 | 我想记忆泊车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"对象功能": "自动息屏"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 副驾自动息屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"调节内容": "能量回收"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 能量回收自适应 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"对象功能": "网"} | NONE | NONE | NONE | 1 | 请我想查下无线网的状态怎么样 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"功能": "临时停车"} | NONE | NONE | NONE | 1 | 打开ACC临时停车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"调节内容": "音量"} | NONE | NONE | NONE | 1 | 我想改改系统的音量设置 | {"非控制": 1} | {} | 是 | {} |
| None | None | {"功能": "查询车况"} | NONE | NONE | NONE | 1 | 我的车有什么状况 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"功能": "驾驶辅助", "子功能": "驾驶辅助"} | NONE | NONE | NONE | 1 | 把驾驶辅助界面跳转 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"功能": "驻车", "调节内容": "时间"} | NONE | NONE | NONE | 1 | 帮我改改驻车的时间配置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"功能": "查询自动辅助驾驶剩余距离"} | NONE | NONE | NONE | 1 | 查询自动辅助驾驶剩余距离 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"调节内容": "温度"} | NONE | NONE | NONE | 1 | 空调开大一点点温度冷一点点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"对象功能": "网络设置"} | NONE | NONE | NONE | 1 | 请调出热点网络设置画面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"对象功能": "均衡器"} | NONE | NONE | NONE | 1 | 让页面跳转到均衡器设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"功能": "交通标志", "调节内容": "音效", "子功能": "超速报警"} | NONE | NONE | NONE | 1 | 超速的时候通过蜂鸣提醒我 | {"非控制": 1} | {} | 是 | {} |
| None | None | {"功能": "车道辅助", "子功能": "保持在当前车道"} | NONE | NONE | NONE | 1 | 帮我保持在当前车道 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"调节内容": "模式"} | NONE | NONE | NONE | 1 | 打开尾翼后视镜内循环 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | None | {"功能": "车道辅助", "子功能": "维持行驶在当前车道上"} | NONE | NONE | NONE | 1 | 维持行驶在当前车道上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 冰箱 | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 1 | 我要在冰箱热下吃的 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 后视镜 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 左边后视镜设置页面开开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 后视镜 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 打开尾翼后视镜内循环 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 天幕 | {"调节内容": "透光值"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 天幕透光值自动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 天幕 | {"调节内容": "透明值"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 天幕透明值自动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 天窗 | {"调节内容": "透明挡位"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 天窗透明挡位自动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 座椅 | {} | NONE | NONE | NONE | 1 | 座椅不舒服重新搞一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 座椅 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 副驾座椅恢复正常 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 座椅 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 座椅一键成床 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 空气净化 | {} | NONE | NONE | NONE | 1 | 打开等离子空气净化 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 车窗 | {} | NONE | NONE | NONE | 1 | 右后车窗和主驾车窗都可以再往上收一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 车窗 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 把天窗打开把主驾驶的车窗升起来 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| None | 麦克风 | {} | NONE | NONE | NONE | 1 | 给我将麦克风设置静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 下来 | 窗户 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 把窗户全落下来把窗户全部下来 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 不再启用 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 不再启用吹脸模式 | {"已知但不开放": 1} | {} | 是 | {} |
| 不显示 | None | {"功能": "环视摄像头"} | NONE | NONE | NONE | 1 | 环视摄像头不显示 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 不用 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 打开副驾吹脸不用吹脚 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 不需要 | None | {"对象功能": "弯道照明"} | NONE | NONE | NONE | 1 | 我不需要弯道照明了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 使用 | None | {"对象功能": "除霜"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 为确保安全驾驶我要使用后除霜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 使用 | 备胎装置 | {} | NONE | NONE | NONE | 1 | 停止使用备胎装置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 使用 | 娱乐大屏 | {} | NONE | NONE | NONE | 1 | 我需要使用娱乐大屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 使用 | 转向灯 | {"车外灯类型": "转向灯"} | NONE | NONE | NONE | 1 | 我需要使用左边的转向灯 | {"正式可执行": 1} | {"TURN_INDICATOR_ON": 1} | 是 | {} |
| 使用一下 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 1 | 帮我使用一下让行感谢功能 | {"非控制": 1} | {} | 是 | {} |
| 保存 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 副驾偏好保存为副驾位 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 保存 | 座椅 | {"调节内容": "座椅记忆位置"} | NONE | NONE | NONE | 1 | 保存当前位置到坐姿二 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 修改 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 修改为越野模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 修改 | None | {"功能": "音效增强"} | NONE | NONE | NONE | 1 | 对音效增强设置进行修改 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 修改 | None | {"对象功能": "蓝牙", "调节内容": "声音"} | NONE | NONE | NONE | 1 | 我想要修改一下蓝牙的声音大小 | {"非控制": 1} | {} | 是 | {} |
| 修改 | None | {"调节内容": "亮度"} | NONE | NONE | NONE | 1 | 我需要修改背光联动设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 修改 | 充电口盖 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 我要修改充电口盖的自定义功能打开设置页 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停了 | None | {"对象功能": "充电"} | NONE | NONE | NONE | 1 | 把充电停了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停掉 | None | {"对象功能": "弯道照明"} | NONE | NONE | NONE | 1 | 给我停掉弯道照明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止 | None | {"调节内容": "风"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 停止极速风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 停止休憩空间 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止 | None | {"调节内容": "风向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 让风停止左右扫动 | {"已知但不开放": 1} | {} | 是 | {} |
| 停止 | None | {"对象功能": "车速补偿", "调节内容": "音随车速档位"} | NONE | NONE | NONE | 1 | 帮我停止运行车速补偿音量吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止 | None | {"功能": "车道辅助", "子功能": "车道引导"} | NONE | NONE | NONE | 1 | 停止车道引导功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止 | None | {"调节内容": "能量回收"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 停止能量回收自动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止 | 净化空气 | {} | NONE | NONE | NONE | 1 | 停止净化空气 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止 | 座椅 | {"对象功能": "出风"} | NONE | NONE | NONE | 1 | 座椅停止出风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止 | 车载儿童座椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 车载儿童座椅停止加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止一下 | 电动侧门 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 把全部电动侧门停止一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止关闭 | 电动侧门 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 停止关闭左后电动侧门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止关闭 | 电动门 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 停止关闭全部电动门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止关闭 | 电动门 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 停止关闭右后电动门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停止收听 | None | {} | NONE | NONE | NONE | 1 | 停止收听车载收音机 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 停用 | None | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 停用后排语音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 储存 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾座椅记忆储存为位置三 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 充 | None | {"调节内容": "充电"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 充电充到50% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 充 | None | {"对象功能": "充电", "调节内容": "电量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 电量充到50% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 充 | None | {"对象功能": "充电", "调节内容": "电池电量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 电池电量充到50% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | None | {"功能": "座舱恒温"} | NONE | NONE | NONE | 1 | 我想关座舱恒温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | None | {"功能": "座舱控温"} | NONE | NONE | NONE | 1 | 我想关座舱控温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | None | {"对象功能": "无线网络"} | NONE | NONE | NONE | 1 | 不准关无线网络 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | None | {"调节内容": "动力来源"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 请给我将燃油优先关 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | None | {"对象功能": "蓝牙"} | NONE | NONE | NONE | 1 | 查一下蓝牙关没 | {"已知但不开放": 1} | {} | 是 | {} |
| 关 | None | {} | NONE | NONE | NONE | 1 | 关音乐关机 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | None | {"对象功能": "智能解锁"} | NONE | NONE | NONE | 1 | 智能解锁设置为关 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | None | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 关弱一点温度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | None | {"调节内容": "风量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 小速风量帮我关 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | None | {"对象功能": "童锁"} | NONE | NONE | NONE | 1 | 帮我关童锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | 备胎装置 | {} | NONE | NONE | NONE | 1 | 把备胎装置关一关 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | 屏 | {} | NONE | NONE | NONE | 1 | 退出关屏 | {"已知但不开放": 1} | {} | 是 | {} |
| 关 | 座椅 | {"对象功能": "出风"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 后排座椅的出风口给关死别让它吹风出来了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | 方向盘 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 设定方向盘的加热开关为关 | {"已知但不开放": 1} | {} | 是 | {} |
| 关 | 空气净化器 | {} | NONE | NONE | NONE | 1 | 关空气净化器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | 窗帘 | {"调节内容": "幅度"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 所有窗帘给我关百分之三十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | 窗帘 | {} | NONE | NONE | NONE | 1 | 关窗帘 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关 | 遥控 | {"对象功能": "解锁功能"} | NONE | NONE | NONE | 1 | 关遥控解锁功能设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关一下 | None | {"对象功能": "除湿模式"} | NONE | NONE | NONE | 1 | 除湿模式给我关一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关一下 | None | {"功能": "座舱过热保护"} | NONE | NONE | NONE | 1 | 给我关一下座舱过热保护 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关一下 | None | {"调节内容": "音量调节"} | NONE | NONE | NONE | 1 | 把音量调节页面关一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关一下 | None | {"功能": "驻车", "调节内容": "摄像头模式"} | NONE | NONE | NONE | 1 | 关一下驻车拍照 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关一下 | None | {"对象功能": "风扇"} | NONE | NONE | NONE | 1 | 风扇帮我关一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关一下 | 窗帘 | {} | NONE | NONE | NONE | 1 | 窗帘关一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关一下 | 蒸发器 | {"对象功能": "自干燥"} | NONE | NONE | NONE | 1 | 帮我关一下蒸发器自干燥 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关上 | None | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 关上所有位置的制冷 | {"已知但不开放": 1} | {} | 是 | {} |
| 关上 | None | {"调节内容": "风量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 快速风量关上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关上 | None | {"功能": "插枪保温"} | NONE | NONE | NONE | 1 | 关上插枪保温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关上 | None | {"调节内容": "风速"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 关上低风速 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关上 | None | {"对象功能": "智能解锁"} | NONE | NONE | NONE | 1 | 智能解锁设置关上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关上 | None | {"调节内容": "风速"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 最小速的风速帮我关上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关上 | None | {"对象功能": "车外低速报警"} | NONE | NONE | NONE | 1 | 车外低速报警配置关上 | {"已知但不开放": 1} | {} | 是 | {} |
| 关上 | 座椅 | {"对象功能": "零重力"} | NONE | NONE | NONE | 1 | 调一下零重力座椅关上吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关上 | 电动门 | {} | NONE | NONE | NONE | 1 | 关上电动门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关上 | 车隔断玻璃 | {} | NONE | NONE | NONE | 1 | 把车隔断玻璃关上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关下 | None | {"功能": "过热保护"} | NONE | NONE | NONE | 1 | 关下过热保护 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关下 | None | {"对象功能": "出风口"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关下全车出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关下 | None | {"调节内容": "亮度"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 关下自动亮度调节开关 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关下 | None | {"功能": "驻车", "调节内容": "摄像头模式"} | NONE | NONE | NONE | 1 | 关下驻车拍照 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关下 | 音响 | {} | NONE | NONE | NONE | 1 | 音响调节页为我关下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关了 | None | {"功能": "驾驶辅助", "子功能": "领航驾驶辅助"} | NONE | NONE | NONE | 1 | 给我把领航驾驶辅助设置页面关了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关了 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 1 | 把音乐音效关了 | {"非控制": 1} | {} | 是 | {} |
| 关了 | None | {} | NONE | NONE | NONE | 1 | 把允许通知关了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关了 | None | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 关了副驾的活力模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关了 | None | {"功能": "音效增强"} | NONE | NONE | NONE | 1 | 音效增强影响音质了快关了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关了 | None | {"对象功能": "观影角度"} | NONE | NONE | NONE | 1 | 观影角度关了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关了 | None | {"对象功能": "接近照明"} | NONE | NONE | NONE | 1 | 用不着接近照明了关了吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关了 | None | {"调节内容": "风量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 低速风量帮我关了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关了 | 抬头显示 | {} | NONE | NONE | NONE | 1 | 关了抬头显示 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关了 | 摄像头 | {} | NONE | NONE | NONE | 1 | 把摄像头关了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关了 | 方向盘 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 方向盘都烫手了加热关了 | {"已知但不开放": 1} | {} | 是 | {} |
| 关了 | 玻璃 | {"调节内容": "透明度"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 1 | 把二排左边玻璃自动透明度关了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关小 | 太阳窗 | {"调节内容": "幅度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 太阳窗关小点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 关掉迎面吹风打开脚下吹风 | {"已知但不开放": 1} | {} | 是 | {} |
| 关掉 | None | {"功能": "全景环视"} | NONE | NONE | NONE | 1 | 请给全景环视关掉 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"调节内容": "风量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 关掉高速风量 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"对象功能": "热点"} | NONE | NONE | NONE | 1 | 关掉热点关掉蓝牙 | {"已知但不开放": 1} | {} | 是 | {} |
| 关掉 | None | {"功能": "无线设备充电"} | NONE | NONE | NONE | 1 | 我想关掉无线设备充电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"对象功能": "风扇"} | NONE | NONE | NONE | 1 | 关掉风扇关掉空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"功能": "侧后辅助", "子功能": "后向碰撞减缓"} | NONE | NONE | NONE | 1 | 把后向碰撞减缓关掉 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {} | NONE | NONE | NONE | 1 | 关掉音乐关掉音乐 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 关掉通风关掉空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"功能": "主动恒温"} | NONE | NONE | NONE | 1 | 需要关掉主动恒温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"调节内容": "风"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 小风关掉 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"对象功能": "儿童锁"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 右边的儿童锁可以帮我把它给关掉 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"功能": "过热保护"} | NONE | NONE | NONE | 1 | 关掉过热保护 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"功能": "驻车模式"} | NONE | NONE | NONE | 1 | 关掉驻车模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | None | {"对象功能": "低速提示音"} | NONE | NONE | NONE | 1 | 关掉低速提示音导航到金茂锦园 | {"已知但不开放": 1} | {} | 是 | {} |
| 关掉 | None | {"对象功能": "童锁"} | NONE | NONE | NONE | 1 | 给我关掉童锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | 后视镜 | {"对象功能": "除霜"} | NONE | NONE | NONE | 1 | 关掉后视镜除霜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | 备胎 | {} | NONE | NONE | NONE | 1 | 备胎设置完了给我关掉吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | 天幕 | {} | NONE | NONE | NONE | 1 | 天幕关掉遮阳帘关掉 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | 座椅 | {} | NONE | NONE | NONE | 1 | 关掉座椅关闭方向盘加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | 电源 | {} | NONE | NONE | NONE | 1 | 关掉空调关掉电源 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | 空气净化 | {} | NONE | NONE | NONE | 1 | 关掉空气净化 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉 | 空气净化器 | {} | NONE | NONE | NONE | 1 | 把空气净化器关掉 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关掉一下 | None | {"功能": "模拟声浪"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 将车外模拟声浪关掉一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"调节内容": "风速"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 低速风速为我关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "低速提示报警"} | NONE | NONE | NONE | 1 | 打开空调关闭低速提示报警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "出风口", "调节内容": "风向"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭主驾出风口 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "吹风"} | NONE | NONE | NONE | 1 | 关闭吹风关闭空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "开机动画音乐"} | NONE | NONE | NONE | 1 | 关闭来电语音播报关闭开机动画音乐 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "离子净化器"} | NONE | NONE | NONE | 1 | 关闭离子净化器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "吹风"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开主驾空调关闭副驾吹风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "全景视频"} | NONE | NONE | NONE | 1 | 关闭全景视频 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "行车低速提示音"} | NONE | NONE | NONE | 1 | 关闭行车低速提示音 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "微升微降"} | NONE | NONE | NONE | 1 | 微升微降关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "超速监测", "子功能": "超速监测"} | NONE | NONE | NONE | 1 | 关闭超速监测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "倒车降低音乐"} | NONE | NONE | NONE | 1 | 关闭倒车降低音乐 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "低速行驶"} | NONE | NONE | NONE | 1 | 关闭低速行驶并打开空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "网络"} | NONE | NONE | NONE | 1 | 播放第一首歌关闭网络 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "泊车辅助"} | NONE | NONE | NONE | 1 | 关闭泊车辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "遗留物品检测"} | NONE | NONE | NONE | 1 | 关闭遗留物品检测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "卫星通讯"} | NONE | NONE | NONE | 1 | 关闭卫星通讯 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "转向联动"} | NONE | NONE | NONE | 1 | 关闭转向联动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "超速警示音", "子功能": "超速警示音"} | NONE | NONE | NONE | 1 | 关闭超速警示音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "自动停车功能"} | NONE | NONE | NONE | 1 | 关闭自动停车功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "出风口"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭全车出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "低速预警"} | NONE | NONE | NONE | 1 | 打开按摩关闭低速预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "对负载充电"} | NONE | NONE | NONE | 1 | 关闭对负载充电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "无线设备充电"} | NONE | NONE | NONE | 1 | 我要关闭无线设备充电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "出风口"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 关闭右前出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "车道辅助", "子功能": "车道偏离辅助"} | NONE | NONE | NONE | 1 | 关闭车道偏离辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "方便上车"} | NONE | NONE | NONE | 1 | 关闭方便上车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "出风口", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭手动出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "手机投屏"} | NONE | NONE | NONE | 1 | 我要关闭手机投屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "风口"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭三排风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "行车视频限制模式"} | NONE | NONE | NONE | 1 | 关闭行车视频限制模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "模拟声浪"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭车内模拟声浪 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "车外低速提示音"} | NONE | NONE | NONE | 1 | 关闭车外低速提示音打开空调 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | None | {"功能": "侧后辅助", "子功能": "后碰撞警告"} | NONE | NONE | NONE | 1 | 关闭后碰撞警告 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "交叉路口碰撞预警", "子功能": "交叉路口碰撞预警"} | NONE | NONE | NONE | 1 | 关闭交叉路口碰撞预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "全景影像", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭自动开启全景影像 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "车外行人提示音"} | NONE | NONE | NONE | 1 | 关闭车外行人提示音音量调到十六 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "三六零"} | NONE | NONE | NONE | 1 | 关闭所有的座椅通风关闭三六零 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"调节内容": "风向"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭主驾风向打开副驾空调 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | None | {"调节内容": "风向"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 关闭前排吹脚模式 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "车外警示音"} | NONE | NONE | NONE | 1 | 关闭车外警示音导航去公司 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "停车", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭停车舒享模式 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | None | {"功能": "乘员监测系统", "子功能": "儿童遗留监测"} | NONE | NONE | NONE | 1 | 关闭儿童遗留监测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "延时断电"} | NONE | NONE | NONE | 1 | 关闭延时断电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "连续说"} | NONE | NONE | NONE | 1 | 连续说开关关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "闭锁关窗"} | NONE | NONE | NONE | 1 | 关闭闭锁关窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "定位", "对象功能": "使用权限"} | NONE | NONE | NONE | 1 | 关闭定位使用权限 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "低速警报"} | NONE | NONE | NONE | 1 | 关闭低速警报打开座位通风座椅按摩 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "开机声音", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 开机声音关闭静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "⾏⼈提示音"} | NONE | NONE | NONE | 1 | 关闭⾏⼈提示音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "导航抑制媒体音"} | NONE | NONE | NONE | 1 | 将导航抑制媒体音关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭前排游戏模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "倒车音"} | NONE | NONE | NONE | 1 | 倒车音关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "自动导航辅助", "子功能": "自动导航辅助"} | NONE | NONE | NONE | 1 | 关闭自动导航辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "限速提醒", "子功能": "限速提醒"} | NONE | NONE | NONE | 1 | 关闭限速提醒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "车道辅助", "子功能": "车道保持"} | NONE | NONE | NONE | 1 | 关闭车道保持 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "回家照明延时"} | NONE | NONE | NONE | 1 | 关闭回家照明延时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "逆向超车预警", "子功能": "逆向超车预警"} | NONE | NONE | NONE | 1 | 关闭逆向超车预警页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "二氧化碳浓度检测"} | NONE | NONE | NONE | 1 | 关闭二氧化碳浓度检测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "马达启停"} | NONE | NONE | NONE | 1 | 关闭马达启停 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"调节内容": "背光"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 把副驾背光关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "单门闭锁"} | NONE | NONE | NONE | 1 | 关闭单门闭锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "超速提醒", "子功能": "超速提醒"} | NONE | NONE | NONE | 1 | 关闭超速提醒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"调节内容": "风向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 我不习惯开启左右扫风 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | None | {"功能": "记忆泊车"} | NONE | NONE | NONE | 1 | 关闭记忆泊车页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "弯路照明"} | NONE | NONE | NONE | 1 | 关闭弯路照明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "模拟声浪"} | NONE | NONE | NONE | 1 | 关闭模拟声浪 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "城市智能领航辅助", "子功能": "城市智能领航辅助"} | NONE | NONE | NONE | 1 | 关闭城市智能领航辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "主动提示"} | NONE | NONE | NONE | 1 | 关闭语音主动提示 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"调节内容": "风"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 大风关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "移动数据"} | NONE | NONE | NONE | 1 | 关闭移动数据 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "侧后辅助", "子功能": "后方交通穿行提示"} | NONE | NONE | NONE | 1 | 关闭后方交通穿行提示 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "侧后辅助", "子功能": "后方碰撞预警"} | NONE | NONE | NONE | 1 | 关闭后方碰撞预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "驻车", "调节内容": "摄像头模式"} | NONE | NONE | NONE | 1 | 关闭驻车照片开关 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "前向辅助", "子功能": "前方侧向交通辅助"} | NONE | NONE | NONE | 1 | 关闭前方侧向交通辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "车速补偿", "调节内容": "音随车速档位"} | NONE | NONE | NONE | 1 | 关闭车速补偿音量 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "座舱主动温控系统"} | NONE | NONE | NONE | 1 | 关闭座舱主动温控系统 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "强制保电记忆"} | NONE | NONE | NONE | 1 | 关闭强制保电记忆 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "开机背景声音"} | NONE | NONE | NONE | 1 | 关闭开机背景声音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 关闭通话中收听导航播报 | {"非控制": 1} | {} | 是 | {} |
| 关闭 | None | {"调节内容": "辅助形式选择"} | NONE | NONE | NONE | 1 | 辅助形式选择关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "低速行驶外警示音"} | NONE | NONE | NONE | 1 | 关闭低速行驶外警示音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "速报警", "子功能": "速报警"} | NONE | NONE | NONE | 1 | 关闭速报警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "按键锁"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 关闭后排按键锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "车外低速警示音"} | NONE | NONE | NONE | 1 | 关闭车外低速警示音放首歌听 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "限速告警", "子功能": "限速告警"} | NONE | NONE | NONE | 1 | 关闭限速告警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "空气质量检测"} | NONE | NONE | NONE | 1 | 关闭空气质量检测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "靠近照明"} | NONE | NONE | NONE | 1 | 关闭靠近照明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"调节内容": "摄像头模式"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 车前短视频关闭录制 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "开机声音"} | NONE | NONE | NONE | 1 | 关闭开机声音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "车外的声音"} | NONE | NONE | NONE | 1 | 关闭车外的声音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "等离子"} | NONE | NONE | NONE | 1 | 关闭等离子 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "车外报警音"} | NONE | NONE | NONE | 1 | 关闭空调关闭车外报警音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"调节内容": "模式"} | NONE | QUANTIFIED_OR_LEVEL | TEXT_ENUM_OR_OTHER | 1 | 关闭最大制冷 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | None | {"对象功能": "无线投屏"} | NONE | NONE | NONE | 1 | 关闭无线投屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"调节内容": "视图"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 关闭尾舱透明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "接近解锁"} | NONE | NONE | NONE | 1 | 关闭接近解锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "靠近解锁"} | NONE | NONE | NONE | 1 | 关闭靠近解锁关闭空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "车对负载放电"} | NONE | NONE | NONE | 1 | 关闭车对负载放电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "按键声"} | NONE | NONE | NONE | 1 | 按键声设置关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "出风口", "调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭主驾出风口手动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "音量随车速补偿", "调节内容": "音随车速档位"} | NONE | NONE | NONE | 1 | 关闭音量随车速补偿页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "侧后辅助", "子功能": "门开预警功能"} | NONE | NONE | NONE | 1 | 门开预警功能关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "智能驾驶语音播报"} | NONE | NONE | NONE | 1 | 关闭智能驾驶语音播报 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "吹风"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 关闭后排吹风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "无线手机充电"} | NONE | NONE | NONE | 1 | 关闭无线手机充电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "环视退出"} | NONE | NONE | NONE | 1 | 关闭环视退出 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "卫星通信"} | NONE | NONE | NONE | 1 | 关闭卫星通信设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "手持打电话提醒"} | NONE | NONE | NONE | 1 | 关闭手持打电话提醒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "盲区检测"} | NONE | NONE | NONE | 1 | 关闭盲区检测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "数据连接"} | NONE | NONE | NONE | 1 | 关闭数据连接 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "开机音量自适应"} | NONE | NONE | NONE | 1 | 关闭开机音量自适应 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "系统快速启动功能"} | NONE | NONE | NONE | 1 | 系统快速启动功能关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"对象功能": "低速行驶音"} | NONE | NONE | NONE | 1 | 打开座椅通风关闭低速行驶音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "汽车保养时间提醒", "调节内容": "时长"} | NONE | NONE | NONE | 1 | 关闭汽车保养时间提醒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "我要把自适", "子功能": "自动变道提醒"} | NONE | NONE | NONE | 1 | 我要把自适应巡航设成禁止给我设一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | None | {"功能": "绕行辅助功能"} | NONE | NONE | NONE | 1 | 关闭绕行辅助功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 交流充电口盖 | {"对象功能": "交流电"} | NONE | NONE | NONE | 1 | 关闭交流充电口盖 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 交流接口盖 | {"对象功能": "交流电"} | NONE | NONE | NONE | 1 | 关闭交流接口盖 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 仪表盘 | {} | NONE | NONE | NONE | 1 | 关闭车机关闭仪表盘 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 侧翼 | {} | NONE | NONE | NONE | 1 | 关闭主动侧翼 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 储物箱 | {} | NONE | NONE | NONE | 1 | 关闭储物箱 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 儿童座椅 | {"对象功能": "通风", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭儿童座椅自然风 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | 充电口盖 | {} | NONE | NONE | NONE | 1 | 关闭充电口盖 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 冰箱 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭冰箱保温模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 反光镜 | {} | NONE | NONE | NONE | 1 | 关闭反光镜关闭空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 后视镜 | {"调节内容": "亮度"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭流媒体内后视镜自动亮度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 后视镜 | {"对象功能": "除霜"} | NONE | NONE | NONE | 1 | 后视镜除霜关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 后视镜 | {"对象功能": "自动下翻功能"} | NONE | NONE | NONE | 1 | 后视镜自动下翻功能关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 后视镜 | {"对象功能": "倒车", "调节内容": "模式"} | NONE | NONE | NONE | 1 | 后视镜倒车模式切换为关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 后视镜 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭流媒体内后视镜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 吸顶屏 | {} | NONE | NONE | NONE | 1 | 吸顶屏息屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 坐垫 | {"调节内容": "软硬度"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 把后排坐垫软硬度关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 备胎 | {} | NONE | NONE | NONE | 1 | 关闭备胎 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 备胎装置 | {} | NONE | NONE | NONE | 1 | 关闭备胎装置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 外后视镜 | {"对象功能": "倒车"} | NONE | NONE | NONE | 1 | 关闭外后视镜倒车模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 天窗窗帘 | {"调节内容": "幅度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 我只要开80%的天窗窗帘 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 太阳窗 | {} | NONE | NONE | NONE | 1 | 关闭太阳窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 头枕屏 | {"对象功能": "蓝牙"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭副驾头枕屏蓝牙 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | 安全带 | {"对象功能": "安全带提示"} | NONE | NONE | NONE | 1 | 关闭低速提示音关闭安全带提示 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 尾翼 | {"对象功能": "迎宾"} | NONE | NONE | NONE | 1 | 关闭尾翼迎宾 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 屏 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 右手边的屏关闭 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | 幕布 | {} | NONE | NONE | NONE | 1 | 关闭天窗关闭幕布 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | 座椅 | {"对象功能": "律动"} | NONE | NONE | NONE | 1 | 打开主驾按摩关闭座椅律动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 座椅 | {"对象功能": "零重力"} | NONE | NONE | NONE | 1 | 好了座椅的零重力快断了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 座椅 | {"对象功能": "通风"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 前排座椅把它的通风更改成不可用 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | 座椅 | {"对象功能": "动力学"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭副驾座椅动力学 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 座椅 | {"对象功能": "震动"} | NONE | NONE | NONE | 1 | 关闭座椅关闭座椅震动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 座椅 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭主驾的座椅调节 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 座椅 | {"对象功能": "加热"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾驶的座椅不用给我加热了 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | 悬架 | {"功能": "方便上下车"} | NONE | NONE | NONE | 1 | 关闭悬架方便上下车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 悬架 | {} | NONE | NONE | NONE | 1 | 悬架调节设置页面关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 手套箱 | {} | NONE | NONE | NONE | 1 | 关闭手套箱 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 折叠屏 | {} | NONE | NONE | NONE | 1 | 关闭折叠屏歌曲同唱 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 抬头显示 | {} | NONE | NONE | NONE | 1 | 关闭抬头显示 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 拖车钩 | {} | NONE | NONE | NONE | 1 | 关闭拖车钩 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 方向盘 | {"对象功能": "加热", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭方向盘低温自动加热 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | 方向盘 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 播放音乐关闭方向盘加热 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | 星空顶棚 | {"车内灯类型": "星空顶棚"} | NONE | NONE | NONE | 1 | 星空顶棚关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 显示器 | {} | NONE | NONE | NONE | 1 | 关闭空调关闭显示器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 智能儿童座椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 智能儿童座椅关闭加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 智能底盘 | {} | NONE | NONE | NONE | 1 | 关闭智能底盘设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 智能除味 | {} | NONE | NONE | NONE | 1 | 关闭智能除味关闭车窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 汽车头显 | {} | NONE | NONE | NONE | 1 | 关闭汽车头显 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 汽车电源 | {} | NONE | NONE | NONE | 1 | 关闭汽车电源 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 液晶大屏 | {} | NONE | NONE | NONE | 1 | 关闭液晶大屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 滑门 | {} | NONE | NONE | NONE | 1 | 打开侧滑门关闭侧滑门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 激光雷达 | {} | NONE | NONE | NONE | 1 | 关闭激光雷达 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 玻璃 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭副驾驶的玻璃关闭天窗打开后备箱 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 玻璃 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 关闭后排玻璃打开空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 玻璃 | {} | NONE | NONE | NONE | 1 | 关闭天窗关闭玻璃 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 电动尾翼 | {"对象功能": "迎宾模式"} | NONE | NONE | NONE | 1 | 电动尾翼迎宾模式关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 电动尾翼 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭电动尾翼手动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 电动门 | {} | NONE | NONE | NONE | 1 | 电动门关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 电子屏 | {} | NONE | NONE | NONE | 1 | 关闭电子屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 空气净化 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭智能空气净化 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 空气净化功能 | {} | NONE | NONE | NONE | 1 | 关闭空气净化功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 窗 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开空调关闭后窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 窗 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭窗户关闭驾驶窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 窗子 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭所有窗子打开空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 窗子 | {} | NONE | NONE | NONE | 1 | 关闭窗子打开空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 窗帘 | {"调节内容": "幅度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 窗帘关闭到百分之十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 窗帘 | {"调节内容": "幅度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 给我把窗帘合上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 窗窗帘 | {} | NONE | NONE | NONE | 1 | 关闭天窗关闭窗窗帘 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 蓝牙钥匙 | {"对象功能": "离车自动落锁"} | NONE | NONE | NONE | 1 | 关闭蓝牙钥匙离车自动落锁 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | 车内照明 | {} | NONE | NONE | NONE | 1 | 关闭车内照明关闭氛围灯 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 车窗 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 让左前面车窗完全上升 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 车载儿童座椅 | {"对象功能": "通风", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 退出车载儿童座椅自然通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 车载冰箱 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 车载冰箱保温时长开关关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 转向灯 | {"车外灯类型": "转向灯"} | NONE | NONE | NONE | 1 | 帮我取消掉转向灯运行 | {"正式可执行": 1} | {"TURN_INDICATOR_OFF": 1} | 是 | {} |
| 关闭 | 遮光帘 | {} | NONE | NONE | NONE | 1 | 关闭天窗关闭遮光帘 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 门窗 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭所有门窗打开空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 门锁 | {"对象功能": "行车闭锁"} | NONE | NONE | NONE | 1 | 关闭行车闭锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 雾灯 | {"车外灯类型": "雾灯"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 不下雾了让前雾灯暗下去 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 音响 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭车外灯光关闭音响 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 音响 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 导航去八佰伴关闭车外音响 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 顶棚屏 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 后排顶棚屏关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 香薰 | {} | NONE | NONE | NONE | 1 | 关闭氛围灯关闭香薰 | {"已知但不开放": 1} | {} | 是 | {} |
| 关闭 | 驶屏 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭中控屏关闭副驾驶屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭 | 麦克风 | {"对象功能": "使用权限"} | NONE | NONE | NONE | 1 | 关闭麦克风使用权限 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭一下 | None | {"功能": "驻车"} | NONE | NONE | NONE | 1 | 关闭一下驻车拍照 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭一下 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 我想要关闭一下手动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭一下下 | 蒸发器 | {"对象功能": "自干燥"} | NONE | NONE | NONE | 1 | 我要把蒸发器自干燥关闭一下下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭下 | None | {"功能": "路口放大图功能"} | NONE | NONE | NONE | 1 | 路口放大图功能关闭下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭下 | None | {"功能": "声浪"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 将车外声浪关闭下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭下 | None | {"功能": "驻车", "调节内容": "摄像头模式"} | NONE | NONE | NONE | 1 | 把驻车拍照关闭下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 关闭掉 | None | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 1 | 关闭掉极速降低温度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 再使用 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 导航可以不再使用无声模式了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 减小成 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 音量帮我减小成一半 | {"非控制": 1} | {} | 是 | {} |
| 切 | None | {"调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 切最小的亮度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切一下 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 切一下自定义模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切为 | None | {"对象功能": "车速自动关窗", "调节内容": "车速"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 车速自动关窗切为每小时60公里 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切到 | None | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 1 | 切到外循环模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切到 | None | {"对象功能": "低速行人警告音"} | NONE | NONE | NONE | 1 | 切到低速行人警告音页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切到 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 切到内循环 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换 | None | {} | NONE | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | 1 | 动力模式切换到纯电驾驶模式切换到标准 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换 | None | {"调节内容": "风向"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 切换副驾风向控制模式为扫风 | {"已知但不开放": 1} | {} | 是 | {} |
| 切换 | None | {"对象功能": "车外SAYHI声音", "调节内容": "音效"} | NONE | NONE | NONE | 1 | 切换车外sayhi声音到呼唤 | {"非控制": 1} | {} | 是 | {} |
| 切换 | None | {"调节内容": "风向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 开始切换风扇方向将车内设置为左右扫风模式 | {"已知但不开放": 1} | {} | 是 | {} |
| 切换 | None | {"功能": "行车保电", "子功能": "智能保电"} | NONE | NONE | NONE | 1 | 切换智能保电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换 | None | {"调节内容": "风量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 切换成极速风量 | {"已知但不开放": 1} | {} | 是 | {} |
| 切换 | None | {"调节内容": "摄像头模式"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 切换车外缩录 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换 | None | {"对象功能": "车模", "调节内容": "颜色"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 车模颜色切换白色 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换 | None | {"调节内容": "风向"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 使车内风扇方向转为自动扫风 | {"已知但不开放": 1} | {} | 是 | {} |
| 切换 | 仪表 | {"对象功能": "续航", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 仪表续航显示切换为动态 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换 | 天幕 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 天幕模式切换为流水 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换 | 车载冰箱 | {"调节内容": "时长"} | NONE | QUANTIFIED_OR_LEVEL | TEXT_ENUM_OR_OTHER | 1 | 切换车载冰箱保温时间至1小时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换一下 | None | {"调节内容": "温度单位"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 切换一下温度为华氏度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换一下 | None | {"调节内容": "视图"} | NONE | NONE | NONE | 1 | 把视图切换一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | None | {"功能": "壁纸桌面"} | NONE | NONE | NONE | 1 | 桌面切换为壁纸桌面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | None | {"功能": "智慧巡航", "调节内容": "模式", "子功能": "辅助驾驶播报"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 驾驶辅助语音播报切换为精简模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | None | {"对象功能": "电动吹风口", "调节内容": "风向"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 后排电动吹风口切换为对人吹模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | None | {"对象功能": "智能表面", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 智能表面切换为呼吸 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | None | {"功能": "音效增强", "调节内容": "音效"} | NONE | NONE | NONE | 1 | 音效增强切换为超重低音 | {"非控制": 1} | {} | 是 | {} |
| 切换为 | None | {"对象功能": "车外行人警示音", "调节内容": "音效"} | NONE | NONE | NONE | 1 | 车外行人警示音切换为音效二 | {"非控制": 1} | {} | 是 | {} |
| 切换为 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 1 | 音效模式切换为古典之韵 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | None | {"对象功能": "电动出风口", "调节内容": "风向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 二排电动出风口切换为左右扫风模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | None | {"功能": "智慧巡航", "调节内容": "车速", "子功能": "限速偏移"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 限速偏移切换为负五公里每小时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | None | {"调节内容": "音量"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 语音音量切换为默认 | {"非控制": 1} | {} | 是 | {} |
| 切换为 | None | {"对象功能": "除雾", "调节内容": "时长"} | NONE | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | 1 | 自动除雾切换为全时开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 切换为吹脚 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | 仪表 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 仪表切换为驾驶模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | 头枕音响播放 | {} | NONE | NONE | NONE | 1 | 切换为头枕音响播放 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为 | 座椅 | {"调节内容": "座椅记忆位置"} | NONE | NONE | NONE | 1 | 座椅记忆位置切换为上一个 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换为关闭 | 外后视镜 | {"对象功能": "倒车下翻"} | NONE | NONE | NONE | 1 | 外后视镜倒车下翻切换为关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换到 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 1 | 让音效模式切换到爵士乐章 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换到 | None | {"调节内容": "动力模式"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 动力模式切换到纯电驾驶模式切换到标准 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换到 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 切换到吹面吹脚模式温度调到二十度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换到 | None | {"功能": "泊车"} | NONE | NONE | NONE | 1 | 切换到泊车设置页 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换到 | None | {"对象功能": "车模", "调节内容": "颜色"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 车模颜色切换到卡其白 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换到 | None | {"调节内容": "声音"} | NONE | NONE | NONE | 1 | 切换到声音设定 | {"非控制": 1} | {} | 是 | {} |
| 切换到 | 底盘 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 底盘切换到动态模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换到 | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 切换到泥泞驾驶模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换成 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 打开全部车窗切换成日间模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换成 | None | {"对象功能": "报警提示音", "调节内容": "音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 报警提示音切换成中 | {"非控制": 1} | {} | 是 | {} |
| 切换成 | None | {"功能": "侧后辅助", "调节内容": "预警方式", "子功能": "后方横向来车预警"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 后方横向来车预警切换成声音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换成 | 冰箱 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 冰箱切换成红酒模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换成 | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 把汽车运行模式切换成运动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换成 | 音响 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 音响切换成共享模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换至 | None | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 1 | 打开空调切换至外循环 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 切换至 | 驾驶 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 驾驶模式切换至个性化模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 加强 | None | {"对象功能": "干燥"} | NONE | NONE | NONE | 1 | 我要加强干燥和智能洗的功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 升 | 座椅 | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 座椅温度升到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 升起 | 窗 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 升起主驾驶窗打开空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 升起来 | 隔断 | {} | NONE | NONE | NONE | 1 | 隔断升起来 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 升高 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 语音音量升高到30% | {"非控制": 1} | {} | 是 | {} |
| 取消 | None | {"对象功能": "儿童锁"} | NONE | NONE | NONE | 1 | 儿童锁键为我取消 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 取消 | None | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 取消全部静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 取消 | None | {"对象功能": "同步", "调节内容": "温度"} | NONE | NONE | NONE | 1 | 取消温度同步 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 取消 | None | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 1 | 取消小憩模式关闭小憩模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 取消 | None | {"对象功能": "低速行人报警设备"} | NONE | NONE | NONE | 1 | 让低速行人报警设备取消 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 取消 | None | {"调节内容": "风量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 取消快速风量 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 取消 | None | {"调节内容": "风速"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 取消快速风速 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 取消 | None | {"对象功能": "驻车档解锁功能"} | NONE | NONE | NONE | 1 | 驻车档解锁功能取消 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 取消 | None | {"功能": "倒车影像"} | NONE | NONE | NONE | 1 | 我想把倒车影像取消 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 取消 | None | {"对象功能": "投屏"} | NONE | NONE | NONE | 1 | 帮我取消手机投屏的运行 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 取消 | None | {"功能": "路口放大图"} | NONE | NONE | NONE | 1 | 取消路口放大图 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 取消 | 电视屏 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 电视屏取消静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 变 | None | {"调节内容": "风速"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 变高一些风速 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 变 | None | {"调节内容": "温度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 变小点温度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 变成 | None | {"调节内容": "亮度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 屏幕调成深色模式变成最暗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 变成 | 空气净化器 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 空气净化器变成自动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 变更为 | 开车模式 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 开车模式变更为雪地模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 变更到 | 座椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 座椅帮我变更到一个更适合我的温度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 可以关了 | None | {"功能": "发动机启停"} | NONE | NONE | NONE | 1 | 发动机启停可以关了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 可以关闭 | None | {"功能": "座舱过热保护"} | NONE | NONE | NONE | 1 | 座舱过热保护可以关闭吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 合上 | 交流端盖 | {"对象功能": "交流电"} | NONE | NONE | NONE | 1 | 合上交流端盖 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 合上 | 充电盖 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 把车后充电盖合上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 合上 | 天窗玻璃 | {"调节内容": "幅度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 不要漏那么多天窗玻璃给合上20%吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 合上 | 门 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 合上主驾的门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 合拢 | 天窗窗帘 | {"调节内容": "幅度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 合拢20%的天窗窗帘 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 合拢 | 车窗 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 帮我合拢左前的车窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 向外显露 | 后视镜 | {} | NONE | NONE | NONE | 1 | 后视镜向外显露 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | None | {"调节内容": "风向"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 前排启动左右扫风模式 | {"已知但不开放": 1} | {} | 是 | {} |
| 启动 | None | {"对象功能": "儿童安全锁"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 启动右侧儿童安全锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | None | {"功能": "辅助驾驶", "子功能": "辅助驾驶"} | NONE | NONE | NONE | 1 | 辅助驾驶启动成我不需要辅助驾驶 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | None | {} | NONE | NONE | NONE | 1 | 启动流媒体显示 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | None | {"调节内容": "风"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 启动高风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | None | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 启动主驾休憩照明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | None | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 启动左后侧语音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | None | {"功能": "停车助手"} | NONE | NONE | NONE | 1 | 启动停车助手 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | None | {"调节内容": "风"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 大风启动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | None | {"调节内容": "时长"} | NONE | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | 1 | 麻烦启动小憩模式二十分钟 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | None | {"功能": "模拟声浪", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 启动运动模拟声浪 | {"已知但不开放": 1} | {} | 是 | {} |
| 启动 | 儿童座椅 | {"对象功能": "通风", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 启动儿童座椅自然通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | 后视镜 | {} | NONE | NONE | NONE | 1 | 启动流媒体后视镜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 启动泥泞驾驶模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | 智能儿童座椅 | {"对象功能": "通风", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 智能儿童座椅启动自然通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | 空气净化功能 | {} | NONE | NONE | NONE | 1 | 启动空气净化功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启动 | 车载智能儿童座椅 | {"对象功能": "通风", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 启动车载智能儿童座椅自然风 | {"已知但不开放": 1} | {} | 是 | {} |
| 启动一下 | None | {"功能": "声浪"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 启动一下车外声浪 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启用 | None | {"对象功能": "低速行人报警"} | NONE | NONE | NONE | 1 | 把低速行人报警启用 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启用 | None | {"对象功能": "低速行人报警设备"} | NONE | NONE | NONE | 1 | 让低速行人报警设备启用 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启用 | None | {} | NONE | NONE | NONE | 1 | 车机系统启用氛围灯呼吸动态效果 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启用 | None | {"调节内容": "能量回收"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 启用能量回收自动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启用 | None | {"对象功能": "儿童保护锁"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 请启用右侧儿童保护锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启用 | None | {"对象功能": "快速充电功能"} | NONE | NONE | NONE | 1 | 启用快速充电功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 启用 | 屏 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 升级驾驶乐趣立即启用主控驾屏 | {"已知但不开放": 1} | {} | 是 | {} |
| 启用下 | None | {"对象功能": "热点"} | NONE | NONE | NONE | 1 | 马上帮我启用下热点 | {"已知但不开放": 1} | {} | 是 | {} |
| 回 | None | {} | NONE | NONE | NONE | 1 | 回桌面继续放音乐 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 增加 | None | {"调节内容": "声音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 增加导航说话的声音到极限 | {"非控制": 1} | {} | 是 | {} |
| 增加 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 语音音量增加到30% | {"非控制": 1} | {} | 是 | {} |
| 增高 | None | {"调节内容": "音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 语音给我增高成一半 | {"非控制": 1} | {} | 是 | {} |
| 复位 | 座椅 | {"调节内容": "座椅记忆位置"} | NONE | NONE | NONE | 1 | 座椅复位所有座椅复位 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 外启 | 后视镜 | {} | NONE | NONE | NONE | 1 | 后视镜外启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 多 | None | {} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 多媒体怎么声这么小给我再大10%吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 大 | None | {"调节内容": "音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 语音为我大至一半 | {"非控制": 1} | {} | 是 | {} |
| 如 | None | {"调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 如果能给我增大10%通话声音就好啦 | {"非控制": 1} | {} | 是 | {} |
| 存 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾座椅位置存到位置1 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 展开 | 上面的窗帘 | {} | NONE | NONE | NONE | 1 | 展开上面的窗帘 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 座 | 座椅 | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 座椅稍微热会儿 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"调节内容": "风量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 空调温度调到最低风量开到最大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"调节内容": "风"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 最低的风为我开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"调节内容": "风量"} | NONE | NONE | NONE | 1 | 空调温度调到二十度开风量开到最大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"调节内容": "音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 语音给我开到一半 | {"非控制": 1} | {} | 是 | {} |
| 开 | None | {"调节内容": "风量"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 整车风量开到一温度开到三二十三度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"调节内容": "温度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 帮我将温度再开高些 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"对象功能": "通风模式"} | NONE | NONE | NONE | 1 | 空调开到低一点能打开通风模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"功能": "开机音量自适应"} | NONE | NONE | NONE | 1 | 开机音量自适应开关我想要开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"功能": "座舱控温"} | NONE | NONE | NONE | 1 | 帮我开座舱控温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"对象功能": "伴你回家"} | NONE | NONE | NONE | 1 | 伴你回家开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"调节内容": "风力"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 我要把风力开为最大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"对象功能": "风扇", "调节内容": "风"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 将第二排风扇开到最高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | None | {"调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 我要开五十的音量 | {"非控制": 1} | {} | 是 | {} |
| 开 | None | {"功能": "驻车", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 开驻车舒享打开空调 | {"已知但不开放": 1} | {} | 是 | {} |
| 开 | 后背 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 副驾座椅后背设置界面帮我开一下啊 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 坐垫 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 副驾座椅坐垫配置的界面帮我把它调开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 天窗 | {} | NONE | NONE | NONE | 1 | 天窗开一开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 天窗 | {"调节内容": "幅度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 我可以把天窗开到百分之五十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 座椅 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 将设置副驾座椅的界面开一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 座椅腰部 | {} | NONE | NONE | NONE | 1 | 我想改改座椅腰部界面赶紧帮我开一开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 空气净化 | {} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 空气净化开最大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 空气净化器 | {} | NONE | NONE | NONE | 1 | 空气净化器帮我把它给调开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 窗 | {"调节内容": "透光度"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 可以帮我把后窗开到全不透明吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 窗 | {"对象功能": "透气"} | NONE | NONE | NONE | 1 | 开窗透气出发去公司 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 窗 | {"调节内容": "幅度"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 天窗开一点点后窗开一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 窗 | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 开窗通风关闭空调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 窗子 | {"调节内容": "幅度"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 每扇窗子都开条缝 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 窗户 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 窗户全开空调打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 蓝牙耳机 | {"调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 蓝牙耳机应该开到最大 | {"已知但不开放": 1} | {} | 是 | {} |
| 开 | 车上窗户 | {} | NONE | NONE | NONE | 1 | 开车上窗户 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 钥匙 | {"对象功能": "解锁", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 钥匙解锁只开主驾门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 门 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 我要下车帮我开驾驶位的门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 隔断 | {"调节内容": "幅度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 隔断开百分之三十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开 | 雾灯 | {"车外灯类型": "雾灯"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 起雾了快开前雾灯 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一下 | None | {} | NONE | NONE | NONE | 1 | 开一下导航吗看下两条路那条路径 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一下 | None | {"对象功能": "除湿模式"} | NONE | NONE | NONE | 1 | 把除湿模式开一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一下 | None | {"功能": "开机动画音乐"} | NONE | NONE | NONE | 1 | 开一下开机动画音乐 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一下 | 座椅 | {} | NONE | NONE | NONE | 1 | 帮我开一下座椅设置界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一下 | 座椅 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 开一下后排座椅的设置页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一下 | 座椅后背 | {} | NONE | NONE | NONE | 1 | 座椅后背设置界面帮我开一下啊 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一下 | 座椅腰部 | {} | NONE | NONE | NONE | 1 | 帮我开一下座椅腰部设置界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一下 | 椅坐垫 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 开一下后排座椅坐垫调节界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一下 | 空气净化器 | {} | NONE | NONE | NONE | 1 | 开一下空气净化器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一下 | 窗帘 | {} | NONE | NONE | NONE | 1 | 把窗帘开一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一开 | None | {"功能": "车道偏离报警", "子功能": "车道偏离报警"} | NONE | NONE | NONE | 1 | 帮我开一开车道偏离报警的设置界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开一点通风 | 天窗 | {} | NONE | NONE | NONE | 1 | 天窗开一点通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开下 | None | {"对象功能": "风窗加热"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 后风窗加热开关开下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开下 | None | {"功能": "车道辅助"} | NONE | NONE | NONE | 1 | 我要在这条车道上行驶赶紧帮我开下保持功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开下 | None | {"调节内容": "播报音量调节"} | NONE | NONE | NONE | 1 | 导航播报音量调节页开下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开下 | None | {"功能": "座舱控温"} | NONE | NONE | NONE | 1 | 我要开下座舱控温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开下 | 窗户 | {} | NONE | NONE | NONE | 1 | 帮我开下窗户 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开个 | 门 | {} | NONE | NONE | NONE | 1 | 开个门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开了 | None | {"功能": "电池包主动保温"} | NONE | NONE | NONE | 1 | 给我开了电池包主动保温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "模拟声浪"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 车外模拟声浪开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "车道辅助", "子功能": "车道偏向预警"} | NONE | NONE | NONE | 1 | 开启车道偏向预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "通风模式"} | NONE | NONE | NONE | 1 | 开空空调开启通风模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 开启吹脸聚焦模式 | {"已知但不开放": 1} | {} | 是 | {} |
| 开启 | None | {"对象功能": "按键声音"} | NONE | NONE | NONE | 1 | 设置按键声音为开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "狭窄道路"} | NONE | NONE | NONE | 1 | 狭窄道路开启影像 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "智慧巡航", "子功能": "辅助驾驶"} | NONE | NONE | NONE | 1 | 把辅助驾驶改为开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "出风口"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 温度调到二十度开启后排出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"调节内容": "风"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 开启中速的风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "开机声音开启", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 开机声音开启静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "前向辅助", "子功能": "前向碰撞预警"} | NONE | NONE | NONE | 1 | 把前向碰撞预警改为开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "显示"} | NONE | NONE | NONE | 1 | 开启显示面板 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "限速告警", "子功能": "限速告警"} | NONE | NONE | NONE | 1 | 开启限速告警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "进入窄道时开启预览"} | NONE | NONE | NONE | 1 | 进入窄道时开启预览 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"调节内容": "风量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 快速风量开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "低速行人报警"} | NONE | NONE | NONE | 1 | 让低速行人报警开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "ACC"} | NONE | NONE | NONE | 1 | 开启自动循环开启ACC | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "背光联动"} | NONE | NONE | NONE | 1 | 请设置背光联动为开启状态 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "均衡器", "调节内容": "音效"} | NONE | NONE | NONE | 1 | 让均衡器开启流行音效 | {"非控制": 1} | {} | 是 | {} |
| 开启 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 1 | 开启歌剧声像体验 | {"非控制": 1} | {} | 是 | {} |
| 开启 | None | {"功能": "前向辅助"} | NONE | NONE | NONE | 1 | 设置后方交叉路口来车预警为开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "前向辅助", "子功能": "碰撞辅助"} | NONE | NONE | NONE | 1 | 开启碰撞辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "限速辅助", "子功能": "限速辅助"} | NONE | NONE | NONE | 1 | 开启限速辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "弯到照明"} | NONE | NONE | NONE | 1 | 我想开启弯到照明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"调节内容": "风向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 请确保上下扫风模式已开启 | {"已知但不开放": 1} | {} | 是 | {} |
| 开启 | None | {"功能": "碰撞安全辅助", "子功能": "碰撞安全辅助"} | NONE | NONE | NONE | 1 | 请帮我碰撞安全辅助开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"调节内容": "张数"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 开启车前三连拍 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "延迟照明"} | NONE | NONE | NONE | 1 | 开启延迟照明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"调节内容": "风向"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 前排开启左右摇头风扫模式 | {"已知但不开放": 1} | {} | 是 | {} |
| 开启 | None | {"对象功能": "儿童锁"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 把左边儿童锁设为开启状态 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "驻车", "调节内容": "摄像头模式"} | NONE | NONE | NONE | 1 | 开启驻车拍照 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"调节内容": "动力来源"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 我要把燃油优先功能开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "伴我照亮回家"} | NONE | NONE | NONE | 1 | 开启伴我照亮回家 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "蓝牙"} | NONE | NONE | NONE | 1 | 你现在蓝牙开启着吗啊 | {"已知但不开放": 1} | {} | 是 | {} |
| 开启 | None | {"功能": "限速警告音", "子功能": "限速警告音"} | NONE | NONE | NONE | 1 | 请开启限速警告音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"调节内容": "摄像头模式"} | NONE | NONE | NONE | 1 | 开启录像录音功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"对象功能": "去霜"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 开启后去霜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "座舱控温"} | NONE | NONE | NONE | 1 | 要开启座舱控温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | None | {"功能": "盲区监测"} | NONE | NONE | NONE | 1 | 开启盲区监测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 上面的窗帘 | {} | NONE | NONE | NONE | 1 | 上面的窗帘给我开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 儿童座椅 | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 儿童座椅开启通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 后背 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾座椅后背帮我把它的设置界面开启一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 坐垫 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 副驾座椅坐垫帮我把它的设置界面开启一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 坐垫 | {"调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 1 | 开启左前侧小腿主动锻炼坐垫 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 座椅 | {"对象功能": "声场优化"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 车内座椅声场优化模式开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 座椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 导航去公司开启座椅加热开启座椅按摩 | {"已知但不开放": 1} | {} | 是 | {} |
| 开启 | 整车 | {"功能": "智慧巡航", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 自动驾驶模式开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 智能除味 | {} | NONE | NONE | NONE | 1 | 开启智能除味 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 电动门 | {} | NONE | NONE | NONE | 1 | 开启电动门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 相机 | {} | NONE | NONE | NONE | 1 | 设置相机为开启状态 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 空气净化 | {} | NONE | NONE | NONE | 1 | 关闭车窗开启空气净化 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 行车记录仪 | {} | NONE | NONE | NONE | 1 | 把行车记录仪调整到开启模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 顶棚屏 | {} | NONE | NONE | NONE | 1 | 开启顶棚屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启 | 香薰发射器 | {} | NONE | NONE | NONE | 1 | 开启香薰发射器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启一下 | None | {"功能": "主动恒温"} | NONE | NONE | NONE | 1 | 要开启一下主动恒温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开启一下 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 开启一下维修模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开始 | None | {"功能": "智慧巡航", "子功能": "自动领航"} | NONE | NONE | NONE | 1 | 开始使用自动领航这个功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开始 | None | {"对象功能": "充电"} | NONE | NONE | NONE | 1 | 我要开始充电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开始 | None | {"对象功能": "接近照明"} | NONE | NONE | NONE | 1 | 我想开始接近照明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开始 | None | {"对象功能": "除霜"} | NONE | NONE | NONE | 1 | 开始除霜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开开 | None | {"对象功能": "WIFI"} | NONE | NONE | NONE | 1 | 开开wifi设置功能 | {"已知但不开放": 1} | {} | 是 | {} |
| 开开 | None | {"功能": "全景"} | NONE | NONE | NONE | 1 | 把全景开开全部打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开开 | None | {} | NONE | NONE | NONE | 1 | 给我开开消息中心 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开开 | 冰箱 | {} | NONE | NONE | NONE | 1 | 冰箱童锁为我开开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开开 | 天窗 | {} | NONE | NONE | NONE | 1 | 把天窗和车窗开开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开开 | 座椅 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 驾驶位位置调节开开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开开 | 窗帘 | {} | NONE | NONE | NONE | 1 | 把窗帘给我开开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开开 | 窗户 | {} | NONE | NONE | NONE | 1 | 窗户给我开开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开开 | 车上窗户 | {} | NONE | NONE | NONE | 1 | 开开车上窗户 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 开开 | 车窗 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 把车窗全部都开开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 弄回去 | 座椅 | {"调节内容": "座椅记忆位置"} | NONE | NONE | NONE | 1 | 刚刚的座椅设置给我弄回去 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 归位 | 座椅 | {"调节内容": "座椅记忆位置"} | NONE | NONE | NONE | 1 | 降下前排车窗打开驻车舒享模式座椅归位 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 往后滑 | 天窗 | {"调节内容": "幅度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 帮我把天窗往后滑一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 往后移 | 天窗 | {"调节内容": "幅度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 天窗往后移一些 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 往外翻 | 后视镜 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 右后视镜往外翻 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 恢复 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 恢复默认设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 恢复 | 抬头显示 | {"调节内容": "角度"} | NONE | NONE | NONE | 1 | 恢复抬头显示角度记忆 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 恢复正常 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 副座椅恢复正常 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 恢复默认 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾座椅恢复默认 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 我 | None | {"调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 我想要声音再大一点10%就可以 | {"非控制": 1} | {} | 是 | {} |
| 我想看 | None | {"功能": "三六零全景影像"} | NONE | NONE | NONE | 1 | 我想看三六零全景影像 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 我要 | None | {"对象功能": "对外供电"} | NONE | NONE | NONE | 1 | 我要对外供电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "手机无线充电"} | NONE | NONE | NONE | 1 | 打开车窗打开遮阳帘打开氛围灯播放周杰伦的音乐打开手机无线充电 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {"功能": "泊车", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 泊车媒体音量设置为关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "座舱主动恒温"} | NONE | NONE | NONE | 1 | 打开座舱主动恒温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "接近照明"} | NONE | NONE | NONE | 1 | 设置红灯制动辅助打开接近照明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "开机动画音乐"} | NONE | NONE | NONE | 1 | 打开开机动画音乐打开报警语音播报 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "报警语音播报"} | NONE | NONE | NONE | 1 | 打开开机动画音乐打开报警语音播报 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "人脸识别"} | NONE | NONE | NONE | 1 | 打开人脸识别开关 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "风扇"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开左后风扇 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "摄像头模式"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 车内短视频拍摄 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "车道辅助", "子功能": "车道偏离辅助"} | NONE | NONE | NONE | 1 | 打开车道偏离辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "亮度"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 打开亮度模式智能切换开关 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "行车保电"} | NONE | NONE | NONE | 1 | 打开行车保电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "前向辅助", "子功能": "后交叉路口辅助"} | NONE | NONE | NONE | 1 | 后面交叉路有车的情况下提醒我 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "车窗除霜"} | NONE | NONE | NONE | 1 | 关掉前挡风除雾把车窗除霜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "生命监测"} | NONE | NONE | NONE | 1 | 生命监测打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "前车起步提醒", "子功能": "前车起步提醒"} | NONE | NONE | NONE | 1 | 打开前车起步提醒页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "出风口"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 关闭行人警示音打开主驾出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "无感进出"} | NONE | NONE | NONE | 1 | 打开无感进出 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "风向"} | NONE | NONE | NONE | 1 | 风向打开 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {"功能": "交通标志", "子功能": "超速限制"} | NONE | NONE | NONE | 1 | 打开超速限制 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "模式"} | NONE | QUANTIFIED_OR_LEVEL | TEXT_ENUM_OR_OTHER | 1 | 打开最大制冷 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {"对象功能": "风扇"} | NONE | NONE | NONE | 1 | 关闭空调打开风扇 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "时长"} | NONE | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | 1 | 打开小憩模式半个小时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "风扇"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开主驾风扇 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "全景影视"} | NONE | NONE | NONE | 1 | 打开全景影视 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "车道辅助", "子功能": "车道偏离报警"} | NONE | NONE | NONE | 1 | 打开车道偏离报警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "童锁"} | NONE | NONE | NONE | 1 | 到最后打开童锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "前横穿侧向预警", "子功能": "前横穿侧向预警"} | NONE | NONE | NONE | 1 | 打开前横穿侧向预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "蓝牙", "调节内容": "模式"} | NONE | NONE | NONE | 1 | 播放蓝牙模式蓝牙音乐 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {"对象功能": "按", "调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 1 | 打开左前侧肩部经典按 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "行车关窗"} | NONE | NONE | NONE | 1 | 打开行车关窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "负离子功能"} | NONE | NONE | NONE | 1 | 帮我打开负离子功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "自动辅助导航驾驶", "子功能": "自动辅助导航驾驶"} | NONE | NONE | NONE | 1 | 打开自动辅助导航驾驶 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "胎压监测"} | NONE | NONE | NONE | 1 | 停止播放音乐打开四轮胎压 | {"非控制": 1} | {} | 是 | {} |
| 打开 | None | {"功能": "城市智能领航辅助", "子功能": "城市智能领航辅助"} | NONE | NONE | NONE | 1 | 打开城市智能领航辅助页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "均衡器"} | NONE | NONE | NONE | 1 | 打开均衡器设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "风量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 为我将风量打开最大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "蓝牙主动降噪"} | NONE | NONE | NONE | 1 | 打开蓝牙主动降噪 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开主驾的腾讯视频 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "车道辅助", "子功能": "车道引导"} | NONE | NONE | NONE | 1 | 打开车道引导 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "声浪模拟"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开外部声浪模拟界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "按键音", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 按键静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "开机音乐动画"} | NONE | NONE | NONE | 1 | 打开开机音乐动画 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "一键翻折"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 我想打开主驾的一键翻折 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "胎压单位"} | NONE | NONE | NONE | 1 | 打开胎压单位设置页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "动力电池包主动保温"} | NONE | NONE | NONE | 1 | 打开动力电池包主动保温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "城市领航辅助功能", "子功能": "城市领航辅助功能"} | NONE | NONE | NONE | 1 | 打开城市领航辅助功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "通风", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 关闭空调打开自通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "声浪仿真"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开内部声浪仿真界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "电池包插枪保温"} | NONE | NONE | NONE | 1 | 打开电池包插枪保温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "音量"} | NONE | NONE | NONE | 1 | 打开通话音量设置页面 | {"非控制": 1} | {} | 是 | {} |
| 打开 | None | {"对象功能": "低速行人报警"} | NONE | NONE | NONE | 1 | 低速行人报警打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "前方侧向交通辅助", "子功能": "前方侧向交通辅助"} | NONE | NONE | NONE | 1 | 帮我把前方侧向交通辅助打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "开机音量自适应"} | NONE | NONE | NONE | 1 | 打开开机音量自适应 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "风力"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 温度调到最高挡打开最大风力 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "行车保电", "子功能": "智能保电"} | NONE | NONE | NONE | 1 | 打开智能保电与补电页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "交通标志识别", "子功能": "交通标志识别"} | NONE | NONE | NONE | 1 | 打开交通标志识别 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "充电"} | NONE | NONE | NONE | 1 | 进入充电选项 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "近距离前向碰撞预警", "调节内容": "距离", "子功能": "近距离前向碰撞预警"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 打开近距离前向碰撞预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "车外低速报警音"} | NONE | NONE | NONE | 1 | 上一个车外低速报警音 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {"对象功能": "电动吹风口"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开三排电动吹风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "方便进出"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开二排左方便进出 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "夜视系统", "子功能": "近红外夜视"} | NONE | NONE | NONE | 1 | 打开近红外夜视 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "侧后辅助", "子功能": "后向横穿"} | NONE | NONE | NONE | 1 | 打开后向横穿 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "车窗锁"} | NONE | NONE | NONE | 1 | 车窗解锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "出风口", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 打开手动出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "预防座舱内过热保护"} | NONE | NONE | NONE | 1 | 将预防座舱内过热保护打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "显示连接设备"} | NONE | NONE | NONE | 1 | 显示连接设备 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "声音平衡"} | NONE | NONE | NONE | 1 | 打开声音平衡 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "儿童危险动作检测"} | NONE | NONE | NONE | 1 | 打开儿童危险动作检测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "左电动出风口"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开主驾左电动出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "车载热点"} | NONE | NONE | NONE | 1 | 没网络给我打开车载热点开关 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {"功能": "学习泊车"} | NONE | NONE | NONE | 1 | 打开学习泊车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "除雾"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 前挡除雾 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "记忆泊车"} | NONE | NONE | NONE | 1 | 打开记忆泊车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "车道辅助", "子功能": "车道偏差预警"} | NONE | NONE | NONE | 1 | 打开车道偏差预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "连续说"} | NONE | NONE | NONE | 1 | 连续说开关打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "如果我占用了应急车道请提醒我"} | NONE | NONE | NONE | 1 | 如果我占用了应急车道请提醒我 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "语音消息播报"} | NONE | NONE | NONE | 1 | 语音消息播报打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "车道辅助", "调节内容": "预警方式"} | NONE | NONE | NONE | 1 | 打开车道偏离纠正 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "盲区提醒"} | NONE | NONE | NONE | 1 | 打开盲区提醒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "出风口", "调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 副驾出风口自动化风向调成自由风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "车外低速报警"} | NONE | NONE | NONE | 1 | 打开车外低速报警 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {"对象功能": "随动座椅"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开副驾随动座椅 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "胎压基数"} | NONE | NONE | NONE | 1 | 打开胎压基数设置页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "三六零全景"} | NONE | NONE | NONE | 1 | 打开前排车窗打开三六零全景 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "全景影像", "调节内容": "视图"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 打开全景影像的行星视角 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "右出风口"} | NONE | NONE | NONE | 1 | 打开右出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "交通标志", "调节内容": "灵敏度", "子功能": "限速报警"} | NONE | NONE | NONE | 1 | 打开限速报警灵敏度页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "寻车模式"} | NONE | NONE | NONE | 1 | 打开寻车模式页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "限速提醒", "子功能": "限速提醒"} | NONE | NONE | NONE | 1 | 打开限速提醒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "驻车模式"} | NONE | NONE | NONE | 1 | 打开驻车模式打开后视镜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "盲区检测预警功能"} | NONE | NONE | NONE | 1 | 盲区检测预警功能打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "设备管理器"} | NONE | NONE | NONE | 1 | 打开设备管理器菜单 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "行车自动落锁"} | NONE | NONE | NONE | 1 | 打开行车自动落锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "三六零影像"} | NONE | NONE | NONE | 1 | 打开三六零影像 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "方便进出"} | NONE | NONE | NONE | 1 | 打开方便进出 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "ACC"} | NONE | NONE | NONE | 1 | 打开ACC临时停车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "手势静音", "子功能": "手势静音"} | NONE | NONE | NONE | 1 | 打开手势静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "透气"} | NONE | NONE | NONE | 1 | 回到首页透气模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "伴你回家"} | NONE | NONE | NONE | 1 | 伴你回家打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "二氧化碳浓度监测"} | NONE | NONE | NONE | 1 | 二氧化碳浓度监测打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "无线电充"} | NONE | NONE | NONE | 1 | 打开无线电充 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "全景影像", "调节内容": "视图"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 打开全景影像左后视角 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "道路标识识别", "子功能": "道路标识识别"} | NONE | NONE | NONE | 1 | 打开道路标识识别 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "限速辅助", "子功能": "限速辅助"} | NONE | NONE | NONE | 1 | 打开限速辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "出风口"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开后排右出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "窗洗涤模式"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开后窗洗涤模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "锁车关窗"} | NONE | NONE | NONE | 1 | 打开锁车关窗页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "车道辅助", "调节内容": "音效", "子功能": "车道偏离"} | NONE | NONE | NONE | 1 | 偏离车道的时候蜂鸣提醒我 | {"非控制": 1} | {} | 是 | {} |
| 打开 | None | {"功能": "车速提醒"} | NONE | NONE | NONE | 1 | 打开车速提醒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "微升微降"} | NONE | NONE | NONE | 1 | 微升微降打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "通风模式"} | NONE | NONE | NONE | 1 | 关闭香氛打开通风模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "连接管理器"} | NONE | NONE | NONE | 1 | 打开连接管理器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "来电语音播报"} | NONE | NONE | NONE | 1 | 打开来电语音播报 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "座舱主动温控系统"} | NONE | NONE | NONE | 1 | 打开座舱主动温控系统 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "电动出风口"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开主驾电动出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "侧后辅助", "子功能": "后向目标横穿预警"} | NONE | NONE | NONE | 1 | 打开后向目标横穿预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "锁车声音"} | NONE | NONE | NONE | 1 | 打开锁车声音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "模式"} | NONE | NONE | QUANTIFIED_OR_LEVEL | 1 | 导航音量最小化 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "车道辅助", "子功能": "偏离车道预警"} | NONE | NONE | NONE | 1 | 打开偏离车道预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "声浪"} | NONE | NONE | NONE | 1 | 后一个我要选声浪 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "零重力"} | NONE | NONE | NONE | 1 | 我要享受零重力模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "加热"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开热点打开迎宾打开音乐律动打开前排加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "高级驾驶辅助", "子功能": "高级驾驶辅助"} | NONE | NONE | NONE | 1 | 高级驾驶辅助打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "下坡行驶辅助"} | NONE | NONE | NONE | 1 | 打开下坡行驶辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "负离子"} | NONE | NONE | NONE | 1 | 打开负离子设置项 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 帮我打开到最高档位 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "闭锁音效"} | NONE | NONE | NONE | 1 | 帮我打开闭锁音效 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "中距离前向碰撞预警", "调节内容": "距离", "子功能": "中距离前向碰撞预警"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 打开中距离前向碰撞预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "连接了什么设备"} | NONE | NONE | NONE | 1 | 打开连接了什么设备 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "吹风"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开后排吹风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "智慧巡航", "子功能": "辅助我进行车道变更"} | NONE | NONE | NONE | 1 | 辅助我进行车道变更 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "来电语音播报模式"} | NONE | NONE | NONE | 1 | 打开来电语音播报模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "蓝牙通话降噪"} | NONE | NONE | NONE | 1 | 打开蓝牙通话降噪 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {"功能": "发动机启停"} | NONE | NONE | NONE | 1 | 把发动机启停的状态设置为开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "限速报警", "子功能": "限速报警"} | NONE | NONE | NONE | 1 | 打开限速报警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "生命监测"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开车内生命监测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "全景模式"} | NONE | NONE | NONE | 1 | 打开全景模式打开酷狗音乐 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "风窗加热"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开后风窗加热开关 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "除霜模式"} | NONE | NONE | NONE | 1 | 吹脚除霜模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "驾驶员监测系统", "子功能": "驾驶员疲劳监测"} | NONE | NONE | NONE | 1 | 打开驾驶员疲劳监测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "动能回收"} | NONE | NONE | NONE | 1 | 打开动能回收调到最高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "NCA"} | NONE | NONE | NONE | 1 | 启用车辆通信系统 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "除霜", "调节内容": "档位"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 最大除霜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "紧急转向辅助", "子功能": "紧急转向辅助"} | NONE | NONE | NONE | 1 | 帮我把紧急转向辅助打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 打开天窗打开通风打开加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "低速提示音"} | NONE | NONE | NONE | 1 | 关闭大灯和低速提示音 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {"对象功能": "左电动出风口"} | NONE | NONE | NONE | 1 | 打开左电动出风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "折叠", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 自动折叠打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "侧后辅助", "子功能": "侧边距离报警"} | NONE | NONE | NONE | 1 | 打开侧边距离报警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "侧窗锁"} | NONE | NONE | NONE | 1 | 打开侧窗锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "超速提醒", "子功能": "超速提醒"} | NONE | NONE | NONE | 1 | 打开超速提醒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "应急车道占用提醒"} | NONE | NONE | NONE | 1 | 帮我把应急车道占用提醒打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "前向预碰撞辅助", "子功能": "前向预碰撞辅助"} | NONE | NONE | NONE | 1 | 打开前向预碰撞辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "网络"} | NONE | NONE | NONE | 1 | 打开网络再打开二十六 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "座舱控温系统"} | NONE | NONE | NONE | 1 | 打开座舱控温系统 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "座舱监测系统", "子功能": "行为监测"} | NONE | NONE | NONE | 1 | 打开行为监测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "自动泊车"} | NONE | NONE | NONE | 1 | 开始执行停车助手功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "声音优化"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开驾驶员声音优化界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "玻璃除霜"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开打开后视镜及前后玻璃除霜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "行人提醒音"} | NONE | NONE | NONE | 1 | 打开行人提醒音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "这台车热点"} | NONE | NONE | NONE | 1 | 打开这台车热点 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {"对象功能": "声音均衡"} | NONE | NONE | NONE | 1 | 打开声音均衡界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "报警提示音"} | NONE | NONE | NONE | 1 | 打开报警提示音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "行人警示音"} | NONE | NONE | NONE | 1 | 打开行人警示音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "右向辅助"} | NONE | NONE | NONE | 1 | 打开右向辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "报警语音", "调节内容": "音量"} | NONE | NUMBER | NONE | 1 | 报警语音音量打开成30 | {"非控制": 1} | {} | 是 | {} |
| 打开 | None | {"功能": "前向辅助", "子功能": "后方侧向交通辅助"} | NONE | NONE | NONE | 1 | 把后方侧向交通辅助调节为可用 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "导航时降低媒体音量"} | NONE | NONE | NONE | 1 | 打开导航时降低媒体音量 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "打开连接设备"} | NONE | NONE | NONE | 1 | 打开连接设备 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "座舱监测系统", "子功能": "危险行为监测"} | NONE | NONE | NONE | 1 | 打开危险行为监测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "车外报警"} | NONE | NONE | NONE | 1 | 打开内循环打开车外报警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "全景影像系统"} | NONE | NONE | NONE | 1 | 打开全景影像系统 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "泊出"} | NONE | NONE | NONE | 1 | 我要泊出 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "手机充电"} | NONE | NONE | NONE | 1 | 打开空调打开手机充电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "蓝牙可见搜索"} | NONE | NONE | NONE | 1 | 打开蓝牙可见搜索 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | None | {"对象功能": "弯路照明"} | NONE | NONE | NONE | 1 | 打开弯路照明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "前向辅助", "子功能": "前向碰撞预警"} | NONE | NONE | NONE | 1 | 更改前向碰撞预警为打开状态 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "加热喷水嘴"} | NONE | NONE | NONE | 1 | 打开加热喷水嘴 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "等离子"} | NONE | NONE | NONE | 1 | 打开等离子空气净化 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "泊车辅助"} | NONE | NONE | NONE | 1 | 打开泊车辅助 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "智能感光"} | NONE | NONE | NONE | 1 | 打开智能感光 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "右面电动吹风口"} | NONE | NONE | NONE | 1 | 打开右面电动吹风口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "时间"} | NONE | NONE | NONE | 1 | 打开时间 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "闭锁"} | NONE | NONE | NONE | 1 | 我要锁车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "回家照明延时"} | NONE | NONE | NONE | 1 | 打开回家照明延时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "车窗起雾了"} | NONE | NONE | NONE | 1 | 车窗起雾了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "开机音量自适应功能"} | NONE | NONE | NONE | 1 | 开机音量自适应功能我想要打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"对象功能": "小憩", "调节内容": "时长"} | NONE | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | 1 | 现在把小憩模式打开二十分钟 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"调节内容": "能量回馈"} | NONE | NONE | NONE | 1 | 打开能量回馈 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "泊入车"} | NONE | NONE | NONE | 1 | 我要泊入车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | None | {"功能": "交通标志", "子功能": "超速报警"} | NONE | NONE | NONE | 1 | 我希望在我超速的时候能够提醒我 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 中控 | {"对象功能": "放倒"} | NONE | NONE | NONE | 1 | 中控放倒车内空气清新模式设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 主动扩散器 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 打开主动扩散器检修 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 交流充电口盖 | {"对象功能": "交流电"} | NONE | NONE | NONE | 1 | 打开交流充电口盖 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 交流直流二合一充电口盖 | {"对象功能": "交直流电"} | NONE | NONE | NONE | 1 | 打开交流直流二合一充电口盖 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 仪表屏的 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 仪表屏的私密模式开关打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 倒后镜 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 打开倒后镜加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 充电口盖 | {} | NONE | NONE | NONE | 1 | 打开充电口盖 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 充电盖 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开后充电盖 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 充电盖口 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开后充电盖口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 全车照明 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开全车照明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 冰箱 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 打开座椅通风打开冰箱制冷 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | 冰箱 | {"对象功能": "延时断电"} | NONE | NONE | NONE | 1 | 打开冰箱延时断电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 冰箱 | {"对象功能": "童锁"} | NONE | NONE | NONE | 1 | 打开冰箱童锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 冰箱门 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开所有冰箱门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 制冷器 | {} | NONE | NONE | NONE | 1 | 打开制冷器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 制热器 | {} | NONE | NONE | NONE | 1 | 打开制热器调节页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 功放 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开车外功放 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 口盖 | {"对象功能": "慢速充电"} | NONE | NONE | NONE | 1 | 打开慢速充电口盖 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 后备箱 | {} | NONE | NONE | NONE | 1 | 把后备箱弹开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 后尾箱 | {} | NONE | NONE | NONE | 1 | 打开后尾箱关闭大灯 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 后背 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开副驾座椅后背设置界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 后视镜 | {"对象功能": "内折收"} | NONE | NONE | NONE | 1 | 后视镜内折收 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 后视镜 | {"对象功能": "倒车时后视镜倾斜", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 倒车时后视镜倾斜副驾 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 后视镜 | {"对象功能": "除霜"} | NONE | NONE | NONE | 1 | 打开后视镜除霜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 吸顶屏 | {"对象功能": "观影角度"} | NONE | NONE | NONE | 1 | 打开吸顶屏观影角度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 坐垫 | {"对象功能": "延长"} | NONE | NONE | NONE | 1 | 打开坐垫延长设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 坐垫 | {"对象功能": "翻折"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 调节HUD后排坐垫翻折 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 坐垫 | {"对象功能": "升温"} | NONE | NONE | NONE | 1 | 打开坐垫升温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 备胎装置 | {} | NONE | NONE | NONE | 1 | 打开备胎装置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 外后视镜 | {} | NONE | NONE | NONE | 1 | 打开外后视镜打开驻车舒享 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 天幕 | {"调节内容": "幅度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 天幕打开二分之一 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 天窗 | {"调节内容": "幅度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 帮我把天窗往后的幅度给我变大些 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 天窗 | {"对象功能": "透透气"} | NONE | NONE | NONE | 1 | 给我透透气天窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 头枕 | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 主驾驶头枕音量静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 安全带 | {"对象功能": "安全带报警音"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 后排安全带报警音打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 安全带 | {"对象功能": "安全带没系提醒音"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开后排安全带没系提醒音开关 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 屏 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾亮屏 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | 屏 | {"对象功能": "自动熄屏"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开副驾屏自动熄屏 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | 幕布 | {} | NONE | NONE | NONE | 1 | 关闭天窗打开幕布 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | 座位 | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 关闭低速警报打开座位通风座椅按摩 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座位 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 座位现在可以进行加热了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座垫 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开主驾座垫后背调节界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "通通风"} | NONE | NONE | NONE | 1 | 打开空调打开座椅通通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 打开空调播放音乐打开座椅加热座椅通风打开座椅按摩 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | 座椅 | {"对象功能": "放平"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 空调调到一挡主驾座椅放平座椅通风一挡 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "竖直"} | NONE | NONE | NONE | 1 | 座椅竖直 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "加热"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 前排座椅小热一会儿 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | 座椅 | {"对象功能": "放倒"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 放倒后排座椅中间扶手 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "躺下"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 二排左座椅躺下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "抬直"} | NONE | NONE | NONE | 1 | 座椅抬直 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "躺平"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 右前座椅躺平然后播放赵雷的歌 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "竖直"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 右后座椅竖直 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "直立"} | NONE | NONE | NONE | 1 | 座椅直立 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "热"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 后排座椅稍微热会儿 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "抬直"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 右后座椅抬直 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "迎宾"} | NONE | NONE | NONE | 1 | 座椅迎宾 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "智能理疗"} | NONE | NONE | NONE | 1 | 打开座椅智能理疗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "热一热"} | NONE | NONE | NONE | 1 | 座椅稍微热一热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "完全放平"} | NONE | NONE | NONE | 1 | 座椅完全放平 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "音场优化"} | NONE | NONE | NONE | 1 | 进入座椅音场优化模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "一键零重力"} | NONE | NONE | NONE | 1 | 座椅一键零重力打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "零重力"} | NONE | NONE | NONE | 1 | 打开驻车舒享模式打开零重力座椅 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "折起来"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 把后排位置折起来吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开前排座椅打开座椅按摩 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "理疗模式"} | NONE | NONE | NONE | 1 | 打开座椅理疗模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "放平"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 调节副驾车门开合角度放平后排座椅 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "直立"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 前排座椅直立然后播放上一首 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅 | {"对象功能": "竖直"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾座椅竖直 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅坐垫 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开副驾座椅坐垫调节界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅脚托 | {"对象功能": "折叠"} | NONE | NONE | NONE | 1 | 座椅脚托收起 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 座椅腰部 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开女王座椅腰部调节界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 悬架 | {"功能": "方便上下车"} | NONE | NONE | NONE | 1 | 打开悬架方便上下车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 手套箱 | {} | NONE | NONE | NONE | 1 | 打开手套箱 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 扩散器 | {} | NONE | NONE | NONE | 1 | 打开扩散器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 抬头显 | {} | NONE | NONE | NONE | 1 | 打开抬头显调整页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 抬头显示 | {} | NONE | NONE | NONE | 1 | 打开抬头显示导航到奓口天一 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 摄像头 | {} | NONE | NONE | NONE | 1 | 打开摄像头画面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 摄像头 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开车内摄像头然后开始录制 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 整车 | {"对象功能": "充电"} | NONE | NONE | NONE | 1 | 调整电池百分比 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 整车 | {"调节内容": "模式"} | NONE | NONE | NONE | 1 | 打开驾驶模式调节 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 用自定义模式驾驶 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 星空顶棚 | {"对象功能": "联动迎宾", "车内灯类型": "星空顶棚"} | NONE | NONE | NONE | 1 | 星空顶棚联动迎宾为我打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 智能儿童座椅 | {"对象功能": "通风", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 自然通风智能儿童座椅 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 智能儿童座椅 | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 智能儿童座椅打开通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 智能除味 | {} | NONE | NONE | NONE | 1 | 打开智能除味打开前排座椅按摩 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 椅背屏 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开右后排椅背屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 液晶屏 | {} | NONE | NONE | NONE | 1 | 打开液晶屏打开中控屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 照明 | {"车内灯类型": "照明"} | NONE | NONE | NONE | 1 | 打开照明设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 玻璃 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开天窗打开主驾驶玻璃 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 玻璃窗 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开前玻璃门全玻璃窗打开前面门窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 电动尾翼 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 打开电动尾翼手动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 电动门 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开右前电动门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 电椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 打开电椅加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 电源 | {} | NONE | NONE | NONE | 1 | 打开电源 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 电滑门 | {"对象功能": "感应开启"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开感应开启后排电滑门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 电视屏 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 电视屏静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 空气净化 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 打开自动空气净化 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 空气净化功能 | {} | NONE | NONE | NONE | 1 | 打开空气净化功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 空气净化器 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 中控放倒车内空气清新模式设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 空气净化器 | {} | NONE | NONE | NONE | 1 | 打开空气内循环去除车内异味 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 窗 | {"调节内容": "幅度"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 关闭空调打开透气模式主驾窗打开百分之三十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 窗帘 | {} | NONE | NONE | NONE | 1 | 我要把窗帘打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 窗帘 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 全部打开窗帘 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 窗户 | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 播放音乐打开窗户通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 窗户 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 导航去蓝石大厦把所有窗户都打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 窗玻璃 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开前窗玻璃打开示廓灯 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 脚托 | {"对象功能": "联动"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开二排右侧脚托联动调节 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 腿托 | {"对象功能": "折叠"} | NONE | NONE | NONE | 1 | 腿托收起 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 行车记录仪 | {} | NONE | NONE | NONE | 1 | 打开行车记录仪播放我喜欢的音乐 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 记录仪 | {"功能": "全景"} | NONE | NONE | NONE | 1 | 打开全景记录仪 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 车内照明 | {} | NONE | NONE | NONE | 1 | 打开车内照明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 车窗 | {"对象功能": "透气"} | NONE | NONE | NONE | 1 | 车窗透气 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 车窗 | {"对象功能": "透气"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 后排车窗透气 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 车载儿童座椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 加热车载儿童座椅 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 车载冰箱抽屉 | {} | NONE | NONE | NONE | 1 | 车载冰箱抽屉打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 车载智能儿童座椅 | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 通风车载智能儿童座椅 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 遮光板 | {} | NONE | NONE | NONE | 1 | 打开遮光板天窗翘起 | {"已知但不开放": 1} | {} | 是 | {} |
| 打开 | 遮阳 | {} | NONE | NONE | NONE | 1 | 呃关闭全车车窗把空调开到二十二度打开遮阳关闭遮阳帘 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 门 | {"对象功能": "感应", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 打开自动感应门开关 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 门 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 关闭空调打开左侧驾驶门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 门 | {} | NONE | NONE | NONE | 1 | 打开开门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 门窗 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开前玻璃门全玻璃窗打开前面门窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 门窗 | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 关闭空调打开门窗通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 门锁 | {"对象功能": "中控锁"} | NONE | NONE | NONE | 1 | 取消车辆锁定 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 门锁 | {"对象功能": "行车闭锁"} | NONE | NONE | NONE | 1 | 打开行车闭锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 门锁 | {"对象功能": "行车落锁"} | NONE | NONE | NONE | 1 | 打开行车落锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 除味 | {} | NONE | NONE | NONE | 1 | 打开除味 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 雷达 | {"对象功能": "倒车", "调节内容": "音量"} | NONE | NONE | NONE | 1 | 打开倒车雷达音量 | {"非控制": 1} | {} | 是 | {} |
| 打开 | 雷达 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 雷达音量关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 颈枕 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 打开颈枕加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 颈部 | {"对象功能": "加热"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 打开前排颈部加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 颈部 | {"对象功能": "加热"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 打开副驾颈部加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开 | 香熏 | {} | NONE | NONE | NONE | 1 | 打开香熏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开一下 | None | {"功能": "限速提醒", "子功能": "限速提醒"} | NONE | NONE | NONE | 1 | 你把限速提醒开关打开一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开一下 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 我要打开一下休息模式设置页面好吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开一下 | None | {"调节内容": "动力来源"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 请替我将燃油优先打开一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开一下 | None | {"功能": "驻车", "调节内容": "摄像头模式"} | NONE | NONE | NONE | 1 | 打开一下驻车拍照 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开一下 | None | {"对象功能": "接近照明"} | NONE | NONE | NONE | 1 | 我要打开一下接近照明好吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开一下 | None | {"功能": "限速信息提醒", "子功能": "限速信息提醒"} | NONE | NONE | NONE | 1 | 打开一下限速信息提醒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开一下 | None | {"功能": "闭锁音效"} | NONE | NONE | NONE | 1 | 打开一下闭锁音效 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打开一下 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 1 | 打开一下歌剧院音效可以吗 | {"非控制": 1} | {} | 是 | {} |
| 打开一下 | 车窗 | {} | NONE | NONE | NONE | 1 | 音乐暂停播放车窗打开一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 打打开 | None | {"功能": "驻车", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 打打开驻车舒适模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 扣一下 | 后备箱的门 | {} | NONE | NONE | NONE | 1 | 扣一下后备箱的门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 扣上 | 后备箱 | {} | NONE | NONE | NONE | 1 | 把我的后备箱扣上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 执行 | None | {"调节内容": "摄像头模式"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 执行车前缩录 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 执行 | None | {"功能": "车道变更确认功能", "子功能": "车道变更确认功能"} | NONE | NONE | NONE | 1 | 执行车道变更确认功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 执行 | None | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 1 | 下雪了给我执行能在雪地里走的功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 抬 | 车身 | {"调节内容": "高度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 车身高度抬至较高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 抬起 | None | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 抬起后俩玻璃 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 拉上 | 窗帘 | {} | NONE | NONE | NONE | 1 | 我想拉上窗帘 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 拉上 | 窗帘 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 窗帘全拉上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 拉上 | 车窗 | {} | NONE | NONE | NONE | 1 | 拉上车窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 拉开 | 窗帘 | {} | NONE | NONE | NONE | 1 | 我要把窗帘拉开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 拍 | 行车记录仪 | {"调节内容": "摄像头模式"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 拍行车记录仪的车内短视频 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 按 | 汽车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 让汽车按自定义模式运行吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 换 | None | {"调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 音量换成三级 | {"非控制": 1} | {} | 是 | {} |
| 换 | None | {"功能": "驻车", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 帮我把模式换成驻车舒享 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 换一个 | None | {} | NONE | NONE | NONE | 1 | 铃声换一个 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 换一个 | 星空顶 | {"调节内容": "模式", "车内灯类型": "星空顶"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 星空顶换一个主题 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 换个 | None | {"调节内容": "音效"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 二排音乐换个音效 | {"非控制": 1} | {} | 是 | {} |
| 换为 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 换为夜间模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 换成 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 1 | 音效换成原声模式 | {"非控制": 1} | {} | 是 | {} |
| 换成 | 仪表盘 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 你能帮我把仪表盘显示模式换成狂暴模式吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 换成 | 头枕音响 | {"调节内容": "声音来源"} | NONE | NONE | NONE | 1 | 通知和安全提醒换成头枕音响 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 换成 | 屏 | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 主驾屏换成经典模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 掀起 | 直流端盖 | {"对象功能": "直流电"} | NONE | NONE | NONE | 1 | 掀起直流端盖 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 掉下去 | 车窗 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 四个车窗全掉下去 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 提升 | 扬声器 | {"调节内容": "声音"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 提升声音的10%给外面的扬声器 | {"非控制": 1} | {} | 是 | {} |
| 撤销 | None | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 撤销所有设备的静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 撤销 | 远光灯 | {"车外灯类型": "远光灯"} | NONE | NONE | NONE | 1 | 灯光选择撤销远光灯 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 操作 | 屏 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 我想操作副驾屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 收回 | 窗帘 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 左侧窗帘收回 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 收起 | None | {"对象功能": "一键零重力坐姿"} | NONE | NONE | NONE | 1 | 收起一键零重力坐姿 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 收起 | 脚托 | {"对象功能": "收起"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 座椅主驾脚托收起 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改 | 座椅 | {"对象功能": "通风", "调节内容": "风力"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 改改座椅风力强度变得更弱些 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改一下 | 座椅 | {"对象功能": "零重力"} | NONE | NONE | NONE | 1 | 零重力座椅不合适给我改一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改个 | 空气净化 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 我要去张家干了心主驾我要改个空气净化 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改为 | None | {"对象功能": "日出日落", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 日出日落改为日出 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改为 | None | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 空调调整为一挡然后改为二十五度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改为 | 抬头显示 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 把抬头显示改为雪地模式关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改为 | 整车 | {"调节内容": "模式"} | NONE | NONE | NONE | 1 | 驾驶模式改为混那个智能模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改为 | 车辆操作模式 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 车辆操作模式改为泥泞模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改为 | 驾驶 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 驾驶模式改为沙地 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改变 | None | {"对象功能": "座椅声场优化"} | NONE | NONE | NONE | 1 | 改变座椅声场优化 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改变到 | None | {"调节内容": "音效模式"} | NONE | NONE | NONE | 1 | 音效模式改变到爵士乐章 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改成 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 改成日出模式打开酷狗音乐 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改成 | None | {"对象功能": "出风模式", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 出风模式改成镜像风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 改成 | None | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 1 | 关闭AC温度调到最低改成外循环 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 放 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 播放QQ音乐然后音量放到最小 | {"非控制": 1} | {} | 是 | {} |
| 放个 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 把空调暖风关掉放个自然风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 敞开 | 天窗窗帘 | {"调节内容": "幅度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天窗窗帘敞开20% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 敞开 | 窗子 | {"调节内容": "幅度"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 主驾窗子敞开百分之六十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 敞开 | 车顶天窗 | {} | NONE | NONE | NONE | 1 | 敞开车顶天窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 整 | None | {"调节内容": "音量"} | NONE | NUMBER | NONE | 1 | 希望以25的音量将语音调整到最佳状态 | {"非控制": 1} | {} | 是 | {} |
| 断 | None | {"功能": "疲劳驾驶提醒"} | NONE | NONE | NONE | 1 | 中断连接疲劳驾驶提醒功能的接口 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 断 | None | {"对象功能": "热点"} | NONE | NONE | NONE | 1 | 请现在为我热点帮我断 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 断 | None | {"对象功能": "车载热点"} | NONE | NONE | NONE | 1 | 暂时不需要车载热点给我把接口断了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 断开 | None | {"对象功能": "蓝牙"} | NONE | NONE | NONE | 1 | 熄灭屏幕断开关闭灯光断开蓝牙 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 断开 | 自适应大灯 | {"车外灯类型": "自适应大灯"} | NONE | NONE | NONE | 1 | 我现在要断开与自适应大灯照明的连接 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 断开一下 | None | {"对象功能": "蓝牙"} | NONE | NONE | NONE | 1 | 断开一下蓝牙吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 断开下 | None | {"对象功能": "热点"} | NONE | NONE | NONE | 1 | 帮我断开下热点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 显示 | None | {"对象功能": "设备连接器"} | NONE | NONE | NONE | 1 | 显示设备连接器菜单 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 显示 | 仪表 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 仪表显示为经典模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 显示 | 摄像头 | {"调节内容": "视图"} | NONE | NONE | NONE | 1 | 显示摄像头视图 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 暂停 | None | {"功能": "模拟一下声浪"} | NONE | NONE | NONE | 1 | 我要模拟一下声浪暂停好吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 暂停 | None | {"功能": "仿真声浪"} | NONE | NONE | NONE | 1 | 仿真声浪暂停 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 暂停 | None | {"对象功能": "滑移"} | NONE | NONE | NONE | 1 | 暂停滑移调动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 暂停 | 后备箱 | {} | NONE | NONE | NONE | 1 | 暂停后备箱 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 暂停 | 尾门 | {} | NONE | NONE | NONE | 1 | 暂停尾门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 暂停 | 空气净化 | {} | NONE | NONE | NONE | 1 | 暂停空气净化 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 暂停 | 窗帘 | {} | NONE | NONE | NONE | 1 | 暂停窗帘 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 暂停一下 | None | {"对象功能": "滑移"} | NONE | NONE | NONE | 1 | 暂停一下滑移 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 暂停调节 | 座椅头枕 | {} | NONE | NONE | NONE | 1 | 座椅头枕暂停调节 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 暗下去 | 近光灯 | {"车外灯类型": "近光灯"} | NONE | NONE | NONE | 1 | 让近光灯暗下去 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 更换 | None | {"调节内容": "浓度"} | NONE | NONE | NONE | 1 | 将香精更换为花香 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 更改 | None | {"调节内容": "铃声"} | NONE | NONE | NONE | 1 | 更改来电铃声设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 更改 | None | {"功能": "驻车", "调节内容": "时间"} | NONE | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | 1 | 把驻车的舒享时间更改到半小时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 更改 | None | {"功能": "驻车", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 我需要更改驻车舒享的设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 更改 | None | {} | NONE | NONE | NONE | 1 | 更改铃声 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 更改 | 天幕调光玻璃 | {"调节内容": "透明度"} | NONE | NONE | NONE | 1 | 更改天幕调光玻璃透明度到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 更改一下 | 座椅 | {"调节内容": "温度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 更改一下座椅的温度让它低一些 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 更改为 | 汽车驾驶模式 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 将汽车驾驶模式更改为智能型 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 更改为 | 车辆驾驶模式 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 将车辆驾驶模式更改为泥泞模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 更改为 | 驾驶 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 将驾驶模式更改为智能模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 更改成 | 椅背屏左 | {"对象功能": "息屏", "调节内容": "时长"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 后排椅背屏左自动息屏为我时长更改成10分钟 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "风量"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 查看主驾风量 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "电池电量还剩多少"} | NONE | NONE | NONE | 1 | 电池电量还剩多少 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"对象功能": "网"} | NONE | NONE | NONE | 1 | 请给我查下无线网当前的怎样 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查询纯电续航里程"} | NONE | NONE | NONE | 1 | 查询纯电续航里程 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "当前电耗多少"} | NONE | NONE | NONE | 1 | 当前电耗多少 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "胎压如何"} | NONE | NONE | NONE | 1 | 胎压如何 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查询滤芯剩余时间"} | NONE | NONE | NONE | 1 | 净水器的滤芯还剩多长的使用期限 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "电量还剩多少"} | NONE | NONE | NONE | 1 | 关闭空调电量还剩多少 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查询剩余里程"} | NONE | NONE | NONE | 1 | 查询剩余里程 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "胎温监测"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 检查左后胎温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "车子油耗是多少"} | NONE | NONE | NONE | 1 | 车子油耗是多少 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "当前车辆还能行驶多远"} | NONE | NONE | NONE | 1 | 当前车辆还能行驶多远 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "轮胎胎压正常吗"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 中间轮胎胎压正常吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查询电耗"} | NONE | NONE | NONE | 1 | 查询电耗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查询一下当前能耗多少"} | NONE | NONE | NONE | 1 | 查询一下当前能耗多少 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查询能耗统计"} | NONE | NONE | NONE | 1 | 查询能耗统计 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {} | NONE | NONE | NONE | 1 | 声音现在大小为多大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "胎压系统"} | NONE | NONE | NONE | 1 | 检查胎压系统 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查询累积能耗"} | NONE | NONE | NONE | 1 | 查询累积能耗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "当前胎温是多少"} | NONE | NONE | NONE | 1 | 当前胎温是多少 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "车内温度是多少度以上"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 车内温度是多少度以上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "冰箱现在可以冷藏吗"} | NONE | NONE | NONE | 1 | 冰箱现在可以冷藏吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "车跑了多少里路"} | NONE | NONE | NONE | 1 | 车跑了多少里路 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "车内二氧化碳查询"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 车内二氧化碳查询 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "车的油耗怎么样"} | NONE | NONE | NONE | 1 | 车的油耗怎么样 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "用多少功率充电"} | NONE | NONE | NONE | 1 | 用多少功率充电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "冰箱是在冷藏吗"} | NONE | NONE | NONE | 1 | 冰箱是在冷藏吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "轮胎压正常吗"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 后轮胎压正常吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "轮胎胎温正常吗"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 左前轮胎胎温正常吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"对象功能": "蓝牙"} | NONE | NONE | NONE | 1 | 查看蓝牙启动了没有 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查一下车内细颗粒物"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 查一下车内细颗粒物 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "还能自动驾驶多远"} | NONE | NONE | NONE | 1 | 还能自动驾驶多远 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "车内温度有多高"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 车内温度有多高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"对象功能": "无线网络"} | NONE | NONE | NONE | 1 | 请给我查看下无线网络状态怎么样 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "还要充多久的电"} | NONE | NONE | NONE | 1 | 还要充多久的电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "胎温查询"} | NONE | NONE | NONE | 1 | 胎温查询 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "轮胎气压"} | NONE | NONE | NONE | 1 | 显示轮胎气压 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "车的能耗怎么样"} | NONE | NONE | NONE | 1 | 车的能耗怎么样 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "还有多少有电"} | NONE | NONE | NONE | 1 | 还有多少有电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"对象功能": "网络"} | NONE | NONE | NONE | 1 | 我要查看下网络的怎样 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查询胎温"} | NONE | NONE | NONE | 1 | 查询胎温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "冰箱多少度"} | NONE | NONE | NONE | 1 | 冰箱多少度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "车内空气质量怎么样"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 车内空气质量怎么样 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "现在电池剩余电量是多少"} | NONE | NONE | NONE | 1 | 现在电池剩余电量是多少 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "看看还有多久"} | NONE | NONE | NONE | 1 | 我要看看还有多久 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查询当前能耗"} | NONE | NONE | NONE | 1 | 查询当前能耗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "现在轮胎气还足吗"} | NONE | NONE | NONE | 1 | 现在轮胎气还足吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "如何查胎压情况"} | NONE | NONE | NONE | 1 | 如何查胎压情况 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查看一下当前可行驶距离"} | NONE | NONE | NONE | 1 | 查看一下当前可行驶距离 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "最近的电耗怎么样"} | NONE | NONE | NONE | 1 | 最近的电耗怎么样 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "下次维修预约的时间是什么时候"} | NONE | NONE | NONE | 1 | 下次维修预约的时间是什么时候 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "总行驶里程是多少"} | NONE | NONE | NONE | 1 | 总行驶里程是多少 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查询车内空气质量"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 查询车内空气质量 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "看一下车内温度"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 我要看一下车内温度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "胎温是多少"} | NONE | NONE | NONE | 1 | 胎温是多少 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "油耗现在多少"} | NONE | NONE | NONE | 1 | 油耗现在多少 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "查询车辆总里程"} | NONE | NONE | NONE | 1 | 查询车辆总里程 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "什么时候充满电"} | NONE | NONE | NONE | 1 | 什么时候充满电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | None | {"功能": "胎压正常"} | NONE | NONE | NONE | 1 | 胎压正常吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查看 | 屏 | {"功能": "查询当前音量"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾屏查询当前音量 | {"非控制": 1} | {} | 是 | {} |
| 查看 | 摄像头 | {} | NONE | NONE | NONE | 1 | 查看摄像头 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 查询 | None | {"功能": "查看小电瓶工作状态"} | NONE | NONE | NONE | 1 | 查看小电瓶工作状态 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 滑 | 中控扶手 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 后面太挤帮忙把中控扶手向后滑 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 滑 | 中间放东西的柜子 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 中间放东西的柜子滑到前方 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 滑 | 中间的柜子 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 中间的柜子滑到车后面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 滑 | 大屏 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 滑副驾大屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 滑一下 | 中控大屏 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 滑一下中控大屏到另外一侧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 滑一下 | 大屏 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 副驾大屏滑一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 滑一下 | 大屏 | {"调节内容": "方向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 大屏向中间滑一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 滑动 | 中间放东西的柜子 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 后面太挤了帮忙把中间放东西的柜子朝车后面滑动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 滑动 | 屏 | {"调节内容": "方向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 屏往驾驶员滑动 | {"已知但不开放": 1} | {} | 是 | {} |
| 滑动 | 座椅 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 请让座椅再靠前一点吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 滑动下 | 中控大屏 | {} | NONE | NONE | NONE | 1 | 滑动下中控大屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 滑动点 | 大屏 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 滑动点副驾大屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 激活 | None | {"功能": "车速限制功能", "子功能": "车速限制功能"} | NONE | NONE | NONE | 1 | 激活车速限制功能 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 激活 | None | {"调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 激活副驾休憩模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 激活 | 仪表板 | {} | NONE | NONE | NONE | 1 | 激活仪表板上的驾驶舱显示器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 激活 | 坐垫 | {} | NONE | NONE | NONE | 1 | 座椅帮我把它坐垫设置界面给激活一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 灭掉 | 自适应大灯 | {"车外灯类型": "自适应大灯"} | NONE | NONE | NONE | 1 | 可以让自适应大灯灭掉了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 热 | 座椅 | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 热一热坐着的车子的座椅 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 现 | None | {"调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 现在的通话声音不合适再小20%就好啦 | {"非控制": 1} | {} | 是 | {} |
| 盖上 | 充电盖 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 把车前充电盖盖上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 看一下 | 行车记录仪 | {} | NONE | NONE | NONE | 1 | 帮我看一下行车记录仪最近一周副驾坐了几个人 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 看看 | None | {"调节内容": "声音"} | NONE | NONE | NONE | 1 | 看看多媒体声音设置 | {"非控制": 1} | {} | 是 | {} |
| 看看 | None | {"对象功能": "离车自动落锁"} | NONE | NONE | NONE | 1 | 看看离车自动落锁设置页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 禁 | 麦克风 | {} | NONE | NONE | NONE | 1 | 你给我禁麦克风呀 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 移 | 中控扶手 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 中控扶手移到前面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 移 | 娱乐主机大屏 | {"调节内容": "方向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 娱乐主机大屏移至驾驶员 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 移 | 座椅 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 副驾座椅移到最前面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 移 | 腿托 | {"调节内容": "方向"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 前排腿托下移 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 移 | 腿托 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 腿托上移 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 移一下 | 中控大屏 | {"调节内容": "方向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 中控大屏主驾位置移一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 移动 | 主屏 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主屏右移动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 移动 | 大屏 | {"调节内容": "方向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 移动大屏到另一边 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 移动 | 娱乐大屏 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 娱乐大屏移动向左 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 移动 | 扶手箱 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 请将扶手箱往前方移动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 移动一下 | 大屏 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 副驾大屏移动一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 终止 | None | {"对象功能": "同步", "调节内容": "温度"} | NONE | NONE | NONE | 1 | 终止温度同步 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 结束 | None | {"功能": "空气质量监测"} | NONE | NONE | NONE | 1 | 结束空气质量监测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 给关掉 | None | {"对象功能": "儿童锁"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 左边的儿童锁可以帮我把它给关掉 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 给关闭 | None | {"对象功能": "儿童锁"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 右边儿童锁请给关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 给我关了 | 安全带 | {"对象功能": "安全带未系报警"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 后排安全带未系报警开关给我关了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 给我开一下 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 抽烟模式给我开一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 给我设 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 将音量给我设到一半 | {"非控制": 1} | {} | 是 | {} |
| 给我调 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 音量给我调到百分之五十 | {"非控制": 1} | {} | 是 | {} |
| 联 | None | {"对象功能": "网"} | NONE | NONE | NONE | 1 | 现在联网了没有呢 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 落下来 | 窗户 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 把窗户全落下来把窗户全部下来 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 落锁 | None | {"对象功能": "儿童锁落锁"} | NONE | NONE | NONE | 1 | 儿童锁落锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 落锁 | None | {"对象功能": "窗户锁"} | NONE | NONE | NONE | 1 | 窗户锁落锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 解禁 | None | {"对象功能": "音随车速", "调节内容": "音随车速档位"} | NONE | NONE | NONE | 1 | 把音随车速解禁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 解锁 | None | {"对象功能": "中控锁"} | NONE | NONE | NONE | 1 | 解锁中控锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | None | {"对象功能": "安全提示音", "调节内容": "音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 安全提示音设为中 | {"非控制": 1} | {} | 是 | {} |
| 设 | None | {"调节内容": "风量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 设快速风量 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | None | {"调节内容": "能量等级回收"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 能量等级回收设为中 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | None | {"调节内容": "声音"} | NONE | NUMBER | NONE | 1 | 把0设成导航的声音 | {"非控制": 1} | {} | 是 | {} |
| 设 | None | {"调节内容": "温度"} | NONE | NUMBER | NONE | 1 | 启动空调且温度设为25度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | None | {"对象功能": "安全提示音", "调节内容": "音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 安全提示音设为高 | {"非控制": 1} | {} | 是 | {} |
| 设 | None | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 全车温度设为十八度空调风速设为四挡 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | None | {"对象功能": "方控", "调节内容": "触摸振感强度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 方控触摸振感强度设为弱 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | None | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 帮我将温度设最小 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | None | {"对象功能": "车速音量补偿", "调节内容": "音随车速档位"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 车速音量补偿设为低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | None | {"功能": "盲区预警", "调节内容": "预警方式"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 盲区预警的提示效果设为震动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | 后背门 | {"调节内容": "开启高度"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 后背门开启高度设为默认 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | 座椅 | {"对象功能": "律动", "调节内容": "律动强度"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 把主驾座椅律动设为最高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾座椅设为账号记忆 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | 座椅 | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主驾那个地方的座椅温度设的高一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | 座椅 | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | NUMBER | NONE | 1 | 主驾座椅设为1 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设 | 雷达 | {"调节内容": "音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 雷达报警音设为中 | {"非控制": 1} | {} | 是 | {} |
| 设为 | None | {"功能": "定位", "调节内容": "使用有效期"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 定位使用有效期设为12个月 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | None | {"调节内容": "透光度"} | NONE | NONE | NONE | 1 | 车顶玻璃请设为不透明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | None | {"调节内容": "预警方式"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 报警模式设为声音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | None | {"调节内容": "风速"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 风速设为自动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | None | {"调节内容": "充电上限"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 充电上限设为90% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | None | {"对象功能": "车速自动关窗", "调节内容": "车速"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 车速自动关窗设为80千米每小时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | None | {"对象功能": "左手侧吹风口", "调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 左手侧吹风口设为避人吹 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | None | {"调节内容": "供电下限"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 供电下限设为96% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | None | {"功能": "定位", "调节内容": "使用有效期"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 定位使用有效期设为本次 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | 冰箱 | {"对象功能": "延时掉电", "调节内容": "时长"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 冰箱延时掉电时间设为3小时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | 冰箱 | {"对象功能": "持续工作", "调节内容": "时长"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 冰箱持续工作时间设为30秒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | 后视镜 | {"对象功能": "倒车后视镜下翻", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 倒车后视镜下翻设为两侧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | 大灯 | {"调节内容": "模式", "车外灯类型": "大灯"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 大灯设为自动大灯 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | 座椅 | {"功能": "方便进出"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 副驾座椅方便进出设为离车加上车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | 摄像头 | {"调节内容": "使用有效期"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 摄像头使用有效期设为12个月 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 驾驶方式设为舒适 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | 近光灯 | {"调节内容": "高度", "车外灯类型": "近光灯"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 近光灯高度设为标准 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | 驾驶 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 驾驶模式设为纯电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为 | 麦克风 | {"调节内容": "使用有效期"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 麦克风使用有效期设为单次 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设为关闭 | 后视镜 | {"对象功能": "倒车后视镜下翻"} | NONE | NONE | NONE | 1 | 倒车后视镜下翻设为关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设定 | None | {"对象功能": "报警音", "调节内容": "声"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 设定报警音为小声 | {"非控制": 1} | {} | 是 | {} |
| 设定为 | None | {"调节内容": "充电上限"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 将充电上限设定为80%的电池容量 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设定为 | None | {"功能": "智慧巡航", "调节内容": "车速", "子功能": "限速报警偏差"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 限速报警偏差设定为30千米每秒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设成 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 1 | 帮我改改播报设置还是设成跑车发动机启动声吧 | {"非控制": 1} | {} | 是 | {} |
| 设成 | None | {"功能": "模拟声浪", "调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 1 | 车外模拟声浪设成狂野 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设成 | 隔断 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 隔断设成不透明 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "温度"} | NONE | NONE | NONE | 1 | 将空调设置为四挡温度设置 | {"已知但不开放": 1} | {} | 是 | {} |
| 设置 | None | {"对象功能": "放电", "调节内容": "时间"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 放电时间设置为3小时2分钟 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"功能": "自适应巡航", "调节内容": "限速"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 自适应巡航限速设置为最大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "风速"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 帮我将风速为我设置成小 | {"已知但不开放": 1} | {} | 是 | {} |
| 设置 | None | {"功能": "前向辅助", "调节内容": "距离", "子功能": "近距离前向碰撞预警"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 近距离前向碰撞预警设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "提示音效"} | NONE | NONE | NONE | 1 | 设置提示音效 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"对象功能": "出风模式", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 设置出风模式为自适应出风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"功能": "智慧巡航", "调节内容": "速度", "子功能": "LIMITER"} | NONE | NUMBER | NONE | 1 | 设置limiter的速度为80 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"对象功能": "出风口模式", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 设置出风口模式为自适应出风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"功能": "音效增强"} | NONE | NONE | NONE | 1 | 设置音效增强座椅温度太高了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "模式"} | NONE | NUMBER | RELATIVE_OR_DIRECTIONAL | 1 | 设置下坡时限制速度的速度为40 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"对象功能": "车速音量增益", "调节内容": "音随车速档位"} | NONE | NONE | NONE | 1 | 设置车速音量增益 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "风速"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 设置成极速风速 | {"已知但不开放": 1} | {} | 是 | {} |
| 设置 | None | {"调节内容": "风向"} | NONE | NONE | NONE | 1 | 设置风扇的风向为正向 | {"已知但不开放": 1} | {} | 是 | {} |
| 设置 | None | {"对象功能": "手机投屏"} | NONE | NONE | NONE | 1 | 设置手机投屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"对象功能": "音效加强"} | NONE | NONE | NONE | 1 | 设置音效加强座椅温度降到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "系统提示音"} | NONE | NONE | NONE | 1 | 设置系统提示音把所有车窗都降低一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "动力来源"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 设置为混动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"对象功能": "低速行驶车外警示音"} | NONE | NONE | NONE | 1 | 设置低速行驶车外警示音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"功能": "智慧巡航"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 设置驾驶辅助距离为2档 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"对象功能": "车外低速报警", "调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 车外低速报警设置为低 | {"非控制": 1} | {} | 是 | {} |
| 设置 | None | {"对象功能": "车外低速报警"} | NONE | NONE | NONE | 1 | 为了更安全行驶请帮我设置车外低速报警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"功能": "保养", "调节内容": "时间"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 保养时间设置最小 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "自适应转弯速度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 自适应转弯速度设置为慢 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"功能": "人脸摄像头"} | NONE | NONE | NONE | 1 | 设置人脸摄像头 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "时间"} | NONE | NONE | NONE | 1 | 时间设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"功能": "车辆盲区预警监测"} | NONE | NONE | NONE | 1 | 设置车辆盲区预警监测 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "回收等级"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 将回收等级设置为中级 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "能量回馈强度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 能量回馈强度设置为标准 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "风"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 设置风扇的风向为前 | {"已知但不开放": 1} | {} | 是 | {} |
| 设置 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 把有声书音量设置成最高 | {"非控制": 1} | {} | 是 | {} |
| 设置 | None | {"对象功能": "警报音", "调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 设置警报音为低音量 | {"非控制": 1} | {} | 是 | {} |
| 设置 | None | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 给我把温度为我设置成最小 | {"已知但不开放": 1} | {} | 是 | {} |
| 设置 | None | {"对象功能": "安全警报提示音", "调节内容": "音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 安全警报提示音设置为慢 | {"非控制": 1} | {} | 是 | {} |
| 设置 | None | {"功能": "智慧巡航", "调节内容": "车速", "子功能": "限速偏移值"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 设置限速偏移值为1千米每小时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "转弯速度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 把转弯速度设置为快 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"对象功能": "安全报警提示音", "调节内容": "音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 安全报警提示音设置为高 | {"非控制": 1} | {} | 是 | {} |
| 设置 | None | {"功能": "放电类型为对设备放电"} | NONE | NONE | NONE | 1 | 设置放电类型为对设备放电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 把亮度设置成最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"对象功能": "儿童锁"} | NONE | NONE | NONE | 1 | 设置儿童锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"调节内容": "提醒灵敏度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 提醒灵敏度设置为较早 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 对比度设置成六十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"对象功能": "低速报警"} | NONE | NONE | NONE | 1 | 设置低速报警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"功能": "盲区预警"} | NONE | NONE | NONE | 1 | 设置盲区预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"功能": "车辆超速通知", "子功能": "车辆超速通知"} | NONE | NONE | NONE | 1 | 设置车辆超速通知 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"对象功能": "车速音量补偿", "调节内容": "音随车速档位"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 我需要中等车速音量补偿设置成它 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"对象功能": "按键音", "调节内容": "音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 按键音设置为低 | {"非控制": 1} | {} | 是 | {} |
| 设置 | None | {"调节内容": "播报音量"} | NONE | NONE | NONE | 1 | 设置导航播报音量 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | None | {"功能": "车道辅助", "子功能": "车道偏离预警"} | NONE | NONE | NONE | 1 | 设置车道偏离预警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 仪表 | {"调节内容": "亮度"} | NONE | NONE | NONE | 1 | 设置仪表亮度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 仪表 | {"功能": "疲劳驾驶时长", "调节内容": "时长"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 仪表疲劳驾驶时长设置为1小时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 仪表 | {"调节内容": "明暗"} | NONE | NONE | NONE | 1 | 设置仪表明暗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 仪表屏 | {"调节内容": "亮度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 仪表屏设置为低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 仪表盘 | {"调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 我的眼睛更习惯于10%的仪表亮度麻烦设置下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 后视镜 | {"调节内容": "高度"} | NONE | NONE | NONE | 1 | 设置流媒体后视镜高度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 后视镜 | {"调节内容": "亮度"} | NONE | NONE | NONE | 1 | 设置流媒体后视镜亮度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 大灯 | {"调节内容": "高度", "车外灯类型": "大灯"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 大灯高度设置为较低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 天幕调光玻璃 | {"调节内容": "透明度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天幕调光玻璃透明度设置最大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 屁股座垫 | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 设置屁股座垫通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 屏 | {} | NONE | NONE | NONE | 1 | 打开后排空调风设置屏页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 屏 | {"调节内容": "亮度"} | TEXT_ENUM_OR_OTHER | NUMBER | NONE | 1 | 主驾屏亮度设置为20中控屏亮度设置为10 | {"已知但不开放": 1} | {} | 是 | {} |
| 设置 | 屏 | {"对象功能": "保"} | NONE | NONE | NONE | 1 | 我想设置屏保 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 座位 | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 设置座位通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 座椅 | {"调节内容": "座椅记忆位置"} | NONE | NONE | NONE | 1 | 座椅偏好设置为偏好一 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 座椅 | {"对象功能": "加", "调节内容": "温度"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 设置主驾座椅温度加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 悬架 | {"调节内容": "阻尼"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 悬架阻尼设置为偏硬 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 扬声器 | {"调节内容": "声音"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 设置一下车外扬声器让声音到50%的位置 | {"非控制": 1} | {} | 是 | {} |
| 设置 | 抬头显示 | {"调节内容": "高度"} | NONE | NONE | NONE | 1 | 怎么才能设置抬头显示的高度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 设置泥泞驾驶模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 汽车 | {"调节内容": "模式"} | NONE | NONE | NONE | 1 | 设置汽车模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 汽车运行 | {"调节内容": "模式"} | NONE | NONE | NONE | 1 | 设置汽车运行模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 电动出风口 | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 设置电动出风口出风风向为吹腹 | {"已知但不开放": 1} | {} | 是 | {} |
| 设置 | 窗口 | {} | NONE | NONE | NONE | 1 | 打开盲区预警的设置窗口给我设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置 | 雷达 | {"对象功能": "倒车", "调节内容": "声音"} | NONE | NONE | NONE | 1 | 设置倒车雷达声音地图最小主驾座椅调到最后 | {"非控制": 1} | {} | 是 | {} |
| 设置一下 | None | {"对象功能": "声音均衡器"} | NONE | NONE | NONE | 1 | 设置一下声音均衡器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置一下 | None | {"对象功能": "声场平衡"} | NONE | NONE | NONE | 1 | 我要设置一下声场平衡好吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置一下 | None | {"对象功能": "蓝牙", "调节内容": "音量"} | NONE | NONE | NONE | 1 | 设置一下蓝牙通话音量 | {"非控制": 1} | {} | 是 | {} |
| 设置一下 | None | {"调节内容": "亮度值"} | NONE | NONE | NONE | 1 | 为我设置一下亮度值 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"功能": "座舱监测系统", "调节内容": "间隔", "子功能": "危险动作检测报警"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 危险动作检测报警提醒间隔设置为3分钟 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"对象功能": "出风口", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 出风口设置为扫风模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"对象功能": "照我回家", "调节内容": "时长"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 照我回家设置为60秒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"功能": "交通标志", "调节内容": "车速", "子功能": "超速报警"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 超速报警设置为最小值 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"功能": "智慧巡航", "调节内容": "车速", "子功能": "智能限速偏移值"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 智能限速偏移值设置为负百分之三十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"功能": "方便进出"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 副驾驶方便进出设置为离车 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"对象功能": "左电动出风口", "调节内容": "风向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 左电动出风口设置为左右循环模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"功能": "前向辅助", "调节内容": "距离", "子功能": "预测性紧急碰撞预警"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 预测性紧急碰撞预警设置为较早 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"对象功能": "电动出风口", "调节内容": "风向"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 右边电动出风口设置为上下扫风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 设置为二十五度二档风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"对象功能": "吹风模式", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 吹风模式设置为普通模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"调节内容": "灵敏度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 前碰撞灵敏度设置为标准 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"功能": "辅助驾驶的语音模式", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 将辅助驾驶的语音模式设置为详细模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"对象功能": "左边出风口", "调节内容": "风向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 左边出风口设置为上下扫风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"功能": "智慧巡航", "调节内容": "模式", "子功能": "智能限速控制"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 智能限速控制设置为自动控速 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"对象功能": "报警音", "调节内容": "音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 报警音设置为中 | {"非控制": 1} | {} | 是 | {} |
| 设置为 | None | {"对象功能": "报警音", "调节内容": "音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 报警音设置为高 | {"非控制": 1} | {} | 是 | {} |
| 设置为 | None | {"对象功能": "警报音量", "调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 将警报音量设置为小 | {"非控制": 1} | {} | 是 | {} |
| 设置为 | None | {"对象功能": "出风模式", "调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 副驾出风模式设置为聚焦模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"功能": "智慧巡航", "调节内容": "模式", "子功能": "辅助驾驶播报"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 辅助驾驶播报模式设置为简洁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"对象功能": "出风口", "调节内容": "风向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 二排出风口设置为左右扫风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"对象功能": "冷藏", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 冷藏模式设置为标准 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"对象功能": "电动出风口", "调节内容": "风向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主驾电动出风口设置为上下扫风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"功能": "前向辅助", "调节内容": "音效", "子功能": "行人提示音"} | NONE | NONE | NONE | 1 | 行人提示音设置为科技 | {"非控制": 1} | {} | 是 | {} |
| 设置为 | None | {"调节内容": "音量"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 语音音量设置为默认 | {"非控制": 1} | {} | 是 | {} |
| 设置为 | None | {"对象功能": "车外行人警示音", "调节内容": "音效"} | NONE | NONE | NONE | 1 | 车外行人警示音设置为音效三 | {"非控制": 1} | {} | 是 | {} |
| 设置为 | None | {"功能": "音效增强", "调节内容": "音效"} | NONE | NONE | NONE | 1 | 音效增强设置为现场音乐会音效 | {"非控制": 1} | {} | 是 | {} |
| 设置为 | None | {"功能": "智慧巡航", "调节内容": "车速", "子功能": "限速偏移"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 限速偏移设置为十千米每小时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | None | {"功能": "对车供电"} | NONE | NONE | NONE | 1 | 对外供电设置为对车供电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | 仪表 | {"对象功能": "全屏"} | NONE | NONE | NONE | 1 | 仪表导航设置为全屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | 仪表 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 仪表模式设置为简洁模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | 儿童座椅 | {"对象功能": "通风", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 儿童座椅设置为恒温通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | 后视镜 | {"对象功能": "照地", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 后视镜照地设置为两侧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | 天幕玻璃 | {"调节内容": "透明度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天幕玻璃透明度设置为5 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | 屏 | {"对象功能": "保", "调节内容": "时长"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 屏保等待时长设置为永不 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | 扩散器 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 扩散器设置为手动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | 空气净化器 | {} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 空气净化器风速设置为低速 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | 蓝牙耳机 | {"调节内容": "声音来源"} | NONE | NONE | NONE | 1 | 声音输出设置为蓝牙耳机 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | 车辆模式 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 将车辆模式设置为越野 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为 | 钥匙 | {"对象功能": "解锁", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 钥匙解锁设置为主驾 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为关闭 | None | {"对象功能": "低速行驶提示音"} | NONE | NONE | NONE | 1 | 低速行驶提示音设置为关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置为关闭 | 外后视镜 | {"对象功能": "倒车下翻"} | NONE | NONE | NONE | 1 | 外后视镜倒车下翻设置为关闭 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置到 | None | {"调节内容": "最大放电量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 最大放电量设置到百分之十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置到 | None | {"对象功能": "出风模式", "调节内容": "风向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 出风模式设置到上下扫风模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置到 | None | {"对象功能": "出风模式", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 出风模式设置到聚焦模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置到 | None | {"调节内容": "最大充电"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 最大充电设置到百分之一 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置到 | 冰箱 | {"调节内容": "时长"} | NONE | QUANTIFIED_OR_LEVEL | TEXT_ENUM_OR_OTHER | 1 | 冰箱保温时间设置到3小时 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置成 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 设置成白天模式调高屏幕亮度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置成 | 冰箱 | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 开空调冰箱温度设置成负六度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置成 | 麦克风 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 我想把麦克风设置成静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 设置调节 | None | {"调节内容": "音量"} | NONE | NONE | NONE | 1 | 设置调节导航音量 | {"非控制": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "音效高音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 音效高音调为五 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"调节内容": "温度"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 设置时间格式后排温度调到最高打开阅读灯 | {"已知但不开放": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "动能回收"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 播放玫瑰花的葬礼动能回收调到适中 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"功能": "开机音量音量", "调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 开机音量音量调到最小 | {"非控制": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "风力"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 风力调到一格然后避开面部吹风 | {"已知但不开放": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "音量"} | NONE | NONE | NONE | 1 | 播放杨宗纬的歌曲并将音量调小后 | {"非控制": 1} | {} | 是 | {} |
| 调 | None | {"对象功能": "报警提示音音量", "调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 报警提示音音量调到十档 | {"非控制": 1} | {} | 是 | {} |
| 调 | None | {"功能": "智慧巡航", "调节内容": "距离", "子功能": "驾驶辅助"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 驾驶辅助距离调到最小 | {"正式可执行": 1} | {"CRUISE_SET_GAP": 1} | 是 | {} |
| 调 | None | {"调节内容": "风量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 打开空调风量调到大 | {"已知但不开放": 1} | {} | 是 | {} |
| 调 | None | {"对象功能": "均衡器", "调节内容": "低音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 均衡器的低音调为30 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"调节内容": "力度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 打开座椅按摩力度调到最大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"对象功能": "均衡器", "调节内容": "音效"} | NONE | NONE | NONE | 1 | 进入音效界面并调至平坦 | {"非控制": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "风力大小"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 风力大小调到最小 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"对象功能": "报警提示音", "调节内容": "音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 报警提示音调中等 | {"非控制": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "温度"} | NONE | NONE | NONE | 1 | 热死了快调温度 | {"已知但不开放": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "动力来源"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 调到混动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"调节内容": "亮度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 亮度调到二十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"调节内容": "动能回收强度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 动能回收强度调为2 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 能不能把对比度调高点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"对象功能": "伴奏", "调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 伴奏音量调到20 | {"非控制": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "风量"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 可以将一排左的风量调到最小吗 | {"已知但不开放": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "气味的浓度"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 帮我把车里气味的浓度调成低级 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 车内温度不够再调一下 | {"已知但不开放": 1} | {} | 是 | {} |
| 调 | None | {"对象功能": "报警提示音", "调节内容": "音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 报警提示音调高 | {"非控制": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "音效低音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 音效低音调为五 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"调节内容": "声音"} | NONE | NUMBER | NONE | 1 | 你的声音调为20 | {"非控制": 1} | {} | 是 | {} |
| 调 | None | {} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 对比度调最小 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"功能": "开机背景音乐", "调节内容": "音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 开机背景音乐调到2 | {"非控制": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "能量回收"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 能量回收模式调为强模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"调节内容": "风"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 把风调到最小空调风调到最小 | {"已知但不开放": 1} | {} | 是 | {} |
| 调 | None | {"调节内容": "风力等级"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 风力等级调到最小 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | None | {"功能": "智慧巡航", "调节内容": "速度", "子功能": "车速限制器"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 车速限制器速度调高 | {"正式可执行": 1} | {"CRUISE_SET_SPEED": 1} | 是 | {} |
| 调 | 内后视镜 | {"调节内容": "高度"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 流媒体内后视镜调到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 减震 | {"调节内容": "高度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 减震高度调到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 副屏 | {"调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 关闭大灯屏幕亮度调到最低仪表屏亮度调到最低一副屏亮度调到最低那是 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 后背 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 我要调副驾后背 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 后视镜 | {"调节内容": "高度"} | NONE | NUMBER | NONE | 1 | 流媒体后视镜高度调到3 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 天幕 | {"调节内容": "幅度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天幕调到百分之二十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 天窗 | {"调节内容": "幅度"} | NONE | NUMBER | NONE | 1 | 天窗调到50 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 座椅 | {"对象功能": "震动", "调节内容": "震动强度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 座椅震动强度调到弱 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 座椅 | {"对象功能": "通风", "调节内容": "风"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 打开蓝牙音乐主驾座椅通风挡位调至中等 | {"已知但不开放": 1} | {} | 是 | {} |
| 调 | 座椅 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 后排座椅要调一调设置页帮我打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 座椅 | {} | NONE | NONE | NONE | 1 | 来把我的座椅重调 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 座椅 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 座椅调副驾座椅调整为位置一 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾位置调到一 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 座椅 | {"对象功能": "律动", "调节内容": "律动强度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 座椅律动强度调为弱 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 悬架 | {"调节内容": "高度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 悬架高度调到最高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 抬头显示 | {"调节内容": "高度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 抬头显示页面调最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 空气净化器 | {} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 将空气净化器帮我调为中速 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 窗帘 | {"调节内容": "幅度"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 所有窗帘调到半开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 车窗 | {"调节内容": "透光度"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 调亮右后车窗5档 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 远光灯 | {"调节内容": "高度", "车外灯类型": "远光灯"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 远光灯高度调到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 钥匙 | {"对象功能": "解锁", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 调钥匙解锁模式为全车解锁 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调 | 香水 | {"调节内容": "浓度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 香水浓度调至最浓 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调一下 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 白天模式调一下面部 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调一下 | None | {"功能": "声浪模拟"} | NONE | NONE | NONE | 1 | 调一下声浪模拟界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调一下 | 后视镜 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 调一下右侧后视镜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调一下 | 后视镜 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 副驾后视镜调一下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调一下 | 座椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 调一下座椅制冷 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调一点 | 腿托 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主驾腿托往前调一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调一点 | 腿架 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主驾腿架往上调一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调为 | None | {"调节内容": "声"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 我想调为最强声 | {"非控制": 1} | {} | 是 | {} |
| 调为 | None | {"对象功能": "车外行人警示音", "调节内容": "音效"} | NONE | NONE | NONE | 1 | 车外行人警示音调为声音一 | {"非控制": 1} | {} | 是 | {} |
| 调为 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 调为夜间模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调为 | None | {"对象功能": "除雾", "调节内容": "时长"} | NONE | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | 1 | 自动除雾调为全时开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调为 | None | {"调节内容": "动力模式"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 动力模式调为纯电驾驶模式调为四驱 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调为 | None | {"对象功能": "伴你回家", "调节内容": "时长"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 伴你回家调为半分钟 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调为 | None | {"功能": "听音位"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 听音位调为第二排 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调为 | 车窗 | {"调节内容": "防晒等级"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 车窗防晒等级调为自动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调低 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 音量调低成一半 | {"非控制": 1} | {} | 是 | {} |
| 调低 | 天窗 | {"调节内容": "防晒等级"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 调低天窗防晒等级3档 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调低 | 整车 | {"调节内容": "亮度"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 调低整车背光亮度到最暗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调低一点 | None | {"调节内容": "浓度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 香味太刺鼻了浓度调低一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调出 | None | {} | NONE | NONE | NONE | 1 | 调出主页那个页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调出 | None | {"对象功能": "热点"} | NONE | NONE | NONE | 1 | 请调出热点网络设置画面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | None | {"调节内容": "防晒等级"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 防晒等级调到最高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | None | {"调节内容": "温度"} | NONE | NONE | NONE | 1 | 将空调的风速调到二挡将温度调到 | {"已知但不开放": 1} | {} | 是 | {} |
| 调到 | None | {"对象功能": "充电", "调节内容": "目标充电量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 将目标充电量调到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | None | {"调节内容": "声音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 广播声音调到非常大 | {"非控制": 1} | {} | 是 | {} |
| 调到 | None | {"对象功能": "报警提示音", "调节内容": "音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 报警提示音调到20 | {"非控制": 1} | {} | 是 | {} |
| 调到 | None | {"对象功能": "智能表面", "调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 智能表面亮度调到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | None | {"对象功能": "出风口", "调节内容": "风向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 副驾的出风口调到最上面 | {"已知但不开放": 1} | {} | 是 | {} |
| 调到 | None | {"调节内容": "音量"} | NONE | NONE | NONE | 1 | 方向盘调节音量调到导航音量 | {"非控制": 1} | {} | 是 | {} |
| 调到 | None | {"调节内容": "温"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 车温还是调到最高吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 1 | 音效调到音乐厅 | {"非控制": 1} | {} | 是 | {} |
| 调到 | None | {"对象功能": "出风口", "调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 副驾出风口调到手动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | None | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 调到最低温度 | {"已知但不开放": 1} | {} | 是 | {} |
| 调到 | None | {"功能": "报警语音播报", "调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 报警语音播报音量调到一半 | {"非控制": 1} | {} | 是 | {} |
| 调到 | None | {"对象功能": "日出日落"} | NONE | NONE | NONE | 1 | 显示模式帮我调到日出日落 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 冰箱 | {"调节内容": "温度"} | NONE | NUMBER | NONE | 1 | 冰箱调到50度 | {"已知但不开放": 1} | {} | 是 | {} |
| 调到 | 冰箱 | {"调节内容": "温度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 冰箱温度调到零下二十度 | {"已知但不开放": 1} | {} | 是 | {} |
| 调到 | 冰箱 | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 冰箱调到最冷的效果 | {"已知但不开放": 1} | {} | 是 | {} |
| 调到 | 后视镜 | {} | NONE | NONE | NONE | 1 | 把音量调到五十八后面的天窗关了然后后视镜调到 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 天幕 | {"调节内容": "透明值"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 把天幕透明值调到最亮 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 天窗 | {"调节内容": "透光度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 天窗调到最亮 | {"已知但不开放": 1} | {} | 是 | {} |
| 调到 | 天窗 | {"调节内容": "透明挡位"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 把天窗透明挡位调到最暗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 天窗 | {"调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天窗亮度调到最小 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 天窗 | {"调节内容": "透光值"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天窗透光值调到20% | {"已知但不开放": 1} | {} | 是 | {} |
| 调到 | 天窗 | {"调节内容": "透光挡位"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 把天窗透光挡位调到最亮 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 天窗 | {"调节内容": "透明值"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 把天窗透明值调到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 天窗 | {"调节内容": "透光度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天窗透光度调到百分之负一 | {"已知但不开放": 1} | {} | 是 | {} |
| 调到 | 座椅坐盆 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 主驾座椅坐盆调到中间位置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 扬声器 | {"调节内容": "音量"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 把车外扬声器音量调到最小 | {"非控制": 1} | {} | 是 | {} |
| 调到 | 空气净化器 | {} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 空气净化器调到二十六度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 系统 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 系统调到黑色模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 荧幕 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 荧幕调到日间模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 车载冰箱 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 车载冰箱调到热饮 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调到 | 门把手 | {"对象功能": "自动缩回", "调节内容": "时长"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 门把手自动缩回时间调到3分钟 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调回 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 调回默认速度接着播 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调大到 | None | {"调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 声音调大到百分之五十 | {"非控制": 1} | {} | 是 | {} |
| 调小 | None | {"调节内容": "目标电量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 调小目标电量3% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调成 | None | {"调节内容": "声"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 调成最大的声 | {"非控制": 1} | {} | 是 | {} |
| 调成 | None | {"调节内容": "风向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 空调调小一点调成避人吹 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调成 | 两块天窗玻璃 | {"调节内容": "透光度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 把两块天窗玻璃调成透光 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调成 | 冰箱 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 冰箱调成极冻 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调成 | 抬头显示 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 抬头显示调成性能视图 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调成 | 空气净化器 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 空气净化器调成自动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调成 | 车载冰箱 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 车载冰箱模式调成红酒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调成 | 驾驶 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 打开所有车窗打开天窗打开遮阳帘打开空调空调温度调到十七度风量调到百分之二十驾驶模式调成标准 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | None | {"调节内容": "能量回收等级"} | NONE | NONE | NONE | 1 | 现在要调整能量回收等级进设置界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | None | {"调节内容": "音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 系统提示音调整为低 | {"非控制": 1} | {} | 是 | {} |
| 调整 | None | {"调节内容": "温度单位"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 调整温度到华氏度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | None | {"对象功能": "充放电"} | NONE | NONE | NONE | 1 | 我想要调整充放电 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | None | {"调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 调整通话音量为较低的级别 | {"非控制": 1} | {} | 是 | {} |
| 调整 | None | {"对象功能": "混响", "调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 将混响音量调整到最小 | {"非控制": 1} | {} | 是 | {} |
| 调整 | None | {"调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 把音量调整到十五 | {"非控制": 1} | {} | 是 | {} |
| 调整 | None | {"调节内容": "音量"} | NONE | NUMBER | NONE | 1 | 导航帮我把它的音量给调整至20 | {"非控制": 1} | {} | 是 | {} |
| 调整 | None | {"调节内容": "动力来源"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 调整到纯电模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | None | {"对象功能": "报警音", "调节内容": "音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 调整报警音为低 | {"非控制": 1} | {} | 是 | {} |
| 调整 | None | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 风量调整至四挡挡温度调整到二十三 | {"已知但不开放": 1} | {} | 是 | {} |
| 调整 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 调整舒适模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | None | {"对象功能": "混响", "调节内容": "音量"} | NONE | NUMBER | NONE | 1 | 给我调整混响到30 | {"非控制": 1} | {} | 是 | {} |
| 调整 | None | {"调节内容": "模式"} | NONE | NUMBER | RELATIVE_OR_DIRECTIONAL | 1 | 下坡限速的速度调整到40 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | 头枕音响 | {"调节内容": "音量"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 调整二排右头枕音响音量 | {"非控制": 1} | {} | 是 | {} |
| 调整 | 悬挂 | {"调节内容": "高度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 调整为较低的悬挂高度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | 悬架 | {"调节内容": "高度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 将悬架高度调整到最高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | 扬声器 | {"调节内容": "音量"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 调整车外扬声器的音量到50%的位置 | {"非控制": 1} | {} | 是 | {} |
| 调整 | 扬声器 | {"调节内容": "声"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 让车外的扬声器别那么吵给我调整一下 | {"非控制": 1} | {} | 是 | {} |
| 调整 | 窗帘 | {"调节内容": "幅度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 窗帘调整到半开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | 脚踏 | {"调节内容": "方向"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 调整脚踏到最高我需要伸展 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | 车身 | {"调节内容": "高度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 调整为较低的车身高度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整 | 雷达 | {"对象功能": "倒车", "调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 把倒车雷达音量调整为低 | {"非控制": 1} | {} | 是 | {} |
| 调整为 | None | {"功能": "车道偏离报警", "调节内容": "预警方式", "子功能": "车道偏离报警"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 把车道偏离报警调整为震动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整为 | None | {"功能": "盲区预警", "调节内容": "音效"} | NONE | NONE | NONE | 1 | 盲区预警调整为蜂鸣模式 | {"非控制": 1} | {} | 是 | {} |
| 调整为 | None | {"功能": "交通标志", "调节内容": "音效", "子功能": "超速提醒"} | NONE | NONE | NONE | 1 | 把超速提醒调整为蜂鸣 | {"非控制": 1} | {} | 是 | {} |
| 调整为 | None | {"功能": "交通标志", "调节内容": "预警方式", "子功能": "超速提醒"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 把超速提醒调整为显示 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整为 | None | {"调节内容": "浓度"} | NONE | NONE | NONE | 1 | 将车载芬芳调整为浓香 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整为 | None | {"对象功能": "白天黑夜", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 白天黑夜模式调整为黑夜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整为 | 天窗 | {"调节内容": "透光度"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 把天窗透明度调整为自动控制 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整为 | 座椅 | {"调节内容": "座椅记忆位置"} | NONE | NONE | NONE | 1 | 座椅调副驾座椅调整为位置一 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整为 | 车辆驾驶模式 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 车辆驾驶模式调整为竞速型 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整为 | 驾驶 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 驾驶模式调整为运动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调整到 | None | {"调节内容": "音量"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 播放一首赵鹏的船歌媒体音量调整到百分之六十 | {"非控制": 1} | {} | 是 | {} |
| 调整到 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 1 | 调整到歌剧院音效 | {"非控制": 1} | {} | 是 | {} |
| 调整成 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 1 | 播报帮我调整成拖拉机启动声 | {"非控制": 1} | {} | 是 | {} |
| 调整成 | 天幕 | {"调节内容": "透光率"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天幕透光率调整成百分之十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调至 | None | {"对象功能": "出风口", "调节内容": "模式"} | TEXT_ENUM_OR_OTHER | NONE | TEXT_ENUM_OR_OTHER | 1 | 副驾出风口调至手动模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调至 | None | {"调节内容": "声音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 我要调至五十的声音 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"调节内容": "风"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 小风吹一吹 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | None | {"对象功能": "投屏"} | NONE | NONE | NONE | 1 | 我要调节投屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"功能": "泊车系统", "调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 调节泊车系统音量为中 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"功能": "驾驶员监测系统", "调节内容": "灵敏度", "子功能": "疲劳驾驶检测"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 疲劳驾驶检测灵敏度低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "安全警报提示音", "调节内容": "音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 调节安全警报提示音为高 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"功能": "车道辅助", "调节内容": "预警方式", "子功能": "偏离车道"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 偏离车道的时候震动提醒我 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "左侧出风口", "调节内容": "风向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 左侧出风口往上调100 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | None | {"调节内容": "气温"} | NONE | NONE | NONE | 1 | 调节气温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "铃声"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 电话铃声大一些 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "加热", "调节内容": "时间"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 停车加热时间调长几分钟 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 最大亮度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "伴奏", "调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 伴奏大点儿声 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"调节内容": "出风量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 调小出风量 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "亮度"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 副驾亮度调高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "张数"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 我想拍摄车内三张照片 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "声音"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 调高车外声音 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"功能": "车道辅助", "子功能": "车道偏离报警"} | NONE | NONE | NONE | 1 | 调节车道偏离报警 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "气温"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 气温再高一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "能量回收强度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 能量回收强度给我往下降 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "风量"} | NONE | NUMBER | NONE | 1 | 更改这个风量让它减到一 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | None | {"对象功能": "均衡器", "调节内容": "中音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 均衡器中音调低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "车辆警示音", "调节内容": "音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 车辆警示音调高 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"调节内容": "视角"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 流媒体视角太低了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "左侧出风口", "调节内容": "风向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主驾左侧出风口往左吹 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | None | {"对象功能": "伴奏", "调节内容": "声音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 将伴奏的声音调高 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"对象功能": "车速音量补偿", "调节内容": "音随车速档位"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 降低车速音量补偿使其处于中档状态 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"功能": "交通标志", "子功能": "超速报警"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 将超速报警下降二十五档 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "车辆报警音", "调节内容": "音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 车辆报警音最低 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"功能": "智慧巡航", "调节内容": "车速", "子功能": "车速限制器"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 减慢车速限制器 | {"正式可执行": 1} | {"CRUISE_SET_SPEED": 1} | 是 | {} |
| 调节 | None | {"功能": "行车保电", "调节内容": "SOC目标电量", "子功能": "强制保电"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 强制保电调低3 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "温度单位"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 以华氏度来量度温度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 主驾温度下降一档 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | None | {"调节内容": "温度"} | NONE | NUMBER | NONE | 1 | 调节脚部空间温度调节为6度 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | None | {"功能": "自适应巡航", "调节内容": "车距"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 增大自适应巡航车距 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"功能": "泊车系统", "调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 调节泊车系统音量为高 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"对象功能": "肩部", "调节内容": "方向"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 前面肩部前移 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {} | QUANTIFIED_OR_LEVEL | QUANTIFIED_OR_LEVEL | NONE | 1 | 副驾档位最高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "加热", "调节内容": "运行时间"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 减少驻车加热运行时间 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "蓝牙", "调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 蓝牙通话的声音需要被调整到40% | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"对象功能": "报警提示音音量", "调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 报警提示音音量调到最大 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 我要用第三排右边的尊享位置请开启 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "中音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 中音调节至负10 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "播报声音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 导航播报声音小一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "强度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 强度应该让它降一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "力度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 力度大一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "模式"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 新风系统最大档风力 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "加热", "调节内容": "运行时长"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 降低五分钟驻车加热的运行时长 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "冷暖度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 冷暖度升高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "风量"} | NONE | NONE | NONE | 1 | 换一个档位的风量 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | None | {"功能": "交通标志", "调节内容": "预警方式", "子功能": "超速报警"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 超速的时候通过震动提醒我 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"功能": "智慧巡航", "调节内容": "车速", "子功能": "限速装置"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 增大限速装置速度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "按键", "调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 按键暗一点 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"调节内容": "温度高低"} | NONE | NONE | NONE | 1 | 调节温度高低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "风力"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 温度调节至十九风力调节至最大 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | None | {"调节内容": "亮"} | NONE | NONE | NONE | 1 | 小亮点亮开启内循环 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "声音大小"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 降低电话接听时的声音大小 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "离家照明延时", "调节内容": "时长"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 离家照明延时中间值 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "高音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 让高音转换最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "风向"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 后排左右扫风 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | None | {"调节内容": "音量"} | NONE | NUMBER | NONE | 1 | 导航语音调节并且把音量调为0 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"对象功能": "均衡器", "调节内容": "音效"} | NONE | NONE | NONE | 1 | 我习惯让均衡器处于平坦模式 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"功能": "车速提醒"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 我要调节大一点车速提醒 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "充电", "调节内容": "电池充电上限限制"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 电池充电上限限制为50% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "速度音量补偿", "调节内容": "音随车速档位"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 速度音量补偿高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "节电延时", "调节内容": "时长"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 节电延时最短 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"功能": "报警语音播报", "调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 报警语音播报静音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"功能": "前向辅助", "调节内容": "距离", "子功能": "前碰撞预警"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 前碰撞预警适中 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"功能": "自适应巡航", "调节内容": "车距"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 车距可以稍微缩短一些吗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "风量大小"} | NONE | NONE | NONE | 1 | 调节风量大小 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "声响"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 导航声响小一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"功能": "保养", "调节内容": "里程"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 保养里程20千米 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "肩部", "调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 肩部前移 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"对象功能": "蓝牙", "调节内容": "声响"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 蓝牙通话声响大一些 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "高频声音"} | NONE | NONE | NONE | 1 | 调节高频声音 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "模式"} | NONE | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | 1 | 暖风调小 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "音量"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 车内音量太大了 | {"非控制": 1} | {} | 是 | {} |
| 调节 | None | {"调节内容": "声响"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 声响调高10% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | None | {"调节内容": "风量"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 右前风量为三档 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | None | {"对象功能": "车辆报警音", "调节内容": "音"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 车辆报警音帮我调节中 | {"非控制": 1} | {} | 是 | {} |
| 调节 | 一体屏 | {"调节内容": "亮度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 调低一体屏亮度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 中控扶手 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 中控扶手到车后面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 中控面板 | {"调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 设定中控面板亮度为40% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 中间的柜子 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 后面太挤给我把中间的柜子朝前面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 仪表 | {"调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 让仪表在现有亮度的基础上再增加10% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 仪表盘 | {"调节内容": "亮度"} | NONE | NONE | NONE | 1 | 让仪表暗度达到极限 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 仪表盘 | {"调节内容": "亮度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 屏幕亮度调低一点仪表盘亮度调低一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 侧翼 | {"对象功能": "转向支撑", "调节内容": "灵敏度"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 前面侧翼转向支撑标准 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 侧翼 | {"对象功能": "主动", "调节内容": "弹性"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 副驾主动侧翼强度调高点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 内后视镜 | {"调节内容": "高度"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 流媒体内后视镜缩小一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 冰箱 | {"调节内容": "温度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 冰箱温度高一点 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | 冰箱 | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 冰箱温度调高3华氏度 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | 制冷器 | {} | NONE | NONE | NONE | 1 | 调节制冷器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 制冷器 | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 副驾制冷器温度高一点 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | 制热器 | {"调节内容": "风量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 制热器风量调小一点 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | 制热器 | {"调节内容": "风量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 制热器中等风量 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | 后备箱 | {} | NONE | NONE | NONE | 1 | 调节后备箱 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 后背 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾座椅后背调节界面帮我打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 后背门 | {"调节内容": "高度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 后背门开启高度最高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 后视镜 | {"调节内容": "高度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 流媒体后视镜高度增加到最大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 吸顶屏 | {"对象功能": "蓝牙", "调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 吸顶屏蓝牙耳机音量调到最大 | {"非控制": 1} | {} | 是 | {} |
| 调节 | 坐垫 | {"调节内容": "高度"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 前面坐垫高度向最低调节 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 坐垫 | {"调节内容": "高度"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 前面坐垫向高调节 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 坐垫 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 坐垫向上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 坐垫 | {"调节内容": "角度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 坐垫角度太高了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 坐垫侧翼 | {"调节内容": "弹性"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 坐垫侧翼松一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 坐垫再 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主驾坐垫再向上一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 大屏 | {"调节内容": "方向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 大屏到主驾位置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 大灯 | {"调节内容": "高度", "车外灯类型": "大灯"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 前大灯的高度调近一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 天幕 | {"调节内容": "透光值"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 天幕透光值最暗 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | 天幕 | {"调节内容": "透明值"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 天幕透明值最暗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 天幕 | {"调节内容": "透明值"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天幕透明值最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 天幕玻璃 | {"调节内容": "透明度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天幕玻璃透明度最小 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 天幕调光玻璃 | {"调节内容": "透明度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 天幕调光玻璃透明度升高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 天幕调光玻璃 | {"调节内容": "透明度"} | NONE | NONE | NONE | 1 | 调节天幕调光玻璃透明度到最大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 天窗 | {"调节内容": "幅度"} | NONE | NUMBER | NONE | 1 | 我要使天窗保留有80%的空余 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 天窗 | {"调节内容": "幅度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天窗调节到百分之六十点儿三 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 天窗 | {"调节内容": "透明值"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天窗透明值最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 天窗 | {"调节内容": "透明度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 天窗透明度最低 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | 天窗 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 天窗再向前20 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 天窗 | {"调节内容": "透光挡位"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 天窗透光挡位低一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 天窗的玻璃 | {"调节内容": "透光度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 天窗的玻璃全黑 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 头枕 | {} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 头枕直接到顶别留空隙 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 头枕屏 | {"调节内容": "亮度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 头枕屏亮度调低30% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 头枕屏 | {"调节内容": "亮度"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 副驾头枕屏亮度调低一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 头枕音响 | {"调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 打开驾享模式头枕音响音量调高 | {"非控制": 1} | {} | 是 | {} |
| 调节 | 头顶 | {"调节内容": "亮度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 头顶亮度调高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 尾门 | {} | NONE | NONE | NONE | 1 | 调节尾门 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 屏 | {"调节内容": "音量"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 右后屏音量最大 | {"非控制": 1} | {} | 是 | {} |
| 调节 | 屏 | {"调节内容": "亮度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 多媒体的屏暗一点 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | 屏 | {"对象功能": "息屏", "调节内容": "时长"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 调节后左屏自动息屏时间为永不 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 屏 | {"调节内容": "方向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 屏过去 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 底盘 | {"调节内容": "高度"} | NONE | NONE | NONE | 1 | 底盘高度调节 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 底盘悬架 | {"调节内容": "高度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 底盘悬架调低点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座位 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 副驾座位有点前了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座位 | {"对象功能": "加热", "调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 给我加热座位的温度一直到最多 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座垫 | {"调节内容": "角度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 座垫倾斜加大 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"对象功能": "律动", "调节内容": "律动强度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 座椅律动升到最高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"对象功能": "律动"} | NONE | NONE | NONE | 1 | 调节座椅律动 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 可以上调主驾座椅温度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"对象功能": "加热", "调节内容": "温度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 设置音效增强座椅温度太高了 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | 座椅 | {"调节内容": "角度"} | RELATIVE_OR_DIRECTIONAL | NUMBER | NONE | 1 | 请调节后排座椅角度为180 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"调节内容": "温度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 设置音效加强座椅温度降到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"对象功能": "肩部位置"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 座椅肩部位置调节至10% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"对象功能": "通风", "调节内容": "风力"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 我需要主驾驶座椅风力效果差点 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | 座椅 | {"对象功能": "零重力"} | NONE | NONE | NONE | 1 | 调节零重力座椅 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"对象功能": "音场优化"} | NONE | NONE | NONE | 1 | 调节座椅音场优化设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"调节内容": "弹性"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 我的座椅裹太紧了 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"对象功能": "零重力"} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 调节右前座椅零重力 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"调节内容": "方向"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 前排座椅都到最后面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅 | {"对象功能": "肩部位置", "调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 座椅肩部位置调到最前 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅侧翼 | {"调节内容": "弹性"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 将座椅侧翼包裹得更紧一点吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅头枕 | {} | NONE | NONE | NONE | 1 | 调节座椅头枕 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 座椅靠背 | {"对象功能": "加热", "调节内容": "温度"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 把右后的座椅靠背加热升高1级 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 悬挂 | {"调节内容": "高度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 较低的悬挂高度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 悬架 | {"调节内容": "高度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 将悬架高度调整为中间的设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 扬声器 | {"调节内容": "高度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 升起扬声器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 扬声器 | {"调节内容": "声音"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 车外扬声器声音小一些 | {"非控制": 1} | {} | 是 | {} |
| 调节 | 扬声器 | {"调节内容": "音量"} | RELATIVE_OR_DIRECTIONAL | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 调高车外扬声器音量 | {"非控制": 1} | {} | 是 | {} |
| 调节 | 抬头显示 | {"调节内容": "角度"} | NONE | NONE | NONE | 1 | 调节抬头显示角度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 抬头显示 | {} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 抬头显示调低百分之五十 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 抬头显示 | {} | NONE | NONE | NONE | 1 | 抬头显示不是我想要的位置改一下吧 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 抬头显示 | {"调节内容": "高度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 抬头显示画面调低点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 按键 | {"调节内容": "亮度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 按键亮一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 摄像头 | {"调节内容": "时长"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 照相延时五秒钟 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 摄像头 | {"调节内容": "摄像头模式"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 延时3秒拍照 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 摄像头 | {} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 缩小摄像头画面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 整车 | {"调节内容": "模式"} | NONE | NUMBER | TEXT_ENUM_OR_OTHER | 1 | 设置车辆坡道缓降的速度为40 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 整车 | {"调节内容": "亮"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 整车背光亮度升高一个档位 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 整车 | {"调节内容": "模式"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 转变为混动驾驶模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 星空穹顶 | {"调节内容": "亮度", "车内灯类型": "星空穹顶"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 星空穹顶亮度设为最亮 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 星空顶 | {"调节内容": "亮度", "车内灯类型": "星空顶"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 切换最低档星空顶亮度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 玻璃 | {"调节内容": "幅度"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 关闭前排玻璃打开遮阳帘空调调到十八摄氏度播放周杰伦的等你下课 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 玻璃天窗 | {"调节内容": "透光度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 让玻璃天窗更清晰 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 空悬 | {"调节内容": "高度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 空悬调到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 空气净化器 | {"调节内容": "温度"} | NONE | NONE | NONE | 1 | 将空气净化器温度调高一点 | {"已知但不开放": 1} | {} | 是 | {} |
| 调节 | 窗 | {"调节内容": "透光度"} | RELATIVE_OR_DIRECTIONAL | TEXT_ENUM_OR_OTHER | NONE | 1 | 零透明度后窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 窗 | {"调节内容": "透明度"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 一半不透明度后窗 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 窗帘 | {"调节内容": "幅度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 窗帘位置到三分之一 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 脚托 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 脚托往下到底别留空隙 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 脚踏 | {"调节内容": "高度"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主驾脚踏向高调节 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 脚踏 | {"对象功能": "加热", "调节内容": "温度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 调高脚踏加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 腰架 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 腰架往前调一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 腰靠 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 腰靠向下来一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 腰靠 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主驾腰靠向下起来一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 腿托 | {"调节内容": "弹性"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 主驾腿托包裹松一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 腿托 | {"调节内容": "高度"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主驾腿托不够高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 腿托 | {"对象功能": "延长", "调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 腿托延长调到最长 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 腿托 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 副驾调整腿托至百分之五十向上 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 腿托 | {"调节内容": "方向"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 腿托高点更好 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 腿托 | {"对象功能": "延长", "调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主驾腿托延长调到最长 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 腿托 | {"对象功能": "伸长", "调节内容": "方向"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 腿托伸长 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 荧幕 | {"调节内容": "亮度"} | TEXT_ENUM_OR_OTHER | TEXT_ENUM_OR_OTHER | NONE | 1 | 副驾驶荧幕最亮 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 荧幕 | {"调节内容": "亮度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 调亮荧幕 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 蓝牙耳机 | {"调节内容": "音量"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 蓝牙耳机的音量不应该这么大 | {"非控制": 1} | {} | 是 | {} |
| 调节 | 车窗 | {"调节内容": "防晒等级"} | RELATIVE_OR_DIRECTIONAL | QUANTIFIED_OR_LEVEL | NONE | 1 | 左后车窗防晒等级降低3档 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 车身 | {"调节内容": "高度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 将车身高度降低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 车门 | {"调节内容": "开合角度"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 调节副驾车门开合角度放平后排座椅 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 车顶 | {"调节内容": "透光度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 车顶再暗一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 银屏 | {"调节内容": "亮度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 调暗银屏 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 雨量传感器 | {"调节内容": "灵敏度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 将雨量传感器灵敏度调高2 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 雨量传感器 | {"调节内容": "灵敏度"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 将雨量传感器灵敏度调低一点 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 靠椅 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 调节后排靠椅 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 颈枕 | {"调节内容": "方向"} | TEXT_ENUM_OR_OTHER | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 主驾颈枕前移 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 驾驶 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 把驾驶模式调节舒适模式调整为舒适模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节 | 麦克风 | {"对象功能": "混响", "调节内容": "音量"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 麦克风混响音量调小 | {"非控制": 1} | {} | 是 | {} |
| 调节为 | None | {"对象功能": "车辆报警音", "调节内容": "音"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 车辆报警音调节为高 | {"非控制": 1} | {} | 是 | {} |
| 调节为 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 调节为智能驾驶模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节为 | None | {"功能": "声浪", "调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 1 | 车外声浪调节为电子 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节为 | 侧翼 | {"对象功能": "转向支撑", "调节内容": "灵敏度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 侧翼转向支撑调节为标准 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节为 | 驾驶 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 音量调大一点关闭车窗把驾驶模式调节为舒适 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调节为打开 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 把压缩机调节为打开 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调试 | 后视镜 | {} | NONE | NONE | NONE | 1 | 调试后视镜 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调调 | None | {"调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 调调导航声音把它给调为50% | {"非控制": 1} | {} | 是 | {} |
| 调高 | None | {"调节内容": "速度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 调高速度到八十km/h | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调高 | None | {"调节内容": "温度"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 主驾温度调高到八档 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 调高 | 脚踏 | {"对象功能": "加热", "调节内容": "温度"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 主驾脚踏加热调高一档 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 转 | 座椅 | {} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 二排座椅转 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 转到 | 电动门 | {} | NONE | NONE | NONE | 1 | 转到电动门控制页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 转动 | 座椅 | {"调节内容": "旋转"} | NONE | NUMBER | NONE | 1 | 座椅旋转180度 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 转换为 | 近光灯 | {"车外灯类型": "近光灯"} | NONE | NONE | NONE | 1 | 车灯转换为近光灯 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 转换至 | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 转换至漂移驾驶模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 运行 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 让汽车在运动模式上运行 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 还原 | None | {"调节内容": "音量"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 语音音量还原到默认 | {"非控制": 1} | {} | 是 | {} |
| 还原 | 座椅 | {"调节内容": "座椅记忆位置"} | TEXT_ENUM_OR_OTHER | NONE | NONE | 1 | 主驾调到默认位置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 还原 | 座椅 | {"调节内容": "座椅记忆位置"} | NONE | NONE | NONE | 1 | 调到默认位置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 进入 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 1 | 进入歌剧院音效 | {"非控制": 1} | {} | 是 | {} |
| 进入 | None | {"对象功能": "驻车解锁"} | NONE | NONE | NONE | 1 | 进入驻车解锁设置页面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 进入 | None | {"对象功能": "座椅声场"} | NONE | NONE | NONE | 1 | 进入座椅声场调节界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 进入 | None | {"功能": "主动恒温"} | NONE | NONE | NONE | 1 | 进入主动恒温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 进入 | None | {"对象功能": "系统应用"} | NONE | NONE | NONE | 1 | 打开后面空调进入应用 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 进入 | None | {"功能": "音效增强"} | NONE | NONE | NONE | 1 | 进入音效增强的设置 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 进入 | 仪表显示 | {"调节内容": "亮度"} | NONE | NONE | NONE | 1 | 进入仪表显示亮度设置界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 进入 | 后背 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 进入后排座椅后背设置界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 进入 | 座椅后背 | {} | NONE | NONE | NONE | 1 | 进入座椅后背设置界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 进行 | None | {"功能": "前向辅助", "子功能": "前向碰撞预警"} | NONE | NONE | NONE | 1 | 现在进行前向碰撞预警程序 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 进行 | 车载智能儿童座椅 | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 车载智能儿童座椅进行通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 连接 | None | {} | NONE | NONE | NONE | 1 | 连接连接蓝牙音乐 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 连接 | None | {"对象功能": "网络"} | NONE | NONE | NONE | 1 | 连接网络打开WIFI | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退一下 | None | {"调节内容": "视图"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 退一下双后视界面 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退下 | None | {} | NONE | NONE | NONE | 1 | 关闭导航语音我要静音谢谢退下 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退出 | None | {"功能": "座舱控温系统"} | NONE | NONE | NONE | 1 | 退出座舱控温系统 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退出 | None | {"调节内容": "模式"} | NONE | NONE | RELATIVE_OR_DIRECTIONAL | 1 | 退出小憩模式关闭座椅通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退出 | None | {"功能": "主动恒温"} | NONE | NONE | NONE | 1 | 退出主动恒温 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退出 | None | {"调节内容": "模式"} | RELATIVE_OR_DIRECTIONAL | NONE | TEXT_ENUM_OR_OTHER | 1 | 退出前排影院模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退出 | None | {"功能": "过热保护"} | NONE | NONE | NONE | 1 | 退出过热保护 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退出 | None | {"功能": "自适应巡航控制系统"} | NONE | NONE | NONE | 1 | 退出自适应巡航控制系统 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退出 | 智能儿童座椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 智能儿童座椅退出加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退出 | 智能儿童座椅 | {"对象功能": "通风"} | NONE | NONE | NONE | 1 | 智能儿童座椅退出通风 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退出 | 车载儿童座椅 | {"对象功能": "加热"} | NONE | NONE | NONE | 1 | 车载儿童座椅退出加热 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退到 | None | {} | NONE | NONE | NONE | 1 | 退到主页 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退回 | None | {} | NONE | NONE | NONE | 1 | 退回到主页 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 退掉一下 | None | {"调节内容": "视图"} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 退掉一下双后视 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 选择 | None | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 选择运动模式 | {"已知但不开放": 1} | {} | 是 | {} |
| 选择 | 抬头显示 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 抬头显示显示风格选择标准 | {"已知但不开放": 1} | {} | 是 | {} |
| 选择 | 整车 | {"调节内容": "模式"} | NONE | NONE | TEXT_ENUM_OR_OTHER | 1 | 选择岩石驾驶模式 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 配置 | None | {"调节内容": "音效"} | NONE | NONE | NONE | 1 | 配置爵士音效 | {"非控制": 1} | {} | 是 | {} |
| 配置 | None | {"对象功能": "声音均衡器"} | NONE | NONE | NONE | 1 | 配置声音均衡器 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 配置 | None | {"对象功能": "座椅声场优化"} | NONE | NONE | NONE | 1 | 配置座椅声场优化 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 链接 | None | {"对象功能": "手机蓝牙"} | NONE | NONE | NONE | 1 | 链接手机蓝牙 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 锁定 | 全景记录仪 | {"对象功能": "录像锁定"} | NONE | NONE | NONE | 1 | 锁定全景记录仪 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 锁定 | 前视记录仪 | {"对象功能": "录像锁定"} | NONE | NONE | NONE | 1 | 锁定前视记录仪 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 闭 | 车门 | {} | NONE | NONE | NONE | 1 | 让车门闭合 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 降 | 座椅 | {} | NONE | RELATIVE_OR_DIRECTIONAL | NONE | 1 | 座椅持续降温到低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 降 | 玻璃 | {"调节内容": "幅度"} | TEXT_ENUM_OR_OTHER | QUANTIFIED_OR_LEVEL | NONE | 1 | 主驾副驾玻璃降到最高升到最高 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 降 | 隔断 | {"调节内容": "幅度"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 隔断降到最低 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 降低 | None | {"调节内容": "温度"} | NONE | TEXT_ENUM_OR_OTHER | NONE | 1 | 空调风速开到最大温度降低到二十二 | {"已知但不开放": 1} | {} | 是 | {} |
| 降到下面去 | 窗子 | {} | RELATIVE_OR_DIRECTIONAL | NONE | NONE | 1 | 左前窗子降到下面去 | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 限制 | None | {"调节内容": "充电限值"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 充电限值限制到50% | {"未知": 1} | {} | 否 | {"UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3": 1} |
| 高 | None | {"调节内容": "声音"} | NONE | QUANTIFIED_OR_LEVEL | NONE | 1 | 声音给我高至一半 | {"非控制": 1} | {} | 是 | {} |

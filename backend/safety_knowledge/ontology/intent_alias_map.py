"""意图别名关键词映射（用于 覆盖矩阵 与 Retrieval Benchmark 的语义判定）

通道说明：
  - 严格匹配：node.canonical_action == intent_id
  - 语义匹配：节点标题/描述/证据命中意图关键词 → 该意图获得知识支撑

关键词优先级：同一节点可支撑多个意图（如"驻车制动装置"同时支撑
PARKING_BRAKE_APPLY / PARKING_BRAKE_RELEASE / PARKING_BRAKE_AUTO_APPLY_*）。
"""
from __future__ import annotations

# intent_id -> 中文语义关键词（节点标题/描述命中即算支撑）
INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    # ---- 行驶控制 ----
    "ACCELERATE": ("加速", "加速踏板", "动力输出", "纵向速度控制"),
    "DECELERATE": ("减速", "制动减速", "降速"),
    "BRAKE": ("制动", "行车制动", "液压制动", "气压制动", "制动系统", "刹车", "制动踏板"),
    "EMERGENCY_BRAKE": ("应急制动", "紧急制动", "自动紧急制动", "AEB"),
    "LANE_KEEP": ("车道保持", "车道偏离", "横向控制", "脱手检测", "驾驶员监测"),
    "LANE_CHANGE": ("换道", "变道", "转向信号", "横向移动中断", "换道安全空间", "车道变更"),
    "CRUISE_ENABLE": ("定速巡航", "巡航", "自适应巡航", "ACC", "跟随"),
    "CRUISE_DISABLE": ("巡航", "定速巡航", "ACC"),
    "CRUISE_SET_GAP": ("时距", "跟车距离", "巡航车距", "车间时距"),
    "CRUISE_SET_SPEED": ("限速", "超速报警", "限速功能", "巡航速度", "巡航车速", "设定车速"),
    "EVASIVE_STEER": ("避让", "紧急转向", "规避", "避险"),
    "ESC_ENABLE": ("车身稳定", "ESC", "防滑", "电子稳定"),
    "ESC_DISABLE": ("车身稳定", "ESC", "防滑", "电子稳定"),
    "GEAR_SET": ("档位", "换挡", "挡位", "齿轮", "互锁", "倒挡锁", "P档", "D档"),
    "GEAR_CHANGE_MODE_SET": ("换挡", "挡位模式", "换挡模式", "齿轮"),
    "AUTO_PARK_ENABLE": ("自动泊车", "泊车辅助", "自动泊入", "APA"),
    # ---- 灯光 ----
    "HEADLIGHT_SET_MODE": ("前照灯", "大灯", "灯光", "前位灯", "后位灯", "照明"),
    "HIGH_BEAM_ON": ("远光灯", "远光", "光束", "远光指示"),
    "HIGH_BEAM_OFF": ("远光灯", "远光", "光束"),
    "LOW_BEAM_ON": ("近光灯", "近光"),
    "LOW_BEAM_OFF": ("近光灯", "近光"),
    "FOG_LIGHT_ON": ("雾灯", "前雾灯", "后雾灯"),
    "FOG_LIGHT_OFF": ("雾灯", "前雾灯", "后雾灯"),
    "HAZARD_LIGHT_ON": ("危险警示灯", "双闪", "危险报警"),
    "HAZARD_LIGHT_OFF": ("危险警示灯", "双闪", "危险报警"),
    "PARKING_LIGHT_ON": ("驻车灯", "示廓灯", "位置灯"),
    "PARKING_LIGHT_OFF": ("驻车灯", "示廓灯", "位置灯"),
    "TURN_INDICATOR_ON": ("转向灯", "转向指示", "转向信号"),
    "TURN_INDICATOR_OFF": ("转向灯", "转向指示", "转向信号"),
    # ---- 车身 ----
    "DOOR_OPEN": ("车门", "乘客门", "门开启", "车门开启"),
    "DOOR_CLOSE": ("车门", "乘客门"),
    "DOOR_SET_POSITION": ("车门", "乘客门", "门位置"),
    "DOOR_LOCK": ("车门锁", "车门闭锁", "门锁", "遥控钥匙"),
    "DOOR_UNLOCK": ("车门锁", "车门解锁", "门锁", "遥控钥匙", "车内开启"),
    "WINDOW_OPEN": ("车窗", "电动窗", "门窗玻璃", "玻璃"),
    "WINDOW_CLOSE": ("车窗", "电动窗", "门窗玻璃"),
    "WINDOW_SET_POSITION": ("车窗", "电动窗"),
    "TRUNK_OPEN": ("后备箱", "行李舱", "行李箱", "尾门"),
    "TRUNK_CLOSE": ("后备箱", "行李舱", "行李箱", "尾门"),
    "TRUNK_SET_POSITION": ("后备箱", "行李舱", "行李箱"),
    "TRUNK_LOCK": ("后备箱锁", "行李箱锁", "门锁", "舱门锁"),
    "TRUNK_UNLOCK": ("后备箱锁", "行李箱锁", "门锁", "舱门锁"),
    "HOOD_OPEN": ("前舱盖", "发动机罩", "引擎盖"),
    "HOOD_CLOSE": ("前舱盖", "发动机罩", "引擎盖"),
    "HORN_ACTIVATE": ("喇叭", "鸣笛", "声响警告"),
    "MIRROR_FOLD": ("后视镜折叠", "外后视镜折叠", "后视镜"),
    "MIRROR_UNFOLD": ("后视镜", "外后视镜"),
    "MIRROR_SET_ANGLE": ("后视镜调整", "后视镜角度"),
    "MIRROR_HEATING_ON": ("后视镜加热", "后视镜除霜", "后视镜"),
    "MIRROR_HEATING_OFF": ("后视镜加热", "后视镜除霜", "后视镜"),
    "WINDSHIELD_HEATING_ON": ("前风窗加热", "前挡加热", "风窗玻璃加热", "除霜", "除雾"),
    "WINDSHIELD_HEATING_OFF": ("前风窗加热", "前挡加热", "除霜", "除雾"),
    "WIPER_SET_MODE": ("雨刮", "雨刮器", "刮水器", "洗涤"),
    "WIPER_SET_SENSITIVITY": ("雨刮", "雨量感应", "刮水器"),
    # ---- 视野 / HVAC ----
    "DEFROST_ON": ("除霜", "除雾", "前风窗除雾", "前风窗除霜", "除霜装置"),
    "DEFROST_OFF": ("除霜", "除雾"),
    # ---- 驻车制动 ----
    "PARKING_BRAKE_APPLY": ("驻车制动", "手刹", "电子驻车", "驻车制动装置", "驻车制动器"),
    "PARKING_BRAKE_RELEASE": ("驻车制动", "手刹", "电子驻车", "驻车制动装置", "驻车制动器"),
    "PARKING_BRAKE_AUTO_APPLY_ENABLE": ("驻车制动", "自动驻车", "Auto Hold"),
    "PARKING_BRAKE_AUTO_APPLY_DISABLE": ("驻车制动", "自动驻车"),
    # ---- 低风险域（R0/R1/R2 舒适功能，供完整性） ----
    "SUNROOF_OPEN": ("天窗", "电动天窗"),
    "SUNROOF_CLOSE": ("天窗", "电动天窗"),
    "SUNROOF_SET_TILT": ("天窗", "天窗倾角"),
    "SEAT_LONGITUDINAL_SET_POSITION": ("座椅", "座椅位置", "座椅前后"),
    "SEAT_BACKREST_SET_ANGLE": ("座椅靠背", "靠背角度"),
    "SEAT_HEIGHT_SET_POSITION": ("座椅高度", "座椅升降"),
    "SEAT_TILT_SET_ANGLE": ("座椅倾角", "座垫角度"),
    "SEAT_LUMBAR_SET_HEIGHT": ("腰托", "腰部支撑"),
    "SEAT_LUMBAR_SET_SUPPORT": ("腰托", "腰部支撑"),
    "STEERING_WHEEL_SET_TILT": ("方向盘", "转向柱", "方向盘角度"),
    "STEERING_WHEEL_SET_EXTENSION": ("方向盘", "转向柱", "方向盘伸缩"),
    "STEERING_WHEEL_HEATING_ON": ("方向盘加热"),
    "STEERING_WHEEL_HEATING_OFF": ("方向盘加热"),
    "SEAT_HEATING_ON": ("座椅加热"),
    "SEAT_HEATING_OFF": ("座椅加热"),
    "SEAT_VENTILATION_ON": ("座椅通风"),
    "SEAT_VENTILATION_OFF": ("座椅通风"),
    "SEAT_MASSAGE_ON": ("座椅按摩"),
    "SEAT_MASSAGE_OFF": ("座椅按摩"),
    "HVAC_ON": ("空调", "暖风", "制冷"),
    "HVAC_OFF": ("空调", "暖风", "制冷"),
    "HVAC_SET_TEMPERATURE": ("空调", "温度", "暖风"),
    "HVAC_SET_FAN_SPEED": ("空调", "风量", "风速"),
    "HVAC_SET_MODE": ("空调", "出风模式"),
    "HVAC_SET_AIRFLOW_DIRECTION": ("空调", "风向", "出风口"),
    "FRAGRANCE_ON": ("香氛", "香薰"),
    "FRAGRANCE_OFF": ("香氛", "香薰"),
    "AMBIENT_LIGHT_SET_COLOR": ("氛围灯", "氛围"),
    "AMBIENT_LIGHT_ON": ("氛围灯", "氛围"),
    "READING_LIGHT_ON": ("阅读灯"),
    "READING_LIGHT_OFF": ("阅读灯"),
    "INTERIOR_LIGHT_ON": ("车内灯", "室内灯", "顶灯"),
    "INTERIOR_LIGHT_OFF": ("车内灯", "室内灯"),
    "CHILD_LOCK_ON": ("儿童锁", "儿童安全锁"),
    "CHILD_LOCK_OFF": ("儿童锁", "儿童安全锁"),
    # ================= 安全域意图（车联网安全 / 数据安全 / OTA / 法规合规） =================
    # ---- 网络安全（GB 44495 / UN R155 / ISO 21434） ----
    "SEC_SECURE_BOOT": ("安全启动", "可信根", "引导加载程序", "固件验证"),
    "SEC_ACCESS_CONTROL": ("访问控制", "权限", "非授权访问", "越权"),
    "SEC_IDENTITY_AUTH": ("身份认证", "身份验证", "认证机制", "证书"),
    "SEC_KEY_MANAGEMENT": ("密钥管理", "密钥", "密钥存储", "证书管理"),
    "SEC_ANTI_TAMPER": ("防篡改", "篡改", "完整性", "防非授权修改"),
    "SEC_ANTI_REPLAY": ("重放", "关键指令", "指令有效性", "指令唯一性", "防重放"),
    "SEC_COMMUNICATION": ("通信安全", "通信加密", "通信信道", "车外通信", "报文"),
    "SEC_SENSITIVE_ENCRYPT": ("敏感个人信息", "加密传输", "保密性"),
    "SEC_MALICIOUS_DATA": ("恶意数据", "异常数据", "恶意数据识别"),
    "SEC_LOG_AUDIT": ("信息安全日志", "日志", "审计", "日志留存", "6个月"),
    "SEC_OTA_PACKAGE": ("升级包", "在线升级", "OTA", "升级安全"),
    "SEC_OBD_PROTECTION": ("OBD", "调试接口", "诊断接口", "外部接口"),
    "SEC_THIRD_PARTY_APP": ("第三方应用", "应用安全"),
    "SEC_TARA": ("TARA", "风险评估", "威胁分析", "攻击路径"),
    "SEC_CSMS": ("网络安全管理体系", "CSMS", "治理"),
    "SEC_VULNERABILITY": ("漏洞", "漏洞管理", "漏洞处置"),
    "SEC_INCIDENT_RESPONSE": ("信息安全事件", "事件应急", "安全事件响应"),
    # ---- 数据安全/隐私（GB/T 44464 / 数安法 / 个保法 / YD/T 3751） ----
    "DATA_CONSENT": ("个人同意", "知情同意", "明示同意"),
    "DATA_COLLECT": ("个人信息收集", "数据收集", "采集"),
    "DATA_STORAGE": ("数据存储", "存储安全", "安全存储"),
    "DATA_USE": ("数据使用", "使用限制", "数据处理"),
    "DATA_TRANSFER": ("数据传输", "传输安全", "传输加密"),
    "DATA_DELETE": ("数据删除", "删除", "清除", "删除权"),
    "DATA_EXPORT": ("数据出境", "出境", "跨境", "境外传输"),
    "DATA_ANONYMIZE": ("匿名化", "去标识化", "匿名化处理"),
    "DATA_OUTSIDE_VEHICLE": ("车外数据", "车外人像", "环境感知"),
    "DATA_INCABIN": ("座舱数据", "车内数据", "座舱"),
    "DATA_CLASSIFICATION": ("数据分类分级", "分类分级", "重要数据", "核心数据"),
    "DATA_IMPORTANT": ("重要数据", "重要数据保护"),
    "DATA_SECURITY_OFFICER": ("数据安全负责人", "管理负责人"),
    "DATA_IMPACT_ASSESSMENT": ("影响评估", "安全评估", "风险评估"),
    # ---- OTA/软件升级（GB 44496 / UN R156） ----
    "OTA_PRECONDITION": ("升级先决条件", "驻车", "升级条件", "禁止升级"),
    "OTA_BATTERY": ("电量保障", "电量", "蓄电池"),
    "OTA_ROLLBACK": ("回滚", "升级失败", "恢复", "安全状态"),
    "OTA_RXSWIN": ("软件识别号", "RXSWIN", "版本号"),
    "OTA_NOTIFY": ("用户告知", "告知", "通知", "升级提示"),
    "OTA_INTEGRITY": ("升级完整性", "防篡改", "真实性", "签名验证"),
    # ---- 事故记录（GB 44497 DSSAD） ----
    "DSSAD_TRIGGER": ("事件记录", "触发", "自动驾驶数据记录", "记录触发"),
    "DSSAD_COLLISION": ("碰撞事件", "碰撞记录", "EDR"),
    "DSSAD_STORAGE": ("数据记录存储", "数据存储", "记录存储"),
    "DSSAD_SECURITY": ("记录信息安全", "记录防篡改", "数据记录安全"),
    # ---- 法规合规（网安法/数安法/个保法/道交法） ----
    "LAW_CLASSIFIED_PROTECTION": ("等级保护", "等保", "网络安全等级保护"),
    "LAW_PRODUCT_SAFETY": ("产品安全义务", "强制要求", "恶意程序", "漏洞补救"),
    "LAW_EMERGENCY_PLAN": ("应急预案", "网络安全事件", "事件报告"),
    "LAW_DATA_DOMESTIC": ("境内存储", "境内", "数据本地化"),
    "LAW_IMAGE_COLLECTION": ("图像采集", "身份识别", "摄像头", "公共场所"),
    "LAW_SENSITIVE_PERSONAL": ("敏感个人信息", "生物识别", "行踪轨迹"),
    "LAW_LIGHT_USAGE": ("灯光使用", "夜间行驶", "会车变光", "雾天", "灯光"),
    "LAW_SPEED_LIMIT": ("限速", "车速限制", "最高车速"),
    "LAW_SAFE_DISTANCE": ("安全距离", "安全车距", "跟车距离", "超车", "紧急制动措施"),
    "LAW_HAZARD_LIGHT": ("危险报警闪光灯", "故障停车", "警示距离", "警告标志"),
    "LAW_CROSSWALK": ("人行横道", "行人", "减速让行", "停车让行", "避让"),
    "LAW_DATA_CLASSIFICATION": ("数据分类分级", "分类分级", "国家核心数据"),
    "LAW_DATA_PROCESSING_SECURITY": ("数据处理", "数据安全管理制度", "全流程"),
    "LAW_IMPACT_ASSESSMENT": ("影响评估", "自动化决策", "对外提供"),
}


def intent_matches_node(intent_id: str, node: dict) -> bool:
    """判定节点是否支撑意图（严格 + 语义双通道）。"""
    if node.get("canonical_action") == intent_id:
        return True
    keywords = INTENT_KEYWORDS.get(intent_id)
    if not keywords:
        return False
    text = f"{node.get('title','')} {node.get('semantic_description','')} {node.get('source','')} {node.get('clause','')}"
    return any(kw in text for kw in keywords)

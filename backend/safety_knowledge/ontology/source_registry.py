"""来源谱系注册表 v2：知识库全部潜在来源的分层登记

层级定义（L0=法律 ... L6=权威库），每源标记状态：
  LOCAL_FULL   本地有全文，可全量解析
  LOCAL_PART   本地有部分条款（law_clauses.json）
  COLLECTED    网络搜集到条款级内容
  FRAMEWORK    仅有框架级公开信息
  TODO         待搜集
"""
SOURCE_REGISTRY = [
    # ============ L0 法律 ============
    {"layer": "L0", "std_id": "CN-ROAD-TRAFFIC-LAW", "name": "中华人民共和国道路交通安全法", "domain": "法规/车控",
     "status": "LOCAL_FULL", "notes": "本地全文；灯光使用/车速/制动条款"},
    {"layer": "L0", "std_id": "CN-CYBERSECURITY-LAW", "name": "中华人民共和国网络安全法", "domain": "网络安全",
     "status": "COLLECTED", "notes": "21/22/25/27/31/37/40-44 条款已搜集"},
    {"layer": "L0", "std_id": "CN-DATASECURITY-LAW", "name": "中华人民共和国数据安全法", "domain": "数据安全",
     "status": "COLLECTED", "notes": "21/24/27/29/30/31/32 条款已搜集"},
    {"layer": "L0", "std_id": "CN-PIPL", "name": "中华人民共和国个人信息保护法", "domain": "数据安全/隐私",
     "status": "COLLECTED", "notes": "4/26/28/30/51/55 条款已搜集"},
    # ============ L1 行政法规/部门规章 ============
    {"layer": "L1", "std_id": "CN-ROAD-TRAFFIC-REG", "name": "道路交通安全法实施条例", "domain": "法规/车控",
     "status": "TODO", "notes": "雾灯使用等灯光条款"},
    {"layer": "L1", "std_id": "MIIT-VEHICLE-DATA", "name": "汽车数据安全管理若干规定（试行）", "domain": "数据安全",
     "status": "TODO", "notes": "车外数据/座舱数据合规"},
    {"layer": "L1", "std_id": "MIIT-ICV-ADMISSION", "name": "智能网联汽车准入管理试行", "domain": "车联网/准入",
     "status": "TODO", "notes": "准入条件/CSMS 要求"},
    # ============ L2 强制性国标 ============
    {"layer": "L2", "std_id": "GB 7258-2017", "name": "机动车运行安全技术条件", "domain": "车控/灯光/车身/视野",
     "status": "LOCAL_FULL", "notes": "372 条款本地全文已解析"},
    {"layer": "L2", "std_id": "GB 44495-2024", "name": "汽车整车信息安全技术要求", "domain": "网络安全/车联网",
     "status": "LOCAL_FULL", "notes": "本地全文；参考 UN R155，2026-01-01 实施"},
    {"layer": "L2", "std_id": "GB 44496-2024", "name": "汽车软件升级通用技术要求", "domain": "OTA/网络安全",
     "status": "COLLECTED", "notes": "升级条件/回滚/电量保障/RXSWIN 要点已搜集，全文待获取"},
    {"layer": "L2", "std_id": "GB 44497-2024", "name": "智能网联汽车 自动驾驶数据记录系统", "domain": "数据记录/事故",
     "status": "LOCAL_FULL", "notes": "本地全文；DSSAD 触发/数据元素/存储/信息安全"},
    {"layer": "L2", "std_id": "GB 4785-2019", "name": "汽车及挂车外部照明和光信号装置的安装规定", "domain": "灯光",
     "status": "COLLECTED", "notes": "前雾灯 5.3/后雾灯 5.11/驻车灯 5.12 条款号已确认"},
    {"layer": "L2", "std_id": "GB 15084-2022", "name": "机动车辆 间接视野装置性能和安装要求", "domain": "视野",
     "status": "FRAMEWORK", "notes": "CMS 电子后视镜首次合法化；条款细节待获取"},
    {"layer": "L2", "std_id": "GB 9656-2021", "name": "机动车玻璃安全技术规范", "domain": "车身", "status": "TODO",
     "notes": "被 GB 7258 11.5.6 引用"},
    {"layer": "L2", "std_id": "GB 11566-2009", "name": "乘用车外部凸出物", "domain": "车身", "status": "TODO",
     "notes": "HOOD 域潜在来源"},
    # ============ L3 推荐性国标 ============
    {"layer": "L3", "std_id": "GB/T 44461.1-2024", "name": "智能网联汽车 组合驾驶辅助系统性能要求及试验方法 第1部分：单车道行驶控制", "domain": "车控/ADAS",
     "status": "LOCAL_FULL", "notes": "巡航/车道保持/跟车时距"},
    {"layer": "L3", "std_id": "GB/T 44461.2-2024", "name": "智能网联汽车 组合驾驶辅助系统 第2部分：换道", "domain": "车控/ADAS",
     "status": "LOCAL_FULL", "notes": "换道触发/转向灯/安全空间"},
    {"layer": "L3", "std_id": "GB/T 40429-2021", "name": "汽车驾驶自动化分级", "domain": "车控", "status": "LOCAL_PART",
     "notes": "L0-L5 分级定义"},
    {"layer": "L3", "std_id": "GB/T 44298-2024", "name": "智能网联汽车 操纵件、指示器及信号装置的标志", "domain": "车控/信息",
     "status": "LOCAL_FULL", "notes": "本地全文"},
    {"layer": "L3", "std_id": "GB/T 44373-2024", "name": "智能网联汽车 术语和定义", "domain": "术语/本体",
     "status": "LOCAL_FULL", "notes": "本地全文；CSMS/OTA 等术语定义"},
    {"layer": "L3", "std_id": "GB/T 44464-2024", "name": "汽车数据通用要求", "domain": "数据安全/隐私",
     "status": "LOCAL_FULL", "notes": "个人信息/重要数据/匿名化/出境，本地全文"},
    {"layer": "L3", "std_id": "GB/T 41871-2022", "name": "信息安全技术 汽车数据处理安全要求", "domain": "数据安全",
     "status": "FRAMEWORK", "notes": "通用/车外/座舱/管理四板块；细则待获取"},
    {"layer": "L3", "std_id": "GB/T 40861-2021", "name": "汽车信息安全通用技术要求", "domain": "网络安全",
     "status": "TODO", "notes": "被 GB 44495 引用"},
    {"layer": "L3", "std_id": "GB/T 24545-2009", "name": "车辆车速限制系统技术要求", "domain": "车控/限速",
     "status": "TODO", "notes": "被 GB 7258 10.5.3 引用"},
    {"layer": "L3", "std_id": "GB/T 30036-2024", "name": "汽车用自适应前照明系统", "domain": "灯光",
     "status": "TODO", "notes": "被 GB 7258 8.5.1 引用"},
    {"layer": "L3", "std_id": "GB/T 22239-2019", "name": "网络安全等级保护基本要求", "domain": "网络安全",
     "status": "FRAMEWORK", "notes": "等保2.0 通用要求，无车联网专项扩展"},
    # ============ L4 行业标准 ============
    {"layer": "L4", "std_id": "YD/T 3751-2020", "name": "车联网信息服务 数据安全技术要求", "domain": "数据安全",
     "status": "COLLECTED", "notes": "5章数据分类/6章分级/7-8章基本与增强级要求目录已确认"},
    {"layer": "L4", "std_id": "YD/T 3594-2019", "name": "车联网信息服务 用户个人信息保护要求", "domain": "数据安全",
     "status": "TODO", "notes": "用户个人信息"},
    {"layer": "L4", "std_id": "QC/T 1160-2022", "name": "汽车OTA技术规范（行业）", "domain": "OTA", "status": "TODO",
     "notes": "OTA 过程要求"},
    # ============ L5 国际法规/标准 ============
    {"layer": "L5", "std_id": "UN R155", "name": "网络安全与网络安全管理系统", "domain": "网络安全",
     "status": "COLLECTED", "notes": "7.2 CSMS/7.3 VTA/附件5 威胁类型与缓解措施"},
    {"layer": "L5", "std_id": "UN R156", "name": "软件更新与软件更新管理系统", "domain": "OTA/网络安全",
     "status": "COLLECTED", "notes": "SUMS/RXSWIN/失败回滚/电量保障/用户告知（近条款级）"},
    {"layer": "L5", "std_id": "ISO/SAE 21434", "name": "道路车辆 网络安全工程", "domain": "网络安全",
     "status": "COLLECTED", "notes": "第15章 TARA 方法论（资产/威胁/影响/攻击可行性）"},
    {"layer": "L5", "std_id": "ISO 26262", "name": "道路车辆 功能安全", "domain": "功能安全", "status": "FRAMEWORK",
     "notes": "ASIL 分级框架"},
    {"layer": "L5", "std_id": "UN R46", "name": "间接视野装置认证", "domain": "视野", "status": "FRAMEWORK",
     "notes": "GB 15084 与 R46 一致"},
    {"layer": "L5", "std_id": "UN R48", "name": "照明和光信号装置安装规定", "domain": "灯光", "status": "FRAMEWORK",
     "notes": "GB 4785 技术来源"},
    # ============ L6 权威知识库/数据库 ============
    {"layer": "L6", "std_id": "NHTSA-RECALL-API", "name": "NHTSA 召回数据库 API", "domain": "事故情报",
     "status": "LOCAL_FULL", "notes": "已接入，37 条候选事故/18 风险节点"},
    {"layer": "L6", "std_id": "CN-DPAC", "name": "市场监管总局缺陷产品召回中心", "domain": "事故情报",
     "status": "TODO", "notes": "国内召回数据源"},
    {"layer": "L6", "std_id": "NVD/CVE", "name": "国家漏洞库", "domain": "网络安全",
     "status": "TODO", "notes": "车载软件 CVE 关联"},
    {"layer": "L6", "std_id": "EU-SafetyGate", "name": "EU Safety Gate", "domain": "事故情报",
     "status": "TODO", "notes": "欧洲产品安全预警"},
]


def main() -> int:
    from collections import Counter
    status_counter = Counter(s["status"] for s in SOURCE_REGISTRY)
    layer_counter = Counter(s["layer"] for s in SOURCE_REGISTRY)
    print("=" * 60)
    print("来源谱系注册表 v2")
    print("=" * 60)
    print(f"总来源数: {len(SOURCE_REGISTRY)}")
    print("层级分布:", dict(sorted(layer_counter.items())))
    print("状态分布:", dict(status_counter))
    print("\n按层级列出:")
    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        items = [s for s in SOURCE_REGISTRY if s["layer"] == layer]
        print(f"\n  {layer}:")
        for s in items:
            print(f"    [{s['status']:12s}] {s['std_id']} - {s['name']} ({s['domain']})")
    return 0


if __name__ == "__main__":
    main()

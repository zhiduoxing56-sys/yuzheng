"""H1: Source Registry v3 —— 全域安全情报来源注册表

地域：CN / US / EU × 类型：RECALL / COMPLAINT / INVESTIGATION / MANUFACTURER_NOTICE /
      INCIDENT / REGULATION / CYBER
层级：L1 政府监管 → L2 OEM 官方 → L3 权威机构 → L4 专业媒体 → L5 公开信息
原则：Authority First；白名单登记；采集宽进、Trusted 严出
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")

# (source_id, region, source_type, authority_level, access_method, update_frequency, language, enabled, notes)
SOURCES: list[dict] = [
    # ==================== 美国 ====================
    {"source_id": "US-NHTSA-RCL", "region": "US", "source_type": "RECALL", "authority": "L1",
     "access": "API", "frequency": "weekly", "language": "EN", "enabled": True,
     "url": "https://api.nhtsa.gov/recalls/recallsByVehicle", "notes": "官方召回 API"},
    {"source_id": "US-NHTSA-CSI", "region": "US", "source_type": "COMPLAINT", "authority": "L1",
     "access": "API", "frequency": "weekly", "language": "EN", "enabled": True,
     "url": "https://api.nhtsa.gov/complaints/complaintsByVehicle", "notes": "消费者投诉（早于召回的风险信号）"},
    {"source_id": "US-NHTSA-CSI-DEFECT", "region": "US", "source_type": "COMPLAINT", "authority": "L1",
     "access": "API", "frequency": "weekly", "language": "EN", "enabled": False,
     "url": "https://api.nhtsa.gov/complaints/complaintsByComponent", "notes": "按组件投诉"},
    {"source_id": "US-NHTSA-INV", "region": "US", "source_type": "INVESTIGATION", "authority": "L1",
     "access": "API", "frequency": "monthly", "language": "EN", "enabled": True,
     "url": "https://api.nhtsa.gov/investigations/investigationsByVehicle", "notes": "缺陷调查（因果链丰富）"},
    {"source_id": "US-NHTSA-FLAT", "region": "US", "source_type": "INCIDENT", "authority": "L1",
     "access": "API", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "https://api.nhtsa.gov/incidents/incidentsByVehicle", "notes": "事故记录"},
    {"source_id": "US-NHTSA-MFR-CAMP", "region": "US", "source_type": "MANUFACTURER_NOTICE", "authority": "L1",
     "access": "API", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "https://api.nhtsa.gov/campaigns", "notes": "制造商沟通/安全活动"},
    {"source_id": "US-NHTSA-SVCBULL", "region": "US", "source_type": "MANUFACTURER_NOTICE", "authority": "L1",
     "access": "API", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "https://api.nhtsa.gov/serviceBulletins", "notes": "技术服务公告"},
    {"source_id": "US-NHTSA-REG", "region": "US", "source_type": "REGULATION", "authority": "L1",
     "access": "API", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "https://api.nhtsa.gov/fmvss", "notes": "FMVSS 法规"},
    {"source_id": "US-CPSC", "region": "US", "source_type": "RECALL", "authority": "L1",
     "access": "API", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "https://www.cpsc.gov", "notes": "消费品安全（含汽车用品）"},
    {"source_id": "US-IIHS", "region": "US", "source_type": "INCIDENT", "authority": "L3",
     "access": "WEB", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "https://www.iihs.org", "notes": "公路安全保险协会（评级/事故研究）"},
    # ==================== 中国 ====================
    {"source_id": "CN-DPAC-RCL", "region": "CN", "source_type": "RECALL", "authority": "L1",
     "access": "WEB", "frequency": "weekly", "language": "ZH", "enabled": True,
     "url": "https://www.dpac.org.cn", "notes": "市场监管总局缺陷产品召回中心（官方）"},
    {"source_id": "CN-SAMR-NOTICE", "region": "CN", "source_type": "REGULATION", "authority": "L1",
     "access": "WEB", "frequency": "monthly", "language": "ZH", "enabled": False,
     "url": "https://www.samr.gov.cn", "notes": "市场监管总局公告"},
    {"source_id": "CN-MIIT-ICV", "region": "CN", "source_type": "REGULATION", "authority": "L1",
     "access": "WEB", "frequency": "monthly", "language": "ZH", "enabled": False,
     "url": "https://www.miit.gov.cn", "notes": "工信部智能网联汽车准入与安全监管"},
    {"source_id": "CN-CQC", "region": "CN", "source_type": "REGULATION", "authority": "L2",
     "access": "WEB", "frequency": "monthly", "language": "ZH", "enabled": False,
     "url": "https://www.cqc.com.cn", "notes": "中国质量认证"},
    {"source_id": "CN-CATARC", "region": "CN", "source_type": "INCIDENT", "authority": "L3",
     "access": "WEB", "frequency": "monthly", "language": "ZH", "enabled": False,
     "url": "https://www.catarc.ac.cn", "notes": "中汽研（测试/事故研究）"},
    {"source_id": "CN-OEM-NOTICE", "region": "CN", "source_type": "MANUFACTURER_NOTICE", "authority": "L2",
     "access": "WEB", "frequency": "monthly", "language": "ZH", "enabled": False,
     "url": "", "notes": "车企官方安全通告（BYD/蔚来/小鹏/理想等官网）"},
    # ==================== 欧盟 ====================
    {"source_id": "EU-SAFETYGATE", "region": "EU", "source_type": "RECALL", "authority": "L1",
     "access": "API", "frequency": "weekly", "language": "EN", "enabled": True,
     "url": "https://ec.europa.eu/safety-gate-alerts/", "notes": "EU Safety Gate（含汽车产品预警）"},
    {"source_id": "EU-SAFETYGATE-RSS", "region": "EU", "source_type": "RECALL", "authority": "L1",
     "access": "RSS", "frequency": "daily", "language": "EN", "enabled": False,
     "url": "https://ec.europa.eu/safety-gate-alerts/screen/searchRSS", "notes": "RSS 订阅"},
    {"source_id": "EU-UNECE", "region": "EU", "source_type": "REGULATION", "authority": "L1",
     "access": "WEB", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "https://unece.org", "notes": "UN R155/R156 等法规"},
    {"source_id": "EU-EEA-RCL", "region": "EU", "source_type": "RECALL", "authority": "L2",
     "access": "WEB", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "https://www.eurocarnews.com", "notes": "欧盟成员国召回汇总（德国 KBA/英国 DVSA 等）"},
    {"source_id": "EU-KBA", "region": "EU", "source_type": "RECALL", "authority": "L1",
     "access": "WEB", "frequency": "monthly", "language": "DE", "enabled": False,
     "url": "https://www.kba.de", "notes": "德国联邦机动车管理局"},
    {"source_id": "EU-DVSA", "region": "EU", "source_type": "RECALL", "authority": "L1",
     "access": "WEB", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "https://www.gov.uk", "notes": "英国 DVSA 召回"},
    {"source_id": "EU-NCAP", "region": "EU", "source_type": "INCIDENT", "authority": "L3",
     "access": "WEB", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "https://www.euroncap.com", "notes": "Euro NCAP"},
    # ==================== 网络安全（独立通道） ====================
    {"source_id": "CYBER-NVD", "region": "GLOBAL", "source_type": "CYBER", "authority": "L1",
     "access": "API", "frequency": "weekly", "language": "EN", "enabled": True,
     "url": "https://services.nvd.nist.gov/rest/json/cves/2.0", "notes": "NVD CVE（车载软件漏洞）"},
    {"source_id": "CYBER-CNVD", "region": "CN", "source_type": "CYBER", "authority": "L1",
     "access": "WEB", "frequency": "weekly", "language": "ZH", "enabled": False,
     "url": "https://www.cnvd.org.cn", "notes": "国家信息安全漏洞共享平台"},
    {"source_id": "CYBER-CNNVD", "region": "CN", "source_type": "CYBER", "authority": "L1",
     "access": "WEB", "frequency": "weekly", "language": "ZH", "enabled": False,
     "url": "https://www.cnnvd.org.cn", "notes": "国家信息安全漏洞库"},
    {"source_id": "CYBER-ICS-CERT", "region": "GLOBAL", "source_type": "CYBER", "authority": "L1",
     "access": "RSS", "frequency": "daily", "language": "EN", "enabled": False,
     "url": "https://www.cisa.gov", "notes": "CISA 汽车相关安全公告"},
    # ==================== OEM 官方 ====================
    {"source_id": "OEM-TESLA", "region": "GLOBAL", "source_type": "MANUFACTURER_NOTICE", "authority": "L2",
     "access": "WEB", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "https://www.tesla.com/support", "notes": "Tesla 安全更新/OTA 说明"},
    {"source_id": "OEM-VW", "region": "GLOBAL", "source_type": "MANUFACTURER_NOTICE", "authority": "L2",
     "access": "WEB", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "", "notes": "VW 集团安全公告"},
    {"source_id": "OEM-BY", "region": "CN", "source_type": "MANUFACTURER_NOTICE", "authority": "L2",
     "access": "WEB", "frequency": "monthly", "language": "ZH", "enabled": False,
     "url": "", "notes": "比亚迪安全通告"},
    {"source_id": "OEM-NIO", "region": "CN", "source_type": "MANUFACTURER_NOTICE", "authority": "L2",
     "access": "WEB", "frequency": "monthly", "language": "ZH", "enabled": False,
     "url": "", "notes": "蔚来安全通告"},
    {"source_id": "OEM-XPENG", "region": "CN", "source_type": "MANUFACTURER_NOTICE", "authority": "L2",
     "access": "WEB", "frequency": "monthly", "language": "ZH", "enabled": False,
     "url": "", "notes": "小鹏安全通告"},
    # ==================== 专业媒体/权威机构（L3-L4） ====================
    {"source_id": "MEDIA-AUTOBLOG", "region": "US", "source_type": "INCIDENT", "authority": "L4",
     "access": "RSS", "frequency": "daily", "language": "EN", "enabled": False,
     "url": "https://www.autoblog.com/rss.xml", "notes": "专业媒体（低可信候选）"},
    {"source_id": "MEDIA-CARNEWS", "region": "CN", "source_type": "INCIDENT", "authority": "L4",
     "access": "WEB", "frequency": "daily", "language": "ZH", "enabled": False,
     "url": "", "notes": "汽车新闻（低可信候选）"},
    {"source_id": "INST-JD-POWER", "region": "US", "source_type": "INCIDENT", "authority": "L3",
     "access": "WEB", "frequency": "monthly", "language": "EN", "enabled": False,
     "url": "", "notes": "J.D. Power 质量研究"},
]


def main() -> int:
    by_region = Counter(s["region"] for s in SOURCES)
    by_type = Counter(s["source_type"] for s in SOURCES)
    by_authority = Counter(s["authority"] for s in SOURCES)
    enabled = [s for s in SOURCES if s["enabled"]]
    print("=" * 60)
    print("Source Registry v3（全域安全情报）")
    print("=" * 60)
    print(f"总来源: {len(SOURCES)} | 已启用: {len(enabled)}")
    print(f"地域分布: {dict(by_region)}")
    print(f"类型分布: {dict(by_type)}")
    print(f"权威层级: {dict(by_authority)}")
    print("\n已启用来源:")
    for s in enabled:
        print(f"  [{s['region']:6s}][{s['source_type']:20s}] {s['source_id']} ({s['access']})")
    print(f"\n待启用（后续批次）: {len(SOURCES) - len(enabled)} 个")

    out = ROOT / "data" / "intelligence_agent_v3" / "source_registry_v3.json"
    out.write_text(json.dumps({
        "version": "v3", "generated_at": "2026-08-15",
        "total": len(SOURCES), "enabled": len(enabled),
        "principle": "Authority First；宽进严出；raw 永久保留",
        "sources": SOURCES,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已保存: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

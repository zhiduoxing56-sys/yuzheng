# CARLA 接入第零关：环境与风险盘点

- 审计时间：2026-08-05 09:24:21 +08:00
- 审计范围：本机 Windows、硬件、磁盘、Conda/Python、CARLA 遗留项、端口、语证 Git 与运行进程、安全软件和防火墙
- 执行约束：未安装或下载 CARLA；未修改 Python/Conda 环境；未修改语证前端或后端；未创建桥接实现；本报告是本次唯一项目文件变更
- 总结论：**第零关通过；无硬性阻塞项。有条件允许进入第一关，但本次执行到此停止，不执行第一关。**

## 一、盘点结果

| # | 检查项 | 实际输出摘要 | 结论 |
|---|---|---|---|
| 1 | Windows 完整版本 | Microsoft Windows 11 家庭版 中文版，25H2，64 位；内核版本 `10.0.26200`；完整构建号 `26200.8875`。注册表兼容字段 `ProductName` 仍显示 `Windows 10 Home China`，以 `Get-ComputerInfo` 的 `OsName` 和构建号为准。未发现 Windows Insider 选择项。 | 通过 |
| 2 | 显卡、显存、驱动 | NVIDIA GeForce RTX 4060 Laptop GPU；`nvidia-smi` 报告显存 `8188 MiB`；NVIDIA 驱动 `560.94`；WMI 驱动版本 `32.0.15.6094`，日期 2024-08-14，设备状态 `OK`。WMI 的 `AdapterRAM` 仅报约 4 GiB，是该字段的 32 位容量上限问题，显存以 `nvidia-smi` 为准。 | 硬件通过；驱动列风险 |
| 3 | 内存总量 | `102860972032` bytes，约 `95.8 GiB`。 | 通过 |
| 4 | 各磁盘剩余空间 | C: 91.59 GiB / 451.42 GiB；D: 200.93 GiB / 500.23 GiB；E: 355.76 GiB / 431.00 GiB；F: 199.45 GiB / 500.50 GiB；均为 NTFS。 | 通过 |
| 5 | `D:\CARLA\0.9.16` 适用性 | 目标目录和父目录 `D:\CARLA` 当前均不存在；D: 存在且剩余 200.93 GiB；D:\ ACL 对 `Authenticated Users` 授予 `Modify`。路径短、无空格、按版本隔离，适合作为安装目录。审计过程未创建该目录。 | 通过 |
| 6 | Conda 版本和环境 | Conda `24.11.3`。环境：`base`、`carla`、`clean_env`、`label-studio`、`label_studio`、`math_project`、`myenv`、`pyfhel_env`、`tts_env`、`vguard`、`vguard_clean`、`yuzheng311`。 | 通过；旧 `carla` 环境列风险 |
| 7 | `yuzheng311` Python | 可执行文件 `D:\software\anaconda\envs\yuzheng311\python.exe`；Python `3.11.15`，64 位。 | 通过 |
| 8 | `carla` Python 包 | `yuzheng311` 中 `find_spec('carla')` 为 `None`，即未安装。另在旧环境 `D:\software\anaconda\envs\carla\Lib\site-packages` 发现 `carla` 和 `carla-0.9.13.dist-info`，元数据版本 `0.9.13`。 | `yuzheng311` 通过；全机已有旧包，列风险 |
| 9 | 旧 CARLA 目录或进程 | 发现 `D:\CARLA_0.9.13`、`D:\CARLA_clean`、`D:\项目\carla_0.9.13`，三处均含 `CarlaUE4.exe`/Shipping 可执行文件；另有 Conda 环境 `D:\software\anaconda\envs\carla`。进程筛查未发现 `CarlaUE4`、CARLA 或 Unreal 进程。 | 无运行冲突；遗留项列风险 |
| 10 | 2000、2001 端口 | TCP 和 UDP 均无匹配监听或占用。 | 通过 |
| 11 | 语证 Git 状态 | 分支 `backend-contract-freeze-v1`；提交 `ecb9701b6c20cfb9f360b3b33292ebd22e75bc78`；18 个已跟踪变更条目，22 个未跟踪条目（目录按 Git 短格式折叠）。 | Git 可识别；脏工作区列风险 |
| 12 | 后端和前端运行状态 | 后端一：PID 58772，`uvicorn app.main:app --host 127.0.0.1 --port 8000`，监听 8000；后端二：PID 76456，`uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8765`，监听 8765；前端：PID 63116，Vite，监听 5173（父 npm PID 8576）。 | 正在运行；与 2000/2001 无冲突 |
| 13 | 至少 25 GiB 安装空间 | 推荐安装盘 D: 剩余 200.93 GiB，超过 25 GiB 门槛约 175.93 GiB。 | 通过 |
| 14 | 显卡、权限、杀毒、防火墙风险 | GPU 型号和显存足够；显卡驱动日期较旧。审计进程为非管理员沙箱身份，但 D:\ ACL 允许普通认证用户修改。Windows Defender 实时保护开启、篡改保护开启、Controlled Folder Access 关闭；同时 Security Center 注册了 Lenovo Anti-Virus powered by Huorong Security。Domain/Private/Public 三个防火墙配置均开启。发现 6 条启用的旧 `CARLA UE4` Public 入站 Allow 规则，只绑定旧 0.9.13 路径，不覆盖建议的新目录。 | 无硬阻塞；存在驱动、扫描、首次防火墙授权和旧规则风险 |

## 二、Git 已修改和未跟踪项

实际 `git status --short --branch` 输出如下。该清单在生成本报告之前采集，因此不包含本报告自身的新增状态。

```text
## backend-contract-freeze-v1
 M .gitignore
 M README.md
 M backend/app/api/routes.py
 M backend/app/services/audit/effective.py
 M backend/app/services/audit/repository.py
 M backend/app/services/decision/safety_gate.py
 M backend/app/services/presentation/assembler.py
 M backend/app/services/quality/evaluator.py
 M backend/app/services/review/service.py
 M backend/app/services/workflow/repository.py
 M backend/tests/contract/test_frontend_contract_v1.py
 M backend/tests/stage3/test_stage3_scenarios.py
 M backend/tests/stage4/test_stage4_workflow.py
 M backend/tests/stage5/test_trusted_voice_pipeline.py
 M config/action_evidence_map.yaml
 M config/safety_rules.yaml
 M config/semantic_rules.yaml
AM tests/batch_commands.json
?? .idea/
?? backend/app/models/read_models.py
?? backend/app/services/read_cache.py
?? backend/scripts/
?? backend/tests/performance/
?? backend/tests/scenarios/test_comfort_alignment_regression.py
?? docs/audit-performance-baseline-2026-08-04.md
?? docs/comfort-command-alignment-results-2026-08-04.md
?? docs/page-read-performance-baseline-2026-08-04.md
?? docs/page-read-performance-results-2026-08-04.md
?? docs/plans/2026-08-04-audit-performance-design.md
?? docs/plans/2026-08-04-comfort-command-alignment-design.md
?? docs/plans/2026-08-04-evidence-layer-list-design.md
?? docs/plans/2026-08-04-page-read-performance-design.md
?? frontend/
?? scripts/smoke_interpreter_provider.py
?? test-results/
?? tools/
?? 前端2.zip
?? 前端2/
?? 后端运行.docx
?? 语证.docx
```

说明：`AM tests/batch_commands.json` 表示该文件已加入暂存区，之后工作区又有修改。以上现存改动均未被本次审计改写。

## 三、实际执行命令与输出摘要

以下命令均为只读查询；唯一写操作是创建 `docs/carla` 目录并写入本报告。

### 1. Windows 版本

```powershell
$cv = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'; [pscustomobject]@{ProductName=$cv.ProductName; DisplayVersion=$cv.DisplayVersion; EditionID=$cv.EditionID; CurrentBuild=$cv.CurrentBuild; UBR=$cv.UBR; FullBuild=($cv.CurrentBuild+'.'+$cv.UBR); BuildLabEx=$cv.BuildLabEx; InstallationType=$cv.InstallationType} | Format-List
Get-ComputerInfo | Select-Object WindowsProductName,WindowsEditionId,WindowsVersion,OsName,OsDisplayVersion,OsVersion,OsBuildNumber,OsArchitecture | Format-List
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\WindowsSelfHost\UI\Selection' -ErrorAction SilentlyContinue
```

输出摘要：`OsName=Microsoft Windows 11 家庭版 中文版`，`OsDisplayVersion=25H2`，`OsVersion=10.0.26200`，注册表 `UBR=8875`，完整构建号 `26200.8875`，`OsArchitecture=64-bit`；未发现 Insider selection key。

### 2. GPU、显存与驱动

```powershell
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion,DriverDate,VideoProcessor,Status | Format-List
```

输出摘要：`NVIDIA GeForce RTX 4060 Laptop GPU, 8188 MiB, 560.94`；WMI 状态 `OK`，驱动日期 `2024/8/14`。

### 3. 内存与磁盘

```powershell
Get-CimInstance Win32_ComputerSystem | Select-Object @{N='TotalPhysicalMemoryBytes';E={$_.TotalPhysicalMemory}},@{N='TotalPhysicalMemoryGiB';E={[math]::Round($_.TotalPhysicalMemory/1GB,2)}} | Format-List
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | Select-Object DeviceID,VolumeName,@{N='SizeGiB';E={[math]::Round($_.Size/1GB,2)}},@{N='FreeGiB';E={[math]::Round($_.FreeSpace/1GB,2)}},FileSystem | Format-Table -AutoSize
```

输出摘要：内存 95.8 GiB；C/D/E/F 剩余空间分别为 91.59/200.93/355.76/199.45 GiB。初次在受限沙箱内调用 CIM 曾返回 `Access denied (0x80041003)`，随后经批准仅以只读提升查询成功；未更改系统状态。

### 4. 安装目录与权限

```powershell
Test-Path -LiteralPath 'D:\CARLA\0.9.16'
Test-Path -LiteralPath 'D:\CARLA'
Get-Acl -LiteralPath 'D:\' | Select-Object Owner,AccessToString | Format-List
```

输出摘要：目标和父目录均不存在；D:\ 所有者为 `NT AUTHORITY\SYSTEM`，`Authenticated Users` 具有 `Modify, Synchronize` 权限。

### 5. Conda、`yuzheng311` 与 Python 包

```powershell
& 'D:\software\anaconda\Scripts\conda.exe' --version
& 'D:\software\anaconda\Scripts\conda.exe' env list
& 'D:\software\anaconda\envs\yuzheng311\python.exe' -c "import sys, importlib.metadata as m, importlib.util as u; print('executable='+sys.executable); print('version='+sys.version.replace(chr(10),' ')); spec=u.find_spec('carla'); print('carla_spec='+str(spec)); print('carla_origin='+str(spec.origin if spec else None))"
Get-ChildItem -LiteralPath 'D:\software\anaconda\envs\carla\Lib\site-packages' -Force | Where-Object { $_.Name -match 'carla' }
Get-Content -LiteralPath 'D:\software\anaconda\envs\carla\Lib\site-packages\carla-0.9.13.dist-info\METADATA' -TotalCount 20 | Select-String '^(Name|Version):'
```

输出摘要：Conda 24.11.3，共列出 12 个环境；`yuzheng311` 为 Python 3.11.15，`carla_spec=None`；旧 `carla` 环境中元数据为 `Name: carla`、`Version: 0.9.13`。未调用其他环境的 Python，也未修改环境。

### 6. 旧 CARLA 目录、进程和防火墙遗留

```powershell
Get-ChildItem -LiteralPath 'D:\CARLA_0.9.13' -Filter 'CarlaUE4.exe' -Recurse -ErrorAction SilentlyContinue
Get-ChildItem -LiteralPath 'D:\CARLA_clean' -Filter 'CarlaUE4.exe' -Recurse -ErrorAction SilentlyContinue
Get-ChildItem -LiteralPath 'D:\项目\carla_0.9.13' -Filter 'CarlaUE4*.exe' -Recurse -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'Carla|UE4|Unreal' -or $_.CommandLine -match 'carla' } | Select-Object ProcessId,Name,ExecutablePath,CommandLine
Get-NetFirewallRule | Where-Object { $_.DisplayName -eq 'CARLA UE4' }
```

输出摘要：三处旧目录均含 CARLA 可执行文件；没有 CARLA/UE4/Unreal 进程；存在 6 条启用的 Public 入站 Allow 规则，分别成对指向：

- `D:\CARLA_0.9.13\WindowsNoEditor\CarlaUE4\Binaries\Win64\CarlaUE4-Win64-Shipping.exe`
- `D:\CARLA_clean\WindowsNoEditor\CarlaUE4\Binaries\Win64\CarlaUE4-Win64-Shipping.exe`
- `D:\项目\carla_0.9.13\WindowsNoEditor\CarlaUE4\Binaries\Win64\CarlaUE4-Win64-Shipping.exe`

### 7. 端口与当前前后端

```powershell
$tcp=netstat -ano -p tcp; $udp=netstat -ano -p udp; foreach($p in 2000,2001){ $tcp | Select-String (':'+$p+'\s'); $udp | Select-String (':'+$p+'\s') }
netstat -ano -p tcp
Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|uvicorn|node|npm|vite' -or $_.CommandLine -match 'uvicorn|vite|语证|yuzheng' } | Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine | Format-List
```

输出摘要：2000/2001 无 TCP 或 UDP 匹配；8000、8765、5173 正在监听。进程命令行确认 8000 和 8765 为两个语证 Uvicorn 后端，5173 为 `D:\语证\frontend` 的 Vite 前端。

### 8. Git

```powershell
git branch --show-current
git rev-parse HEAD
git status --porcelain=v1
git status --short --branch
```

输出摘要：分支 `backend-contract-freeze-v1`；提交 `ecb9701b6c20cfb9f360b3b33292ebd22e75bc78`；报告生成前为 18 个已跟踪变更、22 个未跟踪短格式条目。

### 9. 杀毒软件和防火墙

```powershell
Get-MpComputerStatus | Select-Object AntivirusEnabled,AntispywareEnabled,RealTimeProtectionEnabled,BehaviorMonitorEnabled,IoavProtectionEnabled,NISEnabled,OnAccessProtectionEnabled,IsTamperProtected,AntivirusSignatureVersion,AntivirusSignatureLastUpdated | Format-List
Get-MpPreference | Select-Object EnableControlledFolderAccess,ExclusionPath,DisableRealtimeMonitoring | Format-List
Get-NetFirewallProfile | Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction,NotifyOnListen | Format-Table -AutoSize
Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | Select-Object displayName,productState,pathToSignedProductExe,timestamp | Format-List
```

输出摘要：Defender 实时保护、行为监控、网络检查和篡改保护均开启；Controlled Folder Access 为 0；签名版本 `1.455.509.0`，更新时间 2026-08-05 00:42:12；Lenovo Anti-Virus powered by Huorong Security 和 Windows Defender 均在 Security Center 注册；三种防火墙配置均开启。当前非管理员令牌无法查看 Defender 排除目录，这是审计可见性限制，不是安装阻塞。

## 四、通过项

1. Windows 11 64 位系统可识别，未发现 Insider 通道配置。
2. RTX 4060 Laptop GPU、约 8 GiB 显存、95.8 GiB 内存满足本地运行基础资源要求。
3. D: 剩余 200.93 GiB，显著高于 25 GiB 门槛。
4. `D:\CARLA\0.9.16` 不与现存目录重叠，D:\ ACL 允许创建和修改，命名清晰。
5. `yuzheng311` 可用且未污染：其中没有 `carla` 包。
6. CARLA 默认 RPC/Streaming 端口 2000、2001 的 TCP/UDP 均空闲。
7. 当前没有 CARLA/UE4/Unreal 进程。
8. 当前语证前后端虽在运行，但端口 5173/8000/8765 与 CARLA 默认端口无冲突。

## 五、风险项

1. **旧版本误用风险**：存在三份旧 CARLA 0.9.13 目录、旧 Conda 环境 `carla` 和 `carla 0.9.13` Python 包。后续必须使用版本化绝对路径，不可复用旧环境名称。
2. **防火墙遗留风险**：6 条同名旧规则仅绑定旧 0.9.13 可执行文件且 Profile 为 Public；它们不会自动授权新 0.9.16 路径，且重复规则容易造成判断混乱。第零关不删除或修改它们。
3. **杀毒扫描风险**：Defender 实时保护开启，且系统注册了联想火绒安全组件。CARLA 解压包含大量二进制与资源，后续可能出现扫描变慢、隔离或首次运行拦截。Controlled Folder Access 当前关闭，降低了目录写入阻断概率。
4. **显卡驱动风险**：RTX 4060 硬件合格，但驱动 560.94 日期为 2024-08-14，相对审计日期较旧。进入实际运行前应验证 CARLA 0.9.16/UE 运行稳定性；本关不更新驱动。
5. **权限风险**：普通用户对 D:\ 有修改权限，安装目录本身不构成阻塞；但新增或调整防火墙规则可能触发 UAC/管理员授权。
6. **Git 基线风险**：语证工作区已有大量已修改和未跟踪内容。后续任何需要修改仓库的接入关卡都必须先保护现状并明确变更边界，避免把既有改动误归入 CARLA 接入。
7. **运行实例风险**：语证当前同时运行两个 Uvicorn 后端（8000、8765）。虽然不冲突，但后续联调时必须明确使用哪一个实例，避免请求落到错误后端。

## 六、阻塞项

**无当前硬性阻塞项。**

- 没有 GPU、显存、内存或磁盘容量阻塞。
- 没有目标目录命名或基础 ACL 阻塞。
- 没有 2000/2001 端口阻塞。
- 没有正在运行的旧 CARLA 进程阻塞。
- 杀毒、防火墙、旧版本遗留、较旧驱动和 Git 脏工作区均需在后续关卡受控处理，但本次审计证据不足以将其判定为硬阻塞。

## 七、建议

- **建议安装目录：`D:\CARLA\0.9.16`**
- **建议独立 Conda 环境名称：`carla0916`**
- 不建议复用 `carla`，因为该名称已指向含 `carla 0.9.13` 的旧环境。
- 不建议把 CARLA Python 包直接装入 `yuzheng311`；后续应先在第一关核验 CARLA 0.9.16 官方 Python API 与目标 Python 版本的兼容矩阵，再创建独立环境。
- 旧目录、旧环境和旧防火墙规则暂时保留；只有在另行授权且确认不再需要时才清理。

## 八、是否允许进入第一关

**结论：有条件允许。**

进入第一关的边界条件：

1. 只使用新目录 `D:\CARLA\0.9.16` 和新环境名 `carla0916`，不覆盖或复用任何 0.9.13 资产。
2. 第一关开始前明确 CARLA 0.9.16 的官方来源、校验方式、压缩包预计体积和 Python 兼容版本。
3. 首次运行时单独处理新可执行文件的防火墙授权，不假定旧规则有效。
4. 保持 `yuzheng311` 不变，并保护当前语证 Git 工作区的既有改动。

按照本次任务约束，**报告完成后立即停止；未执行第一关。**

# R4 Final 语义一致性修补设计

## 背景与目标

以 `intent_registry_r4_full_draft.yaml` 为只读父版本，只实施人工批准的九类修补，输出 final candidate、full→final 差异报告和最终校验结果。禁止自由发现新 Intent、修改 71 项 FORMAL、重映射数据、扩写或训练。

## 现状与约束

- 当前 16 个参数型 Known Unsupported Intent 的 VALUE 合同错误地为 OPTIONAL。
- AREA 来自单 Intent 少量示例，不满足 family-level union。
- 8 个已批准 Intent 尚未进入 registry。
- MEDIA/CAMERA mode 直接聚合原始值，存在跨对象污染或动作误作模式。
- R3 与 R4 core 的 SHA256 必须保持不变，full draft 本身也不修改。

## 方案比较

### 方案一：直接手工修改 YAML

- 优点：改动快。
- 缺点：证据、统计、ontology 和差异容易遗漏，无法稳定复现。

### 方案二：受控 final builder（采用）

- 优点：从冻结 full draft 确定性派生；8 个新增 Intent、9 个 AREA family、MEDIA/CAMERA 清洗均有显式白名单和原始证据；校验器可冻结 FORMAL 集合与父文件哈希。
- 缺点：需要新增构建和校验代码。

### 方案三：重写 full expansion 分类器

- 优点：可统一早期分类逻辑。
- 缺点：会重新扫描并改变本轮未批准范围，违反任务边界。

## 详细设计

### 架构

1. 读取 full draft、R3、R4 core 和原始 MAC train/dev/test。
2. 使用仅含 8 个新增 Intent 的精确分类器建立证据 manifest。
3. 对 9 个 family 从全部原始 frame 汇总位置，映射 `area_catalog` 后生成 family-level union；未映射位置写入结构化 `AREA_PENDING_REPORT`。
4. MEDIA 仅接受原文与 frame 都明确指向媒体音效/音效模式/声场效果的值；CAMERA 仅接受明确“模式选择/切换”的摄像模式。其余分别进入 pending。
5. 从 full draft 深拷贝并应用批准修补，重算 family、intent、ontology 和统计，写出 final candidate。
6. 生成 full→final diff 和 validator JSON。

### VALUE 合同

新增七个 `SOURCE_*_REQUIRED` 合同。16 个指定 Intent 的 `required_slots` 加入 VALUE，并从 `optional_slots` 删除 VALUE。相对表达允许保留为语义 VALUE；无可靠物理幅度时仍 unresolved，不引入固定温度、百分比或档位。

### AREA 策略

九个指定 family 的全部 ON/OFF/SET Intent 共享相同 `allowed_areas` 和 AREA slot policy。仅使用 `area_catalog` 可证明映射；“中排左”“三排”“最后一排”等不猜测。方向盘加热固定为单实例，完全删除 AREA。

### 新增 Intent

新增且仅新增：`AIR_PURIFIER_SET_FAN_SPEED`、`DISPLAY_SET_MODE`、`READING_LIGHT_SET_MODE`、`REFRIGERATOR_SET_MODE`、`FRAGRANCE_SET_SCENT`、`INTERIOR_LIGHT_SET_BRIGHTNESS`、`INTERIOR_LIGHT_SET_COLOR`、`INTERIOR_LIGHT_SET_MODE`。全部为 `KNOWN_UNSUPPORTED_CONTROL`、`PROJECT_NATIVE`，不得进入 FORMAL。

### guidance 与 pending

在 `annotation_guidance` 中同步 registry version，加入车内灯词法边界、family AREA policy、`AREA_PENDING_REPORT`、MEDIA mode pending、`camera_action_pending` 和 FRUNK pending operation。pending 只记录证据，不创建新 Intent。

## 测试策略

- 精确冻结 FORMAL ID 集合与顺序、R3/core/full 父文件哈希。
- 精确冻结 final 相对 full 只新增上述 8 个 Intent。
- 校验 Intent ID 和 action+target+attribute 唯一、合同引用、required/optional 互斥、ontology、mode string 类型。
- 校验 AREA family 一致性、方向盘加热无 AREA、MEDIA/CAMERA 禁止值、FRUNK_CLOSE 不存在、`FOLLOWING_GAP_REQUIRED` 不存在。
- 联合运行 R3、core、full、final 回归测试。

## 边界

不修改 full draft，不做数据重映射、数据扩写、训练、运行时接入或任何未批准 Intent 扩展。

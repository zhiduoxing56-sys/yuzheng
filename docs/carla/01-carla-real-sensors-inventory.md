# CARLA 0.9.16 真实传感器整理

## 结论

CARLA 把所有 `sensor.*` Actor 都称为传感器，但其中并不都是现实世界中可安装的硬件。

根据本项目 `carla_reference` 中的 CARLA 0.9.16 运行时蓝图库和采样结果，当前安装版共有 **19 个传感器蓝图**。如果“真实传感器”是指现实车辆上存在直接对应硬件、且 CARLA 输出可作为该类硬件仿真数据使用，则核心是以下 **6 类**：

1. RGB 摄像头
2. DVS 事件摄像头
3. 机械式/扫描式激光雷达
4. 毫米波雷达
5. GNSS 卫星定位接收机
6. IMU 惯性测量单元

常规自动驾驶车辆的主流组合是 **RGB 摄像头 + 激光雷达 + 毫米波雷达 + GNSS + IMU**；DVS 属于有真实硬件对应、但较偏研究和特殊场景的传感器。

## 一、具有现实硬件对应的传感器

| 现实传感器 | CARLA 蓝图 ID | CARLA 数据类型 | 主要输出 | 本机 0.9.16 验证 | 使用判断 |
|---|---|---|---|---|---|
| RGB 摄像头 | `sensor.camera.rgb` | `carla.Image` | 彩色 BGRA 图像、时间戳、位姿 | 创建成功并取得样本 | 真实摄像头的主要仿真入口；可配置分辨率、视场角、曝光、镜头畸变和后处理 |
| DVS 事件摄像头 | `sensor.camera.dvs` | `carla.DVSEventArray` | 像素坐标、事件时间、亮度变化极性 | 创建成功并取得样本 | 有真实事件相机对应；适合高速运动、强动态范围和低时延研究 |
| 激光雷达 | `sensor.lidar.ray_cast` | `carla.LidarMeasurement` | 三维点坐标和强度 | 创建成功并取得样本 | 对应扫描式 LiDAR；可配置线数、量程、扫描频率、视场、点频率、衰减和噪声 |
| 毫米波雷达 | `sensor.other.radar` | `carla.RadarMeasurement` | 目标距离、径向速度、方位角、俯仰角 | 创建成功并取得样本 | 对应车载雷达，但模型较抽象，不等同于某一具体量产雷达的原始 ADC/点云协议 |
| GNSS | `sensor.other.gnss` | `carla.GnssMeasurement` | 经度、纬度、海拔 | 创建成功并取得样本 | 对应卫星定位接收机；支持经纬高偏置、标准差和随机种子 |
| IMU | `sensor.other.imu` | `carla.IMUMeasurement` | 三轴加速度、三轴角速度、指南针航向 | 创建成功并取得样本 | 对应加速度计、陀螺仪及磁航向组合；支持噪声和零偏配置 |

### 建模真实性注意事项

- 上述 6 类有真实硬件对应，但 CARLA 给出的是仿真测量，不能自动视为某个真实品牌/型号传感器的完整数字孪生。
- 当前参考文件中的 GNSS、IMU 和 LiDAR 默认噪声标准差均为 `0`，直接使用会比真实设备理想。做现实迁移时应主动加入噪声、偏置、丢点、时延和标定误差。
- RGB 相机包含曝光、光圈、ISO、运动模糊、镜头畸变等参数，但渲染图像仍受场景资产和渲染引擎限制。
- CARLA 雷达输出已是检测点，不是现实雷达的原始电磁回波或 ADC 数据。

## 二、有类似现实设备，但 CARLA 输出属于仿真真值

这些能力可以用于训练标签、算法验证或中间结果对照，但不应直接说成车辆上存在同名硬件传感器。

| CARLA 蓝图 ID | 输出 | 为什么不归入核心真实传感器 |
|---|---|---|
| `sensor.camera.depth` | 每像素场景深度 | 现实中有双目、ToF、结构光等深度设备，但 CARLA 直接从渲染场景生成深度真值，并非某种具体深度硬件模型 |
| `sensor.camera.semantic_segmentation` | 每像素语义类别 | 是引擎已知物体类别生成的真值标签；现实相机不能直接测得语义 |
| `sensor.camera.instance_segmentation` | 每像素实例 ID/类别 | 是实例级真值标签，不是物理成像传感器的直接输出 |
| `sensor.camera.optical_flow` | 每像素运动向量 | 是仿真生成的稠密光流真值；现实中通常由相机图像经过算法估计 |
| `sensor.camera.normals` | 表面法向图 | 是几何/渲染真值，现实车辆通常不会由单一传感器直接输出 |
| `sensor.lidar.ray_cast_semantic` | 点坐标、入射角、对象 ID、语义标签 | 前半部分近似 LiDAR，语义与对象 ID 来自仿真世界真值，现实 LiDAR 不会直接给出 |
| `sensor.camera.cosmos_visualization` | 可视化图像 | 当前安装版的扩展可视化蓝图，不在参考文件的标准 0.9.16 官方传感器目录中；不作为车辆物理传感器 |

上述 7 个蓝图在本次运行时探测中均已成功创建并取得样本。

## 三、虚拟事件检测器，不是物理传感器硬件

| CARLA 蓝图 ID | 功能 | 本次状态 | 定位 |
|---|---|---|---|
| `sensor.other.collision` | 碰撞事件、对方 Actor、冲量 | 创建成功；场景未触发 | 仿真碰撞事件监听器，可类比碰撞检测逻辑，但不是某种车载传感器模型 |
| `sensor.other.lane_invasion` | 车轮中心跨越 OpenDRIVE 车道线事件 | 创建成功；场景未触发 | 基于地图和车辆位置判断；不是摄像头车道线识别 |
| `sensor.other.obstacle` | 沿指定方向做距离/半径检测 | 创建成功；场景未触发 | 基于射线检测的虚拟障碍物探测器；不能直接等同超声波雷达 |

特别注意：CARLA 标准蓝图库中没有单独的 `sensor.other.ultrasonic`。如果项目需要倒车超声波，不能仅把 `sensor.other.obstacle` 改名后就声称完成了真实超声波建模；至少还需定义波束、盲区、量程、噪声、更新率和多径/误检等行为。

## 四、通信与安全能力，不属于环境感知硬件

| CARLA 蓝图 ID | 功能 | 本次状态 | 说明 |
|---|---|---|---|
| `sensor.other.v2x` | CAM 类 V2X 协同消息 | 创建成功；缺少配对/触发，未收到样本 | 对应车联网通信能力，不是摄像头、雷达一类物理感知器 |
| `sensor.other.v2x_custom` | 自定义 V2X 消息 | 创建成功；未调用发送或缺少接收端 | 需要发送端和接收端配合 |
| `sensor.other.rss` | Responsibility Sensitive Safety 响应 | 本次跳过 | 属于责任敏感安全计算能力；默认关闭或需要专门构建支持，不是物理传感器 |

## 五、完整盘点与数量核对

| 分类 | 数量 | 蓝图 |
|---|---:|---|
| 有现实硬件直接对应 | 6 | RGB、DVS、LiDAR、Radar、GNSS、IMU |
| 仿真真值/可视化 | 7 | Depth、Semantic Camera、Instance Camera、Optical Flow、Normals、Semantic LiDAR、Cosmos Visualization |
| 虚拟事件检测器 | 3 | Collision、Lane Invasion、Obstacle |
| 通信与安全能力 | 3 | V2X、V2X Custom、RSS |
| **合计** | **19** | 与 CARLA 0.9.16 本机运行时蓝图库一致 |

运行时结果中：**18 个蓝图创建成功，1 个 RSS 跳过；13 个取得数据样本，5 个因事件或配对条件未满足而没有样本。** “未产生样本”不代表该蓝图不存在或不可创建。

## 六、项目选型建议

如果目标是构建尽量接近现实自动驾驶车辆的传感器输入，建议主链路只使用：

```text
sensor.camera.rgb
sensor.lidar.ray_cast
sensor.other.radar
sensor.other.gnss
sensor.other.imu
```

需要事件视觉研究时再加入：

```text
sensor.camera.dvs
```

深度、语义分割、实例分割、光流、表面法向和语义 LiDAR 建议放在“训练标签/评估真值”通道，不要作为算法在真实车辆上可以直接获得的输入。碰撞、越线和障碍物检测器建议放在仿真评测或安全判定通道。

## 依据与口径

- 运行时完整能力记录：`carla_reference/carla_full_capabilities.json`
- 人工可读运行时清单：`carla_reference/carla_sensor_inventory.txt`
- 记录环境：CARLA Client/Server 0.9.16，地图 `Town10HD_Opt`
- 本文中的“取得样本”是指参考记录采集时成功创建 Actor 并收到回调数据；不是现实道路实采数据。

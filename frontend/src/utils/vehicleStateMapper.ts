import type { VehicleState } from "../types/contract";

const labels: Record<keyof VehicleState, string> = {
  state_epoch_id: "状态周期",
  started_at: "状态开始时间",
  reset_count: "重置次数",
  last_reset_at: "最近重置时间",
  reset_reason: "重置原因",
  vehicle_speed: "当前车速",
  gear_position: "挡位",
  door_lock_state: "车门锁状态",
  door_state: "车门状态",
  occupant_role: "乘员角色",
  speaker_zone: "发声位置",
  vehicle_mode: "车辆模式",
  authentication_state: "身份认证状态",
  ambient_light: "环境光照",
  headlight_state: "前照灯状态",
  wiper_mode: "雨刮模式",
  wiper_intensity: "雨刮强度",
  wiper_frequency: "雨刮频率",
  wiper_wiping: "雨刮工作状态",
  wiper_error: "雨刮故障状态",
  weather: "天气",
  window_state: "车窗状态",
  navigation_active: "导航状态",
  reverse_camera_active: "倒车影像",
  display_state: "显示屏状态",
  music_state: "音乐状态",
  front_obstacle_distance: "前方障碍距离",
  speed_limit: "道路限速",
  brake_state: "制动状态",
  rear_obstacle_distance: "后方障碍距离",
  road_condition: "路面状况",
  ultrasonic_distance: "超声波距离",
  surround_camera_state: "环视摄像头",
  emergency_flag: "紧急状态",
  collision_state: "碰撞状态",
  collision_target: "碰撞目标",
  collision_at: "碰撞时间",
  surrounding_objects: "周边目标",
  safety_constraint: "安全约束",
  updated_at: "更新时间",
};

const targetKeys: Record<string, readonly (keyof VehicleState)[]> = {
  车门: ["vehicle_speed", "gear_position", "door_lock_state", "door_state", "occupant_role", "speaker_zone", "vehicle_mode", "authentication_state"],
  门锁: ["vehicle_speed", "gear_position", "door_lock_state", "occupant_role", "speaker_zone", "authentication_state"],
  车窗: ["vehicle_speed", "weather", "window_state", "occupant_role", "speaker_zone"],
  前照灯: ["vehicle_speed", "ambient_light", "headlight_state", "weather"],
  雨刮: ["weather", "wiper_mode", "wiper_intensity", "wiper_frequency", "wiper_wiping", "wiper_error"],
  大屏: ["vehicle_speed", "navigation_active", "reverse_camera_active", "display_state"],
  自动泊车: ["vehicle_speed", "gear_position", "ultrasonic_distance", "surround_camera_state", "occupant_role"],
  速度: ["vehicle_speed", "gear_position", "speed_limit", "front_obstacle_distance", "rear_obstacle_distance", "brake_state", "road_condition"],
  制动: ["vehicle_speed", "rear_obstacle_distance", "brake_state", "road_condition"],
  前挡风除雾: ["weather", "vehicle_speed"],
  音乐: ["music_state"],
};

const unconnectedTargets = new Set(["空调", "温度", "风量"]);

export function vehicleStateLabel(key: keyof VehicleState): string {
  return labels[key] || String(key);
}

export function formatVehicleStateValue(key: keyof VehicleState, value: unknown): string {
  if (value === null || value === undefined || value === "") return "暂无数据";
  if (typeof value === "boolean") return value ? "是" : "否";
  if (key === "vehicle_speed" || key === "speed_limit") return `${value} km/h`;
  if (["front_obstacle_distance", "rear_obstacle_distance", "ultrasonic_distance"].includes(key)) return `${value} m`;
  if (key === "surrounding_objects") {
    const list = Array.isArray(value) ? value : [];
    return list.length ? `${list.length} 个目标` : "暂无数据";
  }
  return String(value);
}

export function relevantVehicleStateEntries(state: VehicleState, target?: string | null): [keyof VehicleState, unknown][] {
  const keys = target ? targetKeys[target] ?? [] : [];
  return keys.filter((key) => state[key] !== null && state[key] !== undefined).map((key) => [key, state[key]]);
}

export function vehicleStateAvailabilityMessage(target?: string | null): string | null {
  if (!target || target === "unknown") return "识别出明确动作和目标后，将只显示与该操作相关的车辆状态。";
  if (unconnectedTargets.has(target)) return `${target === "空调" ? "空调" : target}状态未接入，当前后端车辆状态没有对应字段。`;
  if (!targetKeys[target]) return `当前动作目标“${target}”尚未配置相关车辆状态映射。`;
  return null;
}

export function allVehicleStateEntries(state: VehicleState): [keyof VehicleState, unknown][] {
  return (Object.keys(state) as (keyof VehicleState)[]).filter((key) => state[key] !== null && state[key] !== undefined).map((key) => [key, state[key]]);
}

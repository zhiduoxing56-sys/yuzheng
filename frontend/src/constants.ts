export const HEALTH_POLL_INTERVAL_MS = 10_000;
export const MAX_AUDIO_FILE_SIZE_BYTES = 20 * 1024 * 1024;
export const MAX_AUDIO_FILE_SIZE_LABEL = "20 MiB";
export const SUPPORTED_AUDIO_EXTENSIONS = ["wav", "mp3", "m4a", "flac", "ogg"] as const;
export const PRESENTATION_RETRY_DELAYS_MS = [0, 500, 1_000, 1_500, 2_500, 3_500, 4_000, 5_000] as const;
export const MAX_CORRECTED_TEXT_LENGTH = 2048;

export const SPEAKER_ZONES = [
  "driver",
  "front_passenger",
  "rear_left",
  "rear_right",
  "outside",
  "unknown",
] as const;

export const SUBMISSION_STATUS_LABELS = {
  idle: "等待输入",
  validating: "正在校验",
  submitting: "正在提交",
  processing: "后端处理中",
  waiting_presentation: "等待最终持久化结果",
  partial: "指令已受理，结果待归档",
  completed: "处理完成",
  failed: "处理失败",
} as const;

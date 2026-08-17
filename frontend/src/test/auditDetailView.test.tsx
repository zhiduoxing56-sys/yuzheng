// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { AuditCommandSection, AuditDecisionSection, AuditExecutionSection, AuditReviewSection, AuditSnapshotSection, AuditUnderstandingSection } from "../components/AuditDetailSections";
import type { AuditDetailView } from "../types/contract";

function detail(): AuditDetailView {
  return {
    command_summary: { raw_command: "打开右前车门并关闭右前车窗", input_type: "audio", occurred_at: "2026-08-12T08:08:32Z", final_decision: "BLOCK", execution_status: "NOT_EXECUTED" },
    resolved_operations: [
      { operation: "打开右前车门", position: "右前" },
      { operation: "关闭右前车窗", position: "右前", value: null },
    ],
    decision_snapshot: {
      captured_at: "2026-08-12T08:08:32Z",
      source: "simulator_vehicle_state",
      vehicle_state: [{ key: "vehicle_speed", label: "车速", value: 43, unit: "km/h", source: "Simulator" }],
      environment_state: [],
      sensor_summary: [],
    },
    decision_summary: { final_decision: "BLOCK", aggregate_safety_decision: "BLOCK", hit_rules: ["DOOR_MOVING_BLOCK"], reason_codes: ["VEHICLE_MOVING"], reasons: [] },
    key_evidence: [{ label: "车速", value: 43, unit: "km/h", source: "Simulator" }],
    intent_decisions: [
      { operation: "打开右前车门", decision: "BLOCK", reasons: ["车辆正在行驶"], hit_rules: ["DOOR_MOVING_BLOCK"], key_evidence: [{ label: "车速", value: 43, unit: "km/h" }] },
      { operation: "关闭右前车窗", decision: "PASS", reasons: ["当前证据满足安全条件"], hit_rules: [], key_evidence: [] },
    ],
    llm_explanation: { status: "AVAILABLE", text: "车辆正在行驶，打开车门不满足安全条件。系统因此拒绝相关操作。" },
    clarification_history: [],
    authorization_summary: { status: "NOT_AUTHORIZED", authorized: false },
    execution_summary: { status: "NOT_EXECUTED" },
    execution_before_snapshot: null,
    execution_after_snapshot: null,
    execution_changes: [],
  };
}

afterEach(cleanup);

describe("human-readable AuditDetailView", () => {
  it("renders the six audit areas without exposing occurrence ids or empty placeholders", () => {
    const data = detail();
    render(<><AuditCommandSection data={data} /><AuditUnderstandingSection data={data} /><AuditSnapshotSection data={data} /><AuditDecisionSection data={data} /><AuditReviewSection data={data} /><AuditExecutionSection data={data} /></>);
    expect(screen.getAllByText("打开右前车门").length).toBeGreaterThan(0);
    expect(screen.getAllByText("关闭右前车窗").length).toBeGreaterThan(0);
    expect(screen.queryByText("本次无用户复核")).toBeNull();
    expect(screen.queryByText("clause_index")).toBeNull();
    expect(screen.queryByText("intent_id")).toBeNull();
    expect(screen.queryByText("unknown")).toBeNull();
    expect(screen.queryByText("--")).toBeNull();
  });

  it("renders clarification candidates and none-of-above termination", () => {
    const data = detail();
    data.clarification_history = [{ original_text: "运动莫斯", question: "请选择正确指令", review_reasons: ["语音识别不确定"], shown_candidates: [{ display_text: "运动模式" }, { display_text: "运动模式下" }], resolution: "NONE_OF_ABOVE", selected_candidate: null, confirmed_operation: null, command_terminated: true, child_turn_available: false }];
    render(<AuditReviewSection data={data} />);
    expect(screen.getByText("运动模式")).toBeTruthy();
    expect(screen.getByText("运动模式下")).toBeTruthy();
    expect(screen.getByText("都不是，再说一次")).toBeTruthy();
    expect(screen.getByText("本次指令终止")).toBeTruthy();
  });

  it("shows only actual execution changes", () => {
    const data = detail();
    data.execution_changes = [{ key: "vehicle_speed", label: "车速", before: 21.3, after: 28.6, unit: "km/h", delta: 7.3 }];
    render(<AuditExecutionSection data={data} />);
    expect(screen.getByText("21.3 km/h → 28.6 km/h")).toBeTruthy();
    expect(screen.queryByText("变化 +7.3 km/h")).toBeNull();
  });
});

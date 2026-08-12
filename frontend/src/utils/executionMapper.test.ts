import { describe, expect, it } from "vitest";
import type { TurnPresentationResponse, TurnWorkflowStatus } from "../types/contract";
import { executionEnvironmentLabel, getExecutionEligibility, redactAuthorizationToken, requiresExecutionReconciliation } from "./executionMapper";
import { tokenStatusLabel, workflowStatusLabel } from "./workflowMapper";

function executablePresentation(): TurnPresentationResponse {
  return {
    turn_id: "TURN_1",
    authorization: { token_issued: true, token_status: "ISSUED", consumed: false, execution_allowed: true },
    execution: { request_status: "NOT_REQUESTED", execution_status: "NOT_EXECUTED" },
  } as unknown as TurnPresentationResponse;
}

function authorizedWorkflow(): TurnWorkflowStatus {
  return { root_turn_id: "TURN_1", current_turn_id: "TURN_1", status: "AUTHORIZED", review_attempts: 1, max_review_attempts: 3, latest_decision: "PASS", token_status: "ISSUED", event_count: 8, terminal: false };
}

describe("executionMapper", () => {
  it("仅在所有后端执行事实和内存令牌同时满足时允许执行", () => {
    expect(getExecutionEligibility({ turnId: "TURN_1", presentation: executablePresentation(), workflow: authorizedWorkflow(), hasAuthorizationToken: true, writeBusy: false })).toEqual({ allowed: true, reasons: [] });
    expect(getExecutionEligibility({ turnId: "TURN_1", presentation: executablePresentation(), workflow: authorizedWorkflow(), hasAuthorizationToken: false, writeBusy: false }).allowed).toBe(false);
  });

  it("禁止已执行和已取消轮次重复执行", () => {
    const executed = executablePresentation();
    executed.authorization.consumed = true;
    executed.authorization.token_status = "CONSUMED";
    executed.execution.execution_status = "SUCCESS";
    const executedWorkflow = { ...authorizedWorkflow(), status: "EXECUTED", token_status: "CONSUMED" as const, terminal: true };
    expect(getExecutionEligibility({ turnId: "TURN_1", presentation: executed, workflow: executedWorkflow, hasAuthorizationToken: true, writeBusy: false }).allowed).toBe(false);
    const cancelled = { ...authorizedWorkflow(), status: "CANCELLED", token_status: null, terminal: true, latest_decision: "BLOCK" as const };
    expect(getExecutionEligibility({ turnId: "TURN_1", presentation: executablePresentation(), workflow: cancelled, hasAuthorizationToken: true, writeBusy: false }).allowed).toBe(false);
  });

  it("超时或网络中断要求重新查询后端状态", () => {
    expect(requiresExecutionReconciliation("TIMEOUT")).toBe(true);
    expect(requiresExecutionReconciliation("NETWORK_UNAVAILABLE")).toBe(true);
    expect(requiresExecutionReconciliation("WORKFLOW_NOT_ALLOWED")).toBe(false);
  });

  it("执行错误文本不会暴露当前内存令牌", () => {
    const token = "sensitive-one-time-token";
    expect(redactAuthorizationToken(`令牌 ${token} 无效`, token)).toBe("令牌 [授权信息已脱敏] 无效");
  });

  it("映射真实运行环境和工作流状态", () => {
    expect(executionEnvironmentLabel({ vehicle_adapter: "simulator" } as never)).toBe("仿真模式");
    expect(executionEnvironmentLabel({ vehicle_adapter: "mock_bench" } as never)).toBe("车机台架模式");
    expect(workflowStatusLabel("REVIEW_REQUIRED")).toBe("等待人工复核");
    expect(tokenStatusLabel("CONSUMED")).toBe("已使用");
  });
});

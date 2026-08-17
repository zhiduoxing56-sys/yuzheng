// @vitest-environment jsdom

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { getTurnPresentation } from "../api/turns";
import { EvidencePage } from "../pages/EvidencePage";
import { SessionProvider } from "../stores/sessionStore";

vi.mock("../api/turns", () => ({ getTurnPresentation: vi.fn() }));

const node = {
  label: 7, node_id: "KNOWLEDGE_DOOR", node_type: "安全知识", title: "车门开启速度核查", semantic_description: "开门前检查速度与周边目标",
  canonical_action: "DOOR_OPEN", conditions: ["车辆运动"], required_evidence: ["VEHICLE_SPEED"], optional_evidence: ["SURROUNDING_OBJECT_STATE"],
  source: "标准", chapter: "车门", clause: "1.1", trust_level: "L1", rank: 1, similarity: 0.82, result_scope: "ONLINE_TOP_K", threshold_status: "ACCEPTED",
};

const presentation = {
  turn_id: "TURN_1",
  semantic_frame: { raw_text: "打开右后车门" },
  evidence_demand: { intent_demands: [{
    clause_index: 0, intent_id: "DOOR_OPEN", action: "打开", target: "车门", area: "RIGHT_REAR", query_text: "证据查询句",
    knowledge_query_text: "意图=DOOR_OPEN；动作=打开；对象=车门；区域=RIGHT_REAR；运动状态=行驶",
    knowledge_hits: [{ node_id: "KNOWLEDGE_DOOR" }],
    knowledge_retrieval_metadata: {
      status: "READY", eligible_node_count: 1, top_k: 5, ef_search: 30, similarity_threshold: 0.6, accepted_node_count: 1,
      eligible_nodes: [node], raw_results: [node], diagnostic_results: [node], query_vectorization: { model_name: "BAAI/bge-base-zh-v1.5", dimension: 768 },
      context_sources: [{ query_field: "运动状态", query_value: "行驶", evidence_type: "VEHICLE_SPEED", node_id: "EVI_SPEED", source: "SIMULATION", source_field: "value", quality_label: "VALID", availability: 1, freshness: 1 }],
      excluded_context_fields: [{ evidence_type: "ROAD_FRICTION_STATE", node_id: "EVI_ROAD", source: "SIMULATION", source_field: "wetness", value: "DRY", reason: "NOT_RELEVANT_TO_CURRENT_DEMAND" }],
    },
  }] },
};

function renderPage(entry = "/evidence/TURN_1") {
  return render(<SessionProvider><MemoryRouter initialEntries={[entry]}><Routes><Route path="/evidence" element={<EvidencePage />} /><Route path="/evidence/:turnId" element={<EvidencePage />} /></Routes></MemoryRouter></SessionProvider>);
}

beforeEach(() => {
  window.localStorage.clear(); window.sessionStorage.clear();
  vi.mocked(getTurnPresentation).mockReset().mockResolvedValue(presentation as never);
});
afterEach(cleanup);

describe("安全知识检索页面", () => {
  it("从当前会话加载正式轮次", async () => {
    window.sessionStorage.setItem("yuzheng.v2.turn.active", "TURN_ACTIVE");
    renderPage("/evidence");
    await waitFor(() => expect(getTurnPresentation).toHaveBeenCalledWith("TURN_ACTIVE", expect.any(AbortSignal)));
    expect(await screen.findByRole("heading", { name: "安全知识检索" })).toBeTruthy();
  });

  it("只展示最终知识结果、完整查询和已进入上下文", async () => {
    renderPage();
    expect(await screen.findByText("知识检索结果")).toBeTruthy();
    expect(screen.getByText("开门前检查速度与周边目标")).toBeTruthy();
    expect(screen.queryByText("第一层：动作匹配知识")).toBeNull();
    expect(screen.queryByText("合法知识节点")).toBeNull();
    expect(screen.queryByText("向量维数")).toBeNull();
    expect(screen.queryByText("相似度阈值")).toBeNull();
    expect(screen.getByText(/意图=DOOR_OPEN/)).toBeTruthy();
    expect(screen.getAllByText("车辆速度（VEHICLE_SPEED）")).toHaveLength(2);
    expect(screen.getByText("VALID")).toBeTruthy();
    expect(screen.getByText("可用度 100.00% · 新鲜度 100.00%")).toBeTruthy();
    expect(screen.queryByLabelText("最大连接数")).toBeNull();
    expect(screen.queryByText("强制召回审计")).toBeNull();
  });

  it("点击最终结果展开业务详情", async () => {
    const user = userEvent.setup(); renderPage();
    await user.click(await screen.findByText("开门前检查速度与周边目标"));
    expect(screen.getByText("车门开启速度核查")).toBeTruthy();
    expect(screen.getByText("车辆运动")).toBeTruthy();
    expect(screen.getByText("标准")).toBeTruthy();
    expect(screen.queryByText("82.00%")).toBeNull();
  });

  it("展示未进入查询字段及中文排除原因", async () => {
    const user = userEvent.setup(); renderPage();
    await user.click(await screen.findByRole("button", { name: "未进入查询（1）" }));
    expect(screen.getByText("道路附着状态（ROAD_FRICTION_STATE）")).toBeTruthy();
    expect(screen.getByText("与当前证据需求无关")).toBeTruthy();
  });
});

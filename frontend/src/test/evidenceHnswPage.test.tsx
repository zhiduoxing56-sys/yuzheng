// @vitest-environment jsdom

import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { analyzeRecallAudit, getRecentRecallAudits } from "../api/recallAudits";
import { getIndexStatus, updateIndexParameters } from "../api/system";
import { getTurnPresentation } from "../api/turns";
import { EvidencePage } from "../pages/EvidencePage";
import { SessionProvider } from "../stores/sessionStore";

vi.mock("../api/system", () => ({ getIndexStatus: vi.fn(), updateIndexParameters: vi.fn() }));
vi.mock("../api/turns", () => ({ getTurnPresentation: vi.fn() }));
vi.mock("../api/recallAudits", () => ({ getRecentRecallAudits: vi.fn(), analyzeRecallAudit: vi.fn() }));

const status = { M: 16, ef_construction: 200, ef_search: 30, layer_count: 4, top_k: 20 };
const presentation = {
  retrieval_summary: {
    top_k: 20,
    candidate_count: 7,
    mandatory_recall_count: 1,
    elapsed_ms: 12.345,
    layers: [{
      layer: 2,
      layer_name: "第3层",
      hit_count: 1,
      nodes: [{ node_id: "EVI_1", display_name: "车辆速度", evidence_type: "VEHICLE_SPEED", sas: 0.91, rank: 1, matched_intents: ["0:DOOR_OPEN", "1:WINDOW_OPEN"] }],
    }],
  },
};

function renderPage(entry = "/evidence/TURN_1") {
  return render(<SessionProvider><MemoryRouter initialEntries={[entry]}><Routes><Route path="/evidence" element={<EvidencePage />} /><Route path="/evidence/:turnId" element={<EvidencePage />} /></Routes></MemoryRouter></SessionProvider>);
}

beforeEach(() => {
  window.localStorage.clear();
  window.sessionStorage.clear();
  vi.mocked(getIndexStatus).mockReset().mockResolvedValue(status);
  vi.mocked(updateIndexParameters).mockReset().mockResolvedValue({ ...status, M: 12 });
  vi.mocked(getTurnPresentation).mockReset().mockResolvedValue(presentation as never);
  vi.mocked(getRecentRecallAudits).mockReset().mockResolvedValue({ items: [{ turn_id: "TURN_1", created_at: "2026-08-12T00:00:00Z", instruction: "打开车门", mandatory_recall_evidence: [{ evidence_type: "GEAR_STATE", node_id: "EVI_GEAR", display_name: "挡位状态" }], ai_audit_available: false }] });
  vi.mocked(analyzeRecallAudit).mockReset().mockResolvedValue({ turn_id: "TURN_1", attention_required: false, audit_comment: "证据充分", potential_missing_evidence: [], cached: false, status: "SUCCEEDED" });
});
afterEach(cleanup);

describe("HNSW frontend formal contract", () => {
  it("loads the active turn when entering the parameterless evidence navigation", async () => {
    window.localStorage.setItem("yuzheng.v2.turn.active", "TURN_ACTIVE");
    renderPage("/evidence");
    await waitFor(() => expect(getTurnPresentation).toHaveBeenCalledWith("TURN_ACTIVE", expect.any(AbortSignal)));
    expect(await screen.findByText("命中 1 个")).toBeTruthy();
  });

  it("accepts the existing turn_id query navigation and loads that turn", async () => {
    renderPage("/evidence?turn_id=TURN_QUERY");
    await waitFor(() => expect(getTurnPresentation).toHaveBeenCalledWith("TURN_QUERY", expect.any(AbortSignal)));
    expect(await screen.findByText("命中 1 个")).toBeTruthy();
  });

  it("renders backend parameters, one row per layer, and real node details", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect((screen.getByLabelText("M") as HTMLInputElement).value).toBe("16"));
    expect(screen.getByText("命中 1 个")).toBeTruthy();
    expect(screen.getByText("强制补召数量:").parentElement?.textContent).toContain("1");
    await user.click(screen.getByRole("listitem"));
    const dialog = screen.getByRole("dialog", { name: "第3层节点详情" });
    expect(within(dialog).getByText("车辆速度")).toBeTruthy();
    expect(within(dialog).getByText("0:DOOR_OPEN、1:WINDOW_OPEN")).toBeTruthy();
  });

  it("sends the four formal parameters and uses the returned status", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect((screen.getByLabelText("M") as HTMLInputElement).value).toBe("16"));
    const m = screen.getByLabelText("M");
    await user.clear(m);
    await user.type(m, "12");
    await user.click(screen.getByRole("button", { name: "应用参数" }));
    await waitFor(() => expect(updateIndexParameters).toHaveBeenCalledWith({ M: 12, ef_construction: 200, ef_search: 30, layer_count: 4 }));
    expect(screen.getByText("参数已原子生效，将影响下一条指令")).toBeTruthy();
  });

  it("renders actual mandatory recall and runs AI only after clicking view", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect(screen.getByText("挡位状态")).toBeTruthy());
    expect(analyzeRecallAudit).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "查看" }));
    await waitFor(() => expect(analyzeRecallAudit).toHaveBeenCalledWith("TURN_1"));
    expect(screen.getByRole("dialog", { name: "DeepSeek AI审计" })).toBeTruthy();
    expect(screen.getByText("证据充分")).toBeTruthy();
  });
});

// @vitest-environment jsdom

import { StrictMode } from "react";
import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { listAuditRecords } from "../api/auditRecords";
import { AuditsPage } from "../pages/AuditsPage";

vi.mock("../api/auditRecords", () => ({ listAuditRecords: vi.fn() }));

const semanticFrame = {
  frame_id: "SEM-1",
  turn_id: "TURN-1",
  raw_text: "打开左前车窗，然后打开右后车窗",
  normalized_text: "打开左前车窗，然后打开右后车窗",
  semantic_confidence: 0.91,
  ambiguity_score: 0.09,
  semantic_status: "REVIEW",
  review_reasons: ["MULTI_INTENT"],
  review_candidates: [],
  unresolved_clauses: ["然后"],
  security_signals: ["MULTI_INTENT"],
  intents: [
    {
      clause_index: 0,
      clause_text: "打开左前车窗",
      intent_id: "WINDOW_OPEN",
      action: "OPEN",
      target: "WINDOW",
      area: "FRONT_LEFT",
      value: { percent: 50 },
      control_domain: "BODY",
      risk_level: "R1",
      risk_tags: ["BODY_CONTROL"],
      semantic_confidence: 0.94,
      ambiguity_score: 0.06,
    },
    {
      clause_index: 1,
      clause_text: "打开右后车窗",
      intent_id: "WINDOW_OPEN",
      action: "OPEN",
      target: "WINDOW",
      area: "REAR_RIGHT",
      value: true,
      control_domain: "BODY",
      risk_level: "R1",
      risk_tags: ["BODY_CONTROL"],
      semantic_confidence: 0.88,
      ambiguity_score: 0.12,
    },
  ],
};

function response(items: unknown[] = [{
  audit_id: "AUDIT-1",
  turn_id: "TURN-1",
  created_at: "2026-08-12T08:30:00Z",
  semantic_frame: semanticFrame,
}]): unknown {
  return { items, total: items.length, page: 1, page_size: 20 };
}

beforeEach(() => vi.mocked(listAuditRecords).mockReset());
afterEach(cleanup);

describe("AuditsPage formal audit data integration", () => {
  it("completes the formal-list read under React strict mode", async () => {
    vi.mocked(listAuditRecords).mockResolvedValue(response());
    render(<StrictMode><AuditsPage /></StrictMode>);

    await waitFor(() => expect(screen.getByText(semanticFrame.raw_text)).toBeTruthy());
    expect((screen.getByRole("button", { name: "刷新审计记录" }) as HTMLButtonElement).disabled).toBe(false);
  });

  it("uses the list response once, keeps duplicate intent occurrences in order, and never shows a decision", async () => {
    vi.mocked(listAuditRecords).mockResolvedValue(response());
    const user = userEvent.setup();
    render(<AuditsPage />);

    await waitFor(() => expect(listAuditRecords).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.getByText(semanticFrame.raw_text)).toBeTruthy());
    expect(screen.getByText("--")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "查看详情" }));

    const dialog = screen.getByRole("dialog", { name: "语义帧详细结果" });
    const cards = dialog.querySelectorAll(".semantic-intent-card");
    expect(cards).toHaveLength(2);
    expect(within(cards[0] as HTMLElement).getByText("FRONT_LEFT")).toBeTruthy();
    expect(within(cards[1] as HTMLElement).getByText("REAR_RIGHT")).toBeTruthy();
    expect(within(dialog).getAllByText("WINDOW_OPEN")).toHaveLength(2);
    expect(within(dialog).getByText('{"percent":50}')).toBeTruthy();
    expect(within(dialog).getByText("true")).toBeTruthy();
    expect(within(dialog).getByText("REVIEW")).toBeTruthy();
    expect(listAuditRecords).toHaveBeenCalledTimes(1);
  });

  it("keeps the empty-table state when the formal response has no items", async () => {
    vi.mocked(listAuditRecords).mockResolvedValue(response([]));
    render(<AuditsPage />);

    await waitFor(() => expect(screen.getByText("暂无审计记录")).toBeTruthy());
    expect(document.querySelectorAll(".audit-record-table tbody tr")).toHaveLength(0);
  });

  it("renders a single-intent record from its raw semantic-frame text", async () => {
    const singleIntentFrame = {
      ...semanticFrame,
      raw_text: "打开左前车窗",
      intents: [semanticFrame.intents[0]],
    };
    vi.mocked(listAuditRecords).mockResolvedValue(response([{
      audit_id: "AUDIT-SINGLE",
      turn_id: "TURN-SINGLE",
      created_at: "2026-08-12T08:30:00Z",
      semantic_frame: singleIntentFrame,
    }]));
    const user = userEvent.setup();
    render(<AuditsPage />);

    await waitFor(() => expect(screen.getByText(singleIntentFrame.raw_text)).toBeTruthy());
    await user.click(screen.getByRole("button", { name: "查看详情" }));
    expect(document.querySelectorAll(".semantic-intent-card")).toHaveLength(1);
  });

  it("shows an initial-load failure without mock records", async () => {
    vi.mocked(listAuditRecords).mockResolvedValue({ invalid: true });
    render(<AuditsPage />);

    await waitFor(() => expect(screen.getByRole("alert").textContent).toContain("审计记录加载失败"));
    expect(document.querySelectorAll(".audit-record-table tbody tr")).toHaveLength(0);
  });

  it("retains the prior successful list on refresh failure", async () => {
    vi.mocked(listAuditRecords)
      .mockResolvedValueOnce(response())
      .mockRejectedValueOnce(new Error("refresh network unavailable"));
    const user = userEvent.setup();
    render(<AuditsPage />);

    await waitFor(() => expect(screen.getByText(semanticFrame.raw_text)).toBeTruthy());
    await user.click(screen.getByRole("button", { name: "刷新审计记录" }));
    await waitFor(() => expect(screen.getByRole("alert").textContent).toContain("刷新失败"));
    expect(screen.getByText(semanticFrame.raw_text)).toBeTruthy();
  });

  it("disables repeated rapid refreshes while one request is in flight", async () => {
    let resolveRefresh: ((payload: unknown) => void) | undefined;
    vi.mocked(listAuditRecords)
      .mockResolvedValueOnce(response())
      .mockImplementationOnce(() => new Promise((resolve) => { resolveRefresh = resolve; }));
    const user = userEvent.setup();
    render(<AuditsPage />);

    await waitFor(() => expect(screen.getByText(semanticFrame.raw_text)).toBeTruthy());
    const refresh = screen.getByRole("button", { name: "刷新审计记录" });
    await user.click(refresh);
    await user.click(refresh);
    expect(listAuditRecords).toHaveBeenCalledTimes(2);
    expect((refresh as HTMLButtonElement).disabled).toBe(true);

    resolveRefresh?.(response([{
      audit_id: "AUDIT-REFRESHED",
      turn_id: "TURN-REFRESHED",
      created_at: "2026-08-12T09:00:00Z",
      semantic_frame: { ...semanticFrame, raw_text: "关闭左前车窗" },
    }]));
    await waitFor(() => expect((screen.getByRole("button", { name: "刷新审计记录" }) as HTMLButtonElement).disabled).toBe(false));
    expect(screen.getByText("关闭左前车窗")).toBeTruthy();
    expect(screen.queryByText(semanticFrame.raw_text)).toBeNull();
  });

  it("aborts the active formal-list request when the page unmounts", async () => {
    let signal: AbortSignal | undefined;
    vi.mocked(listAuditRecords).mockImplementationOnce((requestSignal) => {
      signal = requestSignal;
      return new Promise(() => undefined);
    });
    const rendered = render(<AuditsPage />);

    await waitFor(() => expect(listAuditRecords).toHaveBeenCalledTimes(1));
    rendered.unmount();
    expect(signal?.aborted).toBe(true);
  });
});

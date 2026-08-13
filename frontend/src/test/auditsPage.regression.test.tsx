// @vitest-environment jsdom

import { StrictMode } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { listAuditRecords } from "../api/auditRecords";
import { useAuditDetail } from "../hooks/useAuditDetail";
import { AuditsPage } from "../pages/AuditsPage";

vi.mock("../api/auditRecords", () => ({ listAuditRecords: vi.fn() }));
vi.mock("../hooks/useAuditDetail", () => ({ useAuditDetail: vi.fn() }));

function response(items: unknown[] = [{
  audit_id: "AUDIT-1",
  created_at: "2026-08-12T08:30:00Z",
  raw_command: "关闭前照灯",
  final_decision: "BLOCK",
  execution_status: "NOT_EXECUTED",
  review_occurred: false,
}]): unknown {
  return { items, total: items.length, page: 1, page_size: 20 };
}

function mount(strict = false) {
  const app = <MemoryRouter initialEntries={["/audits"]}><Routes><Route path="/audits" element={<AuditsPage />} /><Route path="/audits/:auditId" element={<p>详情已打开</p>} /></Routes></MemoryRouter>;
  return render(strict ? <StrictMode>{app}</StrictMode> : app);
}

beforeEach(() => {
  vi.mocked(listAuditRecords).mockReset();
  vi.mocked(useAuditDetail).mockReturnValue({ data: null, loading: true, error: null, refresh: vi.fn() });
});
afterEach(cleanup);

describe("human-readable audit list", () => {
  it("renders only the final list fields", async () => {
    vi.mocked(listAuditRecords).mockResolvedValue(response());
    mount(true);
    await waitFor(() => expect(screen.getByText("关闭前照灯")).toBeTruthy());
    expect(screen.getByText("BLOCK")).toBeTruthy();
    expect(screen.getByText("NOT_EXECUTED")).toBeTruthy();
    expect(screen.getByText("否")).toBeTruthy();
    expect(screen.queryByText("frame_id")).toBeNull();
    expect(screen.queryByText("intent_id")).toBeNull();
  });

  it("opens Audit Detail in the current page dialog", async () => {
    vi.mocked(listAuditRecords).mockResolvedValue(response());
    const user = userEvent.setup();
    mount();
    await user.click(await screen.findByRole("button", { name: "查看详情" }));
    expect(screen.getByRole("dialog", { name: "人类可读安全审计" })).toBeTruthy();
    expect(screen.getByText("审计编号：AUDIT-1")).toBeTruthy();
    expect(screen.queryByText("详情已打开")).toBeNull();
    await user.click(screen.getByRole("button", { name: "关闭" }));
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("keeps the empty state", async () => {
    vi.mocked(listAuditRecords).mockResolvedValue(response([]));
    mount();
    expect(await screen.findByText("暂无审计记录")).toBeTruthy();
  });

  it("reports invalid responses without mock rows", async () => {
    vi.mocked(listAuditRecords).mockResolvedValue({ invalid: true });
    mount();
    await waitFor(() => expect(screen.getByRole("alert").textContent).toContain("审计记录加载失败"));
  });

  it("aborts the active request when unmounted", async () => {
    let signal: AbortSignal | undefined;
    vi.mocked(listAuditRecords).mockImplementationOnce((requestSignal) => {
      signal = requestSignal;
      return new Promise(() => undefined);
    });
    const rendered = mount();
    await waitFor(() => expect(listAuditRecords).toHaveBeenCalledTimes(1));
    rendered.unmount();
    expect(signal?.aborted).toBe(true);
  });
});

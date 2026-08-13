// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ClarificationModal } from "../components/ClarificationModal";
import type { ClarificationRequest } from "../types/contract";

const request: ClarificationRequest = {
  clarification_id: "CLA_1",
  turn_id: "TURN_A",
  clarification_type: "VOICE_CONFIRMATION",
  prompt: "您是否说：",
  original_text: "运动莫斯",
  candidates: Array.from({ length: 5 }, (_, index) => ({
    candidate_id: `CAND_${index + 1}`,
    display_text: `候选 ${index + 1}`,
    candidate_source: "ASR_NBEST",
    source_rank: index + 1,
    confidence: 0.9 - index * 0.1,
    group: null,
    group_label: null,
  })),
};

afterEach(cleanup);

describe("ClarificationModal", () => {
  it("自动展示最多四个候选且固定提供都不是", () => {
    render(<ClarificationModal request={request} submitting={false} error={null} onSelect={vi.fn()} onNoneOfAbove={vi.fn()} />);
    expect(screen.getByRole("dialog", { name: "需要确认" })).not.toBeNull();
    expect(screen.getAllByRole("button")).toHaveLength(5);
    expect(screen.queryByText("候选 5")).toBeNull();
    expect(screen.getByRole("button", { name: "都不是，再说一次" })).not.toBeNull();
  });

  it("点击候选只回传 candidate id", async () => {
    const onSelect = vi.fn();
    render(<ClarificationModal request={request} submitting={false} error={null} onSelect={onSelect} onNoneOfAbove={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: "候选 2" }));
    expect(onSelect).toHaveBeenCalledWith("CAND_2");
  });

  it("点击遮罩空白视为都不是，点击弹窗内容不误触", () => {
    const onNone = vi.fn();
    render(<ClarificationModal request={request} submitting={false} error={null} onSelect={vi.fn()} onNoneOfAbove={onNone} />);
    fireEvent.mouseDown(screen.getByRole("dialog"));
    expect(onNone).not.toHaveBeenCalled();
    fireEvent.mouseDown(screen.getByTestId("clarification-backdrop"));
    expect(onNone).toHaveBeenCalledTimes(1);
  });

  it("零候选时不补位并提示重新输入", () => {
    render(<ClarificationModal request={{ ...request, candidates: [] }} submitting={false} error={null} onSelect={vi.fn()} onNoneOfAbove={vi.fn()} />);
    expect(screen.getByText("暂未找到可靠候选，请重新说一次")).not.toBeNull();
    expect(screen.getAllByRole("button")).toHaveLength(1);
  });

  it("提交期间仅禁用弹窗按钮且遮罩不重复提交", () => {
    const onNone = vi.fn();
    render(<ClarificationModal request={request} submitting error={null} onSelect={vi.fn()} onNoneOfAbove={onNone} />);
    for (const button of screen.getAllByRole("button")) expect((button as HTMLButtonElement).disabled).toBe(true);
    fireEvent.mouseDown(screen.getByTestId("clarification-backdrop"));
    expect(onNone).not.toHaveBeenCalled();
  });
});

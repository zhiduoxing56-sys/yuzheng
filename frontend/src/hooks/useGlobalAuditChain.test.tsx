// @vitest-environment jsdom

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { verifyGlobalAuditChain } from "../api/audits";
import { useGlobalAuditChain } from "./useGlobalAuditChain";

vi.mock("../api/audits", () => ({ verifyGlobalAuditChain: vi.fn() }));

function Probe() {
  const chain = useGlobalAuditChain();
  return <><button onClick={chain.refresh}>验证</button><output>{chain.data?.state || "empty"}</output><time>{chain.verifiedAt ? "verified" : "unverified"}</time></>;
}

describe("useGlobalAuditChain", () => {
  it("keeps a manually verified result after the audit page remounts", async () => {
    vi.mocked(verifyGlobalAuditChain).mockResolvedValue({
      valid: true, total_records: 2, legacy_unsigned_records: 2,
      signature_protected_records: 0, signature_verified_records: 0,
      hash_chain_status: "VALID", signature_status: "NOT_ENABLED",
    });
    const user = userEvent.setup();
    const first = render(<Probe />);
    await user.click(screen.getByRole("button", { name: "验证" }));
    await waitFor(() => expect(screen.getByText("valid")).toBeTruthy());
    expect(screen.getByText("verified")).toBeTruthy();
    first.unmount();

    render(<Probe />);
    expect(screen.getByText("valid")).toBeTruthy();
    expect(screen.getByText("verified")).toBeTruthy();
    expect(verifyGlobalAuditChain).toHaveBeenCalledTimes(1);
  });
});

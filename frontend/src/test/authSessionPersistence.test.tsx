// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it } from "vitest";
import { AuthProvider, useAuth } from "../stores/authStore";

function AuthControls() {
  const { authenticated, login, logout } = useAuth();
  return <><output>{authenticated ? "已登录" : "未登录"}</output><button onClick={login}>登录</button><button onClick={logout}>退出</button></>;
}

beforeEach(() => window.sessionStorage.clear());
afterEach(cleanup);

it("restores the login state for the current browser session", () => {
  window.sessionStorage.setItem("yuzheng.v2.authenticated", "true");
  render(<AuthProvider><AuthControls /></AuthProvider>);
  expect(screen.getByText("已登录")).toBeTruthy();
});

it("writes on login and clears only when the user logs out", () => {
  render(<AuthProvider><AuthControls /></AuthProvider>);
  fireEvent.click(screen.getByRole("button", { name: "登录" }));
  expect(window.sessionStorage.getItem("yuzheng.v2.authenticated")).toBe("true");
  expect(screen.getByText("已登录")).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "退出" }));
  expect(window.sessionStorage.getItem("yuzheng.v2.authenticated")).toBeNull();
  expect(screen.getByText("未登录")).toBeTruthy();
});

import { useState, type FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../stores/authStore";

export function LoginPage() {
  const [account, setAccount] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const destination = (location.state as { from?: string } | null)?.from || "/decision";

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!account.trim() || !password.trim()) { setError("请输入账号和密码"); return; }
    setError("");
    setSubmitting(true);
    window.setTimeout(() => { login(); navigate(destination, { replace: true }); }, 260);
  }

  return <main className="login-page">
    <div className="login-orbit login-orbit-one" aria-hidden="true" />
    <div className="login-orbit login-orbit-two" aria-hidden="true" />
    <section className="login-layout" aria-label="语证系统登录">
      <div className="login-intro">
        <div className="login-brand">语证</div>
        <h1>面向高风险车控指令的<br />证据对齐与可解释裁决系统</h1>
      </div>
      <form className="login-card" onSubmit={handleSubmit}>
        <div className="login-card-heading"><h2>登录语证</h2></div>
        <label>账号<input value={account} onChange={(event) => setAccount(event.target.value)} autoComplete="username" placeholder="请输入账号" autoFocus /></label>
        <label>密码<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" placeholder="请输入密码" /></label>
        {error && <p className="login-error" role="alert">{error}</p>}
        <button className="login-submit" type="submit" disabled={submitting}>{submitting ? "正在进入系统…" : "进入系统"}<span aria-hidden="true">→</span></button>
      </form>
    </section>
  </main>;
}

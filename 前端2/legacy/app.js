const API = window.__YUZHENG_API__ || "http://127.0.0.1:8000";
const $ = (id) => document.getElementById(id);
let currentTurnId = null;
let currentPresentation = null;

function text(value, fallback = "—") {
  return value === null || value === undefined || value === "" ? fallback : String(value);
}

function pct(value) {
  return value === null || value === undefined ? "—" : `${(Number(value) * 100).toFixed(0)}%`;
}

function setHealth(ok, label) {
  $("health").innerHTML = `<span class="dot" style="color:${ok ? "var(--green)" : "var(--red)"}"></span>${label}`;
}

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, { headers: { "Content-Type": "application/json", ...(options.headers || {}) }, ...options });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.message || body.detail || `请求失败 (${response.status})`);
  return body;
}

function renderStages(stage = "semantic") {
  const stages = ["semantic", "retrieval", "evidence", "decision", "review"];
  const active = Math.max(0, stages.indexOf(stage));
  document.querySelectorAll(".stage").forEach((item, index) => item.classList.toggle("active", index <= active));
}

function renderRetrieval(summary = {}) {
  const layers = Array.isArray(summary.security_layers) ? summary.security_layers : [];
  const layerCounts = summary.per_layer_node_count || {};
  $("layer-count").textContent = text(summary.security_layer_count, layers.length || 0);
  $("candidate-count").textContent = text(summary.candidate_count, 0);
  $("elapsed").textContent = summary.elapsed_ms == null ? "—" : `${Number(summary.elapsed_ms).toFixed(1)} ms`;
  $("index").textContent = text(summary.index_implementation, "—").replace("exact_cosine_fallback", "exact cosine");
  $("retrieval-state").textContent = text(summary.availability, "AVAILABLE");
  const container = $("layers");
  if (!layers.length) { container.className = "layers empty-state"; container.innerHTML = "<p>本轮未记录分层导航。</p>"; return; }
  container.className = "layers";
  container.innerHTML = layers.map((layer, index) => {
    const rank = layer.layer ?? layer.rank ?? index;
    const count = layerCounts[rank] ?? layer.node_count ?? 0;
    const status = layer.implementation || layer.status || "READY";
    return `<div class="layer"><span class="layer-name">第 ${rank} 层</span><span class="layer-count">${count} 个节点 · ${text(status)}</span><span class="layer-bar" style="opacity:${Math.max(.3, Math.min(1, Number(count) / 12 || .3))}"></span></div>`;
  }).join("");
  $("trace-note").textContent = summary.internal_hnsw_trace_available ? "已提供内部路径。" : `后端说明：${text(summary.internal_hnsw_trace_reason, "公共 hnswlib API 不提供内部 visited trace")}`;
}

function renderEvidence(presentation = {}) {
  const evidence = presentation.evidence || {};
  const nodes = evidence.evidence_subgraph?.nodes || presentation.evidence?.nodes || [];
  $("evidence-count").textContent = String(nodes.length);
  const container = $("evidence");
  if (!nodes.length) { container.className = "evidence-list empty-state"; container.innerHTML = "<p>本轮没有可展示证据节点。</p>"; return; }
  container.className = "evidence-list";
  container.innerHTML = nodes.slice(0, 12).map((node) => `<div class="evidence-item"><strong>${text(node.evidence_type || node.type, "evidence")}</strong><span>${text(node.value || node.summary || node.node_id)}</span><span>${text(node.quality_label || node.status, "—")}</span></div>`).join("");
}

function renderDecision(presentation = {}) {
  const result = presentation.decision_result || presentation.decision || {};
  const decision = String(result.final_decision || result.decision || "").toUpperCase();
  const score = result.safety_score ?? result.score;
  const quality = presentation.evidence?.quality_metrics || presentation.quality_metrics || {};
  const box = $("decision");
  const klass = decision.toLowerCase();
  box.className = `decision ${klass}`;
  box.innerHTML = `<strong>${text(decision, "等待")}</strong><small>${text(result.decision_explanation || result.explanation || result.reasons?.[0], "后端尚未返回解释")}</small>`;
  $("score").textContent = score == null ? "—" : Number(score).toFixed(2);
  $("coverage").textContent = pct(quality.ecr ?? quality.evidence_coverage ?? result.evidence_coverage);
  const interpreter = presentation.gate_result?.interpreter_result || result.interpreter_result || presentation.interpreter_result;
  $("interpreter").textContent = interpreter ? `${text(interpreter.generation_metadata?.generation_mode, "解释器")} · ${text(interpreter.summary || interpreter.explanation, "已完成本地裁决")}` : "本地确定性裁决已完成，外部解释器状态未记录。";
}

function renderReview(presentation = {}) {
  const review = presentation.review || {};
  const box = $("review");
  if (!review.review_required && !review.status && !review.review_question) { box.className = "review-content empty-state"; box.innerHTML = "<p>当前轮次无需人工复核。</p>"; return; }
  box.className = "review-content";
  const candidates = review.candidate_interpretations || [];
  const candidate = candidates[0];
  box.innerHTML = `<p class="review-question">${text(review.review_question, "请确认或修正当前指令")}</p><div class="review-actions">${candidate ? `<button data-review="CONFIRM" data-candidate="${candidate.candidate_id}">确认候选</button>` : ""}<input id="corrected" maxlength="2048" placeholder="输入修正后的指令" /><button data-review="CORRECT">纠正并重跑</button><button class="danger" data-review="CANCEL">取消</button></div>`;
  box.querySelectorAll("button[data-review]").forEach((button) => button.addEventListener("click", () => submitReview(button.dataset.review, button.dataset.candidate)));
}

async function loadPresentation(turnId) {
  currentTurnId = turnId;
  currentPresentation = await request(`/api/turns/${encodeURIComponent(turnId)}/presentation`);
  renderStages(currentPresentation.current_stage || "decision");
  renderRetrieval(currentPresentation.retrieval_summary || {});
  renderEvidence(currentPresentation);
  renderDecision(currentPresentation);
  renderReview(currentPresentation);
  $("turn-id").textContent = turnId;
  $("audit-status").textContent = `处理状态：${text(currentPresentation.processing_status, "COMPLETED")} · 当前阶段：${text(currentPresentation.current_stage, "decision")}`;
}

async function sendCommand() {
  const button = $("send");
  const value = $("command").value.trim();
  if (!value) return;
  button.disabled = true;
  $("error").hidden = true;
  $("retrieval-state").textContent = "处理中";
  renderStages("semantic");
  try {
    const result = await request("/api/command/text", { method: "POST", body: JSON.stringify({ text: value, speaker_zone: "driver", speaker_role: "driver", session_id: "frontend-v1" }) });
    await loadPresentation(result.turn_id);
    setHealth(true, "服务正常");
  } catch (error) {
    $("error").textContent = error.message;
    $("error").hidden = false;
    setHealth(false, "服务异常");
  } finally { button.disabled = false; }
}

async function submitReview(action, candidateId) {
  if (!currentTurnId) return;
  const body = { action };
  if (action === "CONFIRM") body.selected_candidate_id = candidateId;
  if (action === "CORRECT") body.corrected_text = $("corrected").value.trim();
  try {
    const result = await request(`/api/turns/${encodeURIComponent(currentTurnId)}/review`, { method: "POST", body: JSON.stringify(body) });
    await loadPresentation(result.review_turn_id || result.related_turn_id || currentTurnId);
  } catch (error) { $("error").textContent = error.message; $("error").hidden = false; }
}

async function checkHealth() {
  try { const result = await request("/api/health"); setHealth(result.status === "ok" || result.status === "healthy", `服务 ${text(result.stage, "就绪")}`); }
  catch { setHealth(false, "后端未连接"); }
}

$("send").addEventListener("click", sendCommand);
$("command").addEventListener("keydown", (event) => { if ((event.ctrlKey || event.metaKey) && event.key === "Enter") sendCommand(); });
checkHealth();

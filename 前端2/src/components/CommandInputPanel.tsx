import { useEffect, useState } from "react";
import { MAX_AUDIO_FILE_SIZE_LABEL, SPEAKER_ZONES, SUBMISSION_STATUS_LABELS } from "../constants";
import type { SubmissionStatus } from "../types/contract";
import type { AudioSubmissionInput, MicrophoneSubmissionInput, TextSubmissionInput } from "../hooks/useCommandSubmission";
import { loadCommandDraft, saveCommandDraft } from "../utils/commandSessionStorage";

type InputTab = "text" | "audio" | "microphone";

interface Props {
  sessionId: string;
  status: SubmissionStatus;
  busy: boolean;
  error: string | null;
  draftResetVersion?: string | null;
  onSubmitText: (input: TextSubmissionInput) => Promise<void>;
  onSubmitAudio: (input: AudioSubmissionInput) => Promise<void>;
  onSubmitMicrophone: (input: MicrophoneSubmissionInput) => Promise<void>;
}

export function CommandInputPanel({ sessionId, status, busy, error, draftResetVersion, onSubmitText, onSubmitAudio, onSubmitMicrophone }: Props) {
  const storedDraft = loadCommandDraft(sessionId);
  const [tab, setTab] = useState<InputTab>("text");
  const [speakerZone, setSpeakerZone] = useState(storedDraft?.speakerZone || "driver");
  const [speakerRole, setSpeakerRole] = useState(storedDraft?.speakerRole || "driver");
  const [text, setText] = useState(storedDraft?.text || "");
  const [stateOverridesJson, setStateOverridesJson] = useState("");
  const [evidenceOverridesJson, setEvidenceOverridesJson] = useState("");
  const [microphoneStateOverridesJson, setMicrophoneStateOverridesJson] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [audioSource, setAudioSource] = useState("browser_upload");
  const [arrayChannel, setArrayChannel] = useState("");
  const [channelIndex, setChannelIndex] = useState("");
  const [durationSeconds, setDurationSeconds] = useState(4);
  const [device, setDevice] = useState("");

  useEffect(() => {
    const restored = loadCommandDraft(sessionId);
    setText(restored?.text || "");
    setSpeakerZone(restored?.speakerZone || "driver");
    setSpeakerRole(restored?.speakerRole || "driver");
  }, [sessionId]);

  useEffect(() => {
    saveCommandDraft(sessionId, { text, speakerZone, speakerRole });
  }, [sessionId, text, speakerZone, speakerRole]);

  useEffect(() => {
    if (!draftResetVersion) return;
    setText("");
    setFile(null);
  }, [draftResetVersion]);

  const common = { speakerZone, speakerRole };
  return (
    <section className="decision-card command-input-panel" aria-labelledby="command-input-title">
      <div className="card-heading">
        <div><span className="eyebrow">COMMAND</span><h2 id="command-input-title">指令输入</h2></div>
        <span className={`submission-status submission-${status}`}>{SUBMISSION_STATUS_LABELS[status]}</span>
      </div>

      <div className="input-tabs" role="tablist" aria-label="指令输入方式">
        {(["text", "audio", "microphone"] as const).map((value) => (
          <button key={value} type="button" role="tab" aria-selected={tab === value} className={tab === value ? "active" : ""} onClick={() => setTab(value)} disabled={busy}>
            {value === "text" ? "文本指令" : value === "audio" ? "音频上传" : "麦克风采集"}
          </button>
        ))}
      </div>

      <div className="form-grid two-columns">
        <label>发声位置<select value={speakerZone} onChange={(event) => setSpeakerZone(event.target.value)} disabled={busy}>{SPEAKER_ZONES.map((zone) => <option key={zone} value={zone}>{zone}</option>)}</select></label>
        <label>说话人角色<input value={speakerRole} onChange={(event) => setSpeakerRole(event.target.value)} list="speaker-role-options" disabled={busy} /><datalist id="speaker-role-options"><option value="driver" /><option value="passenger" /><option value="unknown" /></datalist></label>
      </div>

      {tab === "text" && (
        <form onSubmit={(event) => { event.preventDefault(); void onSubmitText({ ...common, text, stateOverridesJson, evidenceOverridesJson }); }}>
          <label>指令文本<textarea className="command-textarea" value={text} maxLength={2048} onChange={(event) => setText(event.target.value)} placeholder="例如：打开车门" disabled={busy} /></label>
          <details className="advanced-inputs"><summary>高级测试参数</summary>
            <label>state_overrides（JSON 对象）<textarea value={stateOverridesJson} onChange={(event) => setStateOverridesJson(event.target.value)} placeholder={'{"vehicle_speed": 0, "gear_position": "P"}'} disabled={busy} /></label>
            <label>evidence_overrides（JSON 对象数组）<textarea value={evidenceOverridesJson} onChange={(event) => setEvidenceOverridesJson(event.target.value)} placeholder={'[{"evidence_type":"vehicle_speed","source":"test","value":0}]'} disabled={busy} /></label>
          </details>
          <button className="primary-button full-width" type="submit" disabled={busy || !text.trim()}>提交文本指令</button>
        </form>
      )}

      {tab === "audio" && (
        <form onSubmit={(event) => { event.preventDefault(); void onSubmitAudio({ ...common, file, audioSource, arrayChannel, channelIndex }); }}>
          <label className="file-picker">选择音频文件<input type="file" accept=".wav,.mp3,.m4a,.flac,.ogg,audio/*" onChange={(event) => setFile(event.target.files?.[0] || null)} disabled={busy} /></label>
          <div className="file-summary">{file ? <><strong>{file.name}</strong><span>{(file.size / 1024 / 1024).toFixed(2)} MiB</span></> : <span>尚未选择文件，最大 {MAX_AUDIO_FILE_SIZE_LABEL}</span>}</div>
          <div className="form-grid two-columns"><label>音频来源<input value={audioSource} onChange={(event) => setAudioSource(event.target.value)} disabled={busy} /></label><span /></div>
          <details className="advanced-inputs"><summary>高级音频参数</summary><div className="form-grid two-columns">
            <label>array_channel<input value={arrayChannel} onChange={(event) => setArrayChannel(event.target.value)} disabled={busy} /></label>
            <label>channel_index<input type="number" min="0" step="1" value={channelIndex} onChange={(event) => setChannelIndex(event.target.value)} disabled={busy} /></label>
          </div></details>
          <button className="primary-button full-width" type="submit" disabled={busy || !file}>{busy ? "上传并处理中" : "上传音频指令"}</button>
        </form>
      )}

      {tab === "microphone" && (
        <form onSubmit={(event) => { event.preventDefault(); void onSubmitMicrophone({ ...common, durationSeconds, device, stateOverridesJson: microphoneStateOverridesJson }); }}>
          <div className="notice-box">该操作将调用运行后端服务的电脑上的麦克风设备，不是浏览器当前设备的麦克风。</div>
          <div className="form-grid two-columns">
            <label>采集时长（秒）<input type="number" min="0.5" max="15" step="0.5" value={durationSeconds} onChange={(event) => setDurationSeconds(Number(event.target.value))} disabled={busy} /></label>
            <label>设备编号或名称（可空）<input value={device} onChange={(event) => setDevice(event.target.value)} disabled={busy} /></label>
          </div>
          <details className="advanced-inputs"><summary>麦克风状态覆盖</summary><label>state_overrides（JSON 对象）<textarea value={microphoneStateOverridesJson} onChange={(event) => setMicrophoneStateOverridesJson(event.target.value)} disabled={busy} /></label></details>
          <button className="primary-button full-width" type="submit" disabled={busy}>{busy ? `后端采集中（最长 ${durationSeconds} 秒）` : "调用后端麦克风"}</button>
        </form>
      )}

      {error && <p className="inline-error" role="alert">{error}</p>}
      <small className="session-hint" title={sessionId}>会话：{sessionId}</small>
    </section>
  );
}

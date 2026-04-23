// Pipeline observer — connects to /api/runs/{id}/events via SSE and
// reflects events into the UI: stage cards, live log, artifact tabs.

const STAGES = [
  "searcher", "analyst", "writer",
  "scripter", "narrator", "designer", "builder", "renderer",
];

const ARTIFACT_DEFS = [
  { key: "report",     file: "report.md",     label: "report.md",     lang: "markdown" },
  { key: "script",     file: "script.txt",    label: "script.txt",    lang: "plaintext" },
  { key: "design",     file: "DESIGN.md",     label: "DESIGN.md",     lang: "markdown" },
  { key: "html",       file: "index.html",    label: "index.html",    lang: "xml" },
  { key: "transcript", file: "transcript.json", label: "transcript.json", lang: "json" },
  { key: "video",      file: "video",         label: "video (mp4)",   lang: "video" },
];

const state = {
  runId: null,
  topic: null,
  startedAt: null,
  elapsedTimer: null,
  stages: {},
  sse: null,
  artifactsEnabled: new Set(),
  activeTab: null,
};

function fmtTime(ts) {
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString([], { hour12: false });
}

function secs(a, b) {
  if (a == null || b == null) return "";
  const dt = Math.max(0, b - a);
  if (dt < 60) return `${dt.toFixed(1)}s`;
  return `${Math.floor(dt / 60)}m${Math.floor(dt % 60)}s`;
}

// --- stage cards ---

function buildStageStrip() {
  const root = document.getElementById("stages");
  root.innerHTML = "";
  for (const s of STAGES) {
    const card = document.createElement("div");
    card.className = "stage-card";
    card.id = `stage-${s}`;
    card.innerHTML = `
      <div class="stage-head">
        <span class="stage-name">${s}</span>
        <span class="dot"></span>
      </div>
      <div class="stage-sub" data-role="sub">idle</div>
      <div class="stage-time" data-role="time">&nbsp;</div>
    `;
    root.appendChild(card);
    state.stages[s] = { t0: null, t1: null, status: "pending", sub: "idle" };
  }
}

function setStageStatus(stage, status, sub) {
  const card = document.getElementById(`stage-${stage}`);
  if (!card) return;
  card.classList.remove("running", "ok", "error", "skipped");
  if (status) card.classList.add(status);
  state.stages[stage].status = status;
  if (sub != null) {
    card.querySelector("[data-role=sub]").textContent = sub;
    state.stages[stage].sub = sub;
  }
}

function setStageTime(stage, label) {
  const card = document.getElementById(`stage-${stage}`);
  if (!card) return;
  card.querySelector("[data-role=time]").textContent = label || "";
}

// --- artifact tabs ---

function buildTabs() {
  const tabs = document.getElementById("artifact-tabs");
  tabs.innerHTML = "";
  for (const a of ARTIFACT_DEFS) {
    const btn = document.createElement("button");
    btn.className = "tab";
    btn.textContent = a.label;
    btn.disabled = true;
    btn.dataset.key = a.key;
    btn.addEventListener("click", () => selectTab(a.key));
    tabs.appendChild(btn);
  }
}

function enableTab(key) {
  if (state.artifactsEnabled.has(key)) return;
  state.artifactsEnabled.add(key);
  const btn = document.querySelector(`.tab[data-key="${key}"]`);
  if (btn) btn.disabled = false;
  // Auto-select first one that becomes available
  if (!state.activeTab) selectTab(key);
}

async function selectTab(key) {
  const def = ARTIFACT_DEFS.find((a) => a.key === key);
  if (!def) return;
  state.activeTab = key;
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.key === key));

  const content = document.getElementById("artifact-content");
  if (!state.runId) { content.innerHTML = "<p class='placeholder'>no run selected</p>"; return; }

  const url = `/api/runs/${state.runId}/artifact/${def.file}`;

  if (def.lang === "video") {
    content.innerHTML = `<video controls src="${url}"></video>`;
    return;
  }

  content.innerHTML = "<p class='placeholder'>loading…</p>";
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    const txt = await res.text();
    const pre = document.createElement("pre");
    const code = document.createElement("code");
    code.className = `language-${def.lang}`;
    code.textContent = txt;
    pre.appendChild(code);
    content.innerHTML = "";
    content.appendChild(pre);
    if (window.hljs) window.hljs.highlightElement(code);
  } catch (e) {
    content.innerHTML = `<p class='placeholder'>failed to load ${def.file}: ${e.message}</p>`;
  }
}

// --- live log ---

function logRow(ev) {
  const row = document.createElement("div");
  const cls = ["row"];
  if (ev.type === "tool_call" || ev.type === "tool_result" || ev.type === "tool_error") cls.push("tool");
  if (ev.type === "subprocess_line") cls.push("sub");
  if (ev.type === "stage_end" && ev.status === "error") cls.push("error");
  if (ev.level === "ERROR") cls.push("error");
  row.className = cls.join(" ");

  const stag = ev.stage || "system";
  row.innerHTML = `
    <span class="ts">${fmtTime(ev.ts)}</span>
    <span class="stag stag-${stag}">${stag}</span>
    <span class="msg"></span>
  `;
  row.querySelector(".msg").textContent = formatEvent(ev);

  const log = document.getElementById("log");
  log.appendChild(row);

  const follow = document.getElementById("follow").checked;
  if (follow) log.scrollTop = log.scrollHeight;
}

function formatEvent(ev) {
  switch (ev.type) {
    case "run_start":       return `▶ run started — topic: ${ev.topic} (mode: ${ev.mode})`;
    case "run_end":         return `■ run ended — status: ${ev.status}${ev.error ? " — " + ev.error : ""}`;
    case "stage_start":     return `▸ ${ev.stage} started`;
    case "stage_end":       return `◂ ${ev.stage} ended — status: ${ev.status || "ok"}` + (ev.artifacts ? ` — artifacts: ${Object.keys(ev.artifacts).join(", ")}` : "");
    case "tool_call":       return `tool ${ev.tool} ← ${typeof ev.args === "string" ? ev.args : JSON.stringify(ev.args)}`;
    case "tool_result":     return `tool ${ev.tool || ""} → ${typeof ev.result === "string" ? ev.result : JSON.stringify(ev.result)} (${ev.elapsed ? ev.elapsed.toFixed(2) + "s" : ""})`;
    case "tool_error":      return `tool error: ${ev.error}`;
    case "subprocess_line": return `[${ev.stream}] ${ev.line}`;
    case "log":             return `${ev.level} ${ev.logger}: ${ev.msg}`;
    default:                return JSON.stringify(ev);
  }
}

// --- event dispatch ---

function handleEvent(ev) {
  logRow(ev);

  switch (ev.type) {
    case "run_start":
      state.startedAt = ev.ts;
      state.topic = ev.topic;
      document.getElementById("run-topic").textContent = ev.topic || "—";
      document.getElementById("run-status").textContent = "running";
      document.getElementById("run-status").className = "badge running";
      startElapsedTimer();
      break;
    case "run_end": {
      stopElapsedTimer();
      const s = ev.status === "ok" ? "ok" : "error";
      const badge = document.getElementById("run-status");
      badge.textContent = ev.status;
      badge.className = `badge ${s}`;
      // Close the SSE connection — server will have ended the stream too
      if (state.sse) state.sse.close();
      break;
    }
    case "stage_start":
      state.stages[ev.stage].t0 = ev.ts;
      setStageStatus(ev.stage, "running", "starting…");
      setStageTime(ev.stage, "");
      break;
    case "stage_end": {
      const st = state.stages[ev.stage];
      st.t1 = ev.ts;
      const status = ev.status === "error" ? "error" : (ev.status === "skipped" ? "skipped" : "ok");
      setStageStatus(ev.stage, status, status === "error" ? `ERROR: ${ev.error || ""}` : status);
      setStageTime(ev.stage, secs(st.t0, st.t1));
      if (ev.artifacts) {
        const a = ev.artifacts;
        if (a.report != null || ev.stage === "writer") enableTab("report");
        if (a.script != null || ev.stage === "scripter") enableTab("script");
        if (a.transcript_path || ev.stage === "narrator") enableTab("script");
        if (ev.stage === "narrator") enableTab("transcript");
        if (a.design_brief != null || ev.stage === "designer") enableTab("design");
        if (a.html != null || ev.stage === "builder") enableTab("html");
        if (a.video_path || ev.stage === "renderer") enableTab("video");
      }
      break;
    }
    case "tool_call":
      if (ev.stage && state.stages[ev.stage] && state.stages[ev.stage].status === "running") {
        setStageStatus(ev.stage, "running", `${ev.tool}(…)`);
      }
      break;
    case "subprocess_line":
      if (ev.stage && state.stages[ev.stage] && state.stages[ev.stage].status === "running") {
        setStageStatus(ev.stage, "running", ev.line.slice(0, 80));
      }
      break;
  }
}

// --- elapsed timer ---

function startElapsedTimer() {
  stopElapsedTimer();
  const tick = () => {
    if (!state.startedAt) return;
    const now = Date.now() / 1000;
    document.getElementById("run-elapsed").textContent = secs(state.startedAt, now);
  };
  tick();
  state.elapsedTimer = setInterval(tick, 500);
}
function stopElapsedTimer() {
  if (state.elapsedTimer) { clearInterval(state.elapsedTimer); state.elapsedTimer = null; }
}

// --- boot ---

async function connectLatest() {
  try {
    const res = await fetch("/api/runs/latest");
    if (!res.ok) {
      logRow({ ts: Date.now() / 1000, type: "log", stage: "system", level: "INFO", logger: "ui", msg: "no runs yet — start one with: python main.py \"your topic\"" });
      // Poll every 2s until we see a run
      setTimeout(connectLatest, 2000);
      return;
    }
    const { run_id } = await res.json();
    openRun(run_id);
  } catch (e) {
    logRow({ ts: Date.now() / 1000, type: "log", stage: "system", level: "ERROR", logger: "ui", msg: `connect error: ${e.message}` });
    setTimeout(connectLatest, 2000);
  }
}

function openRun(runId) {
  if (state.runId === runId) return;
  state.runId = runId;
  state.artifactsEnabled = new Set();
  state.activeTab = null;
  document.getElementById("run-id").textContent = runId;
  document.getElementById("run-topic").textContent = "—";
  document.getElementById("run-elapsed").textContent = "0s";
  document.getElementById("run-status").textContent = "connecting";
  document.getElementById("run-status").className = "badge pending";
  document.getElementById("log").innerHTML = "";
  buildStageStrip();
  buildTabs();
  document.getElementById("artifact-content").innerHTML = "<p class='placeholder'>select a completed stage artifact above to view its file contents.</p>";

  if (state.sse) state.sse.close();
  const es = new EventSource(`/api/runs/${runId}/events`);
  state.sse = es;
  es.onmessage = (m) => {
    try { handleEvent(JSON.parse(m.data)); }
    catch (e) { console.error("bad event", e, m.data); }
  };
  es.onerror = () => {
    // Server closes stream on run_end; check if that's the case.
    // Otherwise poll latest in case a new run started.
    setTimeout(checkForNewerRun, 1500);
  };
}

async function checkForNewerRun() {
  try {
    const res = await fetch("/api/runs/latest");
    if (!res.ok) return;
    const { run_id } = await res.json();
    if (run_id && run_id !== state.runId) openRun(run_id);
  } catch {}
}

// Switch to the newest run when a new one appears
setInterval(checkForNewerRun, 3000);

window.addEventListener("DOMContentLoaded", () => {
  buildStageStrip();
  buildTabs();
  connectLatest();
});

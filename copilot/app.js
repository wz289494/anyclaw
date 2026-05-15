const state = {
  apiBase: "http://127.0.0.1:7000",
  taskId: "",
  sessions: [],
  streaming: false,
};

const elements = {
  statusDot: document.getElementById("statusDot"),
  statusText: document.getElementById("statusText"),
  sessionTitle: document.getElementById("sessionTitle"),
  sessionList: document.getElementById("sessionList"),
  chatView: document.getElementById("chatView"),
  composer: document.getElementById("composer"),
  messageInput: document.getElementById("messageInput"),
  sendBtn: document.getElementById("sendBtn"),
  streamState: document.getElementById("streamState"),
  newSessionBtn: document.getElementById("newSessionBtn"),
  configModal: document.getElementById("configModal"),
  modalBackdrop: document.getElementById("modalBackdrop"),
  modalTitle: document.getElementById("modalTitle"),
  contentPanel: document.getElementById("contentPanel"),
  clearPanelBtn: document.getElementById("clearPanelBtn"),
  messageTemplate: document.getElementById("messageTemplate"),
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function inlineMarkdown(text) {
  let html = escapeHtml(text);
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
  return html;
}

function markdownToHtml(markdown) {
  const blocks = String(markdown || "").split(/\n{2,}/);
  const rendered = blocks.map((block) => {
    const lines = block.split("\n");

    if (lines.length >= 2 && lines.every((line) => line.includes("|"))) {
      const rows = lines
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line) => line.replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim()));

      if (rows.length >= 2 && rows[1].every((cell) => /^:?-{2,}:?$/.test(cell))) {
        const header = rows[0]
          .map((cell) => `<th>${inlineMarkdown(cell)}</th>`)
          .join("");
        const body = rows
          .slice(2)
          .map((row) => `<tr>${row.map((cell) => `<td>${inlineMarkdown(cell)}</td>`).join("")}</tr>`)
          .join("");
        return `<table><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table>`;
      }
    }

    if (block.startsWith("```")) {
      const code = block.replace(/^```[^\n]*\n?/, "").replace(/\n```$/, "");
      return `<pre><code>${escapeHtml(code)}</code></pre>`;
    }
    if (lines.every((line) => line.trim().startsWith("- "))) {
      const items = lines
        .map((line) => `<li>${inlineMarkdown(line.trim().slice(2))}</li>`)
        .join("");
      return `<ul>${items}</ul>`;
    }

    if (lines.every((line) => /^\d+\.\s/.test(line.trim()))) {
      const items = lines
        .map((line) => `<li>${inlineMarkdown(line.trim().replace(/^\d+\.\s/, ""))}</li>`)
        .join("");
      return `<ol>${items}</ol>`;
    }

    if (lines.length === 1 && lines[0].startsWith("### ")) {
      return `<h3>${inlineMarkdown(lines[0].slice(4))}</h3>`;
    }
    if (lines.length === 1 && lines[0].startsWith("## ")) {
      return `<h2>${inlineMarkdown(lines[0].slice(3))}</h2>`;
    }
    if (lines.length === 1 && lines[0].startsWith("# ")) {
      return `<h1>${inlineMarkdown(lines[0].slice(2))}</h1>`;
    }

    return `<p>${lines.map((line) => inlineMarkdown(line)).join("<br>")}</p>`;
  });

  return rendered.join("");
}

function parseMarkdownTable(markdown) {
  const lines = String(markdown || "")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.includes("|"));

  if (lines.length < 2) {
    return null;
  }

  const rows = lines.map((line) => line.replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim()));
  if (!rows[1] || !rows[1].every((cell) => /^:?-{2,}:?$/.test(cell))) {
    return null;
  }

  return {
    headers: rows[0],
    rows: rows.slice(2),
  };
}

function renderConfigContent(resource, markdown) {
  const titleMatch = String(markdown || "").match(/^#\s+(.+)$/m);
  const introTitle = titleMatch ? inlineMarkdown(titleMatch[1]) : "配置详情";

  if (resource === "tools") {
    const items = String(markdown || "")
      .split("\n")
      .map((line) => line.trim())
      .map((line) => {
        const match = line.match(/^-\s+\*\*(.+?)\*\*[：:]\s*(.+)$/);
        return match ? { name: match[1], description: match[2] } : null;
      })
      .filter(Boolean);

    if (!items.length) {
      return markdownToHtml(markdown);
    }

    return `
      <section class="config-section">
        <div class="config-intro">
          <h4>${introTitle}</h4>
          <p>当前可调用的工具列表，每个工具都可以被主模型按需选择并执行。</p>
        </div>
        <div class="config-card-grid">
          ${items
            .map(
              (item) => `
                <article class="config-card">
                  <div class="config-card-head">
                    <h5>${inlineMarkdown(item.name)}</h5>
                    <span class="config-badge">Tool</span>
                  </div>
                  <p>${inlineMarkdown(item.description)}</p>
                </article>
              `,
            )
            .join("")}
        </div>
      </section>
    `;
  }

  if (resource === "models") {
    const table = parseMarkdownTable(markdown);
    const parts = String(markdown || "").split(/^##\s+Thinking Models\s*$/m);
    const thinking = parts[1]
      ? parts[1]
          .split("\n")
          .map((line) => line.trim())
          .filter((line) => line.startsWith("- "))
          .map((line) => line.slice(2).trim())
      : [];

    if (!table || !table.rows.length) {
      return markdownToHtml(markdown);
    }

    return `
      <section class="config-section">
        <div class="config-intro">
          <h4>${introTitle}</h4>
          <p>当前模型工厂中的场景配置。每种场景都有独立的用途、Provider 和模型名称。</p>
        </div>
        <div class="config-stack">
          ${table.rows
            .map((row) => {
              const [scene = "", purpose = "", provider = "", model = ""] = row;
              return `
                <article class="config-card">
                  <div class="config-card-head">
                    <h5>${inlineMarkdown(scene)}</h5>
                    <div class="config-chip-row">
                      <span class="config-badge">${inlineMarkdown(provider)}</span>
                      <span class="config-badge subtle">${inlineMarkdown(model)}</span>
                    </div>
                  </div>
                  <p>${inlineMarkdown(purpose)}</p>
                </article>
              `;
            })
            .join("")}
        </div>
        ${
          thinking.length
            ? `
              <section class="config-subsection">
                <div class="config-subtitle">Thinking Models</div>
                <div class="config-chip-row">
                  ${thinking.map((item) => `<span class="config-badge">${inlineMarkdown(item)}</span>`).join("")}
                </div>
              </section>
            `
            : ""
        }
      </section>
    `;
  }

  if (resource === "skills") {
    const table = parseMarkdownTable(markdown);
    if (!table || !table.rows.length) {
      return markdownToHtml(markdown);
    }

    return `
      <section class="config-section">
        <div class="config-intro">
          <h4>${introTitle}</h4>
          <p>本地已加载的 skills 列表，每个 skill 都通过标准目录和说明文件接入。</p>
        </div>
        <div class="config-stack">
          ${table.rows
            .map((row) => {
              const [name = "", description = "", folder = ""] = row;
              return `
                <article class="config-card">
                  <div class="config-card-head">
                    <h5>${inlineMarkdown(name)}</h5>
                    <span class="config-badge">Skill</span>
                  </div>
                  <p>${inlineMarkdown(description || "暂无描述")}</p>
                  <div class="config-path">${inlineMarkdown(folder)}</div>
                </article>
              `;
            })
            .join("")}
        </div>
      </section>
    `;
  }

  return markdownToHtml(markdown);
}

function setConnectionStatus(isOnline, text) {
  elements.statusDot.classList.remove("online", "offline");
  elements.statusDot.classList.add(isOnline ? "online" : "offline");
  elements.statusText.textContent = text;
}

function setStreaming(isStreaming) {
  state.streaming = isStreaming;
  elements.sendBtn.disabled = isStreaming;
  elements.messageInput.disabled = isStreaming;
  elements.streamState.textContent = isStreaming ? "流式" : "空闲";
}

function shortTaskId(taskId) {
  if (!taskId) {
    return "未命名会话";
  }
  return `${taskId.slice(0, 8)}...${taskId.slice(-4)}`;
}

function sessionHeading(taskId) {
  return taskId ? `会话 ${shortTaskId(taskId)}` : "准备开始对话";
}

function scrollChatToBottom() {
  elements.chatView.scrollTop = elements.chatView.scrollHeight;
}

function toolEventCardHtml(event) {
  const title =
    event.type === "tool_call"
      ? `调用 ${event.tool_name || "unknown"}`
      : event.type === "tool_result"
        ? `${event.tool_name || "unknown"} 返回结果`
        : "状态更新";
  const body =
    event.type === "state_update"
      ? `<pre><code>${escapeHtml(JSON.stringify(event.state || {}, null, 2))}</code></pre>`
      : event.type === "tool_call"
        ? `<pre><code>${escapeHtml(JSON.stringify(event.args || {}, null, 2))}</code></pre>`
        : `<div class="tool-event-text">${markdownToHtml(String(event.result || ""))}</div>`;
  const badge = event.type === "tool_call" ? "调用" : event.type === "tool_result" ? "结果" : "状态";

  return `
    <article class="tool-event ${escapeHtml(event.type || "tool_result")}">
      <div class="tool-event-head">
        <div class="tool-event-title">${escapeHtml(title)}</div>
        <span class="tool-event-badge">${escapeHtml(badge)}</span>
      </div>
      ${body}
    </article>
  `;
}

function syncMessageToolBadge(anchorNode, events) {
  if (!anchorNode) {
    return;
  }

  if (!events || !events.length) {
    anchorNode.innerHTML = "";
    return;
  }

  anchorNode.innerHTML = `
    <div class="message-tool-affordance">
      <button class="message-tool-button" type="button" aria-label="查看工具调用">
        <span class="message-tool-icon">i</span>
      </button>
      <div class="message-tool-popover">
        <div class="message-tool-popover-title">工具调用</div>
        <div class="message-tool-popover-body">
          ${events.map((event) => toolEventCardHtml(event)).join("")}
        </div>
      </div>
    </div>
  `;
}

function showEmptyState(text) {
  elements.chatView.innerHTML = `<div class="empty-state">${escapeHtml(text)}</div>`;
}

function createMessageNode(role, content) {
  const fragment = elements.messageTemplate.content.cloneNode(true);
  const row = fragment.querySelector(".message-row");
  const article = fragment.querySelector(".message");
  const bodyNode = fragment.querySelector(".message-body");
  const toolsAnchor = fragment.querySelector(".message-tools-anchor");
  row.classList.add(role);
  article.classList.add(role);
  bodyNode.innerHTML = markdownToHtml(content);
  return { fragment, row, article, bodyNode, toolsAnchor };
}

function appendMessage(role, content, options = {}) {
  const { fragment, article, toolsAnchor } = createMessageNode(role, content);
  if (role === "assistant" && Array.isArray(options.toolEvents) && options.toolEvents.length) {
    syncMessageToolBadge(toolsAnchor, options.toolEvents);
    article.classList.add("has-tools");
  }
  const empty = elements.chatView.querySelector(".empty-state");
  if (empty) {
    empty.remove();
  }
  elements.chatView.appendChild(fragment);
  scrollChatToBottom();
  return { article, toolsAnchor };
}

function renderMessages(messages) {
  elements.chatView.innerHTML = "";
  if (!messages || messages.length === 0) {
    showEmptyState("新建一个会话，或者从左侧继续之前的记忆。");
    return;
  }

  let pendingToolEvents = [];
  messages.forEach((message) => {
    const role = message.role || "system";
    if (role === "tool") {
      pendingToolEvents.push({
        type: "tool_result",
        tool_name: message.tool_name || "",
        result: message.content || "",
      });
      return;
    }
    appendMessage(role, message.content || "", {
      toolEvents: role === "assistant" ? pendingToolEvents : [],
    });
    if (role === "assistant") {
      pendingToolEvents = [];
    }
  });
}

function renderSessions() {
  const list = elements.sessionList;
  list.innerHTML = "";

  if (!state.sessions.length) {
    list.innerHTML = '<div class="status-meta">还没有历史会话</div>';
    return;
  }

  state.sessions.forEach((taskId) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "session-btn";
    if (taskId === state.taskId) {
      button.classList.add("active");
    }
    button.innerHTML = `
      <div class="session-id">${escapeHtml(shortTaskId(taskId))}</div>
      <div class="session-meta">${escapeHtml(taskId)}</div>
    `;
    button.addEventListener("click", () => {
      void loadSession(taskId);
    });
    list.appendChild(button);
  });
}

async function apiFetch(path, options = {}) {
  const response = await fetch(`${state.apiBase}${path}`, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return response;
}

async function fetchJson(path, options = {}) {
  const response = await apiFetch(path, options);
  return response.json();
}

async function fetchText(path, options = {}) {
  const response = await apiFetch(path, options);
  return response.text();
}

async function initConfig() {
  try {
    const response = await fetch("/config.json");
    if (response.ok) {
      const config = await response.json();
      if (config.apiBase) {
        state.apiBase = config.apiBase;
      }
    }
  } catch (error) {
    console.warn("load config failed", error);
  }
}

async function ensureApiAvailable() {
  try {
    await fetchText("/api/tools");
    setConnectionStatus(true, "API 已连接");
    return true;
  } catch (error) {
    setConnectionStatus(false, "API 不可用");
    showEmptyState("未连接到 AnyClaw API。请先启动 anyclaw-api，再刷新当前页面。");
    return false;
  }
}

async function loadSessions() {
  try {
    const payload = await fetchJson("/api/memory");
    state.sessions = Array.isArray(payload.task_ids) ? payload.task_ids : [];
    renderSessions();
  } catch (error) {
    setConnectionStatus(false, "读取会话失败");
  }
}

async function createSession() {
  const payload = await fetchJson("/api/new", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
  });
  state.taskId = payload.task_id || "";
  elements.sessionTitle.textContent = sessionHeading(state.taskId);
  renderMessages([]);
  await loadSessions();
}

async function loadSession(taskId) {
  try {
    const payload = await fetchJson(`/api/session?task_id=${encodeURIComponent(taskId)}`);
    state.taskId = payload.task_id || taskId;
    elements.sessionTitle.textContent = sessionHeading(state.taskId);
    renderMessages(Array.isArray(payload.messages) ? payload.messages : []);
    renderSessions();
  } catch (error) {
    appendMessage("system", `加载会话失败：${error.message}`);
  }
}

async function openResource(resource) {
  try {
    const text = await fetchText(`/api/${resource}`);
    const titleMap = {
      tools: "Tools 配置",
      models: "Models 配置",
      skills: "Skills 配置",
    };
    elements.modalTitle.textContent = titleMap[resource] || "配置详情";
    elements.contentPanel.innerHTML = renderConfigContent(resource, text);
    elements.configModal.classList.remove("hidden");
    elements.configModal.setAttribute("aria-hidden", "false");
  } catch (error) {
    appendMessage("system", `读取 ${resource} 失败：${error.message}`);
  }
}

function hidePanel() {
  elements.configModal.classList.add("hidden");
  elements.configModal.setAttribute("aria-hidden", "true");
  elements.contentPanel.innerHTML = "";
}

async function streamAgent(query) {
  const response = await apiFetch("/api/agent", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_id: state.taskId, query }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  const assistantNode = createMessageNode("assistant", "");
  const empty = elements.chatView.querySelector(".empty-state");
  if (empty) {
    empty.remove();
  }
  elements.chatView.appendChild(assistantNode.fragment);
  let assistantText = "";
  const toolEvents = [];

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    lines.forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed) {
        return;
      }
      const event = JSON.parse(trimmed);
      if (event.type === "token") {
        assistantText = event.content ? assistantText + event.content : assistantText;
        assistantNode.bodyNode.innerHTML = markdownToHtml(assistantText);
      } else if (event.type === "tool_call") {
        toolEvents.push({
          type: "tool_call",
          tool_name: event.tool_name || "unknown",
          args: event.args || {},
        });
        assistantNode.article.classList.add("has-tools");
        syncMessageToolBadge(assistantNode.toolsAnchor, toolEvents);
      } else if (event.type === "tool_result") {
        toolEvents.push({
          type: "tool_result",
          tool_name: event.tool_name || "unknown",
          result: String(event.result || ""),
        });
        assistantNode.article.classList.add("has-tools");
        syncMessageToolBadge(assistantNode.toolsAnchor, toolEvents);
      } else if (event.type === "state_update") {
        toolEvents.push({
          type: "state_update",
          state: event.state || {},
        });
        assistantNode.article.classList.add("has-tools");
        syncMessageToolBadge(assistantNode.toolsAnchor, toolEvents);
      } else if (event.type === "final") {
        assistantText = event.content || assistantText;
        assistantNode.bodyNode.innerHTML = markdownToHtml(assistantText);
      }
      scrollChatToBottom();
    });
  }
}

async function handleSend(event) {
  event.preventDefault();
  const query = elements.messageInput.value.trim();
  if (!query || state.streaming) {
    return;
  }

  try {
    hidePanel();
    if (!state.taskId) {
      await createSession();
    }
    appendMessage("user", query);
    elements.messageInput.value = "";
    setStreaming(true);
    await streamAgent(query);
    await loadSessions();
  } catch (error) {
    appendMessage("system", `发送失败：${error.message}`);
  } finally {
    setStreaming(false);
  }
}

async function bootstrap() {
  await initConfig();
  elements.sessionTitle.textContent = sessionHeading(state.taskId);

  const apiReady = await ensureApiAvailable();
  if (!apiReady) {
    return;
  }

  await loadSessions();
  if (state.sessions.length) {
    await loadSession(state.sessions[0]);
  } else {
    showEmptyState("当前还没有会话，点击左侧“新建对话”开始。");
  }
}

elements.composer.addEventListener("submit", (event) => {
  void handleSend(event);
});

elements.newSessionBtn.addEventListener("click", () => {
  void createSession();
});

document.querySelectorAll("[data-resource]").forEach((button) => {
  button.addEventListener("click", () => {
    void openResource(button.dataset.resource);
  });
});

elements.clearPanelBtn.addEventListener("click", hidePanel);
elements.modalBackdrop.addEventListener("click", hidePanel);

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !elements.configModal.classList.contains("hidden")) {
    hidePanel();
  }
});

void bootstrap();

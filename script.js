const DEFAULTS = {
  apiUrl: "https://text.pollinations.ai/openai/v1/chat/completions",
  model: "openai",
  systemPrompt:
    "You are a friendly, capable AI assistant. Be concise but helpful. " +
    "Use short paragraphs, bullet points and code blocks where they help readability. " +
    "If the user asks something you cannot answer, say so honestly.",
};

const SUGGESTIONS = [
  "What can you do?",
  "Write a short poem",
  "Explain quantum computing simply",
  "Give me a random fact",
  "Help me fix a bug in my code",
  "Write a product description",
];

const ELEMENTS = {
  chat: document.getElementById("chat"),
  form: document.getElementById("composer"),
  input: document.getElementById("input"),
  send: document.getElementById("send"),
  newChat: document.getElementById("newChat"),
  settingsBtn: document.getElementById("settingsBtn"),
  settings: document.getElementById("settings"),
  closeSettings: document.getElementById("closeSettings"),
  saveSettings: document.getElementById("saveSettings"),
  resetSettings: document.getElementById("resetSettings"),
  apiUrl: document.getElementById("apiUrl"),
  model: document.getElementById("model"),
  systemPrompt: document.getElementById("systemPrompt"),
  suggestions: document.getElementById("suggestions"),
};

let config = { ...DEFAULTS };
let conversation = [];
let busy = false;
let firstRender = true;

function loadConfig() {
  try {
    const saved = JSON.parse(localStorage.getItem("aichatbot-config"));
    config = { ...DEFAULTS, ...saved };
  } catch {
    config = { ...DEFAULTS };
  }
  ELEMENTS.apiUrl.value = config.apiUrl;
  ELEMENTS.model.value = config.model;
  ELEMENTS.systemPrompt.value = config.systemPrompt;
}

function saveConfig() {
  localStorage.setItem("aichatbot-config", JSON.stringify(config));
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderMarkdown(text) {
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
  html = html.replace(/`([^`\n]+)`/g, "<code>$1</code>");
  html = html.replace(/^```([\s\S]*?)```/gm, "<pre><code>$1</code></pre>");
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  html = html.replace(/^### (.*)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.*)$/gm, "<h2>$1</h2>");
  html = html.replace(/^- (.*)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`);
  html = html.replace(/\n{2,}/g, "<br/><br/>").replace(/\n/g, "<br/>");
  return html;
}

function timeNow() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function addMessage(role, text, streaming = false) {
  const msg = document.createElement("div");
  msg.className = `msg ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar";
  avatar.innerHTML = role === "bot" ? '<i class="fa-solid fa-robot"></i>' : '<i class="fa-solid fa-user"></i>';

  const body = document.createElement("div");
  body.className = "msg-body";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.textContent = text;

  const meta = document.createElement("div");
  meta.className = "msg-meta";
  meta.innerHTML = `<span>${timeNow()}</span>`;

  if (role === "bot" && !streaming) {
    const copy = document.createElement("button");
    copy.className = "copy-btn";
    copy.textContent = "Copy";
    copy.addEventListener("click", () => {
      navigator.clipboard.writeText(text);
      copy.textContent = "Copied!";
      setTimeout(() => (copy.textContent = "Copy"), 1500);
    });
    meta.appendChild(copy);
  }

  body.appendChild(bubble);
  body.appendChild(meta);
  msg.appendChild(avatar);
  msg.appendChild(body);
  ELEMENTS.chat.appendChild(msg);
  ELEMENTS.chat.scrollTop = ELEMENTS.chat.scrollHeight;
  return bubble;
}

function showTyping() {
  const msg = document.createElement("div");
  msg.className = "msg bot";
  msg.id = "typing";
  msg.innerHTML = `
    <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
    <div class="msg-bubble typing"><span></span><span></span><span></span></div>
  `;
  ELEMENTS.chat.appendChild(msg);
  ELEMENTS.chat.scrollTop = ELEMENTS.chat.scrollHeight;
}

function removeTyping() {
  const typing = document.getElementById("typing");
  if (typing) typing.remove();
}

function addSuggestions() {
  ELEMENTS.suggestions.innerHTML = "";
  SUGGESTIONS.forEach((label) => {
    const chip = document.createElement("button");
    chip.className = "chip";
    chip.textContent = label;
    chip.addEventListener("click", () => send(label));
    ELEMENTS.suggestions.appendChild(chip);
  });
}

function renderWelcome() {
  addMessage("bot", "Hi, I'm your AI chatbot! I run entirely in your browser and connect to a free, keyless language model. Ask me anything, or try one of the suggestions below.");
  addSuggestions();
  firstRender = false;
}

async function streamResponse(messages, bubble) {
  const response = await fetch(config.apiUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: config.model,
      messages,
      stream: true,
      private: true,
    }),
  });

  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let full = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop();

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith("data:")) continue;
      const data = trimmed.slice(5).trim();
      if (data === "[DONE]") continue;

      try {
        const json = JSON.parse(data);
        const delta = json.choices?.[0]?.delta?.content || "";
        if (delta) {
          full += delta;
          bubble.innerHTML = renderMarkdown(full);
          ELEMENTS.chat.scrollTop = ELEMENTS.chat.scrollHeight;
        }
      } catch {
        // partial JSON on the stream boundary, wait for more
      }
    }
  }
  return full;
}

async function send(text) {
  const content = (text || ELEMENTS.input.value).trim();
  if (!content || busy) return;

  if (firstRender) {
    ELEMENTS.suggestions.innerHTML = "";
    ELEMENTS.suggestions.classList.add("hidden");
    firstRender = false;
  }

  ELEMENTS.input.value = "";
  autoResize();

  addMessage("user", content);
  conversation.push({ role: "user", content });

  const bubble = addMessage("bot", "", true);
  busy = true;
  ELEMENTS.send.disabled = true;
  showTyping();

  const history = conversation.slice(-12);
  const messages = [
    { role: "system", content: config.systemPrompt },
    ...history,
  ];

  try {
    const reply = await streamResponse(messages, bubble);
    bubble.innerHTML = renderMarkdown(reply);
    conversation.push({ role: "assistant", content: reply });
  } catch (err) {
    bubble.innerHTML =
      "I hit a connection issue (the free endpoint may be busy). Please try again in a moment, or check the API URL in settings.";
  } finally {
    removeTyping();
    busy = false;
    ELEMENTS.send.disabled = false;
    ELEMENTS.chat.scrollTop = ELEMENTS.chat.scrollHeight;
  }
}

function autoResize() {
  ELEMENTS.input.style.height = "auto";
  ELEMENTS.input.style.height = Math.min(ELEMENTS.input.scrollHeight, 140) + "px";
}

ELEMENTS.form.addEventListener("submit", (e) => {
  e.preventDefault();
  send();
});

ELEMENTS.input.addEventListener("input", autoResize);

ELEMENTS.input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});

ELEMENTS.newChat.addEventListener("click", () => {
  conversation = [];
  ELEMENTS.chat.innerHTML = "";
  ELEMENTS.suggestions.classList.remove("hidden");
  firstRender = true;
  renderWelcome();
  ELEMENTS.input.focus();
});

ELEMENTS.settingsBtn.addEventListener("click", () => {
  ELEMENTS.settings.hidden = false;
});

ELEMENTS.closeSettings.addEventListener("click", () => {
  ELEMENTS.settings.hidden = true;
});

ELEMENTS.saveSettings.addEventListener("click", () => {
  config.apiUrl = ELEMENTS.apiUrl.value.trim();
  config.model = ELEMENTS.model.value.trim();
  config.systemPrompt = ELEMENTS.systemPrompt.value.trim();
  saveConfig();
  ELEMENTS.settings.hidden = true;
});

ELEMENTS.resetSettings.addEventListener("click", () => {
  config = { ...DEFAULTS };
  ELEMENTS.apiUrl.value = config.apiUrl;
  ELEMENTS.model.value = config.model;
  ELEMENTS.systemPrompt.value = config.systemPrompt;
  saveConfig();
});

ELEMENTS.settings.addEventListener("click", (e) => {
  if (e.target === ELEMENTS.settings) ELEMENTS.settings.hidden = true;
});

loadConfig();
renderWelcome();
ELEMENTS.input.focus();

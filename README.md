<div align="center">

# 🤖 AI Chatbot

### Free Online ChatGPT-Like Chatbot — **No API Key. No Signup. No Backend.**

A beautiful, fast, browser-based AI chatbot built with pure **HTML, CSS & JavaScript** that streams live responses from a free keyless OpenAI-compatible API. Works on desktop and mobile, open-source forever.

[![Live Demo](https://img.shields.io/badge/Live_Demo-nytheon.github.io%2FAi--Chatbot-38bdf8?style=for-the-badge&logo=githubpages&logoColor=white)](https://nytheon.github.io/Ai-Chatbot/)
[![GitHub Stars](https://img.shields.io/github/stars/nytheon/Ai-Chatbot?style=for-the-badge&logo=github&color=yellow)](https://github.com/nytheon/Ai-Chatbot/stargazers)
[![GitHub License](https://img.shields.io/github/license/nytheon/Ai-Chatbot?style=for-the-badge&logo=mit&color=brightgreen)](https://github.com/nytheon/Ai-Chatbot/blob/main/LICENSE)
[![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](#)
[![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](#)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](#)

</div>

---

## ✨ Why You'll Love It

- 🆓 **100% Free** — no API key, no credit card, no account, no signup ever
- ⚡ **Streaming replies** — responses appear word-by-word like ChatGPT
- 🧠 **Real language model** — powered by a keyless OpenAI-compatible endpoint
- 🎨 **Glassmorphism UI** — modern frosted-glass dark theme that looks great anywhere
- 📱 **Fully responsive** — works beautifully on desktop, tablet, and phone
- ⚙️ **Configurable** — change the API URL, model, and system prompt right from the UI
- 🔒 **Private** — your chat never touches a server you didn't configure
- 🧹 **Clean code** — a simple, well-commented vanilla HTML/CSS/JS codebase anyone can learn from

---

## 🚀 Quick Start

**Option 1 — Use it instantly:** open the [live demo](https://nytheon.github.io/Ai-Chatbot/) and start chatting.

**Option 2 — Run it locally:**

```bash
git clone https://github.com/nytheon/Ai-Chatbot.git
cd Ai-Chatbot
# just open index.html in your browser, or serve it:
python -m http.server 8000
```

**Option 3 — Deploy to GitHub Pages:**

1. Fork this repository
2. In your fork go to **Settings → Pages**
3. Set the source to **Deploy from a branch → main → / (root)**
4. Your chatbot is live at `https://<your-username>.github.io/Ai-Chatbot/`

---

## 🛠️ How It Works

The app is a single-page frontend (no build step, no dependencies) that calls an OpenAI-compatible **Chat Completions** API:

```
POST https://text.pollinations.ai/openai/v1/chat/completions
Content-Type: application/json
```

```json
{
  "model": "openai",
  "messages": [
    { "role": "system", "content": "You are a friendly, capable AI assistant." },
    { "role": "user", "content": "Hello!" }
  ],
  "stream": true,
  "private": true
}
```

Because the endpoint needs **no API key**, the request can be made directly from the browser. Your conversation history is kept in memory, and the last 12 messages are sent with each request so the bot remembers context.

> **Bring your own endpoint:** open **Settings** (⚙️) in the app and point it at any OpenAI-compatible API URL and model. No code changes needed.

---

## ⚙️ Settings

| Setting | Default | Purpose |
| --- | --- | --- |
| API URL | `https://text.pollinations.ai/openai/v1/chat/completions` | OpenAI-compatible endpoint |
| Model | `openai` | Model name sent to the endpoint |
| System prompt | Built-in assistant prompt | How the bot behaves |

All settings are saved to your browser's `localStorage`.

---

## 📁 Project Structure

```
Ai-Chatbot/
├── index.html   # page structure
├── style.css    # glassmorphism styling
├── script.js    # chat logic, streaming, settings
└── LICENSE      # MIT license
```

---

## 🧰 Technologies

- **HTML5** — semantic markup
- **CSS3** — custom properties, grid/flexbox, backdrop-filter glassmorphism, responsive breakpoints
- **JavaScript** — async/await, `fetch` streaming via the Fetch API `ReadableStream`, DOM manipulation, `localStorage`

---

## 📸 Features Preview

- Typing indicator animation
- Markdown-rendered bot replies (bold, lists, code blocks, links)
- One-click **Copy** button on every bot reply
- Quick suggestion chips to start conversations
- **New chat** button to reset context
- Configurable model + API URL + system prompt
- Graceful error handling when the free endpoint is busy

---

## 🤝 Contributing

Contributions are very welcome! Open an issue or submit a pull request. If you like this project, please give it a ⭐ — it helps more people find a free AI chatbot.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">Made with ❤️ for developers everywhere.</p>

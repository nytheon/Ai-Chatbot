<div align="center">

# 🤖 AI Chatbot

### A Free, Streaming AI Chatbot for the Terminal

A zero-dependency Python CLI chatbot that talks to any **OpenAI-compatible Chat Completions API**. Streams responses word-by-word, remembers conversation context, and works with the free tier of [OpenRouter](https://openrouter.ai) or any endpoint of your choice.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge&logo=mit&logoColor=white)](#)
[![Endpoint](https://img.shields.io/badge/OpenAI-Compatible-5C2D91?style=for-the-badge&logo=openai&logoColor=white)](#)

</div>

---

## ✨ Features

- ⚡ **Streaming replies** — responses appear live, word-by-word
- 🧠 **Free by default** — works with OpenRouter's free models
- 🔀 **Automatic failover** — tries fallback endpoints if the first is busy
- 💬 **Interactive chat** — with `/new`, `/system`, `/help`, `/quit`
- 📖 **Context-aware** — remembers the last 24 messages of conversation
- 🔑 **Bring your own key/endpoint** — OpenAI, OpenRouter, or any compatible API
- 🐍 **Zero dependencies** — only Python 3.10+ and `requests`

---

## 🚀 Quick Start

### 1. Get a free API key (one-time)

1. Create a free account at [openrouter.ai](https://openrouter.ai)
2. Go to **Keys** and create a key
3. Set it as an environment variable:

   ```bash
   # Windows (PowerShell)
   $env:OPENROUTER_API_KEY = "sk-or-..."

   # macOS / Linux
   export OPENROUTER_API_KEY="sk-or-..."
   ```

### 2. Run

```bash
pip install requests
python chatbot.py
```

That's it. Start chatting — the bot will ask you questions, answer yours, and remember context between messages.

---

## 📖 Usage

### Interactive chat

```bash
python chatbot.py
```

| Command | Action |
| --- | --- |
| `/new` | Clear the conversation history |
| `/system <prompt>` | Set a new system prompt |
| `/help` | Show the in-chat help |
| `/quit` | Exit |

### Single question

```bash
python chatbot.py --once "What is a hash function?"
```

### Command-line options

| Option | Default | Description |
| --- | --- | --- |
| `--api-url` | `https://openrouter.ai/api/v1/chat/completions` | OpenAI-compatible endpoint |
| `--model` | `meta-llama/llama-3.3-70b-instruct:free` | Model name |
| `--system-prompt` | Built-in assistant prompt | How the bot behaves |
| `--api-key` | `OPENROUTER_API_KEY` or `OPENAI_API_KEY` env var | Bearer token (optional) |
| `--once` | — | Ask a single question, then exit |

### Custom endpoints

Any OpenAI-compatible API works. Examples:

```bash
# OpenAI
python chatbot.py --api-url https://api.openai.com/v1/chat/completions \
                  --model gpt-4o-mini \
                  --api-key sk-your-key

# A local server (e.g. llama.cpp, vLLM, Ollama with OpenAI-compat)
python chatbot.py --api-url http://localhost:8000/v1/chat/completions \
                  --model llama-3.1
```

---

## 🛠️ How It Works

The bot sends the conversation as a Chat Completions request with `stream: true`:

```bash
POST {api-url}
Authorization: Bearer {api-key}
Content-Type: application/json
```

```json
{
  "model": "meta-llama/llama-3.3-70b-instruct:free",
  "messages": [
    { "role": "system", "content": "You are a friendly, capable AI assistant." },
    { "role": "user", "content": "Hello!" }
  ],
  "stream": true
}
```

Responses are parsed from the SSE (`text/event-stream`) stream and printed live. If the primary endpoint fails with a transient error (429, 500, 502, 503, 504), the bot retries with exponential backoff, then falls back to alternative endpoints. The last 24 messages are kept as context.

---

## 📁 Project Structure

```
Ai-Chatbot/
├── chatbot.py   # the entire chatbot — CLI, streaming, retries
├── README.md    # you are here
└── LICENSE      # MIT license
```

---

## 🤝 Contributing

Contributions are welcome! Open an issue or submit a pull request.

## 📄 License

Licensed under the [MIT License](LICENSE).

---

<p align="center">Made with ❤️ for developers everywhere.</p>
# 2026-06-09T13:09:53.904464
# 2026-08-04T06:31:42.904464
# 2025-09-24T02:31:05.904464
# 2026-04-26T03:25:49.904464
# 2026-02-15T09:34:01.904464
# 2025-10-29T22:19:42.904464
# 2026-06-29T09:42:33.904464
# 2026-02-19T04:35:09.904464
# 2026-05-31T19:10:28.904464
# 2026-03-21T05:22:15.904464
# 2025-09-20T00:38:17.904464
# 2025-12-26T04:04:47.904464
# 2026-06-16T05:51:38.904464
# 2025-08-26T17:37:32.904464
# 2025-09-10T10:30:56.904464
# 2025-12-10T15:22:40.904464
# 2025-08-13T03:08:00.904464
# 2025-09-27T01:47:03.904464
# 2026-07-30T03:21:07.904464
# 2026-06-17T11:17:08.904464
# 2026-03-22T19:25:19.904464
# 2026-06-17T03:11:27.904464
# 2026-06-29T10:00:01.904464
# 2025-09-02T02:59:45.904464
# 2026-05-07T05:26:28.904464
# 2025-09-24T14:44:43.904464
# 2025-12-12T19:26:34.904464
# 2026-05-01T16:08:02.904464
# 2025-10-02T10:36:13.904464
# 2026-08-07T03:01:45.904464
# 2026-04-12T17:42:10.904464
# 2025-10-11T23:23:27.904464
# 2025-10-16T10:11:39.904464
# 2026-06-10T18:55:19.904464
# 2026-08-04T09:06:37.904464
# 2026-06-05T18:38:54.904464
# 2025-10-06T00:59:59.904464
# 2025-10-19T12:58:02.904464
# 2026-05-18T10:19:25.904464
# 2026-08-05T06:09:15.904464

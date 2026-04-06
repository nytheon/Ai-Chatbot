#!/usr/bin/env python3
"""
AI Chatbot - Python CLI version.

A free, streaming AI chatbot that talks to any OpenAI-compatible
Chat Completions API. Uses the free OpenRouter tier by default;
bring your own endpoint/key for production use.

Usage:
    python chatbot.py                     # start interactive chat
    python chatbot.py --api-url <URL>     # custom endpoint
    python chatbot.py --model <name>      # custom model
    python chatbot.py --once "hello"      # single question, then exit

Commands inside the chat:
    /new     clear conversation history
    /system  set a new system prompt
    /help    show this help
    /quit    exit
"""

import argparse
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    print("Missing dependency: run `pip install requests` first.", file=sys.stderr)
    sys.exit(1)

DEFAULT_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
DEFAULT_SYSTEM_PROMPT = (
    "You are a friendly, capable AI assistant. Be concise but helpful. "
    "Use short paragraphs, bullet points and code blocks where they help readability. "
    "If the user asks something you cannot answer, say so honestly."
)

# If the primary endpoint is unreachable, fall back through these.
FALLBACK_ENDPOINTS = [
    ("https://openrouter.ai/api/v1/chat/completions", "meta-llama/llama-3.3-70b-instruct:free"),
]

USER_AGENT = "Ai-Chatbot/1.0 (+https://github.com/nytheon/Ai-Chatbot)"


def _parse_sse(response):
    """Yield content deltas from a streaming SSE response."""
    for raw_line in response.iter_lines(decode_unicode=True):
        if not raw_line:
            continue
        line = raw_line.strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            chunk = json.loads(data)
            yield chunk["choices"][0].get("delta", {}).get("content", "")
        except (json.JSONDecodeError, KeyError, IndexError):
            continue


def ask(
    api_url: str,
    model: str,
    system_prompt: str,
    history: list,
    stream: bool = True,
    timeout: int = 180,
    echo: bool = True,
    retries: int = 2,
    api_key: str | None = None,
):
    """Send the conversation to the API and return the full reply.

    Uses streaming by default. When ``echo`` is True, tokens are printed
    live as they arrive. If the request fails (rate limit / busy endpoint),
    it falls back to the FALLBACK_ENDPOINTS list, then to OpenRouter when
    an API key is available.
    """
    messages = [{"role": "system", "content": system_prompt}, *history]

    endpoints = [(api_url, model)]
    endpoints.extend(FALLBACK_ENDPOINTS)

    headers = {"User-Agent": USER_AGENT, "Accept": "text/event-stream"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    last_error = None
    for url, mdl in endpoints:
        payload = {"model": mdl, "messages": messages, "stream": stream}
        for attempt in range(retries + 1):
            try:
                response = requests.post(
                    url, json=payload, headers=headers, timeout=timeout, stream=True
                )
            except requests.RequestException as exc:
                last_error = exc
                time.sleep(2 ** attempt)
                continue

            if response.status_code == 200:
                full = ""
                for delta in _parse_sse(response):
                    if delta:
                        full += delta
                        if echo:
                            print(delta, end="", flush=True)
                if echo:
                    print()
                return full

            detail = ""
            try:
                detail = response.json().get("error", str(response.text[:200]))
            except Exception:
                detail = response.text[:200]
            last_error = RuntimeError(f"API returned {response.status_code}: {detail}")

            if response.status_code in (429, 500, 502, 503, 504) or "402" in str(detail):
                time.sleep(2 ** attempt)
                continue
            break

        if echo:
            print()
        print(
            f"\n[endpoint {url} unavailable, trying next...] ",
            end="",
            flush=True,
        )
        time.sleep(1)

    raise RuntimeError(
        f"All endpoints failed. Last error: {last_error}\n"
        "Set an OpenRouter API key (--api-key or OPENROUTER_API_KEY env var) "
        "or point at your own endpoint with --api-url."
    )


def run_interactive(args):
    history = []
    system_prompt = args.system_prompt

    print(f"AI Chatbot (model: {args.model})\nType /help for commands, /quit to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            cmd = user_input.lower().split()
            if cmd[0] == "/quit":
                break
            elif cmd[0] == "/new":
                history = []
                print("[history cleared]\n")
                continue
            elif cmd[0] == "/system":
                system_prompt = input("New system prompt: ").strip() or system_prompt
                continue
            elif cmd[0] == "/help":
                print(
                    "Commands:\n"
                    "  /new     clear conversation history\n"
                    "  /system  set a new system prompt\n"
                    "  /help    show this help\n"
                    "  /quit    exit\n"
                )
                continue
            else:
                print(f"Unknown command: {cmd[0]}\n")
                continue

        history.append({"role": "user", "content": user_input})
        print("AI: ", end="", flush=True)
        try:
            reply = ask(
                args.api_url,
                args.model,
                system_prompt,
                history,
                stream=True,
                api_key=args.api_key,
            )
        except Exception as exc:
            print(f"\n[error] {exc}\n")
            history.pop()
            continue

        history.append({"role": "assistant", "content": reply})

        # Keep context bounded.
        if len(history) > 24:
            history = history[-24:]


def main():
    parser = argparse.ArgumentParser(description="AI Chatbot - streaming Python CLI")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="OpenAI-compatible endpoint URL")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument("--system-prompt", default=DEFAULT_SYSTEM_PROMPT, help="System prompt")
    parser.add_argument("--api-key", default=os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY"), help="Bearer API key (optional)")
    parser.add_argument(
        "--once", metavar="TEXT", help="Ask a single question and exit (streaming)"
    )
    args = parser.parse_args()

    if args.once:
        try:
            reply = ask(
                args.api_url,
                args.model,
                args.system_prompt,
                [{"role": "user", "content": args.once}],
                stream=True,
                api_key=args.api_key,
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)
        return

    run_interactive(args)


if __name__ == "__main__":
    main()
# 2026-04-30T00:39:36.904464
# 2026-04-21T13:01:26.904464
# 2025-10-24T13:20:35.904464
# 2025-11-23T16:22:50.904464
# 2026-08-05T12:10:15.904464
# 2025-10-09T04:51:44.904464
# 2025-08-09T02:14:17.904464
# 2026-01-05T22:31:45.904464
# 2026-06-19T16:33:50.904464
# 2026-04-15T00:30:47.904464
# 2026-02-05T16:20:29.904464
# 2026-04-25T07:59:13.904464
# 2025-12-11T12:43:19.904464
# 2026-05-06T09:22:23.904464
# 2025-09-30T08:20:17.904464
# 2025-12-04T04:51:20.904464
# 2026-05-05T22:34:51.904464
# 2025-12-11T12:55:50.904464
# 2025-10-16T05:19:16.904464
# 2025-11-27T05:13:27.904464
# 2025-10-22T20:33:05.904464
# 2026-07-28T08:25:12.904464
# 2025-11-05T12:01:51.904464
# 2026-06-16T04:07:31.904464
# 2026-07-27T04:48:02.904464
# 2025-12-13T22:12:38.904464
# 2025-08-19T17:55:03.904464
# 2026-06-02T06:44:07.904464
# 2026-04-15T17:01:24.904464
# 2026-02-25T02:30:57.904464
# 2025-08-10T10:51:26.904464
# 2026-02-14T13:26:50.904464
# 2025-08-22T10:38:52.904464
# 2026-01-09T14:59:39.904464
# 2026-07-11T16:04:43.904464
# 2026-01-27T16:05:35.904464
# 2026-06-04T13:17:56.904464
# 2025-12-30T08:29:52.904464
# 2026-04-14T01:30:18.904464
# 2025-10-12T05:29:09.904464
# 2026-08-06T23:37:21.904464
# 2025-10-23T07:45:29.904464
# 2026-06-23T12:04:02.904464
# 2025-12-05T00:58:24.904464
# 2026-04-28T04:21:38.904464
# 2026-05-19T05:09:22.904464
# 2025-09-13T16:44:27.904464
# 2026-07-16T13:04:44.904464
# 2026-04-11T07:08:14.904464
# 2025-12-18T21:18:28.904464
# 2025-10-11T17:48:32.904464
# 2025-11-05T01:54:56.904464
# 2026-02-15T21:03:11.904464
# 2026-02-08T13:53:45.904464
# 2026-03-25T06:49:56.904464
# 2025-10-16T22:16:16.904464
# 2026-04-07T02:34:42.904464
# 2026-07-23T05:32:06.904464
# 2026-05-03T09:22:53.904464
# 2026-06-07T21:05:43.904464
# 2025-11-01T00:10:00.904464
# 2025-12-24T09:08:03.904464
# 2026-07-25T06:35:22.904464
# 2025-10-01T15:25:39.904464
# 2026-03-07T22:43:16.904464
# 2026-05-14T19:21:58.904464
# 2026-03-18T22:39:09.904464
# 2026-08-04T18:52:05.904464
# 2026-01-09T10:16:10.904464
# 2026-06-13T13:03:41.904464
# 2026-07-28T22:21:34.904464
# 2025-12-04T10:46:38.904464
# 2026-05-27T08:10:04.904464
# 2026-06-25T19:07:18.904464
# 2026-02-21T10:59:44.904464
# 2025-10-16T14:31:08.904464
# 2026-03-25T04:57:35.904464
# 2026-07-23T22:28:34.904464
# 2025-10-18T07:00:15.904464
# 2025-12-21T00:44:59.904464
# 2025-08-25T15:01:02.904464
# 2025-12-15T00:24:27.904464
# 2026-02-01T21:46:14.904464
# 2026-05-02T10:05:47.904464
# 2026-06-10T04:32:03.904464
# 2026-05-13T15:53:01.904464
# 2025-10-09T22:57:14.904464
# 2025-12-14T08:16:24.904464
# 2025-09-14T08:36:42.904464
# 2026-04-02T14:27:46.904464
# 2026-04-26T00:57:18.904464
# 2026-01-15T14:30:31.904464
# 2025-11-18T18:46:25.904464
# 2025-08-16T03:17:53.904464
# 2026-04-15T05:54:20.904464
# 2025-08-18T16:33:21.904464
# 2025-11-04T04:28:38.904464
# 2026-07-31T13:13:45.904464
# 2025-12-22T02:39:52.904464
# 2026-03-12T04:37:43.904464
# 2026-07-23T18:22:56.904464
# 2026-04-06T12:36:14.904464

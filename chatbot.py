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

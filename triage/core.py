import json
import os
import re

import requests

DEFAULT_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-20b"

SYSTEM = """You are an automation engine for a small business inbox.
For each customer message return ONLY a JSON object with keys:
- category: one of "order", "quote", "support", "complaint", "spam", "other"
- urgency: "high" | "medium" | "low" (high = money at risk or an angry customer)
- reply: a short, polite draft reply (2-4 sentences) appropriate to the category
Output nothing outside the JSON object."""


def extract_json(text):
    """Pull the first balanced JSON object out of raw LLM output.

    Survives code fences, surrounding prose, and braces inside strings.
    """
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1).strip()

    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object in model output")

    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise ValueError("unbalanced JSON in model output")


def triage_message(message, api_key=None, model=None):
    key = api_key or os.environ["GROQ_API_KEY"]
    model = model or os.environ.get("GROQ_MODEL", DEFAULT_MODEL)
    r = requests.post(
        os.environ.get("LLM_BASE_URL", DEFAULT_URL),
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": message},
            ],
        },
        timeout=30,
    )
    r.raise_for_status()
    return extract_json(r.json()["choices"][0]["message"]["content"])

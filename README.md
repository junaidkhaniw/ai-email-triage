# AI Email Triage

AI-powered inbox automation: takes raw customer messages and turns them into
routed, actionable work — automatically.

For every incoming message it:

1. **Classifies** it with an LLM (order / quote / support / complaint / spam / other)
2. **Scores urgency** (high urgency = money at risk or angry customer)
3. **Drafts a reply** appropriate to the category
4. **Flags urgent ones** for an SMS-style alert channel

Built as the AI upgrade of a manual email-automation workflow: the same
trigger → process → route pattern, with the classification and drafting
handed to an LLM instead of hand-written rules.

## Flow

```
messages (CSV) ──> triage (Groq LLM, structured JSON out)
                      │
                      ├─> results.csv  (originals + category + urgency + reply draft)
                      └─> urgent rows ──> [SMS ALERT] channel (Twilio/WhatsApp-ready hook)
```

## Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env        # then paste your Groq API key into .env
python -m triage --in sample_leads.csv --out results.csv
```

Dry-run (no API calls):

```bash
python -m triage --in sample_leads.csv --dry-run
```

Self-check of the JSON parsing layer:

```bash
python tests\test_extract_json.py
```

## Swapping the LLM provider

Everything is OpenAI-compatible by default. Point `LLM_BASE_URL` at any
compatible endpoint (Groq, OpenRouter, OpenAI, local Ollama via
`http://localhost:11434/v1/chat/completions`) and set the matching key and
`GROQ_MODEL`.

## Design notes

- **Structured output by prompt, parsed defensively** — the model returns
  JSON, and `extract_json` survives code fences, surrounding prose, braces
  inside strings, and malformed output without crashing the batch.
- **One failed message never kills the run** — errors are recorded in the
  output row and the batch continues.
- **Alert channel is a seam, not a feature** — `alert()` prints today; wire
  Twilio/WhatsApp/email behind it without touching the pipeline.

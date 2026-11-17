import argparse
import csv
import sys

from dotenv import load_dotenv

from .core import triage_message


def alert(urgent_rows):
    # Seam for a real channel: wire Twilio/WhatsApp/email API here later.
    for r in urgent_rows:
        print(
            f"[SMS ALERT] -> {r.get('phone', '?')}: urgent {r.get('category', '?')} "
            f"from {r.get('name', '?')} - {r.get('message', '')[:60]}"
        )


def main():
    load_dotenv()
    ap = argparse.ArgumentParser(
        description="Classify customer messages with an LLM and draft replies."
    )
    ap.add_argument("--in", dest="inp", required=True, help="CSV with a 'message' column")
    ap.add_argument("--out", dest="out", default="results.csv")
    ap.add_argument("--dry-run", action="store_true", help="list messages without calling the LLM")
    a = ap.parse_args()

    with open(a.inp, encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("message") or "").strip()]
    if not rows:
        sys.exit("no messages found (CSV needs a 'message' column)")

    if a.dry_run:
        for i, r in enumerate(rows, 1):
            print(f"{i}. {r.get('name', '?')}: {r['message'][:70]}")
        return

    fields = list(rows[0].keys()) + ["category", "urgency", "reply"]
    out_rows, urgent = [], []
    for i, r in enumerate(rows, 1):
        print(f"[{i}/{len(rows)}] triaging: {r['message'][:50]}...")
        try:
            res = triage_message(r["message"])
        except Exception as e:  # one bad row must not kill the batch
            res = {"category": "error", "urgency": "low", "reply": f"triage failed: {e}"}
        out_rows.append({**r, **res})
        if res.get("urgency") == "high":
            urgent.append(out_rows[-1])

    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    alert(urgent)
    print(f"\nwrote {len(out_rows)} rows -> {a.out}; {len(urgent)} urgent flagged")


if __name__ == "__main__":
    main()

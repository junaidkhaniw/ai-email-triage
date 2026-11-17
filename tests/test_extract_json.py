import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from triage.core import extract_json


def check():
    cases = [
        ('{"category": "spam", "urgency": "low", "reply": "ignored"}', "spam"),
        ('Sure! ```json\n{"category": "quote", "urgency": "medium"}\n```', "quote"),
        ('Here you go: {"a": {"b": 1}, "c": 2} hope it helps', None),
        ('{"x": "brace in string } here"}', None),
    ]
    for text, cat in cases:
        got = extract_json(text)
        if cat is not None:
            assert got["category"] == cat, f"{text!r} -> {got}"

    assert extract_json('{"x": "brace in string } here"}')["x"] == "brace in string } here"
    assert extract_json('Here you go: {"a": {"b": 1}, "c": 2} hope it helps')["a"] == {"b": 1}

    for bad in ["no json here", "{oops", ""]:
        try:
            extract_json(bad)
            raise AssertionError(f"should have raised: {bad!r}")
        except ValueError:
            pass

    print("extract_json: all checks passed")


if __name__ == "__main__":
    check()

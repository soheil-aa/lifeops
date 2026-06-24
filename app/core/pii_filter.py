from __future__ import annotations

import re

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Phone: optional +, groups of digits separated by space/dash, 7+ digits total.
_PHONE = re.compile(r"\+?\d[\d\-\s]{6,}\d")
# Card/account-like: 12+ digits possibly space/dash separated.
_DIGITS = re.compile(r"\b(?:\d[ -]?){12,}\b")

_PATTERNS = [_EMAIL, _DIGITS, _PHONE]  # order matters: emails/cards before generic phone


def detect(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for pattern in _PATTERNS:
        for m in pattern.finditer(text):
            value = m.group(0).strip()
            if value and value not in seen:
                seen.add(value)
                found.append(value)
    return found


def contains_pii(text: str) -> bool:
    return len(detect(text)) > 0


def tokenize(text: str) -> tuple[str, dict[str, str]]:
    detected_values = detect(text)
    mapping: dict[str, str] = {}
    redacted = text

    # Sort by descending length to replace longer values first,
    # preventing substring corruption when one detected value is a substring of another.
    sorted_values = sorted(detected_values, key=len, reverse=True)

    # Assign placeholders in detect() order for consistency
    for i, value in enumerate(detected_values, start=1):
        placeholder = f"[[PII_{i}]]"
        mapping[placeholder] = value

    # Perform substitutions in descending length order
    for value in sorted_values:
        # Find the placeholder assigned to this value
        placeholder = next(k for k, v in mapping.items() if v == value)
        redacted = redacted.replace(value, placeholder)

    return redacted, mapping


def restore(text: str, mapping: dict[str, str]) -> str:
    restored = text
    for placeholder, value in mapping.items():
        restored = restored.replace(placeholder, value)
    return restored

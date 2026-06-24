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
    mapping: dict[str, str] = {}
    redacted = text
    for i, value in enumerate(detect(text), start=1):
        placeholder = f"[[PII_{i}]]"
        mapping[placeholder] = value
        redacted = redacted.replace(value, placeholder)
    return redacted, mapping


def restore(text: str, mapping: dict[str, str]) -> str:
    restored = text
    for placeholder, value in mapping.items():
        restored = restored.replace(placeholder, value)
    return restored

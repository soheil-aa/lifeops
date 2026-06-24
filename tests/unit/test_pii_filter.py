from app.core.pii_filter import detect, tokenize, restore, contains_pii


def test_detect_finds_email_and_phone():
    found = detect("ping me at jo@acme.com or 415-555-0199")
    assert any("@" in f for f in found)
    assert any("415" in f for f in found)


def test_detect_finds_long_digit_runs():
    found = detect("card 4111 1111 1111 1111 expires soon")
    assert any(f.replace(" ", "").isdigit() and len(f.replace(" ", "")) >= 12 for f in found)


def test_tokenize_then_restore_roundtrips():
    text = "email jo@acme.com about invoice"
    redacted, mapping = tokenize(text)
    assert "jo@acme.com" not in redacted
    assert "[[PII_" in redacted
    assert restore(redacted, mapping) == text


def test_contains_pii_true_and_false():
    assert contains_pii("reach me: a@b.com") is True
    assert contains_pii("let's meet tomorrow") is False

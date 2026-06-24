from app.core.token_broker import TokenBroker


def test_mint_binds_to_single_scope():
    broker = TokenBroker()
    tok = broker.mint("gmail.readonly")
    assert tok.scope == "gmail.readonly"
    assert broker.is_valid(tok)


def test_distinct_scopes_get_distinct_tokens():
    broker = TokenBroker()
    a = broker.mint("gmail.readonly")
    b = broker.mint("gmail.send")
    assert a.value != b.value


def test_revoke_invalidates():
    broker = TokenBroker()
    tok = broker.mint("gmail.send")
    broker.revoke(tok)
    assert broker.is_valid(tok) is False

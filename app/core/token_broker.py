from __future__ import annotations

import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    value: str
    scope: str


class TokenBroker:
    """Vends short-lived, single-scope tokens (JIT least-privilege).

    v1 local impl: opaque random tokens with in-memory revocation. Real
    OAuth/KMS-backed impls satisfy the same mint/revoke/is_valid interface.
    """

    def __init__(self) -> None:
        self._valid: set[str] = set()

    def mint(self, scope: str) -> Token:
        token = Token(value=secrets.token_urlsafe(24), scope=scope)
        self._valid.add(token.value)
        return token

    def revoke(self, token: Token) -> None:
        self._valid.discard(token.value)

    def is_valid(self, token: Token) -> bool:
        return token.value in self._valid

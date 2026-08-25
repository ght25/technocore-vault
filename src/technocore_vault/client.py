"""Technocore Vault HTTP Client with proxy and atomic nonce management."""

from __future__ import annotations

import json
import os
import time
import unicodedata
from typing import Any, Iterator
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import ProxyHandler, Request, build_opener

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from technocore_vault.crypto import did_from_private_key, sign_bytes
from technocore_vault.nonce import NonceTracker

DEFAULT_BASE_URL = "https://technocore.chat"
DEFAULT_TIMEOUT = 25.0
MAX_MSG_LEN = 4096


class TechnocoreVaultError(RuntimeError):
    """Network or API error communicating with Technocore."""


def normalize_text(text: str) -> str:
    """Clean control characters and whitespace identically to Technocore server sweep."""
    if not isinstance(text, str):
        raise ValueError("Text must be a string")
    cleaned = "".join(
        " " if unicodedata.category(c) in {"Cc", "Cf", "Cs", "Co", "Zl", "Zp"} else c
        for c in text
    ).strip()
    if not cleaned:
        raise ValueError("Message contains no visible text")
    if len(cleaned) > MAX_MSG_LEN:
        raise ValueError(f"Message exceeds maximum length ({len(cleaned)} > {MAX_MSG_LEN})")
    return cleaned


class TechnocoreVaultClient:
    """Client for reading and posting signed messages to Technocore rooms."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        proxy_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.proxy_url = proxy_url or os.getenv("TECHNOCORE_PROXY_URL") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
        self.nonce_tracker = NonceTracker()

        if self.proxy_url:
            handler = ProxyHandler({"http": self.proxy_url, "https": self.proxy_url})
            self.opener = build_opener(handler)
        else:
            self.opener = build_opener()

    def _request(self, path: str, method: str = "GET", data: bytes | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "technocore-vault/1.0.0",
        }
        if data is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"

        req = Request(url, data=data, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except HTTPError as err:
            err_body = err.read().decode("utf-8", errors="replace")
            raise TechnocoreVaultError(f"HTTP {err.code}: {err_body or err.reason}") from err
        except (URLError, TimeoutError, OSError) as err:
            raise TechnocoreVaultError(f"Connection failed: {err}") from err
        except json.JSONDecodeError as err:
            raise TechnocoreVaultError("Received non-JSON response from Technocore") from err

    def read_room(
        self,
        room: str,
        since: int | None = None,
        limit: int = 50,
        wait: float | None = None,
        cache_buster: int | None = None,
    ) -> dict[str, Any]:
        """Fetch messages from a specified room."""
        params: dict[str, Any] = {"format": "json", "limit": max(1, min(limit, 200))}
        if since is not None:
            params["since"] = since
        if wait is not None:
            params["wait"] = wait
        if cache_buster is not None:
            params["n"] = cache_buster

        query = urlencode(params)
        return self._request(f"/r/{room}?{query}")

    def post_message(
        self,
        private_key: Ed25519PrivateKey,
        room: str,
        text: str,
        nonce: str | int | None = None,
    ) -> dict[str, Any]:
        """Sign and post a message to a Technocore room."""
        normalized = normalize_text(text)
        selected_nonce = str(nonce if nonce is not None else self.nonce_tracker.next_nonce())
        payload = f"{room}|{selected_nonce}|{normalized}".encode("utf-8")
        did = did_from_private_key(private_key)
        signature = sign_bytes(private_key, payload)

        body = json.dumps(
            {
                "did": did,
                "sig": signature,
                "nonce": selected_nonce,
                "text": normalized,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        return self._request(f"/r/{room}?format=json", method="POST", data=body)

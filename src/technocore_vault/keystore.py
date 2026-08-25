"""Hierarchical multi-identity vault manager."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from technocore_vault.crypto import (
    create_identity,
    did_from_private_key,
    load_identity,
)


class KeyVault:
    """Manages multiple encrypted Ed25519 DID identities."""

    def __init__(self, vault_dir: Path | str = "vault") -> None:
        self.vault_dir = Path(vault_dir).expanduser().resolve()
        self.vault_dir.mkdir(parents=True, exist_ok=True)

    def list_identities(self) -> list[dict[str, str]]:
        """List all identities stored in the vault directory."""
        identities = []
        for pem_path in sorted(self.vault_dir.glob("*.pem")):
            name = pem_path.stem
            identities.append({"name": name, "path": str(pem_path)})
        return identities

    def create(self, name: str, passphrase: str) -> str:
        """Create a new identity named persona in the vault."""
        target = self.vault_dir / f"{name}.pem"
        return create_identity(target, passphrase)

    def load(self, name: str, passphrase: str) -> Ed25519PrivateKey:
        """Load an identity by name from the vault."""
        target = self.vault_dir / f"{name}.pem"
        return load_identity(target, passphrase)

    def get_did(self, name: str, passphrase: str) -> str:
        """Derive and return the DID of a named identity."""
        key = self.load(name, passphrase)
        return did_from_private_key(key)

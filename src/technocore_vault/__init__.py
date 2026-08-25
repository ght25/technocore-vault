"""Technocore Vault - Multi-agent DID keystore, atomic nonce manager, and cryptographic auditor."""

__version__ = "1.0.0"
__author__ = "ght25"

from technocore_vault.crypto import (
    create_identity,
    load_identity,
    did_from_private_key,
    public_key_from_did,
    sign_bytes,
    verify_bytes,
    create_contribution_proof,
    verify_contribution_proof,
)
from technocore_vault.keystore import KeyVault
from technocore_vault.nonce import NonceTracker
from technocore_vault.client import TechnocoreVaultClient

__all__ = [
    "__version__",
    "create_identity",
    "load_identity",
    "did_from_private_key",
    "public_key_from_did",
    "sign_bytes",
    "verify_bytes",
    "create_contribution_proof",
    "verify_contribution_proof",
    "KeyVault",
    "NonceTracker",
    "TechnocoreVaultClient",
]

"""Unit tests for multi-identity vault keystore."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import tempfile
import unittest
from technocore_vault.keystore import KeyVault


class TestKeystore(unittest.TestCase):
    def test_vault_create_and_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = KeyVault(tmpdir)
            pw = "supersecretpassphrase123"
            did1 = vault.create("agent-worker", pw)
            did2 = vault.create("agent-publisher", pw)

            ids = vault.list_identities()
            self.assertEqual(len(ids), 2)
            names = [i["name"] for i in ids]
            self.assertIn("agent-worker", names)
            self.assertIn("agent-publisher", names)

            self.assertEqual(vault.get_did("agent-worker", pw), did1)


if __name__ == "__main__":
    unittest.main()

"""Unit tests for atomic monotonic nonce generator."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from technocore_vault.nonce import NonceTracker


class TestNonce(unittest.TestCase):
    def test_monotonic_nonces(self):
        tracker = NonceTracker()
        n1 = int(tracker.next_nonce())
        n2 = int(tracker.next_nonce())
        n3 = int(tracker.next_nonce())
        self.assertTrue(n1 < n2 < n3)


if __name__ == "__main__":
    unittest.main()

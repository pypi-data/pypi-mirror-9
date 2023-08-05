from unittest import TestCase
from mock import MagicMock

import shuttle.sync


class TestTxSync(TestCase):

    def test_sync_accepts_tx(self):
        """TxSync should accept the Tx object as a parameter."""

        tx = MagicMock()

        sync = shuttle.sync.TxSync(transifex=tx)
        self.assertEqual(sync.tx, tx)

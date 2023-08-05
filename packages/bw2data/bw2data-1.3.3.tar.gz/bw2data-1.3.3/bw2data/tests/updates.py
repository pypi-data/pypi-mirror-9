# -*- coding: utf-8 -*-
from . import BW2DataTest
from .. import Updates, config
import random

class UpdatesTest(BW2DataTest):
    def test_set_updates_clean_install(self):
        self.assertFalse('updates' in config.p)
        self.assertFalse(Updates.check_status())
        self.assertEqual(
            len(config.p['updates']),
            len(Updates.UPDATES)
        )

    def test_explain(self):
        key = random.choice(Updates.UPDATES.keys())
        self.assertEqual(
            Updates.UPDATES[key]['explanation'],
            Updates.explain(key)
        )

    def test_do_updates(self):
        # Test with mock that overwrites UPDATES?
        pass

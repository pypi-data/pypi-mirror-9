import os
import logging
import time
import types

try:
    import unittest.mock as mock
except ImportError:
    import mock
import json
import os
from unittest import TestCase

from tweeply import utils
from tweeply import defaults 

class TestMisc(TestCase):

    def test_config(self):
        """
        The main task starts, spawns the appropriate workers, and finishes cleanly.
        """
        config = {}
        config = utils.generic_update_config(config)
        assert config == {}
        config = utils.update_config(config, cfgfiles=[])
        assert config == defaults.DEFAULTS
        config = utils.update_config(config,
                                     defaults=defaults.DEFAULTS,
                                     cfgfiles=["/dev/null",])
        assert config == defaults.DEFAULTS
        config = {}
        TEST_DEFAULTS = {"TWEEPLY": {"nested": True}}
        TEST_FILE = "{}/config-test.json".format(os.path.dirname(__file__))
        logging.debug("TEST_FILE %s", TEST_FILE)
        config = utils.update_config(config,
                                     defaults=TEST_DEFAULTS,
                                     cfgfiles=[TEST_FILE,])
        assert config == {"TWEEPLY": "NOTHING", "HTTP": "NOTHING", "and": "test" }

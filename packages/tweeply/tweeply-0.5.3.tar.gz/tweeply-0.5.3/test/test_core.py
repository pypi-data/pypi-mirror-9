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

from tweeply import Tweeply, Stream, TweeplyClient, TweeplyMessage

class TestServer(TestCase):

    def test_tweeply(self):
        """
        The main task starts, spawns the appropriate workers, and finishes cleanly.
        """
        tweeply = Tweeply(name="Tweeply")
        tweeply.setDaemon(False)
        workers = [mock.Mock()]
        tweeply.workers = workers
        tweeply.start()
        tweeply.stop()
        tweeply.join()
        assert workers[0].start.called
        assert workers[0].stop.called


class TestClient(TestCase):
    @mock.patch.object(TweeplyClient, "receive_generic")
    @mock.patch.object(TweeplyClient, "send_generic")
    def test_client(self, send, receive):
        response = TweeplyMessage()
        response.payload = "restpayload"
        response.collection = "testing"
        response.multipart = False
        receive.return_value = response
        c = TweeplyClient()
        res = c.rest.get_some_method()
        assert res == "restpayload"
        response.payload = "stream"
        response.multipart = True
        gen = c.stream.sample(tweeply_timeout=0, tweeply_polling=0)
        assert isinstance(gen, types.GeneratorType)
        response.multipart = True
        response.code = 100
        response.payload = "stream0"
        assert gen.next() == "stream0"
        response.payload = "stream1"
        assert gen.next() == "stream1"
        response.code = 203
        self.assertRaises(StopIteration, gen.next)

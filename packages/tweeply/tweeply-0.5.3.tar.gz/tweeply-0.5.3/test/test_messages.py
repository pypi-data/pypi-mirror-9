import os
import logging
import time
from copy import copy

try:
    import unittest.mock as mock
except ImportError:
    import mock
import json
import os
from unittest import TestCase

from tweeply import TweeplyMessage, ClientMessage

class TestMessages(TestCase):
    
    def test_message(self):
        """
        Generic Messages should be of the form:
          { "code": 200,
            "thread": None,
            "multipart": False,
            "msgid": -1,
            "payload": None,
            "collection": None,
            "stimestamp": None,
            "rtimestamp": None}
        """
        m = TweeplyMessage()
        reference_message = {"code": 200,
                             "thread": None,
                             "multipart": False,
                             "msgid": -1,
                             "payload": None,
                             "collection": None,
                             "stimestamp": None,
                             "rtimestamp": None}
        assert m == reference_message 
        
        intext = m.to_json()
        recovered = TweeplyMessage.from_raw([intext])
        assert recovered == reference_message

    def test_serialise_message(self):
        pass


    def test_client(self):
        """
        Client Messages should be of the form:
          { "code": 200,
            "thread": None,
            "multipart": False,
            "msgid": -1,
            "payload": {
                "fname": [],
                "args": [],
                "kwargs": {}
            },
            "collection": None,
            "stimestamp": None,
            "rtimestamp": None}
        """
        m = ClientMessage()
        reference_client = { "code": 200,
                             "thread": None,
                             "multipart": False,
                             "msgid": -1,
                             "payload": {
                                 "fname": [],
                                 "kwargs": {},
                                 "args": []},
                             "collection": None,
                             "stimestamp": None,
                             "rtimestamp": None }
        assert m.to_dict() == reference_client
        m.fname = ["foo"]
        m.args = [0,1,2]
        m.kwargs["fourth"] = 3
        reference_client["payload"] = {"fname": ["foo"], "args": [0,1,2], "kwargs": {"fourth": 3}}
        assert m == reference_client

        intext = m.to_json()
        recovered = TweeplyMessage.from_raw([intext])
        assert recovered == reference_client

    def test_copy_server(self):
        """ When copied, a message should return a message """
        m = TweeplyMessage()
        cm = m.copy()
        assert isinstance(cm, TweeplyMessage)
        assert cm == m
        cm2 = copy(m)
        assert isinstance(cm2, TweeplyMessage)
        assert cm2 == m


    def test_copy_client(self):
        """ When copied, a message should return a message """
        m = ClientMessage()
        cm = m.copy()
        assert isinstance(cm, ClientMessage)
        assert cm == m
        cm2 = copy(m)
        assert isinstance(cm2, ClientMessage)
        assert cm2 == m

    def test_reply(self):
        m = ClientMessage()
        r = m.buildReply("test")
        assert r.payload == "test"

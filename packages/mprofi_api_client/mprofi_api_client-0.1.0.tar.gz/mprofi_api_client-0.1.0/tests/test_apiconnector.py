#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_mprofi_api_client
----------------------------------

Tests for `mprofi_api_client` module.
"""

import unittest

from mprofi_api_client import MprofiAPIConnector

from .utils import FakeSession


class Testmprofi_api_client(unittest.TestCase):

    def setUp(self):
        self.connector = MprofiAPIConnector(api_token="abcd")
        self.connector.session = FakeSession()

    def test_posting_single(self):
        test_recipient = '123 234 456'
        test_message = "test message"
        test_ref = 'test_ref'
        self.connector.add_message(test_recipient, test_message)
        self.connector.send(test_ref)
        assert self.connector.session.json == (
            '{{"message": "{0}", "recipient": "{1}", "reference": "{2}"}}'.format(
                test_message,
                test_recipient,
                test_ref
            )
        )

    def test_posting_multiple(self):
        test_recipient = '123 234 456'
        test_message = "test message"
        test_ref = 'test_ref'
        self.connector.add_message(test_recipient, test_message)
        self.connector.add_message(test_recipient, test_message)
        self.connector.add_message(test_recipient, test_message)
        self.connector.send(test_ref)
        assert self.connector.session.json == (
            '{{"messages": [{{"message": "{0}", "recipient": "{1}"}}, '
            '{{"message": "{0}", "recipient": "{1}"}}, '
            '{{"message": "{0}", "recipient": "{1}"}}], '
            '"reference": "{2}"}}'.format(test_message,
                test_recipient,
                test_ref)
        )

if __name__ == '__main__':
    unittest.main()
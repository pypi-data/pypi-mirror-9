# coding=utf-8

import unittest
from whois.whois import NICClient


class TestNICClient(unittest.TestCase):
    def setUp(self):
        self.client = NICClient()

    def test_choose_server(self):
        domain = 'рнидс.срб'
        chosen = self.client.choose_server(domain)
        self.assertEqual(
            chosen,
            'срб'.decode('utf-8').encode('idna') + '.whois-servers.net'
        )

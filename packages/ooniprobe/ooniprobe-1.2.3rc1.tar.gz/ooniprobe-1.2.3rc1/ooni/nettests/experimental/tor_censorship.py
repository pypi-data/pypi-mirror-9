from twisted.internet import reactor

from ooni.templates import tcpt
from ooni.templates import httpt

# class TorWebsiteTest(httpt.HTTPTest):
#     inputs = [
#         'http://blog.torproject.org/',
#         'http://trac.torproject.org/',
#         'http://bridges.torproject.org/',
#         'http://torproject.org/',
#     ]
#
#     name = 'tor_website_test'
#
#     def test_website_censorship(self):
#         return self.doRequest(self.input)
#


class TorConnectionTest(tcpt.TCPTest):
    name = 'tor_connect'

    inputs = [
        '8.8.8.8:53',
        '127.0.0.1:2838'
    ]

    def setUp(self):
        self.address, self.port = self.input.split(':')
        self.port = int(self.port)

    def test_connect_to_relay(self):
        return self.connect()

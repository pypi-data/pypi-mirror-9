# -*- encoding: utf-8 -*-
import random

from twisted.python import usage
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint

from twisted.internet.error import ConnectionRefusedError
from twisted.internet.error import TCPTimedOutError, TimeoutError

from ooni.templates import tcpt
from ooni.errors import handleAllFailures
from ooni.utils import log, randomStr


class TCPFactory(Factory):

    def buildProtocol(self, addr):
        return Protocol()


class UsageOptions(usage.Options):
    optParameters = [
        ['backend', 'b', None,
         'Backend to connect to that binds to the 100 most common ports']
    ]


class TopPortsTest(tcpt.TCPTest):
    name = "Top ports"
    description = "This test will verify if it can connect to the 100 most common ports"
    author = "Arturo Filastò"
    version = "0.1"

    usageOptions = UsageOptions

    # These are the top 100 most probably open ports according to
    # https://svn.nmap.org/nmap/nmap-services
    inputs = [80, 23, 443, 21, 22, 25, 3389, 110, 445, 139,
              143, 53, 135, 3306, 8080, 1723, 111, 995, 993,
              5900, 1025, 587, 8888, 199, 1720, 465, 548, 113,
              81, 6001, 10000, 514, 5060, 179, 1026, 2000,
              8443, 8000, 32768, 554, 26, 1433, 49152, 2001,
              515, 8008, 49154, 1027, 5666, 646, 5000, 5631,
              631, 49153, 8081, 2049, 88, 79, 5800, 106, 2121,
              1110, 49155, 6000, 513, 990, 5357, 427, 49156,
              543, 544, 5101, 144, 7, 389, 8009, 3128, 444,
              9999, 5009, 7070, 5190, 3000, 5432, 3986, 1900,
              13, 1029, 9, 6646, 5051, 49157, 1028, 873, 1755,
              2717, 4899, 9100, 119, 37]

    requiredTestHelpers = {'backend': 'top-ports'}
    requiredOptions = ['backend']
    requiresTor = False
    requiresRoot = False

    def setUp(self):
        self.address = self.localOptions['backend']
        self.port = self.input

    def test_connect(self):
        """
        This test performs a TCP connection to the remote host on the specified port.
        the report will contains the string 'success' if the test has
        succeeded, or the reason for the failure if it has failed.
        """
        payload = randomStr(42)
        self.report['response_match'] = None
        d = self.sendPayload(payload)

        @d.addCallback
        def cb(result):
            self.report['response_match'] = False
            if result == payload:
                self.report['response_match'] = True
        return d

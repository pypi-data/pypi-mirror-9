from twisted.python import usage
from urlparse import urlsplit

from ooni.templates import dnst, httpt


class UsageOptions(usage.Options):
    optParameters = [
        ['resolver', 'r', '8.8.8.8',
            'Specify the DNS resolver to use for DNS queries'],
    ]


class DNSnHTTP(dnst.DNSTest, httpt.HTTPTest):
    inputFile = ["filename", "f", None,
                 "file containing urls to test for blocking."]

    usageOptions = UsageOptions
    name = 'DNS n HTTP'
    version = '0.1'

    def test_http(self):
        return self.doRequest(self.input)

    def test_dns(self):
        hostname = urlsplit(self.input)[1]
        return self.performALookup(hostname)

from __future__ import print_function
from twisted.internet import protocol, reactor, endpoints


class Echo(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)


class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

endpoints.serverFromString(reactor, "onion:1234").listen(EchoFactory()).addCallback(lambda x: print(x.getHost()))
reactor.run()

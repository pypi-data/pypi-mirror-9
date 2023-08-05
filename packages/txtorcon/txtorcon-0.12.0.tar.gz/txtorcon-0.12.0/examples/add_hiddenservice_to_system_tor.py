#!/usr/bin/env python

# This connects to the system Tor (by default on control port 9151)
# and adds a new hidden service configuration to it.

import os
import functools
import shutil

from twisted.internet import reactor, defer
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.web import server, resource
from twisted.internet.task import react

import txtorcon


class Simple(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        return "<html>Hello, world! I'm a hidden service!</html>"


def setup_complete(config, proto):
    print "Protocol completed"

    onion_address = config.HiddenServices[0].hostname

    print "I have a hidden (web) service running at:"
    print "http://%s (port %d)" % (onion_address, hs_public_port)
    print "The temporary directory for it is at:", config.HiddenServices[0].dir
    print
    print "For example, you should be able to visit it via:"
    print "  torsocks lynx http://%s" % onion_address


def setup_failed(arg):
    print "SETUP FAILED", arg
    reactor.stop()

hs_port = 9876
hs_public_port = 80
hs_temp = os.path.realpath('/tmp/blam')


@defer.inlineCallbacks
def main(reactor):
    # Connect to the system Tor. Since we leave the
    # "build_state=True" default, this callbacks with a TorState
    # object. Otherwise, it would be a TorControlProtocol object.
    ep = TCP4ClientEndpoint(reactor, "localhost", 9051)
    state = yield txtorcon.build_tor_connection(ep)

    config = txtorcon.TorConfig(state.protocol)
    yield config.post_bootstrap
    hs_string = '%s 127.0.0.1:%d' % (hs_public_port, hs_port)
    hs = txtorcon.HiddenService(config, hs_temp, [hs_string])
    config.HiddenServices.append(hs)

    print config.create_torrc()
    yield config.save()

    print "blam! we have a thing at:", hs.hostname

# we set up our service to listen on hs_port which is forwarded (via
# the HiddenService options) from the hidden service address on port
# hs_public_port. Note that this could be done externally to this
# whole process; there's no requirement to be listening before Tor
# does.
site = server.Site(Simple())
hs_endpoint = TCP4ServerEndpoint(reactor, hs_port, interface='127.0.0.1')
hs_endpoint.listen(site)

# run the reactor main loop until the last callback from main() fires
react(main)

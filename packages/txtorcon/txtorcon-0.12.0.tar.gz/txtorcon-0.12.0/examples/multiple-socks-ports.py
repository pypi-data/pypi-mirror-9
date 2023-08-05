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


def setup_failed(arg):
    print "SETUP FAILED", arg
    reactor.stop()


@defer.inlineCallbacks
def main(reactor):
    # Connect to the system Tor. Since we leave the
    # "build_state=True" default, this callbacks with a TorState
    # object. Otherwise, it would be a TorControlProtocol object.
    ep = TCP4ClientEndpoint(reactor, "localhost", 9051)
    state = yield txtorcon.build_tor_connection(ep)

    config = txtorcon.TorConfig(state.protocol)
    yield config.post_bootstrap

    if False:
        config.socksport = [5432, 4321]
    else:
        config.socksport.append(5555)
        config.socksport.append(4444)
    yield config.save()

# run the reactor main loop until the last callback from main() fires
react(main)

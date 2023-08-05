#!/usr/bin/env python

import cProfile
import txtorcon

proto = txtorcon.TorControlProtocol()
state = txtorcon.TorState(proto)

data = open('consensus', 'r').read()
#cProfile.run('state._update_network_status(data)')
state._update_network_status(data)

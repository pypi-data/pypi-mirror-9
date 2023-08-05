#!/usr/bin/env python

# playing around with some ideas as far as bwauth (inside TorFlow)
# works, and the path-selection stuff from TorCtl which has been
# mentioned as a desireable txtorcon feature.

import random
from functools import partial
from twisted.internet import defer
from twisted.internet import task
import txtorcon


def node_selector(routers,  # torstate,
                  node_filter=lambda x: True,
                  chooser=random.choice):
    nodes = filter(node_filter, routers)
    if len(nodes) == 0:
        raise RuntimeError("No nodes left after filtering.")
    return chooser(nodes)


def flag_filter(flag, router):
    return flag in router.flags


def cmp_bandwidth(router_a, router_b):
    return cmp(router_a.bandwidth, router_b.bandwidth)

guard_filter = partial(flag_filter, 'guard')
exit_filter = partial(flag_filter, 'exit')


def percent_filter(torstate, min_pct, max_pct):
    if min_pct <= 0.0:
        raise RuntimeError("Minimum is too low")
    if max_pct >= 100.0:
        raise RuntimeError("Maximum is too high")

    def actual_filter(router):
        return


def create_paths(routers):
    '''
    This is a generator that produces paths the way Tor does: with a
    single guard node, a single middle node and a single exit
    node.

    Every time the generator runs it returns a tuple of Router
    instances representing the chosen path.

    FIXME need to consider when underlying router list
    changes. e.g. between any iteration it's possible all our cached
    data became stale...
    '''

    guard_selector = lambda: node_selector(routers, node_filter=guard_filter)
    middle_selector = lambda: node_selector(routers)
    exit_selector = lambda: node_selector(routers, node_filter=exit_filter)
    while True:
        yield (guard_selector(), middle_selector(), exit_selector())


@defer.inlineCallbacks
def main(reactor):
    state = yield txtorcon.build_local_tor_connection(reactor)
    yield state.post_bootstrap

    # make a generator for selecting from any possible router
    g = create_paths(state.all_routers)
    for i in range(10):
        path = g.next()
        print map(lambda r: r.name, path)

    # same, except we limit the routers to the top N% fastest ones in
    # each category: guard, middle, exit
    guards = filter(guard_filter, torstate.all_routers).sort(key=lambda x: x.bandwidth)
    middles = list(torstate.all_routers).sort(key=lambda x: x.bandwidth)
    exits = filter(exit_filter, torstate.all_routers).sort(key=lambda x: x.bandwidth)

    print len(routers_by_bandwidth), "routers"
    percent = 10.0
    top_n = int((percent / 100.0) * len(routers_by_bandwidth))
    g = create_paths(routers_by_bandwidth[:top_n])
    for i in range(10):
        path = g.next()
        print map(lambda r: r.name, path)

task.react(main)

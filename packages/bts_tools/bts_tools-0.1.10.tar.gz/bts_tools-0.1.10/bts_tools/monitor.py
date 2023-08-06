#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# bts_tools - Tools to easily manage the bitshares client
# Copyright (c) 2014 Nicolas Wack <wackou@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from collections import deque, defaultdict
from datetime import datetime
from itertools import chain, islice
from .core import StatsFrame
from .notification import send_notification
from .feeds import check_feeds
from . import core, monitoring
import math
import time
import logging

log = logging.getLogger(__name__)

# needs to be accessible at a module level (at least for now)
stats_frames = {}

# make sure we don't have huge plots that take forever to render
maxlen = 2000

cfg = None
time_span = None
time_interval = None
stable_time_interval = None
desired_maxlen = None


def load_monitoring():
    global cfg, time_span, time_interval, desired_maxlen, stable_time_interval
    cfg = core.config['monitoring']
    time_span = cfg['plots_time_span']
    time_interval = cfg['monitor_time_interval']
    desired_maxlen = int(time_span / time_interval)

    if desired_maxlen > maxlen:
        stable_time_interval = time_interval * (desired_maxlen / maxlen)
    else:
        stable_time_interval = time_interval


class AttributeDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class StableStateMonitor(object):
    """Monitor a sequence of states, and is able to compute a "stable" state value when N
    consecutive same states have happened.
    For example, we only want to decide the client is offline after 3 consecutive 'offline' states
    to absorb transient errors and avoid reacting too fast on wrong alerts.
    """
    def __init__(self, n):
        self.n = n
        self.states = deque(maxlen=n+1)
        self.last_stable_state = None

    def push(self, state):
        stable_state = self.stable_state()
        if stable_state is not None:
            self.last_stable_state = stable_state
        self.states.append(state)

    def stable_state(self):
        size = len(self.states)
        if size < self.n:
            return None
        last_state = self.states[-1]
        if all(state == last_state for state in islice(self.states, size-self.n, size)):
            return last_state
        return None

    def just_changed(self):
        stable_state = self.stable_state()
        if stable_state is None or self.last_stable_state is None:
            return False
        return stable_state != self.last_stable_state


def monitoring_thread(*nodes):
    client_node = nodes[0]

    # all different types of monitoring that should be considered by this thread
    all_monitoring = set(chain(*(node.monitoring for node in nodes)))
    node_names = [n.name for n in nodes]

    log.info('Starting thread monitoring on %s:%d for nodes %s' %
             (client_node.rpc_host, client_node.rpc_port, ', '.join(node_names)))

    stats = stats_frames[client_node.rpc_cache_key] = deque(maxlen=min(desired_maxlen, maxlen))

    # launch feed monitoring and publishing thread
    if 'feeds' in all_monitoring:
        check_feeds(nodes)

    # create one global context for the client, and local contexts for each node of this client
    global_ctx = AttributeDict(loop_index=0,
                               time_interval=time_interval,
                               stable_time_interval=stable_time_interval,
                               nodes=nodes,
                               node_names=node_names,
                               stats=stats,
                               online_state=StableStateMonitor(3),
                               connection_state=StableStateMonitor(3))
    contexts = {}
    for node in nodes:
        ctx = AttributeDict(producing_state=StableStateMonitor(3),
                            last_n_notified=0)
        contexts[node.name] = ctx

    while True:
        global_ctx.loop_index += 1

        time.sleep(time_interval)
        # log.debug('-------- Monitoring status of the BitShares client --------')
        client_node.clear_rpc_cache()

        try:
            online = monitoring.online.monitor(client_node, global_ctx)
            if not online:
                continue

            info = client_node.get_info()
            global_ctx.info = info

            if client_node.type == 'seed':
                monitoring.seed.monitor(client_node, global_ctx)

            monitoring.network_connections.monitor(client_node, global_ctx)
            monitoring.resources.monitor(client_node, global_ctx)

            # monitor each node
            for node in nodes:
                ctx = contexts[node.name]
                ctx.info = info
                ctx.online_state = global_ctx.online_state
                monitoring.missed.monitor(node, ctx)
                monitoring.version.monitor(node, ctx)
                monitoring.payroll.monitor(node, ctx)


        except Exception as e:
            log.error('An exception occurred in the monitoring thread:')
            log.exception(e)

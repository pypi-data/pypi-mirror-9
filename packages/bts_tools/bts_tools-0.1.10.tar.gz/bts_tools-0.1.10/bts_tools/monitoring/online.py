#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# bts_tools - Tools to easily manage the bitshares client
# Copyright (c) 2015 Nicolas Wack <wackou@gmail.com>
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

from ..notification import send_notification
from ..core import StatsFrame
from datetime import datetime
import logging

log = logging.getLogger(__name__)


def monitor(node, ctx):
    if not node.is_online():
        log.debug('Nodes %s: offline' % ctx.node_names)
        ctx.online_state.push('offline')

        if ctx.online_state.just_changed():
            log.warning('Nodes %s just went offline...' % ctx.node_names)
            send_notification(ctx.nodes, 'node just went offline...', alert=True)

        ctx.stats.append(StatsFrame(cpu=0, mem=0, connections=0, timestamp=datetime.utcnow()))
        return False

    log.debug('Nodes %s: online' % ctx.node_names)
    ctx.online_state.push('online')

    if ctx.online_state.just_changed():
        log.info('Nodes %s just came online!' % ctx.node_names)
        send_notification(ctx.nodes, 'node just came online!')

    return True

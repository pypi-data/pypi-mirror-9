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

from os.path import join, dirname, expanduser, exists, abspath
from collections import namedtuple
from subprocess import Popen, PIPE
from functools import wraps
import sys
import os
import shutil
import yaml
import time
import logging

log = logging.getLogger(__name__)

platform = sys.platform
if platform.startswith('linux'):
    platform = 'linux'

HERE = abspath(dirname(__file__))
BTS_TOOLS_HOMEDIR = '~/.bts_tools'
BTS_TOOLS_HOMEDIR = expanduser(BTS_TOOLS_HOMEDIR)
BTS_TOOLS_CONFIG_FILE = join(BTS_TOOLS_HOMEDIR, 'config.yaml')

config = None

def load_config(loglevels=None):
    log.info('Using home dir for BTS tools: %s' % BTS_TOOLS_HOMEDIR)
    global config
    if not exists(BTS_TOOLS_CONFIG_FILE):
        log.info('Copying default config file to %s' % BTS_TOOLS_CONFIG_FILE)
        try:
            os.makedirs(BTS_TOOLS_HOMEDIR)
        except OSError:
            pass
        shutil.copyfile(join(dirname(__file__), 'config.yaml'),
                        BTS_TOOLS_CONFIG_FILE)

    try:
        log.info('Loading config file: %s' % BTS_TOOLS_CONFIG_FILE)
        config_contents = open(BTS_TOOLS_CONFIG_FILE).read()
    except:
        log.error('Could not read config file: %s' % BTS_TOOLS_CONFIG_FILE)
        raise

    try:
        config = yaml.load(config_contents)
    except:
        log.error('-'*100)
        log.error('Config file contents is not a valid YAML object:')
        log.error(config_contents)
        log.error('-'*100)
        raise

    # setup given logging levels, otherwise from config file
    loglevels = loglevels or config.get('logging', {})
    for name, level in loglevels.items():
        logging.getLogger(name).setLevel(getattr(logging, level))


    # check whether config.yaml has a correct format
    errors = []
    m = config['monitoring']

    if 'email' in m:
        errors.append("'email' subsection of 'monitoring' should be moved to a 'notification' section instead")

    if 'boxcar' in m:
        errors.append("'boxcar' subsection of 'monitoring' should be moved to a 'notification' section instead")

    if 'cpu_ram_usage' not in m:
        errors.append("the 'monitoring' section should have a 'cpu_ram_usage' configuration entry")

    for node in config['nodes']:
        for notification_type in ['email', 'boxcar']:
            if notification_type in node.get('monitoring', []):
                errors.append("node '%s' has '%s' in its 'monitoring' section, it should be moved to a 'notification' property instead" %
                              (node['name'], notification_type))

    if errors:
        log.error('Invalid config.yaml file. The following errors have been found:')
        for err in errors:
            log.error('* %s' % err)
        log.error('File is located at: %s' % BTS_TOOLS_CONFIG_FILE)
        log.error('Please edit this file or delete it and let the tools create a new default one (run "bts list", for instance).')
        log.error('Note that some monitoring functionality now needs to be specified explicitly (seed, missed, network_connections)')
        log.error('Visit http://bts-tools.readthedocs.org/en/latest/config_format.html#nodes-list for more information).')
        sys.exit(1)

    return config


DEFAULT_HOMEDIRS = {'development': {'linux': '~/.BitSharesXTS',
                                    'darwin': '~/Library/Application Support/BitShares XTS'},
                    'bts':         {'linux': '~/.BitShares',
                                    'darwin': '~/Library/Application Support/BitShares'},
                    'dvs':         {'linux': '~/.DevShares',
                                    'darwin': '~/Library/Application Support/DevShares'},
                    'pts':         {'linux': '~/.PTS',
                                    'darwin': '~/Library/Application Support/PTS'},
                    'pls':         {'linux': '~/.DAC PLAY',
                                    'darwin': '~/Library/Application Support/DAC PLAY'}
                    }


def get_data_dir(env):
    try:
        env = config['run_environments'][env]
    except KeyError:
        log.error('Unknown run environment: %s' % env)
        sys.exit(1)

    data_dir = env.get('data_dir') or DEFAULT_HOMEDIRS.get(env['type'], {}).get(platform)
    return expanduser(data_dir) if data_dir else None

def get_bin_name(env):
    try:
        env = config['run_environments'][env]
    except KeyError:
        log.error('Unknown run environment: %s' % env)
        sys.exit(1)

    build_env = env['type']
    try:
        build_env = config['build_environments'][build_env]
    except KeyError:
        log.error('Unknown build environment: %s' % build_env)
        sys.exit(1)

    return build_env['bin_name']


IOStream = namedtuple('IOStream', 'status, stdout, stderr')
GlobalStatsFrame = namedtuple('GlobalStatsFrame', 'cpu_total, timestamp')
StatsFrame = namedtuple('StatsFrame', 'cpu, mem, connections, timestamp')


def _run(cmd, io=False, verbose=False):
    if isinstance(cmd, list):
        if len(cmd) > 1: # if we have args, quote them properly
            cmd = cmd[0] + ' "' + '" "'.join(cmd[1:]) + '"'
        else:
            cmd = cmd[0]

    (log.info if verbose else log.debug)('SHELL: running command: %s' % cmd)

    if io:
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if sys.version_info[0] >= 3:
            stdout, stderr = (str(stdout, encoding='utf-8'),
                              str(stderr, encoding='utf-8'))
        return IOStream(p.returncode, stdout, stderr)

    else:
        p = Popen(cmd, shell=True)
        p.communicate()
        return IOStream(p.returncode, None, None)


def run(cmd, io=False, verbose=True):
    r = _run(cmd, io, verbose)
    if r.status != 0:
        raise RuntimeError('Failed running: %s' % cmd)
    return r


def get_version():
    version_file = join(HERE, 'version.txt')
    if exists(version_file):
        with open(version_file) as f:
            return f.read().strip()
    try:
        return run('git describe --tags', io=True, verbose=False).stdout.strip()
    except Exception:
        return 'unknown'

VERSION = get_version()


class UnauthorizedError(Exception):
    pass


class RPCError(Exception):
    pass


class NoFeedData(Exception):
    pass


def profile(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        plog = logging.getLogger('bts_tools.profile')

        args_str = ', '.join(str(arg) for arg in args)
        if kwargs:
            args_str + ', ' + ', '.join('%s=%s' % (k, v) for k, v in kwargs.items())

        try:
            start_time = time.time()
            result = f(*args, **kwargs)
            stop_time = time.time()
            plog.debug('Function %s(%s): returned in %0.3f ms' % (f.__name__, args_str, (stop_time-start_time)*1000))
            return result
        except Exception:
            stop_time = time.time()
            plog.debug('Function %s(%s): exception in %0.3f ms' % (f.__name__, args_str, (stop_time-start_time)*1000))
            raise
    return wrapper

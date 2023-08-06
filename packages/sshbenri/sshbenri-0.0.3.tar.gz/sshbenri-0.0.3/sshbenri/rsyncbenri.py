#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

u"""
rsyncbenri
=============

"""

import argcomplete
from argparse import ArgumentParser
import os
import sys
from . import core
from .core import (loadconfig, parsecsv)

def createcommand(hosts, srcpath, destpath, config={}, rsyncopt='', sshopts=''):
    """
    create rsync command

    Arguments:
      hosts(list): list of host names
      srcpath(str): local path
      destpath(str): remote path
      config(dict): setting
      rsyncopt(str): rsync option
      sshopt(str): ssh option


    Example::

    >>> createcommand(['gw', 'host'], './local/', '~/remote/')
    u"rsync -e 'ssh -t -A gw ssh' -rv ./local/ host:'~/remote/'"
    """
    common_options = ['-t', '-A']
    if sshopts:
        common_options += sshopts.split()

    hosts = core.expandhosts(hosts, config)
    if not hosts: return
    opts = ['-rv']
    if rsyncopt:
        opts.append(rsyncopt)

    if len(hosts)>1:
        commands = core.createssh(hosts[:-1], common_options, config)
        executecommand = core.quotecommands(commands)
        quoteescape = core.escape_quote(executecommand, 0)
        opts.append("-e '{sshcomd} ssh'".format(sshcomd=quoteescape))

    depth = len(hosts)
    dest  = "'{}'".format(core.escape(destpath, depth-1))
    cmds = ['rsync']
    cmds += opts
    cmds += [srcpath, "{host}:{destpath}".format(host=hosts[-1], destpath=dest)]
    cmd = " ".join(cmds)
    return cmd

def executersync(hosts, srcpath, destpath, config={}, dryrun=False, rsyncopt='', sshopts='', syncproxy=False):
    """
    create and execute rsync command

    Arguments:
      hosts(list): list of host names
      srcpath(str): local path
      destpath(str): remote path
      config(dict): setting
      dryrun(bool): if True, does not execute command
      rsyncopt(str): rsync option
      sshopt(str): ssh option
    """
    if not os.path.exists(os.path.expanduser(srcpath)):
        sys.stderr("warning: {} does not exists\n".format(srcpath))

    cmd = createcommand(hosts, srcpath, destpath, config, rsyncopt, sshopts)
    print(cmd)
    if not dryrun:
        os.system(cmd)

    hosts = core.expandhosts(hosts, config)
    if syncproxy and len(hosts)>1:
        for i in range(1, len(hosts)):
            cmd = createcommand(hosts[:i], srcpath, destpath, config, rsyncopt, sshopts)
            print(cmd)
            if not dryrun:
                os.system(cmd)

def main():
    config = loadconfig()
    parser = ArgumentParser(description='generate ssh command')
    parser.add_argument('-c', '--config', type=os.path.expanduser)
    parser.add_argument('-n', '--dryrun', dest='dryrun', action='store_true', help='dryrun')
    parser.add_argument('--opts', dest='opts', help='rsync opt', default='')
    parser.add_argument('--sshopts', dest='sshopts', help='ssh opt', default='')
    parser.add_argument('--syncproxy', action='store_true', help='sync to proxy server')
    parser.add_argument('srcpath')
    parser.add_argument('dest')
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    host, dest = args.dest.split(':')
    hosts = parsecsv(host)
    config = core.loadconfig(args.config)
    executersync(hosts, args.srcpath, dest, config=config, dryrun=args.dryrun, rsyncopt=args.opts, sshopts=args.sshopts, syncproxy=args.syncproxy)

if __name__=='__main__':
    main()

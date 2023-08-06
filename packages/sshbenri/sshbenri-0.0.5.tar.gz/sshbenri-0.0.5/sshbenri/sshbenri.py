#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

u"""
 sshbenri
 ========
 多重SSHを便利に使うためのスクリプト
"""

from argparse import ArgumentParser
import os

from . import core
from .core import parsecsv

def executessh(hosts, common_options, execcmd, config={}, dryrun=False):
    """
    create and execute ssh command

    Arguments:
      hosts(list): list of host names
      common_options(list): ssh option
      execcmd(str): remote execute command
      config(dict): setting
      dryrun(bool): if False, does not execute
    """
    hosts = core.expandhosts(hosts, config)
    commands = core.createssh(hosts, common_options, config)
    executecommand = core.quotecommands(commands)
    if execcmd:
        executecommand += ' ' + core.create_remote_command(hosts, execcmd)

    print(executecommand)
    if not dryrun:
        os.system(executecommand)

def _create_forwardopt(ports):
    res = []
    for fport in ports:
        res.append("-L{port}:localhost:{port}".format(port=fport))

    return res

def readscript():
    script = ""
    while True:
        res = raw_input("> ")
        if res.rstrip()=="": break
        script += res + " "

    print(script)
    return script

def main():
    config = core.loadconfig()
    parser = ArgumentParser(description='generate ssh command')
    parser.add_argument('-c', '--config', type=os.path.expanduser)
    parser.add_argument('-p', '--ports', dest='ports', help='forward port', type=parsecsv)
    parser.add_argument('-g', '--opts', dest='opts', help='global ssh options')
    parser.add_argument('-e', '--exec', dest='execcmd', help='execute comand')
    parser.add_argument('-n', '--dryrun', dest='dryrun', action='store_true', help='dryrun')
    parser.add_argument('-i', '--stdin', action='store_true', help='read script from stdin')
    parser.add_argument('hosts', help='target hosts A,B,C', type=parsecsv)
    args = parser.parse_args()
    hosts = args.hosts
    ports = args.ports
    common_options = ['-t', '-A']
    if ports:
        common_options += _create_forwardopt(ports)

    if args.opts:
        common_options += parsecsv(args.opts)

    if args.stdin:
        args.execcmd = readscript()

    config = core.loadconfig(args.config)
    executessh(hosts, common_options, args.execcmd, config=config, dryrun=args.dryrun)

if __name__=='__main__':
    main()

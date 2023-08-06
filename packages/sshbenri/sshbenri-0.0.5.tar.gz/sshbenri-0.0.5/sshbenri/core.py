# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
def loadconfig(path=None):
    """
    Load Config .py File

    default path is ~/.sshbenri.py
    """
    if path is None:
        path = os.path.expanduser('~/.sshbenri.py')

    if not os.path.exists(path): return {}
    G = {}
    L = {}
    execfile(path, G, L)
    return L['hosts']

def parsecsv(string):
    if not string: return []
    return [val.strip() for val in string.split(',')]

def quotecommands(commands):
    """
    quote ssh command

    Arguments:
      commands(list): ssh command list
    """
    depth = len(commands)-1
    res   = ""
    for depth, command in enumerate(commands):
        escapedcommand = escape(command, depth)
        res += ' ' + escapedcommand

    return res.strip()

def getescapechar(depth):
    x = (2 ** depth) - 1
    return '\\' * int(x)

specialchars = ['\\', '$', '~', '&', '|', '<', '>', '[', ']', ';', '\n', '(', ')', '*']
def escape(command, depth):
    """
    escape single command

    Arguments:
      command(str): command string
      depth(int):

    Example::

    >>> escape('ssh -i ~/key', 1)
    'ssh -i \\~/'
    """
    escapechar = getescapechar(depth)
    escapedcommand = command
    for char in specialchars:
        escapedcommand = escapedcommand.replace(char, escapechar+char)

    return escapedcommand

def escape_quote(string, depth):
    """
    escape quote char
    """
    esc = getescapechar(depth+1)
    string = string.replace("'", "'{esc}''".format(esc=esc))
    return string

def createssh(hosts, common_options, config, depth=0):
    """
    create ssh command in list
    """
    commands = []
    for host in hosts:
        # create ssh command
        sshcommand = 'ssh '
        if common_options:
            # common option
            sshcommand += '{} '.format(' '.join(common_options))

        if host.find('ssh ')==0:
            # we admit host name such as 'ssh -i ~/key host'
            sshcommand += host[4:]
        else:
            sshcommand += host

        commands.append(sshcommand.strip())
        depth += 1

    return commands

def expandhosts(hosts, config):
    """
    load config and expand host names
    """
    res = []
    for host in hosts:
        if host in config:
            ehost = config[host].get('host', host)
            if isinstance(ehost, (str, unicode)):
                expandedhosts = parsecsv(ehost)
            elif isinstance(ehost, (list, tuple)):
                expandedhosts = ehost
        else:
            expandedhosts = [host]

        res += expandedhosts

    return res

def create_remote_command(hosts, execcmd):
    """
    create remote execute command
    """
    depth = len(hosts)-1
    cmd = execcmd.strip()
    cmd = escape(cmd, depth)
    cmd = "'"+escape_quote(cmd, depth)+"'"
    return cmd

def create_ssh_command(hosts, common_options, execcmd, config={}, dryrun=False):
    commands = createssh(hosts, common_options, config)
    executecommand = quotecommands(commands)
    return executecommand

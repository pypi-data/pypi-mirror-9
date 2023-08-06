#!/usr/bin/env python
# −*− coding: UTF−8 −*−
"""Manage egress rules in RedBridge Cloud
Currently this tool only opens for all egress traffic

Usage:
  rbc-networks create [-n] [--short] NETWORK

Arguments:
  NETWORK network name

Options:
  -n --noheader                      Do not show the table header
  --short                            Short disply, only shows name
  -h --help      Show this screen.
  --version      Show version.

"""
import sys, operator
from tabulate import tabulate
from config import read_config
from connection import conn
from zone import get_zone
from docopt import docopt

__cli_name__="rbc-egress"
from rbc_tools import __version__

def get_network(c, name):
    nlist = []
    for n in c.list_networks(canusefordeploy="true"):
        if n.name == name:
            nlist.append(n)
    if nlist:
        return nlist
    else:
        print "The search returned no networks"
        sys.exit(0)

def main():
    config = read_config()
    c = conn(config)
    args = docopt(__doc__, version='%s %s' % (__cli_name__, __version__))
    if args['create']:
        id = get_network(c, args['NETWORK'])[0].id
        res = c.create_egressfirewallrule(networkid=id, protocol="All", cidrlist="0.0.0.0/0")
        if res:
            print "egress rule created"
            sys.exit(0)

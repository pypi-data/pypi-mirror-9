#!/usr/bin/env python
# −*− coding: UTF−8 −*−
"""Manage public ip addresses in RedBridge Cloud

Usage:
  rbc-publicips list [-n] [--short] [NETWORK]
  rbc-publicips allocate NETWORK
  rbc-publicips release IPADDRESS

Options:
  -n --noheader                      Do not show the table header
  --short                            Short disply, only shows name
  -h --help      Show this screen.
  --version      Show version.

"""
import sys, operator, os, random, string
from tabulate import tabulate
from config import read_config
from connection import conn
from zone import get_zone
from docopt import docopt

__cli_name__="rbc-publicips"
from rbc_tools import __version__

def get_network_from_name(c, name):
    ret = c.list_networks(keyword=name)
    if len(ret) == 1:
        return ret[0]
    else:
        print "Unable to get network, got: %s" % ret
        sys.exit(1)

def get_id_from_address(c, address):
    try:
        res = c.list_publicipaddresses(ipaddress=address)[0]
        if res:
            return res
        else:
            print "Unable to get ip address id"
            sys.exit(0)
    except:
        print "Unable to get ip address id"
        sys.exit(1)

def print_tabulate(res, noheader=False, short=False):
    config = read_config()
    c = conn(config)
    tbl = []
    for i in res:
        if not i.__dict__.has_key('associatednetworkname'):
            if i.__dict__.has_key('vpcid'):
                i.__setattr__('associatednetworkname', "%s (VPC)" % c.list_vpcs(id=i.vpcid)[0].name)
        if i.isstaticnat:
            vmname = i.virtualmachinename
        else:
            vmname = ""
        if i.issourcenat:
            snat = "Yes"
        else:
            snat = "No"
        if short:
            tbl.append([i.name])
        else:
            tbl.append([
                i.ipaddress,
                i.zonename,
                i.associatednetworkname,
                vmname,
                snat,
                i.allocated,

                ])

    tbl = sorted(tbl, key=operator.itemgetter(2))
    if (noheader or short):
        print tabulate(tbl, tablefmt="plain")
    else:
        tbl.insert(0, ['ip', 'zone', 'network', 'staticnat', 'sourcenat', 'allocated'])
        print tabulate(tbl, headers="firstrow")


def main():
    config = read_config()
    c = conn(config)
    args = docopt(__doc__, version='%s %s' % (__cli_name__, __version__))
    if args['list']:
        res = c.list_publicipaddresses()
    elif args['allocate']:
        res = [c.associate_ipaddress(networkid=get_network_from_name(c, args['NETWORK']).id).get_result()]
    elif args['release']:
        res = [c.disassociate_ipaddress(id=get_id_from_address(c, args['IPADDRESS']).id).get_result()]
        print "Released ip address: %s" % args['IPADDRESS']
        sys.exit(0)
    if res:
        print_tabulate(res, noheader=args['--noheader'], short=args['--short'])
    else:
        print "Unable to execute command"
        sys.exit(1)

#!/usr/bin/env python
# −*− coding: UTF−8 −*−
"""Manage networks in RedBridge Cloud

Usage:
  rbc-networks list [-n] [--short] [--search=SEARCH]
  rbc-networks create [-n] [--short] [-d DOMAIN] [-z ZONE] -o OFFERING NETWORK
  rbc-networks delete [-n] [--short] NETWORK

Arguments:
  NETWORK network name

Options:
  -n --noheader                      Do not show the table header
  --short                            Short disply, only shows name
  --search=SEARCH                    Search networks matching SEARCH
  -o OFFERING --offering=OFFERING    Name of network offering
  -d DOMAIN --domain=DOMAIN          Name of internal domain
  -z ZONE --zone=ZONE                Name of zone
  -h --help      Show this screen.
  --version      Show version.

"""
import sys, operator
from tabulate import tabulate
from config import read_config
from connection import conn
from zone import get_zone
from docopt import docopt

__cli_name__="rbc-networks"
from rbc_tools import __version__

def get_offering_id(c, name):
    try:
        for i in c.list_networkofferings(name=name):
            if i.name == name:
                return i.id
    except:
        print "Unable to get id for offering"
        sys.exit(1)

def get_snat(c, id):
    ip = c.list_publicipaddresses(associatednetworkid=id, issourcenat="true")
    if ip:
        return ','.join([x.ipaddress for x in ip])
    else:
        # Try to get VPC snat
        try:
            ip = c.list_publicipaddresses(vpcid=id, issourcenat="true")
            if ip:
                return ','.join([x.ipaddress for x in ip])
            else:
                return ''
        except:
            return ''

def has_vpn(c, id):
    v = c.list_remoteaccessvpns(networkid=id)
    if isinstance(v, dict):
        if v.has_key('count'):
            return "Yes"
    else:
        return "No"

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

def print_tabulate(res, noheader=False, short=False):
    config = read_config()
    c = conn(config)
    tbl = []
    for i in res:
        if not i.__dict__.has_key('networkofferingname'):
            i.__setattr__('networkofferingname', 'VPC')
        if short:
            tbl.append([i.name])
        else:
            tbl.append([
                i.name,
                i.zonename,
                i.networkofferingname,
                i.cidr,
                i.networkdomain,
                get_snat(c, i.id),
                has_vpn(c, i.id),
                i.state
                ])

    tbl = sorted(tbl, key=operator.itemgetter(0))
    if (noheader or short):
        print tabulate(tbl, tablefmt="plain")
    else:
        tbl.insert(0, ['name', 'zone', 'offering', 'cidr', 'domain', 'snat', 'vpn', 'state'])
        print tabulate(tbl, headers="firstrow")

def main():
    config = read_config()
    c = conn(config)
    args = docopt(__doc__, version='%s %s' % (__cli_name__, __version__))
    if args['list']:
        list_args ={'listall': 'true'}
        if args['--search']:
            list_args['keyword'] = args['--search']
        res = c.list_networks(**list_args)
        try:
            res += c.list_vpcs(**list_args)
        except:
            pass
    if args['delete']:
        id = get_network(c, args['NETWORK'])[0].id
        if id:
            res = c.delete_network(id=id).get_result()
            if res:
                print "network deleted"
                sys.exit(0)
            else:
                print "failed to delete the network, check that there are no running instances deployed on the network."
                sys.exit(1)
    if args['create']:
        create_args = {'name': args['NETWORK'], 'displaytext': args['NETWORK']}
        if args['--offering']:
            create_args['networkofferingid'] = get_offering_id(c, args['--offering'])
        if args['--domain']:
            create_args['networkdomain'] = args['--domain']
        if args['--zone']:
            zone = get_zone(c, args['--zone'])[0]
            create_args['zoneid'] = zone.id
        else:
            zone = get_zone(c)[0]
            create_args['zoneid'] = zone.id
            res = c.create_network(**create_args)
            if res:
                print "network created"
                sys.exit(0)

    if res:
        print_tabulate(res, noheader=args['--noheader'], short=args['--short'])
    else:
        print "Unable to execute command"
        sys.exit(1)

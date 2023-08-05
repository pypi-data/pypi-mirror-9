#!/usr/bin/env python
# −*− coding: UTF−8 −*−
"""Manage static NAT mappings in RedBridge Cloud

Usage:
  rbc-staticnats list [-n] [--short] [NETWORK]
  rbc-staticnats enable INSTANCE IPADDRESS [--rules RULE...]
  rbc-staticnats disable IPADDRESS

Options:
  -n --noheader  Do not show the table header
  --short        Short disply, only shows name
  --open=RULE    A fw rule in the format src:proto/port (0.0.0.0/0:tcp/22)
  -h --help      Show this screen.
  --version      Show version.

"""
import sys, operator, os, random, string
from tabulate import tabulate
from config import read_config
from connection import conn
from zone import get_zone
from docopt import docopt

__cli_name__="rbc-staticnats"
from rbc_tools import __version__

def get_network_from_name(c, name):
    ret = c.list_networks(keyword=name)
    if len(ret) == 1:
        return ret[0]
    else:
        print "Unable to get network, got: %s" % ret
        sys.exit(1)

def get_instance_from_name(c, name):
    ret = c.list_virtualmachines(keyword=name, name=name)
    if len(ret) == 1:
        return ret[0]
    else:
        print "Unable to get instance, got: %s" % ret
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

def get_firewall_rules(c, ipid):
    return c.list_firewallrules(ipaddressid=ipid)

def rule_list_to_string(rules):
    r = []
    for i in rules:
        r.append("%s:%s/%s" % (i.cidrlist, i.protocol, i.startport))
    return " ".join(r)

def print_tabulate(res, noheader=False, short=False, t='list'):
    config = read_config()
    c = conn(config)
    tbl = []
    for i in res:
        if t == 'list':
            rules = get_firewall_rules(c, ipid=i.id)
            r = rule_list_to_string(rules)
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
                    i.allocated,
                    r
                ])

    tbl = sorted(tbl, key=operator.itemgetter(2))
    if (noheader or short):
        print tabulate(tbl, tablefmt="plain")
    else:
        tbl.insert(0, ['ip', 'zone', 'network', 'staticnat', 'allocated', 'rules'])
        print tabulate(tbl, headers="firstrow")

def main():
    config = read_config()
    c = conn(config)
    args = docopt(__doc__, version='%s %s' % (__cli_name__, __version__))
    if args['list']:
        if args['NETWORK']:
            res = c.list_publicipaddresses(networkid=get_network_from_name(c, args['NETWORK']).id, isstaticnat='true')
        else:
            res = c.list_publicipaddresses(isstaticnat='true')
    elif args['enable']:
        try:
            if c.enable_staticnat(ipaddressid=get_id_from_address(c, args['IPADDRESS']).id, virtualmachineid=get_instance_from_name(c, args['INSTANCE']).id):
                if args['--rules']:
                    print args
                    try:
                        for rule in args['RULE']:
                            src = rule.split(':')
                            proto_port = src[1].split('/')
                            c.create_firewallrule(ipaddressid=get_id_from_address(c, args['IPADDRESS']).id, startport=proto_port[1], protocol=proto_port[0], cidrlist=src[0])
                    except Exception as e:
                        print "Unable create firewall rules: %s" % e
                print "Enabled static nat for %s on %s" % (args['INSTANCE'], args['IPADDRESS'])
                sys.exit(0)
        except Exception as e:
            print "Unable to enable static nat: %s" % e[1]
            sys.exit(1)
    elif args['disable']:
        try:
            res = c.disable_staticnat(ipaddressid=get_id_from_address(c, args['IPADDRESS']).id).get_result()
            if res == 'succeded':
                print "Disabled static nat on %s" % args['IPADDRESS']
                sys.exit(0)
        except Exception as e:
            print "Unable to disable static nat: %s" % e[1]
            sys.exit(1)

    if res:
        print_tabulate(res, noheader=args['--noheader'], short=args['--short'])
    else:
        print "Unable to execute command"
        sys.exit(1)

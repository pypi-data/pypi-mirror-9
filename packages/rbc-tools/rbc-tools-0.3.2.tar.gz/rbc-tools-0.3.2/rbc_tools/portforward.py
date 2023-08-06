#!/usr/bin/env python
# −*− coding: UTF−8 −*−
"""Manage port forwarding rules in RedBridge Cloud

Usage:
  rbc-portforward list [-n] [--short] [--network NETWORK] [--pubip IPADDRESS]
  rbc-portforward add INSTANCE (--pubip IPADDRESS|--network NETWORK) --forward RULE...
  rbc-portforward delete UUID

Options:
  -n --noheader     Do not show the table header
  --short           Short display, only shows name
  --network=NETWORK A network name, default public IP for the specified net is used 
  --pubip=IPADDRESS A public IP address
  --forward=RULE    A forward rule in the format proto/publicport:privateport (tcp/22:22)
  -h --help         Show this screen.
  --version         Show version.

"""
import sys, operator, os, random, string
from tabulate import tabulate
from config import read_config
from connection import conn
from zone import get_zone
from docopt import docopt

__cli_name__="rbc-portforward"
from rbc_tools import __version__

def get_default_snat_id(c, id):
    ip = c.list_publicipaddresses(associatednetworkid=id, issourcenat="true")
    if ip:
        return ip[0].id
    else:
        return ['N/A']

def get_network_from_name(c, name):
    ret = c.list_networks(keyword=name)
    if len(ret) == 1:
        return ret[0]
    else:
        print "Unable to get network, got: %s" % ret
        sys.exit(1)


def get_instance_from_name(c, name, networkid=None):
    if networkid:
        ret = c.list_virtualmachines(keyword=name, name=name, networkid=networkid)
    else:
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

def print_tabulate(res, noheader=False, short=False, t='list'):
    config = read_config()
    c = conn(config)
    tbl = []
    for i in res:
        if t == 'list':
            if not i.__dict__.has_key('virtualmachinename'):
                i.__setattr__('virtualmachinename', 'None')
            if short:
                tbl.append([i.id])
            else:
                tbl.append([
                    i.ipaddress,
                    c.list_networks(id=i.networkid)[0].name,
                    i.publicport,
                    i.privateport,
                    i.protocol,
                    i.virtualmachinename,
                    i.state,
                    i.id,
                ])

    tbl = sorted(tbl, key=operator.itemgetter(0))
    if (noheader or short):
        print tabulate(tbl, tablefmt="plain")
    else:
        tbl.insert(0, ['ip', 'network', 'public port', 'private port', 'proto',
            'vmname', 'state', 'uuid'])
        print tabulate(tbl, headers="firstrow")

def main():
    config = read_config()
    c = conn(config)
    args = docopt(__doc__, version='%s %s' % (__cli_name__, __version__))
    if args['list']:
        if args['--network']:
            res = c.list_portforwardingrules(networkid=get_network_from_name(c,
                args['--network']).id)
        elif args['--pubip']:
            res = c.list_portforwardingrules(ipaddressid=get_id_from_address(c,
                args['--pubip']).id)
        else:
            res = c.list_portforwardingrules()
    elif args['add']:
        try:
            if args['--pubip']:
                ipid = get_id_from_address(c, args['--pubip']).id
                network_id = get_id_from_address(c, args['--pubip']).networkid
            elif args['--network']:
                ipid = get_default_snat_id(c, get_network_from_name(c,
                    args['--network']).id)
                network_id = get_network_from_name(c, args['--network']).id
            else:
                print "Either --network or --pubip must be specified"
                sys.exit(1)
        except Exception as e:
            print "Unable to determine network or ip: %s" % e
            sys.exit(1)

        try:
            vmid = get_instance_from_name(c, args['INSTANCE'], networkid=network_id).id
        except Exception as e:
            print "Unable to find specified instance: %s" % e
            sys.exit(1)

        try:
            for f in args['--forward']:
                proto_port = f.split('/')
                ports=proto_port[1].split(':')
                async = c.create_portforwardingrule(
                    ipaddressid=ipid,
                    virtualmachineid=vmid,
                    publicport=ports[0],
                    privateport=ports[1],
                    protocol=proto_port[0])
                res = [async.get_result()]
                if not res:
                    raise Exception("An internal error occured.")
        except Exception as e:
            try:
                msg = e[1]
            except:
                msg = e
            print "Unable to create portforward rule: %s" % msg
            sys.exit(1)
    elif args['delete']:
        try:
            async = c.delete_portforwardingrule(id=args['UUID'])
            res = async.get_result()
            if not res:
                raise Exception("An internal error occured.")
            if res == 'succeded':
                sys.exit(0)
            else:
                raise Exception("Failure")
        except Exception as e:
            try:
                msg = e[1]
            except:
                msg = e
            print "Unable to delete portforward rule: %s" % msg
            sys.exit(1)

    if res:
        print_tabulate(res, noheader=args['--noheader'], short=args['--short'])
    else:
        print "Unable to execute command"
        sys.exit(1)

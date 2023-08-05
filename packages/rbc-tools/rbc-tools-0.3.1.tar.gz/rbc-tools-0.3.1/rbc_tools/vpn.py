#!/usr/bin/env python
# −*− coding: UTF−8 −*−
"""Manage remote access VPN's in RedBridge Cloud

Usage:
  rbc-vpns list [-n] [--short]
  rbc-vpns enable NETWORK
  rbc-vpns disable NETWORK
  rbc-vpns users list [-n] [--short]
  rbc-vpns users add USERNAME [PASSWORD]
  rbc-vpns users remove USERNAME
  rbc-vpns users password USERNAME PASSWORD

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

__cli_name__="rbc-vpns"
from rbc_tools import __version__

def get_network_for_ip(c, ipid):
    ip =  c.list_publicipaddresses(id=ipid)[0]
    if not ip.__dict__.has_key('associatednetworkname'):
        if ip.__dict__.has_key('vpcid'):
            ip.__setattr__('associatednetworkname', "%s (VPC)" % c.list_vpcs(id=ip.vpcid)[0].name)
    return ip.associatednetworkname

def get_network_from_name(c, name):
    ret = c.list_networks(keyword=name)
    if len(ret) == 1:
        return ret[0]
    else:
        print "Unable to get network, got: %s" % ret
        sys.exit(1)

def get_publicip_for_network(c, name):
    net = get_network_from_name(c, name)
    ip = c.list_publicipaddresses(associatednetworkid=net.id, issourcenat='true')
    if len(ip) == 1:
        return ip[0]
    else:
        print "Unable to get ip address"
        sys.exit(1)

def print_tabulate(res, noheader=False, short=False, t="vpn"):
    config = read_config()
    c = conn(config)
    tbl = []
    for i in res:
        if t == 'vpn':
            if short:
                tbl.append([i.publicip])
            else:
                tbl.append([
                    get_network_for_ip(c, i.publicipid),
                    i.publicip,
                    i.presharedkey,
                    i.state,
                    ])
        if t == 'vpnusers':
            if short:
                tbl.append([i.username])
            else:
                tbl.append([
                    i.username,
                    i.state,
                    ])
    
    tbl = sorted(tbl, key=operator.itemgetter(0))
    if (noheader or short):
        print tabulate(tbl, tablefmt="plain")
    else:
        if t == 'vpn':
            tbl.insert(0, ['network', 'endpoint', 'preshared key', 'state'])
        elif t == 'vpnuser':
            tbl.insert(0, ['username', 'state'])
        print tabulate(tbl, headers="firstrow")


def main():
    config = read_config()
    c = conn(config)
    args = docopt(__doc__, version='%s %s' % (__cli_name__, __version__))
    if (args['list'] and not args['users']):
        res = c.list_remoteaccessvpns()
        t = "vpn"
    elif args['enable']:
        ip = get_publicip_for_network(c, args['NETWORK'])
        try:
            ret = c.create_remoteaccessvpn(publicipid=ip.id)
        except Exception as e:
            print "Unable to enable remote access VPN: %s" % e[1]
            sys.exit(1)
    elif args['disable']:
        ip = get_publicip_for_network(c, args['NETWORK'])
        try:
            ret = c.delete_remoteaccessvpn(publicipid=ip.id)
        except Exception as e:
            print "Unable to disable remote access VPN: %s" % e[1]
            sys.exit(1)
    elif args['users']:
        t = 'vpnusers'
        if args['list']:
            res = c.list_vpnusers()
        if args['add']:
            if not args['PASSWORD']:
                length = 8
                chars = string.ascii_letters + string.digits + '@#+=.-_'
                random.seed = (os.urandom(1024))
                passwd = ''.join(random.choice(chars) for i in range(length))
            else:
                passwd = args['PASSWORD']
            c.add_vpnuser(username=args['USERNAME'], password=passwd)
            print "VPN user %s added with password %s" % (args['USERNAME'], passwd)
            sys.exit(1) 
        elif args['remove']:
            try:
                c.remove_vpnuser(username=args['USERNAME'])
                print "Removed user: %s" % args['USERNAME']
                sys.exit(0)
            except Exception as e:
                print "Unable to remove VPN user: %s" % e[1]
                sys.exit(1)
    if res:
        print_tabulate(res, noheader=args['--noheader'], short=args['--short'], t=t)
    else:
        print "Unable to execute command"
        sys.exit(1)

#!/usr/bin/env python
# −*− coding: UTF−8 −*−
"""Manage ssh keypairs in RedBridge Cloud

Usage:
  rbc-sshkeys list [-n] [--short]
  rbc-sshkeys generate NAME
  rbc-sshkeys delete NAME

Options:
  -n --noheader                      Do not show the table header
  --short                            Short disply, only shows name
  -h --help      Show this screen.
  --version      Show version.

"""
import sys, operator, os, random, string
import molnctrl
from tabulate import tabulate
from config import read_config
from connection import conn
from zone import get_zone
from docopt import docopt

__cli_name__="rbc-sshkeys"
from rbc_tools import __version__


def get_sshkey(c, name):
    slist = []
    for k in c.list_sshkeypairs(name=name):
            slist.append(k)
    if slist:
        return slist
    else:
        print "The search returned no ssh keys"
        sys.exit(0)

def print_tabulate(res, noheader=False, short=False):
    config = read_config()
    c = conn(config)
    tbl = []
    for i in res:
        if short:
            tbl.append([i.name])
        else:
            tbl.append([
                i.name,
                i.fingerprint,
                ])

    tbl = sorted(tbl, key=operator.itemgetter(0))
    if (noheader or short):
        print tabulate(tbl, tablefmt="plain")
    else:
        tbl.insert(0, ['name', 'fingerprint'])
        print tabulate(tbl, headers="firstrow")


def main():
    config = read_config()
    c = conn(config)
    args = docopt(__doc__, version='%s %s' % (__cli_name__, __version__))
    if args['list']:
        res = c.list_sshkeypairs()
    if args['generate']:
        try:
            res = c.create_sshkeypair(name=args['NAME'])
            print res.privatekey
            sys.exit(0)
        except molnctrl.csexceptions.ResponseError as e:
            print "Unable to create ssh key: %s" % e[1]
            sys.exit(1)
    if args['delete']:
        try:
            res = c.delete_sshkeypair(name=args['NAME'])
            print "deleted SSH key: %s" % args['NAME']
            sys.exit(0)
        except Exception as e:
            print "Unable to delete SSK keypair: %s" % e[1]
            sys.exit(1)
    if res:
        print_tabulate(res, noheader=args['--noheader'], short=args['--short'])
    else:
        print "Unable to execute command"
        sys.exit(1)

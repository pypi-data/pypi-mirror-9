#!/usr/bin/env python
# −*− coding: UTF−8 −*−
"""View offerings in RedBridge Cloud

Usage:
  rbc-offerings list (compute|network) [-n] [--short]

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

__cli_name__="rbc-offerings"
from rbc_tools import __version__
def get_offering(c, name):
    olist = []
    for o in c.list_serviceofferings(name=name):
            olist.append(o)
    if olist:
        return olist
    else:
        print "The search returned no offerings"
        sys.exit(0)

def list_main():
    config = read_config()
    c = conn(config)
    parser = ArgumentParser(description="View service offerings in RedBridge Cloud")
    parser.add_argument('-s', '--search', dest="search", action="store", help="Search for offering")
    parser.add_argument('-n', '--noheader', dest="noheader", action="store_true", default=False, help="Do not show the header")
    options = parser.parse_args()
    slist = []
    slist.append(['name', 'id', 'description'])
    if options.search:
        offerings = get_offering(c, options.search)
    else:
        offerings = c.list_serviceofferings()
    for o in offerings:
        slist.append([o.name, o.id, o.displaytext])
    print tabulate(slist, headers="firstrow")

def print_tabulate(res, offering_type="compute", noheader=False, short=False):
    config = read_config()
    c = conn(config)
    tbl = []
    for i in res:
        if short:
            tbl.append([i.name])
        else:
            if offering_type == "compute":
                tbl.append([
                    i.name,
                    i.displaytext,
                    i.storagetype,
                    ])
            elif offering_type == "network":
                tbl.append([
                    i.name,
                    i.displaytext,
                    "%s Mbit/s"% i.networkrate,
                    ])

    tbl = sorted(tbl, key=operator.itemgetter(0))
    if (noheader or short):
        print tabulate(tbl, tablefmt="plain")
    else:
        if offering_type == 'compute':
            tbl.insert(0, ['name', 'description', 'storagetype'])
        else:
            tbl.insert(0, ['name', 'description', 'external networkrate'])

        print tabulate(tbl, headers="firstrow")


def main():
    config = read_config()
    c = conn(config)
    args = docopt(__doc__, version='%s %s' % (__cli_name__, __version__))
    if args['list']:
        if args['compute']:
            res = c.list_serviceofferings()
            t = 'compute'
        elif args['network']:
            res = c.list_networkofferings(state="Enabled")
            t = 'network'
    if res:
        print_tabulate(res, noheader=args['--noheader'], short=args['--short'], offering_type=t)
    else:
        print "Unable to execute command"
        sys.exit(1)

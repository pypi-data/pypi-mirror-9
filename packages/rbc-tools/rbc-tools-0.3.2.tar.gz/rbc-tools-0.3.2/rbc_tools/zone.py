#!/usr/bin/env python
# −*− coding: UTF−8 −*−
import sys

def get_zone(c, name=None):
    zlist = []
    args = {}
    if name:
        args['name'] = name
    for z in c.list_zones(**args):
            zlist.append(z)
    if zlist:
        return zlist
    else:
        print "The search returned no zones"
        sys.exit(0)



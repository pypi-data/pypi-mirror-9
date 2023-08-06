#!/usr/bin/env python
# −*− coding: UTF−8 −*−
"""Manage templates in RedBridge Cloud

Usage:
  rbc-templates list [-n] [--short] [--search=SEARCH] [FILTER]
  rbc-templates delete [-n] [--short] TEMPLATE

Arguments:
  FILTER   Template filter, valid options are:
           "featured", "self", "selfexecutable","sharedexecutable","executable", and "community".
           See the RedBridge Cloud API documentation for info.
           [default: executable]
  TEMPLATE Template name

Options:
  -n --noheader                      Do not show the table header
  --short                            Short disply, only shows name
  --search=SEARCH                    Search templates matching STRING 
  -h --help      Show this screen.
  --version      Show version.

"""
import sys, operator
from tabulate import tabulate
from config import read_config
from connection import conn
from docopt import docopt

__cli_name__="rbc-templates"
from rbc_tools import __version__

def list_templates(c, args):
    list_args = {} 
    if args['--search']:
        list_args['keyword'] = args['--search']
    list_args['templatefilter'] = args['FILTER']
    list_args['listall'] = "true"
    return c.list_templates(**list_args)

def delete_template(c, args):
    list_args = {} 
    list_args['id'] = get_template(c, args['TEMPLATE'])[0].id
    job = c.delete_template(**list_args)
    if job.get_result() == 'succeded':
        print "Template %s deleted" % args['TEMPLATE']
        sys.exit(0)
    else:
        print "Error deleting template"
        sys.exit(1)

def get_template_from_id(c ,id):
    try:
        return c.list_templates(templatefilter='executable', id=id)[0]
    except:
        try:
            return c.list_isos(id=id)[0]
        except:
            return False

def get_template(c, t):
    tlist = []
    try:
        account, name = t.split('/', 1)
    except ValueError:
        print "String must be in the format account/name"
        sys.exit(0)
    for t in c.list_templates(name=name, templatefilter='executable', listall="true"):
        tlist.append(t)
    if tlist:
        return tlist
    else:
        print "The search returned no templates"
        sys.exit(0)

def print_tabulate(res, noheader=False, short=False):
    config = read_config()
    c = conn(config)
    tbl = []
    for i in res:
        if not i.__dict__.has_key('passwordenabled'):
            i.__setattr__('passwordenabled', 0)
        if not i.__dict__.has_key('created'):
            i.__setattr__('created', '')
        if i.passwordenabled == 1:
            passw = "Yes"
        else:
            passw = "No"
        if short:
            tbl.append(["%s/%s" % (i.account, i.name)])
        else:
            tbl.append([
                "%s/%s" % (i.account, i.name),
                i.zonename,
                i.ostypename,
                i.created,
                passw,
                ])

    tbl = sorted(tbl, key=operator.itemgetter(0))
    if (noheader or short):
        print tabulate(tbl, tablefmt="plain")
    else:
        tbl.insert(0, ['name', 'zone', 'ostype', 'created', 'passwordenabled'])
        print tabulate(tbl, headers="firstrow")


def main():
    config = read_config()
    c = conn(config)
    args = docopt(__doc__, version='%s %s' % (__cli_name__, __version__))
    if not args['FILTER']:
        args['FILTER'] = 'executable' 
    if not args['FILTER'] in ["featured", "self", "selfexecutable","sharedexecutable","executable", "community"]:
        print "%s is not a valid template filter" % rgs['FILTER']
        sys.exit(1)
    
    if args['list']:
        res = list_templates(c, args)
    if args['delete']:
        res = delete_template(c, args)

    if res:
        print_tabulate(res, noheader=args['--noheader'], short=args['--short'])
    else:
        print "Could not find any templates, try listing featured templates using `rbc-templates list featured`"
        sys.exit(1)

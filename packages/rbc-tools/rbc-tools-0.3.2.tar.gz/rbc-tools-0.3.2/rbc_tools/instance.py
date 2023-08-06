#!/usr/bin/env python
# −*− coding: UTF−8 −*−
"""Manage instances in RedBridge Cloud

Usage:
  rbc-instances list [-n] [--short ] [--search=SEARCH] [--group=GROUP] [--tags=TAGS]  [-w NETWORK]
  rbc-instances get [-n] [-w NETWORK] INSTANCE
  rbc-instances destroy [-n] [-w NETWORK] INSTANCE
  rbc-instances stop [-n] [-w NETWORK] INSTANCE
  rbc-instances start [-n] [-w NETWORK] INSTANCE
  rbc-instances reboot [-n] [-w NETWORK] INSTANCE
  rbc-instances deploy [-n] [--nowait] [-i NUM] [-g GROUP] [-t TEMPLATE]
                       [-o OFFERING] [-w NETWORK] [-z ZONE] [-s SSHKEY]
                       [-d USER-DATA | -f FILE] [--tags=TAGS] INSTANCE

Examples:
  # Deploy 4 small instances with ssh key in group my-group and supply user-data
  rbc-instances deploy -i 4 -g my-group -t rbc/fedora-20-cloudimg-x86_64-10GB -o small -w default -s mykey -f /path/to/userdata  my-instance-name


Arguments:
  INSTANCE  Instance name

Options:
  -n --noheader                      Do not show the table header
  --nowait                           Do not wait for instances to start
  --short                            Short disply, only shows name
  --search=SEARCH                    Search instances matching STRING
  --tags=TAGS                        List or add tags to instances. Tags should be
                                     specified in key/value pairs: tagkey:tagvalue,app:myapp
  -i NUM --number=NUM                Number of instances to deploy [default: 1]
  -g GROUP --group=GROUP             Name of instance group
  -t TEMPLATE --template=TEMPLATE    Name of the template to use
                                     (use "rbc-templates list featured" to get featured templates)
  -o OFFERING --offering=OFFERING    Name of offering to use
                                     (use "rbc-offerings list" to get valid offerings)
  -w NETWORK --network=NETWORK       Name of the network to use
                                     (use "rbc-networks list" to get vaild networks)
  -z ZONE --zone=ZONE                Zone to use for deployment
                                     (use "rbc-zones list" to get vaild zones)
  -s SSHKEY --sshkey=SSHKEY          Name of SSH key to use
                                     (use "rbc-ssh-keys list" to get vaild key names)
  -d USER-DATA --user-data=USER-DATA A string with user data available for the instance
  -f FILE --user-data-file=FILE      A file containing user-data (must not exceed 2KB)
  -h --help      Show this screen.
  --version      Show version.

"""
import os, sys, time, hashlib, random, base64, operator, re
import tabulate
from argparse import ArgumentParser
from tabulate import tabulate
from config import read_config
from connection import conn
from template import get_template
from template import get_template_from_id
from offering import get_offering
from network import get_network
from zone import get_zone
from sshkey import get_sshkey
from docopt import docopt

__cli_name__="rbc-instances"
from rbc_tools import __version__

def deploy_vm(c, a):
    deploy_args = {}
    if a['--number']:
        n = int(a['--number'])
    else:
        n = 1
    if a['INSTANCE']:
        deploy_args['name'] = a['INSTANCE']
        deploy_args['displayname'] = a['INSTANCE']
    if a['--group']:
        deploy_args['group'] = a['--group']
    if a['--template']:
        try:
            template = get_template(c, a['--template'])[0]
            deploy_args['templateid'] = template.id
        except:
            print "Unable to get templateid for %s" % a['--template']
            sys.exit(1)
    if a['--offering']:
        try:
            offering = get_offering(c, a['--offering'])[0]
            deploy_args['serviceofferingid'] = offering.id
        except:
            print "Unable to get offeringid for %s" % a['--offering']
            sys.exit(1)
    if a['--network']:
        try:
            network = get_network(c, a['--network'])[0]
            deploy_args['networkids'] = network.id
        except:
            print "Unable to get networkid for %s" % a['--network']
            sys.exit(1)
    if a['--zone']:
        zone = get_zone(c, a['--zone'])[0]
        deploy_args['zoneid'] = zone.id
    else:
        zone = get_zone(c)[0]
        deploy_args['zoneid'] = zone.id
    if a['--sshkey']:
        try:
            sshkey = get_sshkey(c, a['--sshkey'])[0]
            deploy_args['keypair'] = sshkey.name
        except:
            print "Unable to get ssh key: %s" % a['--sshkey']
            sys.exit(1)
    if a['--user-data']:
        deploy_args['userdata'] = base64.b64encode(a['--user-data'])
    if a['--user-data-file']:
        if os.path.isfile(a['--user-data-file']):
            with open(a['--user-data-file']) as f:
                encoded = base64.b64encode(f.read())
            size = sys.getsizeof(encoded)
            deploy_args['userdata'] = encoded
    # Deploy it!
    res = []
    for i in range(n):
        if n > 1:
            append_hash = hashlib.new('sha1', str(random.randint(0,1000000))).hexdigest()[:3]
            deploy_args['name'] = "%s-%s" % (a['INSTANCE'], append_hash)
            deploy_args['displayname'] = "%s-%s" % (a['INSTANCE'], append_hash)
        res.append(c.deploy_virtualmachine(**deploy_args))
    vms = []
    if a['--tags']:
        tags = {}
        for tag in a['--tags'].split(','):
            regex = re.compile(r"\b(\w+)\s*:\s*([^:]*)(?=\s+\w+\s*:|$)")
            tags.update(dict(regex.findall(tag)))
    if not a['--nowait']:
        for j in res:
            if a['--tags']:
                c.create_tags(resourceids=j.id, resourcetype='UserVm', tags=tags)
            vms.append(j.get_result())
    else:
        for j in res:
            if a['--tags']:
                c.create_tags(resourceids=j.id, resourcetype='UserVm', tags=tags)
            vms.append(c.list_virtualmachines(id=j.id)[0])
    return vms

def list_vms(c, args):
    list_args = {}
    if args['--group']:
        gid = c.list_instancegroups(name=args['--group'])
        if len(gid) > 1:
            g_match = False
            for g in gid:
                if g.name == args['--group']:
                    list_args['groupid'] = g.id
                    g_match = True
            if not g_match:
                print "Multiple groups found: %s" % gid
                sys.exit(1)
        else:
            try:
                list_args['groupid'] = gid[0].id
            except IndexError:
                print "No such group found: %s" % gid
                sys.exit(1)

    if args['--search']:
        list_args['keyword'] = args['--search']

    if args['--tags']:
        tags = {}
        for tag in args['--tags'].split(','):
            regex = re.compile(r"\b(\w+)\s*:\s*([^:]*)(?=\s+\w+\s*:|$)")
            tags.update(dict(regex.findall(tag)))
        list_args['tags'] = tags
    try:
        res = c.list_virtualmachines(**list_args)
    except Exception as e:
        print "error listing instances"
        sys.exit(1)
    return res

def start_vm(c, id):
    try:
        res = c.start_virtualmachine(id=id)
    except Exception as e:
        print "error starting instance: %s"  % e
        sys.exit(1)
    return [res.get_result()]

def stop_vm(c, id):
    try:
        res = c.stop_virtualmachine(id=id)
    except Exception as e:
        print "error stopping instance: %s"  % e
        sys.exit(1)
    return [res.get_result()]

def destroy_vm(c, id):
    try:
        res = c.destroy_virtualmachine(id=id)
    except Exception as e:
        print "error destroying instance: %s"  % e
        sys.exit(1)
    return [res.get_result()]

def print_tabulate(res, noheader=False, short=False):
    config = read_config()
    c = conn(config)
    tbl = []
    template_cache = {}
    for i in res:
        if not i.__dict__.has_key('keypair'):
            i.__setattr__('keypair', 'None')
        if not i.__dict__.has_key('password'):
            i.__setattr__('password', 'None')
        if not i.__dict__.has_key('group'):
            i.__setattr__('group', 'None')
        # cache templates
        if not template_cache.has_key(i.templateid):
            # lookup
            t = get_template_from_id(c, i.templateid)
            if t:
                template_cache[i.templateid] = t
            else:
                template_cache[i.templateid] = type('Template', (object,), {'account': 'DELETED'})
        if short:
            tbl.append([i.name])
        else:
            tbl.append([i.name,
                i.zonename,
                i.state,
                i.serviceofferingname,
                i.group,
                i.nics[0].networkname,
                i.nics[0].ipaddress,
                i.keypair,
                i.password,
                "%s/%s" % (template_cache[i.templateid].account, i.templatename),
                i.created]
            )
    tbl = sorted(tbl, key=operator.itemgetter(0))
    if (noheader or short):
        print tabulate(tbl, tablefmt="plain")
    else:
        tbl.insert(0, ['name', 'zone', 'state', 'offering', 'group', 'network', 'ipaddress', 'sshkey', 'password', 'template', 'created'])
        print tabulate(tbl, headers="firstrow")

def main():
    config = read_config()
    c = conn(config, method='post')
    args = docopt(__doc__, version='%s %s' % (__cli_name__, __version__))
    res = False
    res_get = False
    if args['deploy']:
        try:
            res = deploy_vm(c, args)
        except Exception as e:
            print "error deploying instance: %s"  % e
            sys.exit(1)
    elif args['destroy']:
        try:
            id = c.list_virtualmachines(name=args['INSTANCE'])
            if len(id) == 1:
                res = destroy_vm(c, id[0].id)
            else:
                # Multiple VMs returned
                if args['--network']:
                    id = c.list_virtualmachines(name=args['INSTANCE'], networkid=get_network(c, args['--network'])[0].id)
                    res = destroy_vm(c, id[0].id)
                else:
                    print "Multiple instances with name: %s found, please supply a network name" % args['INSTANCE']
        except Exception as e:
            print "Error destroying instance: %s" % e
    elif args['stop']:
        try:
            id = c.list_virtualmachines(name=args['INSTANCE'])
            if len(id) == 1:
                res = stop_vm(c, id[0].id)
            else:
                # Multiple VMs returned
                if args['--network']:
                    id = c.list_virtualmachines(name=args['INSTANCE'], networkid=get_network(c, args['--network'])[0].id)
                    res = stop_vm(c, id[0].id)
                else:
                    print "Multiple instances with name: %s found, please supply a network name" % args['INSTANCE']
        except Exception as e:
            print "Error stopping instance: %s" % e
    elif args['start']:
        try:
            id = c.list_virtualmachines(name=args['INSTANCE'])
            if len(id) == 1:
                res = start_vm(c, id[0].id)
            else:
                # Multiple VMs returned
                if args['--network']:
                    id = c.list_virtualmachines(name=args['INSTANCE'], networkid=get_network(c, args['--network'])[0].id)
                    res = start_vm(c, id[0].id)
                else:
                    print "Multiple instances with name: %s found, please supply a network name" % args['INSTANCE']
        except Exception as e:
            print "Error starting instance: %s" % e
    elif args['list']:
        res = list_vms(c, args)
    elif args['get']:
        res = c.list_virtualmachines(name=args['INSTANCE'])
    else:
        print "Unable to execute command"
        sys.exit(1)

    if res:
        print_tabulate(res, noheader=args['--noheader'], short=args['--short'])
    else:
        print "No virtual machines found, deploy new machines using `rbc-instances deploy`"
        sys.exit(1)


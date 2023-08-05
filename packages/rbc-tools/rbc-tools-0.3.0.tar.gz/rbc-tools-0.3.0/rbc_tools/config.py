#!/usr/bin/env python
# −*− coding: UTF−8 −*−
import os, sys, ConfigParser, getpass
import requests

def read_config():
    config_file = 'rbc.cfg'
    for loc in os.curdir, "%s/.rbc" % os.path.expanduser("~"), "/etc", os.environ.get('PWD'):
        if os.path.exists(os.path.join(loc,config_file)):
            try:
                config = ConfigParser.ConfigParser()
                config.read(os.path.join(loc,config_file))
                return config
            except IOError:
                pass
    if (os.environ.get("RBC_SECRETKEY") and os.environ.get("RBC_APIKEY")):
        # Initialize using ENV
        return ConfigParser.ConfigParser()
    else:
        # Present an option to create a config file
        print "Could not find a config file (%s) in ~/rbc/, /etc or current dir." % config_file
        print "You may create one by running rbc-setup"
        sys.exit(1)

def main():
    user = get_keys_from_login()
    config = ConfigParser.RawConfigParser()
    config.add_section('main')
    config.set('main', 'apikey', user['user']['apikey'])
    config.set('main', 'secretkey', user['user']['secretkey'])
    config.set('main', 'endpoint', 'api.rbcloud.net')
    d = os.path.join(os.path.expanduser('~'), '.rbc')
    if not os.path.exists(d):
        os.makedirs(d)
    with open(os.path.join(d,'rbc.cfg'), 'wb') as configfile:
        config.write(configfile)

def get_keys_from_login():
    user = raw_input('Enter your rbc username:')
    password = getpass.getpass('Enter your rbc password:')
    url = "https://api.rbcloud.net/client/api"
    s = requests.Session()
    r = s.post(url, data={'username': user, 'password': password, 'domain': '/', 'command': 'login', 'response': 'json'})
    if r.status_code == 200:
        # login ok
        resp = requests.get(url, params={'command': 'updateUser', 
                'id':r.json()['loginresponse']['userid'], 'response':'json', 
                'sessionkey': r.json()['loginresponse']['sessionkey']},
                cookies=dict(JSESSIONID=r.cookies['JSESSIONID'], Path="/")
        )
        if resp.status_code == 200:
            return resp.json()['updateuserresponse']
        else:
            print "Unable to login, please verify your login and password"
            sys.exit(1)
    else:
        print "Unable to perform initial login"
        sys.exit(1)




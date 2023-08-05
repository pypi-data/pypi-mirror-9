#!/usr/bin/env python
# −*− coding: UTF−8 −*−
import os
import molnctrl

def conn(config, method="get"):
    rbc_secret = os.environ.get("RBC_SECRETKEY") or config.get('main', 'secretkey')
    rbc_key = os.environ.get("RBC_APIKEY")  or config.get('main', 'apikey')
    try:
        rbc_endpoint = config.get('main', 'endpoint')
    except NoOptionError:
        rbc_endpoint = os.environ.get("RBC_ENDPOINT") or "api.rbcloud.net"
    return molnctrl.Initialize(api_host=rbc_endpoint, api_key=rbc_key, api_secret=rbc_secret, req_method=method)

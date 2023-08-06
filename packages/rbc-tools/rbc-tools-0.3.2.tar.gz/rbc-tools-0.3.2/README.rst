=================================
rbc-tools: Manage RedBridge Cloud
=================================

rbc-tools are command line tools for managing RedBridge Cloud.

Using rbc-tools you can manage instances, networks and othe compute resources in RBC.

The tools are tested on MacOS X and Linux only at the moment, but should also work on Windows in a cygwin environment.

*The tools are in a early beta stage* so please report any bugs to support@redbridge.se or as issues on `github <https://github.com/redbridge/rbc-tools/issues>`_

Getting started
---------------

1. Register for an account on `RedBridge Portal <https://portal.redbridge.se/account/signup/>`_
2. Get your access key and secret key from your account page in the portal.
3. Create a ~/.rbc/rbc.cfg file (in a terminal)::

    mkdir -p ~/.rbc
    cat > ~/.rbc/rbc.cfg <<EOF
    [main]
    apikey = <your api key as found in the Portal>
    secretkey = <your secret key as found in the Portal>
    endpoint = api.rbcloud.net
    EOF

4. Install rbc-tools using pip (or easy_install)

5. Now you should have access to a number of command line scripts, prefixed with rbc-*

Note that you can also set api key and secret key by using environment variables::

    export RBC_APIKEY=XXXXX; export RBC_SECRETKEY=XXXX

Examples
--------------

Create a ssh key pair::

    rbc-sshkeys generate my-keypair > ~/.ssh/my-keypair_id_rsa

To deploy 3 small instances in the RedBridge Cloud, using a ssh key::

    rbc-instances deploy -i 3 -g test -t rbc/ubuntu-14.04-server-cloudimg-amd64-20GB-201461111 -o small -w default -s my-keypair my-instances


Development
-----------

Development of rbc-tools takes place on github (https://github.com/redbridge/rbc-tools).

History
=======
0.3.2 (2015-04-02)
-------------------

- Do not fail on network create if the command timeouts.

0.3.0 (2015-02-10)
-------------------

- Use post for instances, this makes it possible to use up to 32K of user data

0.1.18 (2014-08-07)
-------------------

- Fix broken network list when using VPC's

0.1.17 (2014-07-31)
-------------------

- First pypi release

0.1.0 (2014-07-31)
------------------

- Initial release.

Credits
=======

"rbc-tools" is written and maintained by RedBridge AB.

Contributors
------------

- `cldmnky <https://github.com/cldmnky>`_

Please add yourself here alphabetically when you submit your first pull request.

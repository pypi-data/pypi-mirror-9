import os, re, codecs
from setuptools import setup, find_packages
from glob import glob

name = 'rbc-tools'

with open('requirements.txt', 'r') as f:
        requires = [x.strip() for x in f if x.strip()]

conf_files = [ ('conf', glob('conf/*.cfg')) ]
dirs = [('log', [])]
data_files =  conf_files + dirs

setup(
    name=name,
    version='0.3.0',
    author='RedBridge AB',
    author_email='info@redbridge.se',
    data_files = data_files,
    url='http://github.com/redbridge/rbc-tools',
    license="Apache 2.0",
    description='Command line tools for managing RedBridge Cloud',
    long_description=open("README.rst").read(),
    packages=['rbc_tools'],
    scripts=glob('bin/*'),
    install_requires=requires,
    entry_points = {
                'console_scripts': [
                        'rbc-instances=rbc_tools.instance:main',
                        'rbc-templates=rbc_tools.template:main',
                        'rbc-networks=rbc_tools.network:main',
                        'rbc-offerings=rbc_tools.offering:main',
                        'rbc-vpns=rbc_tools.vpn:main',
                        'rbc-sshkeys=rbc_tools.sshkey:main',
                        'rbc-ipaddresses=rbc_tools.ipaddress:main',
                        'rbc-staticnat=rbc_tools.staticnat:main',
                        'rbc-portforward=rbc_tools.portforward:main',
                        'rbc-egress=rbc_tools.egress:main',
                        'rbc-setup=rbc_tools.config:main',
                ],
    }
)

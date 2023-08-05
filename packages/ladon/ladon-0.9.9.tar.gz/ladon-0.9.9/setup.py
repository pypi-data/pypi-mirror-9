#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys,os

if sys.version_info[0]==2:
	other_version = 3
else:
	other_version = 2

#ladon_ctl_scriptname = 'scripts/ladon%d.%dctl' % sys.version_info[0:2]
#ladon_ctl_scriptname_windows = 'scripts/ladon%d.%dctl.py' % sys.version_info[0:2]

# Read the cross-version ladon-ctl
#if os.path.exists('scripts/ladon-ctl'):
	#fp = open('scripts/ladon-ctl')
	#ladon_ctl_data = fp.read()
	#fp.close()

	## Rename it to fit the particular version
	#ladon_ctl_data = "#!%s\n%s" % (sys.executable,ladon_ctl_data)
	#fp = open(ladon_ctl_scriptname,'w')
	#fp.write(ladon_ctl_data)
	#fp.close()
	#fp = open(ladon_ctl_scriptname_windows,'w')
	#fp.write(ladon_ctl_data)
	#fp.close()

readme = changes = ''
if os.path.exists('README.rst'):
	readme = open('README.rst').read()
if os.path.exists('CHANGES.rst'):
	changes = open('CHANGES.rst').read()

import imp
m=imp.load_source('init','src/ladon/__init__.py')
VERSION = '%(major)s.%(minor)s.%(micro)s' % m._version_info

SHORT_DESC = "Serve your python methods to several web service interfaces at once, including JSON-WSP, SOAP and JSON-RPC."
PACKAGES = find_packages('src')

try:
	PACKAGES.remove('chardet_py%d' % other_version)
except:
	pass
print(PACKAGES)

setup(
    name='ladon',
    packages=PACKAGES,
    package_dir={'':'src'},
    version=VERSION,
    description=SHORT_DESC,
    long_description='\n\n'.join([readme, changes]),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',       
    ],
    keywords= ['ladonize', 'soap', 'json', 'shell', 'rpc', 'wsgi'],
    author='Jakob Simon-Gaarde',
    author_email='jakob@simon-gaarde.dk',
    maintainer = 'Jakob Simon-Gaarde',
    maintainer_email = 'jakob@simon-gaarde.dk',
    url='http://ladonize.org',
    install_requires=['jinja2','sphinx'],
    requires=['jinja2','sphinx'],
    provides=['ladon'],
    license='LGPL3',
    scripts=['scripts/ladon-ctl'],
    zip_safe=False
)

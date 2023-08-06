#!/usr/bin/env python

from distutils.core import setup
from commands import getoutput

version = '1.1'

setup(name='sh_unifi',
      version=version,
      description='Updated API towards Ubiquiti Networks UniFi controller',
      author='Original: Jakob Borg, forked by Social Hotspot',
      author_email='info@socialhotspot.nl',
      url='https://github.com/SocialHotspot/unifi-api',
      packages=['sh_unifi'],
     )

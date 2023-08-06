#!/usr/bin/env python

from distutils.core import setup
from commands import getoutput

version = '1.1'

setup(name='unifi-sh',
      version=version,
      description='Updated API towards Ubiquity Networks UniFi controller',
      author='Original: Jakob Borg, forked by Social Hotspot',
      author_email='info@socialhotspot.nl',
      url='https://github.com/SocialHotspot/unifi-api',
      packages=['unifi-sh'],
     )

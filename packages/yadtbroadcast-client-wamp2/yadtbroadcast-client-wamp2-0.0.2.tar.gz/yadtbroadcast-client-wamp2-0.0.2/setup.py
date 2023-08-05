#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'yadtbroadcast-client-wamp2',
          version = '0.0.2',
          description = '''YADT - an Augmented Deployment Tool - The Broadcast Client Part''',
          long_description = '''Yet Another Deployment Tool - The Broadcast Client Part
- sends state information to a Yadt Broadcast Server instance
- sends information on start/stop/status/update
- using the Wamp v2 protocol
''',
          author = "Arne Hilmann, Maximilien Riehl, Marcel Wolf",
          author_email = "arne.hilmann@gmail.com, max@riehl.io, marcel.wolf@immobilienscout24.de",
          license = 'GNU GPL v3',
          url = 'http://github.com/yadt/yadtbroadcast-client-wamp2',
          scripts = [],
          packages = ['yadtbroadcastclient'],
          py_modules = [],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'License :: OSI Approved :: GNU General Public License (GPL)', 'Programming Language :: Python', 'Topic :: System :: Networking', 'Topic :: System :: Software Distribution', 'Topic :: System :: Systems Administration'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
             # package data
          install_requires = [ "Twisted", "autobahn" ],
          
          zip_safe=True
    )

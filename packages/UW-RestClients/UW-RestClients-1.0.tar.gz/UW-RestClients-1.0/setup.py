#!/usr/bin/env python

# Taken from django's setup.py:

import os

packages, package_data = [], {}

def is_package(package_name):
    return True

def fullsplit(path, result=None):
    """
Split a pathname into components (the opposite of os.path.join)
in a platform-neutral way.
"""
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)



for dirpath, dirnames, filenames in os.walk("userservice"):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_name = '.'.join(parts)
    if '__init__.py' in filenames and is_package(package_name):
        packages.append(package_name)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()
        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])

from distutils.core import setup

setup(name='UW-RestClients',
      packages=['restclients'],
      version='1.0',
      license = "Apache 2.0",
      author = "UW-IT ACA",
      author_email = "pmichaud@uw.edu",
      package_data = package_data,
      url='https://github.com/uw-it-aca/uw-restclients',
      description='Clients for a variety of RESTful web services at the University of Washington',
      install_requires=['Django', 'lxml==2.3.5', 'urllib3>=1.6', 'twilio==3.4.1', 'boto', 'simplejson>=2.1', 'djangorestframework>=2.0', 'jsonpickle>=0.4.0', 'ordereddict>=1.1', 'python-dateutil>=2.1', 'unittest2>=0.5.1', 'pytz', 'icalendar', 'AuthZ-Group', 'Django-UserService'],
     )

#!/usr/bin/python3.4

'''
Created on Aug 11, 2013

@author: Nicklas Boerjesson
'''

from setuptools import setup

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'source'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'source','mbe'))

from mbe import __release__

if __name__ == "__main__":
    setup(
        name='mbe',
        version=__release__,
        description='MBE is a backend written in Python 3 that provides database access, authentication, access '
                    'control and other features on top of the MongoDB document database.',
        author='Nicklas Boerjesson',
        author_email='nicklas_attheold_optimalbpm.se',
        maintainer='Nicklas Boerjesson',
        maintainer_email='nicklas_attheold_optimalbpm.se',
        long_description="""'MBE is a backend written in Python 3 that provides database access, authentication,
            access control and other features on top of the MongoDB document database.
          """,
        url='https://github.com/OptimalBPM/mbe',
        packages=['mbe', 'mbe.schemas', 'mbe.misc',
                  'mbe.features'],
        package_data = {
            # If any package contains *.txt or *.xml files, include them:
            '': ['*.json', '*.xml', '*.feature']
        },
        license='BSD')

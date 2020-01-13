# -*- coding: utf-8 -*-
"""
bunqexport
"""

import io
import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

with io.open(os.path.join(HERE, 'requirements.txt'), encoding='utf-8') as f:
    REQUIREMENTS = f.readlines()

setup(
    name='bunqexport',
    version='0.0.1',
    description='Convert bunq payments to csv',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/stuertz/pybunqexport',
    author='Jan Stürtz',
    author_email='stuertz@gmail.com',
    license='gpl-3.0',
    # See  https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',
    keywords=('open-banking sepa bunq finance api payment csv lexware '
              'finanzmanager'),
    packages=find_packages(exclude=['tests']),
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': ['nose', 'pre-commit', 'safety', 'flake8', 'pylint',
                'autopep8'],
    },
    entry_points={
        'console_scripts': [
            'bunqexport = bunqexport.export:main',
        ],
    },
    include_package_data=True,
)

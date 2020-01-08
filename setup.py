# -*- coding: utf-8 -*-
"""
A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# To use a consistent encoding
import codecs
import os
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with codecs.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='bunqexport',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.1',

    description='Convert bunq payments to csv',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',

    # The project's main homepage.
    url='https://github.com/stuertz/pybunqexport',

    # Author details
    author='Jan Stürtz',

    # The project's license
    license='gpl-3.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],

    # Require Python version equal or higher than the requested version.
    python_requires='>=3.6',

    # Keywords related to the project
    keywords=('open-banking sepa bunq finance api payment csv lexware '
              'finanzmanager'),

    # Packages of the project. "find_packages()" lists all the project
    # packages.
    packages=find_packages(exclude=['tests']),

    # Run-time dependencies of the project. These will be installed by pip.
    install_requires=['bunq_sdk', 'pandas'],
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

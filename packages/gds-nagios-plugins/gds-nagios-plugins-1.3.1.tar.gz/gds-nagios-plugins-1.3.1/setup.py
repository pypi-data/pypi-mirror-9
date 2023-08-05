#!/usr/bin/env python2

import os
from setuptools import setup, find_packages

from plugins import __version__

repo_directory = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(repo_directory, 'README.rst')).read()
except:
    long_description = None

setup(
    name='gds-nagios-plugins',
    version=__version__,
    packages=find_packages(exclude=['test*']),

    author='Tom Booth',
    author_email='tombooth@gmail.com',
    maintainer='Government Digital Service',
    url='https://github.com/alphagov/nagios-plugins',

    description='nagios-plugins: a set of useful nagios plugins',
    long_description=long_description,
    license='MIT',
    keywords='',

    setup_requires=['setuptools-pep8'],
    install_requires=[
        "nagioscheck==0.1.6"
    ],
    tests_require=[
        "nose >=1.3, <1.4",
        "freezegun==0.1.11",
        "httpretty==0.8.3"
    ],

    test_suite='nose.collector',

    entry_points={
        'console_scripts': [
            'check_apt_security_updates='
            'plugins.command.check_apt_security_updates:main',
            'check_reboot_required=plugins.command.check_reboot_required:main',
            'check_puppetdb_ssh_host_keys=plugins.command.check_puppetdb_ssh_host_keys:main',
            'check_elasticsearch=plugins.command.check_elasticsearch:main'
        ]
    }
)

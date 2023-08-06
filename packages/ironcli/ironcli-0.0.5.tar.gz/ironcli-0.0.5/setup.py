# -*- coding: utf-8 -*-
"""
    setup script for Infinisys command line utilities

    usage: sudo python setup.py install
"""

from setuptools import setup


setup(
    name="ironcli",
    version='0.0.5',
    description='Kilatiron command line utilities',
    author='cloudControl Team',
    author_email='info@cloudcontrol.de',
    url='https://www.cloudcontrol.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet'
    ],
    install_requires=['cctrl>=1.15.2'],
    scripts=['src/ironcliapp', 'src/ironcliuser'],
)

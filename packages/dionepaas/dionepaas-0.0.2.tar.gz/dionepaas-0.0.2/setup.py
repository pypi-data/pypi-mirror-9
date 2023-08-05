# -*- coding: utf-8 -*-
"""
    setup script for cloudControl command line utilities

    usage: sudo python setup.py install
"""

from setuptools import setup


setup(
    name="dionepaas",
    version='0.0.2',
    description='cloudControl command line utilities',
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
    scripts=['src/dionepaasapp', 'src/dionepaasuser'],
)

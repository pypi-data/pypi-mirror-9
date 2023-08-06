#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_client import __version__


INSTALL_REQUIRES = [
    'GitPython==0.3.2.RC1',
    'requests>=1',
    'docopt',
    'pyyaml',
]
DEPENDENCY_LINKS = [
    'https://bitbucket.org/pygame/pygame/get/df48571.zip#egg=pygame-1.9.2',
]
EXTRAS_REQUIRE = {
    'gui': [
        'Kivy==1.7.2',
        'plyer==1.2.1',
        'pygame',
    ],
}
try:
    import json
except ImportError:
    INSTALL_REQUIRES.append('simplejson')

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development',
]

setup(
    name='aldryn-client',
    version=__version__,
    description='The command-line client for the Aldryn Cloud',
    author='Divio AG',
    author_email='aldryn@divio.ch',
    url='http://www.aldryn.com/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    platforms=['OS Independent'],
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    dependency_links=DEPENDENCY_LINKS,
    entry_points="""
    [console_scripts]
    aldryn = aldryn_client.cli:main
    """,
)

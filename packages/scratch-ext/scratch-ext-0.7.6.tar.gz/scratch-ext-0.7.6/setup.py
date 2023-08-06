#!/usr/bin/env python
from setuptools import setup, find_packages

try:
    README = open('README.md').read()
except:
    README = None

try: 
    LICENSE = open('LICENSE').read()
except: 
    LICENSE = None

setup(
    name = 'scratch-ext',
    version = '0.7.6',
    description='Access external Scratch sensors and endpoints through python',
    long_description=README,
    author = 'Sander van de Graaf',
    author_email = 'mail@svdgraaf.nl',
    license = LICENSE,
    url = 'http://github.com/bendoobox/scratch-ext/',
    packages = ['scratch-ext'],
    data_files = [
        ('/usr/share/applications/', ['python-scratch-ext.desktop']),
        ('/home/pi/Desktop/', ['python-scratch-ext.desktop']) # only needed for raspbian, this should move to postinst
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
    ],
    install_requires=[],
)

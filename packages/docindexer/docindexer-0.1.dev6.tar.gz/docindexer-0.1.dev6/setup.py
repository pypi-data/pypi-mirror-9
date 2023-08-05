#!/usr/bin/env python

from setuptools import setup, Extension
import os, sys
import urllib

tika_url = "http://mirrors.fe.up.pt/pub/apache/tika/tika-app-1.6.jar"
tika_path = "docindexer/tika/tika-app.jar"

if not os.path.exists(tika_path):
    print("Retrieving Tika JAR from: " + tika_url)
    urllib.urlretrieve(tika_url, tika_path)

setup(
    name='docindexer',
    version='0.1.dev6',
    description=('Document indexer for multiple file formats.'),
    url='https://bitbucket.org/hjalves/docindexer',
    author='Humberto Alves',
    author_email='hjalves@student.dei.uc.pt',
    license='GPL',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        #'Environment :: Console',
        #'Intended Audience :: Science/Research',
        #'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        #'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3.3',
        #'Programming Language :: Python :: 3.4',
        #'Topic :: Scientific/Engineering',
    ],
    keywords='document indexer',
    packages=[
        'docindexer',
        'docindexer.tika',
    ],
    package_data={
        'docindexer.tika': ['tika-app.jar'],
    },
    install_requires=[
        'Whoosh',
    ],
    include_package_data=True,
    zip_safe=False,
)

#!/usr/bin/env python

import os
import zipfile

from distutils.core import setup

zf = zipfile.ZipFile(os.path.join('pyaas', 'skel.zip'), 'w')
for base,directories,filenames in os.walk('skel'):
    for filename in filenames:
        path = os.path.join(base, filename)
        zf.write(path, path[5:])
zf.close()

# Python 3 compatible
with open('pyaas/util.py') as f:
    exec(compile(f.read(), 'util.py', 'exec'))
version_file = generate_version_file(infile='pyaas/version.py.in', outfile='pyaas/version.py', version='0.5.15')
if not version_file:
    raise Exception('Failed to generate version file!')
with open(version_file) as f:
    exec(compile(f.read(), version_file, 'exec'))

setup(
    name='pyaas',
    version=VERSION,
    author='Matthew Oertle',
    author_email='moertle@gmail.com',
    url='https://github.com/moertle/pyaas',
    license='MIT',
    description='Python-as-a-Service is a set of utilities for quickly creating Tornado applications.',
    long_description=open('README.rst').read(),
    packages=[
        'pyaas',
        # web service components
        'pyaas.web',
        'pyaas.web.auth',
        'pyaas.web.handlers',
        # storage components
        'pyaas.storage',
        'pyaas.storage.engines',
        # cache components
        'pyaas.storage.cache',
    ],
    package_data={
        'pyaas': ['skel.zip']
    },
    install_requires=[
        "tornado >= 4.0.1",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    zip_safe=False
)

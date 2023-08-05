#!/usr/bin/env python

from setuptools import setup
import os


def readme(fname):
    md = open(os.path.join(os.path.dirname(__file__), fname)).read()
    output = md
    try:
        import pypandoc
        output = pypandoc.convert(md, 'rst', format='md')
    except ImportError:
        pass
    return output

setup(
    name='cjdnsadmin',
    version='0.1.5',
    description='A library to interact with the cjdns Admin Interface',
    long_description=readme('README.md'),
    url='https://github.com/thefinn93/cjdnsadmin',
    author='Finn Herzfeld',
    author_email='finn@seattlemesh.net',
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Topic :: System :: Networking'
    ],
    keywords='cjdns',
    packages=['cjdnsadmin'],
    scripts=['util/peerStats']
)

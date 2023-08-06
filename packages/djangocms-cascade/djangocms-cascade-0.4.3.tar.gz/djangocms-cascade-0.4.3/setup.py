#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from cmsplugin_cascade import __version__


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
]

def read(fname):
    readme_file = os.path.join(os.path.dirname(__file__), fname)
    return os.popen('[ -x "$(which pandoc 2>/dev/null)" ] && pandoc -t rst {0} || cat {0}'.format(readme_file)).read()

setup(
    name='djangocms-cascade',
    version=__version__,
    description='Collection of plugins for DjangoCMS >3.0 to add various HTML elements from CSS frameworks to any CMS placeholder',
    author='Jacob Rief',
    author_email='jacob.rief@gmail.com',
    url='https://github.com/jrief/djangocms-cascade',
    packages=find_packages(exclude=['examples', 'docs']),
    install_requires=['jsonfield'],
    license='LICENSE-MIT',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    long_description=read('README.md'),
    include_package_data=True,
    zip_safe=False,
)

#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

import os
import aj

__requires = filter(None, open('requirements.txt').read().splitlines())

plugin_name = 'core'
version = '0.1'

setup(
    name='ajenti.plugin.%s' % plugin_name,
    version=version,
    install_requires=__requires,
    description='Ajenti %s plugin' % plugin_name,
    author='Eugene Pankov',
    author_email='e@ajenti.org',
    url='http://ajenti.org/',
    packages=find_packages(),
)

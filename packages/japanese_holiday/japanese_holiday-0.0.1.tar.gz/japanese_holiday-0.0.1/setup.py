# -*- coding:utf-8 -*-
import os
try:
    import setuptools
    from setuptools import setup, find_packages
except ImportError:
  print("Please install setuptools.")

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requirements = [
]

tests_require = [
]

entry_points = {
    'console_scripts': [
    ],
}

import info
import version
setup_options = info.INFO
setup_options['version'] = version.VERSION


setup_options.update(dict(
    install_requires    = open('requirements.txt').read().splitlines(),
    packages            = find_packages('src'),
    package_dir         = {'': 'src'},
    long_description    = README + '\n\n' + CHANGES,
    tests_require       = tests_require,
    entry_points        = entry_points,
))

setup(**setup_options)
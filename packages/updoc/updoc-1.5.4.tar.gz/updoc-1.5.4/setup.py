# -*- coding: utf-8 -*-
import codecs
import os.path
import sys
from updoc import __version__ as version
from setuptools import setup, find_packages
__author__ = "flanker"


commands = filter(lambda x: x[0:1] != '-', sys.argv)

readme = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.isfile(readme):
    with codecs.open(readme, 'r', encoding='utf-8') as fd:
        long_description = fd.read()
else:
    long_description = ''

ext_modules = []
cmdclass = {}
entry_points = {"console_scripts": ["updoc-manage = updoc.djangoproject.manage:main", ], }

setup(
    name='updoc',
    version=version,
    description='Django-based website for HTML or Markdown docs.',
    long_description=long_description,
    author="flanker",
    author_email="flanker@19pouces.net",
    license="CeCILL-B",
    url="http://19pouces.net/Updoc.html",
    entry_points=entry_points,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='updoc.tests',
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    install_requires=['setuptools>=0.7', 'django', 'django-bootstrap3', 'django-admin-bootstrapped',
                      'elasticsearch', 'requests'],
    setup_requires=[],
    classifiers=['Programming Language :: Python', 'Programming Language :: Python :: 3', ]
)
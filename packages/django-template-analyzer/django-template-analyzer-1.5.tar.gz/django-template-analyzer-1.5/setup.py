#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path
import codecs
import re


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-template-analyzer',
    version=find_version('template_analyzer', '__init__.py'),
    license='BSD License',
    platforms=['OS Independent'],

    description='Django Template Analyzer - Extract template nodes from a Django template',
    long_description=read('README.rst'),

    author='Diederik van der Boor & Django CMS developers',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-template-analyzer',
    download_url='https://github.com/edoburu/django-template-analyzer/zipball/master',

    packages=find_packages(),
    include_package_data=True,

    test_suite = 'runtests',

    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Framework :: Django',
        'Framework :: Django :: 1.4',
        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

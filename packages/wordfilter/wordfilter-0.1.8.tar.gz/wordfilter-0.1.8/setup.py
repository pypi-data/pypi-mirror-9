#!/usr/bin/env python
from setuptools import setup

try:
    from pypandoc import convert

    def read_md(f):
        try:
            return convert(f, 'rst')
        except IOError:
            return ''

except ImportError:
    print("pypandoc module not found, could not convert Markdown to RST")

    def read_md(f):
        try:
            return open(f, 'r').read()
        except IOError:
            return ''


setup(
    name=u'wordfilter',

    version='0.1.8',

    description="A small module meant for use in text generators that lets you filter strings for bad words.",

    long_description=read_md('readme.md'),

    author=u'Darius Kazemi',

    author_email=u'darius.kazemi@gmail.com',

    url='http://tinysubversions.com',

    license='MIT',

    package_dir={'wordfilter': 'lib/wordfilter'},

    packages=['wordfilter'],

    zip_safe=False,

    package_data={
        'wordfilter': ['../badwords.json']
    },

    classifiers=[
        "Programming Language :: Python",
    ],
)

# coding:utf-8
import codecs
import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


NAME = "memcache_clone"

PACKAGES = ["memcache_clone", ]

DESCRIPTION = "Clone memcache data to othor memcahe ."

LONG_DESCRIPTION = read("README")

KEYWORDS = "memcache clone package"

AUTHOR = "lingchang"
AUTHOR_EMAIL = "freelingchang@email.com"

URL = "https://github.com/freelingchang/memcache_clone"

VERSION = "1.0.3"

LICENSE = "MIT"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=True,
)

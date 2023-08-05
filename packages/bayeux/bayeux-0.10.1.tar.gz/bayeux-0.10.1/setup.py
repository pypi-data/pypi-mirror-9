# coding: utf-8
from setuptools import setup
import os
import sys
requires_list = ["yamlish"]
if sys.version_info <= (2, 6):
    requires_list.append("unittest2")


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as inf:
        return "\n" + inf.read().replace("\r\n", "\n")

setup(
    name='bayeux',
    version="0.10.1",
    description='Generator of the TAP protocol',
    author=u'Matěj Cepl',
    author_email='mcepl@cepl.eu',
    url='https://github.com/mcepl/bayeux',
    py_modules=['tap', 'unittest_TAP'],
    scripts=['generate_TAP'],
    long_description=read("README.rst"),
    keywords=['TAP', 'unittest'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    test_suite="test.test_tap",
    install_requires=requires_list,
)

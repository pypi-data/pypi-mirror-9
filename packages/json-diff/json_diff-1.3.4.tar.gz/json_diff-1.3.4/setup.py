# coding: utf-8
from setuptools import setup
import os.path
import json_diff


def read(fname):
    f = open(os.path.join(os.path.dirname(__file__), fname))
    out = "\n" + f.read().replace("\r\n", "\n")
    f.close()
    return out


def get_long_description():
    return read("README.txt") \
        + "\nChangelog:\n" + "=" * 10 + "\n" \
        + read("NEWS.txt")

setup(
    name='json_diff',
    version='%s' % json_diff.__version__,
    description='Generates diff between two JSON files',
    author='Matěj Cepl',
    author_email='mcepl@redhat.com',
    url='https://fedorahosted.org/json_diff/',
    py_modules=['json_diff'],
    long_description=get_long_description(),
    keywords=['json', 'diff'],
    test_suite='test.test_json_diff',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
    ]
)

#!/usr/bin/env python
"""AsyncDB.

    Asynchronous library for data source connections, used by Navigator.
See:
https://github.com/phenobarbital/asyncdb
"""
from os import path
from setuptools import find_packages, setup


def get_path(filename):
    return path.join(path.dirname(path.abspath(__file__)), filename)


with open(get_path('README.md')) as readme:
    README = readme.read()

with open(get_path('asyncdb/version.py')) as meta:
    exec(meta.read())

setup(
    name="asyncdb",
    version=__version__,
    python_requires=">=3.8.0",
    url="https://github.com/phenobarbital/asyncdb",
    description=__description__,
    platforms=['POSIX'],
    long_description=README,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3.8",
    ],
    author=__author__,
    author_email=__author_email__,
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    license=__license__,
    setup_requires=[
        "wheel==0.37.0",
        "Cython==0.29.28",
        "numpy==1.21.1",
        "asyncio==3.4.3",
        "cchardet==2.1.7",
        'cryptography==3.4.7',
        "cpython==0.0.6"
    ],
    install_requires=[
        "wheel==0.37.0",
        "cpython==0.0.6",
        "Cython==0.29.28",
        "numpy==1.22.2",
        "cryptography==3.4.7",
        "aiohttp==3.8.1",
        "asyncpg==0.24.0",
        "uvloop==0.16.0",
        "asyncio==3.4.3",
        "cchardet==2.1.7",
        "objectpath==0.6.1",
        "jinja2==3.0.3",
        "jsonpath-rw==1.4.0",
        "jsonpath-rw-ext==1.2.2",
        "dateparser==1.0.0",
        "rapidjson==1.0.0",
        "python-rapidjson>=1.5",
        "typing_extensions>=3.10.0.2",
        "async-generator==1.10",
        "charset-normalizer>=2.0.7",
        "et-xmlfile>=1.1.0",
        "ciso8601==2.2.0",
        "iso8601==0.1.13",
        "async-timeout==4.0.2",
        "aiopg==1.3.3",
        "tabulate==0.8.7",
        "python-magic==0.4.18",
        "psycopg2-binary>=2.9.1",
        "pgpy==0.5.3",
        "botocore==1.19.29",
        "boto3==1.16.29",
        "xlrd==2.0.1",
        "bs4==0.0.1",
        "beautifulsoup4>=4.10.0",
        "pylibmc==1.6.1",
        "redis==3.5.3",
        "aioredis==2.0.1",
        "rethinkdb==2.4.8",
        "lxml>=4.6.2",
        "pandas==1.4.1",
        "dask==2022.2.0",
        "datatable==1.0.0",
        "polars==0.8.10",
        "py-polars==0.8.10",
        "pyarrow==4.0.1",
        "connectorx==0.2.3",
        "openpyxl==3.0.9",
        "pymssql==2.2.1",
        "pymongo>=3.12.1",
        "motor==2.5.1",
        "elasticsearch[async]==7.15.1",
        "hiredis==2.0.0",
        "aiomcache==0.7.0",
        "aiosqlite>=0.15.0",
        "asyncio_redis>=0.16.0",
        "sqlalchemy==1.3.20",
        "sqlalchemy-aio==0.16.0",
        "aioodbc==0.3.3",
        "pyodbc==4.0.30",
        "lz4==4.0.0",
        "scales==1.0.9",
        "cassandra-driver==3.25.0",
        "influxdb-client==1.26.0",
        "rx==3.2.0"
    ],
    tests_require=[
        'pytest>=6.0.0',
        'pytest-asyncio==0.18.0',
        'pytest-xdist==2.1.0',
        'pytest-assume==2.4.2'
    ],
    project_urls={  # Optional
        "Source": "https://github.com/phenobarbital/asyncdb",
        "Funding": "https://paypal.me/phenobarbital",
        "Say Thanks!": "https://saythanks.io/to/phenobarbital",
    },
)

#!/usr/bin/env python
"""AsyncDB.

    Asynchronous library for data source connections, used by Navigator.
See:
https://github.com/phenobarbital/asyncdb
"""

from setuptools import find_packages, setup

setup(
    name="asyncdb",
    version=open("VERSION").read().strip(),
    python_requires=">=3.8.0",
    url="https://github.com/phenobarbital/asyncdb",
    description="Asyncio Datasource library",
    long_description="Asynchronous library for data source connections, \
    used by Navigator",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3.8",
    ],
    author="Jesus Lara",
    author_email="jlara@trocglobal.com",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    setup_requires=[
        "wheel==0.37.0",
        "Cython==0.29.21",
        "numpy==1.19.4",
        "asyncio==3.4.3",
        "cchardet==2.1.7",
        'cryptography==3.4.7'
    ],
    install_requires=[
        "wheel==0.37.0",
        "Cython==0.29.21",
        "numpy==1.21.1",
        'cryptography==3.4.7',
        "asyncpg==0.24.0",
        "cchardet==2.1.7",
        "asyncio==3.4.3",
        "PyDrive==1.3.1",
        "uvloop==0.14.0",
        "cryptography==3.4.7",
        "objectpath==0.6.1",
        "MarkupSafe==1.1.1",
        "jinja2==2.11.3",
        "requests==2.26.0",
        "jsonpath-rw==1.4.0",
        "jsonpath-rw-ext==1.2.2",
        "dateparser==1.0.0",
        "iso8601==0.1.13",
        "aiopg==1.3.1",
        "tqdm==4.51.0",
        "tabulate==0.8.7",
        "python-magic==0.4.18",
        "pgpy==0.5.3",
        "botocore==1.19.29",
        "boto3==1.16.29",
        "xlrd==1.2.0",
        "bs4==0.0.1",
        "beautifulsoup4==4.10.0",
        "soupsieve==2.2.1",
        "pylibmc==1.6.1",
        "redis==3.5.3",
        "aioredis==2.0.0",
        "rethinkdb==2.4.8",
        "lxml>=4.6.2",
        "isodate==0.6.0",
        "pandas==1.3.1",
        "dask==2.30.0",
        "xlrd==1.2.0",
        "openpyxl==3.0.6",
        "hiredis==2.0.0",
        "aiomcache==0.6.0",
        "aiosqlite==0.15.0",
        "asyncio_redis==0.16.0",
        "sqlalchemy==1.3.20",
        "sqlalchemy-aio==0.16.0",
        "attrs==20.2.0",
        "aioodbc==0.3.3",
        "pyodbc==4.0.30",
        "aiocassandra==2.0.1",
        "cassandra-driver==3.25.0",
        "aioinflux[pandas]",
        "pymssql==2.2.1",
        "motor==2.3.0",
        "elasticsearch[async]==7.15.1",
        "python-rapidjson==0.9.3",
        "rapidjson==1.0.0",
        "typing-extensions==3.10.0.2",
        "aredis==1.1.8"
    ],
    tests_require=[
        'pytest>=6.0.0',
        'pytest-asyncio==0.14.0',
        'pytest-xdist==2.1.0',
        'pytest-assume==2.4.2'
    ],
    project_urls={  # Optional
        "Source": "https://github.com/phenobarbital/asyncdb",
        "Funding": "https://paypal.me/phenobarbital",
        "Say Thanks!": "https://saythanks.io/to/phenobarbital",
    },
)

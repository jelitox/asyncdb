#!/usr/bin/env python3

import asyncio
import json
import time
from datetime import datetime

from pymssql import _mssql

from asyncdb.exceptions import (
    ConnectionTimeout,
    DataError,
    EmptyStatement,
    NoDataFound,
    ProviderError,
    StatementError,
    TooManyConnections,
)
from asyncdb.providers import (
    BaseProvider,
    registerProvider,
)
from asyncdb.utils import (
    EnumEncoder,
    SafeDict,
)

class mssql(BaseProvider):
    """mssql.

    Microsoft SQL Server using low-level _mssql
    """
    _provider = "sqlserver"
    _dsn = ""
    _syntax = "sql"
    _test_query = "SELECT 1"
    _parameters = ()
    _initialized_on = None
    _query_raw = "SELECT {fields} FROM {table} {where_cond}"
    _timeout: int = 5
    _version: str = None

    def __init__(self, loop=None, pool=None, params={}, **kwargs):
        super(mssql, self).__init__(loop=loop, params=params, **kwargs)
        asyncio.set_event_loop(self._loop)
        try:
            if 'host' in self._params:
                self._hosts = self._params['host'].split(',')
        except Exception as err:
            self._hosts = ['127.0.0.1']
        print('HOSTS ', self._hosts)
        try:
            self._auth = {
                "username": self._params["username"],
                "password": self._params["password"]
            }
        except KeyError:
            pass

"""
Registering this Provider
"""

registerProvider(mssql)

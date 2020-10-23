#!/usr/bin/env python3
import os
import asyncio
import aiosqlite
import time
from typing import Any, Generator

from asyncdb.providers import BasePool, BaseProvider, registerProvider
from asyncdb.exceptions import (
    ConnectionTimeout,
    DataError,
    EmptyStatement,
    NoDataFound,
    ProviderError,
    StatementError,
    TooManyConnections,
)

class sqlite(BaseProvider):
    _provider = "sqlite"
    _syntax = "sql"
    _test_query = "SELECT 1"
    _dsn = "{database}"
    _prepared = None
    _initialized_on = None
    _query_raw = "SELECT {fields} FROM {table} {where_cond}"


    """
    Context magic Methods
    """

    # def __await__(self) -> Generator[Any, None, "sqlite"]:
    #     return self.connection().__await__()

    async def __aenter__(self) -> "sqlite":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        return await self.close()

    async def prepare(self):
        pass

    async def close(self, timeout=5):
        """
        Closing Method for SQLite
        """
        try:
            if self._connection:
                if self._cursor:
                    await self._cursor.close()
                await asyncio.wait_for(self._connection.close(), timeout=timeout)
        except Exception as err:
            raise ProviderError("Close Error: {}".format(str(err)))
        finally:
            self._connection = None
            self._connected = False
            return True

    async def connection(self, **kwargs):
        """
        Get a connection
        """
        self._connection = None
        self._connected = False
        try:
            self._connection = await aiosqlite.connect(
                database=self._dsn,
                loop=self._loop,
                **kwargs
            )
            if self._connection:
                if callable(self.init_func):
                    try:
                        await self.init_func(self._connection)
                    except Exception as err:
                        print("Error on Init Connection: {}".format(err))
                self._connected = True
                self._initialized_on = time.time()
        except aiosqlite.OperationalError:
            raise ProviderError("Unable to Open Database File: {}".format(self._dsn))
        except aiosqlite.DatabaseError as err:
            print("Connection Error: {}".format(str(err)))
            raise ProviderError("Database Connection Error: {}".format(str(err)))
        except aiosqlite.Error as err:
            raise ProviderError("Internal Error: {}".format(str(err)))
        except Exception as err:
            raise ProviderError("SQLite Unknown Error: {}".format(str(err)))
        finally:
            return self


    async def release(self):
        """
        Release a Connection
        """
        await self.close()

    async def query(self, sentence:str = Any):
        """
        Getting a Query from Database
        """
        #TODO: getting aiosql structures or sql-like function structures or query functions
        error = None
        self._result = None
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        if not self._connection:
            await self.connection()
        try:
            self._cursor = await self._connection.execute(sentence)
            self._result = await self._cursor.fetchall()
            if not self._result:
                return [None, NoDataFound]
        except Exception as err:
            error = "Error on Query: {}".format(str(err))
            raise ProviderError(error)
        finally:
            await self._cursor.close()
            return [self._result, error]

    async def queryrow(self, sentence:str = Any):
        """
        Getting a Query from Database
        """
        #TODO: getting aiosql structures or sql-like function structures or query functions
        error = None
        self._result = None
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        if not self._connection:
            await self.connection()
        try:
            self._cursor = await self._connection.execute(sentence)
            self._result = await self._cursor.fetchone()
            if not self._result:
                return [None, NoDataFound]
        except Exception as err:
            error = "Error on Query: {}".format(str(err))
            raise ProviderError(error)
        finally:
            await self._cursor.close()
            return [self._result, error]

    async def execute(self, sentence:str = Any):
        """Execute a transaction
        get a SQL sentence and execute
        returns: results of the execution
        """
        error = None
        result = None
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        if not self._connection:
            await self.connection()
        try:
            result = await self._connection.execute(sentence)
            if result:
                await self._connection.commit()
        except Exception as err:
            error = "Error on Query: {}".format(str(err))
            raise ProviderError(error)
        finally:
            await self._cursor.close()
            return [result, error]

    async def executemany(self, sentence:str, *args):
        error = None
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        if not self._connection:
            await self.connection()
        try:
            result = await self._connection.executemany(sentence, *args)
            if result:
                await self._connection.commit()
        except Exception as err:
            error = "Error on Query: {}".format(str(err))
            raise ProviderError(error)
        finally:
            await self._cursor.close()
            return [result, error]

# Registering this Provider
registerProvider(sqlite)

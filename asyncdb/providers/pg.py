""" pg PostgreSQL Provider.
Notes on pg Provider
--------------------
This provider implements all funcionalities from asyncpg (cursors, transactions, copy from and to files, pools, native data types, etc)
"""

import logging
from datetime import datetime
import time
import json

import asyncio
import asyncpg
from asyncpg.exceptions import TooManyConnectionsError, InternalClientError, ConnectionDoesNotExistError, InterfaceError, InterfaceWarning, PostgresError, PostgresSyntaxError, FatalPostgresError, UndefinedColumnError

from asyncdb.providers import BasePool, BaseProvider, registerProvider, exception_handler

from asyncdb.providers.exceptions import EmptyStatement, ConnectionTimeout, ProviderError, NoDataFound, StatementError, TooManyConnections, DataError
from asyncdb.utils import EnumEncoder, SafeDict

logger = logging.getLogger(__name__)

class pgPool(BasePool):
    _max_queries = 300
    _dsn = 'postgres://{user}:{password}@{host}:{port}/{database}'

    def __init__(self, dsn='', loop=None, params={}):
        super(pgPool, self).__init__(dsn=dsn, loop=loop, params=params)
        if loop:
            loop.set_exception_handler(exception_handler)

    def get_event_loop(self):
        return self._loop

    async def init_connection(self, connection):
        # Setup jsonb encoder/decoder
        def _encoder(value):
            return json.dumps(value, cls=EnumEncoder)
        def _decoder(value):
            return json.loads(value)
        await connection.set_type_codec('json', encoder=_encoder, decoder=_decoder, schema='pg_catalog')
        await connection.set_type_codec('jsonb', encoder=_encoder, decoder=_decoder, schema='pg_catalog' )
        await connection.set_builtin_type_codec('hstore', codec_name='pg_contrib.hstore')


    '''
    __init async db initialization
    '''
    # Create a database connection pool
    async def connect(self):
        logger.debug("AsyncPg: Connecting to {}".format(self._dsn))
        try:
            # TODO: pass a setup class for set_builtin_type_codec and a setup for add listener
            self._pool = await asyncpg.create_pool(
                dsn=self._dsn,
                max_size=self._max_queries,
                min_size=2,loop=self._loop,
                max_inactive_connection_lifetime=100,
                command_timeout= self._timeout,
                init=self.init_connection
            )
        except TooManyConnectionsError as err:
            print("Too Many Connections Error: {}".format(str(err)))
            raise TooManyConnections(str(err))
            return False
        except TimeoutError as err:
            raise ConnectionTimeout("Unable to connect to database: {}".format(str(err)))
        except ConnectionRefusedError as err:
            raise ProviderError("Unable to connect to database, connection Refused: {}".format(str(err)))
        except ConnectionDoesNotExistError as err:
            raise ProviderError("Connection Error: {}".format(str(err)))
            return False
        except InternalClientError as err:
            raise ProviderError("Internal Error: {}".format(str(err)))
            return False
        except InterfaceError as err:
            raise ProviderError("Interface Error: {}".format(str(err)))
            return False
        except InterfaceWarning as err:
            print("Interface Warning: {}".format(str(err)))
            return False
        except Exception as err:
            raise ProviderError("Unknown Error: {}".format(str(err)))
            return False
        # is connected
        if self._pool:
            self._connected = True
            self._initialized_on = time.time()


    """
    Take a connection from the pool.
    """
    async def acquire(self):
        db = None
        self._connection = None
        # Take a connection from the pool.
        try:
            self._connection = await self._pool.acquire()
        except TooManyConnectionsError as err:
            print("Too Many Connections Error: {}".format(str(err)))
            return False
        except ConnectionDoesNotExistError as err:
            print("Connection Error: {}".format(str(err)))
            return False
        except InternalClientError as err:
            print("Internal Error: {}".format(str(err)))
            return False
        except InterfaceError as err:
            print("Interface Error: {}".format(str(err)))
            return False
        except InterfaceWarning as err:
            print("Interface Warning: {}".format(str(err)))
            return False
        if self._connection:
            db = pg(pool=self)
            db.set_connection(self._connection)
        return db


    """
    Release a connection from the pool
    """
    async def release(self, connection = None, timeout = 10):
        if not connection:
            conn = self._connection
        else:
            conn = connection
        try:
            release = asyncio.create_task(self._pool.release(conn, timeout = 10))
            #await self._pool.release(connection, timeout = timeout)
            release = asyncio.ensure_future(release, loop=self._loop)
            await asyncio.wait_for(release, timeout = timeout, loop=self._loop)
            #await release
        except InterfaceError as err:
            raise ProviderError("Release Interface Error: {}".format(str(err)))
        except Exception as err:
            raise ProviderError("Release Error: {}".format(str(err)))


    """
    close
        Close Pool Connection
    """
    async def wait_close(self, gracefully = True):
        if self._pool:
            logger.debug("AsyncPg: Closing Pool")
            # try to closing main connection
            try:
                if self._connection:
                    await self._pool.release(self._connection, timeout = 2)
            except InterfaceError as err:
                raise ProviderError("Release Interface Error: {}".format(str(err)))
            except Exception as err:
                raise ProviderError("Release Error: {}".format(str(err)))
            # at now, try to closing pool
            try:
                await self._pool.close()
                #await self._pool.terminate()
            except Exception as err:
                print("Pool Error: {}".format(str(err)))
                await self._pool.terminate()
                raise ProviderError("Pool Error: {}".format(str(err)))
            finally:
                self._pool = None

    """
    Close Pool
    """
    async def close(self):
        try:
            if self._connection:
                await self._pool.release(self._connection, timeout = 2)
        except InterfaceError as err:
            raise ProviderError("Release Interface Error: {}".format(str(err)))
        except Exception as err:
            raise ProviderError("Release Error: {}".format(str(err)))
        try:
            await self._pool.close()
        except Exception as err:
            print("Pool Closing Error: {}".format(str(err)))
            self._pool.terminate()


    def terminate(self, gracefully = True):
        self._loop.run_until_complete(asyncio.wait_for(self.close(), timeout = 5))

    """
    Execute a connection into the Pool
    """
    async def execute(self, sentence, *args):
        if self._pool:
            try:
                result = await self._pool.execute(sentence, *args)
                return result
            except InterfaceError as err:
                raise ProviderError("Execute Interface Error: {}".format(str(err)))
            except Exception as err:
                raise ProviderError("Execute Error: {}".format(str(err)))


class pg(BaseProvider):
    _provider = 'postgresql'
    _syntax = 'sql'
    _test_query = "SELECT 1"
    _dsn = 'postgres://{user}:{password}@{host}:{port}/{database}'
    _loop = None
    _pool = None
    _connection = None
    _connected = False
    _prepared = None
    _parameters = ()
    _cursor = None
    _transaction = None
    _initialized_on = None
    _query_raw = 'SELECT {fields} FROM {table} {where_cond}'

    def __init__(self, dsn='', loop=None, pool=None, params={}):
        super(pg, self).__init__(dsn=dsn, loop=loop, params=params)
        asyncio.set_event_loop(self._loop)
        self._loop.set_exception_handler(exception_handler)
        self._loop.set_debug(self._DEBUG)

    async def close(self, timeout = 5):
        """
        Closing a Connection
        """
        try:
            if self._connection:
                if not self._connection.is_closed():
                    logger.debug("Closing Connection, id: {}".format(self._connection.get_server_pid()))
                    try:
                        if self._pool:
                            await self._pool.pool().release(self._connection)
                        else:
                            await self._connection.close(timeout = timeout)
                    except InterfaceError as err:
                        raise ProviderError("Close Error: {}".format(str(err)))
                    except Exception as err:
                        await self._connection.terminate()
                        self._connection = None
                        raise ProviderError("Connection Error, Terminated: {}".format(str(err)))
        except Exception as err:
            raise ProviderError("Close Error: {}".format(str(err)))
        finally:
            self._connection = None
            self._connected = False

    def terminate(self):
        self._loop.run_until_complete(self.close())

    async def connection(self):
        """
        Get a connection
        """
        self._connection = None
        self._connected = False
        # Setup jsonb encoder/decoder
        def _encoder(value):
            return json.dumps(value, cls=EnumEncoder)

        def _decoder(value):
            return json.loads(value)
        try:
            if self._pool:
                self._connection = await self._pool.pool().acquire()
            else:
                self._connection = await asyncpg.connect(dsn=self._dsn, loop=self._loop, command_timeout= self._timeout)
                await self._connection.set_type_codec('json', encoder=_encoder, decoder=_decoder, schema='pg_catalog')
                await self._connection.set_type_codec('jsonb', encoder=_encoder, decoder=_decoder, schema='pg_catalog' )
                await self._connection.set_builtin_type_codec('hstore', codec_name='pg_contrib.hstore')
            if self._connection:
                self._connected = True
                self._initialized_on = time.time()
        except TooManyConnectionsError as err:
            raise TooManyConnections("Too Many Connections Error: {}".format(str(err)))
        except ConnectionDoesNotExistError as err:
            print("Connection Error: {}".format(str(err)))
            raise ProviderError("Connection Error: {}".format(str(err)))
        except InternalClientError as err:
            print("Internal Error: {}".format(str(err)))
            raise ProviderError("Internal Error: {}".format(str(err)))
        except InterfaceError as err:
            print("Interface Error: {}".format(str(err)))
            raise ProviderError("Interface Error: {}".format(str(err)))
        except InterfaceWarning as err:
            print("Interface Warning: {}".format(str(err)))
        finally:
            return self

    """
    Release a Connection
    """
    async def release(self):
        try:
            if not await self._connection.is_closed():
                if self._pool:
                    release = asyncio.create_task(self._pool.release(self._connection, timeout = 10))
                    asyncio.ensure_future(release, loop=self._loop)
                    return await release
                else:
                    await self._connection.close(timeout = 5)
        except (InterfaceError, RuntimeError) as err:
            raise ProviderError("Release Interface Error: {}".format(str(err)))
            return False
        finally:
            self._connected = False
            self._connection = None


    def prepared_statement(self):
        return self._prepared

    @property
    def connected(self):
        if self._pool:
            return self._pool._connected
        elif self._connection:
            return not self._connection.is_closed()

    """
    Preparing a sentence
    """
    async def prepare(self, sentence=''):
        error = None
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")

        try:
            if not self._connection:
                await self.connection()
            try:
                stmt = await asyncio.shield(self._connection.prepare(sentence))
                try:
                    #print(stmt.get_attributes())
                    self._columns = [a.name for a in stmt.get_attributes()]
                    self._prepared = stmt
                    self._parameters = stmt.get_parameters()
                except TypeError:
                    self._columns = []
            except FatalPostgresError as err:
                error = "Fatal Runtime Error: {}".format(str(err))
                raise StatementError(error)
            except PostgresSyntaxError as err:
                error = "Sentence Syntax Error: {}".format(str(err))
                raise StatementError(error)
            except PostgresError as err:
                error = "PostgreSQL Error: {}".format(str(err))
                raise StatementError(error)
            except RuntimeError as err:
                error = "Prepare Runtime Error: {}".format(str(err))
                raise StatementError(error)
            except Exception as err:
                error = "Unknown Error: {}".format(str(err))
                raise ProviderError(error)
        finally:
            return [self._prepared, error]


    async def query(self, sentence=''):
        error = None
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        if not self._connection:
            await self.connection()
        try:
            startTime = datetime.now()
            #print(timeit.timeit('1 + 3 ', number=50000000))
            self._result = await asyncio.shield(self._connection.fetch(sentence))
            if not self._result:
                raise NoDataFound("Pg: No Data was Found")
                return [None, "Pg: No Data was Found"]
        except RuntimeError as err:
            error = "Runtime Error: {}".format(str(err))
            raise ProviderError(error)
        except (PostgresSyntaxError, UndefinedColumnError, PostgresError) as err:
            error = "Sentence Error: {}".format(str(err))
            self._loop.call_exception_handler(err)
            raise StatementError(error)
        except (asyncpg.exceptions.InvalidSQLStatementNameError, asyncpg.exceptions.UndefinedTableError) as err:
            error = "Invalid Statement Error: {}".format(str(err))
            self._loop.call_exception_handler(err)
            raise StatementError(error)
        except Exception as err:
            error = "Error on Query: {}".format(str(err))
            self._loop.call_exception_handler(err)
            raise Exception(error)
        finally:
            #    self._generated = datetime.now() - startTime
            #    await self.close()
            return [self._result, error]


    async def queryrow(self, sentence=''):
        error = None
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        if not self._connection:
            await self.connection()
        try:
            stmt = await self._connection.prepare(sentence)
            self._columns = [a.name for a in stmt.get_attributes()]
            self._result = await stmt.fetchrow()
        except RuntimeError as err:
            error = "Runtime on Query Row Error: {}".format(str(err))
            raise ProviderError(error)
        except (PostgresSyntaxError, UndefinedColumnError, PostgresError) as err:
            error = "Sentence on Query Row Error: {}".format(str(err))
            self._loop.call_exception_handler(err)
            raise StatementError(error)
        except (asyncpg.exceptions.InvalidSQLStatementNameError, asyncpg.exceptions.UndefinedTableError) as err:
            error = "Invalid Statement Error: {}".format(str(err))
            self._loop.call_exception_handler(err)
            raise StatementError(error)
        except Exception as err:
            error = "Error on Query Row: {}".format(str(err))
            self._loop.call_exception_handler(err)
            raise Exception(error)
        #finally:
            #await self.close()
        return [self._result, error]


    async def execute(self, sentence=''):
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
            return [result, None]
        except InterfaceWarning as err:
            error = "Interface Warning: {}".format(str(err))
            raise ProviderError(error)
            return [None, error]
        except Exception as err:
            error = "Error on Execute: {}".format(str(err))
            self._loop.call_exception_handler(err)
            raise [None, error]
        finally:
            return [result, error]

    async def executemany(self, sentence='', *args):
        error = None
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        if not self._connection:
            await self.connection()
        try:
            async with self._connection.transaction():
                await self._connection.executemany(sentence, args)
        except InterfaceWarning as err:
            error = "Interface Warning: {}".format(str(err))
            raise ProviderError(error)
            return False
        except Exception as err:
            error = "Error on Execute: {}".format(str(err))
            self._loop.call_exception_handler(err)
            raise Exception(error)
        finally:
            return error

    """
    Transaction Context
    """
    async def transaction(self):
        if not self._connection:
            await self.connection()
        self._transaction = self._connection.transaction()
        await self._transaction.start()
        return self

    async def commit(self):
        if self._transaction:
            await self._transaction.commit()

    async def rollback(self):
        if self._transaction:
            await self._transaction.rollback()

    """
    Cursor Context
    """
    async def cursor(self, sentence):
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        if not self._connection:
            await self.connection()
        self._transaction = self._connection.transaction()
        await self._transaction.start()
        self._cursor = await self._connection.cursor(sentence)
        return self

    async def forward(self, number):
        try:
            return await self._cursor.forward(number)
        except Exception as err:
            error = "Error forward Cursor: {}".format(str(err))
            raise Exception(error)

    async def fetch(self, number = 1):
        try:
            return await self._cursor.fetch(number)
        except Exception as err:
            error = "Error Fetch Cursor: {}".format(str(err))
            raise Exception(error)

    async def fetchrow(self):
        try:
            return await self._cursor.fetchrow()
        except Exception as err:
            error = "Error Fetchrow Cursor: {}".format(str(err))
            raise Exception(error)

    """
    Cursor Iterator Context
    """
    def __aiter__(self):
        return self

    async def __anext__(self):
        data = await self._cursor.fetchrow()
        if data is not None:
            return data
        else:
            raise StopAsyncIteration

    """
    COPY Functions
    type: [ text, csv, binary ]
    """
    async def copy_from_table(self, table='', schema='public', output=None, type='csv', columns=None):
        """table_copy
        get a copy of table data into a file, file-like object or a coroutine passed on "output"
        returns: num of rows copied.
        example: COPY 1470
        """
        if not self._connection:
            await self.connection()
        try:
            result = await self._connection.copy_from_table(table_name=table, schema_name=schema, columns=columns, format=type, output=output)
            print(result)
            return result
        except (asyncpg.exceptions.UndefinedTableError):
            error = "Error on Copy, Table doesnt exists: {}".format(str(table))
            raise StatementError(error)
        except (asyncpg.exceptions.InvalidSQLStatementNameError, asyncpg.exceptions.UndefinedTableError) as err:
            error = "Error on Copy, Invalid Statement Error: {}".format(str(err))
            self._loop.call_exception_handler(err)
            raise StatementError(error)
        except Exception as err:
            error = "Error on Table Copy: {}".format(str(err))
            raise Exception(error)

    async def copy_to_table(self, table='', schema='public', source=None, type='csv', columns=None):
        """copy_to_table
        get data from a file, file-like object or a coroutine passed on "source" and copy into table
        returns: num of rows copied.
        example: COPY 1470
        """
        if not self._connection:
            await self.connection()
        try:
            result = await self._connection.copy_to_table(table_name=table, schema_name=schema, columns=columns, format=type, source=source)
            print(result)
            return result
        except (asyncpg.exceptions.UndefinedTableError):
            error = "Error on Copy, Table doesnt exists: {}".format(str(table))
            raise StatementError(error)
        except (asyncpg.exceptions.InvalidSQLStatementNameError, asyncpg.exceptions.UndefinedTableError) as err:
            error = "Error on Copy, Invalid Statement Error: {}".format(str(err))
            self._loop.call_exception_handler(err)
            raise StatementError(error)
        except Exception as err:
            error = "Error on Table Copy: {}".format(str(err))
            raise Exception(error)

    async def copy_into_table(self, table='', schema='public', source=None, columns=None):
        """copy_into_table
        get data from records (any iterable object) and save into table
        returns: num of rows copied.
        example: COPY 1470
        """
        if not self._connection:
            await self.connection()
        try:
            result = await self._connection.copy_records_to_table(table_name=table, schema_name=schema, columns=columns, records=source)
            print(result)
            return result
        except (asyncpg.exceptions.UndefinedTableError):
            error = "Error on Copy, Table doesnt exists: {}".format(str(table))
            raise StatementError(error)
        except (asyncpg.exceptions.InvalidSQLStatementNameError, asyncpg.exceptions.UndefinedTableError) as err:
            error = "Error on Copy, Invalid Statement Error: {}".format(str(err))
            self._loop.call_exception_handler(err)
            raise StatementError(error)
        except (asyncpg.exceptions.UniqueViolationError) as err:
            error = "Error on Copy, Constraint Violated: {}".format(str(err))
            raise DataError(error)
        except Exception as err:
            error = "Error on Table Copy: {}".format(str(err))
            raise Exception(error)

    """
    Meta-Operations
    """

    def table(self, table):
        try:
            return self._query_raw.format_map(SafeDict(table = table))
        except Exception as e:
            print(e)
            return False

    def fields(self, sentence, fields = None):
        _sql = False
        if not fields:
            _sql = sentence.format_map(SafeDict(fields = '*'))
        elif type(fields) == str:
            _sql = sentence.format_map(SafeDict(fields = fields))
        elif type(fields) == list:
            _sql = sentence.format_map(SafeDict(fields = ','.join(fields)))
        return _sql

    """
    where
      add WHERE conditions to SQL
    """
    def where(self, sentence, where):
        sql = ''
        if sentence:
            where_string = ''
            if not where:
                sql = sentence.format_map(SafeDict(where_cond = ''))
            elif type(where) == dict:
                where_cond = []
                for key, value in where.items():
                    #print("KEY {}, VAL: {}".format(key, value))
                    if type(value) == str or type(value) == int:
                        if value == 'null' or value == 'NULL':
                            where_string.append("%s IS NULL" % (key))
                        elif value == '!null' or value == '!NULL':
                            where_string.append("%s IS NOT NULL" % (key))
                        elif key.endswith('!'):
                            where_cond.append("%s != %s" % (key[:-1], value))
                        else:
                            if type(value) == str and value.startswith("'") and value.endswith("'"):
                                where_cond.append("%s = %s" % (key, "{}".format(value)))
                            elif type(value) == int:
                                where_cond.append("%s = %s" % (key, "{}".format(value)))
                            else:
                                where_cond.append("%s = %s" % (key, "'{}'".format(value)))
                    elif type(value) == bool:
                        val = str(value)
                        where_cond.append("%s = %s" % (key, val))
                    else:
                        val = ','.join(map(str, value))
                        if type(val) == str and "'" not in val:
                            where_cond.append("%s IN (%s)" % (key, "'{}'".format(val)))
                        else:
                            where_cond.append("%s IN (%s)" % (key, val))
                #if 'WHERE ' in sentence:
                #    where_string = ' AND %s' % (' AND '.join(where_cond))
                #else:
                where_string = ' WHERE %s' % (' AND '.join(where_cond))
                print("WHERE cond is %s" % where_string)
                sql = sentence.format_map(SafeDict(where_cond = where_string))
            elif type(where) == str:
                where_string = where
                if not where.startswith('WHERE'):
                    where_string = ' WHERE %s' % where
                sql = sentence.format_map(SafeDict(where_cond = where_string))
            else:
                sql = sentence.format_map(SafeDict(where_cond = ''))
            del where
            del where_string
            return sql
        else:
            return False


    def limit(self, sentence, limit = 1):
        """
        LIMIT
          add limiting to SQL
        """
        if sentence:
            return "{q} LIMIT {limit}".format(q=sentence, limit=limit)
        return self


    def orderby(self, sentence, ordering = []):
        """
        LIMIT
          add limiting to SQL
        """
        if sentence:
            if type(ordering) == str:
                return "{q} ORDER BY {ordering}".format(q=sentence, ordering=ordering)
            elif type(ordering) == list:
                return "{q} ORDER BY {ordering}".format(q=sentence, ordering=', '.join(ordering))
        return self


    def get_query(self, sentence):
        """
        get_query
          Get formmated query
        """
        sql = sentence
        try:
            # remove fields and where_cond
            sql = sentence.format_map(SafeDict(fields = '*', where_cond = ''))
            if not self.connected:
                self.connection()
            prepared, error = self._loop.run_until_complete(self.prepare(sql))
            if not error:
                self._columns = self.get_columns()
            else:
                return False
        except (ProviderError, StatementError) as err:
            return False
        except Exception as e:
            print(e)
            return False
        return sql

    def column_info(self, table):
        """
        column_info
          get column information about a table
        """
        discover = "SELECT attname AS column_name, atttypid::regtype AS data_type FROM pg_attribute WHERE attrelid = '{}'::regclass AND attnum > 0 AND NOT attisdropped ORDER  BY attnum".format(table)
        try:
            result, error = self._loop.run_until_complete(self.query(discover))
            if result:
                return result
        except (NoDataFound, ProviderError):
            print(err)
            return False
        except Exception as err:
            print(err)
            return False

    def insert(self, table, data, **kwargs):
        """
        insert
           insert the result onto a table
        """
        sql = 'INSERT INTO {table} ({fields}) VALUES ({values})'
        sql = sql.format_map(SafeDict(table=table))
        # set columns
        sql = sql.format_map(SafeDict(fields=','.join(data.keys())))
        values = ','.join(str(v) for v in data.values())
        sql = sql.format_map(SafeDict(values=values))
        try:
            result = self._loop.run_until_complete(self._connection.execute(sql))
            if not result:
                print(result)
                return False
            else:
                return result
        except Exception as err:
            #print(sql)
            print(err)
            return False

"""
Registering this Provider
"""
registerProvider(pg)

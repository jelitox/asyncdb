""" postgresql, sqlalchemy PostgreSQL Provider.
Notes on sqlalchemy Provider
--------------------
This provider implements a basic set of funcionalities from aiopg sqlalchemy and use threads
"""

import asyncio
import aiopg
from aiopg.sa import create_engine
from psycopg2.extras import NamedTupleCursor

from sqlalchemy.exc import SQLAlchemyError, DatabaseError, OperationalError
from threading import Thread

from . import *
from ..exceptions import EmptyStatement, ConnectionTimeout, ProviderError, NoDataFound, StatementError, TooManyConnections, DataError
from ..utils import EnumEncoder

logger = logging.getLogger(__name__)


class postgresql(BaseProvider, Thread):
    _provider = 'postgresql'
    _syntax = 'sql'
    _test_query = "SELECT 1::integer as column"
    _dsn = 'postgresql://{user}:{password}@{host}:{port}/{database}'
    #_dsn = 'dbname={database} user={user} password={password} host={host} port={port}'
    _loop = None
    _pool = None
    #_engine = None
    _connection = None
    _connected = False
    _initialized_on = None


    def __init__(self, dsn='', loop=None, params={}):
        self._params = params
        if not dsn:
            self._dsn = self.create_dsn(self._params)
        else:
            self._dsn = dsn
        self._result = None
        self._connection = None
        self._engine = None
        self._loop = None
        # create a new loop before thread
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        # calling parent Thread
        Thread.__init__(self)
        self._engine = self.connect()

    def __del__(self):
        self._loop.run_until_complete(self.terminate())

    """
    Context magic Methods
    """
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._loop.run_until_complete(self.release())

    """
    Thread Methodss
    """
    def start(self):
        logging.debug('Running Start')
        Thread.start(self)

    def join(self):
        logging.debug('Running Join')
        Thread.join(self)


    def run(self):
        logging.debug('Running RUN')

    def close(self):
        logging.debug('Running Close')
        if self._loop:
            try:
                self._loop.run_until_complete(asyncio.wait_for(self.terminate(), timeout = 5))
            finally:
                # close loop
                self._loop.close()

    async def terminate(self):
        """
        Closing a Connection
        """
        if self._connection:
            try:
                await self._engine.release(self._connection)
            except Exception as err:
                await self._connection.close()
        if self._engine:
            self._engine.close()
            try:
                await self._engine.wait_closed()
            finally:
                self._engine.terminate()

    def connect(self):
        logging.debug('Running connect')
        try:
            return self._loop.run_until_complete(create_engine(dsn=self._dsn, maxsize=self._max_connections,timeout=self._timeout,loop=self._loop))
            #return self._loop.run_until_complete(aiopg.create_pool(dsn=self._dsn, maxsize=self._max_connections,timeout=self._timeout,loop=self._loop))
        except (SQLAlchemyError, DatabaseError, OperationalError) as err:
            self._engine = None
            raise ProviderError("Connection Error: {}".format(str(err)))
        except Exception as err:
            self._engine = None
            raise ProviderError("Engine Error, Terminated: {}".format(str(err)))


    def connection(self):
        """
        Get a connection
        """
        logger.debug("PostgreSQL: Connecting to {}".format(self._dsn))
        self._connection = None
        self._connected = False
        self.start()
        try:
            if self._engine:
                self._connection = self._loop.run_until_complete(self._engine.acquire())
        except (SQLAlchemyError, DatabaseError, OperationalError) as err:
            self._connection = None
            raise ProviderError("Connection Error: {}".format(str(err)))
        except Exception as err:
            self._connection = None
            raise ProviderError("Engine Error, Terminated: {}".format(str(err)))
        finally:
            return self

    async def release(self):
        """
        Release a Connection object
        """
        try:
            if self._connection:
                if self._engine:
                    await self._engine.release(self._connection)
                else:
                    self._connection.close()
        except Exception as err:
            raise ProviderError("Release Error, Terminated: {}".format(str(err)))
        finally:
            self._connection = None


    async def prepare(self, sentence=''):
        """
        Preparing a sentence
        """
        error = None


    def test_connection(self):
        """
        Test Connnection
        """
        error = None
        row = {}
        if self._test_query is None:
            raise NotImplementedError()
        logger.debug("{}: Running Test".format(self._provider))
        try:
            #cursor = self._loop.run_until_complete(self._connection.cursor(cursor_factory=NamedTupleCursor))
            #self._loop.run_until_complete(cursor.execute(self._test_query))
            result = self._loop.run_until_complete(self._connection.execute(self._test_query))
            row = self._loop.run_until_complete(result.fetchone())
            if row:
                row = dict(row)
            #print(cursor.description)
            #row = dict()
            #print(row)
            #cursor.close()
            if error:
                logger.debug("Test Error: {}".format(error))
        except Exception as err:
            error = str(err)
            raise ProviderError(message = str(err), code = 0)
        finally:
            return [ row, error ]


    @asyncio.coroutine
    async def query(self, sentence=''):
        """
        Running a Query
        """
        error = None
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        try:
            logger.debug('Running Query {}'.format(sentence))
            result = await self._connection.execute(sentence)
            if result:
                rows = await result.fetchall()
                self._result = [dict(row.items()) for row in rows]
        except (DatabaseError, OperationalError) as err:
            error = "Query Error: {}".format(str(err))
            raise ProviderError(error)
        except Exception as err:
            error = "Query Error, Terminated: {}".format(str(err))
            raise ProviderError(error)
        finally:
            return [self._result, error]


    async def queryrow(self, sentence=''):
        """
        Running Query and return only one row
        """
        error = None
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        try:
            logger.debug('Running Query {}'.format(sentence))
            result = await self._connection.execute(sentence)
            if result:
                row = await result.fetchone()
                self._result = dict(row)
        except (DatabaseError, OperationalError) as err:
            error = "Query Row Error: {}".format(str(err))
            raise ProviderError(error)
        except Exception as err:
            error = "Query Row Error, Terminated: {}".format(str(err))
            raise ProviderError(error)
        finally:
            return [self._result, error]


    async def execute(self, sentence=''):
        """Execute a transaction
        get a SQL sentence and execute
        returns: results of the execution
        """
        error = None
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        if not self._connection:
            self.connection()
        try:
            logger.debug('Execute Sentence {}'.format(sentence))
            result = await self._engine.execute(sentence)
            self._result = result
        except (DatabaseError, OperationalError) as err:
            error = "Execute Error: {}".format(str(err))
            raise ProviderError(error)
        except Exception as err:
            error = "Execute Error, Terminated: {}".format(str(err))
            raise ProviderError(error)
        finally:
            return [self._result, error]


    """
    Cursor Context
    """
    async def cursor(self, sentence):
        if not sentence:
            raise EmptyStatement("Sentence is an empty string")
        logger.debug('Creating Cursor {}'.format(sentence))
        self._cursor = await self._connection.execute(sentence)
        #self._cursor = await self._connection.cursor(cursor_factory=NamedTupleCursor)
        #await self._cursor.execute(sentence)
        return self

    """
    Cursor Iterator Context
    """
    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            data = dict(await self._cursor.fetchone())
            if data is not None:
                return data
            else:
                raise StopAsyncIteration
        except TypeError:
            raise StopAsyncIteration

    """
    Fetching a Cursor
    """
    async def fetchrow(self):
        pass


    async def fetch(self, number = 1):
        pass


"""
Registering this Provider
"""
registerProvider(postgresql)

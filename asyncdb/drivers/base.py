# -*- coding: utf-8 -*-
import asyncio
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Optional,
    Any
)
from collections.abc import Callable, Iterable
from asyncdb.exceptions import EmptyStatement
from asyncdb.models import Model
from asyncdb.interfaces import (
    PoolBackend,
    ConnectionDSNBackend,
    ConnectionBackend,
    DatabaseBackend,
    CursorBackend
)
from .outputs import OutputFactory


class BasePool(PoolBackend, ConnectionDSNBackend):
    """BasePool.

    Abstract Class to create Pool-based database connectors.
    """
    init_func: Optional[Callable] = None

    def __init__(self, dsn: str = "", loop=None, params: dict = None, **kwargs):
        ConnectionDSNBackend.__init__(
            self,
            dsn=dsn,
            params=params
        )
        PoolBackend.__init__(self, dsn=dsn, loop=loop, params=params, **kwargs)


    # Create a database connection pool
    @abstractmethod
    async def connect(self):
        """connect.
        __init async db initialization
        """

    @abstractmethod
    async def acquire(self):
        """acquire.
        Take a connection from the pool.
        """

    @abstractmethod
    async def close(self, **kwargs):
        """close.
        Closing a connection from the pool.
        """


class InitDriver(ConnectionBackend, DatabaseBackend, ABC):
    """
    InitDriver
        Abstract Class for Simple Connections.
    ----
    """
    _provider: str = "init"
    _syntax: str = "init"  # can use QueryParser for parsing SQL queries
    init_func: Optional[Callable] = None

    def __init__(self, loop: asyncio.AbstractEventLoop = None, params: dict = None, **kwargs):
        if params is None:
            params = {}
        self._pool = None
        self._max_connections = 4
        self._parameters = ()
        # noinspection PyTypeChecker
        self._serializer: OutputFactory = None
        self._row_format = 'native'
        self._connected: bool = False
        self._connection = None
        ConnectionBackend.__init__(self, loop=loop, params=params, **kwargs)
        DatabaseBackend.__init__(self)
        self._initialized_on = None
        # always starts output format to native:
        self.output_format('native')

    def row_format(self, frmt: str = 'native'):
        """
        Formats:
        - row_format: run before query
        - output: runs in the return (serialization) of data
        """
        self._row_format = frmt

    async def output(self, result, error):
        # return result in default format
        self._result = result
        return [result, error]

    def output_format(self, *args, frmt: str = 'native', **kwargs):
        self._serializer = OutputFactory(self, frmt, *args, **kwargs)

    async def valid_operation(self, sentence: Any):
        if not sentence:
            raise EmptyStatement(
                f"{__name__!s} Error: cannot use an empty sentence"
            )
        if not self._connection:
            await self.connection()


class BaseDriver(InitDriver, ConnectionDSNBackend, ABC):
    """
    BaseDriver
        Abstract Class for DB Connection
    ----
    """
    _provider: str = "base"
    _syntax: str = "base"  # can use QueryParser for parsing SQL queries
    init_func: Optional[Callable] = None

    def __init__(self, dsn="", loop=None, params: dict = None, **kwargs):
        InitDriver.__init__(
            self,
            loop=loop,
            params=params,
            **kwargs
        )
        ConnectionDSNBackend.__init__(
            self,
            dsn=dsn,
            params=params
        )
        # always starts output format to native:
        self.output_format('native')


class BaseDBDriver(BaseDriver):
    """
    Interface for more DB-oriented connections.
    """
    @abstractmethod
    def tables(self, schema: str = "") -> Iterable[Any]:
        """tables.
        Getting a list of tables in schema.
        """

    @abstractmethod
    def table(self, tablename: str = "") -> Iterable[Any]:
        """table.
        Getting table structure in schema.
        """

    @abstractmethod
    async def column_info(
            self,
            tablename: str,
            schema: str = ''
    ) -> Iterable[Any]:
        """
        Getting Column info from an existing Table in Driver.
        """


class BaseCursor(CursorBackend):
    """
    baseCursor.

    Iterable Object for Cursor-Like functionality
    """
    _provider: BaseDriver


class ModelBackend(ABC):
    """
    Interface for Backends with Dataclass-based Models Support.
    """

## Class-based Methods.
    @abstractmethod
    async def mdl_create(self, model: Model, rows: list):
        """
        Create all records based on a dataset and return result.
        """

    @abstractmethod
    async def mdl_delete(self, model: Model, conditions: dict, **kwargs):
        """
        Deleting some records using Model.
        """

    @abstractmethod
    async def mdl_update(self, model: Model, conditions: dict, **kwargs):
        """
        Updating records using Model.
        """

    @abstractmethod
    async def mdl_filter(self, model: Model, **kwargs):
        """
        Filter a Model based on some criteria.
        """

    @abstractmethod
    async def mdl_all(self, model: Model, **kwargs):
        """
        Get all records on a Model.
        """

    @abstractmethod
    async def mdl_get(self, model: Model, **kwargs):
        """
        Get one single record from Model.
        """

    @abstractmethod
    async def _filter_(self, model: Model, *args, **kwargs):
        """
        Filter a Model using Fields.
        """

    @abstractmethod
    async def _select_(self, model: Model, *args, **kwargs):
        """
        Get a query from Model.
        """

    @abstractmethod
    async def _all_(self, model: Model, *args):
        """
        Get queries with model.
        """

    @abstractmethod
    async def _get_(self, model: Model, *args, **kwargs):
        """
        Get one row from model.
        """

    @abstractmethod
    async def _delete_(self, model: Model, *args, **kwargs):
        """
        delete a row from model.
        """

    @abstractmethod
    async def _update_(self, model: Model, *args, **kwargs):
        """
        Updating a row in a Model.
        """

    @abstractmethod
    async def _save_(self, model: Model, *args, **kwargs):
        """
        Save a row in a Model, using Insert-or-Update methodology.
        """

    @abstractmethod
    async def _insert_(self, model: Model, *args, **kwargs):
        """
        insert a row from model.
        """

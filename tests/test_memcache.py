import pytest
from asyncdb import AsyncDB, AsyncPool
import asyncio
import asyncpg
from io import BytesIO
from pathlib import Path


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


DRIVER = 'memcache'
params = {
    "host": "localhost",
    "port": 11211
}


@pytest.fixture
async def conn(event_loop):
    db = AsyncDB(DRIVER, params=params, loop=event_loop)
    await db.connection()
    yield db
    await db.close()

pytestmark = pytest.mark.asyncio


async def test_pool_by_params(event_loop):
    pool = AsyncPool(DRIVER, params=params, loop=event_loop)
    pytest.assume(pool.is_connected() is False)
    await pool.connect()
    pytest.assume(pool.is_connected() is True)
    await pool.close()


@pytest.mark.parametrize("driver", [
    (DRIVER)
])
async def test_pool_by_params(driver, event_loop):
    db = AsyncDB(driver, params=params, loop=event_loop)
    assert db.is_connected() is False


@pytest.mark.parametrize("driver", [
    (DRIVER)
])
async def test_connect(driver, event_loop):
    db = AsyncDB(driver, params=params, loop=event_loop)
    await db.connection()
    pytest.assume(db.is_connected() is True)
    result, error = await db.test_connection('bigtest')
    pytest.assume(not error)
    assert result == 'bigtest'
    await db.close()


async def test_connection(conn):
    pytest.assume(conn.is_connected() is True)
    result, error = await conn.test_connection('bigtest')
    pytest.assume(not error)
    pytest.assume(result == 'bigtest')


async def multiget(conn):
    pytest.assume(conn.is_connected() is True)
    result = await conn.set("Test2", "No More Test")
    pytest.assume(result)
    result = await conn.set("Test3", "Expiration Data", 10)
    pytest.assume(result)
    values = await conn.multiget("Test2", "Test3")
    pytest.assume(values == ["No More Test", "Expiration Data"])
    await conn.delete("Test2")
    await conn.delete("Test3")
    value = await conn.get("Test2")
    assert (not value)

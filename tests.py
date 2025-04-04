import asyncio
from pathlib import Path
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from main import app
import os
from dotenv import load_dotenv
from models import create_tables, drop_tables, new_session
from orm import AddressORM

load_dotenv(Path(__file__).resolve().parent / ".env")
TEST_ADDRESS = os.getenv("TEST_ADDRESS")

@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_get_address_data(client):
    response = await client.get(f"/{TEST_ADDRESS}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_data_and_save(client):
    response = await client.post(f"/{TEST_ADDRESS}")
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == TEST_ADDRESS
    assert isinstance(data["bandwidth"], int)
    assert isinstance(data["energy"], int)
    assert isinstance(data["trx"], float)
    db_data = await AddressORM.get_info_by_address(TEST_ADDRESS)
    assert db_data[0]
    assert db_data[0].address == TEST_ADDRESS
    assert db_data[0].bandwidth == data["bandwidth"]
    assert db_data[0].energy == data["energy"]
    assert db_data[0].trx == data["trx"]




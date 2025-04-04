from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Path
from models import create_tables, drop_tables
from tronpy.async_tron import AsyncTron
from tronpy.providers.async_http import AsyncHTTPProvider
from fastapi import Query
from orm import AddressORM
from schemas import AddressBase, PaginatedAddress

@asynccontextmanager
async def lifespan(app: FastAPI):
    await drop_tables()
    await create_tables()
    yield

@asynccontextmanager
async def get_tron_client():
    provider = AsyncHTTPProvider("https://nile.trongrid.io")
    tron = AsyncTron(provider=provider)
    print("Tron client created")
    try:
        yield tron
    finally:
        print("Tron client closed")

app = FastAPI(lifespan=lifespan)

@app.post("/{address}")
async def get_data_and_save(
    address: str = Path(
        min_length=34, max_length=34, regex=r"^T[1-9A-HJ-NP-Za-km-z]{33}$"
    )
) -> AddressBase:
    async with get_tron_client() as tron:
        print(f"Fetching account for {address}")
        account = await tron.get_account(address)
        if not account:
            raise HTTPException(404, "Account not found")
        print("Fetching bandwidth")
        bandwidth = await tron.get_bandwidth(address)
        print(f"Bandwidth: {bandwidth}")
        energy = account.get("energy_remaining", 0)
        print(f"Energy: {energy}")
        print("Fetching balance")
        trx = await tron.get_account_balance(address)
        print(f"TRX: {trx}")
        new_address = AddressBase(
            address=address, bandwidth=bandwidth, energy=energy, trx=trx
        )
        print("Writing to DB")
        await AddressORM.write_address(new_address)
        print("Returning response")
        result = new_address
    print("After Tron context")
    return result

@app.get("/{address}")
async def get_address_data(
    address: str = Path(
        min_length=34, max_length=34, regex=r"^T[1-9A-HJ-NP-Za-km-z]{33}$",
    ),
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0),
) -> PaginatedAddress:
    print(address)
    addresses = await AddressORM.get_paginated_addresses(address, page, size)
    print([a for a in addresses])
    return PaginatedAddress(
        page=page, size=size, data=[AddressBase.model_validate(a) for a in addresses]
    )
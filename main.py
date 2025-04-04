from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Path
from models import create_tables, drop_tables
from tronpy.async_tron import AsyncTron
from fastapi import Query
from orm import AddressORM
from schemas import AddressBase, PaginatedAddress


@asynccontextmanager
async def lifespan(app: FastAPI):
    await drop_tables()
    await create_tables()
    yield


tron = AsyncTron(network='nile')
app = FastAPI(lifespan=lifespan)


@app.post("/{address}")
async def get_data_and_save(address: str):
    try:
        account = await tron.get_account(address)

        if not account:
            raise HTTPException(400, 'Account not found')
        bandwith = await tron.get_bandwidth(address)
        energy = account.get('energy_remaining', 0)
        trx = await tron.get_account_balance(address)
        new_address = AddressBase(
            address=address, bandwith=bandwith, energy=energy, trx=trx
        )
        await AddressORM.write_address(new_address)
        return new_address

    except Exception as e:
        return HTTPException(400, detail=str(e))


@app.get("/{address}")
async def get_address_data(
    address: str = Path(
        min_length=34, max_length=34, regex=r"^T[1-9A-HJ-NP-Za-km-z]{33}$"
    ),
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0),
):
    print(address)
    addresses = await AddressORM.get_paginated_addresses(address, page, size)
    print([a for a in addresses])
    return PaginatedAddress(
        page=page, size=size, data=[AddressBase.model_validate(a) for a in addresses]
    )

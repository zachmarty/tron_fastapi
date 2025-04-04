from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Path
from models import Address, create_tables, drop_tables, new_session, AsyncSession
from tronpy.async_tron import AsyncTron
from tronpy.providers.async_http import AsyncHTTPProvider
from fastapi import Query
from sqlalchemy import select
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
    try:
        yield tron
    finally:
        await tron.close()

async def get_db():
    database = new_session()
    try:
        yield database
    finally:
        await database.close()

app = FastAPI(lifespan=lifespan)

@app.post("/{address}")
async def get_data_and_save(
    address: str = Path(
        min_length=34, max_length=34, regex=r"^T[1-9A-HJ-NP-Za-km-z]{33}$",
    ),
    db : AsyncSession = Depends(get_db)
) -> AddressBase:
    async with get_tron_client() as tron:
        account = await tron.get_account(address)
        if not account:
            raise HTTPException(404, "Account not found")
        bandwidth = await tron.get_bandwidth(address)
        energy = account.get("energy_remaining", 0)
        trx = await tron.get_account_balance(address)
        new_address = AddressBase(
            address=address, bandwidth=bandwidth, energy=energy, trx=trx
        )
        db_item = Address(**new_address.model_dump())
        db.add(db_item)
        await db.flush()
        await db.commit()
    return new_address

@app.get("/{address}")
async def get_address_data(
    address: str = Path(
        min_length=34, max_length=34, regex=r"^T[1-9A-HJ-NP-Za-km-z]{33}$",
    ),
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0),
    db : AsyncSession = Depends(get_db)
) -> PaginatedAddress:
    query = select(Address).where(Address.address == address).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    addresses = result.scalars().all()
    return PaginatedAddress(
        page=page, size=size, data=[AddressBase.model_validate(a) for a in addresses]
    )
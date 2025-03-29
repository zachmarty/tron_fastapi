from models import Address, new_session
from sqlalchemy import select
from schemas import AddressBase


class AddressORM:

    @classmethod
    async def get_info_by_address(cls, address: str):
        async with new_session() as session:
            query = select(Address).where(Address.address == address)
            result = await session.execute(query)
            addresses = result.scalars().all()
            return addresses

    @classmethod
    async def write_address(cls, data: AddressBase):
        async with new_session() as session:
            new_item = Address(**data)
            session.add(new_item)
            await session.flush()
            await session.commit()
            return new_item
        
    @classmethod
    async def get_paginated_addresses(cls, address, page, size):
        async with new_session() as session:
            query = select(Address).where(Address.address == address).offset((page - 1) * size).limit(size)
            result = await session.execute(query)
            addresses = result.scalars().all()
            return addresses

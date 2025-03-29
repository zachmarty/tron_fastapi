from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import Float, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
import os
load_dotenv(Path(__file__).resolve().parent / ".env")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo = True)
session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Address(Base):
    __tiblename__ = "addresses"

    id:Mapped[int] = mapped_column(primary_key=True)
    address:Mapped[str] = mapped_column(String)
    bandwith:Mapped[int] = mapped_column(Integer)
    energy:Mapped[int] = mapped_column(Integer)
    trx:Mapped[float] = mapped_column(Float)

    def to_dict(self):
        return {
            "id": self.id,
            "address": self.address,
            "bandwith": self.bandwith,
            "energy": self.energy,
            "trx": self.trx
        }
    
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


    async def drop_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
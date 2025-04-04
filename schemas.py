from pydantic import BaseModel, ConfigDict


class AddressBase(BaseModel):
    address: str
    bandwidth: int
    energy: int
    trx: float

    class Config:
        from_attributes = True
        extra = "forbid"


class PaginatedAddress(BaseModel):
    page: int
    size: int
    data: list[AddressBase]

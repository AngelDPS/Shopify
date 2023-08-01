from pydantic import BaseModel, Field
from models.misc import MmetafieldInput


class MLocationAddress(BaseModel):
    address1: str = None
    address2: str = None
    city: str = None
    countryCode: str = "VE"
    phone: str = None
    provinceCode: str = None
    zip: str = None


class MSucursalAddInput(BaseModel):
    name: str = Field(..., alias="nombre")
    address: MLocationAddress
    fulfillsOnlineOrders: bool = True
    metafields: list[MmetafieldInput] | None = None

    class Config:
        allow_population_by_field_name = True

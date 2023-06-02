from pydantic import Field, BaseModel as PydanticBaseModel
from decimal import Decimal
from enum import Enum
# from datetime import datetime


class BaseModel(PydanticBaseModel):
    class Config:
        allow_population_by_field_name = True
        anystr_strip_whitespace = True


class Habilitado(Enum):
    ARCHIVED = 0
    ACTIVE = 1


class Marticulo(BaseModel):
    art_des: str | None = None
    codigoCompania: str | None = None
    codigoTienda: str | None = None
    co_art: str | None = None
    co_lin: str | None = None
    des_shopify: str | None = None
    precio: Decimal | None = Field(None, alias='price')
    stock_act: int | None = None
    stock_com: int | None = None
    codigo_barra: str | None = None
    referencia: str | None = None
    marca: str | None = None
    cobra_impuesto: bool = Field(False, alias='taxable')
    imagen_url: list[str] | None = None
    habilitado: Habilitado | None | str = Field(None, alias='status')
    shopifyGID: dict | None = None
    PK: str | None = None
    SK: str | None = None
    # created_at: datetime | None = None
    # updated_at: datetime | None = None


class Mlinea(BaseModel):
    PK: str | None = None
    SK: str | None = None
    nombre: str | None = Field(None, alias='title')
    codigoCompania: str | None = None
    co_lin: str | None = None
    co_lin_padre: str | None = None
    descuento: Decimal | None = None
    shopifyGID: str | None = None
    des_shopify: str | None = None
    # created_at: datetime | None = None
    # updated_at: datetime | None = None


class Mtienda(BaseModel):
    nombre: str | None = Field(None, alias='name')
    direccion: str | None = None
    telefono: str | None = Field(None, alias='phone')
    habilitado: bool | None = None
    codigoCompania: str | None = None
    codigoTienda: str | None = None
    codigoTiendaAlt: str | None = None
    # configuraciones:
    # correo

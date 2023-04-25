from pydantic import Field, BaseModel as PydanticBaseModel
from typing import Literal
from decimal import Decimal
# from datetime import datetime


class BaseModel(PydanticBaseModel):
    class Config:
        allow_population_by_field_name = True
        anystr_strip_whitespace = True


class Marticulo(BaseModel):
    entity: Literal["articulos"]
    art_des: str | None = None
    codigoCompania: str | None = None
    codigoTienda: str | None = None
    co_art: str | None = None
    co_lin: str | None = None
    prec_vta1: Decimal | None = None
    prec_vta2: Decimal | None = None
    prec_vta3: Decimal | None = None
    stock_act: int | None = None
    stock_com: int | None = None
    codigo_barra: str | None
    referencia: str | None = None
    marca: str | None
    habilitado: bool | None = None
    # created_at: datetime | None = None
    # updated_at: datetime | None = None


class Mlinea(BaseModel):
    entity: Literal["lineas"]
    nombre: str | None = Field(None, alias='title')
    codigoCompania: str | None = None
    co_lin: str | None = None
    co_lin_padre: str | None = None
    descuento: Decimal | None = None
    # created_at: datetime | None = None
    # updated_at: datetime | None = None


class Mtienda(BaseModel):
    entity: Literal["tiendas"]
    nombre: str | None = Field(None, alias='name')
    direccion: str | None = None
    telefono: str | None = Field(None, alias='phone')
    habilitado: bool | None = None
    codigoCompania: str | None = None
    codigoTienda: str | None = None
    codigoTiendaAlt: str | None = None
    # configuraciones:
    # correo


Mimage = Marticulo | Mlinea | Mtienda


class Mevento(BaseModel):
    NewImage: Mimage = Field(..., discriminator='entity')
    OldImage: Mimage | None = Field(None, discriminator='entity')

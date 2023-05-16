from pydantic import Field, BaseModel as PydanticBaseModel
from typing import Literal
from decimal import Decimal
# from datetime import datetime


class BaseModel(PydanticBaseModel):
    class Config:
        allow_population_by_field_name = True
        anystr_strip_whitespace = True


class Marticulo(BaseModel):
    entity: Literal["articulos"] = "articulos"
    art_des: str | None = None
    codigoCompania: str | None = None
    codigoTienda: str | None = None
    co_art: str | None = None
    co_lin: str | None = None
    prec_vta1: Decimal | None = Field(None, alias='precio')
    prec_vta2: Decimal | None = Field(None, alias='precio')
    prec_vta3: Decimal | None = Field(None, alias='precio')
    stock_act: int | None = None
    stock_com: int | None = None
    codigo_barra: str | None = None
    referencia: str | None = None
    marca: str | None = None
    habilitado: bool | None = None
    shopifyGID: dict | None = None
    PK: str | None = None
    SK: str | None = None
    # created_at: datetime | None = None
    # updated_at: datetime | None = None


class McambiosInventario(BaseModel):
    stock_act: int | None = None
    stock_com: int | None = None


class McambiosVariante(BaseModel):
    prec_vta1: Decimal | None = Field(None, alias='precio')
    prec_vta2: Decimal | None = Field(None, alias='precio')
    prec_vta3: Decimal | None = Field(None, alias='precio')
    codigo_barra: str | None = None
    referencia: str | None = None


class McambiosProducto(BaseModel):
    art_des: str | None = None
    co_lin: str | None = None
    marca: str | None = None
    habilitado: bool | None = None
    status: Literal["ACTIVE", "ARCHIVED"] | None = None


class Mlinea(BaseModel):
    PK: str | None = None
    SK: str | None = None
    entity: Literal["lineas"] = "lineas"
    nombre: str | None = Field(None, alias='title')
    codigoCompania: str | None = None
    co_lin: str | None = None
    co_lin_padre: str | None = None
    descuento: Decimal | None = None
    shopifyGID: str | None = None
    # created_at: datetime | None = None
    # updated_at: datetime | None = None


class Mtienda(BaseModel):
    entity: Literal["tiendas"] = "tiendas"
    nombre: str | None = Field(None, alias='name')
    direccion: str | None = None
    telefono: str | None = Field(None, alias='phone')
    habilitado: bool | None = None
    codigoCompania: str | None = None
    codigoTienda: str | None = None
    codigoTiendaAlt: str | None = None
    # configuraciones:
    # correo


Mimage = Marticulo


class Mevento(BaseModel):
    NewImage: Marticulo  # = Field(..., discriminator='entity')
    OldImage: Marticulo | None = None  # = Field(None, discriminator='entity')

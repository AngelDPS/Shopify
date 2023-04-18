from typing import Literal
from pydantic import BaseModel, Field


class RespuestaArticulo(BaseModel):
    pass


class RespuestaColeccion(BaseModel):
    pass


class RespuestaSucursal(BaseModel):
    pass


Respuestas = RespuestaColeccion | RespuestaArticulo | RespuestaSucursal


class Respuesta(BaseModel):
    status: Literal["OK", "ERROR"]
    error: str | None = Field(
        None,
        max_length=100
    )
    data: Respuestas

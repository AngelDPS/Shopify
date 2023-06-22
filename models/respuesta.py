from typing import Literal
from pydantic import BaseModel, Field


class RespuestaArticulo(BaseModel):
    pass


class RespuestaColeccion(BaseModel):
    pass


Respuestas = RespuestaColeccion | RespuestaArticulo


class Respuesta(BaseModel):
    status: Literal["OK", "ERROR"]
    error: str | None = Field(
        None,
        max_length=100
    )
    data: list[dict] | None = None

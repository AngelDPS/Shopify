from pydantic import BaseModel, NonNegativeInt, Field
from typing import Literal
from decimal import Decimal


class MSEOInput(BaseModel):
    """Información para presentar como resultado en los motores de búsqueda.
    """
    description: str | None = Field(None, title="Descripción",
                                    description="Descripción a mostrar para el"
                                    " motor de búsqueda.")
    title: str | None = Field(None, title="Título",
                              description="Titulo para mostrar en el motor de"
                              " búsqueda.")


class MimageInput(BaseModel):
    """Datos de la imagen a asociar con el objeto.
    """
    altText: str | None = Field(None, title="Texto alternativo",
                                description="Palabra o frase para mostrar que "
                                "describa la naturaleza o contenido de la "
                                "imagen.")
    id: str | None = Field(None)
    src: str | None = Field(None, title="Origen",
                            description="El URL de la imagen.")


MediaContentType = Literal["EXTERNAL_VIDEO", "IMAGE", "MODEL_3D", "VIDEO"]


class McreateMediaInput(BaseModel):
    alt: str | None = None
    mediaContentType: MediaContentType
    originalSource: str


PrivateMetafieldValueType = Literal["INTEGER", "JSON_STRING", "STRING"]


class _MprivateMetafieldValueInput(BaseModel):
    value: str
    valueType: PrivateMetafieldValueType


class MprivateMetafieldInput(BaseModel):
    key: str
    namespace: str
    owner: str | None = None
    valueInput: _MprivateMetafieldValueInput


class MmetafieldInput(BaseModel):
    id: str | None = None
    key: str | None = None
    namespace: str | None = None
    type: str | None = None
    value: str | None = None

from pydantic import BaseModel, NonNegativeInt, Field
from enum import Enum
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


class _MmediaContentType(str, Enum):
    EXTERNAL_VIDEO = "EXTERNAL_VIDEO"
    IMAGE = "IMAGE"
    MODEL_3D = "MODEL_3D"
    VIDEO = "VIDEO"


class McreateMediaInput(BaseModel):
    alt: str | None = None
    mediaContentType: _MmediaContentType
    originalSource: str


class _MprivateMetafieldValueType(str, Enum):
    INTEGER = "INTEGER"
    JSON_STRING = "JSON_STRING"
    STRING = "STRING"


class _MprivateMetafieldValueInput(BaseModel):
    value: str
    valueType: _MprivateMetafieldValueType


class MprivateMetafieldInput(BaseModel):
    key: str
    namespace: str
    owner: str | None = None
    valueInput: _MprivateMetafieldValueInput


class MmetafieldInput(BaseModel):
    description: str | None = None
    id: str | None = None
    key: str | None = None
    namespace: str | None = None
    type: str | None = None
    value: str | None = None


class MproductStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DRAFT = "DRAFT"


class MinventoryLevelInput(BaseModel):
    availableQuantity: NonNegativeInt
    locationId: str


class MinventoryItemInput(BaseModel):
    cost: Decimal | None = None
    tracked: bool | None = None


class MproductVariantInventoryPolicy(str, Enum):
    CONTINUE = "CONTINUE"
    DENY = "DENY"

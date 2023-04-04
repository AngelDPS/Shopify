from pydantic import BaseModel, NonNegativeInt
from enum import Enum
from decimal import Decimal


class MSEOInput(BaseModel):
    description: str | None = None
    title: str | None = None


class MimageInput(BaseModel):
    altText: str | None = None
    id: str | None = None
    src: str | None = None


class McreateMediaInput(BaseMode):
    alt: str | None = None
    mediaContentType: _MmediaContentType
    originalSource: str


class _MmediaContentType(str, Enum):
    EXTERNAL_VIDEO = "EXTERNAL_VIDEO"
    IMAGE = "IMAGE"
    MODEL_3D = "MODEL_3D"
    VIDEO = "VIDEO"


class MmetafieldInput(BaseModel):
    description: str | None = None
    id: str | None = None
    key: str | None = None
    namespace: str | None = None
    type: str | None = None
    value: str | None = None


class MprivateMetafieldInput(BaseModel):
    key: str
    namespace: str
    owner: str | None = None
    valueInput: _MprivateMetafieldValueInput


class _MprivateMetafieldValueInput(BaseModel):
    value: str
    valueType: _MprivateMetafieldValueType


class _MprivateMetafieldValueType(str, Enum):
    INTEGER = "INTEGER"
    JSON_STRING = "JSON_STRING"
    STRING = "STRING"


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
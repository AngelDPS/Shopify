from pydantic import BaseModel, NonNegativeInt
from decimal import Decimal
from enum import Enum
from misc import (
    MinventoryLevelInput,
    MinventoryItemInput,
    MproductVariantInventoryPolicy,
    MmetafieldInput,
    MprivateMetafieldInput
)


class _MweightUnit(str, Enum):
    GRAMS = "GRAMS"
    KILOGRAMS = "KILOGRAMS"
    OUNCES = "OUNCES"
    POUNDS = "POUNDS"


class MproductVariantInput(BaseModel):
    options: [str] | None = None
    price: Decimal | None = None
    compareAtPrice: Decimal | None = None
    barcode: str | None = None
    sku: str | None = None
    position: NonNegativeInt | None = None
    requiresShipping: bool | None = None
    weight: Decimal | None = None
    weightUnit: _MweightUnit | None = None
    inventoryQuantities: [MinventoryLevelInput] | None = None
    inventoryItem: MinventoryItemInput | None = None
    inventoryPolicy: MproductVariantInventoryPolicy | None = None
    imageSrc: str | None = None
    imageId: str | None = None
    mediaSrc: [str] | None = None
    metafields: [MmetafieldInput] | None = None
    privateMetafields: [MprivateMetafieldInput] | None = None
    taxCode: str | None = None
    taxable: bool | None = None
    harmonizedSystemCode: str | None = None
    id: str | None = None
    productId: str | None = None

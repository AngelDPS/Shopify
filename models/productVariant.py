from pydantic import BaseModel, NonNegativeInt
from decimal import Decimal
from typing import Literal
from models.misc import (
    MinventoryLevelInput,
    MinventoryItemInput,
    MproductVariantInventoryPolicy,
    MmetafieldInput,
    MprivateMetafieldInput
)


WeightUnit = Literal["GRAMS", "KILOGRAMS", "OUNCES", "POUNDS"]


class MproductVariantInput(BaseModel):
    options: list[str] | None = None
    price: Decimal | None = None
    compareAtPrice: Decimal | None = None
    barcode: str | None = None
    sku: str | None = None
    position: NonNegativeInt | None = None
    requiresShipping: bool | None = None
    weight: Decimal | None = None
    weightUnit: WeightUnit | None = None
    inventoryQuantities: list[MinventoryLevelInput] | None = None
    inventoryItem: MinventoryItemInput | None = None
    inventoryPolicy: MproductVariantInventoryPolicy | None = None
    imageSrc: str | None = None
    imageId: str | None = None
    mediaSrc: list[str] | None = None
    metafields: list[MmetafieldInput] | None = None
    privateMetafields: list[MprivateMetafieldInput] | None = None
    taxCode: str | None = None
    taxable: bool | None = None
    harmonizedSystemCode: str | None = None
    id: str | None = None
    productId: str | None = None

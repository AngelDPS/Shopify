from pydantic import BaseModel as PydanticBaseModel, Field, NonNegativeInt
from decimal import Decimal
from typing import Literal
from models.misc import (
    MimageInput,
    MSEOInput,
    MmetafieldInput,
    MprivateMetafieldInput
)

WeightUnit = Literal["GRAMS", "KILOGRAMS", "OUNCES", "POUNDS"]
ProductStatus = Literal["ACTIVE", "ARCHIVED", "DRAFT"]
ProductVariantInventoryPolicy = Literal["CONTINUE", "DENY"]


class BaseModel(PydanticBaseModel):
    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        validate_assignment = True


class MinventoryLevelInput(BaseModel):
    availableQuantity: NonNegativeInt = Field(
        ...,
        alias='stock_act'
    )
    locationId: str


class MinventoryItemInput(BaseModel):
    cost: Decimal | None = None
    tracked: bool = True


class MproductVariantInput(BaseModel):
    options: list[str] | None = None
    price: float | None = Field(None, alias='precio')
    compareAtPrice: Decimal | None = None
    barcode: str | None = Field(None, alias='codigo_barra')
    sku: str | None = Field(None, alias='referencia')
    position: NonNegativeInt | None = None
    requiresShipping: bool = True
    weight: Decimal | None = None
    weightUnit: WeightUnit | None = None
    inventoryQuantities: list[MinventoryLevelInput] | None = None
    inventoryItem: MinventoryItemInput = MinventoryItemInput()
    inventoryPolicy: ProductVariantInventoryPolicy | None = None
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


class MproductInput(BaseModel):
    title: str | None = Field(None, alias='art_des')
    descriptionHtml: str | None = None
    productType: str | None = None
    status: ProductStatus | None = None
    collectionsToJoin: list[str] | None = None
    tags: list[str] | None = None
    vendor: str | None = Field(None, alias='marca')
    options: list[str] | None = None
    variants: list[MproductVariantInput] | None = None
    images: list[MimageInput] | None = None
    seo: MSEOInput | None = None
    templateSuffix: str | None = None
    requiresSellingPlan: bool | None = None
    handle: str | None = None
    giftCard: bool = False
    giftCardTemplateSuffix: str | None = None
    metafields: list[MmetafieldInput] | None = None
    privateMetafields: list[MprivateMetafieldInput] | None = None
    collectionsToLeave: list[str] | None = None
    id: str | None = None
    redirectNewHandle: bool | None = None

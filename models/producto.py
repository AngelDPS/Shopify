from pydantic import BaseModel
from misc import (
    MimageInput,
    MSEOInput,
    MmetafieldInput,
    MprivateMetafieldInput,
    MproductStatus
)
from productVariantInput import MproductVariantInput


class MproductInput(BaseModel):
    title: str | None = None
    descriptionHtml: str | None = None
    productType: str | None = None
    status: MproductStatus | None = None
    collectionsToJoin: list[str] | None = None
    tags: list[str] | None = None
    vendor: str | None = None
    options: list[str] | None = None
    variants: list[MproductVariantInput] | None = None
    images: list[MimageInput] | None = None
    seo: MSEOInput | None = None
    templateSuffix: str | None = None
    requiresSellingPlan: bool | None = None
    handle: str | None = None
    giftCard: bool | None = None
    giftCardTemplateSuffix: str | None = None
    metafields: list[MmetafieldInput] | None = None
    privateMetafields: list[MprivateMetafieldInput] | None = None
    collectionsToLeave: list[str] | None = None
    id: str | None = None
    redirectNewHandle: bool | None = None

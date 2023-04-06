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
    collectionsToJoin: [str] | None = None
    tags: [str] | None = None
    vendor: str | None = None
    options: [str] | None = None
    variants: [MproductVariantInput] | None = None
    images: [MimageInput] | None = None
    seo: MSEOInput | None = None
    templateSuffix: str | None = None
    requiresSellingPlan: bool | None = None
    handle: str | None = None
    giftCard: bool | None = None
    giftCardTemplateSuffix: str | None = None
    metafields: [MmetafieldInput] | None = None
    privateMetafields: [MprivateMetafieldInput] | None = None
    collectionsToLeave: [str] | None = None
    id: str | None = None
    redirectNewHandle: bool | None = None
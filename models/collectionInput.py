from pydantic import BaseModel, constr
from enum import Enum
from misc import (
    MSEOInput, 
    MimageInput, 
    MmetafieldInput,
    MprivateMetafieldInput
)


class McollectionInput(BaseModel):
    title: str | None = None
    descriptionHtml: str | None = None
    products: [str] | None = None
    ruleSet: _McollectionRuleSetInput | None = None
    sortOrder: _McollectionSortOrder | None = None
    seo: MSEOInput | None
    image: MimageInput | None
    metafields: [MmetafieldInput] | None = None
    privateMetafields: [MprivateMetafieldInput] | None = None
    templateSuffix: str | None = None
    handle: str | None = None
    id: str | None = None
    redirectNewHandle: bool | None = None


class _McollectionSortOrder(str, Enum):
    ALPHA_ASC = "ALPHA_ASC"
    ALPHA_DESC = "APLHA_DESC"
    BEST_SELLING = "BEST_SELLING"
    CREATED = "CREATED"
    CREATED_DESC = "CREATED_DESC"
    MANUAL = "MANUAL"
    PRICE_ASC = "PRICE_ASC"
    PRICE_DESC = "PRICE_DESC"


class _McollectionRuleSetInput(BaseModel):
    appliedDisjunctively: bool
    rules: [_McollectionRuleInput]


class _McollectionRuleInput(BaseModel):
    column: _McollectionRuleColumn
    condition: str
    condtionObjectId: str | None = None
    relation: _McollectionRuleRelation


class _McollectionRuleColumn(str, Enum):
    IS_PRICE_REDUCED = "IS_PRICE_REDUCED"
    PRODUCT_METAFIELD_DEFINITION = "PRODUCT_METAFIELD_DEFINITION"
    PRODUCT_TAXONOMY_NODE_ID = "PRODUCT_TAXONOMY_NODE_ID"
    TAG = "TAG"
    TITLE = "TITLE"
    TYPE = "TYPE"
    VARIANT_COMPARE_AT_PRICE = "VARIANT_COMPARE_AT_PRICE"
    VARIANT_INVENTORY = "VARIANT_INVENTORY"
    VARIANT_METAFIELD_DEFINITION = "VARIANT_METAFIELD_DEFINITION"
    VARIANT_PRICE = "VARIANT_PRICE"
    VARIANT_TITLE = "VARIANT_TITLE"
    VARIANT_WEIGHT = "VARIANT_WEIGHT"
    VENDOR = "VENDOR"


class _McollectionRuleRelation(str, Enum):
    CONTAINS = "CONTAINS"
    ENDS_WITH = "ENDS_WITH"
    EQUALS = "EQUALS"
    GREATER_THAN = "GREATER_THAN"
    IS_NOT_SET = "IS_NOT_SET"
    IS_SET = "IS_SET"
    LESS_THAN = "LESS_THAN"
    NOT_CONTAINS = "NOT_CONTAINS"
    NOT_EQUALS = "NOT_EQUALS"
    STARTS_WITH = "STARTS_WITH"
from pydantic import BaseModel, constr, Field
from enum import Enum
from misc import (
    MSEOInput, 
    MimageInput, 
    MmetafieldInput,
    MprivateMetafieldInput
)


class McollectionInput(BaseModel):
    """Campos utilizados para crear una colección en Shopify
    """
    title: str | None = Field(
        None, title='Título', description="El nombre de la colección")
    descriptionHtml: str | None = Field(
        None, title='Descripción en HTML', 
        description="Descripción de la colección en formato HTML.")
    products: [str] | None = Field(None, title="Productos", 
    description="""
    Lista de los IDs de los productos a añadir a la colección.\n
    Si la colección es inteligente, no es posible añadir productos de esta manera""")
    ruleSet: _McollectionRuleSetInput | None = Field(None, title="Set de reglas")
    sortOrder: _McollectionSortOrder | None = Field(None, title="Orden")
    seo: MSEOInput | None = Field(None)
    image: MimageInput | None = Field(None, title="Imagen")
    metafields: [MmetafieldInput] | None = None
    privateMetafields: [MprivateMetafieldInput] | None = None
    templateSuffix: str | None = Field(None, title="Plantilla", description="Plantilla de tema a utiliza para mostrar el producto en tienda.")
    handle: str | None = Field(None, description="Texto único para humanos, para la colección. Generado automáticamente del título de la colección.")
    id: str | None = Field(None, title="ID", description="Identificador único de la colección. Utilizado para modificarla.")
    redirectNewHandle: bool | None = None


    class Config:
        title = "Parámetros para la creación de colecciónes."
        anystr_strip_whitespace = True


class _McollectionSortOrder(str, Enum):
    """Especificación del orden en que ese muestran los productos dentro de la colección.
    """
    ALPHA_ASC = "ALPHA_ASC"
    ALPHA_DESC = "APLHA_DESC"
    BEST_SELLING = "BEST_SELLING"
    CREATED = "CREATED"
    CREATED_DESC = "CREATED_DESC"
    MANUAL = "MANUAL"
    PRICE_ASC = "PRICE_ASC"
    PRICE_DESC = "PRICE_DESC"


class _McollectionRuleSetInput(BaseModel):
    """Conjunto de reglas utilizadas para dinámicamente añadir productos a la colección.
    """
    appliedDisjunctively: bool = Field(..., title="Aplicar disyuntivamente", description="Si los productos deben coincidir con alguna o con todas las reglas para ser incluídos en la colección.")
    rules: [_McollectionRuleInput] = Field(..., title="Reglas")


class _McollectionRuleInput(BaseModel):
    """Detallado de una regla para discernir la pertenencia de los productos a la colección.
    """
    column: _McollectionRuleColumn = Field(..., title="Atributo")
    condition: str = Field(..., title="Condición", description="Condición a comparar con respecto al atributo")
    condtionObjectId: str | None = Field(None, description="EL ID del objeto que apunta a los atributos adicionales para la regla de la colección. Esto sólo es requerido cuando se usan reglas de definiciones de metacampos.")
    relation: _McollectionRuleRelation = Field(..., title="Relación")


class _McollectionRuleColumn(str, Enum):
    """Especificación del atributo del producto a usar en la regla especificada.
    """
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
    """Establece la relación entre el atributo y la condición"
    """
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
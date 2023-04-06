# Colecciones según Shopify

Puedes agrupar tus productos en colecciones para facilitar que los clientes los encuentren por categoría. A continuación algunos ejemplos de colecciones que puedes crear:
 * Ropa para hombres, mujeres, niños y niñas.
 * Artículos de cierto tipo, como lámparas, cojines o alfombras.
 * Artículos en oferta.
 * Artículos de un cierto tamaño o color.
 * Productos de temporada tales como tarjetas navideñas y decoraciones.

# Para crear una colección

Se utiliza la mutación

## [collectionCreate(input: CollectionInput!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/collectionCreate)

Todos los campos son opcionales. En la siguiente lista se establecen campos de _baja prioridad_ y ~~depreciados~~, o **irrelevantes para crear** colecciones.

CollectionInput:
* title: String

  El nombre de la colección.

* descriptionHtml: String

  Descripción de la colección en formato HTML.

* products: [ID!]

  Lista de los IDs de los productos a añadir a la colección al momento de crearla. 
  Si se crea una colección automática, no es posible añadir productos de esta manera.

* ruleSet: CollectionRuleSetInput

  En caso de colecciones automáticas, no es posible añadir productos de forma manual.

* sortOrder: CollectionSortOrder

  Especifíca el orden en el que se presentan los productos dentro de la colección.
  CollectionSortOrder es un str con posibles valores:

  - ALPHA_ASC

    Alfabéticamente, en orden ascendente, (A - Z).

  - ALPHA_DESC

    Alfabéticamente, en orden descendente, (Z - A).

  - BEST_SELLING

    Según productos mejor vendidos.

  - CREATED

    Por fecha de creación, en orden ascendente (más viejo - más nuevo).

  - CREATED_DESC

    Por fecha de creación, en orden descendente (más nuevo - más viejo).

  - MANUAL

    En el orden establecido manualmente por el mercader.

  - PRICE_ASC

    Por precio, en orden ascendente (menor precio - mayor precio).

  - PRICE_DESC

    Por precio, en orden descendente (mayor precio - menor precio).

* seo: SEOInput
  - description: String
  - title: String

  Información para presentar como resultado en los motores de búsqueda.

* image: ImageInput
  - altText: String
  - id: ID
  - src: String
* _metafields: [MetafieldInput!]_
  - description: String
  - id: ID
  - key: String
  - namespace: String
  - type: String
  - value: String
* _privateMetafields: [PrivateMetafieldInput!]_
  - key: String!
  - namespace: String!
  - owner: ID
  - valueInput: PrivateMetafieldValueInput!
    + value: String!
    + valueType: PrivateMetafieldValueType!
* _templateSuffix: String_
* _handle: String_
* **id: ID**
* **redirectNewHandle: Boolean**
* ~~publications: [CollectionPublicationInput!]~~
  - channelHandle: String
  - channelId: ID
  - publicationId: ID


### Para crear colecciones automáticas.

En esta sección se detallaran los campos del CollectionRuleSetInput utilizado en caso de crear colecciones automáticas.

CollectionRuleSetInput:
- appliedDisjunctively: Boolean!

  Si los productos deben coincidir con alguna o todas las reglas para ser incluidos en la colección. Si es verdadero, los productos deben coincidir con al menos una de las reglas para ser incluidos en la colección. Si es falso, los productos deben coincidir con todas las reglas para ser incluidos en la colección.

- rules: [CollectionRuleInput!]
  + column: CollectionRuleColumn!

    Especifíca el atributo del producto usado para poblar la colección.
    Los valores válidos son:

    * IS_PRICE_REDUCED

      Un atributo evaluado en base al atributo `compare_at_price` de las variantes del producto. Con la relación `is_set`, la regla hace coincidir los productos con al menos una variante con el conjunto `compare_at_price`. Con la relación `is_not_set`, la regla coincide con los productos con al menos una variante con `compare_at_price` no establecida.

    * PRODUCT_METAFIELD_DEFINITION

      Esta categoría incluye definiciones de metacampos que tienen el valor de `useAsCollectionCondition` establecido a `true`.

    * PRODUCT_TAXONOMY_NODE_ID

      El atributo de `product_taxonomy_node_id`.

    * TAG

      El atributo de etiqueta, `tag`.

    * TITLE

      El atributo del título, `title`.
    
    * TYPE

      El atributo del tipo, `type`.

    * VARIANT_COMPARE_AT_PRICE

      El atributo del precio de comparación de las variantes, `variant_compare_at_price`.

    * VARIANT_INVENTORY

      El atributo de inventario de las variantes, `variant_inventory`.

    * VARIANT_METAFIELD_DEFINITION

      Esta categoría incluye definiciones de metacampos que tienen el valor de `the useAsCollectionCondition` establecido a `true` para variantes.

    * VARIANT_PRICE

      El atributo de precio de la variante, `variant_price`.

    * VARIANT_TITLE

      El atributo del título de la variante, `variant_title`.

    * VARIANT_WEIGHT

      El atributo del peso de la variante, `variant_weight`.

    * VENDOR

      El atributo del proveedor, `vendor`.

  + condition: String!
  + conditionObjectId: ID

    EL ID del objeto que apunta a los atributos adicionales para la regla de la colección. Esto sólo es requerido cuando se usan reglas de definiciones de metacampos.

  + relation: CollectionRuleRelation!

    Establece la relación entre el atributo y la condición.
    Los valores válidos son:

    * CONTAINS

      El atributo contiene la condición.

    * ENDS_WITH

      El atributo termina con la condición.

    * EQUALS

      El atributo es igual a la condición.

    * GREATER_THAN

      El atributo es mayor que la condición.

    * IS_NOT_SET

      El atributo no está establecido (es igual a `null`).

    * IS_SET

      El atributo está establecido (no es igual a `null`).

    * LESS_THAN

      El atributo es menor que la condición.

    * NOT_CONTAINS

      El atributo no contiene la condición.

    * NOT_EQUALS

      El atributo no es igual a la condición.

    * STARTS_WITH

      El atributo inicia con la condición.
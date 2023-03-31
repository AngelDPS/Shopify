# Para crear artículos

Se utiliza la mutación 
## [articleCreate(input: ProductInput!, media: [CreateMediaInput!])](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productCreate)

Todos los campos son opcionales. En la siguiente lista se establecen campos de _baja prioridad_ y ~~depreciados~~, o **irrelevantes para crear** productos.


* ProductInput
    - title: String

        Título del producto.
    
    - descriptionHtml: String

        Descripción del producto en formato HTML.

    - productType: String

        Tipo de producto especificado por el vendedor. Es una forma de categorizar los productos.

    - status: ProductStatus

        El status del producto. Activo, inactivo o borrador.

    - collectionsToJoin: [ID!]

        Lista de IDs de las colecciones (categorías personalizadas de la tienda) a las que el artículo va a pertenecer.

    - tags: [String!]

        Etiquetas para clasificar el producto.

    - vendor: String

        Información sobre el proveedor del producto.

    - variants: [ProductVariantInput!]

        Información pertinente a las variantes del producto. Es aquí donde se establece el precio además de datos como el precio, código de barras, SKU, existencia en inventario, entre otros.

    - _images: [ImageInput!]_
        + altText: String
        + id: ID
        + src: String
    - _seo: SEOInput_
        + description: String
        + title: String

        Información personalizada para presentar como resultado en los motores de búsqueda.

    - _productCategory: ProductCategoryInput_
        + productTaxonomyNodeId: ID!

        En el caso de Shopify, la categoría del producto se refiere a una clasificación estandarizada basada en la [taxonomía de productos de Shopify](https://help.shopify.com/txt/product_taxonomy/en.txt).

    - _standardizedProductType: StandardizedProductTypeInput_
        + productTaxonomyNodeId: ID!
    - _customProductType: String_

        Por los momentos no veo la diferencia entre este campo y el campo de productType.

    - _templateSuffix: String_
    - _requiresSellingPlan: Boolean_
    - _handle: String_
    - _giftCard_: Boolean
    - _giftCardTemplateSuffix_: String
    - _metafields_: [MetafieldInput!]

        Los metacampos permiten guardar información especializada del tipo `key: value` de forma personalizada.

    - _privateMetafields_: [PrivateMetafieldInput!]
    - _options_: [String!]
    - **collectionsToLeave: [ID!]**
    - **id: ID**
    - **redirectNewHandle: Boolean**
    - ~~bodyHTML: String~~
    - ~~productPublications: [ProductPublicationInput!]~~
    - ~~publications: [ProductPublicationInput!]~~
    - ~~publishDate: DateTime~~
    - ~~publishOn: DateTime~~
    - ~~published: Boolean~~
    - ~~publishedAt: DateTime~~
* CreateMediaInput
    - alt: String
    - mediaContentType: MediaContentType!
    - originalSource: String!


### Las variantes de un producto

En las variantes de los productos es que se establece información detallada de cada producto. Además que permite establecer opciones distintas para una sola familia de productos, como la talla o el color.

Los campos de `ProductVariantInput`

+ price: Money

    El precio del producto, de tipo str, sin símbolo de moneda o código.
    La moneda a usar corresponde a la establecida a usar en la configuración de la tienda.

+ compareAtPrice: Money

    Precio de comparación a mostrar en tienda. Al comprador se le muestra como un precio tachado, al lado del actual precio de venta.

+ barcode: String

    Valor asociado al código de barras del producto.

+ sku: String

    Código de referencia del producto para inventariado.

+ position: Int

    El orden en el que se muestra la variante dentro de la lista de variantes del producto. La primera posición es la 1.

+ requiresShipping: Boolean

    Si el producto require de envío.

+ weight: Float

    Valór numérico del peso del producto.

+ weightUnit: WeightUnit

    La unidad de medida del peso, con valores aceptados de:

    * GRAMS
    * KILOGRAMS
    * OUNCES
    * POUNDS
+ inventoryQuantities: [InventoryLevelInput!]
    * availableQuantity: Int!

        La cantidad disponible de un ítem del inventario en una sucursal.

    * locationId: ID!

        El ID de la sucursal.
    
+ inventoryItem: InventoryItemInput
    * cost: Decimal

        Costo de producción del producto. Distinto del precio de venta.

    * tracked: Boolean
+ _inventoryPolicy: ProductVariantInventoryPolicy_

    Indica si los compradores pueden poner ordenes de compra en caso de que el producto esté agotado.
    Los valores aceptados son:

    * CONTINUE

    Los compradores pueden comprar este producto después de quedar sin disponibilidad en inventario.

    * DENY

    Los compradores no pueden comprar este producto después de agotarse su existencia.

+ _imageId: ID_
+ _imageSrc: String_
+ _mediaSrc: [String!]_
+ _metafields: [MetafieldInput!]_
+ _privateMetafields: [PrivateMetafieldInput!]_
+ _options: [String!]_
+ _taxCode: String_
+ _taxable: Boolean_
+ _harmonizedSystemCode: String_
+ **id: ID**
+ **productId: ID**
+ ~~title: String~~
+ ~~fulfillmentServiceId: ID~~
+ ~~inventoryManagement: ProductVariantInventoryManagement~~


# Para modificar artículos.

La mutación general para modificar la información de un producto es 

## [productUpdate(input: ProductInput!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productUpdate)

El parámetro de esta mutación, ProductInput, corresponde al mismo parámetro descrito para productCreate, con la importante diferencia de que el ID del producto es ahora un campo requerido.

## Para modificar las variantes del artículo

Una salvedad importante es que, en caso de querer agregar o editar la información de las variantes, la información suministrada reemplazaría la información previa correspondiente a variantes del producto. Es decir, toda variante que no sea incluída en la nueva información, sería eliminada.
Es por esto que para modificar información de las variantes es recomendable utilizar 

### [productVariantCreate(input: ProductVariantInput!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productVariantCreate)

Para crear una sola nueva variante a un artículo. Para esto es necesario especificar el productId entre los campos del input.

### [productVariantsBuklCreate(productId: ID!, input: [ProductVariantsBulkInput!]!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productVariantsBulkCreate)

Para crear múltiples variantes nuevas a un sólo producto especificado por el productId. El **ProductVariantsBulkInput** poseee los mísmos campos de **ProductVariantInput**.

De forma similar existen las mutaciones

### [productVariantUpdate(input: ProductVariantInput!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productVariantUpdate)

Para modificar la información de una variante ya existente. No se require especificar productId, pero sí el ID de la variante entre los campos de **ProductVariantInput**.

### [productVariantsBulkUpdate(productId: ID!, input: [ProductVariantsBulkInput!]!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productVariantsBulkUpdate)

Para modificar la información de varias variantes ya existentes.

### [productVariantDelete(id: ID!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productVariantDelete)

Para eliminar una variante según su ID.

### [productVariantsBulkDelete(productId: ID!, variantsIds: [ID!]!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productVariantsBulkDelete)

Para eliminar varias variantes de un producto mediante sus IDs.

### [productVariantsBulkReorder(positions: [ProductVariantPositionInput!]!, productId: ID!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productVariantsBulkReorder)

Para reordenar las variantes pertenecientes a un producto.


Además de estas funciones generales, existen funciones más específicas según lo que se requiera.

## Colecciones

### [collectionAddProducts(id: ID!, productIds: [ID!]!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/collectionAddProducts)

Añade los artículos a una colección manual de la tienda.

### [collectionAddProductsV2(id: ID!, productIds: [ID!]!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/collectionAddProductsV2)

Añade de forma asícrona los artículos a una colección manual de la tienda.

### [collectionRemoveProducts(id: ID!, productIds: [ID!]!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/collectionRemoveProducts)

Retira los artículos previamente agreados a la colección.

## Estatus del producto

### [productChangeStatus(productId: ID!, status: productStatus!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productChangeStatus)

Cambia el estado de disponibilidad del producto según el str productStatus:
* ACTIVE

    El producto está listo para vender y puede ser publicado a canales de venta y aplicaciones.

* ARCHIVED

    El producto ya no se vende y no está disponible a los compradores en los canales de venta y aplicaciones.

* DRAFT

    El producto no está listo para venderse y no está disponible a los compradores en calanes de venta y aplicaciones.

## Media asociada al producto

### [productCreateMedia(media: [createMediaInput!]!, productId: ID!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productCreateMedia)

### [productDeleteMedia(mediaIds: [ID!]!, productId: ID!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productDeleteMedia)

### [productReorderMedia(productId: ID!, moves: [MoveInput!]!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productReorderMedia)

### [productUpdateMedia(media: [UpdateMediaInput!]!, productId: ID!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productUpdateMedia)

### [productVariantAppendMedia(productId: ID!, variantMedia: [ProductVariantAppendMediaInput!]!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productVariantAppendMedia)

### [productVariantDetachMedia(productId: ID!, variantMedia: [ProductVariantDetachMediaInput!]!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productVariantDetachMedia)

### [stagedUploadsCreate(input:[StagedUploadInput!]!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/stagedUploadsCreate)

Para un mejor entendimiento sobre cómo subir media a Shopify y administrarla en los productos creados, se recomienda el tutorial [enlazado](https://shopify.dev/docs/apps/online-store/media/products#step-1-upload-media-to-shopify).

# Para eliminar artículos.

Se utilizan las mutaciones

## [productDelete(input: ProductDeleteInput!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productDelete)

Donde el ProductDeleteInput consiste en el ID del producto a eliminar.
* ProductDeleteInput
    - id: ID

O para productos grandes, con muchas variantes regadas en muchas sucursales, se utiliza 

## [productDeleteAsync(productId: ID!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/productDeleteAsync)
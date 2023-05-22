Función Lambda de AWS para la integración de un inventario de tienda guardado en DynamoDB con una tienda basada en Shopify.

La función requiere la definición de las siguientes variables de entorno para definir parámetros de configuración:
 * DYNAMODB_TABLE: nombre de la tabla de DynamoDB con el inventario a usar.
 * SHOPIFY_SHOP: identificador de la tienda en Shopify.
 * SHOPIFY_ACCESS_TOKEN: el token de acceso de la API de administrador en Shopify.
 * precio: Atributo de precio a usar en Shopify del registro del artículo en la base de datos.

# NOTAS RESPECTO A LÍNEAS

En caso de que el código de línea encontrado en el registro del artículo no se corresponda al código de línea que identifica al registro de línea.
Esto hace imposible identificar la línea y no permite que ocurran cambios en Shopify.

De igual manera, si el atributo de shopifyGID del registro de línea no apunta a una colección en Shopify, los cambios de línea de los artículos no se reflejarán en Shopify.

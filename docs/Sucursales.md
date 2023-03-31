Puedes configurar múltiples sucursales en tu tienda Shopify para que puedas rastrear el inventario y preparar los pedidos en tus sucursales. Tus sucursales pueden ser tiendas minoristas, depósitos, temporales, dropshippers o cualquier otro lugar donde administres o almacenes el inventario. Las múltiples sucursales te permitirán tener una mejor visibilidad del inventario de todo tu negocio.

Una sucursal es un lugar físico o una app donde realizas una o cualquiera de las siguientes actividades: vender productos, enviar o preparar pedidos o almacenar inventario.

# Para crear sucursales

Para crear sucursales se utiliza la mutación de   
[locationAdd(input: LocationAddINput!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/locationAdd)

LocationAddInput
 * address: LocationAddAddressInput!
    - address1: String

        Primer línea de dirección.

    - address2: String

        Segunda línea de dirección.

    - city: String

        Nombre de la ciudad, distrito, villa o región.

    - countryCode: CountryCode!

        Código de dos letras del país. Por ejemplo: VE.

    - phone: String

        Número de teléfono de la sucursal.

    - provinceCode: String

        El código de la región de la dirección, tal como el estado, provincia o distrito.

    - zip: String

        Código ZIP o postal de la sucursal.

 * fulfillsOnlineOrders: Boolean

    Si el inventario en esta sucursal está dispobible para la venta en línea.

 * name: String!

    El nombre de la sucursal.


# Modificación de las sucursales

Tras la creación de las sucursales, utilizando el ID correspondiente se pueden modificar utilizando las siguientes mutaciones.

## [locationActivate(locationId: ID!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/locationActivate)

Para activar la sucursal.

## [locationDeactivate(locationId: ID!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/locationDeactivate)

Para desactivar la sucursal.

## [locationLocalPickupEnlable(locationId: ID!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/locationLocalPickupEnable)

Para activar esta sucursal como punto de despacho.

## [locationLocalPickupDisable(locationId: ID!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/locationLocalPickupDisable)

Para desactivar esta sucursal como punto de despacho.

## [locationEdit(locationId: ID!, input: LocationEditInput!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/locationEdit)

Para editar cualquier información suministrada al momento de crear la sucursal.

# Eliminar sucursales

Para eliminar una sucursal junto a toda su información de inventario, se utiliza la mutación.  
[locationDelete(locationId: ID!)](https://shopify.dev/docs/api/admin-graphql/2023-01/mutations/locationActivate)
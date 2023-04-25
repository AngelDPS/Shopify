from gql import gql

producto = gql(
    """
    query consultarGidVariante($id: ID!){
        product(id: $id){
            variants(first: 1){
                nodes {
                    id
                }
            }
        }
    }

    query consultarGidInventario($id: ID!){
        product(id: $id) {
            variants(first: 1) {
                nodes {
                    inventoryItem {
                        id
                    }
                }
            }
        }
    }

    mutation crearProducto($input: ProductInput!, $media: [CreateMediaInput!]){
        productCreate(input: $input, media: $media) {
            product {
                ... ProductoInfo
            }
            userErrors {
                message
            }
        }
    }

    mutation modificarProducto($input: ProductInput!) {
        productUpdate(input: $input) {
            product {
                ... ProductoInfo
            }
            userErrors {
                message
            }
        }
    }

    mutation modificarVarianteProducto($input: ProductVariantInput!) {
        productVariantUpdate(input: $input) {
            userErrors {
                message
            }
        }
    }

   mutation establecerInventarioDisponible(
       $inventoryId: ID!, $locationId: ID!, $qty: Int!
    ) {
    inventorySetOnHandQuantities(
        input: {reason: "correction", setQuantities: {
            inventoryItemId: $inventoryId,
            locationId: $locationId,
            quantity: $qty
            }}
    ) {
            inventoryAdjustmentGroup {
                changes {
                    delta
                }
            }
            userErrors {
            message
            }
        }
    }

    mutation ajustarInventarios(
        $delta: Int!,
        $inventoryItemId: ID!,
        $locationId: ID!,
        $name: String!,
        $reason: String!
    ) {
        inventoryAdjustQuantities(input: {
            changes: [
                {
                    delta: $delta,
                    inventoryItemId: $inventoryItemId,
                    locationId: $locationId
                }
            ],
            name: $name,
            reason: $reason
            }){
            userErrors {
                message
            }
        }
    }

    fragment ProductoInfo on Product {
        id
        productType
        status
        title
        variants(first: 1) {
            nodes {
                id
                inventoryItem {
                    id
                }
            }
        }
    }
    """
)

coleccion = gql(
    """
    mutation crearColeccion($input: CollectionInput!) {
        collectionCreate(input: $input) {
            collection {
            ... coleccionInfo
            }
            userErrors {
                field
                message
            }
        }
    }

    mutation modificarColeccion($input: CollectionInput!) {
        collectionUpdate(input: $input) {
            collection {
                ... coleccionInfo
            }
            userErrors {
            field
            message
            }
        }
    }

    mutation agregarProductos($id: ID!, $productIds: [ID!]!) {
        collectionAddProductsV2(id: $id, productIds: $productIds)
        {
            job {
                done
            }
            userErrors {
                field
                message
            }
        }
    }

    fragment coleccionInfo on Collection {
        title
        id
        description
        productsCount
    }
    """
)

sucursal = gql(
    """
    mutation crearSucursal($input: LocationAddInput!) {
        locationAdd(input: $input) {
            location{
                ... SucursalInfo
            }
            userErrors {
                message
            }
        }
    }

    mutation modificarSucursal($id: ID!, $input: LocationEditInput!) {
        locationEdit(id: $id, input: $input) {
            location {
                ... SucursalInfo
            }
            userErrors {
               message
            }
        }
    }

    mutation activarSucursal($id: ID!) {
        locationActivate(locationId: $id) {
            locationActivateUserErrors {
                message
            }
        }
    }

    mutation desactivarSucursal($id: ID!, $altId: ID) {
        locationDeactivate(locationId: $id, destinationLocationId: $altId){
            location {
                ... SucursalInfo
            }
            locationDeactivateUserErrors {
               message
            }
        }
    }

    fragment SucursalInfo on Location {
        id
        name
        address {
            formatted
        }
        isActive
        hasActiveInventory
    }
    """
)

misc = gql(
    """
    query obtenerPublicaciones {
        publications(first: 2) {
            nodes {
                id
            }
        }
    }

    mutation publicar($id: ID!, $input: [PublicationInput!]!) {
        publishablePublish(id: $id, input: $input) {
            userErrors {
                field
                message
            }
        }
    }

    mutation ocultar($id: ID!, $input: [PublicationInput!]!) {
        publishableUnpublish(id: $id, input: $input) {
            userErrors {
                field
                message
            }
        }
    }
    """
)

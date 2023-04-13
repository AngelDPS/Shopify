from gql import gql

coleccion = gql(
    """
    query consultar($id: ID!) {
        collection(id: $id) {
            ... coleccionInfo
        }
    }

    mutation crear($input: CollectionInput!) {
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

    mutation modificar($input: CollectionInput!) {
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

    mutation eliminar($id: ID!) {
        collectionDelete(input: {id: $id}) {
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
    query consultar($id: ID) {
        location(id: $id) {
            ... SucursalInfo
        }
    }


    mutation crear($input: LocationAddInput!) {
        locationAdd(input: $input) {
            location{
                ... SucursalInfo
            }
            userErrors {
                message
            }
        }
    }


    mutation modificar($id: ID!, $input: LocationEditInput!) {
        locationEdit(id: $id, input: $input) {
            location {
                ... SucursalInfo
            }
            userErrors {
               message
            }
        }
    }

    mutation eliminar($id: ID!) {
        locationDelete(locationId: $id) {
            locationDeleteUserErrors {
                message
            }
        }
    }

    mutation activar($id: ID!) {
        locationActivate(locationId: $id) {
            locationActivateUserErrors {
                message
            }
        }
    }


    mutation desactivar($id: ID!, $altId: ID) {
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
    mutation publicar($id: ID!, $input: [publicationInput!]!) {
        publishablePublish(id: $id, input: $input) {
            userErrors {
                field
                message
            }
        }
    }

    mutation ocultar($id: ID!, $input: [publicationInput!]!) {
        publishableUnpublish(id: $id, input: $input) {
            userErrors {
                field
                message
            }
        }
    }
    """
)

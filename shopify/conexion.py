import logging
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import (
    TransportQueryError,
    TransportServerError
)
from shopify.models.producto import MproductInput, MproductVariantInput
from shopify.models.coleccion import McollectionInput
from shopify.models.evento import Mlinea
import os

logger = logging.getLogger(__name__)

try:
    SHOP = os.environ['SHOPIFY_SHOP']
except KeyError:
    logger.exception("No se encontró en la variable de ambiente 'SHOPIFY_SHOP'"
                     " el identificador del URL de la tienda de shopify.")
    raise
try:
    ACCESS_TOKEN = os.environ['SHOPIFY_ACCESS_TOKEN']
except KeyError:
    logger.exception("No se encontró en la variable de ambiente "
                     "'SHOPIFY_ACCESS_TOKEN' el token de acceso para la "
                     "aplicación admin de la tienda de shopify.")
    raise

API_VERSION: str = "2023-04"
URL = f"https://{SHOP}.myshopify.com/admin/api/{API_VERSION}/graphql.json"

transport = RequestsHTTPTransport(
    URL,
    headers={'X-Shopify-Access-Token': ACCESS_TOKEN},
    retries=3
)
cliente = Client(transport=transport)


def execute(request_str: str,
            operacion: str = None,
            variables: dict = None
            ) -> dict:
    """Envía una consulta de GraphQL usando el transporte inicializado en
    la instancia.

    Args:
        request_str (str): Consulta de graphQL
        variables (dict, optional): Variables que 'request' puede utilizar
        para realizar la consulta. Defaults to None.
        operacion (str, optional): Si 'request' esta compuesta de varias
        operaciones posibles. 'operacion' selecciona la que se va a
        utilizar. Defaults to None.

    Returns:
        dict: Json deseralizado recibido como respuesta a la consulta.
    """
    logger.debug(f'{variables = }')
    try:
        respuesta = cliente.execute(
            gql(request_str),
            variable_values=variables,
            operation_name=operacion
        )
        logger.debug(f"{respuesta = }")
    except TransportQueryError as err:
        logger.exception(
            "Hubo un problema con la consulta, "
            f"el servidor retornó un error {err}."
        )
        raise
    except TransportServerError as err:
        logger.exception(
            "Hubo un problema con el servidor, "
            f"retornó un código {err.code}"
        )
        raise
    except Exception as err:
        logger.exception(
            f"Se encontró un error inesperado.\n{type(err)}\n{err}"
        )
        raise
    else:
        if respuesta[list(respuesta)[0]].get("userErrors"):
            msg = ("No fue posible realizar la operación:\n"
                   f"{respuesta['userErrors']}")
            logger.exception(msg)
            raise RuntimeError(msg)
    return respuesta


def obtenerGidTienda(nombre: str) -> str:
    try:
        return execute(
            """
            query Tienda($nombre: String) {
                locations(first: 1, query: $nombre) {
                    nodes {
                        id
                    }
                }
            }
            """,
            variables={"nombre": f"name:{nombre}"}
        )['locations']['nodes'][0]['id']
    except Exception:
        logger.exception("Error al consultar el GID de sucursal.")
        raise


def obtenerGidPublicaciones():
    pubIDs = [i["id"] for i in
              execute(
        """
                query obtenerPublicaciones {
                    publications(first: 2) {
                        nodes {
                            id
                        }
                    }
                }
                """
    )['publications']['nodes']]
    return pubIDs


def publicarRecurso(GID: str, pubIDs: list[str]):
    try:
        execute(
            """
            mutation publicar($id: ID!, $input: [PublicationInput!]!) {
                publishablePublish(id: $id, input: $input) {
                    userErrors {
                        message
                    }
                }
            }
            """,
            variables={
                'id': GID,
                'input': [{"publicationId": id}
                          for id in pubIDs]
            }
        )
        logger.info("Publicación exitosa del recurso.")
    except Exception:
        logger.exception("No se pudo publicar el recurso.")
        raise


def crearProducto(productInput: MproductInput) -> str:
    try:
        respuesta = execute(
            """
            mutation crearProducto($input: ProductInput!,
                    $media: [CreateMediaInput!]){
                productCreate(input: $input, media: $media) {
                    product {
                        id
                        variants(first: 1) {
                            nodes {
                                id
                                inventoryItem {
                                    id
                                }
                            }
                        }
                    }
                    userErrors {
                        message
                    }
                }
            }
            """,
            variables={'input': productInput.dict(exclude_none=True)}
        )
        logger.info("Producto creado exitosamente en Shopify.")
    except Exception:
        logger.exception("Error encontrado al crear el producto en Shopify.")
        raise
    try:
        shopifyGID = {
            'producto': respuesta['productCreate']['product']['id'],
            'variante': {
                'id': (respuesta['productCreate']['product']
                       ['variants']['nodes'][0]['id']),
                'inventario': (respuesta['productCreate']['product']
                               ['variants']['nodes'][0]['inventoryItem']
                               ['id'])
            }
        }
        return shopifyGID
    except (KeyError, IndexError):
        logger.exception("Formato inesperado de respuesta para la creación "
                         "del producto.")
        raise


def modificarInventario(delta: int, invId: str, locId: str):
    try:
        reason = "restock" if delta > 0 else "shrinkage"
        execute(
            """
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
                """,
            variables={
                "delta": delta,
                "name": "available",
                "reason": reason,
                "inventoryItemId": invId,
                "locationId": locId
            }
        )
        logger.info("Inventario modificado exitosamente.")
    except Exception:
        logger.exception("Ocurrió un error al tratar de modificar el "
                         "inventario.")
        raise


def modificarVarianteProducto(variantInput: MproductVariantInput):
    try:
        execute(
            """
            mutation modificarVarianteProducto(
                    $input: ProductVariantInput!
                ) {
                productVariantUpdate(input: $input) {
                    userErrors {
                        message
                    }
                }
            }
            """,
            variables={'input': variantInput.dict(exclude_none=True)}
        )
        logger.info("Variante modificado exitosamente.")
    except Exception:
        logger.exception("Ocurrió un error al tratar de modificar la "
                         "variante del producto.")
        raise


def modificarProducto(productInput: MproductInput):
    try:
        execute(
            """
            mutation modificarProducto($input: ProductInput!) {
                productUpdate(input: $input) {
                    userErrors {
                        message
                    }
                }
            }
            """,
            variables={'input': productInput.dict(exclude_none=True)}
        )
        logger.info("Producto modificado exitosamente.")
    except Exception:
        logger.exception("Ocurrió un error al tratar de modificar el "
                         "producto.")
        raise


def consultarProducto(nombre: str):
    try:
        respuesta = execute(
            """
            query productoPorNombre($nombre: String) {
                products(first: 1, query: $nombre) {
                    nodes {
                        id
                        variants(first: 1) {
                            nodes {
                                id
                                inventoryItem {
                                    id
                                    inventoryLevels(first: 10) {
                                        nodes {
                                            location {
                                                name
                                                id
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """
        )
    except Exception:
        logger.exception("Hubo un problema al consultar el producto en "
                         "Shopify.")
        raise
    try:
        shopifyGID = {
            'producto': respuesta['products']['nodes'][0]['id'],
            'variante': {
                'id': (respuesta['products']['nodes'][0]
                       ['variants']['nodes'][0]['id']),
                'inventario': (respuesta['products']['nodes'][0]
                               ['variants']['nodes'][0]['inventoryItem']
                               ['id'])
            }
        }
        locations = {
            loc['name']: loc['id'] for loc in (
                respuesta['products']['nodes'][0]['variants']['nodes'][0]
                ['inventoryItem']['inventory']
            )
        }
        return (shopifyGID, locations)
    except (KeyError, IndexError):
        logger.exception("Formato inesperado de respuesta para la creación "
                         "del producto.")
        raise


def obtenerGidColeccion(nombre: str) -> str:
    try:
        return execute(
            """
            query coleccionPorNombre($nombre: String) {
                collections(query: $nombre, first: 1) {
                    nodes {
                    id
                    }
                }
            }
            """,
            variables={"nombre": f"title:{nombre}"}
        )['collections']['nodes'][0]['id']
    except IndexError:
        logger.warning(f"Colección con nombre '{nombre}' no encontrada.")
        raise
    except Exception:
        logger.exception("Error al consultar el GID de colección.")
        raise


def crearColeccion(linea: Mlinea) -> str:
    try:
        return execute(
            """
            mutation crearColeccion($input: CollectionInput!) {
                collectionCreate(input: $input) {
                    collection {
                        id
                    }
                    userErrors {
                        message
                    }
                }
            }
            """,
            variables={
                'input': McollectionInput.parse_obj(linea).dict(
                    exclude_none=True
                )
            }
        )["collectionCreate"]["collection"]["id"]
    except Exception:
        logger.exception("Error encontrado al crear la colección en Shopify")
        raise


def modificarColeccion(linea: Mlinea):
    collectionInput = McollectionInput.parse_obj(
        linea.dict(by_alias=True, exclude_none=True)
    )
    execute(
        """
        mutation modificarColeccion($input: CollectionInput!) {
            collectionUpdate(input: $input) {
                userErrors {
                message
                }
            }
        }
        """,
        variables={'input': collectionInput.dict(exclude_none=True)},
    )

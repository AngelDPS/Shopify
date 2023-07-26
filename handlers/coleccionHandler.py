from models.evento import Mlinea
from models.coleccion import McollectionInput
from re import search
from libs.dynamodb import (
    guardar_linea_id,
    obtener_tienda,
    guardar_publicaciones_id
)
from libs.conexion import (
    ClienteShopify,
    obtener_publicaciones_id,
    publicar_recurso
)
from libs.util import ItemHandler
from aws_lambda_powertools import Logger

logger = Logger(child=True, service="shopify")


def shopify_obtener_id(nombre: str, client: ClienteShopify = None) -> str:
    try:
        client = client or ClienteShopify()
        return client.execute(
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


def shopify_crear_coleccion(collection_input: McollectionInput,
                            client: ClienteShopify = None) -> str:
    try:
        client = client or ClienteShopify()
        return client.execute(
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
                'input': collection_input.dict(exclude_none=True)
            }
        )["collectionCreate"]["collection"]["id"]
    except Exception:
        logger.exception("Error encontrado al crear la colección en Shopify")
        raise


def modificarColeccion(collection_input: McollectionInput,
                       client: ClienteShopify = None):
    client = client or ClienteShopify()
    client.execute(
        """
        mutation modificarColeccion($input: CollectionInput!) {
            collectionUpdate(input: $input) {
                userErrors {
                message
                }
            }
        }
        """,
        variables={'input': collection_input.dict(exclude_none=True,
                                                  exclude_unset=True)},
    )


class ColeccionHandler(ItemHandler):
    item = "colección"

    def __init__(self, evento, client: ClienteShopify = None):
        self.old_image = Mlinea.parse_obj(evento.old_image)
        self.cambios = Mlinea.parse_obj(evento.cambios)
        self.client = client or ClienteShopify()
        self.session = None

    @classmethod
    def desde_linea(cls, linea: dict, client: ClienteShopify = None):
        evento = type("evento", (), {
            "cambios": linea,
            "old_image": {}
        })
        return cls(evento, client)

    def guardar_id_dynamo(self):
        logger.debug(f"GID de línea: {self.old_image.shopify_id}")
        guardar_linea_id(
            PK=self.cambios.PK or self.old_image.PK,
            SK=self.cambios.SK or self.old_image.SK,
            GID=self.old_image.shopify_id
        )

    def obtener_publicaciones_id(self) -> str:
        try:
            codigoCompania = search(r"\w+(?=#LINEAS)",
                                    self.cambios.PK or self.old_image.PK)[0]
            SK = self.cambios.SK or self.old_image.SK
            codigoTienda = search(r"(?<=T#)\w+", SK)[0]
            tienda = obtener_tienda(
                codigoCompania,
                codigoTienda
            )
            return tienda['shopify_id']['publicaciones']
        except KeyError:
            pass
        try:
            logger.warning("No se encontró el GID de los canales de "
                           "publicación en la base de datos. Se procederá a "
                           "consultar el GID a Shopify y a guardar el "
                           "resultado obtenido.")
            tienda.setdefault('shopify_id', {})
            tienda['shopify_id']['publicaciones'] = (
                obtener_publicaciones_id(self.session or self.client)
            )
            guardar_publicaciones_id(
                codigoCompania=codigoCompania,
                codigoTienda=codigoTienda,
                pubIDs=tienda['shopify_id']['publicaciones']
            )
            return tienda['shopify_id']['publicaciones']
        except Exception:
            logger.exception("Error al obtener los GIDs de los canales de "
                             "publicación.")
            raise

    def crear(self) -> list[dict]:
        """Función dedicada a crear una colección en Shopify dada
        la información de un evento de línea INSERT

        Returns:
            list[dict]: Lista con las respuestas de las operaciones de crear y
            publicar la colección en Shopify.
        """
        logger.info("Creando colección a partir de línea.")

        try:
            collection_input = McollectionInput.parse_obj(
                self.cambios.dict(by_alias=True, exclude_none=True)
            )
            logger.debug(collection_input)
            self.old_image.shopify_id = shopify_crear_coleccion(
                collection_input,
                self.session or self.client
            )
            self.guardar_id_dynamo()
            logger.info("Colección creada exitosamente.")
            return "Colección creada exitosamente."
        except Exception:
            logger.exception("No fue posible crear la colección")
            raise

    def _publicar(self):
        """Publica el artículo en la tienda virtual y punto de venta de
        Shopify.
        """
        if self.cambios.shopify_id:
            publicar_recurso(
                GID=self.old_image.shopify_id,
                pubIDs=self.obtener_publicaciones_id(),
                client=self.session or self.client
            )
            return "Colección publicada!"
        else:
            return ""

    def modificar(self) -> list[dict]:
        self.old_image.shopify_id = (
            self.cambios.shopify_id or self.old_image.shopify_id
        )
        r = []
        try:
            r.append(self._publicar())
            collection_input = McollectionInput.parse_obj(
                self.cambios.dict(by_alias=True, exclude_none=True,
                                  exclude_unset=True)
            )
            if collection_input.dict(exclude_unset=True):
                collection_input.id = self.old_image.shopify_id
                modificarColeccion(collection_input,
                                   self.session or self.client)
                r.append("Coleccion modificada exitosamente.")
            return r
        except Exception:
            logger.exception("No fue posible modificar la colección.")
            raise

    def ejecutar(self):
        try:
            with self.client as self.session:
                if not self.old_image.shopify_id and self.old_image.nombre:
                    try:
                        self.old_image.shopify_id = shopify_obtener_id(
                            self.old_image.nombre,
                            self.session or self.client
                        )
                        self.guardar_id_dynamo()
                    except IndexError:
                        pass
                respuesta = super().ejecutar("Shopify",
                                             self.cambios.shopify_id
                                             or self.old_image.shopify_id)
                return respuesta
        except Exception:
            logger.exception("Ocurrió un problema ejecutando la acción sobre "
                             "la colección")
            raise

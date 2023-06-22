import logging
from models.evento import Mlinea
from models.coleccion import McollectionInput
from re import search
from libs.dynamodb import (
    actualizarGidLinea,
    obtenerTienda,
    actualizarGidPublicacionesTienda
)
from libs.conexion import (
    ClienteShopify,
    obtenerGidPublicaciones,
    publicarRecurso
)

logger = logging.getLogger("shopify.coleccionHandler")


def obtenerGidColeccion(nombre: str, client: ClienteShopify = None) -> str:
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


def crearColeccion(collectionInput: McollectionInput,
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
                'input': collectionInput.dict(exclude_none=True)
            }
        )["collectionCreate"]["collection"]["id"]
    except Exception:
        logger.exception("Error encontrado al crear la colección en Shopify")
        raise


def modificarColeccion(collectionInput: McollectionInput,
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
        variables={'input': collectionInput.dict(exclude_none=True,
                                                 exclude_unset=True)},
    )


class ColeccionHandler:

    def __init__(self, evento, client: ClienteShopify = None):
        self.eventName = evento.eventName
        self.NewImage = Mlinea.parse_obj(evento.NewImage)
        self.OldImage = Mlinea.parse_obj(evento.OldImage)
        self.cambios = Mlinea.parse_obj(
            evento.obtenerCambios(self.NewImage, self.OldImage)
        )
        self.client = client or ClienteShopify()
        self.session = None

    @classmethod
    def desde_linea(cls, linea: dict, client: ClienteShopify = None):
        evento = type("evento", (), {
            "eventName": "INSERT",
            "NewImage": linea,
            "OldImage": linea,
            "obtenerCambios": (lambda x, y: {})
        })
        return cls(evento, client)

    def actualizarGidBD(self):
        logger.debug(f"GID de línea: {self.NewImage.shopifyGID}")
        actualizarGidLinea(
            PK=self.NewImage.PK,
            SK=self.NewImage.SK,
            GID=self.NewImage.shopifyGID
        )

    def obtenerGidPublicaciones(self, use_old: bool = False) -> str:
        try:
            codigoCompania = search(r"\w+(?=#LINEAS)", self.NewImage.PK)[0]
            SK = self.NewImage.SK if not use_old else self.OldImage.SK
            codigoTienda = search(r"(?<=T#)\w+", SK)[0]
            tienda = obtenerTienda(
                codigoCompania,
                codigoTienda
            )
            return tienda['shopifyGID']['publicaciones']
        except KeyError:
            pass
        try:
            logger.warning("No se encontró el GID de los canales de "
                           "publicación en la base de datos. Se procederá a "
                           "consultar el GID a Shopify y a guardar el "
                           "resultado obtenido.")
            tienda.setdefault('shopifyGID', {})
            tienda['shopifyGID']['publicaciones'] = (
                obtenerGidPublicaciones(self.session or self.client)
            )
            actualizarGidPublicacionesTienda(
                codigoCompania=codigoCompania,
                codigoTienda=codigoTienda,
                pubIDs=tienda['shopifyGID']['publicaciones']
            )
            return tienda['shopifyGID']['publicaciones']
        except Exception:
            logger.exception("Error al obtener los GIDs de los canales de "
                             "publicación.")
            raise

    def publicar(self):
        """Publica el artículo en la tienda virtual y punto de venta de
        Shopify.
        """
        publicarRecurso(
            GID=self.NewImage.shopifyGID,
            pubIDs=self.obtenerGidPublicaciones(),
            client=self.session or self.client
        )

    def crear(self) -> list[dict]:
        """Función dedicada a crear una colección en Shopify dada
        la información de un evento de línea INSERT

        Returns:
            list[dict]: Lista con las respuestas de las operaciones de crear y
            publicar la colección en Shopify.
        """
        logger.info("Creando colección a partir de línea.")

        try:
            collectionInput = McollectionInput.parse_obj(
                self.NewImage.dict(by_alias=True, exclude_none=True)
            )
            self.NewImage.shopifyGID = crearColeccion(
                collectionInput,
                self.session or self.client
            )
            self.publicar()
            self.actualizarGidBD()
            logger.info("Colección creada exitosamente.")
            return "Colección creada exitosamente."
        except Exception:
            logger.exception("No fue posible crear la colección")
            raise

    def modificar(self) -> list[dict]:
        try:
            collectionInput = McollectionInput.parse_obj(
                self.cambios.dict(by_alias=True, exclude_none=True,
                                  exclude_unset=True)
            )
            collectionInput.id = self.NewImage.shopifyGID
            modificarColeccion(collectionInput, self.session or self.client)
            logger.info("La colección fue modificada exitosamente.")
            return "Coleccion modificada exitosamente."
        except Exception:
            logger.exception("No fue posible modificar la colección.")
            raise

    def ejecutar(self):
        try:
            with self.client as self.session:
                if self.eventName == "INSERT":
                    respuesta = self.crear()
                elif self.cambios.dict(exclude_none=True, exclude_unset=True):
                    if self.NewImage.shopifyGID:
                        respuesta = self.modificar()
                    else:
                        logger.warning(
                            "En el evento no se encontró el GID de "
                            "Shopify proveniente de la base de datos.\n"
                            "Se consultará a Shopify por su "
                            "existencia."
                        )
                        try:
                            self.NewImage.shopifyGID = (
                                obtenerGidColeccion(
                                    self.NewImage.nombre,
                                    self.session or self.client)
                            )
                            self.actualizarGidBD()
                            respuesta = self.modificar()
                        except IndexError:
                            logger.warning(
                                "La colección correspondiente no existe"
                                " en Shopify. Se creará una colección "
                                "nueva con la data actualizada."
                            )
                            respuesta = self.crear()
                else:
                    logger.info("Los cambios encontrados no ameritan "
                                "actualizaciones en Shopify.")
                    respuesta = ["No se realizaron acciones."]
                return respuesta
        except Exception:
            logger.exception("Ocurrió un problema ejecutando la acción sobre "
                             "la colección")
            raise

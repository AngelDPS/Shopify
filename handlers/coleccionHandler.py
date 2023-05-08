import logging
from models.coleccion import McollectionInput
from libs.conexion import ConexionShopify
from json import load, dump
from os import rename
from gql import gql
from re import search

logger = logging.getLogger("Shopify.Coleccion")


class Coleccion:

    gqlrequests = """
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

        fragment coleccionInfo on Collection {
            title
            id
            description
            productsCount
        }
        """
    conexion = ConexionShopify(gqlrequests)

    def actualizarGidBD(self):
        DBpath = 'DB/GENERICO2022.json'
        DBpath_temp = DBpath + '.temp'
        with open(DBpath) as DBfile, open(DBpath_temp, 'w') as DBtemp:
            try:
                DB = load(DBfile)
                DB.setdefault('lineas', {}).setdefault(self.NewImage.SK, {})
                DB['lineas'][self.NewImage.SK]['shopifyGID'] = (
                    self.NewImage.shopifyGID
                )
                dump(DB, DBtemp)
            except TypeError as err:
                logger.exception("Hubo un problema actualizando la base "
                                 "de datos. Asegurese que el tipo de la "
                                 "data sea serializable a json.")
                logger.debug(f"{DB = }")
                err.add_note("No se pudo serializar la data entrante a la BD.")
                raise
            else:
                rename(DBpath_temp, DBpath)

    def obtenerGidPublicaciones(self) -> str:
        DBpath = 'DB/GENERICO2022.json'
        with open(DBpath) as DBfile:
            DB = load(DBfile)
        codigoTienda = search(r"(?<=T#)\w+", self.NewImage.SK)[0]
        tienda = DB['tiendas'][codigoTienda]
        try:
            return tienda['shopifyGID']['publicaciones']
        except KeyError:
            tienda['shopifyGID']['publicaciones'] = [
                i['id'] for i in
                self.conexion.execute(
                    gql("""
                        query obtenerPublicaciones {
                            publications(first: 2) {
                                nodes {
                                    id
                                }
                            }
                        }
                        """)
                )['publications']['nodes']
            ]
            DB['tiendas'][codigoTienda] |= tienda
            DBpath_temp = DBpath + '.temp'
            with open(DBpath_temp, 'w') as DBtemp:
                dump(DB, DBtemp)
            rename(DBpath_temp, DBpath)
            return tienda['shopifyGID']['publicaciones']

    def __init__(self, evento):
        self.NewImage = getattr(evento, "NewImage", False) or evento
        self.OldImage = getattr(evento, "OldImage", None)
        self.cambios = getattr(evento, "cambios", None)

    def publicar(self) -> dict:
        """Publica el artículo en la tienda virtual y punto de venta de
        Shopify.

        Returns:
            dict: Json deserealizado con la respuesta obtenida.
        """
        try:
            respuesta = self.conexion.execute(
                gql("""
                    mutation publicar($id: ID!, $input: [PublicationInput!]!) {
                        publishablePublish(id: $id, input: $input) {
                            userErrors {
                                field
                                message
                            }
                        }
                    }
                    """),
                variables={
                    'id': self.NewImage.shopifyGID,
                    'input': [{"publicationId": id}
                              for id in self.obtenerGidPublicaciones()]
                }
            )
            logger.info("Publicación exitosa de la colección.")
            return respuesta
        except Exception:
            logger.exception("No se pudo publicar la colección.")
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
            respuestas = [self.conexion.execute(
                gql("""
                    mutation crearColeccion($input: CollectionInput!) {
                        collectionCreate(input: $input) {
                            collection {
                                id
                            }
                            userErrors {
                                field
                                message
                            }
                        }
                    }
                    """),
                variables={
                    'input': (McollectionInput.parse_obj(self.NewImage)
                              .dict(exclude_none=True))
                }
            )]
            self.NewImage.shopifyGID = (
                respuestas[0]["collectionCreate"]["collection"]["id"]
            )
            respuestas.append(self.publicar())
            self.actualizarGidBD()
            logger.info("Colección creada exitosamente.")
            return respuestas
        except Exception as err:
            logger.exception("No fue posible crear la colección")
            err.add_note("Ocurrieron problemas creando la colección")
            raise

    def modificar(self) -> list[dict]:
        try:
            shopifyInput = McollectionInput.parse_obj(
                self.cambios.dict(by_alias=True, exclude_none=True)
            )
            respuestas = [self.request(
                "modificarColeccion",
                variables={'input': shopifyInput.dict(exclude_none=True)},
            )]
            logger.info("La colección fue modificada exitosamente.")
            return respuestas
        except Exception as err:
            logger.exception("No fue posible modificar la colección.")
            err.add_note("Ocurrieron problemas modificando la colección.")
            raise

    def ejecutar(self):
        try:
            if not self.OldImage:
                respuestas = self.crear()
            elif self.cambios:
                respuestas = self.modificar()
            return respuestas
        except Exception as err:
            err.add_note("Ocurrió un problema ejecutando la acción sobre la"
                         "colección")
            raise

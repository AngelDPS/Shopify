import logging
from models.coleccion import McollectionInput
from models.evento import Mlinea
from libs.conexion import ConexionShopify
from libs import gqlrequests
from json import load, dump
from os import rename


class Coleccion:

    def actualizarBD(self, codigoCompania: str, co_lin: str, gid: str):
        DBpath = f'DB/{codigoCompania}.json'
        DBpath_temp = DBpath + '.temp'
        with open(DBpath) as DBfile, open(DBpath_temp, 'w') as DBtemp:
            try:
                DB = load(DBfile)
                DB.setdefault('gids', {}).setdefault('lineas', {})
                DB['gids']['lineas'][co_lin] = gid
                dump(DB, DBtemp)
            except TypeError as err:
                self.logger.exception("Hubo un problema actualizando la base "
                                      "de datos. Asegurese que el tipo de la "
                                      "data sea serializable a json.")
                self.logger.debug(f"{DB = }")
                err.add_note("No se pudo serializar la data entrante a la BD.")
                raise
            else:
                rename(DBpath_temp, DBpath)

    @staticmethod
    def obtenerGid(codigoCompania: str, co_lin: str) -> str:
        DBpath = f'DB/{codigoCompania}.json'
        with open(DBpath) as DBfile:
            return load(DBfile)['gids']['lineas'][co_lin]

    def __init__(self, evento):
        self.logger = logging.getLogger("Shopify.Coleccion")
        self.NewImage = evento.NewImage
        self.OldImage = evento.OldImage
        self.cambios = evento.cambios
        self.conexion = ConexionShopify(evento.config['shopify'])
        # TODO: Información de configuración
        # "shopify": {
        # "tienda": "generico2022-8056",
        # "access_token": "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"
        # },

    def request(self, operacion: str, variables: dict = None) -> dict:
        """Funcion que realiza operaciones al servidor GraphQL de la tienda
        de Shopify. Las operaciones son seleccionadas de una lista predefinida
        en 'gqlrequests.coleccion'

        Args:
            operacion (str): Nombre de la operación a usar, definida en
            'gqlrequests.coleccion'
            variables (dict, optional): variables que la operación puede
            utilizar. Defaults to None.

        Raises:
            RuntimeError: En caso de que la operación presente un problema
            en la respuesta.

        Returns:
            dict: Json deserealizado con la respuesta obtenida.
        """
        self.logger.debug(f'{variables = }')
        respuesta = (self.conexion.enviarConsulta(
            gqlrequests.coleccion,
            variables=variables,
            operacion=operacion))
        if respuesta[list(respuesta)[0]].get("userErrors"):
            msg = ("No fue posible realizar la operación:\n"
                   f"{respuesta['userErrors']}")
            self.logger.exception(msg)
            raise RuntimeError(msg)
        return respuesta

    def publicar(self, gid: str) -> dict:
        try:
            publicationIds = self.conexion.enviarConsulta(
                gqlrequests.misc, operacion="obtenerPublicaciones"
            )['publications']['nodes']
            respuesta = self.conexion.enviarConsulta(
                gqlrequests.misc,
                operacion='publicar',
                variables={
                    'id': gid,
                    'input': [{"publicationId": i["id"]}
                              for i in publicationIds]
                }
            )
            self.logger.info("Publicación exitosa de la coleccion.")
            return respuesta
        except Exception as err:
            self.logger.exception("No se pudo publicar la colección")
            err.add_note("Error/es encontrado publicando la colección.")
            raise

    def crear(self, input: Mlinea) -> list[dict]:
        """Función dedicada a crear una colección en Shopify dada
        la información de un evento de línea INSERT

        Args:
            input (Mlinea): Información deserealizada de DynamoDB con la línea
            a crear

        Returns:
            list[dict]: Lista con las respuestas de las operaciones de crear y
            publicar la colección en Shopify.
        """
        self.logger.info("Creando colección a partir de línea.")
        try:
            respuestas = [self.request(
                "crearColeccion",
                variables={
                    'input': (McollectionInput.parse_obj(input)
                              .dict(exclude_none=True))
                }
            )]
            respuestas.append(self.publicar(
                respuestas[0]["collectionCreate"]["collection"]["id"]
            ))
            self.actualizarBD(
                input.codigoCompania,
                input.co_lin,
                respuestas[0]["collectionCreate"]["collection"]["id"]
            )
            self.logger.info("Colección creada exitosamente.")
            return respuestas
        except Exception as err:
            self.logger.exception("No fue posible crear la colección")
            err.add_note("Ocurrieron problemas creando la colección")
            raise

    def modificar(self, input: Mlinea) -> list[dict]:
        try:
            shopifyInput = McollectionInput.parse_obj(
                input.dict(by_alias=True, exclude_none=True)
            )
            shopifyInput.id = self.obtenerGid(self.OldImage.codigoCompania,
                                              self.OldImage.co_lin)
            respuestas = [self.request(
                "modificarColeccion",
                variables={'input': shopifyInput.dict(exclude_none=True)},
            )]
            self.logger.info("La colección fue modificada exitosamente.")
            return respuestas
        except Exception as err:
            self.logger.exception("No fue posible modificar la colección.")
            err.add_note("Ocurrieron problemas modificando la colección.")
            raise

    def ejecutar(self):
        try:
            if not self.OldImage:
                respuestas = self.crear(self.NewImage)
            elif self.cambios:
                respuestas = self.modificar(self.cambios)
            return respuestas
        except Exception as err:
            err.add_note("Ocurrió un problema ejecutando la acción sobre la"
                         "colección")
            raise

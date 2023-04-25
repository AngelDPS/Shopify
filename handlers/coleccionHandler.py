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
        try:
            self.conexion = ConexionShopify(evento.config['shopify'])
        except Exception:
            self.error = True
            raise

    def request(self, operacion: str, variables: dict = None) -> dict:
        self.logger.debug(f'{variables = }')
        respuesta = (self.conexion.enviarConsulta(
            gqlrequests.coleccion,
            variables=variables,
            operacion=operacion))
        respuesta = respuesta[list(respuesta)[0]]
        self.logger.debug(f'{respuesta = }')
        if respuesta.get("userErrors"):
            msg = ("No fue posible realizar la operación:\n"
                   f"{respuesta['userErrors']}")
            self.logger.exception(msg)
            raise RuntimeError(msg)
        return respuesta

    def publicar(self, id: str) -> dict:
        try:
            publicationIds = self.conexion.enviarConsulta(
                gqlrequests.misc, operacion="obtenerPublicaciones"
            )['publications']['nodes']
            respuesta = self.conexion.enviarConsulta(
                gqlrequests.misc,
                operacion='publicar',
                variables={
                    'id': id,
                    'input': [{"publicationId": i["id"]}
                              for i in publicationIds]
                }
            )
            self.logger.info("Publicación exitosa de la coleccion.")
            return respuesta
        except Exception:
            self.logger.exception("No se pudo publicar la colección")
            raise

    def crear(self, input: Mlinea, **kwargs) -> dict:
        self.logger.info("Creando colección a partir de línea.")
        try:
            respuesta = self.request(
                "crearColeccion",
                variables={
                    'input': (McollectionInput.parse_obj(input)
                              .dict(exclude_none=True))
                }
            )
            self.publicar(respuesta["collection"]["id"])
            self.actualizarBD(input.codigoCompania, input.co_lin,
                              respuesta["collection"]["id"])
            self.logger.info("Colección creada exitosamente.")
            return respuesta
        except Exception:
            self.logger.exception("No fue posible crear la colección")
            raise

    def modificar(self, input: Mlinea) -> dict:
        try:
            shopifyInput = McollectionInput.parse_obj(
                input.dict(by_alias=True, exclude_none=True)
                )
            shopifyInput.id = self.obtenerGid(self.OldImage.codigoCompania,
                                              self.OldImage.co_lin)
            respuesta = self.request(
                "modificarColeccion",
                variables={'input': shopifyInput.dict(exclude_none=True)},
            )
            self.logger.info("La colección fue modificada exitosamente.")
            return respuesta
        except Exception:
            self.logger.exception("No fue posible modificar la colección.")
            raise

    def _ocultar(self, publicationIds: list[str]) -> dict:
        try:
            respuesta = self.conexion.enviarConsulta(
                gqlrequests.misc,
                operacion='ocultar',
                variables={
                    'id': self.ID,
                    'input': [{"publicationId": i} for i in publicationIds]
                }
            )
            self.logger.info("Ocultada exitosa.")
            return respuesta
        except Exception:
            self.logger.exception("No se pudo ocultar")
            raise

    def ejecutar(self):
        if not self.OldImage:
            self.respuesta = self.crear(self.NewImage)
        elif self.cambios:
            self.respuesta = self.modificar(self.cambios)

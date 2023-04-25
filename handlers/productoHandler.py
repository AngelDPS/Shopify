from logging import getLogger
from models.producto import (
    MproductInput,
    MproductVariantInput,
    MinventoryLevelInput
)
from models.evento import Marticulo
from handlers.coleccionHandler import Coleccion
from libs.conexion import ConexionShopify
from libs import gqlrequests
from json import load, dump
from os import rename


class Producto:

    def actualizarBD(self, codigoCompania: str, co_art: str, gid: str):
        DBpath = f'DB/{codigoCompania}.json'
        DBpath_temp = DBpath + '.temp'
        with open(DBpath) as DBfile, open(DBpath_temp, 'w') as DBtemp:
            try:
                DB = load(DBfile)
                DB.setdefault('gids', {}).setdefault('articulos', {})
                DB['gids']['articulos'][co_art] = gid
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
    def obtenerGidTienda(codigoCompania: str, codigoTienda: str) -> str:
        DBpath = f'DB/{codigoCompania}.json'
        with open(DBpath) as DBfile:
            return load(DBfile)['gids']['tiendas'][codigoTienda]

    @staticmethod
    def obtenerGid(codigoCompania: str, co_art: str) -> str:
        DBpath = f'DB/{codigoCompania}.json'
        with open(DBpath) as DBfile:
            return load(DBfile)['gids']['articulos'][co_art]

    @staticmethod
    def obtenerCampoPrecio(codigoCompania: str) -> str:
        DBpath = f'DB/{codigoCompania}.json'
        with open(DBpath) as DBfile:
            return load(DBfile)['config']['precio']

    def __init__(self, evento):
        self.logger = getLogger("Shopify.Producto")
        self.NewImage = evento.NewImage
        self.OldImage = evento.OldImage
        self.cambios = evento.cambios
        try:
            self.conexion = ConexionShopify(evento.config['shopify'])
        except Exception:
            raise

    def request(self, operacion: str, variables: dict = None) -> dict:
        self.logger.debug(f'{variables = }')
        respuesta = (self.conexion.enviarConsulta(
            gqlrequests.producto,
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

    def obtenerGidVariante(self, GID: str) -> str:
        return self.request(
            "consultarGidVariante",
            variables={"id": GID}
        )["variants"]["nodes"][0]["id"]

    def obtenerGidInventario(self, GID: str) -> str:
        return self.request(
            "consultarGidInventario",
            variables={"id": GID}
        )["variants"]["nodes"][0]["inventoryItem"]["id"]

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
            self.logger.info("Publicación exitosa del producto.")
            return respuesta
        except Exception:
            self.logger.exception("No se pudo publicar el producto.")
            raise

    def crear(self, input: Marticulo) -> dict:
        self.logger.info("Creando producto a partir de artículo.")
        try:
            inventory = [MinventoryLevelInput(
                availableQuantity=input.stock_act,
                locationId=self.obtenerGidTienda(input.codigoCompania,
                                                 input.codigoTienda)
            )]
            variantInput = MproductVariantInput(
                **input.dict(by_alias=True,
                             exclude_none=True),
                inventoryQuantities=inventory)
            variantInput.price = getattr(input,
                                         self.obtenerCampoPrecio(
                                             input.codigoCompania)
                                         )
            productInput = MproductInput(
                **input.dict(by_alias=True,
                             exclude_none=True),
                status=("ACTIVE"
                        if input.habilitado
                        else "ARCHIVED"),
                variants=[variantInput],
                collectionsToJoin=[Coleccion.obtenerGid(
                    input.codigoCompania, input.co_lin)])
            respuesta = self.request(
                "crearProducto",
                variables={'input': productInput.dict(exclude_none=True)}
            )
            self.publicar(respuesta['product']['id'])
            self.actualizarBD(
                input.codigoCompania,
                input.co_art,
                respuesta['product']['id']
            )
            return respuesta
        except Exception:
            self.logger.exception("No fue posible crear el producto.")
            raise

    def ajustarInventario(self, gid: str, delta: int, name: str,
                          reason: str) -> dict:
        respuesta = self.request(
            "ajustarInventarios",
            variables={
                "delta": delta,
                "name": name,
                "reason": reason,
                "inventoryItemId": self.obtenerGidInventario(gid),
                "locationId": self.obtenerGidTienda(
                    self.OldImage.codigoCompania,
                    self.OldImage.codigoTienda
                )
            }
        )
        return respuesta

    def modificar(self, input: Marticulo) -> dict:
        try:
            self.logger.info("Actualizando producto.")
            variantInput = MproductVariantInput(
                **input.dict(by_alias=True, exclude_none=True))
            variantInput.price = getattr(
                input, self.obtenerCampoPrecio(self.OldImage.codigoCompania)
            )
            status = {
                None: None,
                True: "ACTIVE",
                False: "ARCHIVED"
            }[input.habilitado]
            productInput = MproductInput(
                **input.dict(by_alias=True, exclude_none=True),
                status=status)
            gid = self.obtenerGid(self.OldImage.codigoCompania,
                                  self.OldImage.co_art)
            if input.stock_act:
                delta = input.stock_act - self.OldImage.stock_act
                reason = "restock" if delta > 0 else "shrinkage"
                self.ajustarInventario(gid, delta, "available", reason)
            if input.stock_com:
                delta = input.stock_com - self.OldImage.stock_com
                reason = ("reservation_created" if delta > 0
                          else "reservation_deleted")
                self.ajustarInventario(gid, delta, "reserved", reason)
            if variantInput.dict(exclude_none=True):
                variantInput.id = self.obtenerGidVariante(gid)
                self.request(
                    'modificarVarianteProducto',
                    variables={'input': variantInput.dict(exclude_none=True)}
                )
            if productInput.dict(exclude_none=True):
                productInput.id = gid
                self.request(
                    "modificarProducto",
                    variables={'input': productInput.dict(exclude_none=True)}
                )
        except Exception:
            raise

    def ejecutar(self):
        if not self.OldImage:
            self.crear(self.NewImage)
        elif self.cambios:
            self.modificar(self.cambios)

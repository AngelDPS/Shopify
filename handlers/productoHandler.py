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

    # TODO: Función para actualizar BD
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
        """Función para obtener el GID asociado a codigoTienda.

        Args:
            codigoCompania (str): _description_
            codigoTienda (str): _description_

        Returns:
            str: _description_
        """
        DBpath = f'DB/{codigoCompania}.json'
        with open(DBpath) as DBfile:
            return load(DBfile)['gids']['tiendas'][codigoTienda]

    @staticmethod
    def obtenerGid(codigoCompania: str, co_art: str) -> str:
        """Función para obtener GID del producto
        NOTA:
          Se puede obtener el GID en el evento.

        Args:
            codigoCompania (str): _description_
            co_art (str): _description_

        Returns:
            str: _description_
        """
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
        self.conexion = ConexionShopify(evento.config['shopify'])
        # TODO: Información de configuración
        # "shopify": {
        # "tienda": "generico2022-8056",
        # "access_token": "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"
        # },

    def request(self, operacion: str, variables: dict = None) -> dict:
        """Funcion que realiza operaciones al servidor GraphQL de la tienda
        de Shopify. Las operaciones son seleccionadas de una lista predefinida
        en 'gqlrequests.producto'

        Args:
            operacion (str): Nombre de la operación a usar, definida en
            'gqlrequests.producto'
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
            gqlrequests.producto,
            variables=variables,
            operacion=operacion))
        try:
            if respuesta[list(respuesta)[0]].get("userErrors"):
                msg = ("No fue posible realizar la operación:\n"
                       f"{respuesta['userErrors']}")
                self.logger.exception(msg)
                raise RuntimeError(msg)
            return respuesta
        except AttributeError:
            self.logger.exception("Consulta inexitosa, GID no existe.")

    def obtenerGidVariante(self, gid: str) -> str:
        """Consulta Shopify por el GID de la única variante de producto
        asociada al GID de producto.

        Args:
            gid (str): Shopify Global ID del producto a consultar.

        Returns:
            str: Shopify Global ID de la variante del producto.
        """
        return self.request(
            "consultarGidVariante",
            variables={"id": gid}
        )["product"]["variants"]["nodes"][0]["id"]

    def obtenerGidInventario(self, gid: str) -> str:
        """Consulta Shopify por el GID de ítem de inventario de la única
        variante de producto asociada al GID de producto.

        Args:
            gid (str): Shopify Global ID del producto a consultar.

        Returns:
            str: Shopify Global ID del ítem de inventario.
        """
        return self.request(
            "consultarGidInventario",
            variables={"id": gid}
        )["product"]["variants"]["nodes"][0]["inventoryItem"]["id"]

    def publicar(self, gid: str) -> dict:
        """Publica el artículo en la tienda virtual y punto de venta de
        Shopify.

        Args:
            gid (str): GID de Shopify para el producto.

        Returns:
            dict: Json deserealizado con la respuesta obtenida.
        """
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
            self.logger.info("Publicación exitosa del producto.")
            return respuesta
        except Exception as err:
            self.logger.exception("No se pudo publicar el producto.")
            err.add_note("Error/es encontrado publicando el producto.")
            raise

    def crear(self, input: Marticulo) -> list[dict]:
        """Función dedicada a crear un producto en Shopify dada
        la información de un evento de artículo INSERT

        Args:
            input (Marticulo): Información deserealizada de DynamoDB con
            el artículo a crear

        Returns:
            list[dict]: Lista con las respuestas de las operaciones de crear y
            publicar el producto en Shopify.
        """
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
            # TODO: Pendiente obtener configuración de la nube
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
            respuestas = [self.request(
                "crearProducto",
                variables={'input': productInput.dict(exclude_none=True)}
            )]
            self.publicar(respuestas[0]['productCreate']['product']['id'])
            self.actualizarBD(
                input.codigoCompania,
                input.co_art,
                respuestas[0]['productCreate']['product']['id']
            )
            return respuestas
        except Exception as err:
            self.logger.exception("No fue posible crear el producto.")
            err.add_note("Ocurrieron problemas creando el producto.")
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
            variantInput = MproductVariantInput.parse_obj(
                input.dict(by_alias=True))
            # TODO: Pendiente obtener configuración de la nube
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
            respuestas = []
            if input.stock_act:
                delta = input.stock_act - self.OldImage.stock_act
                reason = "restock" if delta > 0 else "shrinkage"
                respuestas.append(
                    self.ajustarInventario(gid, delta, "available", reason)
                )
            if input.stock_com:
                delta = input.stock_com - self.OldImage.stock_com
                reason = ("reservation_created" if delta > 0
                          else "reservation_deleted")
                respuestas.append(
                    self.ajustarInventario(gid, delta, "reserved", reason)
                )
            if variantInput.dict(exclude_none=True):
                variantInput.id = self.obtenerGidVariante(gid)
                respuestas.append(self.request(
                    'modificarVarianteProducto',
                    variables={'input': variantInput.dict(exclude_none=True)}
                ))
            if productInput.dict(exclude_none=True):
                productInput.id = gid
                respuestas.append(self.request(
                    "modificarProducto",
                    variables={'input': productInput.dict(exclude_none=True)}
                ))
            return respuestas
        except Exception as err:
            self.logger.exception("No fue posible modificar el producto.")
            err.add_note("Ocurrieron problemas modificando el producto")
            raise

    def ejecutar(self):
        try:
            if not self.OldImage:
                respuestas = self.crear(self.NewImage)
            elif self.cambios:
                respuestas = self.modificar(self.cambios)
            return respuestas
        except Exception as err:
            err.add_note("Ocurrió un problema ejecutando la acción sobre el"
                         "producto.")

from logging import getLogger
from shopify.models.producto import (
    MproductInput,
    MproductVariantInput,
    MinventoryLevelInput
)
from shopify.models.evento import (
    Marticulo,
    Mlinea
)
from shopify.handlers.coleccionHandler import ColeccionHandler
from os import environ
import dynamodb
import shopify.conexion as conexion

logger = getLogger("shopify.productoHandler")


class ProductoHandler:

    # TODO: Función para actualizar BD
    def actualizarGidBD(self):
        logger.debug(f"GID de artículo: {self.NewImage.shopifyGID}")
        dynamodb.actualizarGidArticulo(
            PK=self.NewImage.PK,
            SK=self.NewImage.SK,
            GID=self.NewImage.shopifyGID
        )

    @staticmethod
    def obtenerCampoPrecio() -> str:
        try:
            return environ['precio']
        except KeyError:
            logger.exception("No se encontró la variable de ambiente 'precio' "
                             "con el campo de precio que deben usar los "
                             "articulos.")
            raise

    def obtenerGidTienda(self, use_old: bool = False) -> str:
        """Función para obtener el GID asociado a codigoTienda.

        Args:
            use_old (bool): Booleano usado para indicar si se utiliza
            OldImage para extraer el codigo de tienda del artículo

        Returns:
            str: El GID de shopify asociado al código de tienda del artículo.
        """
        codigoTienda = (self.NewImage.codigoTienda if not use_old
                        else self.OldImage.codigoTienda)
        try:
            tienda = dynamodb.obtenerTienda(
                codigoCompania=self.NewImage.codigoCompania,
                codigoTienda=codigoTienda
            )
            return tienda['shopifyGID']['sucursal']
        except KeyError:
            pass
        try:
            logger.warning("No se encontró el GID de la tienda en la base "
                           "de datos. Se procederá a consultar el GID a "
                           "Shopify y a guardar el resultado obtenido.")
            tienda.setdefault('shopifyGID', {})
            tienda['shopifyGID']['sucursal'] = conexion.obtenerGidTienda(
                tienda['nombre']
            )
            dynamodb.actualizarGidTienda(
                codigoCompania=self.NewImage.codigoCompania,
                codigoTienda=codigoTienda,
                GID=tienda['shopifyGID']['sucursal']
            )
            return tienda['shopifyGID']['sucursal']
        except Exception:
            logger.exception("No se pudo obtener el GID de la tienda.")
            raise

    def obtenerGidColeccion(self, use_old: bool = False) -> str:
        codigoTienda = (self.NewImage.codigoTienda if not use_old
                        else self.OldImage.codigoTienda)
        co_lin = (self.NewImage.co_lin if not use_old
                  else self.OldImage.co_lin)
        try:
            linea = dynamodb.obtenerLinea(
                codigoCompania=self.NewImage.codigoCompania,
                codigoTienda=codigoTienda,
                co_lin=co_lin
            )
            return linea['shopifyGID']
        except KeyError:
            pass
        try:
            logger.warning("No se encontró el GID de la linea en la base "
                           "de datos. Se procederá a consultar el GID a "
                           "Shopify y a guardar el resultado obtenido.")
            linea = Mlinea.parse_obj(linea)
            coleccion = ColeccionHandler(linea)
            coleccion.NewImage.shopifyGID = (
                conexion.obtenerGidColeccion(linea.nombre)
            )
            coleccion.actualizarGidBD()
            return coleccion.NewImage.shopifyGID
        except IndexError:
            pass
        try:
            coleccion.crear()
            return coleccion.NewImage.shopifyGID
        except Exception:
            logger.exception("No se pudo obtener el GID de la línea.")
            raise

    def obtenerGidPublicaciones(self, use_old: bool = False) -> str:
        codigoTienda = (self.NewImage.codigoTienda if not use_old
                        else self.OldImage.codigoTienda)
        try:
            tienda = dynamodb.obtenerTienda(
                codigoCompania=self.NewImage.codigoCompania,
                codigoTienda=codigoTienda
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
                conexion.obtenerGidPublicaciones()
            )
            dynamodb.actualizarGidPublicacionesTienda(
                codigoCompania=self.NewImage.codigoCompania,
                codigoTienda=codigoTienda,
                pubIDs=tienda['shopifyGID']['publicaciones']
            )
            return tienda['shopifyGID']['publicaciones']
        except Exception:
            logger.exception("Error al obtener los GIDs de los canales de "
                             "publicación.")
            raise

    def __init__(self, NewImage: Marticulo, OldImage: Marticulo = None,
                 cambios: Marticulo = None):
        self.NewImage = NewImage
        self.OldImage = OldImage
        self.cambios = cambios or Marticulo()
        self.usar_precio = self.obtenerCampoPrecio()
        preciosIgnorar = ['prec_vta1', 'prec_vta2', 'prec_vta3']
        preciosIgnorar.remove(self.usar_precio)
        [setattr(self.cambios, prec, None) for prec in preciosIgnorar]
        self.cambios.entity = None

    def publicar(self):
        """Publica el artículo en la tienda virtual y punto de venta de
        Shopify.
        """
        conexion.publicarRecurso(
            GID=self.NewImage.shopifyGID['producto'],
            pubIDs=self.obtenerGidPublicaciones()
        )

    def crear(self) -> list[dict]:
        """Función dedicada a crear un producto en Shopify dada
        la información de un evento de artículo INSERT

        Returns:
            list[dict]: Lista con las respuestas de las operaciones de crear y
            publicar el producto en Shopify.
        """
        logger.info("Creando producto a partir de artículo.")
        try:
            inventory = [MinventoryLevelInput(
                availableQuantity=(self.NewImage.stock_act
                                   - self.NewImage.stock_com),
                locationId=self.obtenerGidTienda()
            )]
            variantInput = MproductVariantInput(
                **self.NewImage.dict(by_alias=True,
                                     exclude_none=True),
                inventoryQuantities=inventory)
            variantInput.price = getattr(self.NewImage,
                                         self.usar_precio)
            productInput = MproductInput(
                **self.NewImage.dict(by_alias=True,
                                     exclude_none=True),
                status=("ACTIVE"
                        if self.NewImage.habilitado
                        else "ARCHIVED"),
                variants=[variantInput],
                collectionsToJoin=[self.obtenerGidColeccion()])
            self.NewImage.shopifyGID = conexion.crearProducto(productInput)
            self.publicar()
            self.actualizarGidBD()
            return ["Producto creado!"]
        except Exception:
            logger.exception("No fue posible crear el producto.")
            raise

    def _modificarInventario(self) -> str:
        try:
            delta_act = (self.cambios.stock_act - self.OldImage.stock_act
                         if self.cambios.stock_act else 0)
            delta_com = (self.cambios.stock_com - self.OldImage.stock_com
                         if self.cambios.stock_com else 0)
            delta = delta_act - delta_com
            if delta != 0:
                conexion.modificarInventario(
                    delta,
                    invId=(
                        self.OldImage.shopifyGID['variante']['inventario']
                    ),
                    locId=self.obtenerGidTienda(use_old=True)
                )
                return "Cambio de inventario"
            else:
                logger.info("La información suministrada no produjo cambios de"
                            " inventario.")
                return "Inventario no actualizado."
        except Exception:
            logger.exception("Se encontró un problema actualizando el "
                             "inventario del producto.")
            raise

    def _modificarVariante(self) -> str:
        try:
            variantInput = MproductVariantInput.parse_obj(
                self.cambios.dict(exclude_none=True, by_alias=True))
            # variantInput.price = getattr(cambios,
            #                             self.usar_precio)
            if variantInput.dict(exclude_none=True, exclude_unset=True):
                variantInput.id = self.OldImage.shopifyGID["variante"]["id"]
                conexion.modificarVarianteProducto(variantInput)
                return "Actualización de variante."
            else:
                logger.info("La información suministrada no produjo cambios a"
                            "la variante del producto.")
                return "Variante no actualizada."
        except Exception:
            logger.exception("Se encontró un problema actualizando la variante"
                             " del producto.")
            raise

    def _modificarProducto(self) -> str:
        try:
            status = {
                None: None,
                True: "ACTIVE",
                False: "ARCHIVED"
            }[self.cambios.habilitado]
            productInput = MproductInput(
                **self.cambios.dict(by_alias=True, exclude_none=True),
                status=status
            )
            if self.cambios.co_lin:
                productInput.collectionsToJoin = [self.obtenerGidColeccion()]
                productInput.collectionsToLeave = [
                    self.obtenerGidColeccion(use_old=True)
                ]
            if productInput.dict(exclude_none=True, exclude_unset=True):
                productInput.id = self.OldImage.shopifyGID["producto"]
                conexion.modificarProducto(productInput)
                return "Actualización de producto"
            else:
                logger.info("La información suministrada no produjo cambios al"
                            " producto.")
                return "Producto no actualizado."
        except Exception:
            logger.exception("Se encontró un problema actualizando el "
                             "producto.")
            raise

    def modificar(self) -> dict:
        try:
            respuestas = []
            respuestas.append(self._modificarInventario())
            respuestas.append(self._modificarVariante())
            respuestas.append(self._modificarProducto())
            return respuestas
        except Exception:
            logger.exception("No fue posible modificar el producto.")
            raise

    def ejecutar(self):
        try:
            if not self.OldImage:
                respuesta = self.crear()
            elif self.cambios.dict(exclude_none=True, exclude_unset=True):
                respuesta = self.modificar()
            else:
                logger.info("Los cambios encontrados no ameritan "
                            "actualizaciones en Shopify.")
                respuesta = "No se realizaron acciones."
            return respuesta
        except Exception:
            logger.exception("Ocurrió un problema ejecutando la acción sobre "
                             "el producto.")
            raise

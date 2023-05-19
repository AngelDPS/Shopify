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
import shopify.libs.dynamodb as dynamodb
import shopify.conexion as conexion

logger = getLogger("shopify.productoHandler")


class ProductoHandler:

    # TODO: Función para actualizar BD
    def actualizarGidBD(self):
        """Actualiza el GID de Shopify para el producto usando la información
        guardada en la instancia.
        """
        logger.debug(f"GID de artículo: {self.NewImage.shopifyGID}")
        dynamodb.actualizarGidArticulo(
            PK=self.NewImage.PK,
            SK=self.NewImage.SK,
            GID=self.NewImage.shopifyGID
        )

    @staticmethod
    def obtenerCampoPrecio() -> str:
        """Lee el campo de precio a usar para el artículo.

        Returns:
            str: Campo de precio a usar.
        """
        try:
            # TODO: Aquí se obtiene el parámetro de configuración para el
            # campo del precio.
            return environ['precio']
        except KeyError:
            logger.exception("No se encontró la variable de ambiente 'precio' "
                             "con el campo de precio que deben usar los "
                             "articulos.")
            raise

    def obtenerGidTienda(self, use_old: bool = False) -> str:
        """Función para obtener el GID asociado a la tienda en la base de datos
        especificada por el codigoTienda guardado en la instancia.

        Args:
            use_old (bool): Booleano usado para indicar si se utiliza
            OldImage para extraer el codigo de tienda del artículo

        Raises:
            ValueError: En caso que el código de tienda no corresponda a ningún
            registro de tienda en la base de datos.

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
        except UnboundLocalError:
            raise ValueError(f"El código de tienda '{codigoTienda}' no parece "
                             "existir en la base de datos.")
        except Exception:
            logger.exception("No se pudo obtener el GID de la tienda.")
            raise

    def obtenerGidColeccion(self, use_old: bool = False) -> str:
        """Función para obtener el GID asociado a la línea en la base de datos
        especificada por el co_lin y codigoTienda guardados en la instancia.

        Args:
            use_old (bool): Booleano usado para indicar si se utiliza
            OldImage para extraer el codigoTienda y co_lin del artículo

        Raises:
            ValueError: En caso que el código de línea no corresponda a ningún
            registro de línea en la base de datos.

        Returns:
            str: El GID de shopify asociado al código de línea del artículo.
        """
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
        except UnboundLocalError:
            logger.error(f"El código de línea '{co_lin}' no parece existir"
                         " en la base de datos para la tienda "
                         f"{codigoTienda}. No se harán cambios con la "
                         "colección asociada en Shopify.")
            return "gid://shopify/Collection/0"
        try:
            coleccion.crear()
            return coleccion.NewImage.shopifyGID
        except Exception:
            logger.exception("No se pudo obtener el GID de la línea.")
            raise

    def obtenerGidPublicaciones(self, use_old: bool = False) -> str:
        """Función para obtener el GID de los canales de publicación
        asociados a la tienda en la base de datos
        especificada por el codigoTienda guardado en la instancia.

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
        """Constructor de la clase

        Args:
            NewImage (Marticulo): Imagen de la base de datos para artículos
            con el artículo a crear (para INSERT) o con la data actualizada
            (para MODIFY).
            OldImage (Marticulo, optional): En caso de MODIFY, la imagen
            previa a las actualizaciones. Defaults to None.
            cambios (Marticulo, optional): En caso de MODIFY, los cambios
            encontrados en los campos entre la imagen nueva y vieja.
            Defaults to None.
        """
        self.NewImage = NewImage
        self.OldImage = OldImage or Marticulo()
        self.cambios = cambios or Marticulo()
        # TODO: Aquí se usa el parámetro de configuración para el campo de
        # precio.
        self.usar_precio = self.obtenerCampoPrecio()
        preciosIgnorar = ['prec_vta1', 'prec_vta2', 'prec_vta3']
        preciosIgnorar.remove(self.usar_precio)
        for prec in preciosIgnorar:
            setattr(self.NewImage, prec, None)
            setattr(self.OldImage, prec, None)
            setattr(self.cambios, prec, None)
        for image in [self.NewImage, self.OldImage, self.cambios]:
            image.habilitado = {
                None: None,
                True: "ACTIVE",
                False: "ARCHIVED"
            }[image.habilitado]

    def publicar(self):
        """Publica el artículo en la tienda virtual y punto de venta de
        Shopify.
        """
        conexion.publicarRecurso(
            GID=self.NewImage.shopifyGID['producto'],
            pubIDs=self.obtenerGidPublicaciones()
        )

    def crear(self) -> list[str]:
        """Función dedicada a crear un producto en Shopify dada
        la información de un evento de artículo INSERT

        Returns:
            str: Respuesta dada una operación exitosa.
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
            productInput = MproductInput(
                **self.NewImage.dict(by_alias=True,
                                     exclude_none=True),
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
        """Detecta cambios de inventario que ameriten actualización en Shopify
        y ejecuto la solicitud en Shopify.

        Returns:
            str: Cadena con información de la operación.
        """
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
        """Si detecta cambios que afecten a la variante, ejecuta la solicitud
        de actualización a Shopify.

        Returns:
            str: Cadena con información de la operación
        """
        try:
            variantInput = MproductVariantInput.parse_obj(
                self.cambios.dict(exclude_none=True, by_alias=True))
            if variantInput.dict(exclude_none=True, exclude_unset=True):
                variantInput.id = self.OldImage.shopifyGID["variante"]["id"]
                conexion.modificarVarianteProducto(variantInput)
                return "Actualización de variante."
            else:
                logger.info("La información suministrada no produjo cambios a"
                            " la variante del producto.")
                return "Variante no actualizada."
        except Exception:
            logger.exception("Se encontró un problema actualizando la variante"
                             " del producto.")
            raise

    def _modificarProducto(self) -> str:
        """Si detecta cambios que afecten al producto general, ejecuta la
        solicitud de actualización a Shopify.

        Returns:
            str: Cadena con información de la operación
        """
        try:
            productInput = MproductInput.parse_obj(
                self.cambios.dict(by_alias=True, exclude_none=True)
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

    def modificar(self) -> list[str]:
        """Ejecuta todas los métodos de modificación para los elementos del
        producto y recolecta las respuestas de cada una.

        Returns:
            list[str]: Conjunto de las respuestas de los métodos de
            modificación.
        """
        try:
            respuestas = []
            respuestas.append(self._modificarInventario())
            respuestas.append(self._modificarVariante())
            respuestas.append(self._modificarProducto())
            return respuestas
        except Exception:
            logger.exception("No fue posible modificar el producto.")
            raise

    def ejecutar(self) -> list[str]:
        """Ejecuta la acción requerida por el evento procesado en la instancia.

        Returns:
            list[str]: Conjunto de resultados obtenidos por las operaciones
            ejecutadas.
        """
        try:
            if not self.OldImage.dict(exclude_none=True, exclude_unset=True):
                respuesta = self.crear()
            elif self.cambios.dict(exclude_none=True, exclude_unset=True):
                if self.NewImage.shopifyGID:
                    respuesta = self.modificar()
                else:
                    logger.warning("En el evento no se encontró el GID de "
                                   "Shopify proveniente de la base de datos. "
                                   "Se asume que el producto correspondiente "
                                   "no existe en Shopify. Se creará un "
                                   "producto nuevo con la data actualizada.")
                    respuesta = self.crear()
            else:
                logger.info("Los cambios encontrados no ameritan "
                            "actualizaciones en Shopify.")
                respuesta = ["No se realizaron acciones."]
            return respuesta
        except Exception:
            logger.exception("Ocurrió un problema ejecutando la acción sobre "
                             "el producto.")
            raise

from logging import getLogger
from models.producto import (
    MproductInput,
    MproductVariantInput,
    MinventoryLevelInput
)
from models.misc import McreateMediaInput
from models.evento import Marticulo
from handlers.coleccionHandler import (
    ColeccionHandler,
    obtenerGidColeccion
)
from handlers.sucursalHandler import obtenerGidTienda
from libs.dynamodb import (
    actualizarGidArticulo,
    obtenerTienda,
    actualizarGidTienda,
    obtenerLinea,
    actualizarGidPublicacionesTienda
)
from libs.util import get_parameter
from libs.conexion import (
    ClienteShopify,
    obtenerGidPublicaciones,
    publicarRecurso
)
from os import getenv
import boto3

logger = getLogger("shopify.productoHandler")
s3_client = boto3.client('s3', region_name=getenv("AWS_REGION"),
                         config=boto3.session.Config(signature_version='s3v4'))


def crearProducto(productInput: MproductInput,
                  mediaInput: list[McreateMediaInput],
                  client: ClienteShopify = None) -> str:
    try:
        client = client or ClienteShopify()
        respuesta = client.execute(
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
                        media(first:10) {
                            nodes {
                                ... on MediaImage {
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
            variables={'input': productInput.dict(exclude_none=True),
                       'media': [mInput.dict(exclude_none=True)
                                 for mInput in mediaInput]}
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
            },
            'imagenes': {
                imInput.fname: imNodes['id']
                for imInput, imNodes in zip(
                    mediaInput,
                    respuesta['productCreate']['product']['media']['nodes']
                )
            }
        }
        return shopifyGID
    except (KeyError, IndexError):
        logger.exception("Formato inesperado de respuesta para la creación "
                         "del producto.")
        raise


def modificarInventario(delta: int, invId: str, locId: str,
                        client: ClienteShopify = None):
    try:
        reason = "restock" if delta > 0 else "shrinkage"
        client = client or ClienteShopify()
        client.execute(
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


def modificarVarianteProducto(variantInput: MproductVariantInput,
                              client: ClienteShopify = None):
    try:
        client = client or ClienteShopify()
        client.execute(
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
            variables={'input': variantInput.dict(exclude_none=True,
                                                  exclude_unset=True)}
        )
        logger.info("Variante modificado exitosamente.")
    except Exception:
        logger.exception("Ocurrió un error al tratar de modificar la "
                         "variante del producto.")
        raise


def modificarProducto(productInput: MproductInput,
                      client: ClienteShopify = None):
    try:
        client = client or ClienteShopify()
        client.execute(
            """
            mutation modificarProducto($input: ProductInput!) {
                productUpdate(input: $input) {
                    userErrors {
                        message
                    }
                }
            }
            """,
            variables={'input': productInput.dict(exclude_none=True,
                                                  exclude_unset=True)}
        )
        logger.info("Producto modificado exitosamente.")
    except Exception:
        logger.exception("Ocurrió un error al tratar de modificar el "
                         "producto.")
        raise


def anexarImagenArticulo(productId: str, mediaInput: list[McreateMediaInput],
                         client: ClienteShopify = None):
    try:
        client = client or ClienteShopify()
        respuesta = client.execute(
            """
            mutation anexarImagen($productId: ID!,
                                  $media: [CreateMediaInput!]!) {
                productCreateMedia(productId: $productId, media: $media) {
                    media {
                        ... on MediaImage{
                            id
                        }
                    }
                    mediaUserErrors {
                        message
                    }
                }
            }
            """,
            variables={'productId': productId,
                       'media': [mInput.dict(exclude_none=True)
                                 for mInput in mediaInput]}
        )
        if respuesta['productCreateMedia']['mediaUserErrors']:
            msg = (f"{respuesta['productCreateMedia']['mediaUserErrors']}")
            logger.exception(msg)
            raise RuntimeError(msg)
        logger.info("Imágenes anexadas correctamente.")
    except Exception:
        logger.exception("Hubo un problema anexando las imágenes")
        raise
    try:
        shopifyGID = {
            'imagenes': {
                imInput.fname: imNodes['id']
                for imInput, imNodes in zip(
                    mediaInput,
                    respuesta['productCreateMedia']['media']
                )
            }
        }
        return shopifyGID
    except (KeyError, IndexError):
        logger.exception("Formato inesperado de respuesta para la creación "
                         "del producto.")
        raise


def eliminarImagenArticulo(productId: str, mediaIds: list[str],
                           client: ClienteShopify = None):
    try:
        client = client or ClienteShopify()
        respuesta = client.execute(
            """
            mutation removerImagen($productId: ID!, $mediaIds: [ID!]!) {
                productDeleteMedia(productId: $productId,
                                   mediaIds: $mediaIds) {
                    mediaUserErrors {
                        message
                        code
                    }
                }
            }
            """,
            variables={'productId': productId, 'mediaIds': mediaIds}
        )
        media_user_errors = respuesta['productDeleteMedia']['mediaUserErrors']
        if media_user_errors:
            for n, error in enumerate(media_user_errors):
                if error['code'] == 'MEDIA_DOES_NOT_EXIST':
                    logger.warning("Una de las imágenes eliminadas no se "
                                   "encontraba en Shopify.")
            logger.error(media_user_errors)
        else:
            logger.info("Imágenes eliminadas correctamente.")
    except Exception:
        logger.exception("Se encontraron problemas eliminando las imágenes.")
        raise


def generar_url(fname: str):
    try:
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': get_parameter("bucketname"),
                    'Key': f"imagenes/{fname}"},
            ExpiresIn=3600
        )
    except Exception:
        logger.exception(
            f"No se pudo generar el url para el archivo 'imagenes/{fname}'"
            f", guardado en el s3 bucket {get_parameter('bucketname')}")
        return None


def obtener_CreateMediaInputs(file_names: list[str]
                              ) -> list[McreateMediaInput]:
    mediaInputs = [
        McreateMediaInput(mediaContentType="IMAGE",
                          originalSource=generar_url(fname),
                          fname=fname)
        for fname in file_names
    ]
    mediaInputs = [mInput for mInput in mediaInputs
                   if mInput.originalSource is not None]
    if not mediaInputs:
        logger.warning("No se cargarán imágenes.")
    return mediaInputs


class ProductoHandler:

    def __init__(self, evento, client: ClienteShopify = None):
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
        self.eventName = evento.event_name
        campo_precio = get_parameter('SHOPIFY_PRECIO')
        for label in ['new_image', 'old_image']:
            setattr(self, label,
                    Marticulo.parse_obj(getattr(evento, label)))
            getattr(self, label).precio = getattr(evento, label)[campo_precio]
            getattr(self, label).habilitado = (
                getattr(self, label).habilitado.name
            )
        self.cambios = Marticulo.parse_obj(evento.cambios)
        self.client = client or ClienteShopify()
        self.session = None

    def actualizarGidBD(self):
        """Actualiza el GID de Shopify para el producto usando la información
        guardada en la instancia.
        """
        logger.debug(f"GID de artículo: {self.new_image.shopifyGID}")
        actualizarGidArticulo(
            PK=self.new_image.PK,
            SK=self.new_image.SK,
            GID=self.new_image.shopifyGID
        )

    def obtenerGidTienda(self, from_old: bool = False) -> str:
        """Función para obtener el GID asociado a la tienda en la base de datos
        especificada por el codigoTienda guardado en la instancia.

        Args:
            from_old (bool): Booleano usado para indicar si se utiliza
            OldImage para extraer el codigo de tienda del artículo

        Raises:
            ValueError: En caso que el código de tienda no corresponda a ningún
            registro de tienda en la base de datos.

        Returns:
            str: El GID de shopify asociado al código de tienda del artículo.
        """
        codigoTienda = (self.new_image.codigoTienda if not from_old
                        else self.old_image.codigoTienda)
        try:
            tienda = obtenerTienda(
                codigoCompania=self.new_image.codigoCompania,
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
            tienda['shopifyGID']['sucursal'] = obtenerGidTienda(
                tienda['nombre'],
                self.session or self.client
            )
            actualizarGidTienda(
                codigoCompania=self.new_image.codigoCompania,
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

    def obtenerGidColeccion(self, from_old: bool = False) -> str:
        """Función para obtener el GID asociado a la línea en la base de datos
        especificada por el co_lin y codigoTienda guardados en la instancia.

        Args:
            from_old (bool): Booleano usado para indicar si se utiliza
            OldImage para extraer el codigoTienda y co_lin del artículo

        Raises:
            ValueError: En caso que el código de línea no corresponda a ningún
            registro de línea en la base de datos.

        Returns:
            str: El GID de shopify asociado al código de línea del artículo.
        """
        codigoTienda = (self.new_image.codigoTienda if not from_old
                        else self.old_image.codigoTienda)
        co_lin = (self.new_image.co_lin if not from_old
                  else self.old_image.co_lin)
        try:
            linea = obtenerLinea(
                codigoCompania=self.new_image.codigoCompania,
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
            coleccion = ColeccionHandler.desde_linea(linea)
            coleccion.NewImage.shopifyGID = (
                obtenerGidColeccion(linea['nombre'],
                                    self.session or self.client)
            )
            coleccion.actualizarGidBD()
            return coleccion.NewImage.shopifyGID
        except IndexError:
            pass
        except UnboundLocalError:
            logger.wawrning(
                f"El código de línea '{co_lin}' no parece existir en la base "
                f"de datos para la tienda {codigoTienda}. No se harán cambios "
                "con la colección asociada en Shopify."
            )
            return "gid://shopify/Collection/0"
        try:
            coleccion.crear()
            return coleccion.NewImage.shopifyGID
        except Exception:
            logger.exception("No se pudo obtener el GID de la línea.")
            raise

    def obtenerGidPublicaciones(self, from_old: bool = False) -> str:
        """Función para obtener el GID de los canales de publicación
        asociados a la tienda en la base de datos
        especificada por el codigoTienda guardado en la instancia.

        Args:
            from_old (bool): Booleano usado para indicar si se utiliza
            OldImage para extraer el codigo de tienda del artículo

        Returns:
            str: El GID de shopify asociado al código de tienda del artículo.
        """
        codigoTienda = (self.new_image.codigoTienda if not from_old
                        else self.old_image.codigoTienda)
        try:
            tienda = obtenerTienda(
                codigoCompania=self.new_image.codigoCompania,
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
                obtenerGidPublicaciones(self.session or self.client)
            )
            actualizarGidPublicacionesTienda(
                codigoCompania=self.new_image.codigoCompania,
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
            GID=self.new_image.shopifyGID['producto'],
            pubIDs=self.obtenerGidPublicaciones(),
            client=self.session or self.client
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
                availableQuantity=(self.new_image.stock_act
                                   - self.new_image.stock_com),
                locationId=self.obtenerGidTienda()
            )]
            variantInput = MproductVariantInput(
                **self.new_image.dict(by_alias=True,
                                      exclude_none=True),
                inventoryQuantities=inventory)
            productInput = MproductInput(
                **self.new_image.dict(by_alias=True,
                                      exclude_none=True),
                variants=[variantInput],
                collectionsToJoin=[self.obtenerGidColeccion()]
            )
            mediaInput = obtener_CreateMediaInputs(self.new_image.imagen_url)
            self.new_image.shopifyGID = crearProducto(
                productInput, mediaInput,
                self.session or self.client
            )
            self.publicar()
            # TODO: Que sucede si se publica y falla la actualización en
            # Dynamo?
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
            delta_act = (self.cambios.stock_act - self.old_image.stock_act
                         if self.cambios.stock_act is not None else 0)
            delta_com = (self.cambios.stock_com - self.old_image.stock_com
                         if self.cambios.stock_com is not None else 0)
            delta = delta_act - delta_com
            if delta != 0:
                modificarInventario(
                    delta,
                    invId=(
                        self.old_image.shopifyGID['variante']['inventario']
                    ),
                    locId=self.obtenerGidTienda(from_old=True),
                    client=self.session or self.client
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
                self.cambios.dict(exclude_none=True, exclude_unset=True,
                                  by_alias=True))
            if variantInput.dict(exclude_none=True, exclude_unset=True):
                variantInput.id = self.old_image.shopifyGID["variante"]["id"]
                modificarVarianteProducto(variantInput,
                                          self.session or self.client)
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
                self.cambios.dict(by_alias=True, exclude_none=True,
                                  exclude_unset=True)
            )
            if self.cambios.co_lin is not None:
                productInput.collectionsToJoin = [self.obtenerGidColeccion()]
                productInput.collectionsToLeave = [
                    self.obtenerGidColeccion(from_old=True)
                ]
            if productInput.dict(exclude_none=True, exclude_unset=True):
                productInput.id = self.old_image.shopifyGID["producto"]
                modificarProducto(productInput,
                                  self.session or self.client)
                return "Actualización de producto"
            else:
                logger.info("La información suministrada no produjo cambios al"
                            " producto.")
                return "Producto no actualizado."
        except Exception:
            logger.exception("Se encontró un problema actualizando el "
                             "producto.")
            raise

    def _cambiosImagenes(self):
        try:
            urls_anexados = list(
                set(self.new_image.imagen_url) - set(self.old_image.imagen_url)
            )
            urls_removidos = list(
                set(self.old_image.imagen_url) - set(self.new_image.imagen_url)
            )
            msg = ""
            if urls_anexados:
                anexarMediaInput = obtener_CreateMediaInputs(urls_anexados)
                logger.debug(anexarMediaInput)
                if anexarMediaInput:
                    self.new_image.shopifyGID['imagenes'] |= (
                        anexarImagenArticulo(
                            self.old_image.shopifyGID["producto"],
                            anexarMediaInput,
                            self.session or self.client
                        )['imagenes']
                    )
                    msg += "Imágenes añadidas."
            if urls_removidos:
                logger.debug(urls_removidos)
                eliminarMediaIds = [
                    self.new_image.shopifyGID["imagenes"].pop(fname)
                    for fname in urls_removidos
                ]
                logger.debug(eliminarMediaIds)
                eliminarImagenArticulo(
                    self.new_image.shopifyGID["producto"],
                    eliminarMediaIds,
                    self.session or self.client
                )
                msg += "Imágenes removidas."
            if not (urls_anexados or urls_removidos):
                logger.info("La información suministrada no produjo cambios a "
                            "las imágenes")
                return "Imágenes no actualizadas."
            self.actualizarGidBD()
            return msg
        except Exception:
            logger.exception("Hubo problemas actualizando las imágenes.")
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
            respuestas.append(self._cambiosImagenes())
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
            with self.client as self.session:
                if self.eventName == "INSERT":
                    respuesta = self.crear()
                elif self.cambios.dict(exclude_none=True, exclude_unset=True):
                    if self.new_image.shopifyGID:
                        respuesta = self.modificar()
                    else:
                        logger.warning(
                            "En el evento no se encontró el GID de "
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

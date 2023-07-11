from models.producto import (
    MproductInput,
    MproductVariantInput,
    MinventoryLevelInput
)
from models.misc import McreateMediaInput
from models.evento import MArticuloShopify as MArticulo
from handlers.eventHandler import EventHandler
from handlers.coleccionHandler import (
    ColeccionHandler,
    shopify_obtener_id as obtener_coleccion_id
)
from handlers.sucursalHandler import (
    shopify_obtener_id as obtener_sucursal_id
)
from libs.dynamodb import (
    guardar_articulo_id,
    obtener_tienda,
    guardar_tienda_id,
    obtener_linea,
    guardar_publicaciones_id
)
from libs.util import get_parameter, ItemHandler
from libs.conexion import (
    ClienteShopify,
    obtener_publicaciones_id,
    publicar_recurso
)
from enum import Enum
import boto3
from aws_lambda_powertools import Logger

logger = Logger(child=True, service="shopify")


def shopify_crear_producto(productInput: MproductInput,
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
        shopify_id = {
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
        return shopify_id
    except (KeyError, IndexError):
        logger.exception("Formato inesperado de respuesta para la creación "
                         "del producto.")
        raise


def shopify_cambiar_inventario(delta: int, invId: str, locId: str,
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


def shopify_cambiar_variante(variantInput: MproductVariantInput,
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


def shopify_cambiar_producto(productInput: MproductInput,
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


def shopify_anexar_imagen(productId: str, mediaInput: list[McreateMediaInput],
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
        shopify_id = {
            'imagenes': {
                imInput.fname: imNodes['id']
                for imInput, imNodes in zip(
                    mediaInput,
                    respuesta['productCreateMedia']['media']
                )
            }
        }
        return shopify_id
    except (KeyError, IndexError):
        logger.exception("Formato inesperado de respuesta para la creación "
                         "del producto.")
        raise


def shopify_borrar_imagen(productId: str, mediaIds: list[str],
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
        s3_client = boto3.client(
            's3', region_name='us-east-2',
            config=boto3.session.Config(signature_version='s3v4')
        )
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


def generar_media_inputs(file_names: list[str]) -> list[McreateMediaInput]:
    media_inputs = [
        McreateMediaInput(mediaContentType="IMAGE",
                          originalSource=generar_url(fname),
                          fname=fname)
        for fname in file_names
    ]
    media_inputs = [m_input for m_input in media_inputs
                    if m_input.originalSource is not None]
    if not media_inputs:
        logger.warning("No se cargarán imágenes.")
    return media_inputs


class Habilitado(Enum):
    ARCHIVED = 0
    ACTIVE = 1


class ProductoHandler(ItemHandler):
    item = "producto"

    def __init__(self, evento: EventHandler, client: ClienteShopify = None):
        """Constructor de la clase

        Args:
            evento (EventHandler):
            client (ClienteShopify, optional): Defaults to None.
        """
        campo_precio = get_parameter('SHOPIFY_PRECIO')

        self.cambios = evento.cambios
        self.cambios.get('shopify_id', {}).pop('imagenes', None)
        self.cambios.get('shopify_id', {}).pop('variante', None)
        if campo_precio in self.cambios:
            self.cambios['precio'] = self.cambios[campo_precio]
        if 'habilitado' in self.cambios:
            self.cambios['habilitado'] = Habilitado(
                self.cambios['habilitado']
            ).name.upper()
        self.cambios = MArticulo.parse_obj(self.cambios)

        self.old_image = evento.old_image
        if self.old_image:
            self.old_image['precio'] = self.old_image.get(campo_precio)
            self.old_image['habilitado'] = Habilitado(
                self.old_image.get('habilitado', 0)
            ).name.upper()
        self.old_image = MArticulo.parse_obj(self.old_image)

        self.client = client or ClienteShopify()
        self.session = None

    def guardar_id_dynamo(self):
        """Actualiza el GID de Shopify para el producto usando la información
        guardada en la instancia.
        """
        logger.debug(f"GID del artículo: {self.old_image.shopify_id}")
        guardar_articulo_id(
            PK=self.old_image.PK or self.cambios.PK,
            SK=self.old_image.SK or self.cambios.SK,
            GID=self.old_image.shopify_id
        )

    def obtener_tienda_id(self) -> str:
        """Función para obtener el GID asociado a la tienda en la base de datos
        especificada por el codigoTienda guardado en la instancia.

        Raises:
            ValueError: En caso que el código de tienda no corresponda a ningún
            registro de tienda en la base de datos.

        Returns:
            str: El GID de shopify asociado al código de tienda del artículo.
        """
        codigo_tienda = (self.cambios.codigoTienda
                         or self.old_image.codigoTienda)
        codigo_compania = (self.cambios.codigoCompania
                           or self.old_image.codigoCompania)
        try:
            tienda = obtener_tienda(codigo_compania, codigo_tienda)
            return tienda['shopify_id']['sucursal']
        except KeyError:
            pass
        try:
            logger.warning("No se encontró el GID de la tienda en la base "
                           "de datos. Se procederá a consultar el GID a "
                           "Shopify y a guardar el resultado obtenido.")
            tienda.setdefault('shopify_id', {})
            tienda['shopify_id']['sucursal'] = obtener_sucursal_id(
                tienda['nombre'],
                self.session or self.client
            )
            guardar_tienda_id(codigo_compania, codigo_tienda,
                              GID=tienda['shopify_id']['sucursal'])
            return tienda['shopify_id']['sucursal']
        except UnboundLocalError:
            raise ValueError(f"El código de tienda '{codigo_tienda}' no parece"
                             " existir en la base de datos.")
        except Exception:
            logger.exception("No se pudo obtener el GID de la tienda.")
            raise

    def obtener_coleccion_id(self, use_old: bool = False) -> str:
        """Función para obtener el GID asociado a la línea en la base de datos
        especificada por el co_lin y codigoTienda guardados en la instancia.

        Raises:
            ValueError: En caso que el código de línea no corresponda a ningún
            registro de línea en la base de datos.

        Returns:
            str: El GID de shopify asociado al código de línea del artículo.
        """
        codigo_tienda = (self.cambios.codigoTienda
                         or self.old_image.codigoTienda)
        co_lin = (
            (self.cambios.co_lin or self.old_image.co_lin)
            if not use_old else self.old_image.co_lin
        )
        try:
            linea = obtener_linea(
                self.cambios.codigoCompania or self.old_image.codigoCompania,
                codigo_tienda,
                co_lin=co_lin
            )
            return linea['shopify_id']
        except KeyError:
            pass
        try:
            logger.warning("No se encontró el GID de la linea en la base "
                           "de datos. Se procederá a consultar el GID a "
                           "Shopify y a guardar el resultado obtenido.")
            coleccion = ColeccionHandler.desde_linea(
                linea,
                self.session or self.client
            )
            coleccion.old_image.shopify_id = (
                obtener_coleccion_id(linea['nombre'],
                                     self.session or self.client)
            )
            coleccion.guardar_id_dynamo()
            return coleccion.old_image.shopify_id
        except IndexError:
            pass
        except UnboundLocalError:
            logger.warning(
                f"El código de línea '{co_lin}' no parece existir en la base "
                f"de datos para la tienda {codigo_tienda}. No se harán "
                "cambios con la colección asociada en Shopify."
            )
            return "gid://shopify/Collection/0"
        try:
            coleccion.crear()
            return coleccion.old_image.shopify_id
        except Exception:
            logger.exception("No se pudo obtener el GID de la línea.")
            raise

    def obtener_publicaciones_id(self) -> str:
        """Función para obtener el GID de los canales de publicación
        asociados a la tienda en la base de datos
        especificada por el codigoTienda guardado en la instancia.

        Args:
            from_old (bool): Booleano usado para indicar si se utiliza
            OldImage para extraer el codigo de tienda del artículo

        Returns:
            str: El GID de shopify asociado al código de tienda del artículo.
        """
        codigo_tienda = (self.cambios.codigoTienda
                         or self.old_image.codigoTienda)
        codigo_compania = (self.cambios.codigoCompania
                           or self.old_image.codigoCompania)
        try:
            tienda = obtener_tienda(codigo_compania, codigo_tienda)
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
            guardar_publicaciones_id(codigo_compania, codigo_tienda,
                                     tienda['shopify_id']['publicaciones'])
            return tienda['shopify_id']['publicaciones']
        except Exception:
            logger.exception("Error al obtener los GIDs de los canales de "
                             "publicación.")
            raise

    def crear(self) -> list[str]:
        """Función dedicada a crear un producto en Shopify dada
        la información de un evento de artículo INSERT

        Returns:
            str: Respuesta dada una operación exitosa.
        """
        logger.info("Creando producto a partir de artículo.")
        try:
            inventory = [MinventoryLevelInput(
                availableQuantity=(self.cambios.stock_act
                                   - self.cambios.stock_com),
                locationId=self.obtener_tienda_id()
            )]
            variantInput = MproductVariantInput(
                **self.cambios.dict(by_alias=True, exclude_none=True),
                inventoryQuantities=inventory)
            productInput = MproductInput(
                **self.cambios.dict(by_alias=True, exclude_none=True),
                variants=[variantInput],
                collectionsToJoin=[self.obtener_coleccion_id()]
            )
            mediaInput = generar_media_inputs(self.cambios.imagen_url)
            self.old_image.shopify_id = shopify_crear_producto(
                productInput, mediaInput, self.session or self.client
            )
            # TODO: Que sucede si se publica y falla la actualización en
            # Dynamo?
            self.guardar_id_dynamo()
            return ["Producto creado!"]
        except Exception:
            logger.exception("No fue posible crear el producto.")
            raise

    def _publicar(self):
        """Publica el artículo en la tienda virtual y punto de venta de
        Shopify.
        """
        if self.cambios.shopify_id.get("producto"):
            publicar_recurso(
                GID=self.cambios.shopify_id['producto'],
                pubIDs=self.obtener_publicaciones_id(),
                client=self.session or self.client
            )
            return "Producto publicado!"
        else:
            return ""

    def _modificarInventario(self) -> str:
        """Detecta cambios de inventario que ameriten actualización en Shopify
        y ejecuto la solicitud en Shopify.

        Returns:
            str: Cadena con información de la operación.
        """
        try:
            delta = (
                (self.cambios.stock_act or self.old_image.stock_act
                 - self.old_image.stock_act)
                - (self.cambios.stock_com or self.old_image.stock_com
                   - self.old_image.stock_com)
            )
            if delta != 0:
                shopify_cambiar_inventario(
                    delta,
                    invId=(
                        self.old_image.shopify_id['variante']['inventario']
                    ),
                    locId=self.obtener_tienda_id(),
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
                self.cambios.dict(exclude_unset=True, by_alias=True))
            if variantInput.dict(exclude_unset=True):
                variantInput.id = self.old_image.shopify_id["variante"]["id"]
                shopify_cambiar_variante(variantInput,
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
                productInput.collectionsToJoin = [self.obtener_coleccion_id()]
                productInput.collectionsToLeave = [
                    self.obtener_coleccion_id(from_old=True)
                ]
            if productInput.dict(exclude_unset=True):
                productInput.id = self.old_image.shopify_id["producto"]
                shopify_cambiar_producto(productInput,
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
                set(self.cambios.imagen_url or self.old_image.imagen_url)
                - set(self.old_image.imagen_url)
            )
            urls_removidos = list(
                set(self.old_image.imagen_url)
                - set(self.cambios.imagen_url or self.old_image.imagen_url)
            )
            msg = ""
            if urls_anexados:
                anexarMediaInput = generar_media_inputs(urls_anexados)
                logger.debug(anexarMediaInput)
                if anexarMediaInput:
                    self.old_image.shopify_id['imagenes'] |= (
                        shopify_anexar_imagen(
                            self.old_image.shopify_id["producto"],
                            anexarMediaInput,
                            self.session or self.client
                        )['imagenes']
                    )
                    msg += "Imágenes añadidas."
            if urls_removidos:
                logger.debug(urls_removidos)
                eliminarMediaIds = [
                    self.old_image.shopify_id["imagenes"].pop(fname)
                    for fname in urls_removidos
                ]
                logger.debug(eliminarMediaIds)
                shopify_borrar_imagen(
                    self.old_image.shopify_id["producto"],
                    eliminarMediaIds,
                    self.session or self.client
                )
                msg += "Imágenes removidas."
            if not (urls_anexados or urls_removidos):
                logger.info("La información suministrada no produjo cambios a "
                            "las imágenes")
                return "Imágenes no actualizadas."
            self.guardar_id_dynamo()
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
        self.old_image.shopify_id = (self.cambios.shopify_id
                                     or self.old_image.shopify_id)
        try:
            respuestas = []
            respuestas.append(self._publicar())
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
                respuesta = super().ejecutar("Shopify",
                                             self.cambios.shopify_id
                                             or self.old_image.shopify_id)
                return respuesta
        except Exception:
            logger.exception("Ocurrió un problema ejecutando la acción sobre "
                             "el producto.")
            raise

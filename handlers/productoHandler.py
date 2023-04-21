from logging import getLogger
from handlers.shopifyObject import ShopifyObject
from models.producto import (
    MproductInput,
    MproductVariantInput,
    MinventoryLevelInput
)


class Producto(ShopifyObject):

    def __init__(self, evento):
        self.logger = getLogger("Shopify.Producto")
        self.establecerTipo(evento.data.NewImage.entity)

        try:
            self._establecerConexion(evento.config['shopify'])
            if not evento.data.OldImage:
                self.logger.info("Creando producto a partir de artículo.")
                inventory = [MinventoryLevelInput(
                    availableQuantity=evento.data.NewImage.stock_act,
                    locationId=(
                        evento.gids['tiendas']
                        [evento.data.NewImage.codigoTienda]
                    )
                )]
                variant = MproductVariantInput(
                    **evento.data.NewImage.dict(by_alias=True,
                                                exclude_none=True),
                    inventoryQuantities=inventory)
                variant.price = getattr(evento.data.NewImage,
                                        evento.config['precio'])
                productInput = MproductInput(
                    **evento.data.NewImage.dict(by_alias=True,
                                                exclude_none=True),
                    status=("ACTIVE"
                            if evento.data.NewImage.habilitado
                            else "ARCHIVED"),
                    variants=[variant])
                respuesta = self._crear(productInput)
                self._publicar(respuesta['product']['id'],
                               evento.gids['publications'])
                evento.gids['articulos'][evento.data.NewImage.co_art] = {
                    'productId': respuesta['product']['id'],
                    'variantId': (
                        respuesta['product']['variants']['nodes'][0]['id']
                    )
                }
                evento.actualizarBD()
            elif evento.cambios:
                self.logger.info("Actualizando producto.")
                inventory = ([MinventoryLevelInput(
                    availableQuantity=(evento.cambios.stock_act
                             if evento.cambios.stock_act
                             else evento.dynamodb.OldImage.stock_act),
                    locationId=evento.gids[
                        evento.cambio.codigoTienda
                        if evento.cambio.codigoTienda
                        else evento.data.OldImage.codigoTienda
                    ]
                )]
                    if evento.cambios.stock_act or evento.cambios.codigoTienda
                    else None)
                variantInput = MproductVariantInput(
                    **evento.cambios.dict(by_alias=True,
                                          exclude_none=True),
                    inventoryQuantities=inventory)
                variantInput.price = getattr(
                    evento.cambios, evento.config['precio'])
                status = {
                    None: None,
                    True: "ACTIVE",
                    False: "ARCHIVED"
                }[evento.cambios.habilitado]
                productInput = MproductInput(
                    **evento.cambios.dict(by_alias=True,
                                          exclude_none=True),
                    status=status)
                productInput.id, variantInput.id = (
                    evento.gids['articulos'][evento.data.OldImage.co_art]
                ).values()
                self._request(
                    'modificarVarianteProducto',
                    variables={'input': variantInput.dict(exclude_none=True)}
                )
                self._modificar(productInput)
        except Exception:
            raise

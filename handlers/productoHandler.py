from logging import getLogger
from handlers.shopifyObject import ShopifyObject
from handlers.sucursalHandler import Sucursal
from models.producto import (
    MproductInput,
    MproductVariantInput,
    MinventoryLevelInput
)
from models.event import Mevent, Marticulo
import json
from os import rename


class Producto(ShopifyObject):

    @staticmethod
    def actualizarBD(data: Marticulo, respuesta: dict):
        DBtemp_path = f'DB/{data.codigoCompania}.json.tmp'
        DBpath = f'DB/{data.codigoCompania}.json'
        with open(DBtemp_path, 'w') as DBtemp:
            with open(DBpath) as DBfile:
                DB = json.load(DBfile)
            DB[data.entity] = {
                data.co_art: {
                    'productId': respuesta['product']['id'],
                    'variantId': (
                        respuesta['product']['variants']['nodes'][0]['id']
                    )
                }
            }
            json.dump(DB, DBtemp)
        rename(DBtemp_path, DBpath)

    @staticmethod
    def obtenerId(codigoCompania: str, co_art: str) -> dict:
        DBpath = f'DB/{codigoCompania}.json'
        with open(DBpath) as DBfile:
            DB = json.load(DBfile)['articulos']
        return DB[co_art]

    def __init__(self, evento: Mevent):
        self.logger = getLogger("Shopify.Producto")
        self.logger.info("Creando instancia de producto")
        self.establecerTipo(evento)

        try:
            self._establecerConexion(evento.config.shopify)
            if evento.eventName == "INSERT":
                data = evento.dynamodb.NewImage
                inventory = [MinventoryLevelInput(
                    availableQuantity=data.stock_act,
                    locationId=Sucursal.obtenerId(data.codigoCompania,
                                                  data.codigoTienda)
                )]
                variant = MproductVariantInput(**data.dict(by_alias=True,
                                                           exclude_none=True),
                                               inventoryQuantities=inventory)
                variant.price = getattr(data, evento.config.precio)
                productInput = MproductInput(
                    **data.dict(by_alias=True,
                                exclude_none=True),
                    status="ACTIVE" if data.habilitado else "ARCHIVED",
                    variants=[variant])
                respuesta = self._crear(productInput)
                self._publicar(respuesta['product']['id'],
                               evento.config.shopify['publicationIds'])
                self.actualizarBD(data, respuesta)
            if evento.eventName == "MODIFY":
                data = self.obtenerCambios(evento)
                inventory = ([MinventoryLevelInput(
                    availableQuantity=(data.stock_act
                             if data.stock_act
                             else evento.dynamodb.OldImage.stock_act),
                    locationId=Sucursal.obtenerId(
                        data.codigoCompania,
                        (data.codigoTienda
                         if data.codigoTienda
                         else evento.dynamodb.OldImage.codigoTienda))
                )]
                    if data.stock_act or data.codigoTienda else None)
                variantInput = MproductVariantInput(
                    **data.dict(by_alias=True,
                                exclude_none=True),
                    inventoryQuantities=inventory)
                variantInput.price = getattr(data, evento.config.precio)
                if data.habilitado is None:
                    status = None
                else:
                    status = "ACTIVE" if data.habilitado else "ARCHIVED"
                productInput = MproductInput(**data.dict(by_alias=True,
                                                         exclude_none=True),
                                             status=status)
                productInput.id, variantInput.id = self.obtenerId(
                    evento.dynamodb.OldImage.codigoCompania,
                    evento.dynamodb.OldImage.co_art).values()
                self._request(
                    'modificarVarianteProducto',
                    variables={'input': variantInput.dict(exclude_none=True)}
                )
                self._modificar(productInput)
        except Exception:
            raise

    def consultar(self):
        try:
            respuesta = self._consultar()
            self._actualizarDatos(respuesta)
        except Exception:
            raise

    def crear(self):
        try:
            self._crear(MproductInput.parse_obj(self.data))
            self._publicar()
        except Exception:
            raise

    def modificar(self, input: dict):
        try:
            input['id'] = self.ID
            self._modificar(MproductInput.parse_obj(input))
        except Exception:
            raise

    def eliminar(self):
        try:
            self._eliminar()
        except Exception:
            raise

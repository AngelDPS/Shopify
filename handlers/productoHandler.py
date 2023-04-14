from logging import getLogger
from handlers.shopifyObject import ShopifyObject
from models.producto import MproductInput


class Producto(ShopifyObject):
    logger = getLogger("Shopify.Producto")
    _Type = "producto"

    def __init__(self, event: dict):
        self.logger.info("Creando instancia de producto")

        try:
            self._establecerConexion()
            self.ID = event['id']
            self._actualizarDatos(event)
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

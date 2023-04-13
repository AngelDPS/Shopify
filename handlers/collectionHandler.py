import logging
from models.collection import McollectionInput
from handlers.shopifyObject import ShopifyObject


class Coleccion(ShopifyObject):
    logger = logging.getLogger("Shopify.Coleccion")
    _Type = "coleccion"

    def __init__(self, input: dict = None, id: str = None):
        self.logger.info("Creando instancia de colección")

        try:
            self._establecerConexion()
            if id:
                self.ID = id
                self._consultar()
            elif input:
                self._crear(McollectionInput.parse_obj(input))
                # self._publicar()
            else:
                msg = "Para instanciar una colección, se debe otorgar un ID " \
                    "de referencia o una entrada con la información para " \
                    "crear una nueva sucursal."
                self.logger.exception(msg, stack_info=True)
                raise ValueError(msg)
        except ValueError as err:
            self.logger.exception(err)
            raise
        except Exception:
            raise

    def modificar(self, input: dict):
        try:
            input['id'] = self.ID
            self._modificar(McollectionInput.parse_obj(input))
        except Exception:
            raise

    def eliminar(self):
        try:
            self._eliminar()
        except Exception:
            raise

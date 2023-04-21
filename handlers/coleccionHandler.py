import logging
from models.coleccion import McollectionInput
from handlers.shopifyObject import ShopifyObject
# from handlers.eventHandler import Evento


class Coleccion(ShopifyObject):

    def __init__(self, evento):
        self.logger = logging.getLogger("Shopify.Coleccion")
        self.establecerTipo(evento.data.NewImage.entity)

        try:
            self._establecerConexion(evento.config['shopify'])
            if not evento.data.OldImage:
                self.logger.info("Creando colección a partir de línea.")
                self.respuesta = self._crear(
                    McollectionInput.parse_obj(
                        evento.data.NewImage
                    )
                )
                self._publicar(self.respuesta["collection"]["id"],
                               evento.gids["publications"])
                (evento.gids['lineas']
                 [evento.data.NewImage.co_lin_padre]
                    [evento.data.NewImage.co_lin]) = (
                    self.respuesta['collection']['id']
                )
                # TODO: Hector aqui se actualiza la BD.
                self.actualizarBD()
            elif evento.cambios:
                self.logger.info("Actualizando colección.")
                shopifyInput = McollectionInput.parse_obj(
                    evento.cambios
                )
                shopifyInput.id = (evento.gids['lineas']
                                   [evento.data.OldImage.co_lin_padre]
                                   [evento.data.OldImage.co_lin])
                self.respuesta = self._modificar(shopifyInput)
            # TODO: Implemetar en caso de delete.
        except Exception:
            self.error = True
            raise

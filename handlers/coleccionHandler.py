import logging
from models.coleccion import McollectionInput
from models.event import Mevent, Mlinea
from handlers.shopifyObject import ShopifyObject
from os import rename
import json


class Coleccion(ShopifyObject):

    @staticmethod
    def actualizarBD(data: Mlinea, respuesta: dict):
        DBtemp_path = f'DB/{data.codigoCompania}.json.tmp'
        DBpath = f'DB/{data.codigoCompania}.json'
        with open(DBtemp_path, 'w') as DBtemp:
            with open(DBpath) as DBfile:
                DB = json.load(DBfile)
            DB[data.entity] = {
                data.co_lin_padre: {
                    data.co_lin: respuesta['collection']['id']
                }
            }
            json.dump(DB, DBtemp)
        rename(DBtemp_path, DBpath)

    @staticmethod
    def obtenerId(codigoCompania: str,
                  co_lin_padre: str,
                  co_lin: str) -> str:
        DBpath = f'DB/{codigoCompania}.json'
        with open(DBpath) as DBfile:
            DB = json.load(DBfile)['lineas']
        return DB[co_lin_padre][co_lin]

    def __init__(self, evento: Mevent):
        self.logger = logging.getLogger("Shopify.Coleccion")
        self.logger.info("Creando instancia de colección")
        self.establecerTipo(evento)

        try:
            self._establecerConexion(evento.config.shopify)
            if evento.eventName == "INSERT":
                respuesta = self._crear(
                    McollectionInput.parse_obj(
                        evento.dynamodb.NewImage
                    )
                )
                self._publicar(respuesta["collection"]["id"],
                               evento.config.shopify["publicationIds"])
                self.actualizarBD(evento, respuesta["collection"]["id"])
            elif evento.eventName == "MODIFY":
                shopifyInput = McollectionInput.parse_obj(
                    self.obtenerCambios(evento)
                )
                shopifyInput.id = self.obtenerId(
                    evento.dynamodb.OldImage.codigoCompania,
                    evento.dynamodb.OldImage.co_lin_padre,
                    evento.dynamodb.OldImage.co_lin
                )
                respuesta = self._modificar(shopifyInput)
        except Exception:
            raise

import logging
from models.event import Mevent, Mtienda
from models.sucursal import MsucursalInput
from handlers.shopifyObject import ShopifyObject
from os import rename
import json
import re


class Sucursal(ShopifyObject):

    @staticmethod
    def parseDireccion(direccion: str) -> dict:
        ISO_3166_2_VE = {
            'Distrito Capital': 'VE-A',
            'Anzoátegui': 'VE-B',
            'Apure': 'VE-C',
            'Aragua': 'VE-D',
            'Barinas': 'VE-E',
            'Bolívar': 'VE-F',
            'Carabobo': 'VE-G',
            'Cojedes': 'VE-H',
            'Falcón': 'VE-I',
            'Guárico': 'VE-J',
            'Lara': 'VE-K',
            'Mérida': 'VE-L',
            'Miranda': 'VE-M',
            'Monagas': 'VE-N',
            'Nueva Esparta': 'VE-O',
            'Portuguesa': 'VE-P',
            'Sucre': 'VE-R',
            'Táchira': 'VE-S',
            'Trujillo': 'VE-T',
            'Yaracuy': 'VE-U',
            'Zulia': 'VE-V',
            'Dependencias Federales': 'VE-W',
            'La Guaira': 'VE-X',
            'Delta Amacuro': 'VE-Y',
            'Amazonas': 'VE-Z'
        }

        m = (re.match(
            r"^(?P<address1>.*)\s(?P<city>\w+), Edo.\s(?P<province>[\w\s]+)$",
            direccion
        ).groupdict()
        )
        m['provinceCode'] = ISO_3166_2_VE[m['province']]
        return m

    @staticmethod
    def actualizarBD(data: Mtienda, respuesta: dict):
        DBtemp_path = f'DB/{data.codigoCompania}.json.tmp'
        DBpath = f'DB/{data.codigoCompania}.json'
        with open(DBtemp_path, 'w') as DBtemp:
            with open(DBpath) as DBfile:
                DB = json.load(DBfile)
            DB[data.entity] = {
                data.codigoTienda: respuesta['location']['id']
            }
            json.dump(DB, DBtemp)
        rename(DBtemp_path, DBpath)

    @staticmethod
    def obtenerId(codigoCompania: str, codigoTienda: str) -> str:
        DBpath = f'DB/{codigoCompania}.json'
        with open(DBpath) as DBfile:
            DB = json.load(DBfile)['tiendas']
        return DB[codigoTienda]

    def __init__(self, evento: Mevent):
        self.logger = logging.getLogger("Shopify.Sucursal")
        self.logger.info("Creando instancia de sucursal.")
        self.establecerTipo(evento)

        try:
            self._establecerConexion(evento.config.shopify)
            if evento.eventName == "INSERT":
                data = evento.dynamodb.NewImage
                respuesta = self._crear(
                    MsucursalInput(
                        name=data.nombre,
                        address={
                            **self.parseDireccion(data.direccion),
                            'phone': data.telefono
                        }
                    )
                )
                self.actualizarBD(data, respuesta)
            elif evento.eventName == "MODIFY":
                data = self.obtenerCambios(evento)
                direccion = (self.parseDireccion(data.direccion)
                             if data.direccion else {})
                shopifyInput = MsucursalInput(
                    name=data.nombre,
                    adrress={
                        **direccion,
                        'phone': data.telefono
                    }
                )
                self._modificar(
                    shopifyInput,
                    id=self.obtenerId(
                        evento.dynamodb.OldImage.codigoCompania,
                        evento.dynamodb.OldImage.codigoTienda
                    )
                )
        except Exception as err:
            self.logger.exception(err)
            raise

    def modificar(self, shopifyInput: dict):
        try:
            self._modificar(
                MsucursalInput.parse_obj(shopifyInput),
                id=self.ID
            )
        except Exception:
            raise

    def eliminar(self):
        try:
            self._eliminar()
        except Exception:
            raise

    def desactivar(self, sucursalAlt=None):
        try:
            respuesta = self._request(
                "desactivar",
                variables={"id": self.ID}
            )
            if respuesta["locationDeactivateUserErrors"]:
                raise RuntimeError(
                    "Ocurrió un error desactivando la sucursal:\n"
                    f"{respuesta['locationDeactivateUserErrors']}")
            self.logger.info("Sucursal desactivada exitosamente.")
        except Exception:
            self.logger.exception("No se pudo desactivar la sucursal.")

    def activar(self):
        try:
            respuesta = self._request(
                "activar",
                variables={"id": self.ID}
            )
            if respuesta["locationActivateUserErrors"]:
                raise RuntimeError(
                    "Ocurrió un error activando la sucursal:\n"
                    f"{respuesta['locationActivateUserErrors']}")
            self.logger.info("Sucursal activada exitosamente.")
        except Exception:
            self.logger.exception("No se pudo activar la sucursal.")

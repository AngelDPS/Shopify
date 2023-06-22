import logging
from models.sucursal import MsucursalInput
from handlers.shopifyObject import ShopifyObject
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
        ).groupdict())
        m['provinceCode'] = ISO_3166_2_VE[m['province']]
        return m

    def __init__(self, evento):
        self.logger = logging.getLogger("Shopify.Sucursal")
        self.establecerTipo(evento.data.NewImage.entity)

        try:
            self._establecerConexion(evento.config['shopify'])
            if not evento.data.OldImage:
                self.logger.info("Creando sucursal a partir de tienda.")
                respuesta = self._crear(
                    MsucursalInput(
                        name=evento.data.NewImage.nombre,
                        address={
                            **self.parseDireccion(
                                evento.data.NewImage.direccion
                            ),
                            'phone': evento.data.NewImage.telefono
                        }
                    )
                )
                evento.gids = (evento.gids | {'tiendas': {
                    evento.data.NewImage.codigoTienda:
                        respuesta['location']['id']
                }})
                evento.actualizarBD()
            elif evento.cambios:
                self.logger.info("Actualizando sucursal.")
                shopifyInput = MsucursalInput(
                    name=evento.cambios.nombre,
                    adrress={
                        **(self.parseDireccion(evento.cambios.direccion)
                           if evento.cambios.direccion else {}),
                        'phone': evento.cambios.telefono
                    }
                )
                self._modificar(
                    shopifyInput,
                    id=(evento.gids['tiendas']
                        [evento.data.OldImage.codigoTienda])
                )
                {
                    None: None,
                    True: self.activar,
                    False: self.desactivar
                }[evento.cambios.habilitado](
                    id=(evento.gids['tiendas']
                        [evento.data.OldImage.codigoTienda]),
                    altId=(evento.gids['tiendas']
                           [evento.data.OldImage.codigoTiendaAlt])
                )
        except Exception:
            raise

    def desactivar(self, id: str, altId: str = None):
        try:
            respuesta = self._request(
                "desactivarSucursal",
                variables={"id": id, "altId": altId}
            )
            if respuesta["locationDeactivateUserErrors"]:
                raise RuntimeError(
                    "Ocurrió un error desactivando la sucursal:\n"
                    f"{respuesta['locationDeactivateUserErrors']}")
            self.logger.info("Sucursal desactivada exitosamente.")
        except Exception:
            self.logger.exception("No se pudo desactivar la sucursal.")

    def activar(self, id: str, altId: str = None):
        try:
            respuesta = self._request(
                "activarSucursal",
                variables={"id": id}
            )
            if respuesta["locationActivateUserErrors"]:
                raise RuntimeError(
                    "Ocurrió un error activando la sucursal:\n"
                    f"{respuesta['locationActivateUserErrors']}")
            self.logger.info("Sucursal activada exitosamente.")
        except Exception:
            self.logger.exception("No se pudo activar la sucursal.")

import logging
from models.sucursal import MsucursalInput
from handlers.shopifyObject import ShopifyObject


class Sucursal(ShopifyObject):
    logger = logging.getLogger("Shopify.Sucursal")
    _Type = "sucursal"

    def __init__(self, input: dict = None,
                 id: str = None):
        self.logger.info("Creando instancia de sucursal.")

        try:
            self._establecerConexion()
            if id:
                self.ID = id
                self._consultar()
            elif input:
                self._crear(MsucursalInput.parse_obj(input))
            else:
                msg = "Para instanciar una sucursal, se debe otorgar un ID " \
                    "de referencia o una entrada con la información para " \
                    "crear una nueva sucursal."
                self.logger.exception(msg, stack_info=True)
                raise TypeError(msg)
        except TypeError as err:
            self.logger.exception(err)
            raise
        except Exception:
            raise

    def modificar(self, input: dict):
        try:
            self._modificar(
                MsucursalInput.parse_obj(input),
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

import logging
import libs.gqlrequests
from pydantic import BaseModel
from typing import Literal
from libs.conexion import ConexionShopify

logger = logging.getLogger("Shopify.object")


class ShopifyObject:
    logger: logging.Logger
    conexion: ConexionShopify
    _Type: Literal["producto", "coleccion", "sucursal"]
    ID: str

    def _establecerModelo(self, Modelo: BaseModel):
        if issubclass(Modelo, BaseModel):
            self.data = Modelo
        else:
            msg = "El 'Modelo' debe ser una subclase de pydantic.BaseModel"
            self.logger.exception(msg)
            raise TypeError(msg)

    def _establecerConexion(self):
        try:
            self.conexion = ConexionShopify()
        except Exception as err:
            self.logger.exception(err)
            raise

    def _actualizarDatos(self, respuesta: dict):
        """Actualiza los atributos de la instancia a los valores
        obtenidos de Shopify

        Args:
            respuesta (dict): diccionario con la información correspondiente.
            TODO: Debe de reemplazarse por un modelo de respuesta apropiado.
        """
        # self.data.parse_obj(respuesta)
        pass

    def _borrarDatos(self):
        """Elimina los atributos de la instancia en el momento en que se
        elimina la sucursal en Shopify.
        """
        del self.data
        del self.ID

    def __str__(self):
        return f"{self._Type.capitalize()}:\n{self.data.json()}"

    def _request(self, operacion: str, variables: dict = None) -> dict:
        respuesta = (self.conexion.enviarConsulta(
            getattr(libs.gqlrequests, self._Type),
            variables=variables,
            operacion=operacion))
        respuesta = respuesta[list(respuesta)[0]]
        if respuesta.get("userErrors"):
            raise RuntimeError("No fue posible realizar la operación:\m"
                               f"{respuesta['userErrors']}")
        return respuesta

    def _consultar(self) -> dict:
        try:
            respuesta = self._request("consultar",
                                      variables={'id': self.ID})
            self.logger.info(
                f"{self._Type.capitalize()} "
                "consultado/a exitosamente en Shopify."
            )
            self.logger.debug(respuesta)
            self._actualizarDatos(respuesta)
            return respuesta
        except ValueError as err:
            self.logger.exception(err, stack_info=True)
            raise
        except Exception:
            self.logger.exception(
                f"No fue posible consultar el/la {self._Type}."
            )
            raise

    def _crear(self, input: BaseModel) -> dict:
        try:
            respuesta = self._request(
                "crear",
                variables={
                    'input': input.dict(exclude_none=True)
                }
            )
            self.logger.info(f"{self._Type.capitalize()} "
                             "creado/a exitosamente.")
            self.logger.debug(respuesta)
            self._actualizarDatos(respuesta)
            return respuesta
        except Exception:
            self.logger.exception(f"No fue posible crear el/la {self._Type}")
            raise

    def _modificar(self, input: BaseModel, **kwargs) -> dict:
        try:
            respuesta = self._request(
                "modificar",
                variables={
                    'input': input.dict(exclude_none=True),
                    **kwargs
                },
            )
            self.logger.info(f"{self._Type.capitalize()} "
                             "fue modificado/a exitosamente.")
            self.logger.debug(respuesta)
            return respuesta
        except Exception:
            self.logger.exception("No fue posible modificar el/la "
                                  f"{self._Type}")
            raise

    def _eliminar(self) -> dict:
        self.logger.info(f'Eliminando el/la {self._Type}')
        try:
            respuesta = self._request(
                'eliminar',
                variables={'id': self.ID}
            )
            if respuesta.get("locationDeleteUserErrors"):
                raise RuntimeError("Ocurrió un error eliminando la sucursal:\n"
                                   f"{respuesta['locationDeleteUserErrors']}")
            self.logger.info(f"{self._Type.capitalize()} "
                             "eliminado/a exitosamente")
            self.logger.debug(respuesta)
            self._borrarDatos()
            return respuesta
        except Exception:
            self.logger.exception(f"No se pudo eliminar el/la {self._Type}.")
            raise

    def _publicar(self, publicationIds: list[str]) -> dict:
        try:
            respuesta = self.conexion.enviarConsulta(
                libs.gqlrequests.misc,
                operacion='publicar',
                variables={
                    'id': self.ID,
                    'input': [{"publicationId": i} for i in publicationIds]
                }
            )
            self.logger.info(f"Publicación exitosa de el/la {self._Type}.")
            self.logger.debug(respuesta)
            return respuesta
        except Exception:
            self.logger.exception(f"No se pudo publicar el/la {self._Type}")
            raise

    def _ocultar(self, publicationIds: list[str]) -> dict:
        try:
            respuesta = self.conexion.enviarConsulta(
                libs.gqlrequests.misc,
                operacion='ocultar',
                variables={
                    'id': self.ID,
                    'input': [{"publicationId": i} for i in publicationIds]
                }
            )
            self.logger.info("Ocultada exitosa.")
            self.logger.debug(respuesta)
            return respuesta
        except Exception:
            self.logger.exception("No se pudo ocultar")
            raise

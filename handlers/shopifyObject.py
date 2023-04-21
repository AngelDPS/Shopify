import logging
import libs.gqlrequests
from typing import Literal
from pydantic import BaseModel
from libs.conexion import ConexionShopify


class ShopifyObject:
    logger: logging.Logger
    conexion: ConexionShopify
    _Type: Literal["producto", "coleccion", "sucursal"]

    def establecerTipo(self, entity: str):
        self._Type = {
            "articulos": "producto",
            "lineas": "coleccion",
            "tiendas": "sucursal"
        }[entity]

    def _establecerConexion(self, config: dict):
        try:
            self.conexion = ConexionShopify(config)
        except Exception as err:
            self.logger.exception(err)
            raise

    def _request(self, operacion: str, variables: dict = None) -> dict:
        self.logger.debug(f'{variables = }')
        respuesta = (self.conexion.enviarConsulta(
            getattr(libs.gqlrequests, self._Type),
            variables=variables,
            operacion=operacion))
        respuesta = respuesta[list(respuesta)[0]]
        self.logger.debug(f'{respuesta = }')
        if respuesta.get("userErrors"):
            msg = ("No fue posible realizar la operación:\n"
                   f"{respuesta['userErrors']}")
            self.logger.exception(msg)
            raise RuntimeError(msg)
        return respuesta

    def _crear(self, input: BaseModel, **kwargs) -> dict:
        try:
            respuesta = self._request(
                "crear" + self._Type.capitalize(),
                variables={
                    'input': input.dict(exclude_none=True),
                    **kwargs
                }
            )
            self.logger.info(f"{self._Type.capitalize()} "
                             "creado/a exitosamente.")
            return respuesta
        except Exception:
            self.logger.exception(f"No fue posible crear el/la {self._Type}")
            raise

    def _modificar(self, input: BaseModel, **kwargs) -> dict:
        try:
            respuesta = self._request(
                "modificar" + self._Type.capitalize(),
                variables={
                    'input': input.dict(exclude_none=True),
                    **kwargs
                },
            )
            self.logger.info(f"{self._Type.capitalize()} "
                             "fue modificado/a exitosamente.")
            return respuesta
        except Exception:
            self.logger.exception("No fue posible modificar el/la "
                                  f"{self._Type}")
            raise

    def _publicar(self, id: str, publicationIds: list[str]) -> dict:
        try:
            respuesta = self.conexion.enviarConsulta(
                libs.gqlrequests.misc,
                operacion='publicar',
                variables={
                    'id': id,
                    'input': [{"publicationId": i} for i in publicationIds]
                }
            )
            self.logger.info(f"Publicación exitosa de el/la {self._Type}.")
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
            return respuesta
        except Exception:
            self.logger.exception("No se pudo ocultar")
            raise

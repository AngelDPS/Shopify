import logging
import libs.gqlrequests
from pydantic import BaseModel
from typing import Literal
from libs.conexion import ConexionShopify
from models.event import Mevent, MdynamoDB


class ShopifyObject:
    logger: logging.Logger
    conexion: ConexionShopify
    _Type: Literal["producto", "coleccion", "sucursal"]
    ID: str

    def establecerTipo(self, event: Mevent):
        mapper = {
            "articulos": "producto",
            "lineas": "coleccion",
            "tiendas": "sucursal"
        }
        self._Type = mapper[event.dynamodb.NewImage.entity]

    def _establecerConexion(self, config: dict):
        try:
            self.conexion = ConexionShopify(config)
        except Exception as err:
            self.logger.exception(err)
            raise

    def __str__(self):
        return f"{self._Type.capitalize()}:\n{self.data.json()}"

    def _request(self, operacion: str, variables: dict = None) -> dict:
        self.logger.debug(variables)
        respuesta = (self.conexion.enviarConsulta(
            getattr(libs.gqlrequests, self._Type),
            variables=variables,
            operacion=operacion))
        respuesta = respuesta[list(respuesta)[0]]
        if respuesta.get("userErrors"):
            msg = ("No fue posible realizar la operación:\n"
                   f"{respuesta['userErrors']}")
            self.logger.exception(msg)
            raise RuntimeError(msg)
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

    def _crear(self, input: BaseModel, **kwargs) -> dict:
        try:
            self.logger.debug(input)
            respuesta = self._request(
                "crear",
                variables={
                    'input': input.dict(exclude_none=True),
                    **kwargs
                }
            )
            self.logger.info(f"{self._Type.capitalize()} "
                             "creado/a exitosamente.")
            self.logger.debug(respuesta)
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

    @staticmethod
    def obtenerCambios(self, evento: Mevent) -> dict:
        cambios = {
            k: v for k, v in evento.dynamodb.NewImage
            if (v != getattr(evento.dynamodb.OldImage, k) or
                k == "entity")
        }
        self.logger.debug(cambios)
        return MdynamoDB(NewImage=cambios).NewImage

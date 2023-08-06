from aws_lambda_powertools.utilities.parameters import SSMProvider
from boto3 import Session
from os import getenv
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any
from aws_lambda_powertools import Logger

logger = Logger(service="utilities")


def obtener_codigo(evento: list[dict]) -> str | None:
    """Obtiene el código identificador de la entidad del ítem de DynamoDB
    que generó el evento.

    Args:
        evento (list[dict]): Evento recibido por Lambda para ser procesado
        debido a cambios en DynamoDB.

    Returns:
        str | None: Código  único del ítem de DynamoDB para la entidad.
    """
    try:
        record = evento["dynamodb"]["NewImage"]
    except KeyError:
        record = evento["Records"][0]["dynamodb"]["NewImage"]
    except IndexError:
        record = evento[0]["dynamodb"]["NewImage"]
    match record["entity"]["S"]:
        case "articulos":
            return record["co_art"]["S"]
        case "lineas":
            return record["co_lin"]["S"]
        case "tiendas":
            return record["codigoTienda"]["S"]
        case _:
            return None


def get_parameter(key: str) -> Any:
    """Obtiene el valor asociado al key del json almacenado como
    parámetro "/akia9/akiastock/{NOMBRE_COMPANIA}"en el
    Parameter Store del AWS Systems Manager.

    Args:
        key (str): Key para la identificación del valor requerido del json
        almacenado en el parámetro.

    Returns:
        Any: Valor obtenido del json almacenado en el parámetro.
    """
    if getenv("AWS_EXECUTION_ENV") is None:
        ssm_provider = SSMProvider(
            boto3_session=Session(profile_name=getenv('AWS_PROFILE_NAME'))
        )
    else:
        ssm_provider = SSMProvider()
    return ssm_provider.get(
        f"/akia9/akiastock/{getenv('NOMBRE_COMPANIA')}",
        transform="json",
        max_age=300
    ).get(key)


class ItemHandler(ABC):
    ITEM_TYPE: str
    old_image: dict | BaseModel
    cambios: dict | BaseModel

    @abstractmethod
    def __init__(self): pass

    @abstractmethod
    def crear(self): pass

    @abstractmethod
    def modificar(self): pass

    @abstractmethod
    def ejecutar(self, web_store: str, id: str | None) -> list[str]:
        """Ejecuta la acción requerida por el evento procesado en la instancia.

        Returns:
            list[str]: Conjunto de resultados obtenidos por las operaciones
            ejecutadas.
        """
        try:
            if self.cambios.dict(exclude_unset=True):
                logger.info("Se aplicarán los cambios al "
                            f"{self.ITEM_TYPE} en {web_store}.")
                if not self.old_image.dict(exclude_unset=True):
                    logger.info(
                        "Al no haber OldImage en el evento, se identica "
                        "como un INSERT y se procede a crear el "
                        f"{self.ITEM_TYPE} en {web_store}."
                    )
                    respuesta = self.crear()
                elif not id:
                    self.cambios = self.cambios.parse_obj(
                        self.old_image.dict()
                        | self.cambios.dict(exclude_unset=True)
                    )
                    logger.info(
                        "En el evento, proveniente de la base de "
                        "datos, no se encontró el ID de "
                        f"{self.ITEM_TYPE} para {web_store}. Se creará un "
                        f"{self.ITEM_TYPE} nuevo con la data actualizada."
                    )
                    respuesta = self.crear()
                else:
                    respuesta = self.modificar()
            else:
                logger.info("Los cambios encontrados no ameritan "
                            f"actualizaciones en {web_store}.")
                respuesta = ["No se realizaron acciones."]
        except Exception:
            logger.exception("Ocurrió un problema ejecutando la acción "
                             "sobre el producto.")
            raise
        return respuesta

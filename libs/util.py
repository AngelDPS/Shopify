# from aws_lambda_powertools.utilities import parameters
# from os import getenv
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
        record = evento[0]["dynamodb"]["NewImage"]
    except IndexError:
        record = evento["Records"][0]["dynamodb"]["NewImage"]
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
    # try:
    #     parameter = f"/akia9/akiastock/{getenv('NOMBRE_COMPANIA')}"
    #     return parameters.get_parameter(parameter, transform="json",
    #                                     max_age=300).get(key)
    # except Exception:
    #     logger.exception(
    #         f"Ocurrión un error obteniendo el valor de '{key}' del "
    #         f"parámetro '{parameter}'.")
    #     raise
    params = {
        "region": "us-east-2",
        "database": "akiastock_generico2022",
        "dbusername": "admin",
        "dbpassword": "Macaveo28!",
        "dbhost": "bisalud-database-rds.cpdpaoh0epx0.us-east-2.rds.amazonaws.com",
        "userpoolid": "us-east-2_2D1N9OQnY",
        "appclientadmin": "38npvd6jh1frluu1920h2qcdpm",
        "appclientuser": "4hoomirg2c72a8lah8jv8o5dlh",
        "monedasistema": "DOLAR",
        "campoprecio": "prec_vta2",
        "loglevel": "DEBUG",
        "loggername": "GENERICO_LOGGER",
        "bucketname": "angelbucket-test",
        "bucketmaxsize": "1000",
        "features": ["pedidos", "inventario", "imagenes", "etiquetas"],
        "opensearchserver": "https://search-akia9-akiastock1-by25omxy2tszfroocxcjgygqpu.us-east-2.es.amazonaws.com",
        "opensearchuser": "generico2022user",
        "opensearchpassword": "r8Akia765.!",
        "dynamodb": "generico2022-db",
        "crear_pedido_tercero": "PREPARADO",
        "SHOPIFY_ACCESS_TOKEN": "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",
        "SHOPIFY_SHOP": "2f64b9",
        "SHOPIFY_SQSURL": "https://sqs.us-east-2.amazonaws.com/099375320271/AngelQueue.fifo",
        "SHOPIFY_PRECIO": "prec_vta1",
        "MELI_PRECIO": "prec_vta2",
        "MELI_SQSURL": "https://sqs.us-east-2.amazonaws.com/099375320271/AngelQueue.fifo"
    }
    return params.get(key)


class ItemHandler(ABC):
    item: str
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
                            f"{self.item} en {web_store}.")
                if not self.old_image.dict(exclude_unset=True):
                    logger.info(
                        "Al no haber OldImage en el evento, se identica como "
                        "un INSERT y se procede a crear el "
                        f"{self.item} en {web_store}."
                    )
                    respuesta = self.crear()
                elif not id:
                    logger.info(
                        "En el evento, proveniente de la base de datos, no se "
                        f"encontró el ID de {self.item} para {web_store}. "
                        f"Se creará un {self.item} nuevo con la data "
                        "actualizada."
                    )
                    self.cambios = self.cambios.parse_obj(
                        self.old_image.dict()
                        | self.cambios.dict(exclude_unset=True)
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

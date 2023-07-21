from os import environ, getenv
from libs.util import get_parameter
from handlers.eventHandler import procesar_todo
from handlers.productoHandler import ProductoHandler
from handlers.coleccionHandler import ColeccionHandler
from aws_lambda_powertools import Logger
from typing import Any, Dict, List

logger = Logger(service="shopify",
                level=get_parameter("loglevel") or "WARNING")


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: List[dict], context: Any) -> List[Dict[str, str]]:
    """Manipulador de los eventos de entrada provenientes de
    una base de datos DynamoDB con el registro de inventario para
    ser manejados en una tienda de Shopify.

    Args:
        event (list[dict]): Lista de eventos provenientes de DynamoDB
        context (Any): context

    Raises:
        Exception: Levanta una excepción en caso de falla general. Trae consigo
        el evento que causó la excepción y la excepción padre que lo generó.

    Returns:
        list[dict[str, str]]: Lista de diccionarios con los mensajes
        retornados por cada evento procesado.
    """
    if getenv("AWS_EXECUTION_ENV") is None:
        environ["NOMBRE_COMPANIA"] = "generico2022"
        environ["AWS_REGION"] = "us-east-2"
        environ["SQSERROR_URL"] = "https://sqs.us-east-2.amazonaws.com/276507440195/generico2022-Dev-SQSShopifyError.fifo"
        environ["AWS_PROFILE_NAME"] = "generico2022-Dev"

    # --> Se desactiva la validación de los campos ya que se hace previo a la ejecución de este escript
    # filtro_campos = [
    #     "prec_vta1", "prec_vta2", "prec_vta3", "PK", "SK", "habilitado",
    #     "art_des", "codigoCompania", "codigoTienda", "co_art", "co_lin",
    #     "stock_act", "stock_com", "codigo_barra", "referencia", "marca",
    #     "imagen_url", "modelo"
    # ]

    # if event[0].get("eventName") == "INSERT":
    #     for key in filtro_campos:
    #         if key not in event[0]["dynamodb"]["NewImage"]:
    #             raise ValueError("El evento no contiene el campo " + key)
    # elif event[0].get("eventName") == "MODIFY":
    #     for key in filtro_campos:
    #         if (key not in event[0]["dynamodb"]["NewImage"]
    #                 or key not in event[0]["dynamodb"]["OldImage"]):
    #             raise ValueError("El evento no contiene el campo " + key)
    # else:
    #     raise ValueError("El evento no es válido")

    handler_mapping = {
        'articulos': ProductoHandler,
        'lineas': ColeccionHandler
        # 'tiendas': SucursalHandler
    }
    return procesar_todo('shopify', event, handler_mapping)

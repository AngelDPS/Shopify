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
    # environ["ENV"] = "local"
    if getenv("ENV") == "local":
        environ["NOMBRE_COMPANIA"] = "generico2022"
        environ["AWS_REGION"] = "us-east-2"

    handler_mapping = {
                'articulos': ProductoHandler,
                'lineas': ColeccionHandler
                # 'tiendas': SucursalHandler
            }
    return procesar_todo('shopify', event, handler_mapping)

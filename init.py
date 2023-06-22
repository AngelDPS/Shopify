from handlers.sqsHandler import SQShandler
from handlers.eventHandler import EventHandler
from libs.util import obtener_codigo, get_parameter
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

    sqs = SQShandler("shopify")
    codigo = obtener_codigo(event)
    eventos_en_cola, ids, codigos_en_cola, repetidos = sqs.process_messages()

    idx = sqs.procesar_entidades_repetidas(
        codigo=codigo,
        lista_codigos=codigos_en_cola,
        eventos=eventos_en_cola,
        NewImage=event[0]["dynamodb"]["NewImage"]
    )
    if idx is not None:
        logger.warning(
            f'Se encontraron eventos en cola para para "{codigo}" '
            'siendo procesado.'
        )
        eventos_en_cola.insert(0, eventos_en_cola.pop(idx))
        ids.insert(0, ids.pop(idx))
    else:
        eventos_en_cola.insert(0, event)
        ids.insert(0, None)

    logger.info(f"Eventos para procesar: {eventos_en_cola}")

    r = []
    for EVs, ID in zip(eventos_en_cola, ids):
        codigo_actual = obtener_codigo(EVs)
        try:
            for EV in EVs:
                r.append(EventHandler(EV).ejecutar())
                logger.debug(r[-1])
        except Exception as err:
            mensaje = (f"Ocurrió un error manejado el evento:\n{EV}."
                       f"Se levantó la excepción '{err}'.")
            logger.exception(mensaje)
            if codigo_actual == codigo:
                raise Exception(mensaje) from err
        else:
            if ID:
                sqs.delete_message(ID)
                if codigo_actual in repetidos:
                    sqs.delete_message(
                        repetidos[codigo_actual]["ReceiptHandle"]
                    )

    return r

from shopify.libs.sqs import (
    process_messages,
    procesar_entidades_repetidas,
    delete_message
)
from shopify.handlers.eventHandler import EventHandler
from shopify.libs.util import obtener_codigo
from aws_lambda_powertools import Logger
from typing import Any

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def event_handler(event: list[dict], context: Any) -> list[dict[str, str]]:
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
    logger.info("*** INICIO LAMBDA SHOPIFY ***")
    # raise Exception("PRUEBA")
    codigo = obtener_codigo(event)
    eventos_en_cola, ids, codigos_en_cola, repetidos = process_messages()

    idx = procesar_entidades_repetidas(
        codigo=codigo,
        lista_codigos=codigos_en_cola,
        eventos=eventos_en_cola,
        NewImage=event[0]["dynamodb"]["NewImage"]
    )
    if idx:
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
                # r.append('PRUEBA')
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
                delete_message(ID)
                if codigo_actual in repetidos:
                    delete_message(repetidos[codigo_actual]["ReceiptHandle"])

    logger.info("*** FIN LAMBDA SHOPIFY ***")
    return r


if __name__ == "__main__":
    event = [
        {
            "eventID": "ee993a53bd063ef72948caba3d7cfb33",
            "eventName": "MODIFY",
            "eventVersion": "1.1",
            "eventSource": "aws:dynamodb",
            "awsRegion": "us-east-2",
            "dynamodb": {
                "ApproximateCreationDateTime": 1685735093,
                "Keys": {
                    "SK": {
                        "S": "METADATA"
                    },
                    "PK": {
                        "S": "GENERICO2022#DLTVA#1005011A1"
                    }
                },
                "NewImage": {
                    "prec_vta1": {
                        "N": "63"
                    },
                    "prec_vta3": {
                        "N": "93"
                    },
                    "stock_com": {
                        "N": "0"
                    },
                    "tipo": {
                        "S": "TIENDA"
                    },
                    "ubicacion": {
                        "S": "C3G11"
                    },
                    "prec_vta2": {
                        "N": "80"
                    },
                    "co_lin": {
                        "S": "11"
                    },
                    "created_at": {
                        "S": "2023-05-18T11:50:26.134847Z"
                    },
                    "des_shopify": {
                        "S": "<p>Bienvenido a <strong>DELECTRA</strong> tu proveedor seguro! ⚡⚡</p><p>Prueba</p>"
                    },
                    "codigoTienda": {
                        "S": "DLTVA"
                    },
                    "marca": {
                        "S": "CHANA"
                    },
                    "updated_at": {
                        "S": "2023-05-18T11:50:26.134847Z"
                    },
                    "iva": {
                        "N": "16"
                    },
                    "codigoCompania": {
                        "S": "GENERICO2022"
                    },
                    "SK": {
                        "S": "METADATA"
                    },
                    "moneda": {
                        "N": "2"
                    },
                    "habilitado": {
                        "N": "1"
                    },
                    "prec_vta5": {
                        "N": "0"
                    },
                    "prec_vta4": {
                        "N": "105"
                    },
                    "info": {
                        "NULL": True
                    },
                    "prec_vta6": {
                        "N": "0"
                    },
                    "art_des": {
                        "S": "VOLANTE MOTOR CHANA-SAIC"
                    },
                    "co_art": {
                        "S": "1005011A1"
                    },
                    "imagen_url": {
                        "L": [
                            {
                                "S": "articulo_01R43119R01_876.webp"
                            },
                            {
                                "S": "articulo_0197C5_367.webp"
                            }
                        ]
                    },
                    "modelo": {
                        "S": "CHANA SV/DC"
                    },
                    "unidad": {
                        "S": "PZA"
                    },
                    "stock_act": {
                        "N": "20"
                    },
                    "PK": {
                        "S": "GENERICO2022#DLTVA#1005011A1"
                    },
                    "fx_costos": {
                        "S": "d208b81bcae86d4354120132c9380157"
                    },
                    "entity": {
                        "S": "articulos"
                    },
                    "referencia": {
                        "S": "CHASVD0200136"
                    }
                },
                "OldImage": {
                    "prec_vta1": {
                        "N": "63"
                    },
                    "prec_vta3": {
                        "N": "93"
                    },
                    "stock_com": {
                        "N": "0"
                    },
                    "tipo": {
                        "S": "TIENDA"
                    },
                    "ubicacion": {
                        "S": "C3G11"
                    },
                    "prec_vta2": {
                        "N": "80"
                    },
                    "co_lin": {
                        "S": "10"
                    },
                    "created_at": {
                        "S": "2023-05-18T11:50:26.134847Z"
                    },
                    "des_shopify": {
                        "S": "<p>Bienvenido a <strong>DELECTRA</strong> tu proveedor seguro! ⚡⚡</p><p>Prueba</p>"
                    },
                    "codigoTienda": {
                        "S": "DLTVA"
                    },
                    "marca": {
                        "S": "CHANA"
                    },
                    "updated_at": {
                        "S": "2023-05-18T11:50:26.134847Z"
                    },
                    "iva": {
                        "N": "16"
                    },
                    "codigoCompania": {
                        "S": "GENERICO2022"
                    },
                    "SK": {
                        "S": "METADATA"
                    },
                    "moneda": {
                        "N": "2"
                    },
                    "habilitado": {
                        "N": "1"
                    },
                    "prec_vta5": {
                        "N": "0"
                    },
                    "prec_vta4": {
                        "N": "105"
                    },
                    "info": {
                        "NULL": True
                    },
                    "prec_vta6": {
                        "N": "0"
                    },
                    "art_des": {
                        "S": "VOLANTE MOTOR CHANA-SAIC"
                    },
                    "co_art": {
                        "S": "1005011A1"
                    },
                    "imagen_url": {
                        "L": [
                            {
                                "S": "articulo_01R43119R01_876.webp"
                            },
                            {
                                "S": "articulo_0197C5_367.webp"
                            }
                        ]
                    },
                    "modelo": {
                        "S": "CHANA SV/DC"
                    },
                    "unidad": {
                        "S": "PZA"
                    },
                    "stock_act": {
                        "N": "20"
                    },
                    "PK": {
                        "S": "GENERICO2022#DLTVA#1005011A1"
                    },
                    "fx_costos": {
                        "S": "d208b81bcae86d4354120132c9380157"
                    },
                    "entity": {
                        "S": "articulos"
                    },
                    "referencia": {
                        "S": "CHASVD0200136"
                    }
                },
                "SequenceNumber": "134413900000000002860505418",
                "SizeBytes": 1302,
                "StreamViewType": "NEW_AND_OLD_IMAGES"
            },
            "eventSourceARN": "arn:aws:dynamodb:us-east-2:099375320271:table/angel-db/stream/2023-05-05T14:09:53.915"
        }
    ]

    cambio = {"co_lin": {
        "S": "10"
    }}
    cambio["stock_act"] = {"N": "20"}
    # event[0]["dynamodb"]["NewImage"] |= cambio

    event_handler(event, None)

from shopify.handlers.eventHandler import EventHandler
import shopify.libs.my_logging as my_logging
from typing import Any

logger = my_logging.getLogger("shopify")


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
    r = []
    for e in event:
        try:
            r.append(EventHandler(e).ejecutar())
            logger.debug(r[-1])
        except Exception as err:
            mensaje = (f"Ocurrió un error manejado el evento:\n{e}."
                       f"Se levantó la excepción '{err}'.")
            raise Exception(mensaje) from err

    logger.info("*** FIN LAMBDA SHOPIFY ***")
    return r


if __name__ == "__main__":
    event = [
        {
            "eventID": "a47d122d7bfc042520063c173ce48fff",
            "eventName": "MODIFY",
            "eventVersion": "1.1",
            "eventSource": "aws:dynamodb",
            "awsRegion": "us-east-2",
            "dynamodb": {
                "ApproximateCreationDateTime": 1683389013,
                "Keys": {
                    "SK": {
                        "S": "METADATA"
                    },
                    "PK": {
                        "S": "GENERICO2022#DLTVA#ACCE13"
                    }
                },
                "NewImage": {
                    "PK": {
                        "S": "GENERICO2022#DLTVA#ACCE13"
                    },
                    "SK": {
                        "S": "METADATA"
                    },
                    "art_des": {
                        "S": "ABRAZADERA EMT 2\" ADPS "
                    },
                    "cantidad_empaque": {
                        "N": "0"
                    },
                    "codigoCompania": {
                        "S": "GENERICO2022"
                    },
                    "codigoTienda": {
                        "S": "DLTVA"
                    },
                    "codigo_barra": {
                        "NULL": True
                    },
                    "co_art": {
                        "S": "ACCE13"
                    },
                    "co_lin": {
                        "S": "10"
                    },
                    "created_at": {
                        "S": "2023-04-14T18:52:12.427940Z"
                    },
                    "entity": {
                        "S": "articulos"
                    },
                    "habilitado": {
                        "N": "1"
                    },
                    "iva": {
                        "N": "16"
                    },
                    "marca": {
                        "NULL": True
                    },
                    "moneda": {
                        "N": "2"
                    },
                    "prec_vta1": {
                        "N": "0.4"
                    },
                    "prec_vta2": {
                        "N": "0.48"
                    },
                    "prec_vta3": {
                        "N": "0.53"
                    },
                    "referencia": {
                        "NULL": True
                    },
                    "stock_act": {
                        "N": "10"
                    },
                    "stock_com": {
                        "N": "0"
                    },
                    "tipo": {
                        "S": "TIENDA"
                    },
                    "ubicacion": {
                        "S": "P01"
                    },
                    "unidad": {
                        "S": "PZA"
                    },
                    "unidad_empaque": {
                        "NULL": True
                    },
                    "updated_at": {
                        "S": "2023-04-14T18:52:12.427940Z"
                    }
                },
                "OldImage": {
                    "PK": {
                        "S": "GENERICO2022#DLTVA#ACCE13"
                    },
                    "SK": {
                        "S": "METADATA"
                    },
                    "art_des": {
                        "S": "ABRAZADERA EMT 2\" ADPS "
                    },
                    "cantidad_empaque": {
                        "N": "0"
                    },
                    "codigoCompania": {
                        "S": "GENERICO2022"
                    },
                    "codigoTienda": {
                        "S": "DLTVA"
                    },
                    "codigo_barra": {
                        "NULL": True
                    },
                    "co_art": {
                        "S": "ACCE13"
                    },
                    "co_lin": {
                        "S": "NO EXISTE"
                    },
                    "created_at": {
                        "S": "2023-04-14T18:52:12.427940Z"
                    },
                    "entity": {
                        "S": "articulos"
                    },
                    "habilitado": {
                        "N": "1"
                    },
                    "iva": {
                        "N": "16"
                    },
                    "marca": {
                        "NULL": True
                    },
                    "moneda": {
                        "N": "2"
                    },
                    "prec_vta1": {
                        "N": "0.4"
                    },
                    "prec_vta2": {
                        "N": "0.48"
                    },
                    "prec_vta3": {
                        "N": "0.53"
                    },
                    "referencia": {
                        "NULL": True
                    },
                    "stock_act": {
                        "N": "10"
                    },
                    "stock_com": {
                        "N": "0"
                    },
                    "tipo": {
                        "S": "TIENDA"
                    },
                    "ubicacion": {
                        "S": "P01"
                    },
                    "unidad": {
                        "S": "PZA"
                    },
                    "unidad_empaque": {
                        "NULL": True
                    },
                    "updated_at": {
                        "S": "2023-04-14T18:52:12.427940Z"
                    },
                    "shopifyGID": {
                        "M": {
                            "producto": {
                                "S": "gid://shopify/Product/8254695604522"
                            },
                            "variante": {
                                "M": {
                                    "id": {
                                        "S": "gid://shopify/ProductVariant/44913176150314"
                                    },
                                    "inventario": {
                                        "S": "gid://shopify/InventoryItem/46984842740010"
                                    }
                                }
                            }
                        }
                    }
                },
                "SequenceNumber": "4911100000000022879305420",
                "SizeBytes": 881,
                "StreamViewType": "NEW_AND_OLD_IMAGES"
            },
            "eventSourceARN": "arn:aws:dynamodb:us-east-2:099375320271:table/angel-db/stream/2023-05-05T14:09:53.915"
        }
    ]

    cambio = {"habilitado": {
        "N": "0"
    }}
    event[0]["dynamodb"]["NewImage"] |= cambio

    event_handler(event, None)

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
                        "S": "GENERICO2022#DLTVA#1005011A1"
                    }
                },
                "NewImage": {
                    "PK": {
                        "S": "GENERICO2022#DLTVA#1005011A1"
                    },
                    "SK": {
                        "S": "METADATA"
                    },
                    "art_des": {
                        "S": "VOLANTE MOTOR CHANA-SAIC"
                    },
                    "codigoCompania": {
                        "S": "GENERICO2022"
                    },
                    "codigoTienda": {
                        "S": "DLTVA"
                    },
                    "co_art": {
                        "S": "1005011A1"
                    },
                    "co_lin": {
                        "S": "10"
                    },
                    "created_at": {
                        "S": "2023-05-18T11:50:26.134847Z"
                    },
                    "entity": {
                        "S": "articulos"
                    },
                    "fx_costos": {
                        "S": "d208b81bcae86d4354120132c9380157"
                    },
                    "habilitado": {
                        "N": "1"
                    },
                    "des_shopify": {
                        "S": "<p>Bienvenido a <strong>DELECTRA</strong> tu proveedor seguro! ⚡⚡</p>"
                    },
                    "imagen_url": {
                        "L": [
                            {
                                "S": "articulo_01R43119R01_876.webp"
                            },
                            {
                                "S": "articulo_020945415AA_425.webp"
                            }
                        ]
                    },
                    "info": {
                        "NULL": True
                    },
                    "iva": {
                        "N": "16"
                    },
                    "marca": {
                        "S": "CHANA"
                    },
                    "modelo": {
                        "S": "CHANA SV/DC"
                    },
                    "moneda": {
                        "N": "2"
                    },
                    "prec_vta1": {
                        "N": "63"
                    },
                    "prec_vta2": {
                        "N": "70"
                    },
                    "prec_vta3": {
                        "N": "83"
                    },
                    "prec_vta4": {
                        "N": "95"
                    },
                    "prec_vta5": {
                        "N": "0"
                    },
                    "prec_vta6": {
                        "N": "0"
                    },
                    "referencia": {
                        "S": "CHASVD0200136"
                    },
                    "stock_act": {
                        "N": "12"
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
                    "unidad": {
                        "S": "PZA"
                    },
                    "updated_at": {
                        "S": "2023-05-18T11:50:26.134847Z"
                    },
                    "shopifyGID": {
                        "M": {
                            "producto": {
                                "S": "gid://shopify/Product/8261363073322"
                            },
                            "variante": {
                                "M": {
                                    "id": {
                                        "S": "gid://shopify/ProductVariant/44944245129514"
                                    },
                                    "inventario": {
                                        "S": "gid://shopify/InventoryItem/47016291336490"
                                    }
                                }
                            },
                            "imagenes": {
                                "M": {
                                    "articulo_01R43119R01_876.webp": {
                                        "S": "gid://shopify/MediaImage/33857652490538"
                                    },
                                    "articulo_020945415AA_425.webp": {
                                        "S": "gid://shopify/MediaImage/33857652523306"
                                    }
                                }
                            }
                        }
                    }
                },
                "OldImage": {
                    "PK": {
                        "S": "GENERICO2022#DLTVA#1005011A1"
                    },
                    "SK": {
                        "S": "METADATA"
                    },
                    "art_des": {
                        "S": "VOLANTE MOTOR CHANA-SAIC"
                    },
                    "codigoCompania": {
                        "S": "GENERICO2022"
                    },
                    "codigoTienda": {
                        "S": "DLTVA"
                    },
                    "co_art": {
                        "S": "1005011A1"
                    },
                    "co_lin": {
                        "S": "10"
                    },
                    "created_at": {
                        "S": "2023-05-18T11:50:26.134847Z"
                    },
                    "entity": {
                        "S": "articulos"
                    },
                    "fx_costos": {
                        "S": "d208b81bcae86d4354120132c9380157"
                    },
                    "habilitado": {
                        "N": "1"
                    },
                    "des_shopify": {
                        "S": "<p>Bienvenido a <strong>DELECTRA</strong> tu proveedor seguro! ⚡⚡</p>"
                    },
                    "imagen_url": {
                        "L": [
                            {
                                "S": "articulo_01R43119R01_876.webp"
                            },
                            {
                                "S": "articulo_020945415AA_425.webp"
                            }
                        ]
                    },
                    "info": {
                        "NULL": True
                    },
                    "iva": {
                        "N": "16"
                    },
                    "marca": {
                        "S": "CHANA"
                    },
                    "modelo": {
                        "S": "CHANA SV/DC"
                    },
                    "moneda": {
                        "N": "2"
                    },
                    "prec_vta1": {
                        "N": "63"
                    },
                    "prec_vta2": {
                        "N": "70"
                    },
                    "prec_vta3": {
                        "N": "83"
                    },
                    "prec_vta4": {
                        "N": "95"
                    },
                    "prec_vta5": {
                        "N": "0"
                    },
                    "prec_vta6": {
                        "N": "0"
                    },
                    "referencia": {
                        "S": "CHASVD0200136"
                    },
                    "stock_act": {
                        "N": "12"
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
                    "unidad": {
                        "S": "PZA"
                    },
                    "updated_at": {
                        "S": "2023-05-18T11:50:26.134847Z"
                    },
                    "shopifyGID": {
                        "M": {
                            "producto": {
                                "S": "gid://shopify/Product/8261363073322"
                            },
                            "variante": {
                                "M": {
                                    "id": {
                                        "S": "gid://shopify/ProductVariant/44944245129514"
                                    },
                                    "inventario": {
                                        "S": "gid://shopify/InventoryItem/47016291336490"
                                    }
                                }
                            },
                            "imagenes": {
                                "M": {
                                    "articulo_01R43119R01_876.webp": {
                                        "S": "gid://shopify/MediaImage/33857652490538"
                                    },
                                    "articulo_020945415AA_425.webp": {
                                        "S": "gid://shopify/MediaImage/33857652523306"
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

    cambio = {"imagen_url": {
        "L": [
            {
                "S": "articulo_01R43119R01_876.webp"
            },
            {
                "S": "articulo_023371101201_146.webp"
            },
            {
                "S": "articulo_0197C5_367.webp"
            }
        ]
    }}
    event[0]["dynamodb"]["NewImage"] |= cambio

    event_handler(event, None)

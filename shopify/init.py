import logging
from shopify.handlers.eventHandler import EventHandler

logging.basicConfig(
    format='%(asctime)s;%(name)-15s;%(levelname)-8s;%(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger("Shopify")


def event_handler(event, context):
    logger.info("*** INICIO LAMBDA SHOPIFY ***")
    r = []
    for e in event:
        try:
            r.append(EventHandler(e).ejecutar())
            logger.debug(r[-1])
        except Exception as err:
            mensaje = ("Ocurrió un error manejado el evento. "
                       f"Se levantó la excepción '{err}'.")
            logger.exception(mensaje)
            logger.debug(f"Evento recibido:\n{e}")
            r.append({"status": "ERROR", "respuesta": mensaje})

    logger.info("*** FIN LAMBDA SHOPIFY ***")
    return r


if __name__ == "__main__":
    event = [
        {
            "eventID": "a47d122d7bfc042520063c173ce48fff",
            "eventName": "INSERT",
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
                    "imagen_url": {
                        "L": [
                            {
                                "S": "articulo_1005011A1_479.webp"
                            },
                            {
                                "S": "articulo_1005011A1_228.webp"
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
                    }
                },
                "SequenceNumber": "4911100000000022879305420",
                "SizeBytes": 881,
                "StreamViewType": "NEW_AND_OLD_IMAGES"
            },
            "eventSourceARN": "arn:aws:dynamodb:us-east-2:099375320271:table/angel-db/stream/2023-05-05T14:09:53.915"
        }
    ]

    # cambio = {"co_lin": {
    #     "S": "11"
    # }}
    # event[0]["dynamodb"]["NewImage"] |= cambio

    event_handler(event, None)

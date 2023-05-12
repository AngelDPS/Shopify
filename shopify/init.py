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
                        "S": "ABRAZADERA EMT 2\"  "
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
                "SequenceNumber": "4911100000000022879305420",
                "SizeBytes": 881,
                "StreamViewType": "NEW_AND_OLD_IMAGES"
            },
            "eventSourceARN": "arn:aws:dynamodb:us-east-2:099375320271:table/angel-db/stream/2023-05-05T14:09:53.915"
        }
    ]

    event_handler(event, None)

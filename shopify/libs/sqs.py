import json
import boto3
from os import environ
from logging import getLogger

logger = getLogger(__name__)
sqs_client = boto3.client("sqs")

SQSURL = environ["SQSURL"]


def receive_messages():
    response = sqs_client.receive_message(
        QueueUrl=SQSURL,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=1,
    )
    logger.warning(f"Se recibieron {len(response.get('Messages', []))} "
                   "eventos NO procesados en cola.")
    return response


def delete_message(id_recepcion):
    sqs_client.delete_message(
        QueueUrl=SQSURL,
        ReceiptHandle=id_recepcion,
    )


def procesar_articulos_repetidos(co_art, lista_co_art, eventos, NewImage):
    if co_art in lista_co_art:
        idx = lista_co_art.index(co_art)
        eventos[idx][0]["dynamodb"].setdefault(
            "OldImage", eventos[idx][0]["dynamodb"]["NewImage"]
        )
        eventos[idx][0]["dynamodb"]["NewImage"] = NewImage
        return idx
    else:
        return None


def process_messages():
    eventos = []
    ids = []
    co_art_vistos = []
    co_art_repetidos = {}

    for n, mensaje in enumerate(receive_messages().get("Messages", [])):
        id_recepcion = mensaje['ReceiptHandle']
        evento = json.loads(mensaje["Body"])
        logger.debug(f"Evento {n} = {evento}")
        co_art = evento[0]["dynamodb"]["NewImage"]["co_art"]["S"]

        if evento[0]["dynamodb"]["NewImage"]["entity"] != {"S": "articulos"}:
            logger.info(f"El evento {n} en cola no puede procesarse y se "
                        "eliminará.")
            delete_message(id_recepcion)
            continue

        if co_art in co_art_vistos:
            logger.info(f"Evento {n} repetido en la cola para {co_art = }")
            if co_art in co_art_repetidos:
                logger.info("El evento ya se había repetido, "
                            "se eliminará el mensaje repetido anterior.")
                delete_message(co_art_repetidos[co_art]["ReceiptHandle"])
            co_art_repetidos[co_art] = {
                "NewImage": evento[0]["dynamodb"]["NewImage"],
                "ReceiptHandle": id_recepcion
            }
        else:
            co_art_vistos.append(co_art)
            eventos.append(evento)
            ids.append(id_recepcion)

    for co_art, co_art_dict in co_art_repetidos.items():
        procesar_articulos_repetidos(co_art, co_art_vistos, eventos,
                                     co_art_dict["NewImage"])

    logger.debug(f'Eventos procesados de la cola = {eventos}')
    return eventos, ids, co_art_vistos, co_art_repetidos


def event_handler(event, context):
    print("Inicio prueba")
    # raise Exception("PRUEBA")
    a, b = process_messages()
    print(f'eventos = {a}, co_arts = {b}')

    print("Finalizo correctamente!!!!!")

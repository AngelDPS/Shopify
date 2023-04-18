from boto3.dynamodb.types import TypeDeserializer
from models.event import Mevent
from handlers.productoHandler import Producto
from handlers.coleccionHandler import Coleccion
from handlers.sucursalHandler import Sucursal
from json import load
from logging import getLogger

logger = getLogger("Shopify.eventHandler")


def obtenerConfiguracion(compañia: str):
    DBpath = f"DB/{compañia}.json"
    with open(DBpath) as DBfile:
        return load(DBfile)["config"]


def deserializar(dynamoDB: dict):
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamoDB.items()}


def formatearEvento(evento: list):
    resultado = evento[0]
    resultado['dynamodb']['NewImage'] = deserializar(
        resultado['dynamodb']['NewImage']
    )
    if resultado['dynamodb'].get('OldImage'):
        resultado['dynamodb']['OldImage'] = deserializar(
            resultado['dynamodb']['OldImage']
        )
    resultado['config'] = obtenerConfiguracion(
        resultado['dynamodb']['NewImage']['codigoCompania']
    )
    return Mevent.parse_obj(resultado)


def procesarEvento(evento: list):
    evento_f = formatearEvento(evento)
    logger.debug(evento_f)
    Handler = {
        'articulos': Producto,
        'lineas': Coleccion,
        'tiendas': Sucursal
    }[evento_f.dynamodb.NewImage.entity]
    Handler(evento_f)

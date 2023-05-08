from libs.custom_log import getLogger
from handlers.eventoHandler import Evento
import eventos
from time import process_time

log = getLogger('Shopify')


def crearArticulo():
    return Evento(eventos.ARTICULO[0]).ejecutar()


def modificarArticulo(cambios: dict):
    evento = eventos.ARTICULO_act[0]
    evento["dynamodb"]["NewImage"] |= cambios
    return Evento(evento).ejecutar()


if __name__ == '__main__':
    cambios = {
        "marca": {
            "S": "ACME"
        }
    }
    modificarArticulo(cambios)
    log.debug(process_time())

NewImage = {
    "stock_com": {
        "N": "0"
    },
    "prec_vta2": {
        "N": "0.48"
    },
    "co_lin": {
        "S": "10"
    },
    "codigoTienda": {
        "S": "DLTVA"
    },
    "habilitado": {
        "N": "1"
    },
    "art_des": {
        "S": "ABRAZADERA EMT 2\"  "
    },
    "codigo_barra": {
        "NULL": True
    },
    "referencia": {
        "NULL": True
    },
    "marca": {
        "NULL": True
    }
}

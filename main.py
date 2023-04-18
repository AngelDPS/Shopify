from libs.custom_log import getLogger
from handlers.eventHandler import procesarEvento
import eventos

getLogger('Shopify')


def crearSucursal():
    procesarEvento(eventos.TIENDA)


def actualizarSucursal():
    procesarEvento(eventos.TIENDA_act)


def crearLinea():
    procesarEvento(eventos.LINEA)


def actualizarLinea():
    procesarEvento(eventos.LINEA_act)


def crearArticulo():
    procesarEvento(eventos.ARTICULO)


def actualizarArticulo():
    procesarEvento(eventos.ARTICULO_act)


if __name__ == '__main__':
    crearSucursal()
    crearLinea()
    crearArticulo()
    actualizarSucursal()
    actualizarLinea()
    actualizarArticulo()

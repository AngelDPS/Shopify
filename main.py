from libs.custom_log import getLogger
from handlers.eventoHandler import Evento
import eventos

getLogger('Shopify')


def crearTienda():
    Evento(eventos.TIENDA).procesar()


def actualizarTienda():
    Evento(eventos.TIENDA_act).procesar()


def crearLinea():
    Evento(eventos.LINEA).procesar()


def actualizarLinea():
    Evento(eventos.LINEA_act).procesar()


def crearArticulo():
    Evento(eventos.ARTICULO).procesar()


def actualizarArticulo():
    Evento(eventos.ARTICULO_act).procesar()


def crearTodo():
    crearTienda()
    crearLinea()
    crearArticulo()


def actualizarTodo():
    actualizarTienda()
    actualizarLinea()
    actualizarArticulo()


if __name__ == '__main__':
    actualizarTodo()

from libs.custom_log import getLogger
from handlers.eventoHandler import Evento
import eventos

getLogger('Shopify')


def crearTienda():
    Evento(eventos.TIENDA).ejecutar()


def actualizarTienda():
    Evento(eventos.TIENDA_act).ejecutar()


def crearLinea():
    Evento(eventos.LINEA[0]).ejecutar()


def actualizarLinea():
    Evento(eventos.LINEA_act[0]).ejecutar()


def crearArticulo():
    Evento(eventos.ARTICULO[0]).ejecutar()


def actualizarArticulo():
    Evento(eventos.ARTICULO_act[0]).ejecutar()


def crearTodo():
    crearLinea()
    crearArticulo()


def actualizarTodo():
    actualizarLinea()
    actualizarArticulo()


if __name__ == '__main__':
    crearArticulo()

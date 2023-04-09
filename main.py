from libs.custom_log import getLogger
from libs.conexion import ConexionShopify
from handlers.sucursalHandler import Sucursal
from handlers.collectionHandler import Coleccion

logger = getLogger('Shopify')


def infoTienda():
    with open('graphql/Info.graphql', 'r') as query:
        return ConexionShopify().enviarConsulta(query.read())


def crearSucursalPrueba():
    input = {
        'name': 'Sucursal de prueba',
        'fulfillsOnlineOrders': True,
        'address': {
            'countryCode': 'VE',
            'city': 'Valencia',
            'address1': 'Av. Bolívar Norte',
            'address2': 'Torre Banaven',
            'zip': '2001',
            'provinceCode': 'VE-G',
            'phone': '+584145834842'
        }
    }
    s = Sucursal(input=input)
    return s


def accerderColeccion(id: str = "gid://shopify/Collection/441266503978") -> Coleccion:
    return Coleccion(id=id)


def crearColeccionPrueba():
    input = {
        'title': 'Creada desde python',
        'descriptionHtml': 'Colección de prueba creada desde <b>python</b>.',
        'sortOrder': 'ALPHA_ASC'
    }
    return Coleccion(input=input)


def main():
    c = crearColeccionPrueba()
    print(c)


if __name__ == '__main__':
    main()

from libs.custom_log import getLogger
from libs.conexion import ConexionShopify
from handlers.sucursalHandler import Sucursal

logger = getLogger('Shopify')
conexion = ConexionShopify()


def infoTienda():
    with open('graphql/Info.graphql', 'r') as query:
        return conexion.enviarConsulta(query.read())


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
    s = Sucursal(conexion=conexion, input=input)
    return s


def main():
    s = crearSucursalPrueba()
    print(s.ID, s.NOMBRE)
    s.eliminar()
    print(s.ID, s.NOMBRE)


if __name__ == '__main__':
    main()

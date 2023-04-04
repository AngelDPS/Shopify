from libs.custom_log import getLogger
from credentials import access_token
from libs.generico2022 import Generico2022

logger = getLogger('Shopify')
tienda = Generico2022(access_token=access_token)


def infoTienda():
    return tienda.get_info


def crearSucursalPrueba():
    tienda.crearSucursal(nombre='Sucursal de prueba', codigoPais='VE', 
                         atiendeOrdenes=True, ciudad='Valencia', 
                         direccion1='Av. Bolívar Norte', direccion2='Torre Banaven', 
                         codigoPostal='2001', provincia='VE-G', 
                         telefono='+584145834842')
    return tienda.sucursales


def main():
    sucursales = crearSucursalPrueba()
    print(sucursales)


if __name__ == '__main__':
    main()
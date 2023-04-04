from models.sucursal import MsucursalInput


class SucursalInput:
    sucursalInput: MsucursalInput

    def __init__(self, nombre: str, 
                 codigoPais: str,
                 atiendeOrdenes: bool = None, 
                 provincia: str = None,
                 ciudad: str = None,
                 direccion1: str = None,
                 direccion2: str = None,
                 telefono: str = None,
                 codigoPostal: str = None):
                 
                 self.sucursalInput = MsucursalInput(
                    name=nombre,
                    fulfillsOnlineOrders=atiendeOrdenes,
                    address={
                        'countryCode': codigoPais,
                        'provinceCode': provincia,
                        'city': ciudad,
                        'address1': direccion1,
                        'address2': direccion2,
                        'phone': telefono,
                        'zip': codigoPostal
                    }
                 )
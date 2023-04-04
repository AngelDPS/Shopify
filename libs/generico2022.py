import logging
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from handlers.sucursalHandler import SucursalInput

logger = logging.getLogger('Shopify.generico2022')


class Generico2022:
    shop: str = 'generico2022-8056'
    api_version: str = '2023-01'
    url: str = f'https://{shop}.myshopify.com/admin/api/{api_version}/graphql.json'
    client: Client
    sucursales: dict = {}

    def __init__(self, access_token: str):
        transport = RequestsHTTPTransport(url=self.url, 
                                          headers={'X-Shopify-Access-Token': access_token})
        self.client = Client(transport=transport, fetch_schema_from_transport=True)


    @property
    def get_info(self) -> dict:
        query = gql('''
            {
                shop {
                    name
                    id
                }
            }
        ''')
        return self.client.execute(query)


    def crearSucursal(self,
                      nombre: str, 
                      codigoPais: str,
                      atiendeOrdenes: bool = None, 
                      provincia: str = None,
                      ciudad: str = None,
                      direccion1: str = None,
                      direccion2: str = None,
                      telefono: str = None,
                      codigoPostal: str = None) -> dict:

        input = SucursalInput(nombre=nombre, 
                              codigoPais=codigoPais, 
                              atiendeOrdenes=atiendeOrdenes,
                              provincia=provincia,
                              ciudad=ciudad,
                              direccion1=direccion1,
                              direccion2=direccion2,
                              telefono=telefono,
                              codigoPostal=codigoPostal)

        input = {
            'input': input.sucursalInput.dict()
        }
        
        query = gql('''
            mutation LocationAdd($input: LocationAddInput!) {
                locationAdd(input: $input) {
                    location {
                        id
                    }
                }
            }
        ''')

        respuesta = self.client.execute(query, variable_values=input) 
        self.sucursales[nombre] = respuesta['locationAdd']['location']['id']
        return self.sucursales[nombre]
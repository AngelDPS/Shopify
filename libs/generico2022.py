import logging
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

logger = logging.getLogger('Shopify.generico2022')


class Generico2022:
    shop = 'generico2022-8056'
    api_version = '2023-01'
    url = f'https://{shop}.myshopify.com/admin/api/{api_version}/graphql.json'

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


    def crearSucursal(access_token: str, 
                      country_code: str,
                      address1: str = '', 
                      city: str = '',
                      province_code: str = '',
                      zip_code: str = '',
                      fulfillsOnlineOrders: bool = '',
                      name: str = '') -> dict:
        with shopify.Session.temp(url, api_version, access_token):
            query_str = '''
                mutation locationAdd($input: LocationAddInput!) {
                    locationAdd(input: $input) {
                        location {
                            id
                        }
                    }
                }
            '''
            variables = {
                'input': {
                    'address': {
                        'address1': address1,
                        'city': city,
                        'countryCode': country_code,
                        'provinceCode': province_code,
                        'zip': zip_code
                    },
                    'fulfillsOnlineOrders': fulfillsOnlineOrders,
                    'name': name
                }
            }

            return shopify.GraphQL().execute(query=query_str, 
                                            variables=variables) 
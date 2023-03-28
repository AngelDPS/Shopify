import logging
import shopify

logger = logging.getLogger('Shopify.tiendaAngel')

url = 'tienda-angel-4273.myshopify.com'
api_version = '2023-01'

def getShopInfo(access_token: str) -> dict:
    with shopify.Session.temp(url, api_version, access_token):
        query_str = '''
            {
                shop {
                    name
                    id
                }
            }
        '''
        return shopify.GraphQL().execute(query_str)

from libs.custom_log import getLogger
from credentials import access_token
from libs.generico2022 import Generico2022

logger = getLogger('Shopify')

tienda = Generico2022(access_token=access_token)

print(tienda.get_info)
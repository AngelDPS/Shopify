from libs.custom_log import getLogger
from credentials import access_token
import libs.tiendaAngel

logger = getLogger('Shopify')

print(libs.tiendaAngel.getShopInfo(access_token))
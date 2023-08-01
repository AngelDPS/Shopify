from libs.conexion import ClienteShopify
from libs.util import ItemHandler
from libs.dynamodb import (
    guardar_tienda_id
)
from models.sucursal import MSucursalAddInput
from models.evento import Mtienda
import re
from aws_lambda_powertools import Logger

logger = Logger(child=True, service="shopify")


def shopify_obtener_id(nombre: str, client: ClienteShopify = None) -> str:
    try:
        client = client or ClienteShopify()
        return client.execute(
            """
            query Tienda($nombre: String) {
                locations(first: 1, query: $nombre) {
                    nodes {
                        id
                    }
                }
            }
            """,
            variables={"nombre": f"name:{nombre}"}
        )['locations']['nodes'][0]['id']
    except Exception:
        logger.exception("Error al consultar el GID de sucursal.")
        raise


def shopify_crear_sucursal(sucursal_input: MSucursalAddInput,
                           client: ClienteShopify = None) -> str:
    try:
        client = client or ClienteShopify()
        return client.execute(
            """
            mutation crearSucursal($input: LocationAddInput!) {
                locationAdd(input: $input) {
                    location {
                        id
                    }
                    userErrors {
                        message
                    }
                }
            }
            """,
            variables={"input": sucursal_input.dict(exclude_none=True)}
        )['locationAdd']['location']['id']
    except Exception:
        logger.exception("Error al crear la sucursal en Shopify.")
        raise


def procesar_direccion(direccion: str) -> dict:
    ISO_3166_2_VE = {
        'Distrito Capital': 'VE-A',
        'Anzoátegui': 'VE-B',
        'Apure': 'VE-C',
        'Aragua': 'VE-D',
        'Barinas': 'VE-E',
        'Bolívar': 'VE-F',
        'Carabobo': 'VE-G',
        'Cojedes': 'VE-H',
        'Falcón': 'VE-I',
        'Guárico': 'VE-J',
        'Lara': 'VE-K',
        'Mérida': 'VE-L',
        'Miranda': 'VE-M',
        'Monagas': 'VE-N',
        'Nueva Esparta': 'VE-O',
        'Portuguesa': 'VE-P',
        'Sucre': 'VE-R',
        'Táchira': 'VE-S',
        'Trujillo': 'VE-T',
        'Yaracuy': 'VE-U',
        'Zulia': 'VE-V',
        'Dependencias Federales': 'VE-W',
        'La Guaira': 'VE-X',
        'Delta Amacuro': 'VE-Y',
        'Amazonas': 'VE-Z'
    }
    pattern = (r"^(?P<address1>.*)\s(?P<city>\w+), "
               r"Edo.\s(?P<province>[\w\s]+)$")
    coincidencias = (re.match(pattern, direccion).groupdict())
    coincidencias['provinceCode'] = ISO_3166_2_VE[coincidencias['province']]

    return coincidencias


class SucursalHandler(ItemHandler):
    item = "sucursal"

    def __init__(self, evento, client: ClienteShopify = None):
        self.old_image = evento.old_image
        if "shopify_id" in self.old_image:
            self.old_image["shopify_id"] = (
                self.old_image["shopify_id"].get("sucursal")
            )
        self.old_image = Mtienda.parse_obj(evento.old_image)
        self.cambios = evento.cambios
        self.cambios.pop("shopify_id", None)
        self.cambios = Mtienda.parse_obj(self.cambios)
        self.client = client or ClienteShopify()
        self.session = None

    @classmethod
    def desde_tienda(cls, tienda: dict, client: ClienteShopify = None):
        evento = type("evento", (), {
            "cambios": tienda,
            "old_image": {}
        })
        return cls(evento, client)

    def guardar_id_dynamo(self):
        logger.info("Guardando GID de sucursal en Dynamo.")
        guardar_tienda_id(
            self.cambios.codigoCompania or self.old_image.codigoCompania,
            self.cambios.codigoTienda or self.old_image.codigoTienda,
            self.old_image.shopify_id
        )

    def crear(self):
        logger.info("Creando sucursal a partir de tienda.")

        try:
            location_input = MSucursalAddInput(
                name=self.cambios.nombre,
                address={
                    **procesar_direccion(self.cambios.direccion),
                    'phone': self.cambios.telefono
                }
            )
            self.old_image.shopify_id = shopify_crear_sucursal(
                location_input,
                self.session or self.client
            )
            self.guardar_id_dynamo()
            logger.info("Sucursal creada.")
        except Exception:
            logger.info("Error al crear la sucursal.")
            raise

    def modificar(self):
        pass

    def ejecutar(self):
        try:
            with self.client as self.session:
                if not self.old_image.shopify_id and self.old_image.nombre:
                    try:
                        self.old_image.shopify_id = shopify_obtener_id(
                            self.old_image.nombre,
                            self.session
                        )
                        self.guardar_id_dynamo()
                    except IndexError:
                        pass
                respuesta = super().ejecutar(
                    "Shopify",
                    self.cambios.shopify_id or self.old_image.shopify_id
                )
                return respuesta
        except Exception:
            logger.info("Error al ejecutar el handler de sucursal.")
            raise

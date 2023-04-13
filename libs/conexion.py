import logging
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import (
    TransportQueryError,
    TransportServerError
)
from graphql.language.ast import DocumentNode
from credentials import shop, access_token


class ConexionShopify:
    _ACCESS_TOKEN: str = access_token
    SHOP: str = shop
    API_VERSION: str = "2023-04"
    URL: str = (f"https://{SHOP}.myshopify.com/admin/api/"
                f"{API_VERSION}/graphql.json")
    cliente: Client

    def __init__(self):
        self.logger = logging.getLogger("Shopify.Conexion")
        self.logger.info("Creando una instancia de Conexión")

        transport = RequestsHTTPTransport(
            self.URL,
            headers={'X-Shopify-Access-Token': self._ACCESS_TOKEN},
            retries=3,
        )

        self.cliente = Client(
            transport=transport,
            fetch_schema_from_transport=True
        )

    def enviarConsulta(self,
                       request: DocumentNode,
                       variables: dict = None,
                       operacion: str = None
                       ) -> dict:
        try:
            self.respuesta = self.cliente.execute(
                request,
                variable_values=variables,
                operation_name=operacion
            )
        except TransportQueryError as err:
            self.logger.exception(
                "Hubo un problema con la consulta, "
                f"el servidor retornó un error {err}.",
                stack_info=True
            )
            raise
        except TransportServerError as err:
            self.logger.exception(
                "Hubo un problema con el servidor, "
                f"retornó un código {err.code}",
                stack_info=True
            )
            raise
        except Exception as err:
            self.logger.exception(
                f"Se encontró un error inesperado.\n{type(err)}\n{err}",
                stack_info=True
            )
            raise
        else:
            self.logger.info("Consulta realizada exitosamente.")
            self.logger.debug(f"{self.respuesta}")
        return self.respuesta

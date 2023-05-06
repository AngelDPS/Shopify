import logging
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import (
    TransportQueryError,
    TransportServerError
)
from graphql.language.ast import DocumentNode


class ConexionShopify:
    _access_token: str
    shop: str
    API_VERSION: str = "2023-04"
    cliente: Client

    def __init__(self, shopifyConfig: dict):
        """Constructor del objeto que utiliza la información de configuración
        para establecer la conexión con el servidor de GraphQL.

        Args:
            shopifyConfig (dict): Información para la conexión con el 
            servidor graphQL de la tienda en Shopify.
        """
        self.shop = shopifyConfig['tienda']
        self.URL: str = (f"https://{self.shop}.myshopify.com/admin/api/"
                         f"{self.API_VERSION}/graphql.json")
        self.logger = logging.getLogger("Shopify.Conexion")
        self.logger.info("Creando una instancia de Conexión")

        transport = RequestsHTTPTransport(
            self.URL,
            headers={'X-Shopify-Access-Token': shopifyConfig['access_token']},
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
        """Envía una consulta de GraphQL usando el transporte inicializado en
        la instancia.

        Args:
            request (DocumentNode): Consulta de graphQL procesada
            variables (dict, optional): Variables que 'request' puede utilizar
            para realizar la consulta. Defaults to None.
            operacion (str, optional): Si 'request' esta compuesta de varias
            operaciones posibles. 'operacion' selecciona la que se va a
            utilizar. Defaults to None.

        Returns:
            dict: Json deseralizado recibido como respuesta a la consulta.
        """
        try:
            self.respuesta = self.cliente.execute(
                request,
                variable_values=variables,
                operation_name=operacion
            )
            self.logger.info("Consulta realizada exitosamente.")
            self.logger.debug(f"{self.respuesta = }")
            return self.respuesta
        except TransportQueryError as err:
            self.logger.exception(
                "Hubo un problema con la consulta, "
                f"el servidor retornó un error {err}.",
                stack_info=True
            )
            err.add_note("Hubo un problema con la consulta de GraphQL")
            raise
        except TransportServerError as err:
            self.logger.exception(
                "Hubo un problema con el servidor, "
                f"retornó un código {err.code}",
                stack_info=True
            )
            err.add_note("Hubo un problema con el servidor de GraphQL")
            raise
        except Exception as err:
            self.logger.exception(
                f"Se encontró un error inesperado.\n{type(err)}\n{err}",
                stack_info=True
            )
            err.add_note("Hubo un problema realizando una consulta de GraphQL")
            raise

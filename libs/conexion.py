import logging
from gql import Client  # , gql
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import (
    TransportQueryError,
    TransportServerError
)
import os

logger = logging.getLogger('Shopify.Conexion')


def get_config() -> dict:
    config = {
        'shop': os.environ['SHOPIFY_SHOP'],
        'access_token': os.environ['SHOPIFY_ACCESS_TOKEN']
    }
    return config


class ConexionShopify(Client):
    API_VERSION: str = "2023-04"

    def __init__(self, request_string: str):
        """Constructor del objeto que utiliza la información de configuración
        para establecer la conexión con el servidor de GraphQL.

        Args:
            request_string (str): _description_
        """
        # self.gqlrequests = gql(request_string)
        config = get_config()
        self.URL: str = (f"https://{config['shop']}.myshopify.com/admin/api/"
                         f"{self.API_VERSION}/graphql.json")

        transport = RequestsHTTPTransport(
            self.URL,
            headers={'X-Shopify-Access-Token': config['access_token']},
            retries=3,
        )

        super().__init__(
            transport=transport  # , fetch_schema_from_transport=True
        )
        logger.info("Instancia de ConexionShopify creada.")

    def execute(self,
                request,
                operacion: str = None,
                variables: dict = None
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
        logger.debug(f'{variables = }')
        try:
            self.respuesta = super().execute(
                request,
                variable_values=variables,
                operation_name=operacion
            )
            logger.info("Consulta realizada exitosamente.")
            logger.debug(f"{self.respuesta = }")
        except TransportQueryError as err:
            logger.exception(
                "Hubo un problema con la consulta, "
                f"el servidor retornó un error {err}."
            )
            err.add_note("Hubo un problema con la consulta de GraphQL")
            raise
        except TransportServerError as err:
            logger.exception(
                "Hubo un problema con el servidor, "
                f"retornó un código {err.code}",
                stack_info=True
            )
            err.add_note("Hubo un problema con el servidor de GraphQL")
            raise
        except Exception as err:
            logger.exception(
                f"Se encontró un error inesperado.\n{type(err)}\n{err}",
                stack_info=True
            )
            err.add_note("Hubo un problema realizando una consulta de GraphQL")
            raise
        else:
            if self.respuesta[list(self.respuesta)[0]].get("userErrors"):
                msg = ("No fue posible realizar la operación:\n"
                       f"{self.respuesta['userErrors']}")
                logger.exception(msg)
                raise RuntimeError(msg)
            return self.respuesta

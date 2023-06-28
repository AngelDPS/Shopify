from logging import getLogger
from gql import Client, gql
from gql.client import SyncClientSession
from gql.transport.async_transport import AsyncTransport
from gql.transport.requests import RequestsHTTPTransport
from libs.util import get_parameter

logger = getLogger("shopify.conexion")


class ClienteShopify(Client):
    API_VERSION: str = "2023-04"
    URL = (f"https://{get_parameter('SHOPIFY_SHOP')}.myshopify.com/"
           f"admin/api/{API_VERSION}/graphql.json")

    def __init__(self):
        transport = RequestsHTTPTransport(
            self.URL,
            headers={
                'X-Shopify-Access-Token': get_parameter('SHOPIFY_ACCESS_TOKEN')
            },
            retries=3,
            timeout=(3.05, 5)
        )
        super().__init__(transport=transport)

    def execute(self, request_str, variables=None, operacion=None,
                **kwargs) -> dict:
        logger.debug(f'{variables = }')
        respuesta = super().execute(gql(request_str),
                                    variable_values=variables,
                                    operation_name=operacion,
                                    **kwargs)
        logger.debug(f"{respuesta = }")
        if respuesta[list(respuesta)[0]].get("userErrors"):
            msg = ("No fue posible realizar la operación:\n"
                   f"{respuesta[list(respuesta)[0]]['userErrors']}")
            logger.exception(msg)
            raise RuntimeError(msg)
        return respuesta
        # except TransportQueryError as err:
        #     logger.exception(
        #         "Hubo un problema con la consulta, "
        #         f"el servidor retornó un error {err}."
        #     )
        #     raise
        # except TransportServerError as err:
        #     logger.exception(
        #         "Hubo un problema con el servidor, "
        #         f"retornó un código {err.code}"
        #     )
        #     raise
        # except Exception as err:
        #     logger.exception(
        #         f"Se encontró un error inesperado.\n{type(err)}\n{err}"
        #     )
        #     raise

    def connect_sync(self):
        r"""Connect synchronously with the underlying sync transport to
        produce a session.

        If you call this method, you should call the
        :meth:`close_sync <gql.client.Client.close_sync>` method
        for cleanup.
        """

        if isinstance(self.transport, AsyncTransport):
            raise TypeError(
                "Only a sync transport can be used."
                " Use 'async with Client(...) as session:' instead"
            )

        self.transport.connect()

        if not hasattr(self, "session"):
            self.session = CustomSyncClientSession(client=self)

        # Get schema from transport if needed
        try:
            if self.fetch_schema_from_transport and not self.schema:
                self.session.fetch_schema()
        except Exception:
            # we don't know what type of exception is thrown here because it
            # depends on the underlying transport; we just make sure that the
            # transport is closed and re-raise the exception
            self.transport.close()
            raise

        return self.session


class CustomSyncClientSession(SyncClientSession):

    def execute(self, request_str, variables=None, operacion=None,
                **kwargs) -> dict:
        logger.debug(f'{variables = }')
        respuesta = super().execute(gql(request_str),
                                    variable_values=variables,
                                    operation_name=operacion,
                                    get_execution_result=True,
                                    **kwargs)
        extensions = respuesta.extensions
        respuesta = respuesta.data
        logger.debug(f"{respuesta = }")
        logger.debug(f"{extensions = }")
        if respuesta[list(respuesta)[0]].get("userErrors"):
            msg = ("No fue posible realizar la operación:\n"
                   f"{respuesta[list(respuesta)[0]]['userErrors']}")
            logger.exception(msg)
            raise RuntimeError(msg)
        return respuesta


def obtenerGidPublicaciones(
    client: ClienteShopify | CustomSyncClientSession = None
):
    client = client or ClienteShopify()
    pubIDs = [i["id"] for i in
              client.execute(
        """
                query obtenerPublicaciones {
                    publications(first: 2) {
                        nodes {
                            id
                        }
                    }
                }
        """
    )['publications']['nodes']]
    return pubIDs


def publicarRecurso(GID: str, pubIDs: list[str],
                    client: ClienteShopify | CustomSyncClientSession = None):
    try:
        client.execute(
            """
            mutation publicar($id: ID!, $input: [PublicationInput!]!) {
                publishablePublish(id: $id, input: $input) {
                    userErrors {
                        message
                    }
                }
            }
            """,
            variables={
                'id': GID,
                'input': [{"publicationId": id}
                          for id in pubIDs]
            }
        )
        logger.info("Publicación exitosa del recurso.")
    except Exception:
        logger.exception("No se pudo publicar el recurso.")
        raise

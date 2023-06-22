import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from os import getenv
from logging import getLogger

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table(f"{getenv('NOMBRE_COMPANIA')}-db")
logger = getLogger(__name__)


def actualizarGidArticulo(PK: str, SK: str, GID: str):
    tabla.update_item(
        Key={"PK": PK, "SK": SK},
        UpdateExpression="SET shopifyGID = :productID",
        ExpressionAttributeValues={":productID": GID}
    )


def obtenerTienda(codigoCompania: str, codigoTienda: str
                  ) -> dict[str, dict[str, str]]:
    """Función para obtener la data de la tienda dada por codigoTienda.
    """
    key = {
        "PK": f"{codigoCompania.upper()}#TIENDAS",
        "SK": f"T#{codigoTienda.upper()}"
    }
    return tabla.get_item(
        Key=key
    )['Item']


def obtenerGidTienda(codigoCompania: str, codigoTienda: str
                     ) -> dict[str, dict[str, str]]:
    """Función para obtener el GID asociado a codigoTienda.

    Args:
        use_old (bool): Booleano usado para indicar si se utiliza
        OldImage para extraer el codigo de tienda del artículo

    Returns:
        str: El GID de shopify asociado al código de tienda del artículo.
    """
    key = {
        "PK": f"{codigoCompania.upper()}#TIENDAS",
        "SK": f"T#{codigoTienda.upper()}"
    }
    return tabla.get_item(
        Key=key,
        ProjectionExpression="shopifyGID.sucursal"
    )['Item']


def obtenerNombreTienda(codigoCompania: str, codigoTienda: str
                        ) -> dict[str, str]:
    """Función para obtener el GID asociado a codigoTienda.

    Args:
        use_old (bool): Booleano usado para indicar si se utiliza
        OldImage para extraer el codigo de tienda del artículo

    Returns:
        str: El GID de shopify asociado al código de tienda del artículo.
    """
    key = {
        "PK": f"{codigoCompania.upper()}#TIENDAS",
        "SK": f"T#{codigoTienda.upper()}"
    }
    return tabla.get_item(
        Key=key,
        ProjectionExpression="nombre"
    )['Item']


def actualizarGidTienda(codigoCompania: str, codigoTienda: str, GID: str):
    key = {
        "PK": f"{codigoCompania.upper()}#TIENDAS",
        "SK": f"T#{codigoTienda.upper()}"
    }
    try:
        tabla.update_item(
            Key=key,
            UpdateExpression="SET shopifyGID.sucursal = :gid",
            ExpressionAttributeValues={
                ":gid": GID
            }
        )
    except ClientError as err:
        if err.response['Error']['Code'] == 'ValidationException':
            tabla.update_item(
                Key=key,
                UpdateExpression="SET shopifyGID = :gid",
                ExpressionAttributeValues={
                    ":gid": {
                        "sucursal": GID
                    }
                }
            )
        else:
            raise


def obtenerGidLinea(codigoCompania: str, codigoTienda: str,
                    co_lin: str) -> dict[str, str]:
    key = {
        "PK": f"{codigoCompania.upper()}#LINEAS",
        "SK": f"T#{codigoTienda}#L#{co_lin}"
    }
    return tabla.get_item(
        Key=key,
        ProjectionExpression="shopifyGID"
    )['Item']


def actualizarGidLinea(PK: str, SK: str, GID: str):
    tabla.update_item(
        Key={"PK": PK, "SK": SK},
        UpdateExpression="SET shopifyGID = :gid",
        ExpressionAttributeValues={
            ":gid": GID
        }
    )


def obtenerLinea(codigoCompania: str, codigoTienda: str,
                 co_lin: str) -> dict[str, any]:
    key = {
        "PK": f"{codigoCompania.upper()}#LINEAS",
        "SK": f"T#{codigoTienda}#L#{co_lin}"
    }
    return tabla.get_item(
        Key=key
    )['Item']


def obtenerGidPublicacionesTienda(codigoCompania: str, codigoTienda: str
                                  ) -> dict[str, dict[str, str]]:
    key = {
        "PK": f"{codigoCompania.upper()}#TIENDAS",
        "SK": f"T#{codigoTienda.upper()}"
    }
    return tabla.get_item(
        Key=key,
        ProjectionExpression="shopifyGID.publicaciones"
    )['Item']


def actualizarGidPublicacionesTienda(codigoCompania: str, codigoTienda: str,
                                     pubIDs: list[str]):
    key = {
        "PK": f"{codigoCompania.upper()}#TIENDAS",
        "SK": f"T#{codigoTienda.upper()}"
    }
    try:
        tabla.update_item(
            Key=key,
            UpdateExpression="SET shopifyGID.publicaciones = :pubIDs",
            ExpressionAttributeValues={
                ":pubIDs": pubIDs
            }
        )
    except ClientError as err:
        if err.response['Error']['Code'] == 'ValidationException':
            tabla.update_item(
                Key=key,
                UpdateExpression="SET shopifyGID = :pubIDs",
                ExpressionAttributeValues={
                    ":pubIDs": {
                        "publicaciones": pubIDs
                    }
                }
            )
        else:
            raise


def consultarArticulos(co_art: str, codigoTienda: str):
    respuesta = tabla.scan(
        FilterExpression=(
            Attr("co_art").eq(co_art) & Attr("codigoTienda").ne(codigoTienda)
        )
    )
    return respuesta

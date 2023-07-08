import boto3
from botocore.exceptions import ClientError
from os import getenv
from logging import getLogger

logger = getLogger("shopify.dynamodb")


def obtener_tabla():
    if getenv('ENV') == 'local':
        session = boto3.Session(profile_name='angel')
    else:
        session = boto3
    return (
        session.resource("dynamodb").Table(f"{getenv('NOMBRE_COMPANIA')}-db")
    )


def guardar_articulo_id(PK: str, SK: str, GID: str):
    obtener_tabla().update_item(
        Key={"PK": PK, "SK": SK},
        UpdateExpression="SET shopify_id = :productID",
        ExpressionAttributeValues={":productID": GID}
    )


def obtener_tienda(codigoCompania: str, codigoTienda: str
                   ) -> dict[str, dict[str, str]]:
    """Función para obtener la data de la tienda dada por codigoTienda.
    """
    key = {
        "PK": f"{codigoCompania.upper()}#TIENDAS",
        "SK": f"T#{codigoTienda.upper()}"
    }
    return obtener_tabla().get_item(
        Key=key
    )['Item']


def guardar_tienda_id(codigoCompania: str, codigoTienda: str, GID: str):
    key = {
        "PK": f"{codigoCompania.upper()}#TIENDAS",
        "SK": f"T#{codigoTienda.upper()}"
    }
    try:
        tabla = obtener_tabla()
        tabla.update_item(
            Key=key,
            UpdateExpression="SET shopify_id.sucursal = :gid",
            ExpressionAttributeValues={
                ":gid": GID
            }
        )
    except ClientError as err:
        if err.response['Error']['Code'] == 'ValidationException':
            tabla.update_item(
                Key=key,
                UpdateExpression="SET shopify_id = :gid",
                ExpressionAttributeValues={
                    ":gid": {
                        "sucursal": GID
                    }
                }
            )
        else:
            raise


def guardar_linea_id(PK: str, SK: str, GID: str):
    obtener_tabla().update_item(
        Key={"PK": PK, "SK": SK},
        UpdateExpression="SET shopify_id = :gid",
        ExpressionAttributeValues={
            ":gid": GID
        }
    )


def obtener_linea(codigoCompania: str, codigoTienda: str,
                  co_lin: str) -> dict[str, any]:
    key = {
        "PK": f"{codigoCompania.upper()}#LINEAS",
        "SK": f"T#{codigoTienda}#L#{co_lin}"
    }
    return obtener_tabla().get_item(
        Key=key
    )['Item']


def guardar_publicaciones_id(codigoCompania: str, codigoTienda: str,
                             pubIDs: list[str]):
    key = {
        "PK": f"{codigoCompania.upper()}#TIENDAS",
        "SK": f"T#{codigoTienda.upper()}"
    }
    try:
        tabla = obtener_tabla()
        tabla.update_item(
            Key=key,
            UpdateExpression="SET shopify_id.publicaciones = :pubIDs",
            ExpressionAttributeValues={
                ":pubIDs": pubIDs
            }
        )
    except ClientError as err:
        if err.response['Error']['Code'] == 'ValidationException':
            tabla.update_item(
                Key=key,
                UpdateExpression="SET shopify_id = :pubIDs",
                ExpressionAttributeValues={
                    ":pubIDs": {
                        "publicaciones": pubIDs
                    }
                }
            )
        else:
            raise

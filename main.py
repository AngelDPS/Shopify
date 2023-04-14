from libs.custom_log import getLogger
from libs.conexion import ConexionShopify
from handlers.sucursalHandler import Sucursal
from handlers.collectionHandler import Coleccion

logger = getLogger('Shopify')


def infoTienda():
    with open('graphql/Info.graphql', 'r') as query:
        return ConexionShopify().enviarConsulta(query.read())


def crearSucursalPrueba():
    input = {
        'name': 'Sucursal de prueba',
        'fulfillsOnlineOrders': True,
        'address': {
            'countryCode': 'VE',
            'city': 'Valencia',
            'address1': 'Av. Bolívar Norte',
            'address2': 'Torre Banaven',
            'zip': '2001',
            'provinceCode': 'VE-G',
            'phone': '+584145834842'
        }
    }
    s = Sucursal(input=input)
    return s


def accerderColeccion(id: str) -> Coleccion:
    return Coleccion(id=id)


def crearColeccionPrueba():
    input = {
        'title': 'Creada desde python',
        'descriptionHtml': 'Colección de prueba creada desde <b>python</b>.',
        'sortOrder': 'ALPHA_ASC'
    }
    return Coleccion(input=input)


def obtenerEvento(evento: str):
    true = "true"
    ARTICULO = [
        {
            "eventID": "dc9dab6c1f61d74bb33206d3eb059a09",
            "eventName": "MODIFY",   # "INSERT"
            "eventVersion": "1.1",
            "eventSource": "aws:dynamodb",
            "awsRegion": "us-east-2",
            "dynamodb": {
                "ApproximateCreationDateTime": 1681153112,
                "Keys": {
                    "SK": {
                        "S": "METADATA"
                    },
                    "PK": {
                        "S": "GENERICO2022#DLTVA#ACCE02"
                    }
                },
                "NewImage": {
                    "prec_vta1": {
                        "N": "100"
                    },
                    "prec_vta3": {
                        "N": "300"
                    },
                    "stock_com": {
                        "N": "0"
                    },
                    "tipo": {
                        "S": "TIENDA"
                    },
                    "ubicacion": {
                        "S": "P01"
                    },
                    "prec_vta2": {
                        "N": "1"
                    },
                    "co_lin": {
                        "S": "CAJETINES, CAJAS DE PASO Y ACCESORIOS"
                    },
                    "created_at": {
                        "S": "2023-04-10T18:58:25.876283Z"
                    },
                    "unidad_empaque": {
                        "NULL": true
                    },
                    "codigoTienda": {
                        "S": "DLTVA"
                    },
                    "marca": {
                        "NULL": true
                    },
                    "updated_at": {
                        "S": "2023-04-10T18:58:25.876283Z"
                    },
                    "iva": {
                        "N": "16"
                    },
                    "codigoCompania": {
                        "S": "GENERICO2022"
                    },
                    "SK": {
                        "S": "METADATA"
                    },
                    "moneda": {
                        "N": "2"
                    },
                    "habilitado": {
                        "N": "1"
                    },
                    "cantidad_empaque": {
                        "N": "0"
                    },
                    "lineas": {
                        "S": "SIN CATEGORIA"
                    },
                    "art_des": {
                        "S": "ABRAZADERA MOROCHA 4\" (TORNILLO Y TUERCA) NUEVO NOMBRE"
                    },
                    "codigo_barra": {
                        "NULL": true
                    },
                    "co_art": {
                        "S": "ACCE02"
                    },
                    "unidad": {
                        "S": "PAR"
                    },
                    "stock_act": {
                        "N": "5"
                    },
                    "PK": {
                        "S": "GENERICO2022#DLTVA#ACCE02"
                    },
                    "entity": {
                        "S": "articulos"
                    },
                    "referencia": {
                        "S": "REF12345-321"
                    }
                },
                "OldImage": {
                    "prec_vta1": {
                        "N": "100"
                    },
                    "prec_vta3": {
                        "N": "300"
                    },
                    "stock_com": {
                        "N": "0"
                    },
                    "tipo": {
                        "S": "TIENDA"
                    },
                    "ubicacion": {
                        "S": "P01"
                    },
                    "prec_vta2": {
                        "N": "1"
                    },
                    "co_lin": {
                        "S": "CAJETINES, CAJAS DE PASO Y ACCESORIOS"
                    },
                    "created_at": {
                        "S": "2023-04-10T18:25:19.785560Z"
                    },
                    "unidad_empaque": {
                        "NULL": true
                    },
                    "codigoTienda": {
                        "S": "DLTVA"
                    },
                    "marca": {
                        "NULL": true
                    },
                    "updated_at": {
                        "S": "2023-04-10T18:25:19.785560Z"
                    },
                    "iva": {
                        "N": "16"
                    },
                    "codigoCompania": {
                        "S": "GENERICO2022"
                    },
                    "SK": {
                        "S": "METADATA"
                    },
                    "moneda": {
                        "N": "2"
                    },
                    "habilitado": {
                        "N": "1"
                    },
                    "cantidad_empaque": {
                        "N": "0"
                    },
                    "lineas": {
                        "S": "SIN CATEGORIA"
                    },
                    "art_des": {
                        "S": "ABRAZADERA MOROCHA 4\" (TORNILLO Y TUERCA) mielda!!"
                    },
                    "codigo_barra": {
                        "NULL": true
                    },
                    "co_art": {
                        "S": "ACCE02"
                    },
                    "unidad": {
                        "S": "PAR"
                    },
                    "stock_act": {
                        "N": "5"
                    },
                    "PK": {
                        "S": "GENERICO2022#DLTVA#ACCE02"
                    },
                    "entity": {
                        "S": "articulos"
                    },
                    "referencia": {
                        "S": "REF12345-321"
                    }
                },
                "SequenceNumber": "379556800000000020897494271",
                "SizeBytes": 1007,
                "StreamViewType": "NEW_AND_OLD_IMAGES"
            },
            "eventSourceARN": "arn:aws:dynamodb:us-east-2:276507440195:table/generico2022-db/stream/2023-03-17T19:09:23.192"
        }
    ]

    LINEA = [
        {
            "eventID": "076294cf324f590c5e047b39150460b5",
            "eventName": "INSERT",  # MODIFY
            "eventVersion": "1.1",
            "eventSource": "aws:dynamodb",
            "awsRegion": "us-east-2",
            "dynamodb": {
                "ApproximateCreationDateTime": 1681153658,
                "Keys": {
                    "SK": {
                        "S": "T#DLTVA#L#9"
                    },
                    "PK": {
                        "S": "GENERICO2022#LINEAS"
                    }
                },
                "NewImage": {
                    "tipo": {
                        "S": "LINEAS"
                    },
                    "updated_at": {
                        "S": "2023-04-10T19:07:37.267878Z"
                    },
                    "co_lin": {
                        "S": "9"
                    },
                    "descuento": {
                        "N": "0"
                    },
                    "SK": {
                        "S": "T#DLTVA#L#9"
                    },
                    "created_at": {
                        "S": "2023-04-10T19:07:37.267878Z"
                    },
                    "PK": {
                        "S": "GENERICO2022#LINEAS"
                    },
                    "co_lin_padre": {
                        "S": "0"
                    },
                    "nombre": {
                        "S": "CONTROL DE TEMPERATURA DESC2"
                    },
                    "entity": {
                        "S": "lineas"
                    }
                },
                "SequenceNumber": "379561900000000020897858575",
                "SizeBytes": 228,
                "StreamViewType": "NEW_AND_OLD_IMAGES"
            },
            "eventSourceARN": "arn:aws:dynamodb:us-east-2:276507440195:table/generico2022-db/stream/2023-03-17T19:09:23.192"
        }
    ]

    TIENDA = 


def main():
    s = crearColeccionPrueba()
    print(s)


if __name__ == '__main__':
    main()

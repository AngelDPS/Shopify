true = True

ARTICULO = [
    {
        "eventID": "dc9dab6c1f61d74bb33206d3eb059a09",
        "eventName": "INSERT",
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
                    "S": "8"
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
                    "S": "REF12345-322"
                }
            },
            "SequenceNumber": "379556800000000020897494271",
            "SizeBytes": 1007,
            "StreamViewType": "NEW_AND_OLD_IMAGES"
        },
        "eventSourceARN": "arn:aws:dynamodb:us-east-2:276507440195:table/generico2022-db/stream/2023-03-17T19:09:23.192"
    }
]

ARTICULO_act = [
    {
        "eventID": "dc9dab6c1f61d74bb33206d3eb059a09",
        "eventName": "MODIFY",
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
                    "S": "ACCE01"
                },
                "unidad": {
                    "S": "PAR"
                },
                "stock_act": {
                    "N": "10"
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
                    "S": "ACCE01"
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
                    "S": "8"
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
                "codigoCompania": {
                    "S": "GENERICO2022"
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

LINEA_act = [
    {
        "eventID": "076294cf324f590c5e047b39150460b5",
        "eventName": "MODIFY",
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
                    "S": "8"
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
                    "S": "CONTROL DE TEMPERATURA"
                },
                "codigoCompania": {
                    "S": "GENERICO2022"
                },
                "entity": {
                    "S": "lineas"
                }
            },
            "OldImage": {
                "tipo": {
                    "S": "LINEAS"
                },
                "updated_at": {
                    "S": "2023-04-10T19:07:37.267878Z"
                },
                "co_lin": {
                    "S": "8"
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
                "codigoCompania": {
                    "S": "GENERICO2022"
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

TIENDA = [
    {
        "eventID": "ba53299c3b6f3c7645c48a862729fccd",
        "eventName": "INSERT",
        "eventVersion": "1.1",
        "eventSource": "aws:dynamodb",
        "awsRegion": "us-east-2",
        "dynamodb": {
            "ApproximateCreationDateTime": 1681154031,
            "Keys": {
                "SK": {
                    "S": "T#DLTVA"
                },
                "PK": {
                    "S": "GENERICO2022#TIENDAS"
                }
            },
            "NewImage": {
                "color": {
                    "S": "#fca50d"
                },
                "horario": {
                    "S": "Lunes a Viernes de 8AM a 4PM / Sábado 8AM a 12M"
                },
                "bienvenida": {
                    "S": "bienvenido a *DELECTRA* tu proveedor seguro! ⚡⚡"
                },
                "coordenadas": {
                    "S": "{\"lat\": 10.175966, \"lng\": -67.977579}"
                },
                "codigoTienda": {
                    "S": "DLTVA"
                },
                "nombre": {
                    "S": "GENERICO2022 DLTVA, C.A."
                },
                "rif": {
                    "S": "J-313561140-1"
                },
                "inicio_presupuesto": {
                    "S": "A continuación detalle de su presupuesto, _*recuerde que los precios son unitarios*_:"
                },
                "mensaje_inicio_presupuesto_online": {
                    "S": "Descargue su presupuesto en formato PDF:"
                },
                "codigoCompania": {
                    "S": "GENERICO2022"
                },
                "correo": {
                    "S": "delectra.ventas@gmail.com"
                },
                "ultimo_archivo_procesado": {
                    "S": "2023-04-10T19:07:38.518316Z"
                },
                "SK": {
                    "S": "T#DLTVA"
                },
                "habilitado": {
                    "N": "1"
                },
                "telefono": {
                    "S": "02418339217"
                },
                "urlbase": {
                    "S": "https://generico2022.s3.us-east-2.amazonaws.com/presupuestos"
                },
                "ultimo_alive": {
                    "S": "2023-04-10T19:13:15.332323Z"
                },
                "notasPresupuesto": {
                    "S": "- Partes eléctricas no tienen cambio ni garantía.\n- Si desea factura, el impuesto debe ser cancelado en Bs.\n- Visítanos en www.delectra.com.ve"
                },
                "direccion": {
                    "S": "Prolongación Av. Michelena, C.C. ARPE, Local 16. Valencia, Edo. Carabobo"
                },
                "mensaje_fin_presupuesto_online": {
                    "S": "👆👆👆👆👆👆"
                },
                "info_pago": {
                    "S": "BANESCO"
                },
                "pagos": {
                    "S": "[{\"idPago\": \"1\", \"tipo\": \"efectivo\", \"nombre\": \"Efectivo en Dólares\", \"info\": \"Informacion adicional de efectivo\", \"moneda\": \"dolar\"}, \n{\"idPago\": \"2\", \"tipo\": \"transferencia\", \"nombre\": \"Transferencia Banco de Venezuela\", \"info\": \"GENERICO2022, C.A. RIF: 1245432, Cuenta: 010254356765434567\", \"moneda\": \"bolivar\"}, {\"idPago\": \"3\", \"tipo\": \"efectivo\", \"nombre\": \"Efectivo en Bolivares\", \"info\": \"Informacion adicional de efectivo en bolívares\", \"moneda\": \"bolivar\"}]"
                },
                "indicador": {
                    "S": "GENERICO VALENCIA"
                },
                "configuraciones": {
                    "S": "{\"procesarPedidoDesconectado\":true}"
                },
                "mensaje_fin2": {
                    "S": "🛵 *Pregunta por nuestro servicio de delivery*"
                },
                "orden_actualizar": {
                    "N": "0"
                },
                "PK": {
                    "S": "GENERICO2022#TIENDAS"
                },
                "slogan": {
                    "S": "*DELECTRA* Tu proveedor seguro!"
                },
                "entity": {
                    "S": "tiendas"
                }
            },
            "SequenceNumber": "379564100000000020898040858",
            "SizeBytes": 3393,
            "StreamViewType": "NEW_AND_OLD_IMAGES"
        },
        "eventSourceARN": "arn:aws:dynamodb:us-east-2:276507440195:table/generico2022-db/stream/2023-03-17T19:09:23.192"
    }
]

TIENDA_act = [
    {
        "eventID": "ba53299c3b6f3c7645c48a862729fccd",
        "eventName": "MODIFY",   # INSERT
        "eventVersion": "1.1",
        "eventSource": "aws:dynamodb",
        "awsRegion": "us-east-2",
        "dynamodb": {
            "ApproximateCreationDateTime": 1681154031,
            "Keys": {
                "SK": {
                    "S": "T#DLTVA"
                },
                "PK": {
                    "S": "GENERICO2022#TIENDAS"
                }
            },
            "NewImage": {
                "color": {
                    "S": "#fca50d"
                },
                "horario": {
                    "S": "Lunes a Viernes de 8AM a 4PM / Sábado 8AM a 12M"
                },
                "bienvenida": {
                    "S": "bienvenido a *DELECTRA* tu proveedor seguro! ⚡⚡"
                },
                "coordenadas": {
                    "S": "{\"lat\": 10.175966, \"lng\": -67.977579}"
                },
                "codigoTienda": {
                    "S": "DLTVA"
                },
                "nombre": {
                    "S": "GENERICO2022 DLTVA, C.A."
                },
                "rif": {
                    "S": "J-313561140-1"
                },
                "inicio_presupuesto": {
                    "S": "A continuación detalle de su presupuesto, _*recuerde que los precios son unitarios*_:"
                },
                "mensaje_inicio_presupuesto_online": {
                    "S": "Descargue su presupuesto en formato PDF:"
                },
                "codigoCompania": {
                    "S": "GENERICO2022"
                },
                "correo": {
                    "S": "delectra.ventas@gmail.com"
                },
                "ultimo_archivo_procesado": {
                    "S": "2023-04-10T19:07:38.518316Z"
                },
                "SK": {
                    "S": "T#DLTVA"
                },
                "habilitado": {
                    "N": "1"
                },
                "telefono": {
                    "S": "02418339217"
                },
                "urlbase": {
                    "S": "https://generico2022.s3.us-east-2.amazonaws.com/presupuestos"
                },
                "ultimo_alive": {
                    "S": "2023-04-10T19:13:51.193715Z"
                },
                "notasPresupuesto": {
                    "S": "- Partes eléctricas no tienen cambio ni garantía.\n- Si desea factura, el impuesto debe ser cancelado en Bs.\n- Visítanos en www.delectra.com.ve"
                },
                "direccion": {
                    "S": "Prolongación Av. Michelena, C.C. ARPE, Local 16. Valencia, Edo. Carabobo"
                },
                "mensaje_fin_presupuesto_online": {
                    "S": "👆👆👆👆👆👆"
                },
                "info_pago": {
                    "S": "BANESCO"
                },
                "pagos": {
                    "S": "[{\"idPago\": \"1\", \"tipo\": \"efectivo\", \"nombre\": \"Efectivo en Dólares\", \"info\": \"Informacion adicional de efectivo\", \"moneda\": \"dolar\"}, \n{\"idPago\": \"2\", \"tipo\": \"transferencia\", \"nombre\": \"Transferencia Banco de Venezuela\", \"info\": \"GENERICO2022, C.A. RIF: 1245432, Cuenta: 010254356765434567\", \"moneda\": \"bolivar\"}, {\"idPago\": \"3\", \"tipo\": \"efectivo\", \"nombre\": \"Efectivo en Bolivares\", \"info\": \"Informacion adicional de efectivo en bolívares\", \"moneda\": \"bolivar\"}]"
                },
                "indicador": {
                    "S": "GENERICO VALENCIA"
                },
                "configuraciones": {
                    "S": "{\"procesarPedidoDesconectado\":true}"
                },
                "mensaje_fin2": {
                    "S": "🛵 *Pregunta por nuestro servicio de delivery*"
                },
                "orden_actualizar": {
                    "N": "0"
                },
                "PK": {
                    "S": "GENERICO2022#TIENDAS"
                },
                "slogan": {
                    "S": "*DELECTRA* Tu proveedor seguro!"
                },
                "entity": {
                    "S": "tiendas"
                }
            },
            "OldImage": {
                "color": {
                    "S": "#fca50d"
                },
                "horario": {
                    "S": "Lunes a Viernes de 8AM a 4PM / Sábado 8AM a 12M"
                },
                "bienvenida": {
                    "S": "bienvenido a *DELECTRA* tu proveedor seguro! ⚡⚡"
                },
                "coordenadas": {
                    "S": "{\"lat\": 10.175966, \"lng\": -67.977579}"
                },
                "codigoTienda": {
                    "S": "DLTVA"
                },
                "nombre": {
                    "S": "GENERICO2022 DLTVA, C.A."
                },
                "rif": {
                    "S": "J-313561140-1"
                },
                "inicio_presupuesto": {
                    "S": "A continuación detalle de su presupuesto, _*recuerde que los precios son unitarios*_:"
                },
                "mensaje_inicio_presupuesto_online": {
                    "S": "Descargue su presupuesto en formato PDF:"
                },
                "codigoCompania": {
                    "S": "GENERICO2022"
                },
                "correo": {
                    "S": "delectra.ventas@gmail.com"
                },
                "ultimo_archivo_procesado": {
                    "S": "2023-04-10T19:07:38.518316Z"
                },
                "SK": {
                    "S": "T#DLTVA"
                },
                "habilitado": {
                    "N": "1"
                },
                "telefono": {
                    "S": "02418339217"
                },
                "urlbase": {
                    "S": "https://generico2022.s3.us-east-2.amazonaws.com/presupuestos"
                },
                "ultimo_alive": {
                    "S": "2023-04-10T19:13:15.332323Z"
                },
                "notasPresupuesto": {
                    "S": "- Partes eléctricas no tienen cambio ni garantía.\n- Si desea factura, el impuesto debe ser cancelado en Bs.\n- Visítanos en www.delectra.com.ve"
                },
                "direccion": {
                    "S": "Prolongación Av. Michelena, C.C. ARPE, Local 16. Valencia, Edo. Carabobo"
                },
                "mensaje_fin_presupuesto_online": {
                    "S": "👆👆👆👆👆👆"
                },
                "info_pago": {
                    "S": "BANESCO"
                },
                "pagos": {
                    "S": "[{\"idPago\": \"1\", \"tipo\": \"efectivo\", \"nombre\": \"Efectivo en Dólares\", \"info\": \"Informacion adicional de efectivo\", \"moneda\": \"dolar\"}, \n{\"idPago\": \"2\", \"tipo\": \"transferencia\", \"nombre\": \"Transferencia Banco de Venezuela\", \"info\": \"GENERICO2022, C.A. RIF: 1245432, Cuenta: 010254356765434567\", \"moneda\": \"bolivar\"}, {\"idPago\": \"3\", \"tipo\": \"efectivo\", \"nombre\": \"Efectivo en Bolivares\", \"info\": \"Informacion adicional de efectivo en bolívares\", \"moneda\": \"bolivar\"}]"
                },
                "indicador": {
                    "S": "GENERICO VALENCIA"
                },
                "configuraciones": {
                    "S": "{\"procesarPedidoDesconectado\":true}"
                },
                "mensaje_fin2": {
                    "S": "🛵 *Pregunta por nuestro servicio de delivery*"
                },
                "orden_actualizar": {
                    "N": "0"
                },
                "PK": {
                    "S": "GENERICO2022#TIENDAS"
                },
                "slogan": {
                    "S": "*DELECTRA* Tu proveedor seguro!"
                },
                "entity": {
                    "S": "tiendas"
                }
            },
            "SequenceNumber": "379564100000000020898040858",
            "SizeBytes": 3393,
            "StreamViewType": "NEW_AND_OLD_IMAGES"
        },
        "eventSourceARN": "arn:aws:dynamodb:us-east-2:276507440195:table/generico2022-db/stream/2023-03-17T19:09:23.192"
    }
]

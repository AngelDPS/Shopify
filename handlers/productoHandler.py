from logging import getLogger
from models.producto import (
    MproductInput,
    MproductVariantInput,
    MinventoryLevelInput
)
from models.evento import Marticulo, Mlinea
from handlers.coleccionHandler import Coleccion
from libs.conexion import ConexionShopify
from json import load, dump
from os import rename, environ
from gql import gql

logger = getLogger("Shopify.Producto")


class Producto:
    gqlrequests = """
        query consultarGidVariante($id: ID!){
            product(id: $id){
                variants(first: 1){
                    nodes {
                        id
                    }
                }
            }
        }

        query consultarGidInventario($id: ID!){
            product(id: $id) {
                variants(first: 1) {
                    nodes {
                        inventoryItem {
                            id
                        }
                    }
                }
            }
        }

        mutation crearProducto($input: ProductInput!,
                               $media: [CreateMediaInput!]){
            productCreate(input: $input, media: $media) {
                product {
                    ... ProductoInfo
                }
                userErrors {
                    message
                }
            }
        }

        mutation modificarProducto($input: ProductInput!) {
            productUpdate(input: $input) {
                product {
                    ... ProductoInfo
                }
                userErrors {
                    message
                }
            }
        }

        mutation modificarVarianteProducto($input: ProductVariantInput!) {
            productVariantUpdate(input: $input) {
                userErrors {
                    message
                }
            }
        }

        mutation establecerInventarioDisponible(
            $inventoryId: ID!, $locationId: ID!, $qty: Int!
            ) {
            inventorySetOnHandQuantities(
                input: {reason: "correction", setQuantities: {
                    inventoryItemId: $inventoryId,
                    locationId: $locationId,
                    quantity: $qty
                    }}
            ) {
                    inventoryAdjustmentGroup {
                        changes {
                            delta
                        }
                    }
                    userErrors {
                    message
                    }
                }
            }

        mutation ajustarInventarios(
            $delta: Int!,
            $inventoryItemId: ID!,
            $locationId: ID!,
            $name: String!,
            $reason: String!
        ) {
            inventoryAdjustQuantities(input: {
                changes: [
                    {
                        delta: $delta,
                        inventoryItemId: $inventoryItemId,
                        locationId: $locationId
                    }
                ],
                name: $name,
                reason: $reason
                }){
                userErrors {
                    message
                }
            }
        }

        query obtenerPublicaciones {
        publications(first: 2) {
            nodes {
                id
            }
        }
    }

    mutation publicar($id: ID!, $input: [PublicationInput!]!) {
        publishablePublish(id: $id, input: $input) {
            userErrors {
                field
                message
            }
        }
    }

    mutation ocultar($id: ID!, $input: [PublicationInput!]!) {
        publishableUnpublish(id: $id, input: $input) {
            userErrors {
                field
                message
            }
        }
    }

        fragment ProductoInfo on Product {
            id
            productType
            status
            title
            variants(first: 1) {
                nodes {
                    id
                    inventoryItem {
                        id
                    }
                }
            }
        }
        """
    conexion = ConexionShopify(gqlrequests)

    # TODO: Función para actualizar BD
    def actualizarGidBD(self):
        DBpath = 'DB/GENERICO2022.json'
        DBpath_temp = DBpath + '.temp'
        with open(DBpath) as DBfile, open(DBpath_temp, 'w') as DBtemp:
            try:
                DB = load(DBfile)
                DB.setdefault('articulos', {}).setdefault(self.NewImage.PK, {})
                DB['articulos'][self.NewImage.PK]['shopifyGID'] = (
                    self.NewImage.shopifyGID
                )
                dump(DB, DBtemp)
            except TypeError as err:
                logger.exception("Hubo un problema actualizando la base "
                                 "de datos. Asegurese que el tipo de la "
                                 "data sea serializable a json.")
                logger.debug(f"{DB = }")
                err.add_note("No se pudo serializar la data entrante a la BD.")
                raise
            else:
                rename(DBpath_temp, DBpath)

    @staticmethod
    def obtenerCampoPrecio() -> str:
        return environ['precio']

    def obtenerGidTienda(self, use_old: bool = False) -> str:
        """Función para obtener el GID asociado a codigoTienda.

        Args:
            codigoCompania (str): _description_
            codigoTienda (str): _description_

        Returns:
            str: _description_
        """
        DBpath = 'DB/GENERICO2022.json'
        codigoTienda = (self.NewImage.codigoTienda if not use_old
                        else self.OldImage.codigoTienda)
        with open(DBpath) as DBfile:
            DB = load(DBfile)
        tienda = DB['tiendas'][codigoTienda]
        try:
            return tienda['shopifyGID']['sucursal']
        except KeyError:
            tienda['shopifyGID']['sucursal'] = self.conexion.execute(
                gql("""
                    query Tienda($nombre: String) {
                        locations(first: 1, query: $nombre) {
                            nodes {
                                id
                            }
                        }
                    }
                    """),
                variables={"name": f"name:{tienda['nombre']}"}
                )['locations']['nodes'][0]['id']
            DB['tiendas'][codigoTienda] |= tienda
            DBpath_temp = DBpath + '.temp'
            with open(DBpath_temp, 'w') as DBtemp:
                dump(DB, DBtemp)
            rename(DBpath_temp, DBpath)
            return tienda['shopifyGID']['sucursal']

    def obtenerGidColeccion(self, use_old: bool = False) -> str:
        DBpath = 'DB/GENERICO2022.json'
        SK = (f"T#{self.NewImage.codigoTienda}#L#{self.NewImage.co_lin}"
              if not use_old else
              f"T#{self.OldImage.codigoTienda}#L#{self.OldImage.co_lin}")
        with open(DBpath) as DBfile:
            linea = load(DBfile)['lineas'][SK]
        try:
            return linea['shopifyGID']
        except KeyError:
            linea = Mlinea.parse_obj(linea)
            respuestas = Coleccion(linea).crear()
            return respuestas[0]["collectionCreate"]["collection"]["id"]

    def obtenerGidPublicaciones(self, use_old: bool = False) -> str:
        codigoTienda = (self.NewImage.codigoTienda if not use_old
                        else self.OldImage.codigoTienda)
        DBpath = 'DB/GENERICO2022.json'
        with open(DBpath) as DBfile:
            DB = load(DBfile)
        tienda = DB['tiendas'][codigoTienda]
        try:
            return tienda['shopifyGID']['publicaciones']
        except KeyError:
            tienda['shopifyGID']['publicaciones'] = [
                i["id"] for i in
                self.conexion.execute(
                    gql("""
                    query obtenerPublicaciones {
                        publications(first: 2) {
                            nodes {
                                id
                            }
                        }
                    }
                    """)
                )['publications']['nodes']
            ]
            DB['tiendas'][codigoTienda] |= tienda
            DBpath_temp = DBpath + '.temp'
            with open(DBpath_temp, 'w') as DBtemp:
                dump(DB, DBtemp)
            rename(DBpath_temp, DBpath)
            return tienda['shopifyGID']['publicaciones']

    def __init__(self, NewImage: Marticulo, OldImage: Marticulo = None,
                 cambios: Marticulo = None):
        self.NewImage = NewImage
        self.OldImage = OldImage
        self.cambios = cambios
        preciosIgnorar = ['prec_vta1', 'prec_vta2', 'prec_vta3']
        preciosIgnorar.remove(self.obtenerCampoPrecio())
        [setattr(self.cambios, prec, None) for prec in preciosIgnorar]
        self.cambios.entity = None

    def publicar(self) -> dict:
        """Publica el artículo en la tienda virtual y punto de venta de
        Shopify.

        Returns:
            dict: Json deserealizado con la respuesta obtenida.
        """
        try:
            respuesta = self.conexion.execute(
                gql("""
                    mutation publicar($id: ID!, $input: [PublicationInput!]!) {
                        publishablePublish(id: $id, input: $input) {
                            userErrors {
                                field
                                message
                            }
                        }
                    }
                    """),
                variables={
                    'id': self.NewImage.shopifyGID['producto'],
                    'input': [{"publicationId": id}
                              for id in self.obtenerGidPublicaciones()]
                }
            )
            logger.info("Publicación exitosa del producto.")
            return respuesta
        except Exception as err:
            logger.exception("No se pudo publicar el producto.")
            err.add_note("Error/es encontrado publicando el producto.")
            raise

    def crear(self) -> list[dict]:
        """Función dedicada a crear un producto en Shopify dada
        la información de un evento de artículo INSERT

        Returns:
            list[dict]: Lista con las respuestas de las operaciones de crear y
            publicar el producto en Shopify.
        """
        logger.info("Creando producto a partir de artículo.")
        try:
            inventory = [MinventoryLevelInput(
                availableQuantity=(self.NewImage.stock_act
                                   - self.NewImage.stock_com),
                locationId=self.obtenerGidTienda()
            )]
            variantInput = MproductVariantInput(
                **self.NewImage.dict(by_alias=True,
                                     exclude_none=True),
                inventoryQuantities=inventory)
            variantInput.price = getattr(self.NewImage,
                                         self.obtenerCampoPrecio())
            productInput = MproductInput(
                **self.NewImage.dict(by_alias=True,
                                     exclude_none=True),
                status=("ACTIVE"
                        if self.NewImage.habilitado
                        else "ARCHIVED"),
                variants=[variantInput],
                collectionsToJoin=[self.obtenerGidColeccion()])
            respuestas = [self.conexion.execute(
                gql("""
                    mutation crearProducto($input: ProductInput!,
                               $media: [CreateMediaInput!]){
                        productCreate(input: $input, media: $media) {
                            product {
                                id
                                variants(first: 1) {
                                    nodes {
                                        id
                                        inventoryItem {
                                            id
                                        }
                                    }
                                }
                            }
                            userErrors {
                                message
                            }
                        }
                    }
                    """),
                variables={'input': productInput.dict(exclude_none=True)}
            )]
            self.NewImage.shopifyGID = {
                'producto': respuestas[0]['productCreate']['product']['id'],
                'variante': {
                    'id': (respuestas[0]['productCreate']['product']
                           ['variants']['nodes'][0]['id']),
                    'inventario': (respuestas[0]['productCreate']['product']
                                   ['variants']['nodes'][0]['inventoryItem']
                                   ['id'])
                }
            }
            self.publicar()
            self.actualizarGidBD()
            return respuestas
        except Exception as err:
            logger.exception("No fue posible crear el producto.")
            err.add_note("Ocurrieron problemas creando el producto.")
            raise

    def _modificarInventario(self, delta: int) -> dict:
        reason = "restock" if delta > 0 else "shrinkage"
        respuesta = self.conexion.execute(
            gql("""
                mutation ajustarInventarios(
                    $delta: Int!,
                    $inventoryItemId: ID!,
                    $locationId: ID!,
                    $name: String!,
                    $reason: String!
                ) {
                    inventoryAdjustQuantities(input: {
                        changes: [
                            {
                                delta: $delta,
                                inventoryItemId: $inventoryItemId,
                                locationId: $locationId
                            }
                        ],
                        name: $name,
                        reason: $reason
                        }){
                        userErrors {
                            message
                        }
                    }
                }
                """),
            variables={
                "delta": delta,
                "name": "available",
                "reason": reason,
                "inventoryItemId": (self.OldImage.shopifyGID['variante']
                                    ['inventario']),
                "locationId": self.obtenerGidTienda(use_old=True)
            }
        )
        return respuesta

    def modificar(self) -> dict:
        try:
            logger.info("Actualizando producto.")
            variantInput = MproductVariantInput.parse_obj(
                self.cambios.dict(by_alias=True))
            variantInput.price = getattr(self.cambios,
                                         self.obtenerCampoPrecio())
            status = {
                None: None,
                True: "ACTIVE",
                False: "ARCHIVED"
            }[self.cambios.habilitado]
            productInput = MproductInput(
                **self.cambios.dict(by_alias=True, exclude_none=True),
                status=status)
            if self.cambios.co_lin:
                productInput.collectionsToJoin = [self.obtenerGidColeccion()]
                productInput.collectionsToLeave = [
                    self.obtenerGidColeccion(use_old=True)
                ]
            respuestas = []
            if self.cambios.stock_act or self.cambios.stock_com:
                delta_act = (self.cambios.stock_act - self.OldImage.stock_act
                             if self.cambios.stock_act else 0)
                delta_com = (self.cambios.stock_com - self.OldImage.stock_com
                             if self.cambios.stock_com else 0)
                delta = delta_act - delta_com
                if delta != 0:
                    respuestas.append(
                        self.ajustarInventario(delta)
                    )
            if variantInput.dict(exclude_none=True, exclude_unset=True):
                variantInput.id = self.OldImage.shopifyGID["variante"]["id"]
                respuestas.append(self.conexion.execute(
                    gql("""
                        mutation modificarVarianteProducto(
                                $input: ProductVariantInput!
                            ) {
                            productVariantUpdate(input: $input) {
                                userErrors {
                                    message
                                }
                            }
                        }
                        """),
                    variables={'input': variantInput.dict(exclude_none=True)}
                ))
            if productInput.dict(exclude_none=True, exclude_unset=True):
                productInput.id = self.OldImage.shopifyGID["producto"]
                respuestas.append(self.conexion.execute(
                    gql("""
                        mutation modificarProducto($input: ProductInput!) {
                            productUpdate(input: $input) {
                                userErrors {
                                    message
                                }
                            }
                        }
                        """),
                    variables={'input': productInput.dict(exclude_none=True)}
                ))
            return respuestas
        except Exception as err:
            logger.exception("No fue posible modificar el producto.")
            err.add_note("Ocurrieron problemas modificando el producto")
            raise

    def ejecutar(self):
        try:
            if not self.OldImage:
                respuestas = (self.crear())
            elif self.cambios.dict(exclude_none=True):
                respuestas = (self.modificar())
            else:
                logger.info("Los cambios encontrados no ameritan "
                            "actualizaciones en Shopify.")
                respuestas = [{}]
            return respuestas
        except Exception as err:
            err.add_note("Ocurrió un problema ejecutando la acción sobre el"
                         "producto.")

import logging
from shopify.models.evento import Mlinea
from re import search
import dynamodb
import shopify.conexion as conexion

logger = logging.getLogger("shopify.coleccionHandler")


class ColeccionHandler:

    def actualizarGidBD(self):
        logger.debug(f"GID de línea: {self.NewImage.shopifyGID}")
        dynamodb.actualizarGidLinea(
            PK=self.NewImage.PK,
            SK=self.NewImage.SK,
            GID=self.NewImage.shopifyGID
        )

    def obtenerGidPublicaciones(self, use_old: bool = False) -> str:
        try:
            codigoCompania = search(r"\w+(?=#LINEAS)", self.NewImage.PK)[0]
            SK = self.NewImage.SK if not use_old else self.OldImage.SK
            codigoTienda = search(r"(?<=T#)\w+", SK)[0]
            tienda = dynamodb.obtenerTienda(
                codigoCompania,
                codigoTienda
            )
            return tienda['shopifyGID']['publicaciones']
        except KeyError:
            pass
        try:
            logger.warning("No se encontró el GID de los canales de "
                           "publicación en la base de datos. Se procederá a "
                           "consultar el GID a Shopify y a guardar el "
                           "resultado obtenido.")
            tienda.setdefault('shopifyGID', {})
            tienda['shopifyGID']['publicaciones'] = (
                conexion.obtenerGidPublicaciones()
            )
            dynamodb.actualizarGidPublicacionesTienda(
                codigoCompania=codigoCompania,
                codigoTienda=codigoTienda,
                pubIDs=tienda['shopifyGID']['publicaciones']
            )
            return tienda['shopifyGID']['publicaciones']
        except Exception:
            logger.exception("Error al obtener los GIDs de los canales de "
                             "publicación.")
            raise

    def __init__(self, NewImage: Mlinea, OldImage: Mlinea = None,
                 cambios: Mlinea = None):
        self.NewImage = NewImage
        self.OldImage = OldImage
        self.cambios = cambios or Mlinea()
        self.cambios.entity = None

    def publicar(self):
        """Publica el artículo en la tienda virtual y punto de venta de
        Shopify.
        """
        conexion.publicarRecurso(
            GID=self.NewImage.shopifyGID,
            pubIDs=self.obtenerGidPublicaciones()
        )

    def crear(self) -> list[dict]:
        """Función dedicada a crear una colección en Shopify dada
        la información de un evento de línea INSERT

        Returns:
            list[dict]: Lista con las respuestas de las operaciones de crear y
            publicar la colección en Shopify.
        """
        logger.info("Creando colección a partir de línea.")

        try:
            self.NewImage.shopifyGID = conexion.crearColeccion(self.NewImage)
            self.publicar()
            self.actualizarGidBD()
            logger.info("Colección creada exitosamente.")
            return "Colección creada exitosamente."
        except Exception:
            logger.exception("No fue posible crear la colección")
            raise

    def modificar(self) -> list[dict]:
        try:
            conexion.modificarColeccion(self.cambios)
            logger.info("La colección fue modificada exitosamente.")
            return "Coleccion modificada exitosamente."
        except Exception:
            logger.exception("No fue posible modificar la colección.")
            raise

    def ejecutar(self):
        try:
            if not self.OldImage:
                respuestas = self.crear()
            elif self.cambios:
                respuestas = self.modificar()
            return respuestas
        except Exception:
            logger.exception("Ocurrió un problema ejecutando la acción sobre "
                             "la colección")
            raise

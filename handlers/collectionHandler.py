import logging
from models.collection import McollectionInput
from libs.conexion import ConexionShopify

logger = logging.getLogger("Shopify.collectionHandler")
with open('graphql/coleccion.graphql') as file:
    queries = file.read()


class Coleccion:
    logger = logging.getLogger("Shopify.coleccionHandler.Coleccion")
    conexion = ConexionShopify()
    ID: str
    titulo: str
    descripcion: str
    nProductos: int

    def _actualizarInstancia(self, respuesta: dict):
        """Actualiza los atributos de la instancia a los valores
        obtenidos de Shopify

        Args:
            respuesta (dict): diccionario con la información correspondiente.
            TODO: Debe de reemplazarse por un modelo de respuesta apropiado.
        """
        self.ID = respuesta['collection']['id']
        self.titulo = respuesta['collection']['title']
        self.direccion = respuesta['collection']['description']
        self.nProductos = int(respuesta['collection']['productsCount'])

    def _borrarDatos(self):
        """Elimina los atributos de la instancia en el momento en que se
        elimina la sucursal en Shopify.
        """
        del self.ID
        del self.titulo
        del self.descripcion
        del self.nProductos

    def publicar(self):
        try:
            respuesta = self.conexion.enviarConsulta(
                queries,
                variables={'id': self.ID},
                operacion='publicarColeccion'
            )
        except Exception:
            self.logger.exception("No fue posible publicar la colección.")
            raise
        else:
            self.logger.info("La colección fue publicada exitosamente.")
            self.logger.debug(respuesta)

    def __init__(self, input: dict = None, id: str = None):
        self.logger.info("Creando instancia de colección")

        if id:
            try:
                respuesta = self.conexion.enviarConsulta(
                    queries,
                    variables={'id': id},
                    operacion='consultarColeccion'
                )
                if not respuesta['collection']:
                    raise ValueError(
                        "El ID proporcionado no corresponde a una colección "
                        "existente"
                    )
            except Exception:
                self.logger.exception("No fue posible consultar la colección.")
                raise
            else:
                self.logger.info("Instancia creada por consulta.")
                self.logger.debug(respuesta)
                self._actualizarInstancia(respuesta)
        elif input:
            try:
                respuesta = self.conexion.enviarConsulta(
                    queries,
                    variables={
                        'input': (McollectionInput.parse_obj(input)
                                  .dict(exclude_none=True))
                    },
                    operacion='crearColeccion'
                )
            except Exception:
                self.logger.exception("No fue posible crear la coleccion")
                raise
            else:
                self.logger.info(
                    "Instancia creada por añadir una nueva colección."
                )
                self.logger.debug(respuesta)
                self._actualizarInstancia(respuesta['collectionCreate'])
        else:
            msg = "Para instanciar una colección, se debe otorgar un ID de " \
                  "referencia o una entrada con la información para crear " \
                  "una nueva sucursal."
            self.logger.exception(msg, stack_info=True)
            raise ValueError(msg)

        self.publicar()

    def __str__(self):
        return f"Colección '{self.titulo}' con ID: '{self.ID}'"

    def modificar(self, input: dict):
        input['id'] = self.ID
        try:
            respuesta = self.conexion.enviarConsulta(
                queries,
                variables={
                    'input': (McollectionInput.parse_obj(input)
                              .dict(exclude_none=True))
                },
                operacion='modificarColeccion'
            )
        except Exception:
            self.logger.exception("La colección no pudo ser modificada")
            raise
        else:
            self.logger.info("La colección fue modificada exitosamente.")
            self._actualizarInstancia(respuesta)

    def eliminar(self):
        self.logger.info(f'Eliminando la colección: {self.titulo}')
        try:
            respuesta = self.conexion.enviarConsulta(
                queries,
                variables={'id': self.ID},
                operacion='eliminarColeccion'
            )
        except Exception:
            self.logger.exception("No se pudo eliminar la colección")
            raise
        else:
            self.logger.info("Colección eliminada exitosamente")
            self.logger.debug(respuesta)
            self._borrarDatos()

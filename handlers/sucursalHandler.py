import logging
from models.sucursal import MsucursalInput
from libs.conexion import ConexionShopify

logger = logging.getLogger("Shopify.sucursalHandler")
with open('graphql/sucursal.graphql') as file:
    queries = file.read()


class Sucursal:
    logger = logging.getLogger("Shopify.sucursalHandler.Sucursal")
    conexion = ConexionShopify()
    ID: str
    nombre: str
    direccion: str

    def _actualizarInstancia(self, respuesta: dict):
        """Actualiza los atributos de la instancia a los valores
        obtenidos de Shopify

        Args:
            respuesta (dict): diccionario con la información correspondiente.
            TODO: Debe de reemplazarse por un modelo de respuesta apropiado.
        """
        self.nombre = respuesta['location']['name']
        self.ID = respuesta['location']['id']
        self.direccion = respuesta['location']['address']['formatted']

    def _borrarDatos(self):
        """Elimina los atributos de la instancia en el momento en que se
        elimina la sucursal en Shopify.
        """
        del self.nombre
        del self.ID
        del self.direccion

    def __init__(self, input: dict = None,
                 id: str = None):
        self.logger.info("Creando instancia de sucursal")

        if id:
            try:
                respuesta = self.conexion.enviarConsulta(
                    queries,
                    variables={'ID': id},
                    operacion='consultarSucursal'
                )
                if not respuesta['collection']:
                    raise ValueError(
                        "El ID proporcionado no corresponde a una sucursal "
                        "existente"
                    )
            except Exception:
                self.logger.exception("No fue posible consultar la sucursal.")
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
                        'input': (MsucursalInput.parse_obj(input)
                                  .dict(exclude_none=True))
                    },
                    operacion='crearSucursal'
                )
            except Exception:
                self.logger.exception("No fue posible crear la sucursal")
                raise
            else:
                self.logger.info(
                    "Instancia creada por añadir una nueva sucursal."
                )
                self.logger.debug(respuesta)
                self._actualizarInstancia(respuesta['locationAdd'])
        else:
            msg = "Para instanciar una sucursal, se debe otorgar un ID de " \
                  "referencia o una entrada con la información para crear " \
                  "una nueva sucursal."
            self.logger.exception(msg, stack_info=True)
            raise Exception(msg)

    def __str__(self):
        return f'Sucursal "{self.nombre}" con ID: "{self.ID}"'

    def modificar(self, input: dict):
        try:
            respuesta = self.conexion.enviarConsulta(
                queries,
                variables={
                    'locationId': self.ID,
                    'input': (MsucursalInput.parse_obj(input)
                              .dict(exclude_none=True))
                },
                operacion='modificarSucursal'
            )
        except Exception:
            self.logger.exception("La sucursal no pudo ser modificada")
            raise
        else:
            self.logger.info("La sucursal fue modificada exitosamente.")
            self._actualizarInstancia(respuesta)

    def eliminar(self, sucursalAlt=None):
        self.logger.info(f'Eliminando la sucursal "{self.NOMBRE = }"')

        try:
            respuesta = self.conexion.enviarConsulta(
                queries,
                variables={
                    'locationId': self.ID,
                    'alternateLocationId': (
                        sucursalAlt.ID if sucursalAlt else None)
                },
                operacion='eliminarSucursal'
            )
        except Exception:
            self.logger.exception("No se pudo eliminar la sucursal")
            raise
        else:
            self.logger.info("Sucursal eliminada exitosamente")
            self.logger.debug(respuesta)
            self._borrarDatos()

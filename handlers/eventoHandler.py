from boto3.dynamodb.types import TypeDeserializer
from models.evento import Mevento, Mimage
from handlers.productoHandler import Producto
from handlers.coleccionHandler import Coleccion
from handlers.sucursalHandler import Sucursal
from json import load, dump
from os import rename
from logging import getLogger


class Evento:

    @staticmethod
    def obtenerBD(compañia: str) -> dict:
        """Dado el codigo de compañia, lee la base de datos asociada en
        un archivo json.

        Args:
            compañia (str): Código de compañía.

        Returns:
            dict: Información de la base de datos en json deserealizado.
        """
        logger = getLogger("Shopify.eventHandler")
        DBpath = f"DB/{compañia}.json"
        try:
            with open(DBpath) as DBfile:
                return load(DBfile)
        except FileNotFoundError as err:
            logger.error(f"Base de datos '{DBpath}' no encontrada.\n"
                         "Asegurese de que el archivo json se encuentre con "
                         "el siguiente formato:\n"
                         '{\n\t"gids": {\n\t\t"publications": [\n\t\t\t'
                         '<gid tienda online>\n\t\t]\n\t},\n\t'
                         '"config": {\n\t\t"shopify": {\n\t\t\t'
                         '"tienda": <nombre de tienda en Shopify>,\n\t\t\t'
                         '"access_token": <token de acceso de la admin app de'
                         ' la tienda>\n\t\t},\n\t\t'
                         '"precio": <campo de precio a usar>\n\t}\n}')
            err.add_note(f"Base de datos '{DBpath}' no encontrada.")
            raise

    def actualizarBD(self):
        """Actualiza la base de datos con la información almacenada en la
        instancia
        """
        DBpath = f'DB/{self.data.NewImage.codigoCompania}.json'
        DBpath_temp = DBpath + '.temp'
        with open(DBpath_temp, 'w') as DBtemp:
            try:
                dump({'gids': self.gids, 'config': self.config}, DBtemp)
            except TypeError as err:
                self.logger.exception("Hubo un problema actualizando la base "
                                      "de datos. Asegurese que el tipo de la "
                                      "data sea serializable a json.")
                self.logger.debug(f"{self.gids = }\n{self.config = }")
                err.add_note("No se pudo serializar la data entrante a la BD.")
                raise
            else:
                rename(DBpath_temp, DBpath)

    @staticmethod
    def deserializar(Image: dict) -> dict:
        """Deserializa un diccionario en serializado segun DynamoDB

        Args:
            Image (dict): Diccionario serializado segun DynamoDB

        Returns:
            dict: Diccionario deserealizado
        """
        logger = getLogger("Shopify.eventHandler")
        deserializer = TypeDeserializer()
        try:
            return {k: deserializer.deserialize(v) for k, v in Image.items()}
        except TypeError as err:
            logger.exception('Los valores de "NewImage" y "OldImage" deberían '
                             'ser diccionarios no-vacíos cuya key corresponde '
                             'a un tipo de dato de DynamoDB soportado por '
                             'boto3.')
            err.add_note(f'"{Image}" no tiene el formato de DynamoDB')
            raise

    @staticmethod
    def formatearEvento(evento: list) -> Mevento:
        """Recibe el evento y lo analiza para su posterior manipulación.

        Args:
            evento (list): Evento de AWS dentro de una lista.

        Raises:
            KeyError: En caso de que el evento no tenga los campos esperados.

        Returns:
            Mevento: Objeto con los campos de interés del evento.
        """
        logger = getLogger("Shopify.eventHandler")
        try:
            resultado = evento[0]
        except IndexError:
            logger.warning(
                "Formato inesperado. El evento no se encuentra en un array.\n")
            resultado = evento
        try:
            resultado = resultado['dynamodb']
            if 'NewImage' not in resultado:
                raise KeyError
            resultado['NewImage'] = Evento.deserializar(resultado['NewImage'])
            resultado['OldImage'] = (Evento.deserializar(resultado['OldImage'])
                                     if resultado.get('OldImage') else None)
            return Mevento.parse_obj(resultado)
        except KeyError as err:
            logger.exception("Formato inesperado para el evento.\n"
                             "El evento debería tener los objetos\n"
                             '{\n\t...,\n\t"dynamobd": {\n\t\t...\n\t\t'
                             '"NewImage": ...\n\t}\n}')
            err.add_note("")
            raise
        except Exception:
            raise

    @staticmethod
    def obtenerCambios(evento: Mevento) -> Mimage | None:
        """Obtiene los cambios realizados en un evento de tipo "MODIFY"

        Args:
            evento (Mevento): Modelo de evento con los campos de interés

        Returns:
            Mimage | None: Modelo con los campos de la base de datos que sufrieron cambios
            o None en caso de no haber ninguno
        """
        cambios = {
            k: v for k, v in evento.NewImage
            if (v != getattr(evento.OldImage, k) or
                k == "entity")
        } if evento.OldImage else {}
        if len(cambios) > 1:
            return Mevento(NewImage=cambios).NewImage
        else:
            return None

    def __init__(self, evento: list):
        """Constructor de la instancia encargada de procesar y ejecutar el evento

        Args:
            evento (list): Evento de AWS dentro de una lista.
        """
        self.logger = getLogger("Shopify.eventHandler")
        self.data = Evento.formatearEvento(evento)
        self.gids, self.config = Evento.obtenerBD(
            self.data.NewImage.codigoCompania
        ).values()
        self.cambios = self.obtenerCambios(self.data)
        self.logger.debug(f'{self.cambios = }')

    def procesar(self):
        self.logger.debug(f'{self.data = }')
        if self.cambios or not self.data.OldImage:
            {
                'articulos': Producto,
                'lineas': Coleccion,
                'tiendas': Sucursal
            }[self.data.NewImage.entity](self)
            # TODO: Revisar la selección de clase.

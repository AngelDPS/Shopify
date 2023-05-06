from boto3.dynamodb.types import TypeDeserializer
from models.respuesta import Respuesta
from models.evento import Mevento, Mimage
from handlers.productoHandler import Producto
from handlers.coleccionHandler import Coleccion
from handlers.sucursalHandler import Sucursal
from logging import getLogger
from json import load


class Evento:

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
    def formatearEvento(evento: dict) -> Mevento:
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
            resultado = evento['dynamodb']
            resultado['NewImage'] = Evento.deserializar(resultado['NewImage'])
            resultado['OldImage'] = (Evento.deserializar(resultado['OldImage'])
                                     if resultado.get('OldImage') else None)
            resultado = Mevento.parse_obj(resultado)
            return resultado.NewImage, resultado.OldImage
        except KeyError as err:
            logger.exception("Formato inesperado para el evento.\n"
                             "El evento debería tener los objetos\n"
                             '{\n\t...,\n\t"dynamobd": {\n\t\t...\n\t\t'
                             '"NewImage": ...\n\t}\n}')
            err.add_note("")
            raise

    @staticmethod
    def obtenerCambios(NewImage: Mimage, OldImage: Mimage) -> Mimage | None:
        """Obtiene los cambios realizados en un evento de tipo "MODIFY"

        Args:
            evento (Mevento): Modelo de evento con los campos de interés

        Returns:
            Mimage | None: Modelo con los campos de la base de datos que
            sufrieron cambios o None en caso de no haber ninguno
        """
        cambios = {
            k: v for k, v in NewImage
            if (v != getattr(OldImage, k) or
                k == "entity")
        } if OldImage else {}
        if len(cambios) > 1:
            return Mevento(NewImage=cambios).NewImage
        else:
            return None

    @staticmethod
    def obtenerConfiguracion(codigoCompania: str) -> dict:
        """Recuperar información del archivo de configuración.

        Args:
            codigoCompania (str): _description_

        Returns:
            dict: _description_
        """
        DBpath = f'DB/{codigoCompania}.json'
        with open(DBpath) as DBfile:
            return load(DBfile)['config']

    def __init__(self, evento: dict):
        """Constructor de la instancia encargada de procesar el evento

        Args:
            evento (list): Evento de AWS dentro de una lista.
        """
        self.logger = getLogger("Shopify.eventHandler")
        self.NewImage, self.OldImage = Evento.formatearEvento(evento)
        self.cambios = self.obtenerCambios(self.NewImage, self.OldImage)
        self.config = self.obtenerConfiguracion(self.NewImage.codigoCompania)
        self.logger.debug(f'{self.cambios = }')

    def ejecutar(self):
        try:
            if self.cambios or not self.OldImage:
                r = {
                    'articulos': Producto,
                    'lineas': Coleccion,
                    'tiendas': Sucursal
                }[self.NewImage.entity](self).ejecutar()
                # TODO: Revisar la selección de clase.
                return Respuesta(status="OK", data=r)
        except Exception as err:
            return Respuesta(status="ERROR", error=str(err))

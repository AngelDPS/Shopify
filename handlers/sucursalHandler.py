from models.sucursal import MsucursalInput


class Sucursal:

    def parseInput(self, input: dict) -> MsucursalInput:
        return MsucursalInput.parse_obj(input)

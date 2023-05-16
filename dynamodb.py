from json import load, dump
from os import rename

DBpath = 'angel-tabla.json'


def actualizarGidArticulo(PK: str, SK: str, GID: str):
    DBpath_temp = DBpath + '.temp'
    with open(DBpath) as DBfile, open(DBpath_temp, 'w') as DBtemp:
        DB = load(DBfile)
        DB.setdefault(PK, {}).setdefault(SK, {})
        DB[PK][SK]['shopifyGID'] = GID
        dump(DB, DBtemp)
    rename(DBpath_temp, DBpath)


def obtenerTienda(codigoCompania: str, codigoTienda: str
                  ) -> dict[str, dict[str, str]]:
    """Función para obtener el GID asociado a codigoTienda.

    Args:
        use_old (bool): Booleano usado para indicar si se utiliza
        OldImage para extraer el codigo de tienda del artículo

    Returns:
        str: El GID de shopify asociado al código de tienda del artículo.
    """
    PK = f"{codigoCompania.upper()}#TIENDAS"
    SK = f"T#{codigoTienda.upper()}"
    with open(DBpath) as DBfile:
        DB = load(DBfile)
    tienda = DB[PK][SK]
    return tienda


def obtenerNombreTienda(codigoCompania: str, codigoTienda: str
                        ) -> dict[str, str]:
    """Función para obtener el GID asociado a codigoTienda.

    Args:
        use_old (bool): Booleano usado para indicar si se utiliza
        OldImage para extraer el codigo de tienda del artículo

    Returns:
        str: El GID de shopify asociado al código de tienda del artículo.
    """
    PK = f"{codigoCompania.upper()}#TIENDAS"
    SK = f"T#{codigoTienda.upper()}"
    with open(DBpath) as DBfile:
        DB = load(DBfile)
    tienda = DB[PK][SK]
    temp = tienda.copy()
    for k in tienda:
        if k == "nombre":
            continue
        del temp[k]
    return temp


def actualizarGidTienda(codigoCompania: str, codigoTienda: str, GID: str):
    PK = f"{codigoCompania.upper()}#TIENDAS"
    SK = f"T#{codigoTienda.upper()}"
    DBpath_temp = DBpath + '.temp'
    with open(DBpath) as DBfile, open(DBpath_temp, 'w') as DBtemp:
        DB = load(DBfile)
        DB.setdefault(PK, {}).setdefault(SK, {}).setdefault("shopifyGID", {})
        DB[PK][SK]['shopifyGID']['sucursal'] = GID
        dump(DB, DBtemp)
    rename(DBpath_temp, DBpath)


def obtenerGidLinea(codigoCompania: str, codigoTienda: str,
                    co_lin: str) -> dict[str, str]:
    PK = f"{codigoCompania.upper()}#LINEAS"
    SK = f"T#{codigoTienda}#L#{co_lin}"
    with open(DBpath) as DBfile:
        DB = load(DBfile)
    linea = DB[PK][SK]
    temp = linea.copy()
    for k in linea:
        if k == "shopifyGID":
            continue
        del temp[k]
    return temp


def actualizarGidLinea(PK: str, SK: str, GID: str):
    DBpath_temp = DBpath + '.temp'
    with open(DBpath) as DBfile, open(DBpath_temp, 'w') as DBtemp:
        DB = load(DBfile)
        DB.setdefault(PK, {}).setdefault(SK, {})
        DB[PK][SK]['shopifyGID'] = GID
        dump(DB, DBtemp)
    rename(DBpath_temp, DBpath)


def obtenerLinea(codigoCompania: str, codigoTienda: str,
                 co_lin: str) -> dict[str, any]:
    PK = f"{codigoCompania.upper()}#LINEAS"
    SK = f"T#{codigoTienda}#L#{co_lin}"
    with open(DBpath) as DBfile:
        DB = load(DBfile)
    linea = DB[PK][SK]
    return linea


def obtenerGidPublicacionesTienda(codigoCompania: str, codigoTienda: str
                                  ) -> dict[str, dict[str, str]]:
    PK = f"{codigoCompania.upper()}#TIENDAS"
    SK = f"T#{codigoTienda.upper()}"
    with open(DBpath) as DBfile:
        DB = load(DBfile)
    tienda = DB[PK][SK]
    temp = tienda.copy()
    for k in tienda:
        if k == "shopifyGID":
            continue
        del temp[k]
    return temp


def actualizarGidPublicacionesTienda(codigoCompania: str, codigoTienda: str,
                                     pubIDs: list[str]):
    PK = f"{codigoCompania.upper()}#TIENDAS"
    SK = f"T#{codigoTienda.upper()}"
    DBpath_temp = DBpath + '.temp'
    with open(DBpath) as DBfile, open(DBpath_temp, 'w') as DBtemp:
        DB = load(DBfile)
        (DB.setdefault(PK, {})
         .setdefault(SK, {}).
         setdefault('shopifyGID', {}))
        DB[PK][SK]['shopifyGID']['publicaciones'] = pubIDs
        dump(DB, DBtemp)
    rename(DBpath_temp, DBpath)

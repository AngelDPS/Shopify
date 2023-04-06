from pydantic import BaseModel, Field, constr


class _MsucursalAddress(BaseModel):
    """Información relacionada a la dirección de la sucursal
    """
    countryCode: constr(to_upper=True, curtail_length=2) = Field(..., title="Código del país", description="Código ISO 3166-1 alpha-2 del país.", min_length=2, max_length=2)
    provinceCode: constr(to_upper=True) | None = Field(None, title="Código de provincia", description="Código ISO 3166-2 de la provincia del país", min_length=4, max_length=5)
    city: str | None = Field(None, title="Ciudad", description="Ciudad, poblado o distrito en el que se ubica la sucursal.")
    address1: str | None = Field(None, title="Línea 1 de dirección", description="Primera línea para especificar la dirección de la sucursal.", max_lengt=40)
    address2: str | None = Field(None, title="Línea 2 de dirección", description="Segunda línea para especificar la dirección de la sucursal.", max_lengt=40)
    phone: str | None = Field(None, title="Teléfono", description="Número telefónico para llamar a la sucursal.", max_length=15)
    zip: str | None = Field(None, title="Código postal", description="Código zip o postal para enviar correspondencia a la sucursal.")

    
    class Config:
        title = "Dirección de sucursal"
        anystr_strip_whitespace = True


class MsucursalInput(BaseModel):
    """Campos utilizados para añadir una sucursal a una tienda.
    """
    address: _MsucursalAddress
    name: constr(strip_whitespace=True)
    fulfillsOnlineOrders: bool | None = None
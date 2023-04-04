from pydantic import BaseModel, constr


class _MsucursalAddress(BaseModel):
    countryCode: constr(to_upper=True, curtail_length=2)
    provinceCode: constr(strip_whitespace=True) | None = None
    city: constr(strip_whitespace=True) | None = None
    address1: constr(max_length=40, strip_whitespace=True) | None = None
    address2: constr(max_length=40, strip_whitespace=True) | None = None
    phone: constr(strip_whitespace=True) | None = None
    zip: constr(strip_whitespace=True) | None = None


class MsucursalInput(BaseModel):
    address: _MsucursalAddress
    name: constr(strip_whitespace=True)
    fulfillsOnlineOrders: bool | None = None
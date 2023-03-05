from pydantic import BaseModel, Field


class RawCity(BaseModel):
    name: str = Field(..., alias='nom')
    code: str
    zip_codes: list[str] = Field(..., alias='codesPostaux')
    siren: str
    epci: str = Field(..., alias='codeEpci')
    department: str = Field(..., alias='codeDepartement')
    region: str = Field(..., alias='codeRegion')
    population: int


class Input(BaseModel):
    department: str
    surface: float = Field(..., gt=0.0)
    maximum_price: float = Field(..., gt=0.0)


class City(BaseModel):
    average_price: float
    city: str
    note: float
    zip_code: str
    population: int

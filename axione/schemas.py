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

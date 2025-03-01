from pydantic import BaseModel, PositiveInt, Field
from datetime import datetime

class InvoiceRequest(BaseModel):
    client_id: PositiveInt
    year: int = Field(..., ge=2000, le=2100)  
    month: int = Field(..., ge=1, le=12) 
    class Config:
        schema_extra = {
            "example": {
                "client_id": 1,
                "year": 2023,
                "month": 9
            }
        }

class ClientStatsRequest(BaseModel):
    client_id: PositiveInt
    class Config:
        schema_extra = {
                "example": {
                    "client_id": 1
                }
            }

class ClientInvoiceResponse(BaseModel):
    Energia_Activa: float
    Excedentes_Energia: float
    Excedentes_Energia_1: float
    Excedentes_Energia_2: float

class ClientStatsResponse(BaseModel):
    month: str
    total_consumption: float
    total_injection: float

class SystemLoadResponse(BaseModel):
    timestamp: datetime
    hourly_load: float



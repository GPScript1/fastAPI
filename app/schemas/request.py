from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Estado(BaseModel):
    estado: int
    fecha: date

class Factura(BaseModel):
    fecha_facturacion: date
    estado: int
    monto: Optional[float]

class PredictRequest(BaseModel):
    nombre_cliente: str
    correo_vendedor: str
    valor_total: float
    fecha_inicio: date
    estados: List[Estado]
    facturas: List[Factura]
class SujetosPromedioValor(BaseModel):
    nombreEnte: str = Field(..., alias="NombreEnte")
    promedioInicioComFinCom: int = Field(..., alias="PromedioInicioComFinCom")
    promedioFinComInicioFactura: int = Field(..., alias="PromedioFinComInicioFactura")
    promedioInicioFacturaFinPagado: int = Field(..., alias="PromedioInicioFacturaFinPagado")
    promedioInicioComFinPagado: int = Field(..., alias="PromedioInicioComFinPagado")
    cantidadComercializaciones: int = Field(..., alias="CantidadComercializaciones")
    valorTotalComercializaciones: int = Field(..., alias="ValorTotalComercializaciones")
    class Config:
        allow_population_by_field_name = True
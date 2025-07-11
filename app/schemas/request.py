from pydantic import BaseModel
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
    
class Comercializacion(BaseModel):
    nombreEnte: str
    promedioInicioComFinCom: int
    promedioFinComInicioFactura: int
    promedioInicioFacturaFinPagado: int
    promedioInicioComFinPagado: int

from pydantic import BaseModel

class PredictResponse(BaseModel):
    dias_estimados: int

class ModelStatusResponse(BaseModel):
    entrenado: bool
    version: str
    ultima_actualizacion: str

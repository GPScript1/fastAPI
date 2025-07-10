from pydantic import BaseModel

class PredictResponse(BaseModel):
    dias_estimados: int

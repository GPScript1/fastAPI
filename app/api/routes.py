from fastapi import APIRouter, HTTPException
from app.schemas.request import PredictionRequest
from app.services.predictor import predict_payment_time

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
def predict(data: PredictionRequest):
    prediction: predict_payment_time(data)
    # Aquí iría la lógica de predicción
    return {"prediction": "resultado"}
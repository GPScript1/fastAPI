# app/api/routes.py
from fastapi import APIRouter, Body, Depends, HTTPException, Header
from app.core.security import verificar_api_key
from app.schemas.request import PredictRequest, Comercializacion
from app.schemas.response import PredictResponse, ModelStatusResponse
from app.services.predictor import predict_payment_time, train_model, get_model_status, delete_training_data

router = APIRouter()

@router.post("/predict", response_model=PredictResponse)
def predict(data: PredictRequest):
    try:
        prediction = predict_payment_time(data)
        return PredictResponse(dias_estimados=prediction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/model/train")
def train():
    try:
        result = train_model()
        return {"message": "Modelo entrenado correctamente", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/status", response_model=ModelStatusResponse)
def status():
    try:
        status_info = get_model_status()
        return status_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/training-data")
def delete_data():
    try:
        delete_training_data()
        return {"message": "Datos de entrenamiento eliminados"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ping", dependencies=[Depends(verificar_api_key)])
def ping(data: list[Comercializacion] = Body(...)):
    return data
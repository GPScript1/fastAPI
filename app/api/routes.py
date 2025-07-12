# app/api/routes.py
from fastapi import APIRouter, Body, Depends, HTTPException
from app.core.security import verificar_api_key
from app.schemas.request import PrediccionInput, SujetosPromedioValor
from app.services.classificator import cluster_classify
from app.services.predictor import entrenar_modelo

router = APIRouter()

@router.post("/ping", dependencies=[Depends(verificar_api_key)])
def ping(data: list[SujetosPromedioValor] = Body(...)):
    return data

@router.post("/cluster", dependencies=[Depends(verificar_api_key)])
def cluster(data: list[SujetosPromedioValor] = Body(...)):
    try:
        json_data = cluster_classify(data)
        return json_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train", dependencies=[Depends(verificar_api_key)])
def train(data: PrediccionInput = Body(...)):
    try:
        json_data = entrenar_modelo(data)
        return json_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

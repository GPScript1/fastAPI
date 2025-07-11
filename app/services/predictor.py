import joblib
from datetime import datetime
from app.services.preprocessing import generar_features

modelo = None
fecha_entrenamiento = None
tipo_modelo = "RegresionLineal"

MODEL_PATH = "app/models/model.pkl"


def load_model():
    global modelo, fecha_entrenamiento
    modelo = joblib.load(MODEL_PATH)
    fecha_entrenamiento = datetime.now()


def predict_payment_time(data):
    if modelo is None:
        load_model()
    features = generar_features(data)
    return int(modelo.predict([features])[0])


def train_model():
    # Simulando reentrenamiento
    load_model()
    return {"modelo": tipo_modelo, "fecha": fecha_entrenamiento}


def get_model_status():
    return {
        "entrenado": modelo is not None,
        "fecha_entrenamiento": fecha_entrenamiento or datetime.min,
        "tipo_modelo": tipo_modelo
    }


def delete_training_data():
    global modelo
    modelo = None
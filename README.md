
# 🔮 FastAPI - Predicción y Clasificación de Sujetos

Este proyecto utiliza **FastAPI** para exponer servicios RESTful que permiten:
- Entrenar un modelo de predicción de pagos basado en Random Forest.
- Clasificar sujetos en clústeres usando KMeans.
- Predecir días hasta el pago a partir de datos comerciales históricos.

## 🚀 Tecnologías

- Python 3.10+
- FastAPI
- Scikit-learn
- Pandas
- Uvicorn
- Pydantic
- python-dotenv

## ⚙️ Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/GPScript1/fastAPI
cd fastAPI
```

2. Crea un entorno virtual e instálalo:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Crea un archivo `.env`:

```
FASTAPI_API_KEY=tu_api_key
FASTAPI_API_KEY_NAME=api-key
FASTAPI_URL=http://localhost:8000/
```

4. Ejecuta el servidor:

```bash
uvicorn app.main:app --reload
```

## 📬 Endpoints principales

- `POST /predict`: Predice días hasta el pago.
- `POST /cluster`: Clasifica sujetos según sus promedios.
- `POST /entrenar`: Entrena el modelo con nuevos datos.

## 🔐 Seguridad

Se requiere una clave de API en los headers:

```http
api-key: tu_api_key
api-key-name: tu_api_key_name
```

## 🧪 Testing

Puedes usar herramientas como **Postman** o **curl** para probar los endpoints.
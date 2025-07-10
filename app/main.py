from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Modelo Predictivo Insecap")
app.include_router(router)

from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title = "GPScript API",
              description = "API para interactuar con el modelo de GPScript")

app.include_router(api_router)
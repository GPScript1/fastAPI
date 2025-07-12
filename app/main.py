from fastapi import FastAPI
from app.api.routes import router
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Modelo Predictivo Insecap")
app.include_router(router)

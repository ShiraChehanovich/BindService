from fastapi import FastAPI
from src.EntryPoint.controllers.bind import router as bind_router

app = FastAPI()

app.include_router(bind_router)

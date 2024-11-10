import os
from route import main_router

from fastapi import Depends, FastAPI
from db import create_db_and_tables

app = FastAPI(debug=True)

app.include_router(main_router, prefix="/api")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}

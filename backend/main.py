from typing import Union
from route import main_router
from fastapi import FastAPI

app = FastAPI(debug=True)

app.include_router(main_router, prefix="/api")


@app.get("/")
def read_root():
    return {"Hello": "World"}

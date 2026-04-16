from fastapi import FastAPI
from .api import api_router
from .middleware import ProcessTimeMiddleware


app = FastAPI()
app.add_middleware(ProcessTimeMiddleware)
app.include_router(api_router)
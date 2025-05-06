from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from api import users, ingredients, recipes, carbon, admin
import os
from dotenv import load_dotenv
from AI import ai,ai_models,request

load_dotenv()

app = FastAPI(title="GreenMirror AI API")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="GreenMirror AI API",
        version="1.0.0",
        description="Tarif ve karbon ayak izi API'si",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(users.router)
app.include_router(ingredients.router)
app.include_router(recipes.router)
app.include_router(carbon.router)
app.include_router(admin.router)
app.include_router(request.router)
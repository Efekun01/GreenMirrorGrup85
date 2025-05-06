from fastapi import FastAPI, Body, Path, Query, HTTPException, Depends, Request
from starlette.responses import RedirectResponse
from models import Base
from database import engine, SessionLocal
from typing import Annotated,Optional
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from routers.auth import router as auth_router
from routers.recipes import router as recipes_router
from routers.admin import router as admin_router


app = FastAPI()

@app.get("/")
def read_root(request: Request):
    return RedirectResponse(url="/recipes/recipes-page", status_code=status.HTTP_302_FOUND)
app.include_router(auth_router)

app.include_router(recipes_router)

app.include_router(admin_router)

Base.metadata.create_all(bind=engine)
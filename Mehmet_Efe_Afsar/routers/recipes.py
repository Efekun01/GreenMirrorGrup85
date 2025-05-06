from fastapi import APIRouter, Body, Path, Query, HTTPException, Depends, Request
from starlette.responses import RedirectResponse
from models import Base, Recipe
from database import engine, SessionLocal
from typing import Annotated,Optional
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from routers.auth import router as auth_router
from routers.auth import get_current_user


router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)


class RecipeCreate(BaseModel):
    recipe_title: str = Field(min_length=3, max_length=1000)
    description: str = Field(min_length=3, max_length=1000)
    ingredients: str = Field(min_length=3, max_length=1000)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response

@router.get("/recipes-page")
async def render_recipe_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        recipes = db.query(Recipe).filter(Recipe.owner_id == user.get('id')).all()
        return recipes
    except:
        return redirect_to_login()

@router.get("/recipe")
async def read_all(user: user_dependency,db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Recipe).filter(Recipe.owner_id == user.get("id")).all()

@router.get("/recipe/{recipe_id}", status_code=status.HTTP_200_OK)
async def read_by_id(user: user_dependency, db: db_dependency, recipe_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).filter(Recipe.owner_id == user.get('id')).first()
    if recipe is not None:
        return recipe
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Recipe not found")

@router.post("/recipe", status_code=status.HTTP_201_CREATED)
async def create_recipe(user: user_dependency, db: db_dependency, recipe_request: RecipeCreate):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    recipe = Recipe(**recipe_request.model_dump(), owner_id=user.get('id'))
    db.add(recipe)
    db.commit()

@router.put("/recipe/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_recipe(user: user_dependency, db: db_dependency,
                      recipe_request: RecipeCreate,
                      recipe_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).filter(Recipe.owner_id == user.get('id')).first()
    if recipe is None:
        raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    recipe.recipe_title = recipe_request.recipe_title
    recipe.description = recipe_request.description
    recipe.ingredients = recipe_request.ingredients
    db.add(recipe)
    db.commit()

@router.delete("/recipe/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(user: user_dependency, db: db_dependency, recipe_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    recipe_model = db.query(Recipe).filter(Recipe.id == recipe_id).filter(Recipe.owner_id == user.get('id')).first()
    if recipe_model is None:
        raise HTTPException(status_code=404, detail='Recipe not found.')
    db.query(Recipe).filter(Recipe.id == recipe_id).filter(Recipe.owner_id == user.get('id')).delete()

    db.commit()

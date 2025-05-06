from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Ingredient, Recipe

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/ingredients")
async def list_admin_ingredients(db: Session = Depends(get_db)):
    ingredients = db.query(Ingredient).all()
    return {"ingredients": [{"name": i.name, "carbon_footprint": i.carbon_footprint} for i in ingredients]}

@router.post("/ingredients")
async def add_admin_ingredient(name: str, carbon_footprint: float, db: Session = Depends(get_db)):
    db_ingredient = Ingredient(name=name, carbon_footprint=carbon_footprint)
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return {"message": f"Ingredient {name} added by admin"}

@router.put("/ingredients/{name}")
async def update_admin_ingredient(name: str, carbon_footprint: float, db: Session = Depends(get_db)):
    db_ingredient = db.query(Ingredient).filter(Ingredient.name == name).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db_ingredient.carbon_footprint = carbon_footprint
    db.commit()
    db.refresh(db_ingredient)
    return {"message": f"Ingredient {name} updated by admin"}

@router.delete("/ingredients/{name}")
async def delete_admin_ingredient(name: str, db: Session = Depends(get_db)):
    db_ingredient = db.query(Ingredient).filter(Ingredient.name == name).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.delete(db_ingredient)
    db.commit()
    return {"message": f"Ingredient {name} deleted by admin"}

@router.get("/recipes")
async def list_admin_recipes(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).all()
    return {"recipes": [{"name": r.name, "ingredients": r.ingredients, "instructions": r.instructions, "total_carbon_footprint": r.total_carbon_footprint} for r in recipes]}

@router.post("/recipes")
async def add_admin_recipe(name: str, ingredients: str, instructions: str, db: Session = Depends(get_db)):
    ing_list = [ing.strip() for ing in ingredients.split(",")]
    ing_carbon = db.query(Ingredient.carbon_footprint).filter(Ingredient.name.in_(ing_list)).all()
    total_carbon = sum(carbon for (carbon,) in ing_carbon) if ing_carbon else 0.0
    db_recipe = Recipe(name=name, ingredients=ingredients, instructions=instructions, total_carbon_footprint=total_carbon)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return {"message": f"Recipe {name} added by admin"}

@router.put("/recipes/{name}")
async def update_admin_recipe(name: str, ingredients: str, instructions: str, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.name == name).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    ing_list = [ing.strip() for ing in ingredients.split(",")]
    ing_carbon = db.query(Ingredient.carbon_footprint).filter(Ingredient.name.in_(ing_list)).all()
    db_recipe.ingredients = ingredients
    db_recipe.instructions = instructions
    db_recipe.total_carbon_footprint = sum(carbon for (carbon,) in ing_carbon) if ing_carbon else 0.0
    db.commit()
    db.refresh(db_recipe)
    return {"message": f"Recipe {name} updated by admin"}

@router.delete("/recipes/{name}")
async def delete_admin_recipe(name: str, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.name == name).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(db_recipe)
    db.commit()
    return {"message": f"Recipe {name} deleted by admin"}

@router.get("/panel")
async def admin_panel():
    with open("static/admin.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())
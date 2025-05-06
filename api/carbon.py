from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Recipe, Ingredient

router = APIRouter(prefix="/carbon", tags=["carbon"])

@router.get("/calculate-footprint")
async def calculate_footprint(recipe_name: str, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.name == recipe_name).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"recipe_name": recipe.name, "total_carbon_footprint": recipe.total_carbon_footprint}

@router.get("/total-savings")
async def total_savings(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).all()
    total_savings = sum(r.total_carbon_footprint for r in recipes if r.total_carbon_footprint) or 0.0
    return {"total_savings": f"{total_savings} kg CO₂ tasarrufu"}

@router.get("/top-saving-recipes")
async def top_saving_recipes(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).order_by(Recipe.total_carbon_footprint.asc()).limit(5).all()
    return [{"name": r.name, "total_carbon_footprint": r.total_carbon_footprint} for r in recipes]
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Recipe, Ingredient
from gemini_service import ask_gemiai, parse_recipe_suggestion
from typing import List

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.post("")
async def create_recipe(name: str, ingredients: str, instructions: str, db: Session = Depends(get_db)):
    ing_list = [ing.strip() for ing in ingredients.split(",")]
    ing_carbon = db.query(Ingredient.carbon_footprint).filter(Ingredient.name.in_(ing_list)).all()
    total_carbon = sum(carbon for (carbon,) in ing_carbon) if ing_carbon else 0.0
    db_recipe = Recipe(name=name, ingredients=ingredients, instructions=instructions, total_carbon_footprint=total_carbon)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return {"message": "Recipe created", "recipe": {"name": db_recipe.name, "total_carbon_footprint": db_recipe.total_carbon_footprint}}

@router.get("")
async def list_recipes(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).all()
    return [{"name": r.name, "ingredients": r.ingredients, "instructions": r.instructions, "total_carbon_footprint": r.total_carbon_footprint} for r in recipes]

@router.put("/{name}")
async def update_recipe(name: str, ingredients: str, instructions: str, db: Session = Depends(get_db)):
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
    return {"message": f"Recipe {name} updated"}

@router.delete("/{name}")
async def delete_recipe(name: str, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.name == name).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(db_recipe)
    db.commit()
    return {"message": f"Recipe {name} deleted"}

@router.post("/suggest")
async def suggest_recipe(ingredients: List[str], db: Session = Depends(get_db)):
    try:
        ingredients_text = ", ".join(ingredients)
        prompt = (
            f"Benim elimde şu malzemeler var: {ingredients_text}.\n"
            "Bu malzemelerle yapabileceğim, düşük karbon ayak izine sahip, bitki bazlı bir yemek tarifi önerir misin?\n"
            "Tarifin adı, malzemeleri ve nasıl yapılacağını belirt lütfen."
        )
        ai_response = await ask_gemiai(prompt)
        parsed_recipe = await parse_recipe_suggestion(ai_response)

        ing_list = [ing.strip() for ing in parsed_recipe["ingredients"]]
        ing_carbon = db.query(Ingredient.carbon_footprint).filter(Ingredient.name.in_(ing_list)).all()
        total_carbon = sum(carbon for (carbon,) in ing_carbon) if ing_carbon else 0.0

        db_recipe = Recipe(
            name=parsed_recipe["name"],
            ingredients=", ".join(parsed_recipe["ingredients"]),
            instructions=parsed_recipe["instructions"],
            total_carbon_footprint=total_carbon
        )
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)

        return {
            "ingredients": ingredients,
            "recipe_suggestion": parsed_recipe,
            "total_carbon_footprint": total_carbon
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tarif önerme hatası: {str(e)}")
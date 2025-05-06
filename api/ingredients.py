from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from database import get_db
from models import Ingredient
from gemini_service import ask_gemiai
import re
from typing import List

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

def extract_main_ingredient(ingredient_str):
    s = re.sub(r"\([^)]*\)", "", ingredient_str)  # parantez içi
    s = re.sub(r"\d+\s*[a-zA-ZçğıöşüÇĞİÖŞÜ\.]*", "", s)  # sayı ve birim
    s = s.replace("-", " ").replace(",", " ")
    return s.strip().lower().split()[-1] if s.strip().lower().split() else s.strip().lower()

async def get_carbon_footprint_from_ai(name: str) -> float:
    prompt = f"{name} malzemesinin 1 kg başına ortalama karbon ayak izi nedir? Sadece sayısal bir değer (ör: 1.2) olarak cevap ver."
    try:
        response = await ask_gemiai(prompt)
        print("AI karbon cevabı:", response)
        match = re.search(r"([0-9]+[.,]?[0-9]*)", response)
        if match:
            value = float(match.group(1).replace(",", "."))
        else:
            value = 0.0
        return value
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI ile karbon ayak izi hesaplanamadı: {str(e)}")

@router.post("")
async def add_ingredient(name: str, carbon_footprint: float = None, db: Session = Depends(get_db), api_key: str = Security(lambda: "admin-secret-key")):
    if api_key != "admin-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    if carbon_footprint is None:
        carbon_footprint = await get_carbon_footprint_from_ai(name)
    db_ingredient = Ingredient(name=name, carbon_footprint=carbon_footprint)
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return {"message": f"Ingredient {name} added", "ingredient": {"name": db_ingredient.name, "carbon_footprint": db_ingredient.carbon_footprint}}

@router.post("/calculate-meal-footprint")
async def calculate_meal_footprint(items: List[str], db: Session = Depends(get_db)):
    total = 0.0
    missing = []
    for item in items:
        for word in item.lower().replace(",", " ").split():
            ingredient = db.query(Ingredient).filter(Ingredient.name == word.strip()).first()
            if ingredient:
                total += ingredient.carbon_footprint
            else:
                # Ingredient tablosunda yoksa AI'dan karbon ayak izi çek
                ai_footprint = await get_carbon_footprint_from_ai(word)
                total += ai_footprint
                missing.append(word)
    return {
        "total_carbon_footprint": total,
        "not_found": missing
    }

@router.put("/{name}")
async def update_ingredient(name: str, carbon_footprint: float, db: Session = Depends(get_db), api_key: str = Security(lambda: "admin-secret-key")):
    if api_key != "admin-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    db_ingredient = db.query(Ingredient).filter(Ingredient.name == name).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db_ingredient.carbon_footprint = carbon_footprint
    db.commit()
    db.refresh(db_ingredient)
    return {"message": f"Ingredient {name} updated"}

@router.delete("/{name}")
async def delete_ingredient(name: str, db: Session = Depends(get_db), api_key: str = Security(lambda: "admin-secret-key")):
    if api_key != "admin-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    db_ingredient = db.query(Ingredient).filter(Ingredient.name == name).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.delete(db_ingredient)
    db.commit()
    return {"message": f"Ingredient {name} deleted"}

@router.get("")
async def list_ingredients(db: Session = Depends(get_db)):
    ingredients = db.query(Ingredient).all()
    return [{"name": i.name, "carbon_footprint": i.carbon_footprint} for i in ingredients]
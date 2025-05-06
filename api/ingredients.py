from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from database import get_db
from models import Ingredient
from gemini_service import ask_gemiai
import re

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

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
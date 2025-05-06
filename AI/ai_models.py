from pydantic import BaseModel
from typing import List

class Ingredient(BaseModel):
    name: str
    carbon_footprint: float

class Recipe(BaseModel):
    name: str
    ingredients: List[str]
    instructions: str

class AIRequest(BaseModel):
    prompt: str

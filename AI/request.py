# request.py
from fastapi import APIRouter, Depends, HTTPException, Security, Body
from AI.ai import ask_gemiai
from AI.ai_models import AIRequest
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv
from typing import List

router = APIRouter()

load_dotenv()


API_KEY = os.getenv("API_KEY", "123456")
api_key_header = APIKeyHeader(name="X_API_Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Yetkisiz")
    return api_key

@router.post("/ai/chat", tags=["AI"], summary="AI ile sohbet et", dependencies=[Depends(verify_api_key)])
async def chat_ai(request: AIRequest):
    try:
        ai_response = await ask_gemiai(request.prompt)
        return {"response": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI hatası: {str(e)}")

@router.post("/ai/recipe_suggest", tags=["AI"], summary="AI tarif önerisi ver", dependencies=[Depends(verify_api_key)])
async def suggest_recipe(ingredients: List[str] = Body(..., embed=True)):
    try:
        ingredients_text = ", ".join(ingredients)
        prompt = (
            f"Benim elimde şu malzemeler var: {ingredients_text}.\n"
            "Bu malzemelerle yapabileceğim, düşük karbon ayak izine sahip, bitki bazlı bir yemek tarifi önerir misin?\n"
            "Tarifin adı, malzemeleri ve nasıl yapılacağını belirt lütfen."
        )
        ai_response = await ask_gemiai(prompt)
        return {"ingredients": ingredients, "recipe_suggestion": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tarif önerme hatası: {str(e)}")

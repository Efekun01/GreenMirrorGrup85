import google.generativeai as genai
import os
from dotenv import load_dotenv
import asyncio
import re

load_dotenv()  # .env dosyasını yükle
GEMIAI_API_KEY = os.getenv("GEMIAI_API_KEY")

if not GEMIAI_API_KEY:
    raise ValueError("GEMIAI_API_KEY ortam değişkeni bulunamadı. .env dosyasını kontrol edin.")

genai.configure(api_key=GEMIAI_API_KEY)

async def ask_gemiai(message: str) -> str:
    loop = asyncio.get_event_loop()
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = await loop.run_in_executor(None, lambda: model.generate_content(message))
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API hatası: {str(e)}")

async def parse_recipe_suggestion(ai_response: str) -> dict:
    print("AI tarif cevabı:", ai_response)
    try:
        # Tarifin adı
        name_match = re.search(r"Tarif(in adı|:)?[:\s]*([^\n]+)", ai_response, re.IGNORECASE)
        name = name_match.group(2).strip() if name_match else ""
        # Malzemeler
        ingredients_match = re.search(r"Malzemeler[:\s]*([\s\S]+?)(?:Yapılışı|Nasıl yapılacağı|$)", ai_response, re.IGNORECASE)
        ingredients = []
        if ingredients_match:
            # Satır satır veya virgülle ayrılmış olabilir
            raw_ings = ingredients_match.group(1).strip()
            if "\n" in raw_ings:
                ingredients = [i.strip("-* ") for i in raw_ings.split("\n") if i.strip()]
            else:
                ingredients = [i.strip() for i in raw_ings.split(",") if i.strip()]
        # Yapılışı
        instructions_match = re.search(r"(Yapılışı|Nasıl yapılacağı)[:\s]*([\s\S]+)", ai_response, re.IGNORECASE)
        instructions = instructions_match.group(2).strip() if instructions_match else ""
        if not name or not ingredients or not instructions:
            raise ValueError("Tarif formatı uygun değil")
        return {
            "name": name,
            "ingredients": ingredients,
            "instructions": instructions
        }
    except Exception as e:
        raise Exception(f"Tarif parse hatası: {str(e)}")
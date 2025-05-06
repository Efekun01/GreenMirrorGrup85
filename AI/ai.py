import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

GEMIAI_API_KEY = os.getenv("GEMIAI_API_KEY")


genai.configure(api_key=GEMIAI_API_KEY)


async def ask_gemiai(message: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API hatası: {str(e)}")

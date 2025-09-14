import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_ai_response(prompt: str, context: str) -> str:
    """
    Google Gemini 1.5 Flash API orqali AI javobini olish
    
    Args:
        prompt: Foydalanuvchi so'rovi
        context: Yuklangan fayldan olingan matn konteksti
    
    Returns:
        AI javob matni
    """
    try:
        # Gemini modelini olish
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Promptni tayyorlash
        if context and context.strip():
            full_prompt = f"""
Kontekst ma'lumotlari:
{context}

Foydalanuvchi so'rovi:
{prompt}

Yuqoridagi kontekst ma'lumotlari asosida foydalanuvchi so'roviga javob bering. Agar kontekstda kerakli ma'lumot bo'lmasa, umumiy bilimlaringizdan foydalaning. Javobni o'zbek tilida bering.
"""
        else:
            full_prompt = f"""
Foydalanuvchi so'rovi:
{prompt}

Iltimos, ushbu so'rovga o'zbek tilida javob bering.
"""
        
        # AI javobini olish
        response = model.generate_content(full_prompt)
        
        if response.text:
            return response.text
        else:
            return "Kechirasiz, AI javob bera olmadi. Iltimos, so'rovingizni boshqacha ifoda eting."
    
    except Exception as e:
        error_message = str(e)
        if "API_KEY" in error_message.upper():
            return "Kechirasiz, AI xizmati sozlanmagan. Administrator bilan bog'laning."
        elif "QUOTA" in error_message.upper():
            return "Kechirasiz, API limitiga yetdik. Keyinroq urinib ko'ring."
        else:
            return f"Kechirasiz, AI bilan bog'lanishda xatolik yuz berdi: {error_message}"
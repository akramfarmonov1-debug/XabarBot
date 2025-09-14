import google.generativeai as genai
from langdetect import detect
import os

def get_ai_response(prompt, context=None, language='uz'):
    """Get AI response from Google Gemini with context"""
    try:
        # Detect language if not provided
        if not language or language == 'auto':
            try:
                language = detect(prompt)
                if language not in ['uz', 'ru', 'en']:
                    language = 'uz'
            except:
                language = 'uz'
        
        # Language-specific system prompts
        system_prompts = {
            'uz': """Siz yordamchi AI assistentsiz. Foydalanuvchi savollariga aniq va foydali javoblar bering. 
                     Agar kontekst berilgan bo'lsa, uni asosiy ma'lumot manbai sifatida ishlatib javob bering.
                     Javoblaringiz qisqa, aniq va tushunarli bo'lsin.""",
            'ru': """Вы AI-помощник. Отвечайте точно и полезно на вопросы пользователя. 
                     Если предоставлен контекст, используйте его как основной источник информации.
                     Ваши ответы должны быть краткими, точными и понятными.""",
            'en': """You are an AI assistant. Provide accurate and helpful answers to user questions. 
                     If context is provided, use it as the primary source of information.
                     Keep your answers concise, accurate and understandable."""
        }
        
        system_prompt = system_prompts.get(language, system_prompts['uz'])
        
        # Prepare the full prompt
        if context:
            full_prompt = f"""
{system_prompt}

Kontekst/Context/Контекст:
{context[:3000]}  # Limit context to avoid token limits

Savol/Question/Вопрос: {prompt}

Javob/{language} tilida bering:
"""
        else:
            full_prompt = f"{system_prompt}\n\nSavol: {prompt}\n\nJavob:"
        
        # Get response from Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        
        return response.text if response.text else "Kechirasiz, javob berish mumkin emas."
        
    except Exception as e:
        error_messages = {
            'uz': "Xatolik yuz berdi. Qaytadan urinib ko'ring.",
            'ru': "Произошла ошибка. Попробуйте еще раз.", 
            'en': "An error occurred. Please try again."
        }
        return error_messages.get(language, error_messages['uz'])
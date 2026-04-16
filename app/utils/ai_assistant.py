import google.generativeai as genai
from app.config.settings import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

async def get_doctor_suggestion(symptoms: str) -> dict:
    prompt = f"""
You are a medical assistant. A patient has these symptoms: {symptoms}

Reply in JSON format only:
{{
    "specialization": "which doctor specialization they need",
    "reason": "why this specialization",
    "urgency": "low/medium/high",
    "tips": "basic home care tips"
}}
"""
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Clean JSON
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    import json
    return json.loads(text)
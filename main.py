import os
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import google.generativeai as genai

# O'zimiz yaratgan fayllardan import qilamiz
from schemas import ChatRequest, ChatResponse
from database import get_db, ChatHistory

load_dotenv()

# 1. AI-ni sozlash
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# model = genai.GenerativeModel(
#     model_name="gemini-1.5-flash",
#     system_instruction="Sen interaktiv ingliz tili o'qituvchisisan. Xatolarni tuzat va o'zbekcha tushuntir."
# )
# for m in genai.list_models():
#     if 'generateContent' in m.supported_generation_methods:
#         print(f"Siz foydalana oladigan model: {m.name}")


# Biz ro'yxatdagi eng yangi va tezkor modelni tanlaymiz
model = genai.GenerativeModel(
    model_name="models/gemini-3-flash-preview",
    system_instruction=(
        "Sen yengiltak (sexy) qizsan . "
        "User bilan sevgi xaqida suhbat qurasan. "
        "Har doim suhbatni qiziqarli savol bilan davom ettir."
    )
)


app = FastAPI(title="AI Tutor Backend")


# 2. Chat funksiyasi (Asosiy mantiq)
@app.post("/chat", response_model=ChatResponse)
def chat_with_ai(data: ChatRequest, db: Session = Depends(get_db)):

    try:
        # a) Bazadan ushbu foydalanuvchining oldingi suhbatlarini olamiz
        history_records = db.query(ChatHistory).filter(ChatHistory.user_id == data.user_id).all()

        # b) Gemini tushunadigan formatga o'tkazamiz
        formatted_history = [
            {"role": rec.role, "parts": [rec.content]} for rec in history_records
        ]

        # d) AI bilan suhbatni boshlaymiz (tarix bilan birga)
        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(data.message)
        ai_text = response.text

        # e) YANGI GAPLARNI BAZAGA SAQLAYMIZ
        # Foydalanuvchi gapi
        user_entry = ChatHistory(user_id=data.user_id, role="user", content=data.message)
        # AI javobi
        ai_entry = ChatHistory(user_id=data.user_id, role="model", content=ai_text)

        db.add(user_entry)
        db.add(ai_entry)
        db.commit()  # Bazaga muhrlaymiz

        return ChatResponse(response=ai_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def home():
    return {"status": "Database va AI ulangan! 🚀"}


print("1 - DB OK")
print("2 - Chat started")
print("3 - Before send_message")
print("4 - After send_message")

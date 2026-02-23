import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 🔥 TO‘G‘RI MODEL
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="You are a helpful AI assistant."
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ⚡ Async va tez ishlaydigan versiya
@app.post("/chat")
async def chat(data: dict):
    response = await model.generate_content_async(data["message"])
    return {"response": response.text}
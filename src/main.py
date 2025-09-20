from fastapi import FastAPI

from src.routers import whatsapp

app = FastAPI(title="SIH Health Chatbot Backend")

app.include_router(whatsapp.router)


@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Backend is running 🚀"}

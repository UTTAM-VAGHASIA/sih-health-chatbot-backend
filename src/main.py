from fastapi import FastAPI

app = FastAPI(title="SIH Health Chatbot Backend")

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Backend is running 🚀"}

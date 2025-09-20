import os

import httpx
from fastapi import APIRouter, Request, Response

router = APIRouter()

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")


@router.get("/webhook/whatsapp")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
        # Return the raw challenge (plain text)
        return Response(content=str(challenge), media_type="text/plain")
    return Response(content="verification failed", status_code=400)


@router.post("/webhook/whatsapp")
async def receive_message(payload: dict):
    try:
        message = payload["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = message["from"]
        text = message["text"]["body"]

        # Echo back
        url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {
            "messaging_product": "whatsapp",
            "to": sender,
            "text": {"body": f"You said: {text}"},
        }
        async with httpx.AsyncClient() as client:
            await client.post(url, headers=headers, json=data)

        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

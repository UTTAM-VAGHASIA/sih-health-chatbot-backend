# src/routers/whatsapp.py
import logging
import os

import requests
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")  # from Meta dashboard
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_API_URL = "https://graph.facebook.com/v23.0"  # use your version


# ✅ Step 1: Verification (GET)
@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    # If no parameters provided, return a helpful message
    if not hub_mode and not hub_challenge and not hub_verify_token:
        return JSONResponse(
            content={
                "message": "WhatsApp webhook endpoint. Use POST for messages or GET with verification parameters."
            },
            status_code=200,
        )

    # Verify webhook subscription
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)

    return JSONResponse(content={"error": "Invalid verify token"}, status_code=403)


# ✅ Step 2: Handle messages (POST → echo)
@router.post("")
async def receive_message(request: Request):
    try:
        body = await request.json()
        logger.info(f"Received webhook payload: {body}")

        if "entry" in body:
            for entry in body["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    if messages:
                        msg = messages[0]
                        from_number = msg["from"]
                        text = msg.get("text", {}).get("body")

                        if text:
                            logger.info(f"Sending echo message to {from_number}: {text}")
                            send_message(from_number, f"Echo: {text}")

        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)


def send_message(to: str, message: str):
    """Send message back via WhatsApp Cloud API"""
    try:
        url = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "text": {"body": message},
        }
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            logger.info(f"Message sent successfully to {to}")
        else:
            logger.error(f"Failed to send message: {response.status_code} - {response.text}")

        return response.json()
    except Exception as e:
        logger.error(f"Error sending message to {to}: {e}")
        return {"error": str(e)}

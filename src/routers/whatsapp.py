# src/routers/whatsapp.py
import logging
import os
from typing import Any, Dict

import requests
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from src.services.message_service import message_service
from src.services.user_service import UserService

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


# ✅ Step 2: Handle messages (POST → intelligent responses)
@router.post("")
async def receive_message(request: Request):
    """
    Handle incoming WhatsApp messages with intelligent responses.

    This endpoint processes webhook messages from WhatsApp, automatically registers users,
    generates intelligent responses using the Message Service, and handles errors gracefully.

    Requirements addressed: 1.1, 1.2, 1.3, 1.4, 3.1, 3.2, 3.3, 4.1
    """
    try:
        body = await request.json()
        logger.info(f"Received webhook payload: {body}")

        # Validate webhook payload structure
        if not isinstance(body, dict) or "entry" not in body:
            logger.warning("Invalid webhook payload structure")
            return JSONResponse(content={"error": "Invalid webhook payload"}, status_code=400)

        # Process each entry in the webhook
        for entry in body["entry"]:
            if not isinstance(entry, dict):
                logger.warning(f"Invalid entry format: {entry}")
                continue

            await process_webhook_entry(entry)

        return {"status": "received"}

    except ValueError as e:
        logger.error(f"Validation error processing webhook: {e}")
        return JSONResponse(content={"error": "Invalid request data"}, status_code=400)
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {e}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)


async def process_webhook_entry(entry: Dict[str, Any]) -> None:
    """
    Process a single webhook entry containing WhatsApp changes.

    Args:
        entry: Webhook entry containing changes and metadata
    """
    try:
        changes = entry.get("changes", [])
        if not changes:
            logger.debug("No changes found in webhook entry")
            return

        for change in changes:
            if not isinstance(change, dict):
                logger.warning(f"Invalid change format: {change}")
                continue

            await process_webhook_change(change)

    except Exception as e:
        logger.error(f"Error processing webhook entry: {e}")


async def process_webhook_change(change: Dict[str, Any]) -> None:
    """
    Process a single webhook change containing message data.

    Args:
        change: Webhook change containing value and message data
    """
    try:
        value = change.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            logger.debug("No messages found in webhook change")
            return

        # Process each message (typically one per webhook)
        for message in messages:
            if not isinstance(message, dict):
                logger.warning(f"Invalid message format: {message}")
                continue

            await process_user_message(message)

    except Exception as e:
        logger.error(f"Error processing webhook change: {e}")


async def process_user_message(message: Dict[str, Any]) -> None:
    """
    Process a single user message with intelligent response generation.

    This function handles:
    - User registration (automatic on first message)
    - Message content extraction and validation
    - Intelligent response generation via Message Service
    - Response delivery via WhatsApp API
    - Error handling and fallback responses

    Args:
        message: WhatsApp message object containing sender and content
    """
    try:
        # Extract message data
        from_number = message.get("from")
        message_text = message.get("text", {}).get("body")
        message_id = message.get("id")

        if not from_number:
            logger.warning("Message missing sender information")
            return

        logger.info(f"Processing message from {from_number}: {message_text}")

        # Handle automatic user registration and activity tracking
        try:
            user = UserService.process_user_message(from_number)
            logger.debug(f"User processed: {user.phone_number} (messages: {user.message_count})")
        except Exception as e:
            logger.error(f"User registration/update failed for {from_number}: {e}")
            # Continue processing even if user registration fails

        # Generate intelligent response
        if message_text:
            try:
                response = message_service.generate_response(message_text, from_number)
                logger.info(f"Generated response for {from_number}: {response.content[:50]}...")

                # Send response via WhatsApp API
                send_result = send_message(from_number, response.content)

                if send_result.get("error"):
                    logger.error(f"Failed to send response to {from_number}: {send_result['error']}")
                    # Try sending fallback message
                    fallback_response = message_service.process_error_message("network")
                    send_message(from_number, fallback_response.content)

            except Exception as e:
                logger.error(f"Error generating response for {from_number}: {e}")
                # Send error fallback message
                try:
                    fallback_response = message_service.process_error_message("processing")
                    send_message(from_number, fallback_response.content)
                except Exception as fallback_error:
                    logger.error(f"Failed to send fallback message to {from_number}: {fallback_error}")
        else:
            logger.info(f"Received non-text message from {from_number}, message_id: {message_id}")
            # Handle non-text messages (images, documents, etc.)
            non_text_response = (
                "Thanks for your message! I currently support text messages. Please send me a text to get started."
            )
            send_message(from_number, non_text_response)

    except Exception as e:
        logger.error(f"Unexpected error processing user message: {e}")
        # Last resort - try to send a basic error message
        if "from_number" in locals() and from_number:
            try:
                send_message(from_number, "Sorry, I'm having technical difficulties. Please try again later.")
            except Exception as fallback_error:
                logger.error(f"Failed to send final fallback message to {from_number}: {fallback_error}")


def send_message(to: str, message: str) -> Dict[str, Any]:
    """
    Send message back via WhatsApp Cloud API with enhanced error handling.

    Args:
        to: Recipient phone number
        message: Message content to send

    Returns:
        Dict containing response data or error information
    """
    if not to or not message:
        error_msg = "Missing recipient or message content"
        logger.error(error_msg)
        return {"error": error_msg}

    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        error_msg = "WhatsApp API credentials not configured"
        logger.error(error_msg)
        return {"error": error_msg}

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

        logger.debug(f"Sending message to {to} via WhatsApp API")
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        # Parse response
        try:
            response_data = response.json()
        except ValueError:
            response_data = {"raw_response": response.text}

        if response.status_code == 200:
            logger.info(f"Message sent successfully to {to}")
            return response_data
        elif response.status_code == 401:
            error_msg = "WhatsApp API authentication failed - check access token"
            logger.error(f"{error_msg}: {response.text}")
            return {"error": error_msg, "status_code": 401}
        elif response.status_code == 400:
            error_msg = f"Bad request to WhatsApp API: {response.text}"
            logger.error(error_msg)
            return {"error": error_msg, "status_code": 400}
        elif response.status_code == 429:
            error_msg = "WhatsApp API rate limit exceeded"
            logger.warning(f"{error_msg}: {response.text}")
            return {"error": error_msg, "status_code": 429}
        else:
            error_msg = f"WhatsApp API error: {response.status_code}"
            logger.error(f"{error_msg} - {response.text}")
            return {"error": error_msg, "status_code": response.status_code, "details": response.text}

    except requests.exceptions.Timeout:
        error_msg = "WhatsApp API request timeout"
        logger.error(f"{error_msg} for recipient {to}")
        return {"error": error_msg}
    except requests.exceptions.ConnectionError:
        error_msg = "WhatsApp API connection error"
        logger.error(f"{error_msg} for recipient {to}")
        return {"error": error_msg}
    except requests.exceptions.RequestException as e:
        error_msg = f"WhatsApp API request failed: {str(e)}"
        logger.error(f"{error_msg} for recipient {to}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error sending message: {str(e)}"
        logger.error(f"{error_msg} to {to}")
        return {"error": error_msg}

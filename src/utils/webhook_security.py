# src/utils/webhook_security.py
"""
Webhook security utilities for WhatsApp webhook verification.

This module provides functions for verifying webhook signatures and
ensuring the authenticity of incoming webhook requests from WhatsApp.
"""

import hashlib
import hmac
import logging
from typing import Optional

from src.config import Config
from src.utils.error_handlers import WebhookValidationError

logger = logging.getLogger(__name__)


def verify_webhook_signature(payload: bytes, signature: str, secret: Optional[str] = None) -> bool:
    """
    Verify WhatsApp webhook signature for security.

    WhatsApp sends a signature in the X-Hub-Signature-256 header that can be used
    to verify that the webhook payload came from WhatsApp and hasn't been tampered with.

    Args:
        payload: Raw webhook payload bytes
        signature: Signature from X-Hub-Signature-256 header
        secret: Webhook secret (defaults to config value)

    Returns:
        True if signature is valid, False otherwise

    Raises:
        WebhookValidationError: If signature format is invalid
    """
    webhook_secret = secret or Config.WHATSAPP_VERIFY_TOKEN

    # If no secret is configured, log warning and skip verification
    if not webhook_secret:
        logger.warning("Webhook signature verification skipped - no secret configured")
        return True

    # DEVELOPMENT MODE: Skip signature verification for easier testing
    if Config.ENVIRONMENT == "development":
        logger.info("Webhook signature verification skipped - development mode")
        return True

    # Validate signature format
    if not signature:
        logger.warning("Missing webhook signature")
        return False

    # WhatsApp sends signature as "sha256=<hash>"
    if not signature.startswith("sha256="):
        logger.error(f"Invalid signature format: {signature[:20]}...")
        raise WebhookValidationError("Invalid signature format - must start with 'sha256='")

    # Extract the hash part
    received_hash = signature[7:]  # Remove "sha256=" prefix

    try:
        # Calculate expected signature
        expected_signature = hmac.new(webhook_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

        # Use secure comparison to prevent timing attacks
        is_valid = hmac.compare_digest(expected_signature, received_hash)

        if is_valid:
            logger.debug("Webhook signature verification successful")
        else:
            logger.warning("Webhook signature verification failed")
            logger.debug(f"Expected: {expected_signature}")
            logger.debug(f"Received: {received_hash}")

        return is_valid

    except Exception as e:
        logger.error(f"Error during signature verification: {str(e)}")
        raise WebhookValidationError(f"Signature verification error: {str(e)}")


def validate_webhook_payload_structure(payload: dict) -> None:
    """
    Validate the basic structure of a WhatsApp webhook payload.

    Args:
        payload: Parsed webhook payload dictionary

    Raises:
        WebhookValidationError: If payload structure is invalid
    """
    if not isinstance(payload, dict):
        raise WebhookValidationError("Payload must be a JSON object")

    # Check for required top-level fields
    if "object" not in payload:
        raise WebhookValidationError("Missing 'object' field in webhook payload")

    if payload.get("object") != "whatsapp_business_account":
        raise WebhookValidationError(f"Invalid object type: {payload.get('object')}")

    if "entry" not in payload:
        raise WebhookValidationError("Missing 'entry' field in webhook payload")

    if not isinstance(payload["entry"], list):
        raise WebhookValidationError("'entry' field must be an array")

    if len(payload["entry"]) == 0:
        raise WebhookValidationError("'entry' array cannot be empty")

    logger.debug("Webhook payload structure validation passed")


def validate_webhook_entry(entry: dict) -> None:
    """
    Validate the structure of a webhook entry.

    Args:
        entry: Individual entry from webhook payload

    Raises:
        WebhookValidationError: If entry structure is invalid
    """
    if not isinstance(entry, dict):
        raise WebhookValidationError("Webhook entry must be an object")

    required_fields = ["id", "changes"]
    for field in required_fields:
        if field not in entry:
            raise WebhookValidationError(f"Missing required field '{field}' in webhook entry")

    if not isinstance(entry["changes"], list):
        raise WebhookValidationError("'changes' field must be an array")

    logger.debug(f"Webhook entry validation passed for entry ID: {entry.get('id')}")


def validate_webhook_change(change: dict) -> None:
    """
    Validate the structure of a webhook change.

    Args:
        change: Individual change from webhook entry

    Raises:
        WebhookValidationError: If change structure is invalid
    """
    if not isinstance(change, dict):
        raise WebhookValidationError("Webhook change must be an object")

    required_fields = ["value", "field"]
    for field in required_fields:
        if field not in change:
            raise WebhookValidationError(f"Missing required field '{field}' in webhook change")

    # Validate field type
    if change.get("field") != "messages":
        logger.debug(f"Ignoring non-message webhook change: {change.get('field')}")
        return

    # Validate value structure for message changes
    value = change.get("value", {})
    if not isinstance(value, dict):
        raise WebhookValidationError("Webhook change 'value' must be an object")

    logger.debug("Webhook change validation passed")


def sanitize_phone_number(phone_number: str) -> str:
    """
    Sanitize and normalize phone number from webhook.

    Args:
        phone_number: Raw phone number from webhook

    Returns:
        Sanitized phone number

    Raises:
        WebhookValidationError: If phone number is invalid
    """
    if not phone_number or not isinstance(phone_number, str):
        raise WebhookValidationError("Invalid phone number format")

    # Remove any whitespace
    sanitized = phone_number.strip()

    # Basic validation - should be digits with optional + prefix
    if not sanitized.replace("+", "").isdigit():
        raise WebhookValidationError("Phone number contains invalid characters")

    # Ensure it starts with +
    if not sanitized.startswith("+"):
        sanitized = f"+{sanitized}"

    # Basic length validation (international numbers are typically 7-15 digits)
    digits_only = sanitized[1:]  # Remove + prefix
    if len(digits_only) < 7 or len(digits_only) > 15:
        raise WebhookValidationError("Phone number length is invalid")

    logger.debug(f"Phone number sanitized: {phone_number} -> {sanitized}")
    return sanitized


def extract_message_content(message: dict) -> dict:
    """
    Extract and validate message content from webhook message object.

    Args:
        message: Message object from webhook

    Returns:
        Dictionary with extracted message content

    Raises:
        WebhookValidationError: If message structure is invalid
    """
    if not isinstance(message, dict):
        raise WebhookValidationError("Message must be an object")

    # Extract basic message info
    extracted = {
        "id": message.get("id"),
        "from": message.get("from"),
        "timestamp": message.get("timestamp"),
        "type": message.get("type", "unknown"),
    }

    # Validate required fields
    if not extracted["id"]:
        raise WebhookValidationError("Message missing ID")

    if not extracted["from"]:
        raise WebhookValidationError("Message missing sender information")

    # Sanitize phone number
    try:
        extracted["from"] = sanitize_phone_number(extracted["from"])
    except WebhookValidationError as e:
        raise WebhookValidationError(f"Invalid sender phone number: {str(e)}")

    # Extract content based on message type
    if extracted["type"] == "text":
        text_content = message.get("text", {})
        if isinstance(text_content, dict):
            extracted["content"] = text_content.get("body", "")
        else:
            extracted["content"] = ""
    else:
        # For non-text messages, we don't extract content but note the type
        extracted["content"] = None

    logger.debug(f"Message content extracted: ID={extracted['id']}, Type={extracted['type']}")
    return extracted

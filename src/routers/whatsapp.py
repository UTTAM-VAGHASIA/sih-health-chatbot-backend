# src/routers/whatsapp.py
"""
Enhanced WhatsApp Router with comprehensive error handling and security.

This router handles WhatsApp webhook verification and message processing with:
- Webhook signature verification for security
- Comprehensive error handling and logging
- Fallback responses for API failures
- Structured error responses for malformed requests
"""

from typing import Any, Dict

import requests
from fastapi import APIRouter, Header, Query, Request, status
from fastapi.responses import JSONResponse

from src.config import Config, get_logger
from src.services.message_service import message_service
from src.services.user_service import UserService
from src.utils.error_handlers import (
    MessageProcessingError,
    WebhookValidationError,
    create_error_response,
    log_error_with_context,
)
from src.utils.webhook_security import (
    extract_message_content,
    validate_webhook_change,
    validate_webhook_entry,
    validate_webhook_payload_structure,
    verify_webhook_signature,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])

# Configuration from centralized config
VERIFY_TOKEN = Config.WHATSAPP_VERIFY_TOKEN
ACCESS_TOKEN = Config.WHATSAPP_ACCESS_TOKEN
PHONE_NUMBER_ID = Config.WHATSAPP_PHONE_NUMBER_ID
WHATSAPP_API_URL = Config.WHATSAPP_API_URL


# ✅ Step 1: Enhanced Webhook Verification (GET)
@router.get("")
async def verify_webhook(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Enhanced WhatsApp webhook verification with comprehensive logging and error handling.

    This endpoint handles webhook verification requests from WhatsApp with:
    - Detailed logging of verification attempts
    - Proper error responses for invalid tokens
    - Security validation and monitoring

    Requirements addressed: 3.1, 3.4, 3.5
    """
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        # If no parameters provided, return a helpful message
        if not hub_mode and not hub_challenge and not hub_verify_token:
            logger.info(f"Webhook info request - ID: {request_id}")
            return JSONResponse(
                content={
                    "message": "WhatsApp webhook endpoint. Use POST for messages or GET with verification parameters.",
                    "status": "ready",
                    "configuration": {
                        "verify_token_configured": bool(VERIFY_TOKEN),
                        "webhook_secret_configured": bool(VERIFY_TOKEN),
                    },
                },
                status_code=200,
            )

        # Log verification attempt
        logger.info(
            f"Webhook verification attempt - Mode: {hub_mode}, Token provided: {bool(hub_verify_token)} - ID: {request_id}"
        )

        # Validate required parameters
        if not hub_mode or not hub_challenge or not hub_verify_token:
            logger.warning(f"Incomplete verification parameters - ID: {request_id}")
            return create_error_response(
                error_code="WEBHOOK_VERIFICATION_INCOMPLETE",
                message="Missing required verification parameters",
                status_code=status.HTTP_400_BAD_REQUEST,
                request_id=request_id,
            )

        # Check if verify token is configured
        if not VERIFY_TOKEN:
            logger.error(f"Webhook verification failed - No verify token configured - ID: {request_id}")
            return create_error_response(
                error_code="WEBHOOK_VERIFICATION_NOT_CONFIGURED",
                message="Webhook verification not configured",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                request_id=request_id,
            )

        # Verify webhook subscription
        if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
            logger.info(f"Webhook verification successful - Challenge: {hub_challenge} - ID: {request_id}")
            return int(hub_challenge)
        else:
            logger.warning(f"Webhook verification failed - Invalid token or mode - Mode: {hub_mode} - ID: {request_id}")
            return create_error_response(
                error_code="WEBHOOK_VERIFICATION_FAILED",
                message="Invalid verify token or mode",
                status_code=status.HTTP_403_FORBIDDEN,
                request_id=request_id,
            )

    except ValueError as e:
        logger.error(f"Webhook verification error - Invalid challenge format: {str(e)} - ID: {request_id}")
        return create_error_response(
            error_code="WEBHOOK_VERIFICATION_INVALID_CHALLENGE",
            message="Invalid challenge format",
            status_code=status.HTTP_400_BAD_REQUEST,
            request_id=request_id,
        )
    except Exception as e:
        log_error_with_context(
            logger, e, {"endpoint": "webhook_verification", "request_id": request_id, "hub_mode": hub_mode}
        )
        return create_error_response(
            error_code="WEBHOOK_VERIFICATION_ERROR",
            message="Webhook verification failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id,
        )


# ✅ Step 2: Enhanced Message Handling (POST → intelligent responses with security)
@router.post("")
async def receive_message(request: Request, x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256")):
    """
    Enhanced WhatsApp message handling with comprehensive security and error handling.

    This endpoint processes webhook messages from WhatsApp with:
    - Webhook signature verification for security
    - Comprehensive payload validation
    - Structured error responses
    - Automatic user registration and intelligent responses
    - Fallback handling for all error scenarios

    Requirements addressed: 1.1, 1.2, 1.3, 1.4, 1.5, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.4, 4.5
    """
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        # Read raw payload for signature verification
        raw_payload = await request.body()

        # Verify webhook signature for security
        try:
            if not verify_webhook_signature(raw_payload, x_hub_signature_256 or ""):
                logger.warning(f"Webhook signature verification failed - ID: {request_id}")
                raise WebhookValidationError("Invalid webhook signature")
        except WebhookValidationError as e:
            logger.warning(f"Webhook signature validation error: {str(e)} - ID: {request_id}")
            return create_error_response(
                error_code="WEBHOOK_SIGNATURE_INVALID",
                message="Webhook signature verification failed",
                status_code=status.HTTP_401_UNAUTHORIZED,
                request_id=request_id,
            )

        # Parse JSON payload
        try:
            if not raw_payload:
                raise WebhookValidationError("Empty webhook payload")

            import json

            body = json.loads(raw_payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Invalid JSON payload: {str(e)} - ID: {request_id}")
            raise WebhookValidationError("Invalid JSON payload format")

        logger.info(f"Received webhook payload - Size: {len(raw_payload)} bytes - ID: {request_id}")
        logger.debug(
            f"Webhook payload structure: {list(body.keys()) if isinstance(body, dict) else 'not_dict'} - ID: {request_id}"
        )

        # Validate webhook payload structure
        try:
            validate_webhook_payload_structure(body)
        except WebhookValidationError as e:
            logger.warning(f"Webhook payload validation failed: {str(e)} - ID: {request_id}")
            return create_error_response(
                error_code="WEBHOOK_PAYLOAD_INVALID",
                message=f"Invalid webhook payload: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
                request_id=request_id,
            )

        # Process each entry in the webhook
        processed_entries = 0
        processing_errors = []

        for entry in body["entry"]:
            try:
                await process_webhook_entry(entry, request_id)
                processed_entries += 1
            except Exception as e:
                error_msg = f"Entry processing failed: {str(e)}"
                processing_errors.append(error_msg)
                logger.error(f"{error_msg} - ID: {request_id}")

        # Log processing summary
        logger.info(
            f"Webhook processing completed - Entries: {processed_entries}, Errors: {len(processing_errors)} - ID: {request_id}"
        )

        if processing_errors and processed_entries == 0:
            # All entries failed
            return create_error_response(
                error_code="WEBHOOK_PROCESSING_FAILED",
                message="All webhook entries failed to process",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"errors": processing_errors},
                request_id=request_id,
            )

        return {
            "status": "received",
            "processed_entries": processed_entries,
            "errors": processing_errors if processing_errors else None,
        }

    except WebhookValidationError as e:
        # Re-raise for proper error handler
        raise e
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {str(e)} - ID: {request_id}")
        return create_error_response(
            error_code="WEBHOOK_INVALID_JSON",
            message="Invalid JSON format in webhook payload",
            status_code=status.HTTP_400_BAD_REQUEST,
            request_id=request_id,
        )
    except Exception as e:
        log_error_with_context(
            logger,
            e,
            {
                "endpoint": "receive_message",
                "request_id": request_id,
                "payload_size": len(raw_payload) if "raw_payload" in locals() else 0,
            },
        )
        return create_error_response(
            error_code="WEBHOOK_PROCESSING_ERROR",
            message="Unexpected error processing webhook",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id,
        )


async def process_webhook_entry(entry: Dict[str, Any], request_id: str) -> None:
    """
    Process a single webhook entry containing WhatsApp changes with enhanced validation.

    Args:
        entry: Webhook entry containing changes and metadata
        request_id: Request ID for tracking

    Raises:
        WebhookValidationError: If entry structure is invalid
        Exception: For processing errors
    """
    try:
        # Validate entry structure
        validate_webhook_entry(entry)

        entry_id = entry.get("id")
        changes = entry.get("changes", [])

        logger.debug(f"Processing webhook entry - ID: {entry_id}, Changes: {len(changes)} - Request: {request_id}")

        if not changes:
            logger.debug(f"No changes found in webhook entry {entry_id} - Request: {request_id}")
            return

        # Process each change
        processed_changes = 0
        for change in changes:
            try:
                await process_webhook_change(change, request_id)
                processed_changes += 1
            except Exception as e:
                logger.error(f"Change processing failed in entry {entry_id}: {str(e)} - Request: {request_id}")
                # Continue processing other changes

        logger.debug(
            f"Entry processing completed - ID: {entry_id}, Processed: {processed_changes}/{len(changes)} - Request: {request_id}"
        )

    except WebhookValidationError as e:
        logger.warning(f"Webhook entry validation failed: {str(e)} - Request: {request_id}")
        raise e
    except Exception as e:
        logger.error(f"Error processing webhook entry: {str(e)} - Request: {request_id}")
        raise e


async def process_webhook_change(change: Dict[str, Any], request_id: str) -> None:
    """
    Process a single webhook change containing message data with enhanced validation.

    Args:
        change: Webhook change containing value and message data
        request_id: Request ID for tracking

    Raises:
        WebhookValidationError: If change structure is invalid
        Exception: For processing errors
    """
    try:
        # Validate change structure
        validate_webhook_change(change)

        field = change.get("field")
        value = change.get("value", {})

        # Only process message changes
        if field != "messages":
            logger.debug(f"Ignoring non-message change: {field} - Request: {request_id}")
            return

        messages = value.get("messages", [])
        logger.debug(f"Processing webhook change - Field: {field}, Messages: {len(messages)} - Request: {request_id}")

        if not messages:
            logger.debug(f"No messages found in webhook change - Request: {request_id}")
            return

        # Process each message (typically one per webhook)
        processed_messages = 0
        for message in messages:
            try:
                await process_user_message(message, request_id)
                processed_messages += 1
            except Exception as e:
                logger.error(f"Message processing failed: {str(e)} - Request: {request_id}")
                # Continue processing other messages

        logger.debug(
            f"Change processing completed - Messages: {processed_messages}/{len(messages)} - Request: {request_id}"
        )

    except WebhookValidationError as e:
        logger.warning(f"Webhook change validation failed: {str(e)} - Request: {request_id}")
        raise e
    except Exception as e:
        logger.error(f"Error processing webhook change: {str(e)} - Request: {request_id}")
        raise e


async def process_user_message(message: Dict[str, Any], request_id: str) -> None:
    """
    Process a single user message with comprehensive error handling and intelligent responses.

    This function handles:
    - Message content extraction and validation with security checks
    - User registration (automatic on first message) with error recovery
    - Intelligent response generation via Message Service with fallbacks
    - Response delivery via WhatsApp API with retry logic
    - Comprehensive error handling and fallback responses

    Args:
        message: WhatsApp message object containing sender and content
        request_id: Request ID for tracking

    Raises:
        MessageProcessingError: For message processing failures
        UserServiceError: For user service failures
        WhatsAppAPIError: For API communication failures
    """
    from_number = None

    try:
        # Extract and validate message content
        try:
            extracted_message = extract_message_content(message)
            from_number = extracted_message["from"]
            message_text = extracted_message["content"]
            message_id = extracted_message["id"]
            message_type = extracted_message["type"]
        except WebhookValidationError as e:
            logger.warning(f"Message content extraction failed: {str(e)} - Request: {request_id}")
            raise MessageProcessingError(f"Invalid message format: {str(e)}")

        logger.info(
            f"USER_MESSAGE - From: {from_number}, Type: {message_type}, ID: {message_id} - Request: {request_id}"
        )

        if message_text:
            logger.debug(
                f"Message content: {message_text[:100]}{'...' if len(message_text) > 100 else ''} - Request: {request_id}"
            )

        # Handle automatic user registration and activity tracking
        try:
            user = UserService.process_user_message(from_number)
            logger.info(
                f"USER_PROCESSED - Phone: {user.phone_number}, Messages: {user.message_count}, Active: {user.is_active} - Request: {request_id}"
            )
        except Exception as e:
            logger.error(f"USER_SERVICE_ERROR - Failed for {from_number}: {str(e)} - Request: {request_id}")
            # Continue processing even if user registration fails
            # This ensures message processing isn't blocked by user service issues

        # Generate and send intelligent response
        if message_text and message_type == "text":
            await handle_text_message(from_number, message_text, request_id)
        else:
            await handle_non_text_message(from_number, message_type, message_id, request_id)

    except MessageProcessingError as e:
        logger.error(f"MESSAGE_PROCESSING_ERROR - {str(e)} - Request: {request_id}")
        # Try to send error message to user if we have their number
        if from_number:
            await send_error_fallback(from_number, "processing", request_id)
        raise e
    except Exception as e:
        logger.error(f"UNEXPECTED_MESSAGE_ERROR - {str(e)} - Request: {request_id}")
        # Last resort - try to send a basic error message
        if from_number:
            await send_error_fallback(from_number, "general", request_id)
        raise MessageProcessingError(f"Unexpected error processing message: {str(e)}")


async def handle_text_message(from_number: str, message_text: str, request_id: str) -> None:
    """
    Handle text message processing with intelligent responses and fallbacks.

    Args:
        from_number: User's phone number
        message_text: Text content of the message
        request_id: Request ID for tracking
    """
    import time

    start_time = time.time()

    try:
        # Generate intelligent response
        response = message_service.generate_response(message_text, from_number)
        logger.info(f"RESPONSE_GENERATED - For: {from_number}, Type: {response.message_type} - Request: {request_id}")
        logger.debug(
            f"Response content: {response.content[:100]}{'...' if len(response.content) > 100 else ''} - Request: {request_id}"
        )

        # Send response via WhatsApp API with retry logic
        send_result = await send_message_with_retry(from_number, response.content, request_id)

        # Calculate processing time for demo logging
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        if not send_result.get("success", False):
            logger.warning(
                f"RESPONSE_SEND_FAILED - To: {from_number}, Error: {send_result.get('error')} - Request: {request_id}"
            )
            # Try sending fallback message
            await send_error_fallback(from_number, "network", request_id)
        else:
            logger.info(f"RESPONSE_SENT - To: {from_number} - Request: {request_id}")

            # Demo-specific logging for judge evaluation
            try:
                from src.utils.demo_utils import demo_logger

                demo_logger.log_user_interaction(
                    phone_number=from_number,
                    message=message_text,
                    response=response.content,
                    processing_time=processing_time,
                )
            except Exception as demo_log_error:
                logger.debug(f"Demo logging failed: {str(demo_log_error)} - Request: {request_id}")

    except Exception as e:
        logger.error(f"TEXT_MESSAGE_ERROR - For {from_number}: {str(e)} - Request: {request_id}")
        # Send error fallback message
        await send_error_fallback(from_number, "processing", request_id)


async def handle_non_text_message(from_number: str, message_type: str, message_id: str, request_id: str) -> None:
    """
    Handle non-text message types (images, documents, etc.) with appropriate responses.

    Args:
        from_number: User's phone number
        message_type: Type of message received
        message_id: Message ID
        request_id: Request ID for tracking
    """
    logger.info(
        f"NON_TEXT_MESSAGE - From: {from_number}, Type: {message_type}, ID: {message_id} - Request: {request_id}"
    )

    # Generate appropriate response for non-text messages
    non_text_responses = {
        "image": "Thanks for the image! I currently support text messages. Please send me a text to get health information.",
        "document": "Thanks for the document! I currently support text messages. Please send me a text to get health information.",
        "audio": "Thanks for the audio message! I currently support text messages. Please send me a text to get health information.",
        "video": "Thanks for the video! I currently support text messages. Please send me a text to get health information.",
        "sticker": "Thanks for the sticker! 😊 Please send me a text message to get health information.",
        "location": "Thanks for sharing your location! I currently support text messages. Please send me a text to get health information.",
        "contacts": "Thanks for the contact! I currently support text messages. Please send me a text to get health information.",
    }

    response_text = non_text_responses.get(
        message_type,
        "Thanks for your message! I currently support text messages. Please send me a text to get started.",
    )

    # Send response
    send_result = await send_message_with_retry(from_number, response_text, request_id)

    if send_result.get("success", False):
        logger.info(f"NON_TEXT_RESPONSE_SENT - To: {from_number}, Type: {message_type} - Request: {request_id}")
    else:
        logger.warning(
            f"NON_TEXT_RESPONSE_FAILED - To: {from_number}, Error: {send_result.get('error')} - Request: {request_id}"
        )


async def send_error_fallback(from_number: str, error_type: str, request_id: str) -> None:
    """
    Send error fallback message to user with comprehensive error handling.

    Args:
        from_number: User's phone number
        error_type: Type of error that occurred
        request_id: Request ID for tracking
    """
    try:
        fallback_response = message_service.process_error_message(error_type)
        logger.info(f"FALLBACK_ATTEMPT - To: {from_number}, Type: {error_type} - Request: {request_id}")

        send_result = await send_message_with_retry(from_number, fallback_response.content, request_id, max_retries=1)

        if send_result.get("success", False):
            logger.info(f"FALLBACK_SENT - To: {from_number} - Request: {request_id}")
        else:
            logger.error(
                f"FALLBACK_FAILED - To: {from_number}, Error: {send_result.get('error')} - Request: {request_id}"
            )

    except Exception as fallback_error:
        logger.error(f"FALLBACK_EXCEPTION - To: {from_number}, Error: {str(fallback_error)} - Request: {request_id}")


async def send_message_with_retry(
    from_number: str, message: str, request_id: str, max_retries: int = 2
) -> Dict[str, Any]:
    """
    Send message with retry logic for improved reliability.

    Args:
        from_number: Recipient phone number
        message: Message content
        request_id: Request ID for tracking
        max_retries: Maximum number of retry attempts

    Returns:
        Dict containing success status and error information
    """
    for attempt in range(max_retries + 1):
        try:
            send_result = send_message(from_number, message)

            if not send_result.get("error"):
                return {"success": True, "attempt": attempt + 1}

            # Check if error is retryable
            error_code = send_result.get("status_code")
            if error_code in [429, 500, 502, 503, 504]:  # Retryable errors
                if attempt < max_retries:
                    logger.warning(
                        f"SEND_RETRY - Attempt {attempt + 1}/{max_retries + 1} failed for {from_number}: {send_result.get('error')} - Request: {request_id}"
                    )
                    continue

            # Non-retryable error or max retries reached
            return {"success": False, "error": send_result.get("error"), "attempts": attempt + 1}

        except Exception as e:
            if attempt < max_retries:
                logger.warning(
                    f"SEND_EXCEPTION_RETRY - Attempt {attempt + 1}/{max_retries + 1} failed for {from_number}: {str(e)} - Request: {request_id}"
                )
                continue
            else:
                return {
                    "success": False,
                    "error": f"Exception after {attempt + 1} attempts: {str(e)}",
                    "attempts": attempt + 1,
                }

    return {"success": False, "error": "Max retries exceeded", "attempts": max_retries + 1}


def send_message(to: str, message: str) -> Dict[str, Any]:
    """
    Send message back via WhatsApp Cloud API with comprehensive error handling and monitoring.

    This function provides:
    - Input validation and sanitization
    - Comprehensive error handling for all API scenarios
    - Detailed logging for monitoring and debugging
    - Structured error responses for different failure types
    - Security and rate limiting awareness

    Args:
        to: Recipient phone number
        message: Message content to send

    Returns:
        Dict containing response data or error information with detailed status

    Raises:
        WhatsAppAPIError: For API-specific errors that need special handling
    """
    # Input validation
    if not to or not isinstance(to, str) or not to.strip():
        error_msg = "Missing or invalid recipient phone number"
        logger.error(f"SEND_VALIDATION_ERROR - {error_msg}")
        return {"error": error_msg, "error_type": "validation"}

    if not message or not isinstance(message, str) or not message.strip():
        error_msg = "Missing or invalid message content"
        logger.error(f"SEND_VALIDATION_ERROR - {error_msg}")
        return {"error": error_msg, "error_type": "validation"}

    # Configuration validation
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        error_msg = "WhatsApp API credentials not configured"
        logger.error(f"SEND_CONFIG_ERROR - {error_msg}")
        return {"error": error_msg, "error_type": "configuration"}

    # Sanitize inputs
    to = to.strip()
    message = message.strip()

    # Message length validation (WhatsApp limit is 4096 characters)
    if len(message) > 4096:
        error_msg = f"Message too long: {len(message)} characters (max: 4096)"
        logger.warning(f"SEND_LENGTH_ERROR - To: {to}, Length: {len(message)}")
        return {"error": error_msg, "error_type": "validation"}

    try:
        # Prepare API request
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

        logger.debug(f"SEND_REQUEST - To: {to}, Length: {len(message)} chars")

        # Make API request with timeout
        response = requests.post(url, headers=headers, json=payload, timeout=Config.API_TIMEOUT)

        # Parse response
        try:
            response_data = response.json()
        except ValueError as e:
            logger.warning(f"SEND_PARSE_ERROR - Invalid JSON response: {str(e)}")
            response_data = {"raw_response": response.text[:500]}  # Limit raw response size

        # Handle different response status codes
        if response.status_code == 200:
            logger.info(
                f"SEND_SUCCESS - To: {to}, MessageID: {response_data.get('messages', [{}])[0].get('id', 'unknown')}"
            )
            return {
                "success": True,
                "response_data": response_data,
                "message_id": response_data.get("messages", [{}])[0].get("id"),
                "status_code": 200,
            }

        elif response.status_code == 401:
            error_msg = "WhatsApp API authentication failed - check access token"
            logger.error(f"SEND_AUTH_ERROR - {error_msg}: {response.text[:200]}")
            return {"error": error_msg, "status_code": 401, "error_type": "authentication", "details": response_data}

        elif response.status_code == 400:
            error_msg = "Bad request to WhatsApp API"
            logger.error(f"SEND_BAD_REQUEST - To: {to}, Error: {response.text[:200]}")
            return {"error": error_msg, "status_code": 400, "error_type": "bad_request", "details": response_data}

        elif response.status_code == 403:
            error_msg = "WhatsApp API access forbidden - check permissions"
            logger.error(f"SEND_FORBIDDEN - To: {to}, Error: {response.text[:200]}")
            return {"error": error_msg, "status_code": 403, "error_type": "forbidden", "details": response_data}

        elif response.status_code == 429:
            error_msg = "WhatsApp API rate limit exceeded"
            logger.warning(f"SEND_RATE_LIMIT - To: {to}, Error: {response.text[:200]}")
            return {
                "error": error_msg,
                "status_code": 429,
                "error_type": "rate_limit",
                "details": response_data,
                "retry_after": response.headers.get("Retry-After"),
            }

        elif response.status_code >= 500:
            error_msg = f"WhatsApp API server error: {response.status_code}"
            logger.error(f"SEND_SERVER_ERROR - To: {to}, Status: {response.status_code}, Error: {response.text[:200]}")
            return {
                "error": error_msg,
                "status_code": response.status_code,
                "error_type": "server_error",
                "details": response_data,
            }

        else:
            error_msg = f"Unexpected WhatsApp API response: {response.status_code}"
            logger.error(
                f"SEND_UNEXPECTED_ERROR - To: {to}, Status: {response.status_code}, Error: {response.text[:200]}"
            )
            return {
                "error": error_msg,
                "status_code": response.status_code,
                "error_type": "unexpected",
                "details": response_data,
            }

    except requests.exceptions.Timeout:
        error_msg = f"WhatsApp API request timeout ({Config.API_TIMEOUT}s)"
        logger.error(f"SEND_TIMEOUT - To: {to}, Timeout: {Config.API_TIMEOUT}s")
        return {"error": error_msg, "error_type": "timeout"}

    except requests.exceptions.ConnectionError as e:
        error_msg = "WhatsApp API connection error"
        logger.error(f"SEND_CONNECTION_ERROR - To: {to}, Error: {str(e)}")
        return {"error": error_msg, "error_type": "connection", "details": str(e)}

    except requests.exceptions.RequestException as e:
        error_msg = f"WhatsApp API request failed: {str(e)}"
        logger.error(f"SEND_REQUEST_ERROR - To: {to}, Error: {str(e)}")
        return {"error": error_msg, "error_type": "request", "details": str(e)}

    except Exception as e:
        error_msg = f"Unexpected error sending message: {str(e)}"
        logger.error(f"SEND_UNEXPECTED_EXCEPTION - To: {to}, Error: {str(e)}")
        log_error_with_context(logger, e, {"function": "send_message", "recipient": to, "message_length": len(message)})
        return {"error": error_msg, "error_type": "unexpected", "details": str(e)}

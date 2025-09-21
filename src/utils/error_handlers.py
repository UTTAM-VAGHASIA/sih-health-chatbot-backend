# src/utils/error_handlers.py
"""
Comprehensive error handling utilities for the SIH Health Chatbot Backend.

This module provides custom exception classes, error response formatters,
and centralized error handling logic for consistent error management
across the application.
"""

import logging
import traceback
from typing import Any, Callable, Dict, Optional, Union

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class WhatsAppAPIError(Exception):
    """Custom exception for WhatsApp API related errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class WebhookValidationError(Exception):
    """Custom exception for webhook validation errors."""

    def __init__(self, message: str, payload: Optional[Dict] = None):
        self.message = message
        self.payload = payload
        super().__init__(self.message)


class UserServiceError(Exception):
    """Custom exception for user service related errors."""

    def __init__(self, message: str, user_id: Optional[str] = None):
        self.message = message
        self.user_id = user_id
        super().__init__(self.message)


class MessageProcessingError(Exception):
    """Custom exception for message processing errors."""

    def __init__(self, message: str, original_message: Optional[str] = None):
        self.message = message
        self.original_message = original_message
        super().__init__(self.message)


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        error_code: Unique error code for categorization
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details
        request_id: Request identifier for tracking

    Returns:
        JSONResponse with standardized error format
    """
    error_response: Dict[str, Any] = {
        "error": {"code": error_code, "message": message, "timestamp": None}  # Will be set by logging system
    }

    if details:
        error_response["error"]["details"] = details

    if request_id:
        error_response["error"]["request_id"] = str(request_id)

    return JSONResponse(status_code=status_code, content=error_response)


def log_error_with_context(
    logger_instance: logging.Logger, error: Exception, context: Dict[str, Any], level: int = logging.ERROR
) -> None:
    """
    Log error with comprehensive context information.

    Args:
        logger_instance: Logger to use for logging
        error: Exception that occurred
        context: Additional context information
        level: Logging level to use
    """
    error_info = {"error_type": type(error).__name__, "error_message": str(error), "context": context}

    # Add traceback for unexpected errors
    if not isinstance(error, (HTTPException, ValidationError)):
        error_info["traceback"] = traceback.format_exc()

    logger_instance.log(level, f"Error occurred: {error_info}")


async def whatsapp_api_error_handler(request: Request, exc: WhatsAppAPIError) -> JSONResponse:
    """
    Handle WhatsApp API specific errors.

    Args:
        request: FastAPI request object
        exc: WhatsAppAPIError exception

    Returns:
        JSONResponse with appropriate error details
    """
    log_error_with_context(
        logger,
        exc,
        {
            "endpoint": str(request.url),
            "method": request.method,
            "whatsapp_status_code": exc.status_code,
            "whatsapp_details": exc.details,
        },
    )

    # Map WhatsApp API errors to appropriate HTTP status codes
    status_code_mapping = {
        400: status.HTTP_400_BAD_REQUEST,
        401: status.HTTP_401_UNAUTHORIZED,
        403: status.HTTP_403_FORBIDDEN,
        429: status.HTTP_429_TOO_MANY_REQUESTS,
        500: status.HTTP_502_BAD_GATEWAY,  # WhatsApp API is down
    }

    http_status = status_code_mapping.get(exc.status_code or 500, status.HTTP_502_BAD_GATEWAY)

    return create_error_response(
        error_code="WHATSAPP_API_ERROR",
        message=f"WhatsApp API error: {exc.message}",
        status_code=int(http_status),
        details={"whatsapp_status_code": exc.status_code, "whatsapp_details": exc.details},
    )


async def webhook_validation_error_handler(request: Request, exc: WebhookValidationError) -> JSONResponse:
    """
    Handle webhook validation errors.

    Args:
        request: FastAPI request object
        exc: WebhookValidationError exception

    Returns:
        JSONResponse with validation error details
    """
    log_error_with_context(
        logger,
        exc,
        {
            "endpoint": str(request.url),
            "method": request.method,
            "payload_preview": str(exc.payload)[:200] if exc.payload else None,
        },
        level=logging.WARNING,
    )

    return create_error_response(
        error_code="WEBHOOK_VALIDATION_ERROR",
        message=f"Webhook validation failed: {exc.message}",
        status_code=status.HTTP_400_BAD_REQUEST,
        details={"validation_error": exc.message},
    )


async def user_service_error_handler(request: Request, exc: UserServiceError) -> JSONResponse:
    """
    Handle user service errors.

    Args:
        request: FastAPI request object
        exc: UserServiceError exception

    Returns:
        JSONResponse with user service error details
    """
    log_error_with_context(
        logger, exc, {"endpoint": str(request.url), "method": request.method, "user_id": exc.user_id}
    )

    return create_error_response(
        error_code="USER_SERVICE_ERROR",
        message=f"User service error: {exc.message}",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"user_id": exc.user_id},
    )


async def message_processing_error_handler(request: Request, exc: MessageProcessingError) -> JSONResponse:
    """
    Handle message processing errors.

    Args:
        request: FastAPI request object
        exc: MessageProcessingError exception

    Returns:
        JSONResponse with message processing error details
    """
    log_error_with_context(
        logger, exc, {"endpoint": str(request.url), "method": request.method, "original_message": exc.original_message}
    )

    return create_error_response(
        error_code="MESSAGE_PROCESSING_ERROR",
        message=f"Message processing error: {exc.message}",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"original_message": exc.original_message},
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request object
        exc: ValidationError exception

    Returns:
        JSONResponse with validation error details
    """
    log_error_with_context(
        logger,
        exc,
        {"endpoint": str(request.url), "method": request.method, "validation_errors": exc.errors()},
        level=logging.WARNING,
    )

    return create_error_response(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"validation_errors": exc.errors(), "error_count": len(exc.errors())},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions.

    Args:
        request: FastAPI request object
        exc: HTTPException

    Returns:
        JSONResponse with HTTP exception details
    """
    log_error_with_context(
        logger,
        exc,
        {"endpoint": str(request.url), "method": request.method, "status_code": exc.status_code},
        level=logging.WARNING if exc.status_code < 500 else logging.ERROR,
    )

    return create_error_response(error_code="HTTP_ERROR", message=exc.detail, status_code=exc.status_code)


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected general exceptions.

    Args:
        request: FastAPI request object
        exc: General exception

    Returns:
        JSONResponse with general error details
    """
    log_error_with_context(
        logger,
        exc,
        {
            "endpoint": str(request.url),
            "method": request.method,
            "user_agent": request.headers.get("user-agent"),
            "content_type": request.headers.get("content-type"),
        },
    )

    # Don't expose internal error details in production
    from src.config import Config

    if Config.ENVIRONMENT == "production":
        message = "An internal server error occurred"
        details = None
    else:
        message = f"Unexpected error: {str(exc)}"
        details = {"error_type": type(exc).__name__}

    return create_error_response(
        error_code="INTERNAL_SERVER_ERROR",
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=details,
    )


def get_error_handlers() -> Dict[Union[int, type], Callable]:
    """
    Get all error handlers for FastAPI application.

    Returns:
        Dictionary mapping exception types to handler functions
    """
    return {
        WhatsAppAPIError: whatsapp_api_error_handler,
        WebhookValidationError: webhook_validation_error_handler,
        UserServiceError: user_service_error_handler,
        MessageProcessingError: message_processing_error_handler,
        ValidationError: validation_error_handler,
        HTTPException: http_exception_handler,
        Exception: general_exception_handler,
    }

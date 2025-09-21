# src/utils/middleware.py
"""
Custom middleware for request logging, error tracking, and performance monitoring.

This module provides middleware components for comprehensive logging of all
user interactions, system events, and error tracking across the application.
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request and response logging.

    Logs all incoming requests, response times, status codes, and errors
    for monitoring and debugging purposes.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log comprehensive information.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response
        """
        # Generate unique request ID for tracking
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Log request start
        start_time = time.time()

        # Extract request information
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": {
                "user-agent": request.headers.get("user-agent"),
                "content-type": request.headers.get("content-type"),
                "content-length": request.headers.get("content-length"),
                "x-forwarded-for": request.headers.get("x-forwarded-for"),
                "x-real-ip": request.headers.get("x-real-ip"),
            },
            "client_ip": self._get_client_ip(request),
        }

        # Log incoming request
        logger.info(f"REQUEST_START - {request_info['method']} {request_info['path']} - ID: {request_id}")
        logger.debug(f"Request details: {request_info}")

        # Process request and handle errors
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log successful response
            response_info = {
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
                "response_headers": {
                    "content-type": response.headers.get("content-type"),
                    "content-length": response.headers.get("content-length"),
                },
            }

            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id

            # Log response based on status code
            if response.status_code >= 500:
                logger.error(
                    f"REQUEST_ERROR - {request_info['method']} {request_info['path']} - "
                    f"Status: {response.status_code} - Time: {response_info['process_time_ms']}ms - ID: {request_id}"
                )
            elif response.status_code >= 400:
                logger.warning(
                    f"REQUEST_CLIENT_ERROR - {request_info['method']} {request_info['path']} - "
                    f"Status: {response.status_code} - Time: {response_info['process_time_ms']}ms - ID: {request_id}"
                )
            else:
                logger.info(
                    f"REQUEST_SUCCESS - {request_info['method']} {request_info['path']} - "
                    f"Status: {response.status_code} - Time: {response_info['process_time_ms']}ms - ID: {request_id}"
                )

            logger.debug(f"Response details: {response_info}")

            return response

        except Exception as e:
            # Calculate processing time for failed requests
            process_time = time.time() - start_time

            # Log exception
            logger.error(
                f"REQUEST_EXCEPTION - {request_info['method']} {request_info['path']} - "
                f"Error: {str(e)} - Time: {round(process_time * 1000, 2)}ms - ID: {request_id}"
            )
            logger.exception(f"Exception details for request {request_id}")

            # Re-raise the exception to be handled by error handlers
            raise

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request headers.

        Args:
            request: HTTP request object

        Returns:
            Client IP address
        """
        # Check for forwarded IP headers (common in load balancers/proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"


class UserInteractionLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware specifically for logging user interactions with the WhatsApp bot.

    Provides detailed logging of WhatsApp webhook interactions, user messages,
    and bot responses for analytics and debugging.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process WhatsApp webhook requests with specialized logging.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response
        """
        # Only process WhatsApp webhook endpoints
        if not request.url.path.startswith("/webhook/whatsapp"):
            return await call_next(request)

        request_id = getattr(request.state, "request_id", "unknown")

        # Log WhatsApp webhook interaction
        if request.method == "POST":
            logger.info(f"WHATSAPP_WEBHOOK - Incoming message webhook - ID: {request_id}")

            # Try to extract and log webhook payload (without sensitive data)
            try:
                # Read body for logging (this consumes the stream, so we need to be careful)
                body = await request.body()

                # Log payload size and basic info
                logger.debug(f"WHATSAPP_WEBHOOK - Payload size: {len(body)} bytes - ID: {request_id}")

                # Create a new request with the body for downstream processing
                # This is necessary because reading the body consumes the stream
                async def receive():
                    return {"type": "http.request", "body": body}

                request._receive = receive

            except Exception as e:
                logger.warning(f"WHATSAPP_WEBHOOK - Could not read payload: {str(e)} - ID: {request_id}")

        elif request.method == "GET":
            # Log webhook verification attempts
            hub_mode = request.query_params.get("hub.mode")
            if hub_mode:
                logger.info(f"WHATSAPP_WEBHOOK - Verification request: mode={hub_mode} - ID: {request_id}")
            else:
                logger.info(f"WHATSAPP_WEBHOOK - Info request - ID: {request_id}")

        # Process request
        response = await call_next(request)

        # Log WhatsApp webhook response
        if request.method == "POST":
            if response.status_code == 200:
                logger.info(f"WHATSAPP_WEBHOOK - Message processed successfully - ID: {request_id}")
            else:
                logger.warning(
                    f"WHATSAPP_WEBHOOK - Message processing failed: {response.status_code} - ID: {request_id}"
                )

        return response


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for monitoring application performance and resource usage.

    Tracks slow requests, memory usage patterns, and performance metrics
    for optimization and alerting purposes.
    """

    def __init__(self, app, slow_request_threshold: float = 5.0):
        """
        Initialize performance monitoring middleware.

        Args:
            app: FastAPI application instance
            slow_request_threshold: Threshold in seconds for slow request alerts
        """
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Monitor request performance and log slow requests.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response
        """
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log slow requests
        if process_time > self.slow_request_threshold:
            logger.warning(
                f"SLOW_REQUEST - {request.method} {request.url.path} - "
                f"Time: {round(process_time * 1000, 2)}ms - ID: {request_id}"
            )

        # Log performance metrics for specific endpoints
        if request.url.path.startswith("/webhook/whatsapp") and request.method == "POST":
            logger.info(
                f"WHATSAPP_PERFORMANCE - Message processing time: {round(process_time * 1000, 2)}ms - ID: {request_id}"
            )

        elif request.url.path.startswith("/admin/alerts") and request.method == "POST":
            logger.info(
                f"ADMIN_PERFORMANCE - Alert broadcast time: {round(process_time * 1000, 2)}ms - ID: {request_id}"
            )

        return response


def setup_middleware(app):
    """
    Configure all middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Add middleware in reverse order (last added = first executed)

    # Performance monitoring (outermost)
    app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold=5.0)

    # User interaction logging
    app.add_middleware(UserInteractionLoggingMiddleware)

    # General request logging (innermost)
    app.add_middleware(RequestLoggingMiddleware)

    logger.info("All middleware configured successfully")

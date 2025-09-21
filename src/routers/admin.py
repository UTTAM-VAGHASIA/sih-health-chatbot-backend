# src/routers/admin.py
"""
Admin API Router for WhatsApp Demo Bot.

This router provides administrative endpoints for broadcasting alerts
to all registered WhatsApp users. It includes input validation,
error handling, and comprehensive logging for demo purposes.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.config import get_logger
from src.routers.whatsapp import send_message
from src.services.user_service import UserService

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


class AlertRequest(BaseModel):
    """Request model for broadcasting alerts to users."""

    message: str = Field(..., min_length=1, max_length=1000, description="Alert message content")
    priority: Optional[str] = Field(default="medium", pattern="^(low|medium|high)$", description="Alert priority level")

    @field_validator("message", mode="after")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message content."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v.strip()


class AlertResponse(BaseModel):
    """Response model for alert broadcasting results."""

    success: bool = Field(description="Whether the broadcast was successful")
    users_targeted: int = Field(description="Number of users targeted for the alert")
    successful_deliveries: int = Field(description="Number of successful message deliveries")
    failed_deliveries: int = Field(description="Number of failed message deliveries")
    message_id: str = Field(description="Unique identifier for this alert broadcast")
    errors: Optional[List[str]] = Field(default=None, description="List of error messages if any failures occurred")


class BroadcastResult(BaseModel):
    """Internal model for tracking broadcast results."""

    phone_number: str
    success: bool
    error_message: Optional[str] = Field(default=None)


@router.post("/alerts", response_model=AlertResponse)
async def broadcast_alert(alert_request: AlertRequest) -> AlertResponse:
    """
    Broadcast an alert message to all registered WhatsApp users.

    This endpoint implements the admin alert broadcasting functionality:
    - Validates the alert message content and priority
    - Retrieves all active registered users
    - Sends the alert to each user via WhatsApp API
    - Tracks delivery success/failure for each user
    - Returns comprehensive results including error details

    Requirements addressed: 2.1, 2.2, 2.3, 2.4, 2.5

    Args:
        alert_request: AlertRequest containing message and priority

    Returns:
        AlertResponse with broadcast results and statistics

    Raises:
        HTTPException: For validation errors or system failures
    """
    try:
        logger.info(f"Received alert broadcast request: priority={alert_request.priority}")
        logger.debug(f"Alert message content: {alert_request.message[:100]}...")

        # Get all active users for broadcasting
        active_users = UserService.get_all_active_users()
        users_targeted = len(active_users)

        logger.info(f"Broadcasting alert to {users_targeted} active users")

        # Handle case where no users are registered
        if users_targeted == 0:
            logger.info("No registered users found for alert broadcast")
            return AlertResponse(
                success=True,
                users_targeted=0,
                successful_deliveries=0,
                failed_deliveries=0,
                message_id=f"alert_{hash(alert_request.message) % 1000000}",
                errors=None,
            )

        # Format alert message with priority indicator
        formatted_message = format_alert_message(alert_request.message, alert_request.priority)

        # Broadcast to all users and collect results
        broadcast_results = []
        for user in active_users:
            result = await send_alert_to_user(user.phone_number, formatted_message)
            broadcast_results.append(result)

        # Calculate statistics
        successful_deliveries = sum(1 for result in broadcast_results if result.success)
        failed_deliveries = users_targeted - successful_deliveries

        # Collect error messages
        errors = [
            f"{result.phone_number}: {result.error_message}"
            for result in broadcast_results
            if not result.success and result.error_message
        ]

        # Generate unique message ID for tracking
        message_id = f"alert_{abs(hash(alert_request.message + str(users_targeted))) % 1000000}"

        # Log broadcast summary
        logger.info(
            f"Alert broadcast completed: {successful_deliveries}/{users_targeted} successful, "
            f"{failed_deliveries} failed, message_id={message_id}"
        )

        if failed_deliveries > 0:
            logger.warning(f"Alert broadcast had {failed_deliveries} failures: {errors}")

        return AlertResponse(
            success=True,
            users_targeted=users_targeted,
            successful_deliveries=successful_deliveries,
            failed_deliveries=failed_deliveries,
            message_id=message_id,
            errors=errors if errors else None,
        )

    except ValueError as e:
        logger.error(f"Validation error in alert broadcast: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error during alert broadcast: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during alert broadcast")


async def send_alert_to_user(phone_number: str, message: str) -> BroadcastResult:
    """
    Send alert message to a specific user and track the result.

    Args:
        phone_number: User's WhatsApp phone number
        message: Formatted alert message to send

    Returns:
        BroadcastResult with delivery status and error details
    """
    try:
        logger.debug(f"Sending alert to user: {phone_number}")

        # Use existing send_message function from whatsapp router
        send_result = send_message(phone_number, message)

        if send_result.get("error"):
            error_msg = send_result.get("error", "Unknown error")
            logger.warning(f"Failed to send alert to {phone_number}: {error_msg}")
            return BroadcastResult(phone_number=phone_number, success=False, error_message=error_msg)

        logger.debug(f"Successfully sent alert to {phone_number}")
        return BroadcastResult(phone_number=phone_number, success=True)

    except Exception as e:
        error_msg = f"Exception sending alert: {str(e)}"
        logger.error(f"Error sending alert to {phone_number}: {error_msg}")
        return BroadcastResult(phone_number=phone_number, success=False, error_message=error_msg)


def format_alert_message(message: str, priority: Optional[str] = "medium") -> str:
    """
    Format alert message with priority indicators and branding.

    Args:
        message: Raw alert message content
        priority: Alert priority level (low, medium, high)

    Returns:
        Formatted alert message with priority indicators
    """
    priority_indicators = {
        "low": "ℹ️",
        "medium": "⚠️",
        "high": "🚨",
    }

    priority_labels = {
        "low": "INFO",
        "medium": "ALERT",
        "high": "URGENT",
    }

    indicator = priority_indicators.get(priority or "medium", "⚠️")
    label = priority_labels.get(priority or "medium", "ALERT")

    formatted_message = f"{indicator} {label}: {message}\n\n📱 SIH Health Assistant"

    return formatted_message


@router.get("/stats")
async def get_admin_stats():
    """
    Get administrative statistics for the demo dashboard.

    Returns basic statistics about registered users and system status
    for demo purposes and admin monitoring.

    Returns:
        Dict containing user statistics and system information
    """
    try:
        total_users = UserService.get_user_count()
        active_users = UserService.get_active_user_count()
        inactive_users = total_users - active_users

        logger.debug(f"Admin stats requested: {total_users} total, {active_users} active users")

        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "system_status": "operational",
            "last_updated": "2025-01-21T10:30:00Z",  # In production, use actual timestamp
        }

    except Exception as e:
        logger.error(f"Error retrieving admin stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve admin statistics")


@router.get("/users")
async def get_registered_users():
    """
    Get list of all registered users for admin monitoring.

    Returns anonymized user information for demo and debugging purposes.
    Phone numbers are partially masked for privacy.

    Returns:
        List of user information with masked phone numbers
    """
    try:
        users = UserService.get_all_active_users()

        # Anonymize phone numbers for demo purposes
        anonymized_users = []
        for user in users:
            masked_number = mask_phone_number(user.phone_number)
            anonymized_users.append(
                {
                    "phone_number": masked_number,
                    "first_seen": user.first_seen.isoformat(),
                    "last_activity": user.last_activity.isoformat(),
                    "message_count": user.message_count,
                    "is_active": user.is_active,
                }
            )

        logger.debug(f"Admin users list requested: {len(anonymized_users)} users returned")

        return {"users": anonymized_users, "total_count": len(anonymized_users)}

    except Exception as e:
        logger.error(f"Error retrieving user list: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user list")


def mask_phone_number(phone_number: str) -> str:
    """
    Mask phone number for privacy in admin displays.

    Args:
        phone_number: Full phone number

    Returns:
        Masked phone number (e.g., +91****7944)
    """
    if len(phone_number) <= 6:
        return phone_number

    # Keep country code and last 4 digits, mask the middle
    if phone_number.startswith("+"):
        country_code = phone_number[:3]  # +91 or similar
        last_digits = phone_number[-4:]
        middle_length = len(phone_number) - 7  # Total - country code - last 4
        if middle_length <= 0:
            return phone_number  # Too short to mask properly
        masked_middle = "*" * 4  # Always use 4 asterisks for consistency
        return f"{country_code}{masked_middle}{last_digits}"
    else:
        # Fallback for numbers without country code
        last_digits = phone_number[-4:]
        masked_middle = "*" * 6  # Use 6 asterisks for numbers without country code
        return f"{masked_middle}{last_digits}"

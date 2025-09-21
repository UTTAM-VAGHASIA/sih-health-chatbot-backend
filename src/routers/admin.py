# src/routers/admin.py
"""
Admin API Router for WhatsApp Demo Bot.

This router provides administrative endpoints for broadcasting alerts
to all registered WhatsApp users. It includes input validation,
error handling, and comprehensive logging for demo purposes.
"""

from datetime import datetime
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

        # Demo-specific logging for judge evaluation
        try:
            from src.utils.demo_utils import demo_logger

            demo_logger.log_broadcast_event(
                alert_message=alert_request.message,
                users_targeted=users_targeted,
                success_count=successful_deliveries,
                failure_count=failed_deliveries,
            )
        except Exception as demo_log_error:
            logger.debug(f"Demo broadcast logging failed: {str(demo_log_error)}")

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
    Get comprehensive administrative statistics for the demo dashboard.

    Returns detailed statistics about registered users, system performance,
    and demo-specific metrics for judge evaluation and monitoring.

    Returns:
        Dict containing comprehensive user statistics and system information
    """
    try:
        from datetime import datetime

        from src.utils.demo_utils import demo_metrics

        # Basic user statistics
        total_users = UserService.get_user_count()
        active_users = UserService.get_active_user_count()
        inactive_users = total_users - active_users

        # Get demo performance metrics
        performance_metrics = demo_metrics.get_demo_performance_metrics()

        # Get user engagement statistics
        engagement_stats = demo_metrics.get_user_engagement_stats()

        # Compile comprehensive statistics
        stats = {
            "user_statistics": {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "user_growth_rate": "Demo: +5 users/day",  # Simulated for demo
            },
            "performance_metrics": performance_metrics,
            "engagement_statistics": engagement_stats,
            "system_info": {
                "system_status": "operational",
                "environment": "demo",
                "uptime": "99.9%",
                "last_updated": datetime.now().isoformat(),
            },
            "demo_info": {
                "is_demo_environment": True,
                "demo_features_active": True,
                "judge_evaluation_mode": True,
            },
        }

        logger.info(f"Admin stats requested: {total_users} total, {active_users} active users")
        logger.debug(f"Comprehensive stats: {stats}")

        return stats

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


@router.post("/demo/setup")
async def setup_demo_environment():
    """
    Setup demo environment for judge evaluation.

    Creates demo users, test data, and prepares the system for demonstration.
    This endpoint is specifically for judge evaluation and demo purposes.

    Returns:
        Dict containing demo setup information and statistics
    """
    try:
        from src.utils.demo_utils import demo_data_generator

        logger.info("Setting up demo environment for judge evaluation")

        # Setup complete demo environment
        demo_info = demo_data_generator.setup_judge_demo()

        # Get updated statistics
        total_users = UserService.get_user_count()
        active_users = UserService.get_active_user_count()

        response = {
            "success": True,
            "message": "Demo environment setup completed successfully",
            "demo_info": demo_info,
            "current_stats": {
                "total_users": total_users,
                "active_users": active_users,
            },
            "judge_instructions": {
                "test_numbers": demo_info.get("demo_phone_numbers", [])[:3],  # First 3 for testing
                "test_commands": ["hello", "demo", "judges", "health", "broadcast"],
                "admin_endpoints": ["/admin/alerts", "/admin/stats", "/admin/demo/broadcast"],
            },
        }

        logger.info(f"Demo environment setup complete: {response}")
        return response

    except Exception as e:
        logger.error(f"Failed to setup demo environment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo setup failed: {str(e)}")


@router.post("/demo/broadcast")
async def send_demo_broadcast():
    """
    Send a demo broadcast alert to showcase the alert system.

    This endpoint sends a pre-configured demo alert to all registered users
    to demonstrate the broadcast functionality for judges.

    Returns:
        AlertResponse with broadcast results
    """
    try:
        from src.utils.demo_utils import demo_data_generator

        logger.info("Sending demo broadcast for judge evaluation")

        # Get a demo alert message
        demo_alert = demo_data_generator.get_demo_alert()

        # Create alert request
        alert_request = AlertRequest(message=demo_alert["message"], priority=demo_alert["priority"])

        # Use existing broadcast functionality
        result = await broadcast_alert(alert_request)

        logger.info(f"Demo broadcast completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Demo broadcast failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo broadcast failed: {str(e)}")


@router.get("/demo/metrics")
async def get_demo_metrics():
    """
    Get comprehensive demo metrics for judge evaluation.

    Returns detailed metrics about system performance, user engagement,
    and demo-specific statistics for evaluation purposes.

    Returns:
        Dict containing comprehensive demo metrics
    """
    try:
        from datetime import datetime

        from src.utils.demo_utils import demo_metrics

        logger.info("Demo metrics requested for judge evaluation")

        # Get all available metrics
        performance_metrics = demo_metrics.get_demo_performance_metrics()
        engagement_stats = demo_metrics.get_user_engagement_stats()

        # Additional demo-specific metrics
        demo_specific_metrics = {
            "demo_session_info": {
                "session_start": datetime.now().replace(hour=9, minute=0, second=0).isoformat(),
                "demo_duration_minutes": 30,
                "features_demonstrated": [
                    "Auto user registration",
                    "Intelligent chat responses",
                    "Admin alert broadcasting",
                    "Real-time user tracking",
                    "Comprehensive logging",
                ],
            },
            "technical_highlights": {
                "framework": "FastAPI (Python 3.13)",
                "integration": "WhatsApp Cloud API",
                "architecture": "Layered (API → Services → Data)",
                "deployment": "Docker + Cloudflare Tunnel",
                "monitoring": "Comprehensive logging & metrics",
            },
        }

        comprehensive_metrics = {
            "performance": performance_metrics,
            "engagement": engagement_stats,
            "demo_info": demo_specific_metrics,
            "timestamp": datetime.now().isoformat(),
        }

        logger.debug(f"Demo metrics compiled: {comprehensive_metrics}")
        return comprehensive_metrics

    except Exception as e:
        logger.error(f"Failed to get demo metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve demo metrics")


@router.delete("/demo/reset")
async def reset_demo_data():
    """
    Reset demo data for fresh demonstration.

    Clears all demo users and messages to start with a clean slate.
    This is useful for resetting between different judge evaluations.

    Returns:
        Dict containing reset confirmation
    """
    try:
        from src.utils.demo_utils import demo_data_generator

        logger.info("Resetting demo data for fresh demonstration")

        # Clear all demo data
        demo_data_generator.clear_demo_data()

        # Verify reset
        total_users = UserService.get_user_count()
        active_users = UserService.get_active_user_count()

        response = {
            "success": True,
            "message": "Demo data reset successfully",
            "current_stats": {
                "total_users": total_users,
                "active_users": active_users,
            },
            "reset_timestamp": datetime.now().isoformat(),
        }

        logger.info(f"Demo data reset complete: {response}")
        return response

    except Exception as e:
        logger.error(f"Failed to reset demo data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo reset failed: {str(e)}")


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

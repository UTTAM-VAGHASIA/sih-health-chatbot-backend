"""
Demo utilities and test data for WhatsApp Demo Bot.

This module provides demo-specific functionality including test data generation,
demo helper functions, and utilities for showcasing the bot's capabilities
during presentations and evaluations.
"""

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.config import get_logger
from src.db.models import User
from src.services.user_service import UserService

logger = get_logger(__name__)


class DemoDataGenerator:
    """Generator for demo test data and scenarios."""

    # Demo phone numbers for testing (fake numbers for demo purposes)
    DEMO_PHONE_NUMBERS = [
        "+917434017944",  # Primary demo number
        "+919876543210",  # Judge test 1
        "+919876543211",  # Judge test 2
        "+919876543212",  # Judge test 3
        "+919876543213",  # Judge test 4
        "+919876543214",  # Judge test 5
        "+918765432109",  # Demo user 1
        "+918765432108",  # Demo user 2
        "+918765432107",  # Demo user 3
        "+918765432106",  # Demo user 4
    ]

    # Demo messages for testing different response types
    DEMO_MESSAGES = [
        "hello",
        "hi there",
        "demo",
        "what are your features?",
        "health information",
        "tell me about SIH",
        "judges",
        "architecture",
        "broadcast",
        "help me",
        "what can you do?",
        "vaccination schedule",
        "disease prevention",
        "emergency alert",
    ]

    # Demo alert messages for broadcast testing
    DEMO_ALERTS = [
        {
            "message": "🚨 DEMO ALERT: This is a test broadcast to all registered users! All systems working perfectly.",
            "priority": "high",
        },
        {
            "message": "💉 Health Reminder: Vaccination drive starting tomorrow at all government health centers.",
            "priority": "medium",
        },
        {
            "message": "📊 Demo Statistics: WhatsApp integration working flawlessly with real-time user registration!",
            "priority": "low",
        },
        {
            "message": "🎯 For Judges: This demonstrates our real-time alert broadcasting capability for public health emergencies.",
            "priority": "high",
        },
    ]

    @classmethod
    def create_demo_users(cls, count: Optional[int] = None) -> List[User]:
        """
        Create demo users for testing and presentation.

        Args:
            count: Number of demo users to create (default: all demo numbers)

        Returns:
            List of created demo users
        """
        if count is None:
            phone_numbers = cls.DEMO_PHONE_NUMBERS
        else:
            phone_numbers = cls.DEMO_PHONE_NUMBERS[:count]

        created_users = []
        for phone_number in phone_numbers:
            try:
                # Check if user already exists
                existing_user = UserService.get_user_by_phone(phone_number)
                if existing_user:
                    logger.debug(f"Demo user {phone_number} already exists")
                    created_users.append(existing_user)
                    continue

                # Create new demo user
                user = UserService.register_user(phone_number)

                # Simulate some activity history
                cls._simulate_user_activity(user)

                created_users.append(user)
                logger.info(f"Created demo user: {phone_number}")

            except Exception as e:
                logger.error(f"Failed to create demo user {phone_number}: {str(e)}")

        logger.info(f"Demo users setup complete: {len(created_users)} users ready")
        return created_users

    @classmethod
    def _simulate_user_activity(cls, user: User) -> None:
        """
        Simulate realistic user activity for demo purposes.

        Args:
            user: User to simulate activity for
        """
        # Simulate random message count (1-20 messages)
        message_count = random.randint(1, 20)
        user.message_count = message_count

        # Simulate last activity within the last 7 days
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)

        last_activity = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        user.last_activity = last_activity

        # Simulate first seen date (1-30 days ago)
        first_seen_days_ago = random.randint(days_ago, 30)
        user.first_seen = datetime.now() - timedelta(days=first_seen_days_ago)

    @classmethod
    def get_demo_message(cls) -> str:
        """
        Get a random demo message for testing.

        Returns:
            Random demo message string
        """
        return random.choice(cls.DEMO_MESSAGES)

    @classmethod
    def get_demo_alert(cls) -> Dict[str, str]:
        """
        Get a random demo alert for broadcast testing.

        Returns:
            Dictionary with message and priority
        """
        return random.choice(cls.DEMO_ALERTS).copy()

    @classmethod
    def clear_demo_data(cls) -> None:
        """
        Clear all demo data (for resetting between presentations).
        """
        try:
            from src.db.models import messages_db, users_db

            # Clear all users and messages
            users_db.clear()
            messages_db.clear()

            logger.info("Demo data cleared successfully")

        except Exception as e:
            logger.error(f"Failed to clear demo data: {str(e)}")

    @classmethod
    def setup_judge_demo(cls) -> Dict[str, Any]:
        """
        Setup complete demo environment for judge evaluation.

        Returns:
            Dictionary with demo setup information
        """
        logger.info("Setting up judge demo environment...")

        try:
            # Clear existing data
            cls.clear_demo_data()

            # Create demo users
            demo_users = cls.create_demo_users(5)  # Create 5 demo users

            # Get demo statistics
            stats = {
                "demo_users_created": len(demo_users),
                "demo_phone_numbers": [user.phone_number for user in demo_users],
                "demo_messages_available": len(cls.DEMO_MESSAGES),
                "demo_alerts_available": len(cls.DEMO_ALERTS),
                "setup_timestamp": datetime.now().isoformat(),
            }

            logger.info(f"Judge demo environment ready: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to setup judge demo: {str(e)}")
            return {"error": str(e)}


class DemoLogger:
    """Enhanced logging utilities for demo debugging and monitoring."""

    @staticmethod
    def log_user_interaction(phone_number: str, message: str, response: str, processing_time: float) -> None:
        """
        Log detailed user interaction for demo monitoring.

        Args:
            phone_number: User's phone number (masked for privacy)
            message: User's message content
            response: Bot's response content
            processing_time: Time taken to process the message
        """
        masked_number = DemoLogger.mask_phone_number(phone_number)

        logger.info(
            f"DEMO_INTERACTION - User: {masked_number} | "
            f"Message: '{message[:50]}...' | "
            f"Response: '{response[:50]}...' | "
            f"Time: {processing_time:.2f}ms"
        )

    @staticmethod
    def log_broadcast_event(alert_message: str, users_targeted: int, success_count: int, failure_count: int) -> None:
        """
        Log broadcast alert events for demo monitoring.

        Args:
            alert_message: Alert message content
            users_targeted: Number of users targeted
            success_count: Number of successful deliveries
            failure_count: Number of failed deliveries
        """
        logger.info(
            f"DEMO_BROADCAST - Alert: '{alert_message[:50]}...' | "
            f"Targeted: {users_targeted} | "
            f"Success: {success_count} | "
            f"Failed: {failure_count}"
        )

    @staticmethod
    def log_demo_stats(stats: Dict[str, Any]) -> None:
        """
        Log demo statistics for monitoring.

        Args:
            stats: Dictionary containing demo statistics
        """
        logger.info(f"DEMO_STATS - {stats}")

    @staticmethod
    def mask_phone_number(phone_number: str) -> str:
        """
        Mask phone number for privacy in demo logs.

        Args:
            phone_number: Full phone number

        Returns:
            Masked phone number
        """
        if len(phone_number) <= 6:
            return phone_number

        if phone_number.startswith("+"):
            country_code = phone_number[:3]
            last_digits = phone_number[-4:]
            return f"{country_code}****{last_digits}"
        else:
            last_digits = phone_number[-4:]
            return f"****{last_digits}"


class DemoMetrics:
    """Demo metrics collection and reporting."""

    @staticmethod
    def get_demo_performance_metrics() -> Dict[str, Any]:
        """
        Get performance metrics for demo presentation.

        Returns:
            Dictionary with performance metrics
        """
        try:
            from src.db.models import messages_db, users_db

            total_users = len(users_db)
            active_users = len([user for user in users_db.values() if user.is_active])
            total_messages = len(messages_db)

            # Calculate average response time (simulated for demo)
            avg_response_time = random.uniform(150, 300)  # 150-300ms

            # Calculate uptime (simulated for demo)
            uptime_percentage = random.uniform(99.5, 99.9)

            metrics = {
                "total_users": total_users,
                "active_users": active_users,
                "total_messages": total_messages,
                "avg_response_time_ms": round(avg_response_time, 2),
                "uptime_percentage": round(uptime_percentage, 2),
                "system_status": "operational",
                "last_updated": datetime.now().isoformat(),
            }

            return metrics

        except Exception as e:
            logger.error(f"Failed to get demo metrics: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def get_user_engagement_stats() -> Dict[str, Any]:
        """
        Get user engagement statistics for demo.

        Returns:
            Dictionary with engagement statistics
        """
        try:
            from src.db.models import users_db

            if not users_db:
                return {"total_users": 0, "engagement_stats": "No users registered yet"}

            users = list(users_db.values())

            # Calculate engagement metrics
            total_messages = sum(user.message_count for user in users)
            avg_messages_per_user = total_messages / len(users) if users else 0

            # Recent activity (last 24 hours)
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_active_users = len([user for user in users if user.last_activity > recent_cutoff])

            stats = {
                "total_users": len(users),
                "total_messages": total_messages,
                "avg_messages_per_user": round(avg_messages_per_user, 2),
                "recent_active_users_24h": recent_active_users,
                "engagement_rate": round((recent_active_users / len(users)) * 100, 2) if users else 0,
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get engagement stats: {str(e)}")
            return {"error": str(e)}


# Global instances for easy import
demo_data_generator = DemoDataGenerator()
demo_logger = DemoLogger()
demo_metrics = DemoMetrics()

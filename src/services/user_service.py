"""
User Service for WhatsApp Demo Bot.

This service handles user registration, management, and provides methods
for user-related operations including automatic registration and broadcasting.
"""

from typing import List, Optional

from src.config import get_logger
from src.db.models import User, create_user, get_all_active_users, get_user, update_user_activity

logger = get_logger(__name__)


class UserService:
    """Service class for managing WhatsApp bot users."""

    @staticmethod
    def register_user(phone_number: str) -> User:
        """
        Register a new user or return existing user.

        Args:
            phone_number: User's WhatsApp phone number

        Returns:
            User: The registered or existing user

        Raises:
            ValueError: If phone number is invalid
        """
        if not phone_number or not isinstance(phone_number, str):
            raise ValueError("Phone number must be a non-empty string")

        # Normalize phone number format
        normalized_number = phone_number.strip()
        if not normalized_number.startswith("+"):
            normalized_number = f"+{normalized_number}"

        # Check if user already exists
        existing_user = get_user(normalized_number)
        if existing_user:
            logger.info(f"User {normalized_number} already registered")
            return existing_user

        # Create new user
        try:
            new_user = create_user(normalized_number)
            logger.info(f"Successfully registered new user: {normalized_number}")
            return new_user
        except Exception as e:
            logger.error(f"Failed to register user {normalized_number}: {str(e)}")
            raise

    @staticmethod
    def get_user_by_phone(phone_number: str) -> Optional[User]:
        """
        Get a user by their phone number.

        Args:
            phone_number: User's WhatsApp phone number

        Returns:
            Optional[User]: The user if found, None otherwise
        """
        if not phone_number:
            return None

        normalized_number = phone_number.strip()
        if not normalized_number.startswith("+"):
            normalized_number = f"+{normalized_number}"

        return get_user(normalized_number)

    @staticmethod
    def update_last_activity(phone_number: str) -> Optional[User]:
        """
        Update user's last activity timestamp and increment message count.

        Args:
            phone_number: User's WhatsApp phone number

        Returns:
            Optional[User]: The updated user if found, None otherwise
        """
        if not phone_number:
            return None

        try:
            updated_user = update_user_activity(phone_number)
            if updated_user:
                logger.debug(f"Updated activity for user {phone_number}")
            else:
                logger.warning(f"User {phone_number} not found for activity update")
            return updated_user
        except Exception as e:
            logger.error(f"Failed to update activity for user {phone_number}: {str(e)}")
            return None

    @staticmethod
    def get_all_active_users() -> List[User]:
        """
        Get all active users for broadcasting purposes.

        Returns:
            List[User]: List of all active users
        """
        try:
            active_users = get_all_active_users()
            logger.debug(f"Retrieved {len(active_users)} active users")
            return active_users
        except Exception as e:
            logger.error(f"Failed to retrieve active users: {str(e)}")
            return []

    @staticmethod
    def deactivate_user(phone_number: str) -> bool:
        """
        Deactivate a user (they won't receive broadcasts).

        Args:
            phone_number: User's WhatsApp phone number

        Returns:
            bool: True if user was deactivated, False otherwise
        """
        user = UserService.get_user_by_phone(phone_number)
        if user:
            user.is_active = False
            logger.info(f"Deactivated user {phone_number}")
            return True

        logger.warning(f"Cannot deactivate user {phone_number}: user not found")
        return False

    @staticmethod
    def reactivate_user(phone_number: str) -> bool:
        """
        Reactivate a user (they will receive broadcasts again).

        Args:
            phone_number: User's WhatsApp phone number

        Returns:
            bool: True if user was reactivated, False otherwise
        """
        user = UserService.get_user_by_phone(phone_number)
        if user:
            user.is_active = True
            logger.info(f"Reactivated user {phone_number}")
            return True

        logger.warning(f"Cannot reactivate user {phone_number}: user not found")
        return False

    @staticmethod
    def process_user_message(phone_number: str) -> User:
        """
        Process a message from a user - handles automatic registration and activity update.

        This method implements the automatic user registration requirement:
        - If user doesn't exist, register them automatically
        - If user exists, update their last activity
        - Always increment message count for the current message

        Args:
            phone_number: User's WhatsApp phone number

        Returns:
            User: The user (newly registered or existing)

        Raises:
            ValueError: If phone number is invalid
        """
        if not phone_number:
            raise ValueError("Phone number is required")

        # Try to get existing user
        user = UserService.get_user_by_phone(phone_number)

        if user:
            # Update existing user's activity
            UserService.update_last_activity(phone_number)
            logger.debug(f"Updated activity for existing user {phone_number}")
        else:
            # Register new user automatically
            user = UserService.register_user(phone_number)
            # Update activity for the first message
            UserService.update_last_activity(phone_number)
            logger.info(f"Auto-registered new user {phone_number}")

        return user

    @staticmethod
    def get_user_count() -> int:
        """
        Get the total number of registered users.

        Returns:
            int: Total number of users
        """
        try:
            from src.db.models import users_db

            return len(users_db)
        except Exception as e:
            logger.error(f"Failed to get user count: {str(e)}")
            return 0

    @staticmethod
    def get_active_user_count() -> int:
        """
        Get the number of active users.

        Returns:
            int: Number of active users
        """
        return len(UserService.get_all_active_users())

"""
Unit tests for User Service.

Tests cover user registration, management, and all functionality
required for the WhatsApp demo bot.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from src.db.models import clear_storage
from src.services.user_service import UserService


class TestUserService:
    """Test cases for UserService class."""

    def setup_method(self):
        """Clear storage before each test."""
        clear_storage()

    def teardown_method(self):
        """Clear storage after each test."""
        clear_storage()

    def test_register_user_new_user(self):
        """Test registering a new user."""
        phone_number = "+1234567890"

        user = UserService.register_user(phone_number)

        assert user is not None
        assert user.phone_number == phone_number
        assert user.is_active is True
        assert user.message_count == 0
        assert isinstance(user.first_seen, datetime)
        assert isinstance(user.last_activity, datetime)

    def test_register_user_existing_user(self):
        """Test registering an existing user returns the same user."""
        phone_number = "+1234567890"

        # Register user first time
        user1 = UserService.register_user(phone_number)
        original_first_seen = user1.first_seen

        # Register same user again
        user2 = UserService.register_user(phone_number)

        assert user1 is user2
        assert user2.first_seen == original_first_seen
        assert user2.phone_number == phone_number

    def test_register_user_normalizes_phone_number(self):
        """Test that phone numbers are normalized with + prefix."""
        phone_number = "1234567890"  # Without +

        user = UserService.register_user(phone_number)

        assert user.phone_number == "+1234567890"

    def test_register_user_invalid_phone_number(self):
        """Test registering with invalid phone number raises ValueError."""
        with pytest.raises(ValueError, match="Phone number must be a non-empty string"):
            UserService.register_user("")

        with pytest.raises(ValueError, match="Phone number must be a non-empty string"):
            UserService.register_user(None)

    def test_get_user_by_phone_existing_user(self):
        """Test getting an existing user by phone number."""
        phone_number = "+1234567890"
        UserService.register_user(phone_number)

        user = UserService.get_user_by_phone(phone_number)

        assert user is not None
        assert user.phone_number == phone_number

    def test_get_user_by_phone_nonexistent_user(self):
        """Test getting a non-existent user returns None."""
        user = UserService.get_user_by_phone("+9999999999")

        assert user is None

    def test_get_user_by_phone_normalizes_number(self):
        """Test that get_user_by_phone normalizes phone numbers."""
        # Register with +
        UserService.register_user("+1234567890")

        # Get without +
        user = UserService.get_user_by_phone("1234567890")

        assert user is not None
        assert user.phone_number == "+1234567890"

    def test_get_user_by_phone_empty_number(self):
        """Test getting user with empty phone number returns None."""
        user = UserService.get_user_by_phone("")
        assert user is None

        user = UserService.get_user_by_phone(None)
        assert user is None

    def test_update_last_activity_existing_user(self):
        """Test updating last activity for existing user."""
        phone_number = "+1234567890"
        user = UserService.register_user(phone_number)
        original_activity = user.last_activity
        original_count = user.message_count

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        updated_user = UserService.update_last_activity(phone_number)

        assert updated_user is not None
        assert updated_user.last_activity > original_activity
        assert updated_user.message_count == original_count + 1

    def test_update_last_activity_nonexistent_user(self):
        """Test updating last activity for non-existent user returns None."""
        result = UserService.update_last_activity("+9999999999")

        assert result is None

    def test_update_last_activity_empty_number(self):
        """Test updating last activity with empty phone number returns None."""
        result = UserService.update_last_activity("")
        assert result is None

        result = UserService.update_last_activity(None)
        assert result is None

    def test_get_all_active_users_empty(self):
        """Test getting active users when none exist."""
        users = UserService.get_all_active_users()

        assert users == []

    def test_get_all_active_users_with_users(self):
        """Test getting active users when some exist."""
        # Register multiple users
        UserService.register_user("+1234567890")
        UserService.register_user("+1234567891")
        UserService.register_user("+1234567892")

        users = UserService.get_all_active_users()

        assert len(users) == 3
        assert all(user.is_active for user in users)

    def test_get_all_active_users_excludes_inactive(self):
        """Test that inactive users are excluded from active users list."""
        # Register users
        UserService.register_user("+1234567890")
        UserService.register_user("+1234567891")

        # Deactivate one user
        UserService.deactivate_user("+1234567890")

        users = UserService.get_all_active_users()

        assert len(users) == 1
        assert users[0].phone_number == "+1234567891"

    def test_deactivate_user_existing_user(self):
        """Test deactivating an existing user."""
        phone_number = "+1234567890"
        UserService.register_user(phone_number)

        result = UserService.deactivate_user(phone_number)

        assert result is True
        user = UserService.get_user_by_phone(phone_number)
        assert user.is_active is False

    def test_deactivate_user_nonexistent_user(self):
        """Test deactivating a non-existent user returns False."""
        result = UserService.deactivate_user("+9999999999")

        assert result is False

    def test_reactivate_user_existing_user(self):
        """Test reactivating an existing user."""
        phone_number = "+1234567890"
        UserService.register_user(phone_number)
        UserService.deactivate_user(phone_number)

        result = UserService.reactivate_user(phone_number)

        assert result is True
        user = UserService.get_user_by_phone(phone_number)
        assert user.is_active is True

    def test_reactivate_user_nonexistent_user(self):
        """Test reactivating a non-existent user returns False."""
        result = UserService.reactivate_user("+9999999999")

        assert result is False

    def test_process_user_message_new_user(self):
        """Test processing message from new user auto-registers them."""
        phone_number = "+1234567890"

        user = UserService.process_user_message(phone_number)

        assert user is not None
        assert user.phone_number == phone_number
        assert user.is_active is True
        # Should be in the database now
        assert UserService.get_user_by_phone(phone_number) is not None

    def test_process_user_message_existing_user(self):
        """Test processing message from existing user updates activity."""
        phone_number = "+1234567890"

        # Register user first
        original_user = UserService.register_user(phone_number)
        original_activity = original_user.last_activity
        original_count = original_user.message_count

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        # Process message
        user = UserService.process_user_message(phone_number)

        assert user is not None
        assert user.phone_number == phone_number
        assert user.last_activity > original_activity
        assert user.message_count == original_count + 1

    def test_process_user_message_empty_number(self):
        """Test processing message with empty phone number raises ValueError."""
        with pytest.raises(ValueError, match="Phone number is required"):
            UserService.process_user_message("")

        with pytest.raises(ValueError, match="Phone number is required"):
            UserService.process_user_message(None)

    def test_get_user_count_empty(self):
        """Test getting user count when no users exist."""
        count = UserService.get_user_count()

        assert count == 0

    def test_get_user_count_with_users(self):
        """Test getting user count with multiple users."""
        UserService.register_user("+1234567890")
        UserService.register_user("+1234567891")
        UserService.register_user("+1234567892")

        count = UserService.get_user_count()

        assert count == 3

    def test_get_active_user_count_empty(self):
        """Test getting active user count when no users exist."""
        count = UserService.get_active_user_count()

        assert count == 0

    def test_get_active_user_count_with_users(self):
        """Test getting active user count with mixed active/inactive users."""
        UserService.register_user("+1234567890")
        UserService.register_user("+1234567891")
        UserService.register_user("+1234567892")

        # Deactivate one user
        UserService.deactivate_user("+1234567890")

        count = UserService.get_active_user_count()

        assert count == 2

    @patch("src.services.user_service.logger")
    def test_logging_on_registration(self, mock_logger):
        """Test that appropriate logging occurs during user registration."""
        phone_number = "+1234567890"

        # Register new user
        UserService.register_user(phone_number)
        mock_logger.info.assert_called_with(f"Successfully registered new user: {phone_number}")

        # Register existing user
        UserService.register_user(phone_number)
        mock_logger.info.assert_called_with(f"User {phone_number} already registered")

    @patch("src.services.user_service.logger")
    def test_logging_on_activity_update(self, mock_logger):
        """Test that appropriate logging occurs during activity updates."""
        phone_number = "+1234567890"
        UserService.register_user(phone_number)

        # Update existing user
        UserService.update_last_activity(phone_number)
        mock_logger.debug.assert_called_with(f"Updated activity for user {phone_number}")

        # Update non-existent user
        UserService.update_last_activity("+9999999999")
        mock_logger.warning.assert_called_with("User +9999999999 not found for activity update")

    def test_integration_user_lifecycle(self):
        """Test complete user lifecycle integration."""
        phone_number = "+1234567890"

        # 1. Process first message (auto-registration)
        user = UserService.process_user_message(phone_number)
        assert user.phone_number == phone_number
        assert user.message_count == 1

        # 2. Process second message (activity update)
        UserService.process_user_message(phone_number)
        updated_user = UserService.get_user_by_phone(phone_number)
        assert updated_user.message_count == 2

        # 3. Check user appears in active users
        active_users = UserService.get_all_active_users()
        assert len(active_users) == 1
        assert active_users[0].phone_number == phone_number

        # 4. Deactivate user
        UserService.deactivate_user(phone_number)
        active_users = UserService.get_all_active_users()
        assert len(active_users) == 0

        # 5. Reactivate user
        UserService.reactivate_user(phone_number)
        active_users = UserService.get_all_active_users()
        assert len(active_users) == 1


if __name__ == "__main__":
    pytest.main([__file__])

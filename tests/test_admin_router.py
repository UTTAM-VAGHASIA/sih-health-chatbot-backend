# tests/test_admin_router.py
"""
Tests for Admin API Router functionality.

This test suite covers alert broadcasting, input validation,
error handling, and admin statistics endpoints.
"""

from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.db.models import User, users_db
from src.main import app
from src.services.user_service import UserService

client = TestClient(app)


class TestAdminAlerts:
    """Test cases for admin alert broadcasting functionality."""

    def setup_method(self):
        """Set up test data before each test."""
        # Clear users database
        users_db.clear()

        # Add test users
        test_users = [
            User(
                phone_number="+917434017944",
                first_seen=datetime.now(),
                last_activity=datetime.now(),
                message_count=5,
                is_active=True,
            ),
            User(
                phone_number="+1234567891",
                first_seen=datetime.now(),
                last_activity=datetime.now(),
                message_count=3,
                is_active=True,
            ),
            User(
                phone_number="+1234567892",
                first_seen=datetime.now(),
                last_activity=datetime.now(),
                message_count=1,
                is_active=False,  # Inactive user
            ),
        ]

        for user in test_users:
            users_db[user.phone_number] = user

    def teardown_method(self):
        """Clean up after each test."""
        users_db.clear()

    @patch("src.routers.admin.send_message")
    def test_broadcast_alert_success(self, mock_send_message):
        """Test successful alert broadcasting to all active users."""
        # Mock successful message sending
        mock_send_message.return_value = {"message_id": "test_123"}

        alert_data = {"message": "This is a test health alert", "priority": "high"}

        response = client.post("/admin/alerts", json=alert_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["users_targeted"] == 2  # Only active users
        assert data["successful_deliveries"] == 2
        assert data["failed_deliveries"] == 0
        assert "alert_" in data["message_id"]
        assert data["errors"] is None

        # Verify send_message was called for each active user
        assert mock_send_message.call_count == 2

    @patch("src.routers.admin.send_message")
    def test_broadcast_alert_partial_failure(self, mock_send_message):
        """Test alert broadcasting with some delivery failures."""

        # Mock mixed success/failure responses
        def mock_send_side_effect(phone_number, message):
            if phone_number == "+917434017944":
                return {"message_id": "success_123"}
            else:
                return {"error": "Network timeout"}

        mock_send_message.side_effect = mock_send_side_effect

        alert_data = {"message": "Test alert with failures", "priority": "medium"}

        response = client.post("/admin/alerts", json=alert_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["users_targeted"] == 2
        assert data["successful_deliveries"] == 1
        assert data["failed_deliveries"] == 1
        assert data["errors"] is not None
        assert len(data["errors"]) == 1
        assert "Network timeout" in data["errors"][0]

    def test_broadcast_alert_no_users(self):
        """Test alert broadcasting when no users are registered."""
        # Clear all users
        users_db.clear()

        alert_data = {"message": "Test alert with no users", "priority": "low"}

        response = client.post("/admin/alerts", json=alert_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["users_targeted"] == 0
        assert data["successful_deliveries"] == 0
        assert data["failed_deliveries"] == 0

    def test_broadcast_alert_invalid_message(self):
        """Test alert broadcasting with invalid message content."""
        invalid_requests = [
            {"message": "", "priority": "high"},  # Empty message
            {"message": "   ", "priority": "medium"},  # Whitespace only
            {"priority": "low"},  # Missing message
            {"message": "Valid message", "priority": "invalid"},  # Invalid priority
        ]

        for invalid_data in invalid_requests:
            response = client.post("/admin/alerts", json=invalid_data)
            assert response.status_code == 422  # Validation error

    def test_broadcast_alert_message_too_long(self):
        """Test alert broadcasting with message exceeding length limit."""
        long_message = "x" * 1001  # Exceeds 1000 character limit

        alert_data = {"message": long_message, "priority": "medium"}

        response = client.post("/admin/alerts", json=alert_data)
        assert response.status_code == 422

    def test_alert_message_formatting(self):
        """Test alert message formatting with different priorities."""
        from src.routers.admin import format_alert_message

        test_cases = [
            ("Test message", "low", "ℹ️ INFO: Test message\n\n📱 SIH Health Assistant"),
            ("Urgent alert", "high", "🚨 URGENT: Urgent alert\n\n📱 SIH Health Assistant"),
            ("Regular alert", "medium", "⚠️ ALERT: Regular alert\n\n📱 SIH Health Assistant"),
            ("Default priority", None, "⚠️ ALERT: Default priority\n\n📱 SIH Health Assistant"),
        ]

        for message, priority, expected in test_cases:
            result = format_alert_message(message, priority)
            assert result == expected


class TestAdminStats:
    """Test cases for admin statistics endpoints."""

    def setup_method(self):
        """Set up test data before each test."""
        users_db.clear()

        # Add mixed active/inactive users
        test_users = [
            User("+917434017944", datetime.now(), datetime.now(), 5, True),
            User("+1234567891", datetime.now(), datetime.now(), 3, True),
            User("+1234567892", datetime.now(), datetime.now(), 1, False),
            User("+1234567893", datetime.now(), datetime.now(), 0, False),
        ]

        for user in test_users:
            users_db[user.phone_number] = user

    def teardown_method(self):
        """Clean up after each test."""
        users_db.clear()

    def test_get_admin_stats(self):
        """Test admin statistics endpoint."""
        response = client.get("/admin/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_users"] == 4
        assert data["active_users"] == 2
        assert data["inactive_users"] == 2
        assert data["system_status"] == "operational"
        assert "last_updated" in data

    def test_get_registered_users(self):
        """Test registered users list endpoint."""
        response = client.get("/admin/users")

        assert response.status_code == 200
        data = response.json()

        assert "users" in data
        assert "total_count" in data
        assert data["total_count"] == 2  # Only active users returned

        # Check user data structure
        for user in data["users"]:
            assert "phone_number" in user
            assert "first_seen" in user
            assert "last_activity" in user
            assert "message_count" in user
            assert "is_active" in user

            # Verify phone number is masked
            assert "*" in user["phone_number"]

    def test_phone_number_masking(self):
        """Test phone number masking functionality."""
        from src.routers.admin import mask_phone_number

        test_cases = [
            ("+917434017944", "+91****7944"),
            ("+1234567890", "+12****7890"),
            ("1234567890", "******7890"),
            ("+91123", "+91123"),  # Too short to mask
        ]

        for original, expected in test_cases:
            result = mask_phone_number(original)
            assert result == expected


class TestAdminErrorHandling:
    """Test cases for admin API error handling."""

    def test_malformed_json_request(self):
        """Test handling of malformed JSON requests."""
        response = client.post("/admin/alerts", data="invalid json", headers={"Content-Type": "application/json"})

        assert response.status_code == 422

    @patch("src.routers.admin.UserService.get_all_active_users")
    def test_database_error_handling(self, mock_get_users):
        """Test handling of database errors during alert broadcasting."""
        # Mock database error
        mock_get_users.side_effect = Exception("Database connection failed")

        alert_data = {"message": "Test alert", "priority": "medium"}

        response = client.post("/admin/alerts", json=alert_data)

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

    @patch("src.routers.admin.UserService.get_user_count")
    def test_stats_error_handling(self, mock_get_count):
        """Test error handling in admin stats endpoint."""
        # Mock service error
        mock_get_count.side_effect = Exception("Service unavailable")

        response = client.get("/admin/stats")

        assert response.status_code == 500
        assert "Failed to retrieve admin statistics" in response.json()["detail"]


class TestAdminIntegration:
    """Integration tests for admin functionality."""

    def setup_method(self):
        """Set up integration test environment."""
        users_db.clear()

    def teardown_method(self):
        """Clean up integration test environment."""
        users_db.clear()

    @patch("src.routers.admin.send_message")
    def test_end_to_end_alert_flow(self, mock_send_message):
        """Test complete alert broadcasting flow."""
        # Mock successful message sending
        mock_send_message.return_value = {"message_id": "integration_test"}

        # Register users through UserService
        UserService.register_user("+917434017944")
        UserService.register_user("+1234567891")

        # Send alert
        alert_data = {"message": "Integration test alert", "priority": "high"}

        response = client.post("/admin/alerts", json=alert_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["users_targeted"] == 2
        assert data["successful_deliveries"] == 2

        # Verify stats endpoint reflects the users
        stats_response = client.get("/admin/stats")
        stats_data = stats_response.json()

        assert stats_data["total_users"] == 2
        assert stats_data["active_users"] == 2

    def test_admin_endpoints_accessibility(self):
        """Test that all admin endpoints are accessible."""
        endpoints = [
            ("/admin/stats", "GET"),
            ("/admin/users", "GET"),
        ]

        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)

            # Should not return 404 (endpoint exists)
            assert response.status_code != 404

"""
Test suite for demo enhancements and polish features.

This test suite verifies that all demo-specific enhancements are working
correctly, including judge-friendly responses, user count tracking,
demo test data generation, and comprehensive logging.
"""

from unittest.mock import Mock, patch

import pytest

from src.services.message_service import MessageService
from src.utils.demo_setup import DemoSetup
from src.utils.demo_utils import DemoDataGenerator, DemoLogger, DemoMetrics


class TestDemoEnhancements:
    """Test class for demo enhancement features."""

    def setup_method(self):
        """Setup test environment before each test."""
        self.message_service = MessageService()
        self.demo_generator = DemoDataGenerator()
        self.demo_logger = DemoLogger()
        self.demo_metrics = DemoMetrics()
        self.demo_setup = DemoSetup()

    def test_judge_friendly_responses(self):
        """Test that judge-friendly response messages are working."""
        # Test judge-specific keywords
        response = self.message_service.generate_response("judges", "test_user")
        assert "For Evaluation Panel" in response.content
        assert "LIVE working demo" in response.content

        # Test architecture keyword
        response = self.message_service.generate_response("architecture", "test_user")
        assert "System Architecture" in response.content
        assert "FastAPI backend" in response.content

        # Test broadcast keyword
        response = self.message_service.generate_response("broadcast", "test_user")
        assert "Admin Broadcast System" in response.content
        assert "POST /admin/alerts" in response.content

    def test_enhanced_demo_responses(self):
        """Test enhanced demo responses with judge-specific content."""
        # Test demo keyword
        response = self.message_service.generate_response("demo", "test_user")
        assert "*LIVE DEMO*" in response.content
        assert "Government of Odisha" in response.content
        assert "Tech Stack" in response.content

        # Test features keyword
        response = self.message_service.generate_response("features", "test_user")
        assert "*Key Features Demonstrated*" in response.content
        assert "Judge Note" in response.content

        # Test health keyword
        response = self.message_service.generate_response("health", "test_user")
        assert "*Health Assistant Capabilities*" in response.content
        assert "SIH Problem ID 25049" in response.content

    def test_enhanced_help_message(self):
        """Test enhanced help message with judge-specific content."""
        help_message = self.message_service.get_help_message()
        assert "*For Judges*" in help_message
        assert "All features are working live" in help_message
        assert "Government of Odisha" in help_message

    def test_demo_data_generator(self):
        """Test demo data generation functionality."""
        # Test demo phone numbers
        assert len(self.demo_generator.DEMO_PHONE_NUMBERS) >= 5
        assert all(phone.startswith("+91") for phone in self.demo_generator.DEMO_PHONE_NUMBERS)

        # Test demo messages
        assert len(self.demo_generator.DEMO_MESSAGES) > 0
        demo_message = self.demo_generator.get_demo_message()
        assert isinstance(demo_message, str)
        assert len(demo_message) > 0

        # Test demo alerts
        demo_alert = self.demo_generator.get_demo_alert()
        assert "message" in demo_alert
        assert "priority" in demo_alert
        assert demo_alert["priority"] in ["low", "medium", "high"]

    @patch("src.db.models.users_db")
    @patch("src.db.models.messages_db")
    def test_demo_metrics(self, mock_messages_db, mock_users_db):
        """Test demo metrics collection."""
        # Mock data
        mock_users_db.__len__.return_value = 5
        mock_users_db.values.return_value = []
        mock_messages_db.__len__.return_value = 20

        # Test performance metrics
        metrics = self.demo_metrics.get_demo_performance_metrics()
        assert "total_users" in metrics
        assert "avg_response_time_ms" in metrics
        assert "uptime_percentage" in metrics
        assert "system_status" in metrics

        # Test engagement stats
        engagement = self.demo_metrics.get_user_engagement_stats()
        assert "total_users" in engagement

    def test_demo_logger_phone_masking(self):
        """Test phone number masking for privacy."""
        # Test with country code
        masked = self.demo_logger.mask_phone_number("+917434017944")
        assert masked == "+91****7944"

        # Test without country code
        masked = self.demo_logger.mask_phone_number("7434017944")
        assert masked == "****7944"

        # Test short number
        masked = self.demo_logger.mask_phone_number("123")
        assert masked == "123"

    def test_demo_setup_judge_instructions(self):
        """Test judge instruction generation."""
        demo_users = [Mock(phone_number="+917434017944")]
        instructions = self.demo_setup._generate_judge_instructions(demo_users)

        assert "overview" in instructions
        assert "test_phone_numbers" in instructions
        assert "test_scenarios" in instructions
        assert "evaluation_points" in instructions

        # Check scenarios
        scenarios = instructions["test_scenarios"]
        assert len(scenarios) >= 3
        assert any("Basic Chat Interaction" in scenario["scenario"] for scenario in scenarios)

    def test_demo_commands_list(self):
        """Test demo commands list generation."""
        commands = self.demo_setup._get_demo_commands()
        assert len(commands) > 0

        # Check required commands
        command_names = [cmd["command"] for cmd in commands]
        assert "hello" in command_names
        assert "demo" in command_names
        assert "judges" in command_names
        assert "health" in command_names

    def test_admin_endpoints_list(self):
        """Test admin endpoints list generation."""
        endpoints = self.demo_setup._get_admin_endpoints()
        assert len(endpoints) > 0

        # Check required endpoints
        endpoint_paths = [ep["endpoint"] for ep in endpoints]
        assert any("POST /admin/alerts" in ep for ep in endpoint_paths)
        assert any("GET /admin/stats" in ep for ep in endpoint_paths)
        assert any("POST /admin/demo/setup" in ep for ep in endpoint_paths)

    def test_demo_report_generation(self):
        """Test comprehensive demo report generation."""
        with (
            patch("src.services.user_service.UserService.get_user_count", return_value=5),
            patch("src.services.user_service.UserService.get_active_user_count", return_value=4),
        ):

            report = self.demo_setup.generate_demo_report()

            assert "report_metadata" in report
            assert "system_overview" in report
            assert "current_statistics" in report
            assert "features_demonstrated" in report
            assert "demo_capabilities" in report
            assert "evaluation_notes" in report

            # Check metadata
            metadata = report["report_metadata"]
            assert metadata["sih_problem_id"] == "25049"
            assert "Government of Odisha" in metadata["client"]

    @patch("src.utils.demo_utils.demo_logger")
    def test_demo_logging_integration(self, mock_demo_logger):
        """Test demo logging integration."""
        # Test user interaction logging
        self.demo_logger.log_user_interaction(
            phone_number="+917434017944", message="hello", response="Welcome message", processing_time=150.5
        )

        # Test broadcast event logging
        self.demo_logger.log_broadcast_event(
            alert_message="Test alert", users_targeted=5, success_count=4, failure_count=1
        )

        # Test demo stats logging
        self.demo_logger.log_demo_stats({"test": "data"})

    def test_error_handling_in_demo_utils(self):
        """Test error handling in demo utilities."""
        # Test demo setup error handling by patching at module level
        with patch("src.utils.demo_utils.DemoDataGenerator.create_demo_users", side_effect=Exception("Test error")):
            result = self.demo_setup.setup_complete_demo()
            assert result["success"] is False
            assert "error" in result

        # Test metrics with empty data (should still work)
        with patch("src.db.models.users_db", {}):
            metrics = self.demo_metrics.get_demo_performance_metrics()
            assert "total_users" in metrics
            assert metrics["total_users"] == 0


class TestDemoIntegration:
    """Integration tests for demo features."""

    def test_message_service_demo_integration(self):
        """Test message service integration with demo features."""
        message_service = MessageService()

        # Test all demo-specific keywords
        demo_keywords = [
            ("judges", "For Evaluation Panel"),
            ("architecture", "System Architecture"),
            ("broadcast", "Admin Broadcast System"),
            ("demo", "LIVE DEMO"),
            ("features", "Key Features Demonstrated"),
            ("health", "Health Assistant Capabilities"),
        ]

        for keyword, expected_content in demo_keywords:
            response = message_service.generate_response(keyword, "test_user")
            assert expected_content in response.content, f"Expected '{expected_content}' in response for '{keyword}'"

    def test_complete_demo_workflow(self):
        """Test complete demo workflow from setup to reporting."""
        demo_setup = DemoSetup()

        # Test setup
        with (
            patch("src.utils.demo_utils.DemoDataGenerator.create_demo_users", return_value=[]),
            patch("src.utils.demo_utils.DemoDataGenerator.clear_demo_data"),
        ):

            setup_result = demo_setup.setup_complete_demo()
            assert setup_result["success"] is True
            assert "judge_instructions" in setup_result
            assert "demo_commands" in setup_result

        # Test report generation
        with patch("src.services.user_service.UserService.get_user_count", return_value=5):
            report = demo_setup.generate_demo_report()
            assert "report_metadata" in report
            assert "features_demonstrated" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

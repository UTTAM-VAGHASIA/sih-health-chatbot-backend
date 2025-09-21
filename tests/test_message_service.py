"""
Unit tests for the Message Service.

Tests cover greeting detection, response generation, demo-specific responses,
fallback handling, and error scenarios.
"""

import pytest

from src.services.message_service import MessageResponse, MessageService


class TestMessageService:
    """Test suite for MessageService functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = MessageService()
        self.test_user_id = "+917434017944"

    def test_greeting_detection(self):
        """Test that various greeting patterns are correctly identified."""
        greetings = [
            "hi",
            "hello",
            "hey",
            "Hi there",
            "HELLO",
            "good morning",
            "good afternoon",
            "good evening",
            "start",
            "begin",
            "namaste",
            "hola",
        ]

        for greeting in greetings:
            assert self.service.is_greeting(greeting.lower()), f"Failed to detect greeting: {greeting}"

    def test_non_greeting_detection(self):
        """Test that non-greeting messages are not identified as greetings."""
        non_greetings = [
            "what is health",
            "demo features",
            "help me",
            "I need assistance",
            "tell me about sih",
            "random message",
        ]

        for message in non_greetings:
            assert not self.service.is_greeting(message.lower()), f"Incorrectly detected greeting: {message}"

    def test_greeting_response(self):
        """Test that greeting messages return welcome response."""
        greetings = ["hi", "hello", "good morning", "start"]

        for greeting in greetings:
            response = self.service.generate_response(greeting, self.test_user_id)
            assert isinstance(response, MessageResponse)
            assert "Welcome to our Health Assistant" in response.content
            assert response.requires_followup is True

    def test_demo_keyword_responses(self):
        """Test responses to demo-related keywords."""
        demo_messages = [
            ("demo", "real-time WhatsApp messaging"),
            ("showcase", "real-time WhatsApp messaging"),
            ("presentation", "real-time WhatsApp messaging"),
        ]

        for message, expected_content in demo_messages:
            response = self.service.generate_response(message, self.test_user_id)
            assert expected_content in response.content
            assert response.message_type == "text"

    def test_features_keyword_responses(self):
        """Test responses to feature-related keywords."""
        feature_messages = ["features", "capability", "what can you do"]

        for message in feature_messages:
            response = self.service.generate_response(message, self.test_user_id)
            assert "Auto user registration" in response.content
            assert "broadcast alerts" in response.content

    def test_health_keyword_responses(self):
        """Test responses to health-related keywords."""
        health_messages = ["health", "medical", "doctor", "medicine"]

        for message in health_messages:
            response = self.service.generate_response(message, self.test_user_id)
            assert "health information" in response.content
            assert "vaccination schedules" in response.content

    def test_sih_keyword_responses(self):
        """Test responses to SIH/competition-related keywords."""
        sih_messages = ["sih", "hackathon", "competition", "odisha"]

        for message in sih_messages:
            response = self.service.generate_response(message, self.test_user_id)
            assert "SIH 2025" in response.content
            assert "Government of Odisha" in response.content

    def test_help_keyword_responses(self):
        """Test responses to help-related keywords."""
        help_messages = ["help", "support", "assist me"]

        for message in help_messages:
            response = self.service.generate_response(message, self.test_user_id)
            help_content = self.service.get_help_message()
            assert response.content == help_content
            assert "Health Assistant Bot" in response.content

    def test_default_fallback_response(self):
        """Test default response for unknown messages."""
        unknown_messages = [
            "random text",
            "xyz123",
            "completely unknown message",
            "this should trigger default response",
        ]

        for message in unknown_messages:
            response = self.service.generate_response(message, self.test_user_id)
            assert "Thanks for your message" in response.content
            assert "WhatsApp integration capabilities" in response.content

    def test_empty_message_handling(self):
        """Test handling of empty or whitespace-only messages."""
        empty_messages = ["", "   ", "\n", "\t", None]

        for message in empty_messages:
            response = self.service.generate_response(message, self.test_user_id)
            assert "Please send me a message to get started" in response.content

    def test_case_insensitive_processing(self):
        """Test that message processing is case-insensitive."""
        test_cases = [
            ("HELLO", "Welcome to our Health Assistant"),
            ("Demo", "real-time WhatsApp messaging"),
            ("FEATURES", "Auto user registration"),
            ("Health", "health information"),
        ]

        for message, expected_content in test_cases:
            response = self.service.generate_response(message, self.test_user_id)
            assert expected_content in response.content

    def test_help_message_content(self):
        """Test the structure and content of help message."""
        help_message = self.service.get_help_message()

        expected_elements = ["Health Assistant Bot", "demo", "features", "health", "sih", "WhatsApp integration"]

        for element in expected_elements:
            assert element in help_message

    def test_fallback_response_variety(self):
        """Test that fallback responses provide variety based on attempt count."""
        fallback_0 = self.service.get_fallback_response(0)
        fallback_1 = self.service.get_fallback_response(1)
        fallback_2 = self.service.get_fallback_response(2)

        # Should get different messages for different attempt counts
        assert fallback_0 != fallback_1
        assert fallback_1 != fallback_2

        # High attempt count should not cause errors
        fallback_high = self.service.get_fallback_response(10)
        assert isinstance(fallback_high, str)
        assert len(fallback_high) > 0

    def test_error_message_processing(self):
        """Test error message generation for different error types."""
        error_types = ["general", "network", "processing", "unknown_type"]

        for error_type in error_types:
            response = self.service.process_error_message(error_type)
            assert isinstance(response, MessageResponse)
            assert len(response.content) > 0
            # Check that error messages contain appropriate keywords
            content_lower = response.content.lower()
            error_keywords = ["sorry", "trouble", "issues", "try again", "couldn't"]
            assert any(keyword in content_lower for keyword in error_keywords)

    def test_message_response_structure(self):
        """Test that MessageResponse objects have correct structure."""
        response = self.service.generate_response("hello", self.test_user_id)

        assert hasattr(response, "content")
        assert hasattr(response, "message_type")
        assert hasattr(response, "requires_followup")
        assert isinstance(response.content, str)
        assert isinstance(response.message_type, str)
        assert isinstance(response.requires_followup, bool)

    def test_whitespace_handling(self):
        """Test proper handling of messages with extra whitespace."""
        messages_with_whitespace = ["  hello  ", "\thello\n", "   demo   ", "\n\nfeatures\t\t"]

        for message in messages_with_whitespace:
            response = self.service.generate_response(message, self.test_user_id)
            # Should process correctly despite whitespace
            assert len(response.content) > 0
            assert response.message_type == "text"

    def test_multiple_keywords_in_message(self):
        """Test handling of messages containing multiple keywords."""
        multi_keyword_messages = [
            "hello, tell me about demo features",
            "hi there, what health services do you provide",
            "demo and sih information please",
        ]

        for message in multi_keyword_messages:
            response = self.service.generate_response(message, self.test_user_id)
            # Should return a valid response (priority based on first match)
            assert len(response.content) > 0
            assert response.message_type == "text"


if __name__ == "__main__":
    pytest.main([__file__])

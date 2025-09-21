"""
Message Service for intelligent WhatsApp bot responses.

This service handles message processing, response generation, and conversation logic
for the WhatsApp demo bot. It provides greeting detection, demo-specific responses,
and fallback handling for unknown messages.
"""

import re
from dataclasses import dataclass


@dataclass
class MessageResponse:
    """Response object containing the bot's reply and metadata."""

    content: str
    message_type: str = "text"
    requires_followup: bool = False


class MessageService:
    """Service for processing user messages and generating intelligent responses."""

    def __init__(self):
        """Initialize the message service with predefined responses."""
        self.greeting_patterns = [
            r"\b(hi|hello|hey|hola|namaste)\b",
            r"\b(good\s+(morning|afternoon|evening))\b",
            r"\b(start|begin)\b",
        ]

        self.demo_responses = {
            "welcome": "👋 Welcome to our Health Assistant! This is a live WhatsApp integration demo for SIH 2025.",
            "demo": "🚀 This bot showcases real-time WhatsApp messaging with intelligent health responses! Built for Government of Odisha.",
            "features": "✨ Features: Auto user registration, broadcast alerts, intelligent chat responses, health information delivery",
            "health": "🏥 I can help with health information, vaccination schedules, disease awareness, and preventive care tips!",
            "sih": "🏆 This is our SIH 2025 submission (Problem ID: 25049) for the Government of Odisha - AI-driven public health chatbot system.",
            "default": "Thanks for your message! This demo shows our WhatsApp integration capabilities. Try 'demo', 'features', or 'health'!",
        }

        self.fallback_messages = [
            "I'm here to help with health-related questions. Try asking about 'health' or 'features'!",
            "Sorry, I didn't understand that. Type 'demo' to see what I can do!",
            "I'm still learning! For now, try 'health', 'demo', or 'features' to see my capabilities.",
        ]

    def generate_response(self, message: str, user_id: str) -> MessageResponse:
        """
        Generate an appropriate response based on user input.

        Args:
            message: The user's message content
            user_id: The user's phone number or identifier

        Returns:
            MessageResponse object with the bot's reply
        """
        if not message or not message.strip():
            return MessageResponse(content="Please send me a message to get started!", message_type="text")

        message_lower = message.lower().strip()

        # Check for greetings
        if self.is_greeting(message_lower):
            return MessageResponse(content=self.demo_responses["welcome"], message_type="text", requires_followup=True)

        # Check for demo-specific keywords
        if any(keyword in message_lower for keyword in ["demo", "showcase", "presentation"]):
            return MessageResponse(content=self.demo_responses["demo"], message_type="text")

        if any(keyword in message_lower for keyword in ["feature", "capability", "what can you"]):
            return MessageResponse(content=self.demo_responses["features"], message_type="text")

        if any(keyword in message_lower for keyword in ["health", "medical", "doctor", "medicine"]):
            return MessageResponse(content=self.demo_responses["health"], message_type="text")

        if any(keyword in message_lower for keyword in ["sih", "hackathon", "competition", "odisha"]):
            return MessageResponse(content=self.demo_responses["sih"], message_type="text")

        # Help requests
        if any(keyword in message_lower for keyword in ["help", "support", "assist"]):
            return MessageResponse(content=self.get_help_message(), message_type="text")

        # Default fallback response
        return MessageResponse(content=self.demo_responses["default"], message_type="text")

    def is_greeting(self, message: str) -> bool:
        """
        Check if the message contains a greeting pattern.

        Args:
            message: The message to check (should be lowercase)

        Returns:
            True if message contains a greeting, False otherwise
        """
        for pattern in self.greeting_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False

    def get_help_message(self) -> str:
        """
        Get the help message explaining bot capabilities.

        Returns:
            Help message string
        """
        return (
            "🤖 I'm your Health Assistant Bot! Here's what you can try:\n\n"
            "• Type 'demo' - See the demo features\n"
            "• Type 'features' - Learn about my capabilities\n"
            "• Type 'health' - Get health information\n"
            "• Type 'sih' - About our SIH 2025 project\n\n"
            "This is a live demonstration of WhatsApp integration for healthcare!"
        )

    def get_fallback_response(self, attempt_count: int = 0) -> str:
        """
        Get a fallback response for unknown messages.

        Args:
            attempt_count: Number of previous fallback attempts (for variety)

        Returns:
            Fallback message string
        """
        index = min(attempt_count, len(self.fallback_messages) - 1)
        return self.fallback_messages[index]

    def process_error_message(self, error_type: str = "general") -> MessageResponse:
        """
        Generate error response for system failures.

        Args:
            error_type: Type of error that occurred

        Returns:
            MessageResponse with error message
        """
        error_messages = {
            "general": "Sorry, I'm having trouble right now. Please try again later.",
            "network": "I'm having connectivity issues. Please try sending your message again.",
            "processing": "I couldn't process your message properly. Could you try rephrasing it?",
        }

        message = error_messages.get(error_type, error_messages["general"])
        return MessageResponse(content=message, message_type="text")


# Global instance for easy import
message_service = MessageService()

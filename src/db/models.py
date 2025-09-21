"""
Data models for WhatsApp Demo Bot.

This module contains the dataclasses and in-memory storage for the demo bot.
For production use, these would be replaced with proper database models.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class User:
    """User model for WhatsApp bot users."""

    phone_number: str
    first_seen: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    is_active: bool = True

    def __post_init__(self):
        """Ensure phone number is properly formatted."""
        if not self.phone_number.startswith("+"):
            self.phone_number = f"+{self.phone_number}"


@dataclass
class Message:
    """Message model for storing chat history."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_user: str = ""
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: str = "user"  # 'user' or 'bot'

    def __post_init__(self):
        """Validate message type."""
        if self.message_type not in ["user", "bot"]:
            raise ValueError("message_type must be 'user' or 'bot'")


# In-memory storage for demo purposes
# In production, these would be replaced with proper database connections
users_db: Dict[str, User] = {}
messages_db: List[Message] = []


# Utility functions for data access
def get_user(phone_number: str) -> Optional[User]:
    """Get a user by phone number."""
    # Ensure consistent phone number format
    if not phone_number.startswith("+"):
        phone_number = f"+{phone_number}"
    return users_db.get(phone_number)


def create_user(phone_number: str) -> User:
    """Create a new user and store in memory."""
    # Ensure consistent phone number format
    if not phone_number.startswith("+"):
        phone_number = f"+{phone_number}"

    user = User(phone_number=phone_number)
    users_db[phone_number] = user
    return user


def update_user_activity(phone_number: str) -> Optional[User]:
    """Update user's last activity timestamp."""
    user = get_user(phone_number)
    if user:
        user.last_activity = datetime.now()
        user.message_count += 1
    return user


def get_all_active_users() -> List[User]:
    """Get all active users for broadcasting."""
    return [user for user in users_db.values() if user.is_active]


def store_message(from_user: str, content: str, message_type: str = "user") -> Message:
    """Store a message in memory."""
    message = Message(from_user=from_user, content=content, message_type=message_type)
    messages_db.append(message)
    return message


def get_user_messages(phone_number: str, limit: int = 50) -> List[Message]:
    """Get recent messages for a specific user."""
    # Ensure consistent phone number format
    if not phone_number.startswith("+"):
        phone_number = f"+{phone_number}"

    user_messages = [msg for msg in messages_db if msg.from_user == phone_number]
    # Return most recent messages first
    return sorted(user_messages, key=lambda x: x.timestamp, reverse=True)[:limit]


def get_all_messages(limit: int = 100) -> List[Message]:
    """Get all messages, most recent first."""
    return sorted(messages_db, key=lambda x: x.timestamp, reverse=True)[:limit]


def clear_storage() -> None:
    """Clear all stored data (useful for demo resets)."""
    global users_db, messages_db
    users_db.clear()
    messages_db.clear()


def get_storage_stats() -> Dict[str, int]:
    """Get statistics about stored data."""
    return {
        "total_users": len(users_db),
        "active_users": len(get_all_active_users()),
        "total_messages": len(messages_db),
    }

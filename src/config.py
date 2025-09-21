# src/config.py
"""
Configuration module for the SIH Health Chatbot Backend.

This module handles environment configuration, logging setup, and application settings
with comprehensive error handling and validation.
"""

import logging
import logging.config
import os
import sys
from typing import Any, Dict, Optional, cast


class Config:
    """Application configuration with environment variable management."""

    # WhatsApp API Configuration
    WHATSAPP_VERIFY_TOKEN: Optional[str] = os.getenv("WHATSAPP_VERIFY_TOKEN")
    WHATSAPP_ACCESS_TOKEN: Optional[str] = os.getenv("WHATSAPP_ACCESS_TOKEN")
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    # API Configuration
    WHATSAPP_API_URL: str = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v23.0")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "10"))

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "detailed")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")

    # Application Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    @classmethod
    def validate_required_config(cls) -> Dict[str, Any]:
        """
        Validate required configuration and return validation results.

        Returns:
            Dict containing validation results and missing configurations
        """
        required_configs = {
            "WHATSAPP_VERIFY_TOKEN": cls.WHATSAPP_VERIFY_TOKEN,
            "WHATSAPP_ACCESS_TOKEN": cls.WHATSAPP_ACCESS_TOKEN,
            "WHATSAPP_PHONE_NUMBER_ID": cls.WHATSAPP_PHONE_NUMBER_ID,
        }

        missing_configs = [key for key, value in required_configs.items() if not value]

        return {
            "is_valid": len(missing_configs) == 0,
            "missing_configs": missing_configs,
            "warnings": cls._get_config_warnings(),
        }

    @classmethod
    def _get_config_warnings(cls) -> list:
        """Get configuration warnings for optional but recommended settings."""
        warnings = []

        if not cls.WHATSAPP_VERIFY_TOKEN:
            warnings.append("WHATSAPP_VERIFY_TOKEN not set - webhook signature verification disabled")

        if cls.ENVIRONMENT == "production" and cls.DEBUG:
            warnings.append("DEBUG mode enabled in production environment")

        return warnings


def setup_logging() -> None:
    """
    Configure comprehensive logging for the application.

    Sets up structured logging with appropriate handlers, formatters,
    and log levels based on environment configuration.
    """
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)

    # Define log formats
    formats = {
        "simple": "%(levelname)s - %(message)s",
        "detailed": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "structured": "%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s",
    }

    log_format = formats.get(Config.LOG_FORMAT, formats["detailed"])

    # Configure logging
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": log_format, "datefmt": "%Y-%m-%d %H:%M:%S"},
            "access": {"format": "%(asctime)s - ACCESS - %(message)s", "datefmt": "%Y-%m-%d %H:%M:%S"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": sys.stdout,
            }
        },
        "loggers": {
            "src": {"level": log_level, "handlers": ["console"], "propagate": False},
            "fastapi": {"level": "INFO", "handlers": ["console"], "propagate": False},
            "uvicorn": {"level": "INFO", "handlers": ["console"], "propagate": False},
            "uvicorn.access": {"level": "INFO", "handlers": ["console"], "propagate": False, "formatter": "access"},
        },
        "root": {"level": log_level, "handlers": ["console"]},
    }

    # Add file handler if LOG_FILE is specified
    if Config.LOG_FILE:
        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "default",
            "filename": Config.LOG_FILE,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }

        # Add file handler to all loggers
        loggers_config = cast(Dict[str, Dict[str, Any]], logging_config["loggers"])
        for logger_config in loggers_config.values():
            if "handlers" in logger_config:
                logger_config["handlers"].append("file")
        root_config = cast(Dict[str, Any], logging_config["root"])
        if "handlers" in root_config:
            root_config["handlers"].append("file")

    # Apply logging configuration
    logging.config.dictConfig(logging_config)

    # Log configuration status
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {Config.LOG_LEVEL}, Format: {Config.LOG_FORMAT}")

    # Validate and log configuration status
    config_validation = Config.validate_required_config()
    if not config_validation["is_valid"]:
        logger.error(f"Missing required configuration: {config_validation['missing_configs']}")

    for warning in config_validation["warnings"]:
        logger.warning(warning)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Initialize logging when module is imported
setup_logging()

# Global configuration instance
config = Config()

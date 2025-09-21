from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import Config, get_logger
from src.routers import admin, whatsapp
from src.utils.error_handlers import get_error_handlers
from src.utils.middleware import setup_middleware

# Initialize logger
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.

    Handles application initialization, configuration validation,
    and cleanup operations.
    """
    # Startup
    logger.info("Starting SIH Health Chatbot Backend...")

    # Validate configuration
    config_validation = Config.validate_required_config()
    if not config_validation["is_valid"]:
        logger.error(f"Configuration validation failed: {config_validation['missing_configs']}")
        logger.error("Application may not function properly without required configuration")
    else:
        logger.info("Configuration validation passed")

    # Log configuration warnings
    for warning in config_validation["warnings"]:
        logger.warning(f"Configuration warning: {warning}")

    logger.info("Application startup completed successfully")

    yield

    # Shutdown
    logger.info("Shutting down SIH Health Chatbot Backend...")
    logger.info("Application shutdown completed")


# Create FastAPI application with comprehensive configuration
app = FastAPI(
    title="SIH Health Chatbot Backend",
    description="AI-driven public health chatbot system for SIH 2025 (Problem ID: 25049)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if Config.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if Config.ENVIRONMENT != "production" else None,
)

# Setup comprehensive middleware
setup_middleware(app)

# Register error handlers
error_handlers = get_error_handlers()
for exception_type, handler in error_handlers.items():
    app.add_exception_handler(exception_type, handler)

# Include routers
app.include_router(whatsapp.router)
app.include_router(admin.router)


@app.get("/ping")
async def ping():
    """
    Health check endpoint for monitoring application status.

    Returns:
        Dict containing application status and configuration info
    """
    logger.debug("Health check requested")

    config_validation = Config.validate_required_config()

    return {
        "status": "ok",
        "message": "Backend is running 🚀",
        "environment": Config.ENVIRONMENT,
        "configuration_valid": config_validation["is_valid"],
        "warnings": config_validation["warnings"] if config_validation["warnings"] else None,
    }


@app.get("/health")
async def health_check():
    """
    Detailed health check endpoint for comprehensive monitoring.

    Returns:
        Dict containing detailed application health information
    """
    logger.debug("Detailed health check requested")

    try:
        # Check configuration
        config_validation = Config.validate_required_config()

        # Check services (basic validation)
        services_status = {
            "user_service": "ok",
            "message_service": "ok",
            "whatsapp_api": "ok" if Config.WHATSAPP_ACCESS_TOKEN else "not_configured",
        }

        # Overall health status
        overall_status = "healthy" if config_validation["is_valid"] else "degraded"

        health_info = {
            "status": overall_status,
            "timestamp": None,  # Will be set by logging system
            "environment": Config.ENVIRONMENT,
            "configuration": {
                "valid": config_validation["is_valid"],
                "missing_configs": config_validation["missing_configs"],
                "warnings": config_validation["warnings"],
            },
            "services": services_status,
        }

        logger.info(f"Health check completed - Status: {overall_status}")
        return health_info

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": "Health check failed", "timestamp": None}

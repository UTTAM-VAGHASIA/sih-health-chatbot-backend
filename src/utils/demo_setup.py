#!/usr/bin/env python3
"""
Demo Setup Script for WhatsApp Demo Bot.

This script provides utilities for setting up and managing the demo environment
for judge evaluation and presentations. It includes functions for creating
test data, resetting the environment, and generating demo scenarios.
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.config import get_logger
from src.services.user_service import UserService
from src.utils.demo_utils import DemoDataGenerator, DemoMetrics

logger = get_logger(__name__)


class DemoSetup:
    """Main demo setup and management class."""

    def __init__(self):
        """Initialize demo setup with configuration."""
        self.demo_generator = DemoDataGenerator()
        self.demo_metrics = DemoMetrics()

    def setup_complete_demo(self) -> Dict[str, Any]:
        """
        Setup complete demo environment with all necessary data.

        Returns:
            Dictionary with setup results and instructions
        """
        logger.info("Starting complete demo environment setup...")

        try:
            # Clear existing data
            self.demo_generator.clear_demo_data()
            logger.info("Cleared existing demo data")

            # Create demo users
            demo_users = self.demo_generator.create_demo_users()
            logger.info(f"Created {len(demo_users)} demo users")

            # Get current metrics
            metrics = self.demo_metrics.get_demo_performance_metrics()
            engagement = self.demo_metrics.get_user_engagement_stats()

            # Prepare judge instructions
            judge_instructions = self._generate_judge_instructions(demo_users)

            setup_result = {
                "success": True,
                "setup_timestamp": datetime.now().isoformat(),
                "demo_users_created": len(demo_users),
                "demo_phone_numbers": [user.phone_number for user in demo_users[:5]],  # First 5 for testing
                "performance_metrics": metrics,
                "engagement_stats": engagement,
                "judge_instructions": judge_instructions,
                "demo_commands": self._get_demo_commands(),
                "admin_endpoints": self._get_admin_endpoints(),
            }

            logger.info("Complete demo environment setup successful")
            return setup_result

        except Exception as e:
            logger.error(f"Demo setup failed: {str(e)}")
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _generate_judge_instructions(self, demo_users: List) -> Dict[str, Any]:
        """
        Generate comprehensive instructions for judges.

        Args:
            demo_users: List of created demo users

        Returns:
            Dictionary with judge instructions
        """
        return {
            "overview": "This is a live WhatsApp integration demo for SIH 2025 Problem ID 25049",
            "test_phone_numbers": [user.phone_number for user in demo_users[:3]],
            "test_scenarios": [
                {
                    "scenario": "Basic Chat Interaction",
                    "steps": [
                        "Send 'hello' to see welcome message",
                        "Send 'demo' to see live features",
                        "Send 'judges' for evaluation guide",
                    ],
                },
                {
                    "scenario": "Health Information",
                    "steps": [
                        "Send 'health' to see health capabilities",
                        "Send 'vaccination' for vaccination info",
                        "Send 'help' for available commands",
                    ],
                },
                {
                    "scenario": "Technical Details",
                    "steps": [
                        "Send 'architecture' for technical details",
                        "Send 'features' for capability overview",
                        "Send 'sih' for project information",
                    ],
                },
                {
                    "scenario": "Admin Broadcast System",
                    "steps": [
                        "Use POST /admin/alerts to send alerts",
                        "Check /admin/stats for user statistics",
                        "Use /admin/demo/broadcast for quick demo",
                    ],
                },
            ],
            "evaluation_points": [
                "Real-time WhatsApp message processing",
                "Automatic user registration on first message",
                "Intelligent response generation",
                "Admin alert broadcasting to all users",
                "Comprehensive logging and monitoring",
                "Scalable architecture design",
            ],
        }

    def _get_demo_commands(self) -> List[Dict[str, str]]:
        """
        Get list of demo commands for testing.

        Returns:
            List of command dictionaries
        """
        return [
            {"command": "hello", "description": "Welcome message and auto-registration"},
            {"command": "demo", "description": "Show live demo features"},
            {"command": "judges", "description": "Evaluation guide for judges"},
            {"command": "health", "description": "Health assistant capabilities"},
            {"command": "architecture", "description": "Technical system details"},
            {"command": "features", "description": "Complete feature overview"},
            {"command": "broadcast", "description": "Admin broadcast system info"},
            {"command": "sih", "description": "SIH 2025 project details"},
            {"command": "help", "description": "Available commands and help"},
        ]

    def _get_admin_endpoints(self) -> List[Dict[str, str]]:
        """
        Get list of admin API endpoints for testing.

        Returns:
            List of endpoint dictionaries
        """
        return [
            {
                "endpoint": "POST /admin/alerts",
                "description": "Broadcast alert to all users",
                "example": '{"message": "Demo alert message", "priority": "high"}',
            },
            {
                "endpoint": "GET /admin/stats",
                "description": "Get comprehensive admin statistics",
                "example": "No body required",
            },
            {
                "endpoint": "GET /admin/users",
                "description": "Get list of registered users (anonymized)",
                "example": "No body required",
            },
            {
                "endpoint": "POST /admin/demo/setup",
                "description": "Setup demo environment",
                "example": "No body required",
            },
            {
                "endpoint": "POST /admin/demo/broadcast",
                "description": "Send demo broadcast alert",
                "example": "No body required",
            },
            {
                "endpoint": "GET /admin/demo/metrics",
                "description": "Get comprehensive demo metrics",
                "example": "No body required",
            },
            {
                "endpoint": "DELETE /admin/demo/reset",
                "description": "Reset demo data for fresh start",
                "example": "No body required",
            },
        ]

    def generate_demo_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive demo report for evaluation.

        Returns:
            Dictionary with complete demo report
        """
        try:
            logger.info("Generating comprehensive demo report...")

            # Get current statistics
            total_users = UserService.get_user_count()
            active_users = UserService.get_active_user_count()
            performance_metrics = self.demo_metrics.get_demo_performance_metrics()
            engagement_stats = self.demo_metrics.get_user_engagement_stats()

            # Generate report
            report = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "report_type": "demo_evaluation",
                    "sih_problem_id": "25049",
                    "client": "Government of Odisha (Electronics & IT Department)",
                },
                "system_overview": {
                    "project_name": "SIH Health Chatbot Backend",
                    "description": "AI-driven public health chatbot system",
                    "technology_stack": {
                        "backend": "FastAPI (Python 3.13)",
                        "integration": "WhatsApp Cloud API",
                        "architecture": "Layered (API → Services → Data)",
                        "deployment": "Docker + Cloudflare Tunnel",
                        "monitoring": "Comprehensive logging & metrics",
                    },
                },
                "current_statistics": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "performance_metrics": performance_metrics,
                    "engagement_statistics": engagement_stats,
                },
                "features_demonstrated": [
                    "Real-time WhatsApp message processing",
                    "Automatic user registration on first message",
                    "Intelligent health-focused chat responses",
                    "Admin alert broadcasting system",
                    "Comprehensive logging and monitoring",
                    "Judge-friendly demo responses",
                    "Scalable architecture design",
                    "Error handling and fallback responses",
                ],
                "demo_capabilities": {
                    "messaging": "Bi-directional WhatsApp communication",
                    "user_management": "Auto-registration and activity tracking",
                    "admin_features": "Alert broadcasting and user statistics",
                    "monitoring": "Real-time logging and performance metrics",
                    "scalability": "Production-ready architecture",
                },
                "evaluation_notes": {
                    "live_demo": "All features working in real-time",
                    "test_data": "Demo users and scenarios available",
                    "admin_access": "Full admin API available for testing",
                    "source_code": "Complete implementation available",
                    "documentation": "Comprehensive technical documentation",
                },
            }

            logger.info("Demo report generated successfully")
            return report

        except Exception as e:
            logger.error(f"Failed to generate demo report: {str(e)}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def export_demo_data(self, filename: Optional[str] = None) -> str:
        """
        Export demo data to JSON file for backup or analysis.

        Args:
            filename: Optional filename for export

        Returns:
            Filename of exported data
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"demo_data_export_{timestamp}.json"

        try:
            # Generate comprehensive demo report
            demo_data = self.generate_demo_report()

            # Add raw data
            from src.db.models import messages_db, users_db

            demo_data["raw_data"] = {
                "users": [
                    {
                        "phone_number": user.phone_number,
                        "first_seen": user.first_seen.isoformat(),
                        "last_activity": user.last_activity.isoformat(),
                        "message_count": user.message_count,
                        "is_active": user.is_active,
                    }
                    for user in users_db.values()
                ],
                "messages": [
                    {
                        "id": msg.id,
                        "from_user": msg.from_user,
                        "content": msg.content[:100],  # Truncate for privacy
                        "timestamp": msg.timestamp.isoformat(),
                        "message_type": msg.message_type,
                    }
                    for msg in messages_db
                ],
            }

            # Write to file
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(demo_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Demo data exported to {filename}")
            return filename

        except Exception as e:
            logger.error(f"Failed to export demo data: {str(e)}")
            raise


def main():
    """Main function for running demo setup from command line."""
    if len(sys.argv) < 2:
        print("Usage: python demo_setup.py <command>")
        print("Commands:")
        print("  setup    - Setup complete demo environment")
        print("  report   - Generate demo report")
        print("  export   - Export demo data to JSON")
        print("  reset    - Reset demo data")
        return

    command = sys.argv[1].lower()
    demo_setup = DemoSetup()

    if command == "setup":
        print("Setting up demo environment...")
        result = demo_setup.setup_complete_demo()
        print(json.dumps(result, indent=2))

    elif command == "report":
        print("Generating demo report...")
        report = demo_setup.generate_demo_report()
        print(json.dumps(report, indent=2))

    elif command == "export":
        print("Exporting demo data...")
        filename = demo_setup.export_demo_data()
        print(f"Demo data exported to: {filename}")

    elif command == "reset":
        print("Resetting demo data...")
        demo_setup.demo_generator.clear_demo_data()
        print("Demo data reset complete")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()

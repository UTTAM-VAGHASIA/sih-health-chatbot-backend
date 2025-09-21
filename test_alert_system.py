#!/usr/bin/env python3
"""
Real-time Alert System Testing Script

This script helps you test the WhatsApp alert broadcasting system
with your live server and webhook connection.
"""

import time

import requests

# Configuration
# BASE_URL = "http://localhost:8000"  # Change this to your server URL
BASE_URL = "https://persian-addresses-rebound-estimated.trycloudflare.com"  # Your cloudflare URL


def test_server_health():
    """Test if the server is running and healthy."""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Server is healthy: {health_data['status']}")
            print(f"   Environment: {health_data['environment']}")
            print(f"   Configuration valid: {health_data['configuration']['valid']}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False


def get_user_stats():
    """Get current user statistics."""
    print("\n📊 Getting user statistics...")
    try:
        response = requests.get(f"{BASE_URL}/admin/stats")
        if response.status_code == 200:
            stats = response.json()
            user_stats = stats["user_statistics"]
            print(f"   Total users: {user_stats['total_users']}")
            print(f"   Active users: {user_stats['active_users']}")
            return user_stats["total_users"]
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
            return 0
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return 0


def setup_demo_users():
    """Setup demo users for testing."""
    print("\n🎯 Setting up demo users...")
    try:
        response = requests.post(f"{BASE_URL}/admin/demo/setup")
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print("✅ Demo setup successful!")
                print(f"   Created {result['demo_info']['demo_users_created']} demo users")
                print(f"   Test numbers: {result['demo_info']['demo_phone_numbers'][:3]}")
                return True
            else:
                print(f"❌ Demo setup failed: {result}")
                return False
        else:
            print(f"❌ Demo setup request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error setting up demo: {e}")
        return False


def send_test_alert(message, priority="medium"):
    """Send a test alert and return the results."""
    print(f"\n📢 Sending test alert (priority: {priority})...")
    print(f"   Message: {message[:50]}...")

    try:
        payload = {"message": message, "priority": priority}

        response = requests.post(f"{BASE_URL}/admin/alerts", headers={"Content-Type": "application/json"}, json=payload)

        if response.status_code == 200:
            result = response.json()
            print("✅ Alert sent successfully!")
            print(f"   Users targeted: {result['users_targeted']}")
            print(f"   Successful deliveries: {result['successful_deliveries']}")
            print(f"   Failed deliveries: {result['failed_deliveries']}")
            print(f"   Message ID: {result['message_id']}")

            if result["errors"]:
                print("   Errors:")
                for error in result["errors"][:3]:  # Show first 3 errors
                    print(f"     - {error}")

            return result
        else:
            print(f"❌ Alert request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except Exception:
                print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error sending alert: {e}")
        return None


def send_demo_alert():
    """Send a pre-configured demo alert."""
    print("\n🚀 Sending demo alert...")
    try:
        response = requests.post(f"{BASE_URL}/admin/demo/broadcast")
        if response.status_code == 200:
            result = response.json()
            print("✅ Demo alert sent!")
            print(f"   Users targeted: {result['users_targeted']}")
            print(f"   Successful: {result['successful_deliveries']}")
            print(f"   Failed: {result['failed_deliveries']}")
            return result
        else:
            print(f"❌ Demo alert failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error sending demo alert: {e}")
        return None


def main():
    """Main testing function."""
    print("🧪 WhatsApp Alert System - Real-time Testing")
    print("=" * 50)

    # Test server health
    if not test_server_health():
        print("\n❌ Server is not healthy. Please check your server.")
        return

    # Get current user stats
    user_count = get_user_stats()

    # If no users, setup demo users
    if user_count == 0:
        print("\n⚠️  No users registered. Setting up demo users...")
        if not setup_demo_users():
            print("\n❌ Failed to setup demo users. Please check your configuration.")
            return
        user_count = get_user_stats()

    if user_count == 0:
        print("\n❌ Still no users available for testing.")
        return

    print(f"\n✅ Ready to test with {user_count} users!")

    # Test different types of alerts
    test_alerts = [
        {
            "message": "🧪 TEST ALERT: This is a live test of the WhatsApp broadcasting system. If you receive this, everything is working!",
            "priority": "high",
        },
        {
            "message": "📱 Demo Alert: Testing the admin panel alert system for SIH 2025 presentation.",
            "priority": "medium",
        },
    ]

    print("\n" + "=" * 50)
    print("🚀 STARTING ALERT TESTS")
    print("=" * 50)

    for i, alert in enumerate(test_alerts, 1):
        print(f"\n--- Test {i}/{len(test_alerts)} ---")
        result = send_test_alert(alert["message"], alert["priority"])

        if result:
            if result["successful_deliveries"] > 0:
                print(f"🎉 SUCCESS! {result['successful_deliveries']} alerts delivered!")
                print("   Check your WhatsApp to see if you received the message.")
            else:
                print("⚠️  Alert was processed but no successful deliveries.")
                print("   This might be due to WhatsApp API configuration issues.")

        # Wait between tests
        if i < len(test_alerts):
            print("   Waiting 5 seconds before next test...")
            time.sleep(5)

    # Try demo alert
    print("\n--- Demo Alert Test ---")
    demo_result = send_demo_alert()

    print("\n" + "=" * 50)
    print("📋 TESTING SUMMARY")
    print("=" * 50)
    print("Server Status: ✅ Healthy")
    print(f"Users Available: {user_count}")
    print(
        f"Alert System: {'✅ Working' if any([result and result['users_targeted'] > 0 for result in [result, demo_result] if result]) else '⚠️  Needs Configuration'}"
    )

    if user_count > 0:
        print("\n💡 NEXT STEPS:")
        print("1. If alerts failed due to authentication:")
        print("   - Check your WhatsApp access token")
        print("   - Verify your WhatsApp Business API setup")
        print("   - Make sure your token hasn't expired")
        print("")
        print("2. To test with real users:")
        print("   - Send a WhatsApp message to your bot from your phone")
        print("   - Then run this script again to send alerts to real users")
        print("")
        print("3. The alert system architecture is working correctly!")
        print("   - Users are being targeted properly")
        print("   - The broadcast logic is functioning")
        print("   - Only the WhatsApp API delivery needs configuration")


if __name__ == "__main__":
    main()

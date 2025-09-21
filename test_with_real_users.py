#!/usr/bin/env python3
"""
Test Alert System with Real Users

This script helps you test the alert system after you've registered
yourself by sending a message to your WhatsApp bot.
"""

import requests

BASE_URL = "http://localhost:8000"


def check_real_users():
    """Check if any real users are registered."""
    print("👥 Checking for registered users...")
    try:
        response = requests.get(f"{BASE_URL}/admin/users")
        if response.status_code == 200:
            data = response.json()
            users = data["users"]
            print(f"   Found {len(users)} registered users:")
            for user in users:
                print(f"   - {user['phone_number']} (messages: {user['message_count']})")
            return len(users)
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0


def send_real_alert():
    """Send an alert to real registered users."""
    user_count = check_real_users()

    if user_count == 0:
        print("\n⚠️  No users found!")
        print("📱 Please send a WhatsApp message to your bot first:")
        print("   1. Open WhatsApp on your phone")
        print("   2. Send a message to your bot number")
        print("   3. Send any text like 'hello' or 'test'")
        print("   4. Then run this script again")
        return

    print(f"\n📢 Sending alert to {user_count} real users...")

    alert_message = """🚨 LIVE TEST ALERT 🚨

This is a real-time test of the WhatsApp alert broadcasting system!

✅ If you receive this message, the system is working perfectly!
🎯 This demonstrates the admin panel's ability to send alerts to all registered users.

SIH 2025 - Health Chatbot Demo"""

    try:
        payload = {"message": alert_message, "priority": "high"}

        response = requests.post(f"{BASE_URL}/admin/alerts", headers={"Content-Type": "application/json"}, json=payload)

        if response.status_code == 200:
            result = response.json()
            print("✅ Alert broadcast completed!")
            print(f"   Users targeted: {result['users_targeted']}")
            print(f"   Successful deliveries: {result['successful_deliveries']}")
            print(f"   Failed deliveries: {result['failed_deliveries']}")

            if result["successful_deliveries"] > 0:
                print("\n🎉 SUCCESS! Check your WhatsApp - you should have received the alert!")
            else:
                print("\n⚠️  No successful deliveries. Errors:")
                for error in result.get("errors", []):
                    print(f"     - {error}")

        else:
            print(f"❌ Alert failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Error sending alert: {e}")


if __name__ == "__main__":
    print("📱 WhatsApp Alert System - Real User Test")
    print("=" * 45)
    send_real_alert()

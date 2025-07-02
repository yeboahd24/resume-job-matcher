#!/usr/bin/env python3
"""
Admin script for managing user subscriptions
"""

import requests
import json
import sys
import argparse

API_BASE_URL = "http://localhost:8000"

def login_admin(email: str, password: str):
    """Login as admin and get token"""
    print("🔐 Logging in as admin...")
    
    login_data = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/jwt/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"   ✅ Admin login successful")
            return token_data['access_token']
        else:
            print(f"   ❌ Admin login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def reset_user_usage(token: str, user_id: int):
    """Reset a user's monthly usage"""
    print(f"🔄 Resetting usage for user ID {user_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/subscription/reset-usage",
            json=user_id,
            headers=headers
        )
        
        if response.status_code == 200:
            subscription = response.json()
            print(f"   ✅ Usage reset successfully")
            print(f"   💳 Tier: {subscription['tier']}")
            print(f"   📊 Matches used (reset): {subscription['matches_used']}")
            return True
        else:
            print(f"   ❌ Usage reset failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def get_usage_stats(token: str):
    """Get overall usage statistics"""
    print("📊 Getting usage statistics...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/subscription/usage-stats",
            headers=headers
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Usage statistics retrieved")
            print(f"   👥 Total users: {stats['total_users']}")
            print(f"   📊 Subscription breakdown:")
            for tier, count in stats['subscription_breakdown'].items():
                print(f"      • {tier.capitalize()}: {count} users")
            print(f"   🎯 Monthly job matches: {stats['monthly_job_matches']}")
            print(f"   📈 Average matches per user: {stats['average_matches_per_user']}")
            print(f"   💰 Top tier conversion rate: {stats['top_tier_conversion_rate']}")
            return stats
        else:
            print(f"   ❌ Failed to get usage stats: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    """Main admin interface"""
    parser = argparse.ArgumentParser(description='Admin Subscription Manager')
    parser.add_argument('--admin-email', required=True, help='Admin email')
    parser.add_argument('--admin-password', required=True, help='Admin password')
    parser.add_argument('--action', choices=['reset-usage', 'stats'], required=True, help='Action to perform')
    parser.add_argument('--user-id', type=int, help='User ID (required for reset-usage)')
    
    args = parser.parse_args()
    
    print("🛠️ Admin Subscription Manager")
    print("=" * 50)
    
    # Login as admin
    token = login_admin(args.admin_email, args.admin_password)
    if not token:
        print("❌ Admin login failed, stopping")
        sys.exit(1)
    
    print()
    
    if args.action == 'reset-usage':
        if not args.user_id:
            print("❌ User ID is required for reset-usage action")
            sys.exit(1)
        
        success = reset_user_usage(token, args.user_id)
        if success:
            print("✅ User usage reset successfully!")
        else:
            print("❌ Failed to reset user usage")
    
    elif args.action == 'stats':
        stats = get_usage_stats(token)
        if stats:
            print("✅ Usage statistics retrieved successfully!")
        else:
            print("❌ Failed to get usage statistics")
    
    print()
    print("=" * 50)
    print("🎉 Admin operation complete!")

if __name__ == "__main__":
    main()
# Subscription System Guide

This guide explains how to use and manage the subscription system in the Resume Job Matcher API.

## Overview

The subscription system provides different tiers of service with varying limits and features:

- **Free**: 5 matches per month, basic features
- **Student**: 15 matches per month, student discount, career resources
- **Pro**: Unlimited matches, priority processing, advanced features
- **Enterprise**: All Pro features plus API access and dedicated support

## API Endpoints

### Get Subscription Information
```http
GET /api/v1/auth/me/subscription
Authorization: Bearer <token>
```

Returns detailed subscription information including:
- Current tier
- Monthly usage limits
- Matches used/remaining
- Available features
- Next reset date
- Available upgrade options
- Pricing information

### Upgrade Subscription
```http
POST /api/v1/subscription/upgrade
Authorization: Bearer <token>
Content-Type: application/json

"pro"
```

Upgrades the user's subscription to a higher tier. Note: This is a simplified implementation without payment processing.

### Reset Usage (Admin Only)
```http
POST /api/v1/subscription/reset-usage
Authorization: Bearer <admin-token>
Content-Type: application/json

123
```

Resets a user's monthly usage counter. Requires admin privileges.

### Get Usage Statistics (Admin Only)
```http
GET /api/v1/subscription/usage-stats
Authorization: Bearer <admin-token>
```

Returns aggregate usage statistics across all users and subscription tiers.

## Usage Limits

The system automatically tracks and enforces usage limits:

1. **Free Tier**: 5 job matches per month
2. **Student Tier**: 15 job matches per month
3. **Pro/Enterprise**: Unlimited matches

When a user reaches their limit, they receive a `402 Payment Required` response with instructions to upgrade.

## Monthly Reset

Usage counters automatically reset every 30 days from the last reset date. The system checks for reset eligibility:
- When getting subscription information
- When attempting to use job matching services

## Testing the Subscription System

### 1. Using the Test Script
```bash
python test_subscription_system.py
```

This script will:
- Register a test user
- Test subscription information retrieval
- Test job matching with limits
- Test subscription upgrades
- Verify all functionality

### 2. Using the Web Interface
Open `subscription_test.html` in your browser to:
- Login with your account
- View current subscription details
- See available upgrade options
- Test usage limits with file uploads
- Upgrade your subscription

### 3. Admin Management
```bash
python admin_subscription_manager.py \
  --admin-email admin@example.com \
  --admin-password adminpassword \
  --action stats

python admin_subscription_manager.py \
  --admin-email admin@example.com \
  --admin-password adminpassword \
  --action reset-usage \
  --user-id 123
```

## Implementation Details

### Database Schema
The subscription system uses the existing `users` table with these fields:
- `subscription_tier`: Current subscription level
- `monthly_matches_used`: Number of matches used this month
- `last_match_reset`: Date of last usage reset

### Subscription Tiers
Defined in `app/models/user.py` as an enum:
```python
class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    STUDENT = "student"
```

### Usage Enforcement
Implemented in `app/api/endpoints/jobs.py` in the job matching endpoint:
- Checks current usage against tier limits
- Automatically resets counters when appropriate
- Increments usage on successful matches
- Returns appropriate error messages when limits are exceeded

## Future Enhancements

### Payment Integration
To make this production-ready, integrate with a payment provider:

1. **Stripe Integration**:
   ```python
   import stripe
   
   # Create subscription
   subscription = stripe.Subscription.create(
       customer=customer_id,
       items=[{'price': price_id}],
   )
   ```

2. **Webhook Handling**:
   - Handle successful payments
   - Process subscription cancellations
   - Manage failed payments

### Advanced Features
- **Billing Cycles**: Proper monthly/annual billing
- **Prorations**: Handle mid-cycle upgrades/downgrades
- **Usage Analytics**: Detailed usage tracking and reporting
- **Subscription Pausing**: Temporary subscription suspension
- **Team Subscriptions**: Multi-user enterprise accounts

### Database Migrations
For production deployment, create proper database migrations:

```sql
-- Add subscription-related columns if not exists
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(20) DEFAULT 'free';
ALTER TABLE users ADD COLUMN IF NOT EXISTS monthly_matches_used INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_match_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create subscriptions table for advanced billing
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    stripe_subscription_id VARCHAR(255),
    status VARCHAR(50),
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Security Considerations

1. **Authorization**: All subscription endpoints require authentication
2. **Admin Privileges**: Admin-only endpoints check for superuser status
3. **Input Validation**: All inputs are validated before processing
4. **Rate Limiting**: Consider adding rate limiting to prevent abuse

## Monitoring and Alerts

Set up monitoring for:
- Subscription upgrade/downgrade events
- Usage limit violations
- Failed payment attempts (when payment is integrated)
- Unusual usage patterns

## Support and Troubleshooting

### Common Issues

1. **Usage Not Resetting**: Check `last_match_reset` date and ensure 30 days have passed
2. **Upgrade Failures**: Verify user has permission to upgrade to the target tier
3. **Admin Access Denied**: Ensure the user has `is_superuser=True`

### Debug Commands
```bash
# Check user subscription status
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/auth/me/subscription

# Test job matching limits
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -F "file=@test_resume.txt" \
     http://localhost:8000/api/v1/jobs/match
```

This subscription system provides a solid foundation for monetizing your Resume Job Matcher service while maintaining a great user experience.
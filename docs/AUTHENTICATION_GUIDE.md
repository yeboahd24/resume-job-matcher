# 🔐 Authentication System Guide

## Overview

The Resume Job Matcher now includes a comprehensive authentication system that enables:

- 👤 **User Registration & Login**
- 🔑 **JWT Token Authentication**
- 👥 **User Profiles**
- 💳 **Subscription Tiers**
- 📊 **Usage Tracking**
- 📝 **Job Match History**

## 🚀 Getting Started

### Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**:
   ```bash
   python setup_auth.py
   ```

3. **Create Admin User**:
   ```bash
   python create_admin_user.py
   ```

4. **Start the API Server**:
   ```bash
   python main.py
   ```

5. **Test Authentication**:
   ```bash
   python test_auth_system.py
   ```

### Web Interface

Open `auth_test.html` in your browser to test the authentication system with a simple web interface.

## 📚 API Documentation

### Authentication Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/v1/auth/register` | POST | Register a new user | None |
| `/api/v1/auth/jwt/login` | POST | Login and get JWT token | None |
| `/api/v1/auth/jwt/logout` | POST | Logout (invalidate token) | JWT |
| `/api/v1/auth/me` | GET | Get current user info | JWT |
| `/api/v1/auth/me/profile` | GET | Get user profile | JWT |
| `/api/v1/auth/me/profile` | POST | Update user profile | JWT |
| `/api/v1/auth/me/subscription` | GET | Get subscription info | JWT |
| `/api/v1/auth/me/job-matches` | GET | Get job match history | JWT |

### Registration

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/jwt/login \
  -d "username=user@example.com&password=password123" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

### Authenticated Requests

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔧 Technical Details

### Database Schema

The authentication system uses SQLAlchemy models:

- **User**: Core user information and authentication
- **UserProfile**: Extended user preferences and settings
- **JobMatch**: History of job matching requests

### Subscription Tiers

- **Free**: 5 job matches per month
- **Pro**: Unlimited job matches
- **Enterprise**: Unlimited job matches + API access
- **Student**: 15 job matches per month

### Security Features

- **Password Hashing**: Secure bcrypt hashing
- **JWT Authentication**: Short-lived access tokens
- **Rate Limiting**: Prevents abuse
- **Input Validation**: Prevents injection attacks

## 🧩 Integration with Job Matching

The job matching system now integrates with authentication:

1. **Usage Tracking**: Counts matches against monthly limits
2. **Job History**: Saves match results to user profile
3. **Personalization**: Uses profile preferences for matching

## 🔄 Workflow

1. User registers an account
2. User logs in and receives JWT token
3. User updates their profile with preferences
4. User uploads resume with authentication
5. System tracks usage and enforces limits
6. User can view their job match history

## 🛠️ Configuration

Authentication settings can be configured in `.env`:

```
# Authentication Settings
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=jwt-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# User Settings
USER_REGISTRATION_ENABLED=true
USER_VERIFICATION_ENABLED=false
RESET_PASSWORD_ENABLED=true
```

## 📱 Frontend Integration

To integrate with a frontend application:

1. **Registration**: POST to `/api/v1/auth/register`
2. **Login**: POST to `/api/v1/auth/jwt/login`
3. **Store Token**: Save JWT token in localStorage or secure cookie
4. **Authenticated Requests**: Include token in Authorization header
5. **Profile Management**: GET/POST to `/api/v1/auth/me/profile`

## 🔜 Coming Soon

- Email verification
- Password reset
- Social login (Google, GitHub)
- Admin dashboard
- Enhanced subscription management

## 🐞 Troubleshooting

### Common Issues

- **Database Errors**: Run `python setup_auth.py` to initialize the database
- **Import Errors**: Ensure all dependencies are installed
- **Token Errors**: Check that the token is valid and not expired
- **Permission Errors**: Verify user has appropriate subscription tier

### Debugging

For detailed logs:

```bash
LOG_LEVEL=DEBUG python main.py
```

## 📚 Resources

- [FastAPI Users Documentation](https://fastapi-users.github.io/fastapi-users/)
- [JWT Authentication Guide](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/14/)
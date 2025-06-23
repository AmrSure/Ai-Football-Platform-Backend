# Authentication System Changes

## Overview
The AI Football Platform now uses **email-based authentication** instead of username-based authentication. This change simplifies the user experience and aligns with modern authentication practices.

## Key Changes

### 1. User Model Updates
- **Removed**: `username` field
- **Updated**: `email` field is now unique and required
- **Added**: Custom user manager for email-based user creation
- **Set**: `USERNAME_FIELD = 'email'`

### 2. Authentication Backend
- **Added**: Custom `EmailBackend` in `apps.core.authentication`
- **Features**: Case-insensitive email lookup
- **Configured**: In Django settings as primary authentication backend

### 3. API Changes
All authentication endpoints now use email instead of username:

#### Login Endpoint: `POST /auth/login/`
```json
{
  "username": "user@example.com",  // Actually email, but field name remains for JWT compatibility
  "password": "your_password"
}
```

#### Registration Endpoint: `POST /auth/register/`
```json
{
  "email": "user@example.com",
  "password": "your_password",
  "password_confirm": "your_password",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "external_client"
}
```

### 4. Admin Interface Updates
- Search fields updated to use email instead of username
- User creation forms now use email as primary identifier
- All profile admin interfaces updated

### 5. JWT Token Updates
- JWT tokens now include email instead of username
- Token claims updated for consistency

## Migration Guide

### For Developers
1. Update any hardcoded references to `username` field
2. Use `email` field for user lookups
3. Update forms and serializers to use email

### For API Clients
1. Use email address in login requests
2. Update user registration to include email as primary field
3. Expect email in JWT token responses instead of username

### Creating Users

#### Management Command
```bash
# Create a test user
python manage.py create_test_user --email admin@example.com --password admin123 --superuser

# Create regular user
python manage.py create_test_user --email user@example.com --user-type external_client
```

#### Programmatically
```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Create regular user
user = User.objects.create_user(
    email='user@example.com',
    password='password123',
    first_name='John',
    last_name='Doe',
    user_type='external_client'
)

# Create superuser
admin = User.objects.create_superuser(
    email='admin@example.com',
    password='admin123',
    first_name='Admin',
    last_name='User'
)
```

## Benefits

1. **Simplified UX**: Users only need to remember their email
2. **Industry Standard**: Email authentication is widely adopted
3. **Unique Identification**: Email naturally provides unique identification
4. **Consistency**: Aligns with JWT best practices
5. **Security**: Case-insensitive email lookup prevents confusion

## Backward Compatibility

⚠️ **Breaking Change**: This is a breaking change for existing installations.

For existing databases:
1. Create a migration to handle the username to email transition
2. Ensure all existing users have valid email addresses
3. Update any existing API clients to use email for authentication

## Testing

Use the provided management command to create test users:

```bash
# Create superuser for admin access
python manage.py create_test_user --email admin@test.com --password admin123 --superuser

# Create different user types
python manage.py create_test_user --email coach@test.com --user-type coach
python manage.py create_test_user --email player@test.com --user-type player
```

## API Documentation

The OpenAPI/Swagger documentation has been updated to reflect these changes. All user-related endpoints now use email as the primary identifier.

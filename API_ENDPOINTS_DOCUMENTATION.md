# API Endpoints Documentation - Email Authentication Update

## 🔄 Authentication Changes Summary

The AI Football Platform API has been updated to use **email-based authentication** instead of username authentication. This document outlines all the affected endpoints and their new request/response formats.

## 🔐 Authentication Endpoints

### 1. Login (JWT Token Obtain)
**Endpoint**: `POST /api/v1/auth/login/`

**New Request Format**:
```json
{
  "username": "user@example.com",  // ⚠️ Field name is "username" but value is email
  "password": "your_secure_password"
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "email": "user@example.com",           // ✅ Now returns email instead of username
  "user_type": "player",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Key Changes**:
- 🔄 Login field accepts email address
- ✅ Case-insensitive email lookup
- 🚫 Username field removed from response
- ✅ Email field added to response

---

### 2. User Registration (External Client)
**Endpoint**: `POST /api/v1/auth/register/`

**New Request Format**:
```json
{
  "email": "newuser@example.com",        // ✅ Primary identifier
  "password": "secure_password",
  "password_confirm": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "external_client",        // Must be "external_client"
  "phone": "+1234567890"                 // Optional
}
```

**Response**:
```json
{
  "id": 1,
  "email": "newuser@example.com",        // ✅ Email as primary identifier
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "external_client",
  "phone": "+1234567890"
}
```

**Key Changes**:
- 🚫 `username` field removed
- ✅ `email` field is now primary identifier
- ✅ Email validation and uniqueness enforced

---

### 3. Academy User Registration
**Endpoint**: `POST /api/v1/auth/academy/register-user/`
**Permissions**: Academy Admin only

**New Request Format**:
```json
{
  "email": "coach@academy.com",          // ✅ Primary identifier
  "password": "secure_password",
  "first_name": "Jane",
  "last_name": "Smith",
  "user_type": "coach",                  // coach, player, or parent
  "academy_id": 1,
  "phone": "+1234567890"                 // Optional
}
```

**Response**:
```json
{
  "id": 2,
  "email": "coach@academy.com",          // ✅ Email as identifier
  "first_name": "Jane",
  "last_name": "Smith",
  "user_type": "coach",
  "phone": "+1234567890"
}
```

---

### 4. Password Change
**Endpoint**: `PUT /api/v1/auth/change-password/`
**Permissions**: Authenticated users only

**Request Format** (unchanged):
```json
{
  "old_password": "current_password",
  "new_password": "new_secure_password",
  "new_password_confirm": "new_secure_password"
}
```

---

### 5. Profile Management
**Endpoint**: `GET/PUT/PATCH /api/v1/auth/profile/`
**Permissions**: Authenticated users only

**Response Format** (updated):
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "email": "user@example.com",         // ✅ Email instead of username
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "user_type": "player"
  },
  "bio": "Professional football player",
  "date_of_birth": "1995-05-15",
  "age": 29
}
```

## 👥 User Management Endpoints

### 1. System Admin - User Management
**Endpoint**: `/api/v1/users/`
**Permissions**: System Admin only

**List Response** (updated):
```json
{
  "count": 50,
  "next": "http://api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "user@example.com",       // ✅ Email field
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "user_type": "player"
    }
  ]
}
```

**Search Parameters** (updated):
- ✅ `search=user@example.com` - Search by email
- ✅ `search=John` - Search by first name
- ✅ `search=Doe` - Search by last name
- 🚫 Username search removed

---

### 2. Academy Admin - User Management
**Endpoint**: `/api/v1/academy-users/`
**Permissions**: Academy Admin only

**Features**:
- List academy users with email-based search
- Create, update, delete users in academy
- Activate/deactivate users
- Reset user passwords

**Search Parameters** (updated):
- ✅ Email-based search: `search=coach@academy.com`
- ✅ Name-based search: `search=John`
- 🚫 Username search removed

## 🔍 Search and Filtering Updates

All user-related endpoints now support:

### Email-based Search
```
GET /api/v1/users/?search=user@example.com
GET /api/v1/academy-users/?search=coach@academy.com
```

### User Type Filtering
```
GET /api/v1/users/?user_type=player
GET /api/v1/academy-users/?user_type=coach
```

### Active Status Filtering
```
GET /api/v1/users/?is_active=true
GET /api/v1/academy-users/?is_active=false
```

## 🛠️ Admin Interface Updates

### Django Admin Changes
- **Login**: Uses email instead of username
- **User Creation**: Email as primary field
- **Search**: Email, first name, last name
- **Display**: Shows email in list views

### User Profile Admin
All profile admin interfaces updated:
- ✅ Search by `user__email`
- ✅ Search by `user__first_name`
- ✅ Search by `user__last_name`
- 🚫 `user__username` search removed

## 📊 Response Schema Updates

### User Object Schema
**Before**:
```json
{
  "id": 1,
  "username": "johndoe",               // 🚫 Removed
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "player"
}
```

**After**:
```json
{
  "id": 1,
  "email": "user@example.com",         // ✅ Primary identifier
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",             // ✅ Computed field
  "user_type": "player"
}
```

### JWT Token Response Schema
**Before**:
```json
{
  "access": "token",
  "refresh": "token",
  "user_id": 1,
  "username": "johndoe",               // 🚫 Removed
  "email": "user@example.com",
  "user_type": "player"
}
```

**After**:
```json
{
  "access": "token",
  "refresh": "token",
  "user_id": 1,
  "email": "user@example.com",         // ✅ Primary identifier
  "user_type": "player",
  "first_name": "John",               // ✅ Added
  "last_name": "Doe"                  // ✅ Added
}
```

## 🔧 Development & Testing

### Management Command
Create test users with email authentication:

```bash
# Create superuser
python manage.py create_test_user \
  --email admin@test.com \
  --password admin123 \
  --superuser

# Create academy admin
python manage.py create_test_user \
  --email academy@test.com \
  --user-type academy_admin \
  --first-name Academy \
  --last-name Admin

# Create player
python manage.py create_test_user \
  --email player@test.com \
  --user-type player \
  --first-name John \
  --last-name Player
```

### Testing Login
```bash
# Test login with email
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@test.com",
    "password": "admin123"
  }'
```

### Testing Registration
```bash
# Test external client registration
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@test.com",
    "password": "secure123",
    "password_confirm": "secure123",
    "first_name": "New",
    "last_name": "User",
    "user_type": "external_client"
  }'
```

## ⚠️ Breaking Changes Summary

1. **Login Field**: Use email address in `username` field for JWT compatibility
2. **User Responses**: No more `username` field, `email` is primary identifier
3. **Search Parameters**: All username-based searches replaced with email
4. **Admin Interface**: Email-based login and search
5. **Database Schema**: Username field removed, email field is unique

## 🔄 Migration Notes

For existing API clients:
1. Update login requests to use email addresses
2. Update user creation requests to use email field
3. Update search queries from username to email
4. Update any hardcoded username references

The API maintains backward compatibility where possible, but clients should migrate to email-based authentication for optimal functionality.

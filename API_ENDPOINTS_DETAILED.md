# AI Football Platform API - Complete Endpoints with Request/Response Examples

## 🚀 Overview

This documentation provides detailed request and response examples for all API endpoints, organized by user type.

### Base URL
```
Development: http://localhost:8000/api/v1/
Production: https://your-domain.com/api/v1/
```

### Authentication
- **Type**: JWT (JSON Web Token)
- **Header**: `Authorization: Bearer <access_token>`
- **Login Field**: Email address (case-insensitive)

---

## 🔐 Shared Authentication Endpoints

### 1. **Login**
```http
POST /api/v1/auth/login/
```

**Request:**
```json
{
  "username": "admin@academy.com",
  "password": "securepassword123"
}
```

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "email": "admin@academy.com",
  "user_type": "academy_admin",
  "first_name": "John",
  "last_name": "Admin",
  "profile": {
    "id": 1,
    "user": {
      "id": 1,
      "email": "admin@academy.com",
      "first_name": "John",
      "last_name": "Admin"
    },
    "position": "Director",
    "bio": "Academy director with 15 years experience",
    "date_of_birth": "1975-05-20",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Error Response (401):**
```json
{
  "detail": "No active account found with the given credentials"
}
```

### 2. **Token Refresh**
```http
POST /api/v1/auth/refresh/
```

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. **Logout**
```http
POST /api/v1/auth/logout/
```

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

### 4. **External Client Registration**
```http
POST /api/v1/auth/register/
```

**Request:**
```json
{
  "email": "client@example.com",
  "password": "secure_password123",
  "password_confirm": "secure_password123",
  "first_name": "John",
  "last_name": "Client",
  "user_type": "external_client",
  "phone": "+1234567890"
}
```

**Success Response (201):**
```json
{
  "id": 5,
  "email": "client@example.com",
  "first_name": "John",
  "last_name": "Client",
  "user_type": "external_client",
  "phone": "+1234567890",
  "is_active": true,
  "date_joined": "2024-01-20T10:00:00Z"
}
```

### 5. **Get User Profile**
```http
GET /api/v1/auth/profile/
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "email": "coach@academy.com",
    "first_name": "Jane",
    "last_name": "Coach",
    "full_name": "Jane Coach",
    "user_type": "coach"
  },
  "bio": "Experienced football coach",
  "date_of_birth": "1985-03-15",
  "age": 39,
  "specialization": "Youth Development",
  "experience_years": 8,
  "certification": "UEFA B License",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 6. **Update User Profile**
```http
PUT /api/v1/auth/profile/
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "bio": "Updated bio text",
  "date_of_birth": "1985-03-15",
  "specialization": "Advanced Tactics"
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "bio": "Updated bio text",
  "date_of_birth": "1985-03-15",
  "specialization": "Advanced Tactics",
  "updated_at": "2024-01-20T10:00:00Z"
}
```

### 7. **Change Password**
```http
PUT /api/v1/auth/change-password/
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "old_password": "current_password",
  "new_password": "new_secure_password",
  "new_password_confirm": "new_secure_password"
}
```

**Success Response (200):**
```json
{
  "message": "Password updated successfully"
}
```

---

## 🔔 Shared Notification Endpoints

### 1. **List User Notifications**
```http
GET /api/v1/notifications/notifications/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `is_read`: true/false
- `notification_type`: match, booking, announcement
- `page`: Page number
- `page_size`: Items per page

**Success Response (200):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Match Scheduled",
      "message": "Your team has a match scheduled for tomorrow at 15:00",
      "notification_type": "match",
      "is_read": false,
      "created_at": "2024-01-20T10:00:00Z",
      "data": {
        "match_id": 5,
        "match_date": "2024-01-21T15:00:00Z"
      }
    }
  ]
}
```

### 2. **Mark Notification as Read**
```http
POST /api/v1/notifications/notifications/{id}/mark_as_read/
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "message": "Notification marked as read",
  "notification_id": 1
}
```

### 3. **Mark All as Read**
```http
POST /api/v1/notifications/notifications/mark_all_as_read/
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "message": "All notifications marked as read",
  "updated_count": 5
}
```

### 4. **Get Unread Count**
```http
GET /api/v1/notifications/notifications/unread_count/
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "unread_count": 3
}
```

### 5. **Notification Statistics**
```http
GET /api/v1/notifications/notifications/statistics/
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "total_notifications": 25,
  "unread_count": 5,
  "read_count": 20,
  "notifications_by_type": {
    "match": 10,
    "booking": 8,
    "announcement": 7
  }
}
```

---

## 🔧 System Admin Endpoints

### Global User Management

#### 1. **List All Users**
```http
GET /api/v1/users/
Authorization: Bearer <system_admin_token>
```

**Query Parameters:**
- `search`: Search by email, first name, or last name
- `user_type`: Filter by user type
- `is_active`: Filter by active status
- `page`: Page number
- `page_size`: Items per page (default: 20)

**Success Response (200):**
```json
{
  "count": 45,
  "next": "http://api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "admin@system.com",
      "first_name": "System",
      "last_name": "Admin",
      "full_name": "System Admin",
      "user_type": "system_admin",
      "is_active": true,
      "date_joined": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-20T10:30:00Z"
    },
    {
      "id": 2,
      "email": "admin@academy.com",
      "first_name": "Academy",
      "last_name": "Admin",
      "full_name": "Academy Admin",
      "user_type": "academy_admin",
      "is_active": true,
      "date_joined": "2024-01-02T00:00:00Z",
      "last_login": "2024-01-20T09:15:00Z"
    }
  ]
}
```

#### 2. **Get User Details**
```http
GET /api/v1/users/{id}/
Authorization: Bearer <system_admin_token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "email": "admin@system.com",
  "first_name": "System",
  "last_name": "Admin",
  "full_name": "System Admin",
  "user_type": "system_admin",
  "is_active": true,
  "date_joined": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-15T10:30:00Z",
  "phone": "+1234567890"
}
```

#### 3. **Update User**
```http
PUT /api/v1/users/{id}/
Authorization: Bearer <system_admin_token>
```

**Request:**
```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "phone": "+1987654321",
  "is_active": true
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "email": "admin@system.com",
  "first_name": "Updated",
  "last_name": "Name",
  "full_name": "Updated Name",
  "phone": "+1987654321",
  "is_active": true,
  "updated_at": "2024-01-20T10:00:00Z"
}
```

#### 4. **Delete User**
```http
DELETE /api/v1/users/{id}/
Authorization: Bearer <system_admin_token>
```

**Success Response (204):** No Content

#### 5. **Activate User**
```http
POST /api/v1/users/{id}/activate/
Authorization: Bearer <system_admin_token>
```

**Success Response (200):**
```json
{
  "message": "User activated successfully",
  "user_id": 1,
  "is_active": true
}
```

#### 6. **Deactivate User**
```http
POST /api/v1/users/{id}/deactivate/
Authorization: Bearer <system_admin_token>
```

**Success Response (200):**
```json
{
  "message": "User deactivated successfully",
  "user_id": 1,
  "is_active": false
}
```

### Academy Management

#### 1. **List All Academies**
```http
GET /api/v1/academies/
Authorization: Bearer <system_admin_token>
```

**Query Parameters:**
- `search`: Search by name, email, or phone
- `is_active`: Filter by active status
- `page`: Page number
- `page_size`: Items per page

**Success Response (200):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Elite Football Academy",
      "name_ar": "أكاديمية النخبة لكرة القدم",
      "description": "Premier football training academy",
      "logo": "http://api/media/academies/logos/logo.jpg",
      "address": "123 Sports St, City",
      "phone": "+1234567890",
      "email": "info@elite.com",
      "website": "https://elite.com",
      "established_date": "2020-01-01",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "basic_statistics": {
        "total_coaches": 8,
        "total_players": 45,
        "total_teams": 6,
        "total_fields": 3
      }
    }
  ]
}
```

#### 2. **Create Academy**
```http
POST /api/v1/academies/
Authorization: Bearer <system_admin_token>
```

**Request:**
```json
{
  "name": "New Football Academy",
  "name_ar": "أكاديمية كرة القدم الجديدة",
  "description": "A new premier football academy",
  "address": "456 New St, City",
  "phone": "+1987654321",
  "email": "info@newacademy.com",
  "website": "https://newacademy.com",
  "established_date": "2024-01-01"
}
```

**Success Response (201):**
```json
{
  "id": 2,
  "name": "New Football Academy",
  "name_ar": "أكاديمية كرة القدم الجديدة",
  "description": "A new premier football academy",
  "address": "456 New St, City",
  "phone": "+1987654321",
  "email": "info@newacademy.com",
  "website": "https://newacademy.com",
  "established_date": "2024-01-01",
  "is_active": true,
  "created_at": "2024-01-20T10:00:00Z",
  "updated_at": "2024-01-20T10:00:00Z"
}
```

#### 3. **Get Academy Details**
```http
GET /api/v1/academies/{id}/
Authorization: Bearer <system_admin_token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "name": "Elite Football Academy",
  "name_ar": "أكاديمية النخبة لكرة القدم",
  "description": "Premier football training academy",
  "logo": "http://api/media/academies/logos/logo.jpg",
  "address": "123 Sports St, City",
  "phone": "+1234567890",
  "email": "info@elite.com",
  "website": "https://elite.com",
  "established_date": "2020-01-01",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "admins": [
    {
      "id": 1,
      "user": {
        "id": 2,
        "email": "admin@elite.com",
        "first_name": "Academy",
        "last_name": "Admin"
      },
      "position": "Director",
      "bio": "Academy director with 15 years experience"
    }
  ],
  "coaches": [
    {
      "id": 1,
      "user": {
        "id": 3,
        "email": "coach@elite.com",
        "first_name": "John",
        "last_name": "Coach"
      },
      "specialization": "Youth Development",
      "experience_years": 8
    }
  ],
  "players": [
    {
      "id": 1,
      "user": {
        "id": 4,
        "email": "player@elite.com",
        "first_name": "Ahmed",
        "last_name": "Player"
      },
      "jersey_number": 10,
      "position": "Midfielder"
    }
  ],
  "teams": [
    {
      "id": 1,
      "name": "U-17 Team",
      "age_group": "U-17",
      "formation": "4-4-2",
      "total_players": 18
    }
  ],
  "fields": [
    {
      "id": 1,
      "name": "Main Field",
      "field_type": "football",
      "capacity": 500,
      "hourly_rate": "150.00"
    }
  ],
  "statistics": {
    "total_admins": 1,
    "total_coaches": 8,
    "total_players": 45,
    "total_parents": 35,
    "total_teams": 6,
    "total_fields": 3
  }
}
```

#### 4. **Update Academy**
```http
PUT /api/v1/academies/{id}/
Authorization: Bearer <system_admin_token>
```

**Request:**
```json
{
  "name": "Updated Academy Name",
  "description": "Updated description",
  "phone": "+1111111111",
  "is_active": true
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "name": "Updated Academy Name",
  "description": "Updated description",
  "phone": "+1111111111",
  "is_active": true,
  "updated_at": "2024-01-20T10:00:00Z"
}
```

#### 5. **Delete Academy**
```http
DELETE /api/v1/academies/{id}/
Authorization: Bearer <system_admin_token>
```

**Success Response (204):** No Content

#### 6. **Academy Statistics**
```http
GET /api/v1/academies/{id}/statistics/
Authorization: Bearer <system_admin_token>
```

**Success Response (200):**
```json
{
  "total_coaches": 8,
  "total_players": 45,
  "total_parents": 35,
  "total_teams": 6,
  "total_fields": 3,
  "active_bookings": 12,
  "completed_matches": 25,
  "upcoming_matches": 5,
  "monthly_revenue": "15000.00"
}
```

### Global Player/Coach/Parent Management

#### 1. **List All Players**
```http
GET /api/v1/players/playerprofile/
Authorization: Bearer <system_admin_token>
```

**Success Response (200):**
```json
{
  "count": 45,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 4,
        "email": "player@elite.com",
        "first_name": "Ahmed",
        "last_name": "Player",
        "user_type": "player"
      },
      "academy": 1,
      "academy_name": "Elite Football Academy",
      "jersey_number": 10,
      "position": "Midfielder",
      "height": "175.50",
      "weight": "68.00",
      "dominant_foot": "right",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### 2. **List All Coaches**
```http
GET /api/v1/players/coachprofile/
Authorization: Bearer <system_admin_token>
```

**Success Response (200):**
```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 3,
        "email": "coach@elite.com",
        "first_name": "John",
        "last_name": "Coach",
        "user_type": "coach"
      },
      "academy": 1,
      "academy_name": "Elite Football Academy",
      "specialization": "Youth Development",
      "experience_years": 8,
      "certification": "UEFA B License",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### 3. **List All Parents**
```http
GET /api/v1/players/parentprofile/
Authorization: Bearer <system_admin_token>
```

**Success Response (200):**
```json
{
  "count": 35,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 5,
        "email": "parent@elite.com",
        "first_name": "Father",
        "last_name": "Player",
        "user_type": "parent"
      },
      "relationship": "father",
      "bio": "Supportive parent",
      "is_active": true,
      "children_count": 1,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### 4. **List All Teams**
```http
GET /api/v1/players/team/
Authorization: Bearer <system_admin_token>
```

**Success Response (200):**
```json
{
  "count": 6,
  "results": [
    {
      "id": 1,
      "name": "U-17 Team",
      "academy": 1,
      "academy_name": "Elite Football Academy",
      "coach": 1,
      "category": "U-17",
      "formation": "4-4-2",
      "is_active": true,
      "total_players": 18,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

*This is the first part of the comprehensive documentation. Continue reading for Academy Admin, Coach, Player, Parent, and External Client endpoints with detailed examples...*

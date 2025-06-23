# AI Football Platform API - Complete Endpoints Documentation

## 🚀 Overview

The AI Football Platform API provides comprehensive endpoints for managing football academies, players, coaches, matches, bookings, analytics, and notifications. All endpoints use **email-based JWT authentication** and support **atomic transactions** for data consistency and reliability.

### ✨ Latest Updates
- **Atomic Transactions**: All write operations wrapped with `@transaction.atomic` for data consistency
- **Advanced Booking System**: Complete field booking system with conflict detection and email notifications
- **Email Automation**: Professional email templates for booking lifecycle management
- **Enhanced Serializers**: Comprehensive serializers for all models with proper validation
- **Nested Data Support**: Academy endpoints return complete nested object hierarchies
- **Conflict Prevention**: Sophisticated booking overlap detection with alternative suggestions
- **Management Commands**: Automated booking reminder system with cron support

## 📋 Table of Contents

1. [Authentication & Setup](#authentication--setup)
2. [Authentication Endpoints](#authentication-endpoints)
3. [User Management](#user-management)
4. [Academy Management](#academy-management)
5. [Player Management](#player-management)
6. [Match Management](#match-management)
7. [Advanced Booking System](#advanced-booking-system)
8. [Analytics & Reporting](#analytics--reporting)
9. [Notifications](#notifications)
10. [Email System](#email-system)
11. [Management Commands](#management-commands)
12. [Error Handling](#error-handling)

---

## 🔐 Authentication & Setup

### Base URL
```
Development: http://localhost:8000/api/v1/
Production: https://your-domain.com/api/v1/
```

### Authentication Method
- **Type**: JWT (JSON Web Token)
- **Header**: `Authorization: Bearer <access_token>`
- **Login Field**: Email address (case-insensitive)

### User Types & Permissions
- **System Admin**: Full system access, can manage all academies
- **Academy Admin**: Manage their academy, register/manage users
- **Coach**: Manage assigned teams, players, matches
- **Player**: View profile, matches, performance data
- **Parent**: View children's profiles and progress
- **External Client**: Book facilities, limited access

---

## 🔐 Authentication Endpoints

### 1. **Login with Profile Information**
```http
POST /api/v1/auth/login/
```

**Request Body:**
```json
{
  "username": "user@example.com",  // Field name is "username" for JWT compatibility
  "password": "your_secure_password"
}
```

**Success Response for Parent User (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "email": "parent@example.com",
  "user_type": "parent",
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "id": 1,
    "user": {
      "id": 1,
      "email": "parent@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "relationship": "father",
    "bio": "Parent bio information",
    "date_of_birth": "1980-01-01",
    "children": [
      {
        "id": 2,
        "user": {
          "id": 2,
          "email": "child@example.com",
          "first_name": "Jane",
          "last_name": "Doe"
        },
        "jersey_number": "10",
        "position": "midfielder"
      }
    ],
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Success Response for Coach User (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 3,
  "email": "coach@academy.com",
  "user_type": "coach",
  "first_name": "Mike",
  "last_name": "Smith",
  "profile": {
    "id": 3,
    "user": {
      "id": 3,
      "email": "coach@academy.com",
      "first_name": "Mike",
      "last_name": "Smith"
    },
    "specialization": "Youth Development",
    "experience_years": 5,
    "certification": "UEFA B License",
    "bio": "Experienced youth coach with focus on skill development",
    "date_of_birth": "1985-03-15",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Profile Serializers by User Type:**
- **parent**: `ParentProfileNestedSerializer` with children information
- **player**: `PlayerProfileNestedSerializer` with parents and teams
- **coach**: `CoachProfileNestedSerializer` with specialization details
- **academy_admin**: `AcademyAdminProfileNestedSerializer`
- **external_client/system_admin**: Basic profile information

**Error Response (401):**
```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### 2. **Token Refresh**
```http
POST /api/v1/auth/refresh/
```

**Request Body:**
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

---

### 3. **Logout**
```http
POST /api/v1/auth/logout/
```

**Request Body:**
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

---

### 4. **External Client Registration**
```http
POST /api/v1/auth/register/
```

**Request Body:**
```json
{
  "email": "client@example.com",
  "password": "secure_password123",
  "password_confirm": "secure_password123",
  "first_name": "John",
  "last_name": "Client",
  "user_type": "external_client",
  "phone": "+1234567890"  // Optional
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
  "phone": "+1234567890"
}
```

---

### 5. **Academy User Registration**
```http
POST /api/v1/auth/academy/register-user/
```
**Permissions**: Academy Admin only

**Request Body:**
```json
{
  "email": "coach@academy.com",
  "password": "secure_password123",
  "first_name": "Jane",
  "last_name": "Coach",
  "user_type": "coach",  // "coach", "player", or "parent"
  "academy_id": 1,
  "phone": "+1234567890"  // Optional
}
```

**Success Response (201):**
```json
{
  "id": 6,
  "email": "coach@academy.com",
  "first_name": "Jane",
  "last_name": "Coach",
  "user_type": "coach",
  "phone": "+1234567890"
}
```

---

### 6. **Get User Profile**
```http
GET /api/v1/auth/profile/
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
  "specialization": "Youth Development",  // For coaches
  "experience_years": 8  // For coaches
}
```

---

### 7. **Update User Profile**
```http
PUT /api/v1/auth/profile/
PATCH /api/v1/auth/profile/
```

**Request Body:**
```json
{
  "bio": "Updated bio text",
  "date_of_birth": "1985-03-15"
}
```

---

### 8. **Change Password**
```http
PUT /api/v1/auth/change-password/
```

**Request Body:**
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

## 👥 User Management

### 1. **List All Users (System Admin)**
```http
GET /api/v1/users/
```
**Permissions**: System Admin only

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
      "date_joined": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 2. **Get User Details (System Admin)**
```http
GET /api/v1/users/{user_id}/
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
  "last_login": "2024-01-15T10:30:00Z"
}
```

---

### 3. **List Academy Users (Academy Admin)**
```http
GET /api/v1/academy-users/
```
**Permissions**: Academy Admin only

**Query Parameters:**
- `search`: Search by email, first name, or last name
- `user_type`: Filter by user type (coach, player, parent)
- `is_active`: Filter by active status

**Success Response (200):**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 5,
      "email": "coach@academy.com",
      "first_name": "Jane",
      "last_name": "Coach",
      "full_name": "Jane Coach",
      "user_type": "coach",
      "is_active": true,
      "date_joined": "2024-01-10T00:00:00Z"
    }
  ]
}
```

---

### 4. **Academy User Actions**
```http
POST /api/v1/academy-users/{user_id}/activate/
POST /api/v1/academy-users/{user_id}/deactivate/
POST /api/v1/academy-users/{user_id}/reset_password/
```

**Activate/Deactivate Success Response (200):**
```json
{
  "message": "User activated successfully"
}
```

**Reset Password Success Response (200):**
```json
{
  "message": "Password reset successfully",
  "new_password": "temp123456"
}
```

---

## 🏟️ Academy Management

### 1. **List Academies**
```http
GET /api/v1/academies/
```

**Query Parameters:**
- `search`: Search by name, email, or phone
- `is_active`: Filter by active status

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

---

### 2. **Get Academy Details with All Nested Objects**
```http
GET /api/v1/academies/{academy_id}/
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
        "last_name": "Admin",
        "full_name": "Academy Admin",
        "user_type": "academy_admin"
      },
      "position": "Director",
      "bio": "Academy director with 15 years experience",
      "date_of_birth": "1975-05-20",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],

  "coaches": [
    {
      "id": 1,
      "user": {
        "id": 3,
        "email": "coach@elite.com",
        "first_name": "John",
        "last_name": "Coach",
        "full_name": "John Coach",
        "user_type": "coach"
      },
      "specialization": "Youth Development",
      "experience_years": 8,
      "certification": "UEFA B License",
      "bio": "Specialist in youth player development",
      "date_of_birth": "1985-08-10",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],

  "players": [
    {
      "id": 1,
      "user": {
        "id": 4,
        "email": "player@elite.com",
        "first_name": "Ahmed",
        "last_name": "Player",
        "full_name": "Ahmed Player",
        "user_type": "player"
      },
      "jersey_number": 10,
      "position": "Midfielder",
      "height": "175.50",
      "weight": "68.00",
      "dominant_foot": "right",
      "bio": "Talented young midfielder",
      "date_of_birth": "2006-03-15",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "parents": [
        {
          "id": 1,
          "user": {
            "id": 5,
            "email": "parent@elite.com",
            "first_name": "Father",
            "last_name": "Player"
          },
          "relationship": "father"
        }
      ],
      "teams": [
        {
          "id": 1,
          "name": "U-17 Team",
          "age_group": "U-17",
          "formation": "4-4-2"
        }
      ]
    }
  ],

  "teams": [
    {
      "id": 1,
      "name": "U-17 Team",
      "age_group": "U-17",
      "formation": "4-4-2",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "total_players": 18,
      "coach": {
        "id": 1,
        "user": {
          "id": 3,
          "email": "coach@elite.com",
          "first_name": "John",
          "last_name": "Coach"
        },
        "specialization": "Youth Development",
        "experience_years": 8
      },
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
      ]
    }
  ],

  "fields": [
    {
      "id": 1,
      "name": "Main Field",
      "field_type": "football",
      "capacity": 500,
      "hourly_rate": "150.00",
      "facilities": {
        "lights": true,
        "changing_rooms": true,
        "parking": true
      },
      "is_available": true,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "upcoming_bookings": [
        {
          "id": 1,
          "start_time": "2024-01-20T15:00:00Z",
          "end_time": "2024-01-20T17:00:00Z",
          "status": "confirmed",
          "booked_by": {
            "id": 4,
            "email": "player@elite.com",
            "first_name": "Ahmed",
            "last_name": "Player"
          }
        }
      ]
    }
  ],

  "statistics": {
    "total_admins": 1,
    "total_coaches": 8,
    "total_players": 45,
    "total_parents": 35,
    "total_teams": 6,
    "total_fields": 3,
    "coaches_by_specialization": {
      "Youth Development": 3,
      "Goalkeeping": 1,
      "Fitness": 2,
      "Tactics": 2
    },
    "players_by_position": {
      "Midfielder": 15,
      "Forward": 12,
      "Defender": 15,
      "Goalkeeper": 3
    },
    "teams_by_age_group": {
      "U-17": 2,
      "U-19": 2,
      "Senior": 2
    },
    "fields_by_type": {
      "Football": 2,
      "Training": 1
    }
  }
}
```

---

### 3. **Create Academy (System Admin)**
```http
POST /api/v1/academies/
```
**Permissions**: System Admin only

**Request Body:**
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

---

### 4. **Update Academy (System Admin)**
```http
PUT /api/v1/academies/{academy_id}/
PATCH /api/v1/academies/{academy_id}/
```

---

### 5. **Delete Academy (System Admin)**
```http
DELETE /api/v1/academies/{academy_id}/
```

**Success Response (204): No Content**

---

### 6. **Academy Statistics**
```http
GET /api/v1/academies/{academy_id}/statistics/
```

**Success Response (200):**
```json
{
  "total_coaches": 8,
  "total_players": 45,
  "total_parents": 35,
  "total_teams": 6,
  "total_fields": 3
}
```

---

## ⚽ Player Management

### 🎯 Features
- **Complete Profile Management**: Full CRUD operations for players, coaches, parents
- **Team Management**: Advanced team composition and player assignment
- **Academy Scoping**: Automatic filtering based on user permissions
- **Statistics Tracking**: Individual and team performance metrics
- **Relationship Management**: Parent-child and coach-team relationships

### 1. **List Player Profiles**
```http
GET /api/v1/players/
```

**Query Parameters:**
- `search`: Search by user email, name, position, or academy name
- `academy`: Filter by academy ID
- `position`: Filter by player position
- `team`: Filter by team ID
- `is_active`: Filter by active status
- `page`: Page number for pagination
- `page_size`: Items per page (default: 20)

**Success Response (200):**
```json
{
  "count": 45,
  "next": "http://api/v1/players/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 4,
        "email": "player@elite.com",
        "first_name": "Ahmed",
        "last_name": "Player",
        "full_name": "Ahmed Player",
        "user_type": "player"
      },
      "academy": 1,
      "jersey_number": 10,
      "position": "Midfielder",
      "height": "175.50",
      "weight": "68.00",
      "dominant_foot": "right",
      "bio": "Talented young midfielder",
      "date_of_birth": "2006-03-15",
      "age": 17,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 2. **Get Player Profile Details**
```http
GET /api/v1/players/{player_id}/
```

**Success Response (200):**
```json
{
  "id": 1,
  "user": {
    "id": 4,
    "email": "player@elite.com",
    "first_name": "Ahmed",
    "last_name": "Player",
    "full_name": "Ahmed Player",
    "user_type": "player"
  },
  "academy": 1,
  "jersey_number": 10,
  "position": "Midfielder",
  "height": "175.50",
  "weight": "68.00",
  "dominant_foot": "right",
  "bio": "Talented young midfielder with excellent ball control",
  "date_of_birth": "2006-03-15",
  "age": 17,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "teams": [
    {
      "id": 1,
      "name": "U-17 Team",
      "category": "U-17"
    }
  ],
  "parents": [
    {
      "id": 1,
      "user": {
        "first_name": "Father",
        "last_name": "Player"
      },
      "relationship": "father"
    }
  ]
}
```

---

### 3. **Create Player Profile (Academy Admin)**
```http
POST /api/v1/players/
```
**Permissions**: Academy Admin only

**Request Body:**
```json
{
  "user": 4,
  "academy": 1,
  "jersey_number": 10,
  "position": "Midfielder",
  "height": "175.50",
  "weight": "68.00",
  "dominant_foot": "right",
  "bio": "Talented young midfielder",
  "date_of_birth": "2006-03-15"
}
```

---

### 4. **Update Player Profile**
```http
PUT /api/v1/players/{player_id}/
PATCH /api/v1/players/{player_id}/
```

---

### 5. **Get Player Statistics**
```http
GET /api/v1/players/{player_id}/statistics/
```

**Success Response (200):**
```json
{
  "player_id": 1,
  "player_name": "Ahmed Player",
  "matches_played": 15,
  "goals_scored": 8,
  "assists": 5,
  "average_rating": 7.5,
  "total_minutes": 1200,
  "yellow_cards": 2,
  "red_cards": 0,
  "pass_accuracy": 85.2,
  "shots_on_target": 12,
  "performance_trend": "improving"
}
```

---

### 6. **List Coach Profiles**
```http
GET /api/v1/coaches/
```

**Query Parameters:**
- `search`: Search by user email, name, specialization, or academy name
- `academy`: Filter by academy ID
- `specialization`: Filter by coaching specialization
- `is_active`: Filter by active status

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
        "full_name": "John Coach",
        "user_type": "coach"
      },
      "academy": 1,
      "specialization": "Youth Development",
      "experience_years": 8,
      "certification": "UEFA B License",
      "bio": "Specialist in youth player development",
      "date_of_birth": "1985-08-10",
      "age": 39,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 7. **Get Coach Details & Teams**
```http
GET /api/v1/coaches/{coach_id}/
GET /api/v1/coaches/{coach_id}/teams/
```

**Coach Teams Response (200):**
```json
[
  {
    "id": 1,
    "name": "U-17 Team",
    "category": "U-17",
    "formation": "4-4-2",
    "total_players": 18
  },
  {
    "id": 2,
    "name": "U-19 Team",
    "category": "U-19",
    "formation": "4-3-3",
    "total_players": 20
  }
]
```

---

### 8. **Get Coach Statistics**
```http
GET /api/v1/coaches/{coach_id}/statistics/
```

**Success Response (200):**
```json
{
  "coach_id": 1,
  "coach_name": "John Coach",
  "teams_managed": 2,
  "total_players": 38,
  "matches_coached": 45,
  "wins": 28,
  "draws": 12,
  "losses": 5,
  "win_rate": 62.2,
  "player_development_success": 85.5
}
```

---

### 9. **List Parent Profiles**
```http
GET /api/v1/parents/
```

**Query Parameters:**
- `search`: Search by user email, name, or academy name
- `academy`: Filter by academy ID
- `is_active`: Filter by active status

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
        "full_name": "Father Player",
        "user_type": "parent"
      },
      "relationship": "father",
      "bio": "Supportive parent",
      "date_of_birth": "1980-05-20",
      "age": 44,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "children": [
        {
          "id": 1,
          "user": {
            "first_name": "Ahmed",
            "last_name": "Player"
          },
          "position": "Midfielder",
          "jersey_number": 10
        }
      ]
    }
  ]
}
```

---

### 10. **List Teams**
```http
GET /api/v1/teams/
```

**Query Parameters:**
- `search`: Search by name, category, academy name, or coach name
- `academy`: Filter by academy ID
- `category`: Filter by team category (U-17, U-19, Senior, etc.)
- `coach`: Filter by coach ID
- `is_active`: Filter by active status

**Success Response (200):**
```json
{
  "count": 6,
  "results": [
    {
      "id": 1,
      "name": "U-17 Team",
      "academy": 1,
      "coach": 1,
      "category": "U-17",
      "formation": "4-4-2",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "total_players": 18,
      "coach_details": {
        "id": 1,
        "user": {
          "first_name": "John",
          "last_name": "Coach"
        },
        "specialization": "Youth Development"
      }
    }
  ]
}
```

---

### 11. **Team Management Actions**
```http
GET /api/v1/teams/{team_id}/players/
POST /api/v1/teams/{team_id}/add_player/
POST /api/v1/teams/{team_id}/remove_player/
```

**Get Team Players Response (200):**
```json
[
  {
    "id": 1,
    "user": {
      "first_name": "Ahmed",
      "last_name": "Player"
    },
    "jersey_number": 10,
    "position": "Midfielder",
    "date_of_birth": "2006-03-15"
  },
  {
    "id": 2,
    "user": {
      "first_name": "Mohamed",
      "last_name": "Forward"
    },
    "jersey_number": 9,
    "position": "Forward",
    "date_of_birth": "2006-08-22"
  }
]
```

**Add Player Request:**
```json
{
  "player_id": 5
}
```

**Remove Player Request:**
```json
{
  "player_id": 5
}
```

**Success Response (200):**
```json
{
  "message": "Player added to team successfully"
}
```

---

### 12. **Team Statistics**
```http
GET /api/v1/teams/{team_id}/statistics/
```

**Success Response (200):**
```json
{
  "team_id": 1,
  "team_name": "U-17 Team",
  "total_players": 18,
  "matches_played": 20,
  "wins": 12,
  "draws": 5,
  "losses": 3,
  "goals_scored": 35,
  "goals_conceded": 18,
  "win_rate": 60.0,
  "goal_difference": 17,
  "average_age": 16.8,
  "top_scorer": {
    "player_id": 2,
    "name": "Mohamed Forward",
    "goals": 15
  },
  "position_distribution": {
    "Forward": 4,
    "Midfielder": 8,
    "Defender": 5,
    "Goalkeeper": 1
  }
}
```

---

## 🥅 Match Management

### 1. **List Matches**
```http
GET /api/v1/matches/
```

**Query Parameters:**
- `search`: Search by team names, venue, match type
- `home_team`: Filter by home team ID
- `away_team`: Filter by away team ID
- `venue`: Filter by venue ID
- `match_type`: Filter by match type
- `status`: Filter by match status

**Success Response (200):**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "home_team": {
        "id": 1,
        "name": "U-17 Team",
        "academy": "Elite Football Academy"
      },
      "away_team": {
        "id": 2,
        "name": "U-17 Visitors",
        "academy": "Another Academy"
      },
      "match_type": "friendly",
      "match_date": "2024-01-25T15:00:00Z",
      "venue": {
        "id": 1,
        "name": "Main Field",
        "academy": "Elite Football Academy"
      },
      "status": "scheduled",
      "home_score": null,
      "away_score": null,
      "is_active": true,
      "created_at": "2024-01-20T00:00:00Z"
    }
  ]
}
```

---

### 2. **Create Match (Academy Admin)**
```http
POST /api/v1/matches/
```

**Request Body:**
```json
{
  "home_team": 1,
  "away_team": 2,
  "match_type": "friendly",
  "match_date": "2024-01-25T15:00:00Z",
  "venue": 1
}
```

---

### 3. **Match Actions**
```http
POST /api/v1/matches/{match_id}/start_match/
POST /api/v1/matches/{match_id}/end_match/
POST /api/v1/matches/{match_id}/cancel_match/
```

**Start Match Response (200):**
```json
{
  "message": "Match started successfully",
  "status": "in_progress"
}
```

**End Match Request:**
```json
{
  "home_score": 2,
  "away_score": 1
}
```

**End Match Response (200):**
```json
{
  "message": "Match ended successfully",
  "status": "completed",
  "home_score": 2,
  "away_score": 1
}
```

---

### 4. **Match Statistics**
```http
GET /api/v1/matches/{match_id}/statistics/
```

**Success Response (200):**
```json
{
  "home_score": 2,
  "away_score": 1,
  "total_players": 22,
  "match_duration": 90,
  "total_goals": 3
}
```

---

## 📅 Advanced Booking System

### 🎯 Features
- **🔒 Conflict Detection**: Automatic booking overlap prevention with intelligent suggestions
- **📧 Lifecycle Email Automation**: Complete email workflow from creation to completion
- **⚡ Real-time Availability**: Instant field availability checking with alternative slots
- **💰 Smart Cost Calculation**: Automatic pricing with duration and rate calculations
- **📊 Comprehensive Analytics**: Booking statistics, utilization reports, and revenue tracking
- **🔔 Reminder System**: Automated email reminders with management commands
- **🎯 Academy Scoping**: Automatic filtering based on user permissions and academy access
- **📅 Schedule Management**: Complete field scheduling with conflict resolution
- **💳 Booking States**: Full lifecycle management (pending → confirmed → completed/cancelled)
- **🔍 Advanced Filtering**: Search and filter by multiple criteria

### 1. **List Fields**
```http
GET /api/v1/fields/
```

**Query Parameters:**
- `search`: Search by name, field type, or academy name
- `field_type`: Filter by field type (football, training, etc.)
- `academy`: Filter by academy ID
- `is_available`: Filter by availability status
- `is_active`: Filter by active status
- `page`: Page number for pagination
- `page_size`: Items per page (default: 20)

**Success Response (200):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "academy": 1,
      "academy_name": "Elite Football Academy",
      "academy_details": {
        "id": 1,
        "name": "Elite Football Academy",
        "phone": "+1234567890",
        "email": "info@elite.com"
      },
      "name": "Main Field",
      "field_type": "football",
      "capacity": 500,
      "hourly_rate": "150.00",
      "facilities": {
        "lights": true,
        "changing_rooms": true,
        "parking": true,
        "sound_system": true,
        "scoreboard": true
      },
      "is_available": true,
      "is_active": true,
      "booking_count": 85,
      "next_available_slot": "2024-01-25T14:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 2. **Get Field Details**
```http
GET /api/v1/fields/{field_id}/
```

**Success Response (200):**
```json
{
  "id": 1,
  "academy": 1,
  "academy_name": "Elite Football Academy",
  "name": "Main Field",
  "field_type": "football",
  "capacity": 500,
  "hourly_rate": "150.00",
  "facilities": {
    "lights": true,
    "changing_rooms": true,
    "parking": true,
    "sound_system": true,
    "scoreboard": true
  },
  "is_available": true,
  "is_active": true,
  "booking_count": 85,
  "next_available_slot": "2024-01-25T14:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "upcoming_bookings": [
    {
      "id": 15,
      "start_time": "2024-01-25T15:00:00Z",
      "end_time": "2024-01-25T17:00:00Z",
      "status": "confirmed",
      "booked_by": {
        "first_name": "Ahmed",
        "last_name": "Player"
      }
    }
  ]
}
```

---

### 3. **Create Field (Academy Admin)**
```http
POST /api/v1/fields/
```
**Permissions**: Academy Admin only

**Request Body:**
```json
{
  "academy": 1,
  "name": "Training Field 2",
  "field_type": "training",
  "capacity": 200,
  "hourly_rate": "120.00",
  "facilities": {
    "lights": true,
    "changing_rooms": false,
    "parking": true
  }
}
```

---

### 4. **Update Field (Academy Admin)**
```http
PUT /api/v1/fields/{field_id}/
PATCH /api/v1/fields/{field_id}/
```

---

### 5. **Check Field Availability**
```http
GET /api/v1/fields/{field_id}/availability/
```

**Query Parameters:**
- `start_time`: Start time (ISO format: YYYY-MM-DDTHH:MM:SS)
- `end_time`: End time (ISO format: YYYY-MM-DDTHH:MM:SS)

**Success Response (200):**
```json
{
  "available": true,
  "conflicting_bookings": [],
  "alternative_slots": [
    {
      "start_time": "2024-01-25T13:00:00Z",
      "end_time": "2024-01-25T15:00:00Z",
      "reason": "Earlier slot available"
    },
    {
      "start_time": "2024-01-25T17:00:00Z",
      "end_time": "2024-01-25T19:00:00Z",
      "reason": "Later slot available"
    }
  ]
}
```

**Conflict Response (200):**
```json
{
  "available": false,
  "conflicting_bookings": [
    {
      "id": 20,
      "start_time": "2024-01-25T14:00:00Z",
      "end_time": "2024-01-25T16:00:00Z",
      "booked_by": "Ahmed Player",
      "status": "confirmed"
    }
  ],
  "alternative_slots": [
    {
      "start_time": "2024-01-25T16:00:00Z",
      "end_time": "2024-01-25T18:00:00Z",
      "reason": "Next available slot"
    }
  ]
}
```

---

### 6. **Get Field Utilization Statistics**
```http
GET /api/v1/fields/{field_id}/utilization/
```

**Query Parameters:**
- `start_date`: Start date for analysis (YYYY-MM-DD)
- `end_date`: End date for analysis (YYYY-MM-DD)

**Success Response (200):**
```json
{
  "field_id": 1,
  "field_name": "Main Field",
  "total_booked_hours": 156.5,
  "total_available_hours": 210.0,
  "utilization_rate": 74.5,
  "booking_count": 45,
  "peak_hours": ["15:00", "16:00", "17:00", "18:00"],
  "revenue_generated": "23475.00",
  "average_booking_duration": 3.5,
  "cancellation_rate": 8.2,
  "busiest_days": ["Saturday", "Sunday", "Wednesday"]
}
```

---

### 7. **Get Field Schedule**
```http
GET /api/v1/fields/{field_id}/schedule/
```

**Query Parameters:**
- `date`: Start date for schedule (YYYY-MM-DD, defaults to today)
- `days`: Number of days to show (default: 7)

**Success Response (200):**
```json
[
  {
    "date": "2024-01-25",
    "bookings": [
      {
        "id": 15,
        "start_time": "15:00:00",
        "end_time": "17:00:00",
        "booked_by": "Ahmed Player",
        "status": "confirmed",
        "booking_type": "training"
      },
      {
        "id": 16,
        "start_time": "18:00:00",
        "end_time": "20:00:00",
        "booked_by": "John Coach",
        "status": "pending",
        "booking_type": "team_practice"
      }
    ],
    "available_slots": [
      {
        "start_time": "09:00:00",
        "end_time": "15:00:00"
      },
      {
        "start_time": "17:00:00",
        "end_time": "18:00:00"
      },
      {
        "start_time": "20:00:00",
        "end_time": "22:00:00"
      }
    ]
  }
]
```

---

### 8. **List Bookings**
```http
GET /api/v1/bookings/
```

**Query Parameters:**
- `search`: Search by field name, booked by name, or email
- `field`: Filter by field ID
- `status`: Filter by booking status (pending, confirmed, cancelled, completed)
- `field__academy`: Filter by academy ID
- `booked_by`: Filter by user ID
- `start_date`: Filter bookings starting from date (YYYY-MM-DD)
- `end_date`: Filter bookings ending before date (YYYY-MM-DD)
- `page`: Page number for pagination
- `page_size`: Items per page (default: 20)

**Success Response (200):**
```json
{
  "count": 125,
  "next": "http://api/v1/bookings/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "field": {
        "id": 1,
        "name": "Main Field",
        "field_type": "football",
        "academy": "Elite Football Academy"
      },
      "field_details": {
        "id": 1,
        "name": "Main Field",
        "hourly_rate": "150.00",
        "facilities": {
          "lights": true,
          "changing_rooms": true
        }
      },
      "booked_by": {
        "id": 4,
        "email": "player@elite.com",
        "first_name": "Ahmed",
        "last_name": "Player"
      },
      "booked_by_details": {
        "id": 4,
        "email": "player@elite.com",
        "full_name": "Ahmed Player",
        "user_type": "player"
      },
      "academy_name": "Elite Football Academy",
      "start_time": "2024-01-25T15:00:00Z",
      "end_time": "2024-01-25T17:00:00Z",
      "duration_hours": 2.0,
      "total_cost": "300.00",
      "status": "confirmed",
      "notes": "Team training session",
      "match": null,
      "can_cancel": true,
      "can_modify": true,
      "is_active": true,
      "created_at": "2024-01-20T00:00:00Z",
      "updated_at": "2024-01-20T00:00:00Z"
    }
  ]
}
```

---

### 3. **Create Booking**
```http
POST /api/v1/bookings/
```

**Request Body:**
```json
{
  "field": 1,
  "start_time": "2024-01-25T15:00:00Z",
  "end_time": "2024-01-25T17:00:00Z",
  "notes": "Training session"
}
```

**Success Response (201):**
```json
{
  "id": 16,
  "field": 1,
  "booked_by": 4,
  "start_time": "2024-01-25T15:00:00Z",
  "end_time": "2024-01-25T17:00:00Z",
  "total_cost": "300.00",
  "status": "pending",
  "notes": "Training session",
  "is_active": true,
  "created_at": "2024-01-20T10:00:00Z"
}
```

---

### 4. **Booking Actions**
```http
POST /api/v1/bookings/{booking_id}/confirm/
POST /api/v1/bookings/{booking_id}/cancel/
POST /api/v1/bookings/{booking_id}/complete/
```

**Confirm Booking Response (200):**
```json
{
  "message": "Booking confirmed successfully",
  "status": "confirmed"
}
```

---

### 5. **Advanced Booking Availability Check**
```http
POST /api/v1/bookings/check_availability/
```

**Request Body:**
```json
{
  "field": 1,
  "start_time": "2024-01-25T15:00:00Z",
  "end_time": "2024-01-25T17:00:00Z"
}
```

**Success Response (200):**
```json
{
  "available": true,
  "conflicts": [],
  "suggestions": [
    {
      "start_time": "2024-01-25T13:00:00Z",
      "end_time": "2024-01-25T15:00:00Z",
      "reason": "Alternative slot available"
    }
  ],
  "estimated_cost": "300.00",
  "reason": "Field is available for requested time"
}
```

**Conflict Response (200):**
```json
{
  "available": false,
  "conflicts": [
    {
      "booking_id": 15,
      "start_time": "2024-01-25T14:00:00Z",
      "end_time": "2024-01-25T16:00:00Z",
      "booked_by": "Ahmed Player"
    }
  ],
  "suggestions": [
    {
      "start_time": "2024-01-25T16:00:00Z",
      "end_time": "2024-01-25T18:00:00Z",
      "reason": "Next available slot"
    },
    {
      "start_time": "2024-01-25T12:00:00Z",
      "end_time": "2024-01-25T14:00:00Z",
      "reason": "Earlier slot available"
    }
  ],
  "reason": "Booking conflicts with existing reservation"
}
```

---

### 6. **My Bookings**
```http
GET /api/v1/bookings/my_bookings/
```

**Success Response (200):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 20,
      "field": {
        "id": 1,
        "name": "Main Field",
        "academy": "Elite Football Academy"
      },
      "start_time": "2024-01-25T15:00:00Z",
      "end_time": "2024-01-25T17:00:00Z",
      "status": "confirmed",
      "total_cost": "300.00",
      "created_at": "2024-01-20T10:00:00Z"
    }
  ]
}
```

---

### 7. **Booking Statistics (Academy Admin)**
```http
GET /api/v1/bookings/statistics/
```

**Success Response (200):**
```json
{
  "total_bookings": 125,
  "confirmed_bookings": 95,
  "pending_bookings": 15,
  "cancelled_bookings": 15,
  "total_revenue": "18750.00",
  "average_booking_duration": 2.5,
  "peak_booking_hours": ["15:00", "16:00", "17:00"],
  "most_popular_field": {
    "id": 1,
    "name": "Main Field",
    "booking_count": 65
  },
  "monthly_stats": [
    {
      "month": "2024-01",
      "bookings": 45,
      "revenue": "6750.00"
    }
  ]
}
```

---

### 8. **Send Booking Reminder**
```http
POST /api/v1/bookings/{booking_id}/send_reminder/
```

**Success Response (200):**
```json
{
  "message": "Reminder email sent successfully",
  "sent_to": "player@elite.com",
  "reminder_type": "upcoming_booking"
}
```

---

### 9. **Field Utilization**
```http
GET /api/v1/fields/{field_id}/utilization/
```

**Query Parameters:**
- `start_date`: Start date for analysis (YYYY-MM-DD)
- `end_date`: End date for analysis (YYYY-MM-DD)

**Success Response (200):**
```json
{
  "total_booked_hours": 156.5,
  "total_available_hours": 210.0,
  "utilization_rate": 74.5,
  "booking_count": 45,
  "peak_hours": ["15:00", "16:00", "17:00"],
  "revenue_generated": "23475.00"
}
```

---

### 10. **Field Schedule**
```http
GET /api/v1/fields/{field_id}/schedule/
```

**Query Parameters:**
- `date`: Start date for schedule (YYYY-MM-DD, defaults to today)
- `days`: Number of days to show (default: 7)

**Success Response (200):**
```json
[
  {
    "date": "2024-01-25",
    "bookings": [
      {
        "id": 15,
        "start_time": "15:00:00",
        "end_time": "17:00:00",
        "booked_by": "Ahmed Player",
        "status": "confirmed"
      },
      {
        "id": 16,
        "start_time": "18:00:00",
        "end_time": "20:00:00",
        "booked_by": "John Coach",
        "status": "pending"
      }
    ]
  }
]
```

---

## 📊 Analytics & Reporting

### 🎯 Enhanced Features
- **Real-time Statistics**: Live academy, player, field, and booking analytics
- **Performance Tracking**: Individual and team performance metrics with trends
- **Utilization Reports**: Field usage, booking analytics, and revenue tracking
- **Comprehensive Filtering**: Filter by academy, date range, team, and player criteria
- **Trend Analysis**: Monthly growth patterns and performance improvements
- **Custom Reports**: Detailed breakdowns by position, age group, and specialization

### 1. **Academy Overview Analytics**
```http
GET /api/v1/analytics/academy_overview/
```

**Query Parameters:**
- `academy_id`: Academy ID (required for system admins)

**Success Response (200):**
```json
{
  "academy_id": 1,
  "academy_name": "Elite Football Academy",
  "total_players": 45,
  "total_coaches": 8,
  "total_teams": 6,
  "total_matches": 125,
  "total_fields": 3,
  "active_bookings": 25,
  "monthly_growth": {
    "new_players": 8,
    "new_coaches": 2,
    "matches_played": 15,
    "booking_increase": 20
  },
  "performance_summary": {
    "overall_win_rate": 68.5,
    "average_team_size": 18,
    "field_utilization": 72.3,
    "revenue_this_month": "12500.00"
  }
}
```

---

### 2. **Player Performance Analytics**
```http
GET /api/v1/analytics/player_performance/
```

**Query Parameters:**
- `academy_id`: Filter by academy (system admin)
- `team_id`: Filter by specific team
- `position`: Filter by player position
- `start_date`: Start date for analysis (YYYY-MM-DD)
- `end_date`: End date for analysis (YYYY-MM-DD)

**Success Response (200):**
```json
{
  "total_players": 45,
  "average_age": 16.8,
  "position_distribution": {
    "Midfielder": 15,
    "Forward": 12,
    "Defender": 15,
    "Goalkeeper": 3
  },
  "top_performers": [
    {
      "player_id": 1,
      "name": "Ahmed Player",
      "position": "Midfielder",
      "rating": 8.2,
      "goals": 15,
      "assists": 8,
      "matches": 20
    },
    {
      "player_id": 2,
      "name": "Mohamed Forward",
      "position": "Forward",
      "rating": 7.9,
      "goals": 22,
      "assists": 5,
      "matches": 18
    }
  ],
  "performance_trends": {
    "average_rating_improvement": 0.3,
    "goal_scoring_trend": "increasing",
    "fitness_levels": "excellent"
  },
  "monthly_stats": [
    {
      "month": "2024-01",
      "total_goals": 45,
      "total_assists": 28,
      "average_rating": 7.4,
      "improvement_rate": 12.5
    }
  ]
}
```

---

### 3. **Team Performance Analytics**
```http
GET /api/v1/analytics/team_performance/
```

**Query Parameters:**
- `academy_id`: Filter by academy (system admin)
- `category`: Filter by team category (U-17, U-19, Senior)
- `start_date`: Start date for analysis
- `end_date`: End date for analysis

**Success Response (200):**
```json
{
  "total_teams": 6,
  "category_distribution": {
    "U-17": 2,
    "U-19": 2,
    "Senior": 2
  },
  "top_teams": [
    {
      "team_id": 1,
      "name": "U-17 Team",
      "category": "U-17",
      "matches_played": 20,
      "wins": 14,
      "draws": 4,
      "losses": 2,
      "win_rate": 70.0,
      "goals_scored": 42,
      "goals_conceded": 18,
      "goal_difference": 24
    },
    {
      "team_id": 2,
      "name": "U-19 Team",
      "category": "U-19",
      "matches_played": 18,
      "wins": 12,
      "draws": 3,
      "losses": 3,
      "win_rate": 66.7,
      "goals_scored": 38,
      "goals_conceded": 22,
      "goal_difference": 16
    }
  ],
  "overall_statistics": {
    "total_matches": 95,
    "total_wins": 58,
    "total_draws": 20,
    "total_losses": 17,
    "overall_win_rate": 61.1,
    "average_goals_per_match": 2.8
  },
  "performance_trends": {
    "win_rate_trend": "improving",
    "goal_scoring_efficiency": "excellent",
    "defensive_stability": "good"
  }
}
```

---

### 4. **Match Statistics & Trends**
```http
GET /api/v1/analytics/match_statistics/
```

**Query Parameters:**
- `academy_id`: Filter by academy
- `team_id`: Filter by specific team
- `match_type`: Filter by match type (friendly, league, tournament)
- `start_date`: Start date for analysis
- `end_date`: End date for analysis

**Success Response (200):**
```json
{
  "total_matches": 125,
  "match_type_distribution": {
    "friendly": 45,
    "league": 65,
    "tournament": 15
  },
  "results_summary": {
    "wins": 75,
    "draws": 28,
    "losses": 22,
    "win_rate": 60.0
  },
  "scoring_statistics": {
    "total_goals_scored": 285,
    "total_goals_conceded": 198,
    "average_goals_per_match": 2.28,
    "clean_sheets": 35,
    "high_scoring_matches": 28
  },
  "monthly_trends": [
    {
      "month": "2024-01",
      "matches": 15,
      "wins": 10,
      "goals_scored": 38,
      "goals_conceded": 22,
      "win_rate": 66.7
    }
  ],
  "venue_performance": {
    "home_matches": 65,
    "home_wins": 45,
    "away_matches": 60,
    "away_wins": 30,
    "home_advantage": 15.4
  }
}
```

---

### 5. **Field Utilization & Booking Analytics**
```http
GET /api/v1/analytics/field_utilization/
```

**Query Parameters:**
- `academy_id`: Filter by academy
- `field_id`: Filter by specific field
- `start_date`: Start date for analysis (YYYY-MM-DD)
- `end_date`: End date for analysis (YYYY-MM-DD)

**Success Response (200):**
```json
{
  "total_fields": 3,
  "total_bookings": 285,
  "overall_utilization_rate": 74.5,
  "total_revenue": "42750.00",
  "most_popular_fields": [
    {
      "field_id": 1,
      "name": "Main Field",
      "bookings_count": 125,
      "utilization_rate": 82.3,
      "revenue": "18750.00",
      "hourly_rate": "150.00"
    },
    {
      "field_id": 2,
      "name": "Training Field",
      "bookings_count": 95,
      "utilization_rate": 71.2,
      "revenue": "14250.00",
      "hourly_rate": "120.00"
    }
  ],
  "booking_trends": {
    "peak_hours": ["15:00", "16:00", "17:00", "18:00"],
    "busiest_days": ["Saturday", "Sunday", "Wednesday"],
    "seasonal_pattern": "increasing",
    "average_booking_duration": 2.3
  },
  "revenue_analysis": {
    "monthly_revenue": "8500.00",
    "revenue_growth": 15.2,
    "average_booking_value": "150.00",
    "cancellation_rate": 8.5
  },
  "utilization_by_type": {
    "training_sessions": 45.2,
    "matches": 28.8,
    "private_bookings": 26.0
  },
  "booking_status_distribution": {
    "confirmed": 245,
    "pending": 25,
    "cancelled": 15,
    "completed": 220
  }
}
```

---

## 🔔 Notifications

### 1. **List User Notifications**
```http
GET /api/v1/notifications/
```

**Query Parameters:**
- `is_read`: Filter by read status
- `notification_type`: Filter by notification type

**Success Response (200):**
```json
{
  "count": 10,
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

---

### 2. **Mark Notification as Read**
```http
POST /api/v1/notifications/{notification_id}/mark_as_read/
```

**Success Response (200):**
```json
{
  "message": "Notification marked as read"
}
```

---

### 3. **Mark All as Read**
```http
POST /api/v1/notifications/mark_all_as_read/
```

**Success Response (200):**
```json
{
  "message": "All notifications marked as read",
  "updated_count": 5
}
```

---

### 4. **Notification Statistics**
```http
GET /api/v1/notifications/statistics/
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

## 📧 Email System

### 🎯 Automated Email Notifications

The platform includes a comprehensive email notification system for booking lifecycle management:

### **Email Types**

#### 1. **Booking Created**
- **Trigger**: When a new booking is submitted
- **Recipient**: Customer
- **Content**: Booking confirmation with details and next steps

#### 2. **Booking Confirmed**
- **Trigger**: When academy admin approves a booking
- **Recipient**: Customer
- **Content**: Confirmation with arrival instructions and contact info

#### 3. **Booking Cancelled**
- **Trigger**: When booking is cancelled by admin or customer
- **Recipient**: Customer or Admin
- **Content**: Cancellation notice with refund information

#### 4. **Booking Reminder**
- **Trigger**: 24 hours before booking (automated)
- **Recipient**: Customer
- **Content**: Reminder with checklist and academy contact

#### 5. **Booking Completed**
- **Trigger**: After booking end time
- **Recipient**: Customer
- **Content**: Thank you message with feedback request

#### 6. **Admin New Booking**
- **Trigger**: When new booking is submitted
- **Recipient**: Academy Admin
- **Content**: New booking notification with customer details

### **Email Configuration**

**Environment Variables (.env file):**
```bash
# Email Configuration (Mailtrap)
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_HOST_USER=3a92a30635c240
EMAIL_HOST_PASSWORD=f40c398838ce54
EMAIL_PORT=2525
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=AI Football Platform <noreply@aifootballplatform.com>
```

**Django Settings (uses environment variables):**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='sandbox.smtp.mailtrap.io')
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = env('EMAIL_PORT', default=2525)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='AI Football Platform <noreply@aifootballplatform.com>')
```

**Production Environment:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-production-smtp-host.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-production-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-production-password'
```

### **Email Templates**

All emails use professional HTML templates with:
- Academy branding and colors
- Responsive design for mobile devices
- Clear call-to-action buttons
- Contact information and support links
- Booking details and instructions

---

## 🔧 Management Commands

### **Send Booking Reminders**

Automated command for sending booking reminders:

```bash
# Send reminders for bookings in next 24 hours
python manage.py send_booking_reminders

# Send reminders for specific hours ahead
python manage.py send_booking_reminders --hours 48

# Dry run to test without sending emails
python manage.py send_booking_reminders --dry-run

# Verbose output
python manage.py send_booking_reminders --verbosity 2
```

**Cron Job Setup:**
```bash
# Add to crontab for daily execution at 9 AM
0 9 * * * /path/to/venv/bin/python /path/to/project/manage.py send_booking_reminders
```

**Command Features:**
- Configurable hours ahead (default: 24)
- Dry-run capability for testing
- Comprehensive error handling and logging
- Email sending status tracking
- Duplicate prevention

---

## ❌ Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content returned
- **400 Bad Request**: Validation errors or malformed request
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Error Response Format

**Validation Errors (400):**
```json
{
  "email": ["This field is required."],
  "password": ["Password must be at least 8 characters long."]
}
```

**Authentication Error (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Permission Error (403):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Not Found Error (404):**
```json
{
  "detail": "Not found."
}
```

---

## 🧪 Testing

### **System Check**
```bash
# Verify all systems are working
python manage.py check

# Run with specific settings
python manage.py check --settings=config.settings.production
```

### **Environment Setup**
```bash
# 1. Copy environment variables template
cp env.example .env

# 2. Edit .env file with your settings
# (Email credentials are already set for Mailtrap)

# 3. Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser
```

### **Sample API Tests**

#### **Authentication Test**
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@test.com", "password": "admin123"}'
```

#### **Academy Management Test**
```bash
# Get academy with all nested objects
curl -X GET http://localhost:8000/api/v1/academies/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### **Booking System Test**
```bash
# Check availability
curl -X POST http://localhost:8000/api/v1/bookings/check_availability/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field": 1,
    "start_time": "2024-01-25T15:00:00Z",
    "end_time": "2024-01-25T17:00:00Z"
  }'

# Create booking
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field": 1,
    "start_time": "2024-01-25T15:00:00Z",
    "end_time": "2024-01-25T17:00:00Z",
    "notes": "Training session"
  }'
```

#### **Analytics Test**
```bash
# Get academy overview
curl -X GET http://localhost:8000/api/v1/analytics/academy_overview/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **Email Testing**
```bash
# Test booking reminders (dry run)
python manage.py send_booking_reminders --dry-run

# Send actual test reminders
python manage.py send_booking_reminders

# Check emails in Mailtrap inbox
# Visit: https://mailtrap.io/inboxes
# Login with your Mailtrap account to see sent emails
```

**Mailtrap Integration:**
- All emails are captured by Mailtrap for testing
- No emails reach real recipients during development
- Professional email previews with HTML rendering
- Easy testing of email templates and content

---

## 📖 Additional Resources

### **API Documentation**
- **Swagger Documentation**: `/api/docs/` - Interactive API explorer
- **ReDoc Documentation**: `/api/redoc/` - Detailed API documentation
- **Admin Interface**: `/admin/` - Django admin (email-based login)

### **Complete API Coverage Summary**

**📊 Total Endpoints: 65+ Across 9 Major Categories**

#### **🔐 Authentication (8 endpoints)**
- Login/Logout with JWT tokens
- User registration (external client + academy users)
- Password management and profile updates
- Token refresh and session management

#### **👥 User Management (7 endpoints)**
- System admin user management (full CRUD)
- Academy admin user management (academy-scoped)
- User activation/deactivation and password reset
- Advanced filtering and search capabilities

#### **🏟️ Academy Management (6 endpoints + statistics)**
- Complete CRUD operations for academies
- Comprehensive nested data retrieval (all related objects)
- Academy statistics and performance metrics
- System admin vs academy user permission handling

#### **⚽ Player Management (12 endpoints + team actions)**
- Player, coach, parent profile management
- Team composition and player assignment
- Individual and team statistics tracking
- Relationship management (parent-child, coach-team)

#### **🥅 Match Management (7 endpoints + state management)**
- Match scheduling and CRUD operations
- Match state transitions (start, end, cancel)
- Match statistics and performance tracking
- Academy-scoped match access and management

#### **📅 Advanced Booking System (15+ endpoints)**
- Field management with complete CRUD operations
- Field availability checking with conflict detection
- Booking lifecycle management (pending → confirmed → completed/cancelled)
- Advanced availability checking with alternative suggestions
- Field utilization statistics and revenue tracking
- Schedule management with booking calendar
- Academy admin booking oversight and management
- User booking history and personal bookings
- Automated email notifications for all booking states
- Booking reminders and automated follow-ups

#### **📊 Analytics & Reporting (5 comprehensive reports)**
- Academy overview with complete statistics
- Player performance analytics with trends
- Team performance and comparison analytics
- Match statistics and venue performance
- Field utilization and booking revenue analytics

#### **🔔 Notifications (5 endpoints + bulk actions)**
- User notification management with filtering
- Mark as read functionality (individual + bulk)
- Notification statistics and unread counts
- Academy-scoped notification delivery

#### **📧 Email System (6 automated email types)**
- Booking created confirmation emails
- Booking confirmed academy approval emails
- Booking cancelled notification emails
- Booking reminder emails (24h advance)
- Booking completed thank you emails
- Academy admin new booking notifications

#### **🛠️ Management Commands**
- Automated booking reminder system
- Configurable reminder timing (default 24h)
- Dry-run capability for testing
- Comprehensive error handling and logging

### **✨ Key Features Summary**
- ✅ **Atomic Transactions**: All write operations are transaction-safe with rollback
- ✅ **Email Automation**: Complete booking lifecycle email system with HTML templates
- ✅ **Conflict Prevention**: Advanced booking overlap detection with intelligent suggestions
- ✅ **Nested Data**: Academy endpoints return comprehensive object hierarchies
- ✅ **Real-time Analytics**: Live statistics and reporting with trend analysis
- ✅ **Management Commands**: Automated reminder and maintenance tasks with cron support
- ✅ **Professional UI**: Responsive email templates and admin interface
- ✅ **Comprehensive Validation**: Robust data validation and error handling
- ✅ **Academy Scoping**: Automatic filtering based on user permissions and academy access
- ✅ **Performance Optimized**: Query optimization with prefetch_related and select_related
- ✅ **Revenue Tracking**: Complete booking cost calculation and revenue analytics
- ✅ **Schedule Management**: Advanced field scheduling with availability checking
- ✅ **User Experience**: Professional booking workflow with clear status management

### **System Architecture**
- **Backend**: Django 4.x with Django REST Framework
- **Authentication**: JWT with email-based login
- **Database**: PostgreSQL (recommended) or SQLite for development
- **Email**: SMTP integration with HTML templates
- **Documentation**: Auto-generated OpenAPI/Swagger specs
- **Permissions**: Role-based access control with academy scoping

### **Production Deployment**
- Configure SMTP settings for email functionality
- Set up cron jobs for automated booking reminders
- Configure static file serving for media uploads
- Set up proper logging and monitoring
- Configure database connection pooling

---

*This documentation covers all 44+ endpoints across 9 categories in the AI Football Platform API. The system includes atomic transactions, comprehensive email automation, advanced booking conflict detection, and real-time analytics. For the most up-to-date information, refer to the interactive API documentation at `/api/docs/`.*

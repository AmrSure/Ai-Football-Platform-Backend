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

### 1. **Login**
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

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "email": "user@example.com",
  "user_type": "academy_admin",
  "first_name": "John",
  "last_name": "Doe"
}
```

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

### 1. **List Players**
```http
GET /api/v1/players/
```

**Query Parameters:**
- `search`: Search by user email, name, or academy name
- `academy`: Filter by academy ID
- `is_active`: Filter by active status

**Success Response (200):**
```json
{
  "count": 45,
  "next": null,
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
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 2. **List Coaches**
```http
GET /api/v1/coaches/
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

### 3. **List Parents**
```http
GET /api/v1/parents/
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
        "full_name": "Father Player",
        "user_type": "parent"
      },
      "relationship": "father",
      "bio": "Supportive parent",
      "date_of_birth": "1980-05-20",
      "age": 44,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 4. **List Teams**
```http
GET /api/v1/teams/
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
      "coach": 1,
      "age_group": "U-17",
      "formation": "4-4-2",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 5. **Team Player Management**
```http
POST /api/v1/teams/{team_id}/add_player/
POST /api/v1/teams/{team_id}/remove_player/
```

**Add Player Request:**
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

### 6. **Player/Coach/Team Statistics**
```http
GET /api/v1/players/{player_id}/statistics/
GET /api/v1/coaches/{coach_id}/statistics/
GET /api/v1/teams/{team_id}/statistics/
```

**Player Statistics Response (200):**
```json
{
  "matches_played": 15,
  "goals_scored": 8,
  "assists": 5,
  "average_rating": 7.5,
  "total_minutes": 1200
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
- **Conflict Detection**: Automatic booking overlap prevention
- **Email Notifications**: Complete lifecycle email automation
- **Availability Checking**: Real-time field availability with suggestions
- **Cost Calculation**: Automatic pricing based on duration and field rates
- **Booking Analytics**: Comprehensive statistics and utilization reports
- **Reminder System**: Automated booking reminders via management commands

### 1. **List Fields**
```http
GET /api/v1/fields/
```

**Success Response (200):**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "academy": 1,
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
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 2. **List Bookings**
```http
GET /api/v1/bookings/
```

**Success Response (200):**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "field": {
        "id": 1,
        "name": "Main Field",
        "field_type": "football"
      },
      "booked_by": {
        "id": 4,
        "email": "player@elite.com",
        "first_name": "Ahmed",
        "last_name": "Player"
      },
      "start_time": "2024-01-25T15:00:00Z",
      "end_time": "2024-01-25T17:00:00Z",
      "total_cost": "300.00",
      "status": "confirmed",
      "notes": "Training session",
      "is_active": true,
      "created_at": "2024-01-20T00:00:00Z"
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
- **Real-time Statistics**: Live academy, player, and field analytics
- **Performance Tracking**: Player and team performance metrics
- **Utilization Reports**: Field usage and booking analytics
- **Trend Analysis**: Monthly growth and performance trends
- **Custom Filtering**: Filter by academy, date range, and specific criteria

### 1. **Academy Overview**
```http
GET /api/v1/analytics/academy_overview/
```

**Success Response (200):**
```json
{
  "total_academies": 5,
  "total_players": 200,
  "total_matches": 150,
  "total_bookings": 500,
  "monthly_growth": {
    "players": 15,
    "matches": 25,
    "bookings": 80
  }
}
```

---

### 2. **Player Performance**
```http
GET /api/v1/analytics/player_performance/
```

**Query Parameters:**
- `player_id`: Specific player ID
- `academy_id`: Filter by academy
- `start_date`: Start date for analysis
- `end_date`: End date for analysis

**Success Response (200):**
```json
{
  "player_id": 1,
  "player_name": "Ahmed Player",
  "performance_metrics": {
    "matches_played": 15,
    "goals_scored": 8,
    "assists": 5,
    "average_rating": 7.5,
    "improvement_trend": "positive"
  },
  "monthly_stats": [
    {
      "month": "2024-01",
      "matches": 5,
      "goals": 3,
      "assists": 2,
      "rating": 7.2
    }
  ]
}
```

---

### 3. **Team Performance**
```http
GET /api/v1/analytics/team_performance/
```

**Success Response (200):**
```json
{
  "team_id": 1,
  "team_name": "U-17 Team",
  "performance_metrics": {
    "matches_played": 20,
    "wins": 12,
    "draws": 5,
    "losses": 3,
    "goals_scored": 35,
    "goals_conceded": 18,
    "win_rate": 60.0
  }
}
```

---

### 4. **Field Utilization**
```http
GET /api/v1/analytics/field_utilization/
```

**Success Response (200):**
```json
{
  "utilization_rate": 75.5,
  "peak_hours": ["15:00", "16:00", "17:00"],
  "most_popular_field": {
    "id": 1,
    "name": "Main Field",
    "bookings_count": 125
  },
  "monthly_trends": [
    {
      "month": "2024-01",
      "utilization": 78.2,
      "bookings": 85
    }
  ]
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

### **Key Features Summary**
- ✅ **Atomic Transactions**: All write operations are transaction-safe
- ✅ **Email Automation**: Complete booking lifecycle email system
- ✅ **Conflict Prevention**: Advanced booking overlap detection
- ✅ **Nested Data**: Academy endpoints return comprehensive object hierarchies
- ✅ **Real-time Analytics**: Live statistics and reporting
- ✅ **Management Commands**: Automated reminder and maintenance tasks
- ✅ **Professional UI**: Responsive email templates and admin interface
- ✅ **Comprehensive Validation**: Robust data validation and error handling

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

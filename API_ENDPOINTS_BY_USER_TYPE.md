# AI Football Platform API - Endpoints by User Type

## 🚀 Overview

This documentation organizes all API endpoints by user type for easy reference. Each user type has specific permissions and access to different sets of endpoints.

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

**Available to all users**

### Authentication & Profile
```http
POST /api/v1/auth/login/                   # Login with email and password
POST /api/v1/auth/refresh/                 # Refresh access token
POST /api/v1/auth/logout/                  # Logout and blacklist token
POST /api/v1/auth/register/                # External client registration
GET /api/v1/auth/profile/                  # Get own profile
PUT /api/v1/auth/profile/                  # Update own profile
PATCH /api/v1/auth/profile/                # Partial update profile
PUT /api/v1/auth/change-password/          # Change password
```

### Notifications
```http
GET /api/v1/notifications/notifications/   # List user notifications
GET /api/v1/notifications/notifications/{id}/ # Get notification details
POST /api/v1/notifications/notifications/{id}/mark_as_read/ # Mark as read
POST /api/v1/notifications/notifications/mark_all_as_read/ # Mark all as read
GET /api/v1/notifications/notifications/unread_count/ # Get unread count
GET /api/v1/notifications/notifications/statistics/ # Notification stats
```

---

## 🔧 System Admin Endpoints

**Full system access - can manage all academies and users**

### Global User Management
```http
GET /api/v1/users/                         # List all users in system
GET /api/v1/users/{id}/                    # Get user details
PUT /api/v1/users/{id}/                    # Update user
DELETE /api/v1/users/{id}/                 # Delete user
POST /api/v1/users/{id}/activate/          # Activate user
POST /api/v1/users/{id}/deactivate/        # Deactivate user
```

### Academy Management
```http
GET /api/v1/academies/                     # List all academies
POST /api/v1/academies/                    # Create new academy
GET /api/v1/academies/{id}/                # Get academy details with all nested data
PUT /api/v1/academies/{id}/                # Update academy
PATCH /api/v1/academies/{id}/              # Partial update academy
DELETE /api/v1/academies/{id}/             # Delete academy
GET /api/v1/academies/{id}/statistics/     # Academy statistics
```

### Global Player/Coach/Parent Management
```http
GET /api/v1/players/playerprofile/         # List all players (all academies)
GET /api/v1/players/coachprofile/          # List all coaches (all academies)
GET /api/v1/players/parentprofile/         # List all parents (all academies)
GET /api/v1/players/team/                  # List all teams (all academies)
```

### Global Analytics
```http
GET /api/v1/analytics/academy_overview/    # System-wide academy overview
GET /api/v1/analytics/player_performance/  # Cross-academy player analytics
GET /api/v1/analytics/team_performance/    # Cross-academy team analytics
GET /api/v1/analytics/field_utilization/   # System-wide field analytics
GET /api/v1/analytics/match_statistics/    # System-wide match analytics
```

### Global Booking Overview
```http
GET /api/v1/fieldbooking/         # View all bookings (all academies)
GET /api/v1/fieldbooking/statistics/ # System booking statistics
```

---

## 🏟️ Academy Admin Endpoints

**Manage specific academy - scoped to their academy only**

### Academy User Registration & Management
```http
POST /api/v1/auth/academy/register-user/   # Register new academy users
GET /api/v1/academy-users/                 # List academy users
GET /api/v1/academy-users/{id}/            # Get academy user details
PUT /api/v1/academy-users/{id}/            # Update academy user
POST /api/v1/academy-users/{id}/activate/  # Activate user
POST /api/v1/academy-users/{id}/deactivate/ # Deactivate user
POST /api/v1/academy-users/{id}/reset_password/ # Reset user password
```

### Academy Profile Management
```http
GET /api/v1/academies/{id}/                # View own academy details
PUT /api/v1/academies/{id}/                # Update own academy
PATCH /api/v1/academies/{id}/              # Partial update academy
```

### Academy Admin Profile Management
```http
GET /api/v1/academies/academy-admins/      # List academy admins
POST /api/v1/academies/academy-admins/     # Create academy admin
GET /api/v1/academies/academy-admins/{id}/ # Get admin details
PUT /api/v1/academies/academy-admins/{id}/ # Update admin
```

### Player Profile Management
```http
GET /api/v1/players/playerprofile/         # List academy players
POST /api/v1/players/playerprofile/        # Create player profile
GET /api/v1/players/playerprofile/{id}/    # Get player details
PUT /api/v1/players/playerprofile/{id}/    # Update player
PATCH /api/v1/players/playerprofile/{id}/  # Partial update player
DELETE /api/v1/players/playerprofile/{id}/ # Delete player
GET /api/v1/players/playerprofile/{id}/statistics/ # Player statistics
POST /api/v1/players/playerprofile/{id}/add_parent/ # Add parent to player
POST /api/v1/players/playerprofile/{id}/remove_parent/ # Remove parent from player
```

### Coach Profile Management
```http
GET /api/v1/players/coachprofile/          # List academy coaches
POST /api/v1/players/coachprofile/         # Create coach profile
GET /api/v1/players/coachprofile/{id}/     # Get coach details
PUT /api/v1/players/coachprofile/{id}/     # Update coach
PATCH /api/v1/players/coachprofile/{id}/   # Partial update coach
DELETE /api/v1/players/coachprofile/{id}/  # Delete coach
GET /api/v1/players/coachprofile/{id}/teams/ # Get coach's teams
GET /api/v1/players/coachprofile/{id}/statistics/ # Coach statistics
```

### Parent Profile Management
```http
GET /api/v1/players/parentprofile/         # List academy parents
POST /api/v1/players/parentprofile/        # Create parent profile
GET /api/v1/players/parentprofile/{id}/    # Get parent details
PUT /api/v1/players/parentprofile/{id}/    # Update parent
PATCH /api/v1/players/parentprofile/{id}/  # Partial update parent
DELETE /api/v1/players/parentprofile/{id}/ # Delete parent
GET /api/v1/players/parentprofile/{id}/children/ # Get parent's children
POST /api/v1/players/parentprofile/{id}/add_child/ # Add child to parent
POST /api/v1/players/parentprofile/{id}/remove_child/ # Remove child from parent
POST /api/v1/players/parentprofile/{id}/set_children/ # Set all children for parent
```

### Team Management
```http
GET /api/v1/players/team/                  # List academy teams
POST /api/v1/players/team/                 # Create team
GET /api/v1/players/team/{id}/             # Get team details
PUT /api/v1/players/team/{id}/             # Update team
PATCH /api/v1/players/team/{id}/           # Partial update team
DELETE /api/v1/players/team/{id}/          # Delete team
GET /api/v1/players/team/{id}/players/     # List team players
POST /api/v1/players/team/{id}/add_player/ # Add player to team
POST /api/v1/players/team/{id}/remove_player/ # Remove player from team
GET /api/v1/players/team/{id}/statistics/  # Team statistics
```

### Field Management
```http
GET /api/v1/field/                # List academy fields
POST /api/v1/field/               # Create field
GET /api/v1/field/{id}/           # Get field details
PUT /api/v1/field/{id}/           # Update field
PATCH /api/v1/field/{id}/         # Partial update field
DELETE /api/v1/field/{id}/        # Delete field
GET /api/v1/field/{id}/availability/ # Check field availability
GET /api/v1/field/{id}/schedule/  # Field schedule
GET /api/v1/field/{id}/utilization/ # Field utilization statistics
```

### Booking Management
```http
GET /api/v1/fieldbooking/         # List academy bookings
GET /api/v1/fieldbooking/{id}/    # Get booking details
PUT /api/v1/fieldbooking/{id}/    # Update booking
POST /api/v1/fieldbooking/{id}/confirm/ # Confirm booking
POST /api/v1/fieldbooking/{id}/cancel/ # Cancel booking
POST /api/v1/fieldbooking/{id}/complete/ # Complete booking
POST /api/v1/fieldbooking/{id}/send_reminder/ # Send reminder
GET /api/v1/fieldbooking/statistics/ # Academy booking statistics
```

### Match Management
```http
GET /api/v1/matches/matches/               # List academy matches
POST /api/v1/matches/matches/              # Create match
GET /api/v1/matches/matches/{id}/          # Get match details
PUT /api/v1/matches/matches/{id}/          # Update match
DELETE /api/v1/matches/matches/{id}/       # Delete match
POST /api/v1/matches/matches/{id}/start_match/ # Start match
POST /api/v1/matches/matches/{id}/end_match/ # End match
POST /api/v1/matches/matches/{id}/cancel_match/ # Cancel match
GET /api/v1/matches/matches/{id}/statistics/ # Match statistics
```

### Academy Analytics
```http
GET /api/v1/analytics/academy_overview/    # Academy overview analytics
GET /api/v1/analytics/player_performance/  # Academy player analytics
GET /api/v1/analytics/team_performance/    # Academy team analytics
GET /api/v1/analytics/field_utilization/   # Academy field analytics
GET /api/v1/analytics/match_statistics/    # Academy match analytics
```

---

## ⚽ Coach Endpoints

**Manage assigned teams and players**

### Profile Management
```http
GET /api/v1/players/coachprofile/{id}/     # View own profile
PUT /api/v1/players/coachprofile/{id}/     # Update own profile
PATCH /api/v1/players/coachprofile/{id}/   # Partial update profile
GET /api/v1/players/coachprofile/{id}/statistics/ # Own statistics
```

### Team Management
```http
GET /api/v1/players/coachprofile/{coach_id}/teams/ # Get assigned teams
GET /api/v1/players/team/{id}/             # View team details
GET /api/v1/players/team/{id}/players/     # List team players
GET /api/v1/players/team/{id}/statistics/  # Team statistics
```

### Player Interaction
```http
GET /api/v1/players/playerprofile/         # View academy players
GET /api/v1/players/playerprofile/{id}/    # View player details
GET /api/v1/players/playerprofile/{id}/statistics/ # Player statistics
```

### Match Management
```http
GET /api/v1/matches/matches/               # View team matches
GET /api/v1/matches/matches/{id}/          # View match details
GET /api/v1/matches/matches/{id}/statistics/ # Match statistics
```

### Field Booking
```http
GET /api/v1/field/                # View available fields
GET /api/v1/field/{id}/availability/ # Check field availability
POST /api/v1/fieldbooking/        # Create booking
GET /api/v1/fieldbooking/my_bookings/ # Own bookings
POST /api/v1/fieldbooking/check_availability/ # Check availability
```

---

## 👤 Player Endpoints

**View profile, matches, and performance data**

### Profile Management
```http
GET /api/v1/players/playerprofile/{id}/    # View own profile
PUT /api/v1/players/playerprofile/{id}/    # Update own profile
PATCH /api/v1/players/playerprofile/{id}/  # Partial update profile
GET /api/v1/players/playerprofile/{id}/statistics/ # Own statistics
GET /api/v1/players/playerprofile/{id}/parents/ # View own parents
```

### Team Information
```http
GET /api/v1/players/team/{id}/             # View team details
GET /api/v1/players/team/{id}/players/     # View teammates
GET /api/v1/players/team/{id}/statistics/  # Team statistics
```

### Match Information
```http
GET /api/v1/matches/matches/               # View own matches
GET /api/v1/matches/matches/{id}/          # View match details
GET /api/v1/matches/matches/{id}/statistics/ # Match statistics
```

### Field Booking
```http
GET /api/v1/field/                # View available fields
GET /api/v1/field/{id}/availability/ # Check field availability
POST /api/v1/fieldbooking/        # Create booking
GET /api/v1/fieldbooking/my_bookings/ # Own bookings
POST /api/v1/fieldbooking/check_availability/ # Check availability
```

---

## 👨‍👩‍👧‍👦 Parent Endpoints

**View children's profiles and progress**

### Profile Management
```http
GET /api/v1/players/parentprofile/{id}/    # View own profile
PUT /api/v1/players/parentprofile/{id}/    # Update own profile
PATCH /api/v1/players/parentprofile/{id}/  # Partial update profile
GET /api/v1/players/parentprofile/{id}/children/ # View own children
```

### Children's Information
```http
GET /api/v1/players/playerprofile/{child_id}/ # View child's profile
GET /api/v1/players/playerprofile/{child_id}/statistics/ # Child's statistics
```

### Team & Match Information (for children)
```http
GET /api/v1/players/team/{id}/             # View child's team
GET /api/v1/players/team/{id}/statistics/  # Team statistics
GET /api/v1/matches/matches/               # View child's matches
GET /api/v1/matches/matches/{id}/          # View match details
GET /api/v1/matches/matches/{id}/statistics/ # Match statistics
```

### Field Booking
```http
GET /api/v1/field/                # View available fields
GET /api/v1/field/{id}/availability/ # Check field availability
POST /api/v1/fieldbooking/        # Create booking
GET /api/v1/fieldbooking/my_bookings/ # Own bookings
POST /api/v1/fieldbooking/check_availability/ # Check availability
```

---

## 🌐 External Client Endpoints

**Book facilities with limited access**

### Field Information
```http
GET /api/v1/field/                # View available fields
GET /api/v1/field/{id}/           # View field details
GET /api/v1/field/{id}/availability/ # Check field availability
GET /api/v1/field/{id}/schedule/  # View field schedule
```

### Booking Management
```http
POST /api/v1/fieldbooking/        # Create booking
GET /api/v1/fieldbooking/my_bookings/ # Own bookings
GET /api/v1/fieldbooking/{id}/    # View own booking details
POST /api/v1/fieldbooking/check_availability/ # Check availability
POST /api/v1/fieldbooking/{id}/cancel/ # Cancel own booking
```

### Academy Information (Limited)
```http
GET /api/v1/academies/                     # View academy list (basic info)
GET /api/v1/academies/{id}/                # View academy details (public info only)
```

---

## 📝 Detailed Request/Response Examples

### **Authentication Examples**

#### Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "admin@academy.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "email": "admin@academy.com",
  "user_type": "academy_admin",
  "profile": {
    "id": 1,
    "position": "Director",
    "bio": "Academy director with 15 years experience"
  }
}
```

#### Register External Client
```http
POST /api/v1/auth/register/
Content-Type: application/json

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

**Response (201):**
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

### **System Admin Examples**

#### List All Users
```http
GET /api/v1/users/?page=1&page_size=10&user_type=coach
Authorization: Bearer <system_admin_token>
```

**Response (200):**
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
      "user_type": "system_admin",
      "is_active": true,
      "date_joined": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Create Academy
```http
POST /api/v1/academies/
Authorization: Bearer <system_admin_token>
Content-Type: application/json

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

**Response (201):**
```json
{
  "id": 2,
  "name": "New Football Academy",
  "name_ar": "أكاديمية كرة القدم الجديدة",
  "description": "A new premier football academy",
  "address": "456 New St, City",
  "phone": "+1987654321",
  "email": "info@newacademy.com",
  "is_active": true,
  "created_at": "2024-01-20T10:00:00Z"
}
```

### **Academy Admin Examples**

#### Register Academy User
```http
POST /api/v1/auth/academy/register-user/
Authorization: Bearer <academy_admin_token>
Content-Type: application/json

{
  "email": "coach@academy.com",
  "password": "secure_password123",
  "first_name": "Jane",
  "last_name": "Coach",
  "user_type": "coach",
  "academy_id": 1,
  "phone": "+1234567890"
}
```

**Response (201):**
```json
{
  "id": 6,
  "email": "coach@academy.com",
  "first_name": "Jane",
  "last_name": "Coach",
  "user_type": "coach",
  "phone": "+1234567890",
  "is_active": true,
  "date_joined": "2024-01-20T10:00:00Z"
}
```

#### Create Player Profile
```http
POST /api/v1/players/playerprofile/
Authorization: Bearer <academy_admin_token>
Content-Type: application/json

{
  "user": {
    "email": "player@academy.com",
    "password": "securepassword123",
    "first_name": "Ahmed",
    "last_name": "Ali",
    "user_type": "player",
    "phone": "+20123456789"
  },
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

**Response (201):**
```json
{
  "id": 2,
  "user": {
    "email": "player@academy.com",
    "password": "securepassword123",
    "first_name": "Ahmed",
    "last_name": "Ali",
    "user_type": "player",
    "phone": "+20123456789"
  },
  "user_email": "player@academy.com",
  "user_name": "Ahmed Ali",
  "academy": 1,
  "academy_name": "Future Stars Academy",
  "jersey_number": 10,
  "position": "Midfielder",
  "height": "175.50",
  "weight": "68.00",
  "dominant_foot": "right",
  "bio": "Talented young midfielder",
  "date_of_birth": "2006-03-15",
  "parents": [],
  "is_active": true,
  "created_at": "2024-01-20T10:00:00Z",
  "updated_at": "2024-01-20T10:00:00Z"
}
```

#### Add Child to Parent
```http
POST /api/v1/players/parentprofile/4/add_child/
Authorization: Bearer <academy_admin_token>
Content-Type: application/json

{
  "player_id": 6
}
```

**Response (200):**
```json
{
  "message": "Child added to parent successfully",
  "parent_id": 4,
  "child_id": 6
}
```

#### Create Team
```http
POST /api/v1/players/team/
Authorization: Bearer <academy_admin_token>
Content-Type: application/json

{
  "academy": 1,
  "coach": 1,
  "name": "U-19 Team",
  "category": "U-19",
  "formation": "4-3-3"
}
```

**Response (201):**
```json
{
  "id": 3,
  "academy": 1,
  "coach": 1,
  "name": "U-19 Team",
  "category": "U-19",
  "formation": "4-3-3",
  "is_active": true,
  "total_players": 0,
  "created_at": "2024-01-20T10:00:00Z"
}
```

#### Create Field
```http
POST /api/v1/field/
Authorization: Bearer <academy_admin_token>
Content-Type: application/json

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

**Response (201):**
```json
{
  "id": 2,
  "academy": 1,
  "name": "Training Field 2",
  "field_type": "training",
  "capacity": 200,
  "hourly_rate": "120.00",
  "facilities": {
    "lights": true,
    "changing_rooms": false,
    "parking": true
  },
  "is_available": true,
  "is_active": true,
  "created_at": "2024-01-20T10:00:00Z"
}
```

### **Player/Coach/Parent Examples**

#### Get Player Statistics
```http
GET /api/v1/players/playerprofile/1/statistics/
Authorization: Bearer <player_token>
```

**Response (200):**
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

#### Get Coach's Teams
```http
GET /api/v1/players/coachprofile/1/teams/
Authorization: Bearer <coach_token>
```

**Response (200):**
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

#### Get Parent's Children
```http
GET /api/v1/players/parentprofile/1/children/
Authorization: Bearer <parent_token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "user": {
      "first_name": "Ahmed",
      "last_name": "Player"
    },
    "position": "Midfielder",
    "jersey_number": 10,
    "team": {
      "id": 1,
      "name": "U-17 Team"
    },
    "statistics": {
      "matches_played": 15,
      "goals_scored": 8
    }
  }
]
```

### **Booking Examples**

#### Check Field Availability
```http
POST /api/v1/fieldbooking/check_availability/
Authorization: Bearer <client_token>
Content-Type: application/json

{
  "field": 1,
  "start_time": "2024-01-25T15:00:00Z",
  "end_time": "2024-01-25T17:00:00Z"
}
```

**Response (200):**
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

#### Create Booking
```http
POST /api/v1/fieldbooking/
Authorization: Bearer <client_token>
Content-Type: application/json

{
  "field": 1,
  "start_time": "2024-01-25T15:00:00Z",
  "end_time": "2024-01-25T17:00:00Z",
  "notes": "Training session"
}
```

**Response (201):**
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

#### Confirm Booking
```http
POST /api/v1/fieldbooking/16/confirm/
Authorization: Bearer <academy_admin_token>
```

**Response (200):**
```json
{
  "message": "Booking confirmed successfully",
  "booking_id": 16,
  "status": "confirmed"
}
```

### **Match Management Examples**

#### Create Match
```http
POST /api/v1/matches/matches/
Authorization: Bearer <academy_admin_token>
Content-Type: application/json

{
  "home_team": 1,
  "away_team": 2,
  "match_type": "friendly",
  "match_date": "2024-01-25T15:00:00Z",
  "venue": 1
}
```

**Response (201):**
```json
{
  "id": 5,
  "home_team": 1,
  "away_team": 2,
  "match_type": "friendly",
  "match_date": "2024-01-25T15:00:00Z",
  "venue": 1,
  "status": "scheduled",
  "home_score": null,
  "away_score": null,
  "is_active": true,
  "created_at": "2024-01-20T10:00:00Z"
}
```

#### End Match
```http
POST /api/v1/matches/matches/5/end_match/
Authorization: Bearer <academy_admin_token>
Content-Type: application/json

{
  "home_score": 2,
  "away_score": 1
}
```

**Response (200):**
```json
{
  "message": "Match ended successfully",
  "match_id": 5,
  "status": "completed",
  "home_score": 2,
  "away_score": 1
}
```

### **Analytics Examples**

#### Academy Overview
```http
GET /api/v1/analytics/academy_overview/
Authorization: Bearer <academy_admin_token>
```

**Response (200):**
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
    "matches_played": 15
  },
  "performance_summary": {
    "overall_win_rate": 68.5,
    "field_utilization": 72.3,
    "revenue_this_month": "12500.00"
  }
}
```

### **Notification Examples**

#### List Notifications
```http
GET /api/v1/notifications/notifications/?is_read=false
Authorization: Bearer <user_token>
```

**Response (200):**
```json
{
  "count": 3,
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

## 📊 Endpoint Summary by User Type

| User Type | Total Endpoints | Management | Viewing | Booking |
|-----------|----------------|------------|---------|---------|
| **System Admin** | 50+ | All academies, users | Global analytics | All bookings |
| **Academy Admin** | 40+ | Academy scope | Academy analytics | Academy bookings |
| **Coach** | 15+ | Assigned teams | Team/player data | Training bookings |
| **Player** | 12+ | Own profile | Team/match data | Personal bookings |
| **Parent** | 12+ | Own profile | Children's data | Family bookings |
| **External Client** | 8+ | None | Field availability | Facility bookings |

---

## 🔐 Permission Matrix

| Endpoint Category | System Admin | Academy Admin | Coach | Player | Parent | External Client |
|------------------|--------------|---------------|--------|--------|--------|-----------------|
| **User Management** | ✅ All | ✅ Academy only | ❌ | ❌ | ❌ | ❌ |
| **Academy Management** | ✅ All | ✅ Own academy | ❌ | ❌ | ❌ | ❌ |
| **Player Profiles** | ✅ All | ✅ Academy only | 👁️ View only | 👁️ Own + team | 👁️ Children only | ❌ |
| **Coach Profiles** | ✅ All | ✅ Academy only | 👁️ Own profile | 👁️ View only | 👁️ View only | ❌ |
| **Parent Profiles** | ✅ All | ✅ Academy only | 👁️ View only | 👁️ Own parents | ✅ Own profile | ❌ |
| **Team Management** | ✅ All | ✅ Academy only | ✅ Assigned teams | 👁️ Own team | 👁️ Children's teams | ❌ |
| **Match Management** | ✅ All | ✅ Academy only | 👁️ Team matches | 👁️ Own matches | 👁️ Children's matches | ❌ |
| **Field Management** | ✅ All | ✅ Academy only | ❌ | ❌ | ❌ | ❌ |
| **Booking Management** | 👁️ All | ✅ Academy only | ✅ Create/view own | ✅ Create/view own | ✅ Create/view own | ✅ Create/view own |
| **Analytics** | ✅ Global | ✅ Academy only | 👁️ Team stats | 👁️ Own stats | 👁️ Children's stats | ❌ |

**Legend:**
- ✅ = Full access (create, read, update, delete)
- 👁️ = Read-only access
- ❌ = No access

---

*This documentation provides a complete overview of all API endpoints organized by user type. For detailed request/response examples and interactive testing, visit `/api/docs/` in your browser.*

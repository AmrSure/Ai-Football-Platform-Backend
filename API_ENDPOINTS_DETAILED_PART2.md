# AI Football Platform API - Academy Admin Endpoints (Part 2)

## 🏟️ Academy Admin Endpoints

**Manage specific academy - scoped to their academy only**

### Academy User Registration & Management

#### 1. **Register New Academy User**
```http
POST /api/v1/auth/academy/register-user/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
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

**Success Response (201):**
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

#### 2. **List Academy Users**
```http
GET /api/v1/academy-users/
Authorization: Bearer <academy_admin_token>
```

**Query Parameters:**
- `search`: Search by email, first name, or last name
- `user_type`: Filter by user type (coach, player, parent)
- `is_active`: Filter by active status

**Success Response (200):**
```json
{
  "count": 25,
  "results": [
    {
      "id": 5,
      "email": "coach@academy.com",
      "first_name": "Jane",
      "last_name": "Coach",
      "full_name": "Jane Coach",
      "user_type": "coach",
      "is_active": true,
      "date_joined": "2024-01-10T00:00:00Z",
      "last_login": "2024-01-20T09:30:00Z"
    },
    {
      "id": 6,
      "email": "player@academy.com",
      "first_name": "Ahmed",
      "last_name": "Player",
      "full_name": "Ahmed Player",
      "user_type": "player",
      "is_active": true,
      "date_joined": "2024-01-12T00:00:00Z",
      "last_login": "2024-01-19T16:45:00Z"
    }
  ]
}
```

#### 3. **Get Academy User Details**
```http
GET /api/v1/academy-users/{id}/
Authorization: Bearer <academy_admin_token>
```

**Success Response (200):**
```json
{
  "id": 5,
  "email": "coach@academy.com",
  "first_name": "Jane",
  "last_name": "Coach",
  "full_name": "Jane Coach",
  "user_type": "coach",
  "phone": "+1234567890",
  "is_active": true,
  "date_joined": "2024-01-10T00:00:00Z",
  "last_login": "2024-01-20T09:30:00Z"
}
```

#### 4. **Update Academy User**
```http
PUT /api/v1/academy-users/{id}/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "phone": "+9876543210",
  "is_active": true
}
```

**Success Response (200):**
```json
{
  "id": 5,
  "first_name": "Updated",
  "last_name": "Name",
  "phone": "+9876543210",
  "is_active": true,
  "updated_at": "2024-01-20T10:00:00Z"
}
```

#### 5. **Activate User**
```http
POST /api/v1/academy-users/{id}/activate/
Authorization: Bearer <academy_admin_token>
```

**Success Response (200):**
```json
{
  "message": "User activated successfully",
  "user_id": 5,
  "is_active": true
}
```

#### 6. **Deactivate User**
```http
POST /api/v1/academy-users/{id}/deactivate/
Authorization: Bearer <academy_admin_token>
```

**Success Response (200):**
```json
{
  "message": "User deactivated successfully",
  "user_id": 5,
  "is_active": false
}
```

#### 7. **Reset User Password**
```http
POST /api/v1/academy-users/{id}/reset_password/
Authorization: Bearer <academy_admin_token>
```

**Success Response (200):**
```json
{
  "message": "Password reset successfully",
  "user_id": 5,
  "new_password": "temp123456"
}
```

### Player Profile Management

#### 1. **List Academy Players**
```http
GET /api/v1/players/playerprofile/
Authorization: Bearer <academy_admin_token>
```

**Query Parameters:**
- `search`: Search by user email, name, position
- `position`: Filter by player position
- `team`: Filter by team ID
- `is_active`: Filter by active status

**Success Response (200):**
```json
{
  "count": 45,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 4,
        "email": "player@academy.com",
        "first_name": "Ahmed",
        "last_name": "Player",
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
      "parents": [
        {
          "id": 1,
          "user": {
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
          "category": "U-17"
        }
      ]
    }
  ]
}
```

#### 2. **Create Player Profile**
```http
POST /api/v1/players/playerprofile/
Authorization: Bearer <academy_admin_token>
```

**Request (with nested user creation):**
```json
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

**Success Response (201):**
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

#### 3. **Get Player Details**
```http
GET /api/v1/players/playerprofile/{id}/
Authorization: Bearer <academy_admin_token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "user": {
    "id": 4,
    "email": "player@academy.com",
    "first_name": "Ahmed",
    "last_name": "Player",
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
      "category": "U-17",
      "formation": "4-4-2"
    }
  ],
  "parents": [
    {
      "id": 1,
      "user": {
        "first_name": "Father",
        "last_name": "Player",
        "email": "parent@academy.com"
      },
      "relationship": "father",
      "phone": "+1234567890"
    }
  ]
}
```

#### 4. **Update Player**
```http
PUT /api/v1/players/playerprofile/{id}/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "jersey_number": 11,
  "position": "Forward",
  "height": "180.00",
  "weight": "70.00",
  "bio": "Updated player bio"
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "jersey_number": 11,
  "position": "Forward",
  "height": "180.00",
  "weight": "70.00",
  "bio": "Updated player bio",
  "updated_at": "2024-01-20T10:00:00Z"
}
```

#### 5. **Delete Player**
```http
DELETE /api/v1/players/playerprofile/{id}/
Authorization: Bearer <academy_admin_token>
```

**Success Response (204):** No Content

#### 6. **Player Statistics**
```http
GET /api/v1/players/playerprofile/{id}/statistics/
Authorization: Bearer <academy_admin_token>
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
  "performance_trend": "improving",
  "position": "Midfielder",
  "team": "U-17 Team"
}
```

#### 7. **Add Parent to Player**
```http
POST /api/v1/players/playerprofile/{id}/add_parent/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "parent_id": 2
}
```

**Success Response (200):**
```json
{
  "message": "Parent added to player successfully",
  "player_id": 1,
  "parent_id": 2
}
```

#### 8. **Remove Parent from Player**
```http
POST /api/v1/players/playerprofile/{id}/remove_parent/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "parent_id": 2
}
```

**Success Response (200):**
```json
{
  "message": "Parent removed from player successfully",
  "player_id": 1,
  "parent_id": 2
}
```

### Coach Profile Management

#### 1. **List Academy Coaches**
```http
GET /api/v1/players/coachprofile/
Authorization: Bearer <academy_admin_token>
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
        "email": "coach@academy.com",
        "first_name": "John",
        "last_name": "Coach",
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

#### 2. **Create Coach Profile**
```http
POST /api/v1/players/coachprofile/
Authorization: Bearer <academy_admin_token>
```

**Request (with nested user creation):**
```json
{
  "user": {
    "email": "coach@academy.com",
    "password": "securepassword123",
    "first_name": "Ahmed",
    "last_name": "Hassan",
    "user_type": "coach",
    "phone": "+20123456789"
  },
  "academy": 1,
  "specialization": "Youth Development",
  "experience_years": 8,
  "certification": "UEFA B License",
  "bio": "Specialist in youth player development",
  "date_of_birth": "1985-08-10"
}
```

**Success Response (201):**
```json
{
  "id": 2,
  "user": {
    "email": "coach@academy.com",
    "password": "securepassword123",
    "first_name": "Ahmed",
    "last_name": "Hassan",
    "user_type": "coach",
    "phone": "+20123456789"
  },
  "user_email": "coach@academy.com",
  "user_name": "Ahmed Hassan",
  "academy": 1,
  "academy_name": "Future Stars Academy",
  "specialization": "Youth Development",
  "experience_years": 8,
  "certification": "UEFA B License",
  "bio": "Specialist in youth player development",
  "date_of_birth": "1985-08-10",
  "is_active": true,
  "created_at": "2024-01-20T10:00:00Z",
  "updated_at": "2024-01-20T10:00:00Z"
}
```

#### 3. **Get Coach Details**
```http
GET /api/v1/players/coachprofile/{id}/
Authorization: Bearer <academy_admin_token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "user": {
    "id": 3,
    "email": "coach@academy.com",
    "first_name": "John",
    "last_name": "Coach",
    "user_type": "coach"
  },
  "academy": 1,
  "specialization": "Youth Development",
  "experience_years": 8,
  "certification": "UEFA B License",
  "bio": "Specialist in youth player development with focus on technical skills",
  "date_of_birth": "1985-08-10",
  "age": 39,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "teams": [
    {
      "id": 1,
      "name": "U-17 Team",
      "category": "U-17",
      "total_players": 18
    },
    {
      "id": 2,
      "name": "U-19 Team",
      "category": "U-19",
      "total_players": 20
    }
  ]
}
```

#### 4. **Get Coach's Teams**
```http
GET /api/v1/players/coachprofile/{id}/teams/
Authorization: Bearer <academy_admin_token>
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "name": "U-17 Team",
    "category": "U-17",
    "formation": "4-4-2",
    "total_players": 18,
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "name": "U-19 Team",
    "category": "U-19",
    "formation": "4-3-3",
    "total_players": 20,
    "created_at": "2024-01-02T00:00:00Z"
  }
]
```

#### 5. **Coach Statistics**
```http
GET /api/v1/players/coachprofile/{id}/statistics/
Authorization: Bearer <academy_admin_token>
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
  "player_development_success": 85.5,
  "specialization": "Youth Development",
  "experience_years": 8
}
```

### Parent Profile Management

#### 1. **List Academy Parents**
```http
GET /api/v1/players/parentprofile/
Authorization: Bearer <academy_admin_token>
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
        "email": "parent@academy.com",
        "first_name": "Father",
        "last_name": "Player",
        "user_type": "parent"
      },
      "relationship": "father",
      "bio": "Supportive parent",
      "date_of_birth": "1980-05-20",
      "age": 44,
      "is_active": true,
      "children_count": 1,
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

#### 2. **Create Parent Profile**
```http
POST /api/v1/players/parentprofile/
Authorization: Bearer <academy_admin_token>
```

**Request (with nested user creation):**
```json
{
  "user": {
    "email": "parent@example.com",
    "password": "securepassword123",
    "first_name": "Fatima",
    "last_name": "Ali",
    "user_type": "parent",
    "phone": "+20123456789"
  },
  "relationship": "mother",
  "bio": "Supportive parent committed to child's development",
  "date_of_birth": "1980-12-05",
  "children": [1]
}
```

**Success Response (201):**
```json
{
  "id": 2,
  "user": {
    "email": "parent@example.com",
    "password": "securepassword123",
    "first_name": "Fatima",
    "last_name": "Ali",
    "user_type": "parent",
    "phone": "+20123456789"
  },
  "user_email": "parent@example.com",
  "user_name": "Fatima Ali",
  "relationship": "mother",
  "bio": "Supportive parent committed to child's development",
  "date_of_birth": "1980-12-05",
  "children": [1],
  "children_details": [
    {
      "id": 1,
      "user": {
        "id": 4,
        "email": "player@academy.com",
        "first_name": "Ahmed",
        "last_name": "Player",
        "full_name": "Ahmed Player"
      },
      "academy": "Future Stars Academy",
      "jersey_number": 10,
      "position": "Midfielder",
      "is_active": true
    }
  ],
  "children_count": 1,
  "is_active": true,
  "created_at": "2024-01-20T10:00:00Z",
  "updated_at": "2024-01-20T10:00:00Z"
}
```

#### 3. **Get Parent Details**
```http
GET /api/v1/players/parentprofile/{id}/
Authorization: Bearer <academy_admin_token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "user": {
    "id": 5,
    "email": "parent@academy.com",
    "first_name": "Father",
    "last_name": "Player",
    "user_type": "parent"
  },
  "relationship": "father",
  "bio": "Supportive parent who attends all matches",
  "date_of_birth": "1980-05-20",
  "age": 44,
  "is_active": true,
  "children_count": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "children_details": [
    {
      "id": 1,
      "user": {
        "first_name": "Ahmed",
        "last_name": "Player",
        "email": "player@academy.com"
      },
      "position": "Midfielder",
      "jersey_number": 10,
      "team": "U-17 Team"
    }
  ]
}
```

#### 4. **Get Parent's Children**
```http
GET /api/v1/players/parentprofile/{id}/children/
Authorization: Bearer <academy_admin_token>
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "user": {
      "id": 4,
      "email": "player@academy.com",
      "first_name": "Ahmed",
      "last_name": "Player"
    },
    "position": "Midfielder",
    "jersey_number": 10,
    "team": {
      "id": 1,
      "name": "U-17 Team",
      "category": "U-17"
    },
    "statistics": {
      "matches_played": 15,
      "goals_scored": 8,
      "assists": 5
    }
  }
]
```

#### 5. **Add Child to Parent**
```http
POST /api/v1/players/parentprofile/{id}/add_child/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "player_id": 6
}
```

**Success Response (200):**
```json
{
  "message": "Child added to parent successfully",
  "parent_id": 4,
  "child_id": 6
}
```

#### 6. **Remove Child from Parent**
```http
POST /api/v1/players/parentprofile/{id}/remove_child/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "player_id": 6
}
```

**Success Response (200):**
```json
{
  "message": "Child removed from parent successfully",
  "parent_id": 4,
  "child_id": 6
}
```

#### 7. **Set All Children for Parent**
```http
POST /api/v1/players/parentprofile/{id}/set_children/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "children_ids": [6, 8, 10]
}
```

**Success Response (200):**
```json
{
  "message": "Children set for parent successfully",
  "parent_id": 4,
  "children_ids": [6, 8, 10],
  "children_count": 3
}
```

---

*Continue to Part 3 for Team Management, Field Management, Booking Management, Match Management, and Analytics endpoints...*

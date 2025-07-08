# Dashboard Stats Endpoint Documentation

## 📊 Overview

The Dashboard Stats endpoint provides auto-detection of user type and returns appropriate statistics based on whether the user is a **system admin**, **academy admin**, or **coach**. This endpoint is designed to power dashboard interfaces with relevant metrics for different user roles.

## 🎯 Endpoint Details

```
GET /api/v1/dashboardstats/
```

- **Authentication**: Required (JWT Bearer Token)
- **Permissions**: `system_admin`, `academy_admin`, or `coach` only
- **Method**: GET
- **Content-Type**: application/json

## 🔐 Auto-Detection Logic

The endpoint automatically detects the user type from the authenticated user's profile and returns appropriate statistics:

- **System Admin**: Returns system-wide statistics across all academies
- **Academy Admin**: Returns statistics scoped to their specific academy
- **Coach**: Returns statistics related to their teams, players, and matches
- **Other User Types**: Returns 403 Forbidden error

## 📈 Response Format

### For System Admin

**Request:**
```http
GET /api/v1/dashboardstats/
Authorization: Bearer <system_admin_jwt_token>
```

**Response (200 OK):**
```json
{
  "user_type": "system_admin",
  "academies_count": 15,
  "coaches_count": 45,
  "players_count": 320,
  "parents_count": 280,
  "external_clients_count": 125,
  "fields_count": 38,
  "bookings_count": 1850
}
```

### For Academy Admin

**Request:**
```http
GET /api/v1/dashboardstats/
Authorization: Bearer <academy_admin_jwt_token>
```

**Response (200 OK):**
```json
{
  "user_type": "academy_admin",
  "academy_id": 3,
  "academy_name": "Elite Football Academy",
  "coaches_count": 12,
  "players_count": 180,
  "parents_count": 160,
  "external_clients_count": 45,
  "fields_count": 8,
  "bookings_count": 450
}
```

### For Coach

**Request:**
```http
GET /api/v1/dashboardstats/
Authorization: Bearer <coach_jwt_token>
```

**Response (200 OK):**
```json
{
  "user_type": "coach",
  "academy_id": 3,
  "academy_name": "Elite Football Academy",
  "teams_count": 2,
  "players_count": 45,
  "matches_count": 28
}
```

## ❌ Error Responses

### Unauthorized (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Forbidden (403)
```json
{
  "error": "User does not have required role"
}
```

## 📊 Statistics Explained

### System Admin Statistics

| Field | Description |
|-------|-------------|
| `academies_count` | Total number of active academies in the system |
| `coaches_count` | Total number of active coaches across all academies |
| `players_count` | Total number of active players across all academies |
| `parents_count` | Total number of active parents across all academies |
| `external_clients_count` | Total number of active external clients |
| `fields_count` | Total number of active fields across all academies |
| `bookings_count` | Total number of active bookings across all academies |

### Academy Admin Statistics

| Field | Description |
|-------|-------------|
| `academy_id` | ID of the admin's academy |
| `academy_name` | Name of the admin's academy |
| `coaches_count` | Number of active coaches in this academy |
| `players_count` | Number of active players in this academy |
| `parents_count` | Number of unique active parents of players in this academy |
| `external_clients_count` | Number of unique external clients who have bookings at this academy |
| `fields_count` | Number of active fields in this academy |
| `bookings_count` | Number of active bookings for fields in this academy |

### Coach Statistics

| Field | Description |
|-------|-------------|
| `academy_id` | ID of the coach's academy |
| `academy_name` | Name of the coach's academy |
| `teams_count` | Number of active teams coached by this coach |
| `players_count` | Total number of active players across all teams coached by this coach |
| `matches_count` | Total number of matches involving teams coached by this coach |

## 🔧 Implementation Features

### Clean Code Principles
- **Single Responsibility**: Each method handles one specific user type
- **Auto-Detection**: Automatically determines user type without manual parameters
- **Error Handling**: Comprehensive error handling for edge cases
- **Logging**: Proper logging for monitoring and debugging
- **Documentation**: Full Swagger/OpenAPI documentation

### Performance Optimizations
- **Efficient Queries**: Uses optimized database queries with proper filtering
- **Active Records Only**: Only counts active records to provide accurate statistics
- **Set-Based Counting**: Uses Python sets for unique counting where needed

### Security Features
- **Authentication Required**: JWT token required for all requests
- **Role-Based Access**: Only system and academy admins can access
- **Academy Scoping**: Academy admins only see their own academy data
- **Profile Validation**: Validates user profile and academy associations

## 🧪 Testing

### Test with cURL

**System Admin:**
```bash
curl -X GET \
  http://localhost:8000/api/v1/dashboardstats/ \
  -H "Authorization: Bearer <system_admin_token>" \
  -H "Content-Type: application/json"
```

**Academy Admin:**
```bash
curl -X GET \
  http://localhost:8000/api/v1/dashboardstats/ \
  -H "Authorization: Bearer <academy_admin_token>" \
  -H "Content-Type: application/json"
```

**Coach:**
```bash
curl -X GET \
  http://localhost:8000/api/v1/dashboardstats/ \
  -H "Authorization: Bearer <coach_token>" \
  -H "Content-Type: application/json"
```

### Test Script

Use the provided `test_dashboard_endpoint.py` script:

```bash
python test_dashboard_endpoint.py
```

## 🔗 Integration

### Frontend Integration

**React/JavaScript Example:**
```javascript
const fetchDashboardStats = async () => {
  try {
    const response = await fetch('/api/v1/dashboardstats/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const stats = await response.json();
      // Auto-detected user type and appropriate stats
      console.log('User Type:', stats.user_type);
      console.log('Statistics:', stats);
    } else {
      console.error('Failed to fetch dashboard stats');
    }
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### API Documentation

The endpoint is automatically documented in:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

## 🚀 Usage Examples

### Dashboard Component Logic

```javascript
const DashboardStats = ({ userType, stats }) => {
  if (userType === 'system_admin') {
    return (
      <div className="system-admin-dashboard">
        <StatCard title="Academies" value={stats.academies_count} />
        <StatCard title="Total Coaches" value={stats.coaches_count} />
        <StatCard title="Total Players" value={stats.players_count} />
        <StatCard title="Total Parents" value={stats.parents_count} />
        <StatCard title="External Clients" value={stats.external_clients_count} />
        <StatCard title="Total Fields" value={stats.fields_count} />
        <StatCard title="Total Bookings" value={stats.bookings_count} />
      </div>
    );
  }

  if (userType === 'academy_admin') {
    return (
      <div className="academy-admin-dashboard">
        <h2>{stats.academy_name} Dashboard</h2>
        <StatCard title="Coaches" value={stats.coaches_count} />
        <StatCard title="Players" value={stats.players_count} />
        <StatCard title="Parents" value={stats.parents_count} />
        <StatCard title="External Clients" value={stats.external_clients_count} />
        <StatCard title="Fields" value={stats.fields_count} />
        <StatCard title="Bookings" value={stats.bookings_count} />
      </div>
    );
  }

  if (userType === 'coach') {
    return (
      <div className="coach-dashboard">
        <h2>{stats.academy_name} Dashboard</h2>
        <StatCard title="Teams" value={stats.teams_count} />
        <StatCard title="Players" value={stats.players_count} />
        <StatCard title="Matches" value={stats.matches_count} />
      </div>
    );
  }

  return <div>Access Denied</div>;
};
```

## ✨ Benefits

1. **Auto-Detection**: No need to manually specify user type in frontend
2. **Clean Separation**: Different statistics for different user roles
3. **Secure**: Role-based access control with proper validation
4. **Efficient**: Optimized database queries for performance
5. **Scalable**: Easy to extend with additional user types or statistics
6. **Well-Documented**: Comprehensive API documentation and examples

## 🔄 Future Enhancements

Potential future improvements:
- **Caching**: Add Redis caching for frequently accessed statistics
- **Time Ranges**: Add date range parameters for historical statistics
- **Filters**: Add filtering options for more granular statistics
- **Real-time**: Add WebSocket support for real-time dashboard updates
- **Export**: Add export functionality for statistics data

# External Client Dashboard Statistics

## 📊 Overview

The External Client Dashboard Statistics endpoint provides comprehensive booking history and analytics for external clients. This endpoint automatically detects when an external client is accessing the dashboard and returns personalized statistics about their booking activity, spending patterns, and favorite academies.

## 🎯 Endpoint Details

```
GET /api/v1/dashboardstats/
```

- **Authentication**: Required (JWT Bearer Token)
- **Permissions**: `external_client` only (auto-detected)
- **Method**: GET
- **Content-Type**: application/json

## 🔐 Auto-Detection Logic

The endpoint automatically detects the user type from the authenticated user's profile:
- **External Client**: Returns booking history and personal statistics
- **Other User Types**: Returns appropriate stats for their role (system admin, academy admin, coach)

## 📈 Response Format

### For External Client

**Request:**
```http
GET /api/v1/dashboardstats/
Authorization: Bearer <external_client_jwt_token>
```

**Response (200 OK):**
```json
{
  "user_type": "external_client",
  "user_id": 15,
  "user_email": "client@company.com",
  "user_name": "Ahmed Ali",
  "total_bookings": 25,
  "upcoming_bookings": 3,
  "completed_bookings": 18,
  "cancelled_bookings": 2,
  "pending_bookings": 1,
  "confirmed_bookings": 21,
  "total_spent": "3750.00",
  "average_booking_cost": "150.00",
  "favorite_academies": [
    {
      "academy_name": "Elite Football Academy",
      "bookings_count": 12
    },
    {
      "academy_name": "Sports Complex Cairo",
      "bookings_count": 8
    },
    {
      "academy_name": "Youth Development Center",
      "bookings_count": 5
    }
  ],
  "recent_bookings": [
    {
      "id": 45,
      "field_name": "Main Football Field",
      "academy_name": "Elite Football Academy",
      "start_time": "2024-01-27T14:00:00Z",
      "end_time": "2024-01-27T16:00:00Z",
      "status": "confirmed",
      "total_cost": "300.00",
      "created_at": "2024-01-25T15:30:00Z"
    },
    {
      "id": 44,
      "field_name": "Indoor Training Field",
      "academy_name": "Sports Complex Cairo",
      "start_time": "2024-01-26T10:00:00Z",
      "end_time": "2024-01-26T12:00:00Z",
      "status": "completed",
      "total_cost": "200.00",
      "created_at": "2024-01-24T10:15:00Z"
    },
    {
      "id": 43,
      "field_name": "Outdoor Field 1",
      "academy_name": "Youth Development Center",
      "start_time": "2024-01-25T16:00:00Z",
      "end_time": "2024-01-25T18:00:00Z",
      "status": "completed",
      "total_cost": "250.00",
      "created_at": "2024-01-23T14:20:00Z"
    },
    {
      "id": 42,
      "field_name": "Main Football Field",
      "academy_name": "Elite Football Academy",
      "start_time": "2024-01-24T15:00:00Z",
      "end_time": "2024-01-24T17:00:00Z",
      "status": "completed",
      "total_cost": "300.00",
      "created_at": "2024-01-22T11:45:00Z"
    },
    {
      "id": 41,
      "field_name": "Training Field A",
      "academy_name": "Sports Complex Cairo",
      "start_time": "2024-01-23T09:00:00Z",
      "end_time": "2024-01-23T11:00:00Z",
      "status": "completed",
      "total_cost": "180.00",
      "created_at": "2024-01-21T16:30:00Z"
    }
  ],
  "booking_status_distribution": {
    "pending": 1,
    "confirmed": 21,
    "completed": 18,
    "cancelled": 2
  },
  "member_since": "2023-06-15T10:30:00Z",
  "last_booking_date": "2024-01-25T15:30:00Z"
}
```

## 📊 Statistics Explained

### Basic User Information

| Field | Description |
|-------|-------------|
| `user_type` | Always "external_client" for this user type |
| `user_id` | Unique identifier for the external client |
| `user_email` | Email address of the external client |
| `user_name` | Full name of the external client |

### Booking Statistics

| Field | Description |
|-------|-------------|
| `total_bookings` | Total number of bookings made by this client |
| `upcoming_bookings` | Number of future bookings (pending or confirmed) |
| `completed_bookings` | Number of completed bookings |
| `cancelled_bookings` | Number of cancelled bookings |
| `pending_bookings` | Number of pending bookings |
| `confirmed_bookings` | Number of confirmed bookings |

### Financial Statistics

| Field | Description |
|-------|-------------|
| `total_spent` | Total amount spent on confirmed and completed bookings |
| `average_booking_cost` | Average cost per booking |

### Academy Preferences

| Field | Description |
|-------|-------------|
| `favorite_academies` | Array of top 3 academies by booking count |
| `academy_name` | Name of the academy |
| `bookings_count` | Number of bookings at this academy |

### Recent Activity

| Field | Description |
|-------|-------------|
| `recent_bookings` | Array of last 5 bookings with details |
| `booking_status_distribution` | Breakdown of bookings by status |
| `member_since` | Date when the client joined the platform |
| `last_booking_date` | Date of the most recent booking |

## 🎯 Use Cases

### 1. Dashboard Overview
External clients can see a comprehensive overview of their booking activity:
- Total bookings and spending
- Upcoming bookings
- Favorite academies
- Recent activity

### 2. Financial Tracking
Track spending patterns and costs:
- Total amount spent
- Average booking cost
- Cost breakdown by academy

### 3. Booking History
View detailed booking history:
- Recent bookings with full details
- Booking status distribution
- Academy preferences

### 4. Activity Monitoring
Monitor booking activity over time:
- Member since date
- Last booking date
- Booking frequency patterns

## 🔧 Implementation Features

### Clean Code Principles
- **Single Responsibility**: Dedicated method for external client statistics
- **Auto-Detection**: Automatically determines user type without manual parameters
- **Error Handling**: Comprehensive error handling for edge cases
- **Logging**: Proper logging for monitoring and debugging
- **Documentation**: Full Swagger/OpenAPI documentation

### Performance Optimizations
- **Efficient Queries**: Uses optimized database queries with proper filtering
- **Select Related**: Uses `select_related` to minimize database hits
- **Aggregation**: Uses Django aggregation for financial calculations
- **Set-Based Counting**: Uses Python sets for unique counting where needed

### Security Features
- **Authentication Required**: JWT token required for all requests
- **User Scoping**: External clients only see their own booking data
- **Profile Validation**: Validates user profile and associations

## 🧪 Testing

### Test with cURL

**External Client:**
```bash
curl -X GET \
  http://localhost:8000/api/v1/dashboardstats/ \
  -H "Authorization: Bearer <external_client_token>" \
  -H "Content-Type: application/json"
```

### Expected Response Structure
```json
{
  "user_type": "external_client",
  "user_id": 15,
  "user_email": "client@company.com",
  "user_name": "Ahmed Ali",
  "total_bookings": 25,
  "upcoming_bookings": 3,
  "completed_bookings": 18,
  "cancelled_bookings": 2,
  "pending_bookings": 1,
  "confirmed_bookings": 21,
  "total_spent": "3750.00",
  "average_booking_cost": "150.00",
  "favorite_academies": [...],
  "recent_bookings": [...],
  "booking_status_distribution": {...},
  "member_since": "2023-06-15T10:30:00Z",
  "last_booking_date": "2024-01-25T15:30:00Z"
}
```

## 🔗 Frontend Integration

### React/JavaScript Example

```javascript
const ExternalClientDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
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
          const data = await response.json();
          setStats(data);
        } else {
          setError('Failed to fetch dashboard stats');
        }
      } catch (error) {
        setError('Error fetching dashboard stats');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardStats();
  }, []);

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!stats) return <div>No data available</div>;

  return (
    <div className="external-client-dashboard">
      <h1>Welcome, {stats.user_name}!</h1>

      {/* Overview Cards */}
      <div className="stats-grid">
        <StatCard
          title="Total Bookings"
          value={stats.total_bookings}
          icon="calendar"
        />
        <StatCard
          title="Upcoming Bookings"
          value={stats.upcoming_bookings}
          icon="clock"
          color="blue"
        />
        <StatCard
          title="Total Spent"
          value={`$${stats.total_spent}`}
          icon="dollar"
          color="green"
        />
        <StatCard
          title="Average Cost"
          value={`$${stats.average_booking_cost}`}
          icon="chart"
        />
      </div>

      {/* Favorite Academies */}
      <div className="favorite-academies">
        <h2>Favorite Academies</h2>
        <div className="academy-list">
          {stats.favorite_academies.map((academy, index) => (
            <div key={index} className="academy-card">
              <h3>{academy.academy_name}</h3>
              <p>{academy.bookings_count} bookings</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Bookings */}
      <div className="recent-bookings">
        <h2>Recent Bookings</h2>
        <div className="booking-list">
          {stats.recent_bookings.map((booking) => (
            <div key={booking.id} className="booking-card">
              <div className="booking-header">
                <h3>{booking.field_name}</h3>
                <span className={`status ${booking.status}`}>
                  {booking.status}
                </span>
              </div>
              <p>{booking.academy_name}</p>
              <p>
                {new Date(booking.start_time).toLocaleDateString()} -
                {new Date(booking.start_time).toLocaleTimeString()}
              </p>
              <p className="cost">${booking.total_cost}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Booking Status Distribution */}
      <div className="status-distribution">
        <h2>Booking Status</h2>
        <div className="status-chart">
          {Object.entries(stats.booking_status_distribution).map(([status, count]) => (
            <div key={status} className="status-item">
              <span className="status-label">{status}</span>
              <span className="status-count">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color = "default" }) => (
  <div className={`stat-card ${color}`}>
    <div className="stat-icon">{icon}</div>
    <div className="stat-content">
      <h3>{title}</h3>
      <p className="stat-value">{value}</p>
    </div>
  </div>
);
```

### Vue.js Example

```vue
<template>
  <div class="external-client-dashboard">
    <h1>Welcome, {{ stats?.user_name }}!</h1>

    <!-- Overview Cards -->
    <div class="stats-grid">
      <StatCard
        title="Total Bookings"
        :value="stats?.total_bookings"
        icon="calendar"
      />
      <StatCard
        title="Upcoming Bookings"
        :value="stats?.upcoming_bookings"
        icon="clock"
        color="blue"
      />
      <StatCard
        title="Total Spent"
        :value="`$${stats?.total_spent}`"
        icon="dollar"
        color="green"
      />
      <StatCard
        title="Average Cost"
        :value="`$${stats?.average_booking_cost}`"
        icon="chart"
      />
    </div>

    <!-- Favorite Academies -->
    <div class="favorite-academies">
      <h2>Favorite Academies</h2>
      <div class="academy-list">
        <div
          v-for="academy in stats?.favorite_academies"
          :key="academy.academy_name"
          class="academy-card"
        >
          <h3>{{ academy.academy_name }}</h3>
          <p>{{ academy.bookings_count }} bookings</p>
        </div>
      </div>
    </div>

    <!-- Recent Bookings -->
    <div class="recent-bookings">
      <h2>Recent Bookings</h2>
      <div class="booking-list">
        <div
          v-for="booking in stats?.recent_bookings"
          :key="booking.id"
          class="booking-card"
        >
          <div class="booking-header">
            <h3>{{ booking.field_name }}</h3>
            <span :class="`status ${booking.status}`">
              {{ booking.status }}
            </span>
          </div>
          <p>{{ booking.academy_name }}</p>
          <p>{{ formatDateTime(booking.start_time) }}</p>
          <p class="cost">${{ booking.total_cost }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import StatCard from './StatCard.vue';

export default {
  name: 'ExternalClientDashboard',
  components: {
    StatCard
  },
  setup() {
    const stats = ref(null);
    const loading = ref(true);
    const error = ref(null);

    const fetchDashboardStats = async () => {
      try {
        const response = await fetch('/api/v1/dashboardstats/', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          stats.value = data;
        } else {
          error.value = 'Failed to fetch dashboard stats';
        }
      } catch (err) {
        error.value = 'Error fetching dashboard stats';
      } finally {
        loading.value = false;
      }
    };

    const formatDateTime = (dateTimeString) => {
      const date = new Date(dateTimeString);
      return `${date.toLocaleDateString()} - ${date.toLocaleTimeString()}`;
    };

    onMounted(() => {
      fetchDashboardStats();
    });

    return {
      stats,
      loading,
      error,
      formatDateTime
    };
  }
};
</script>
```

## 🚀 Usage Examples

### Dashboard Component Logic

```javascript
const ExternalClientDashboard = ({ stats }) => {
  if (!stats) return <div>Loading...</div>;

  return (
    <div className="external-client-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1>Welcome back, {stats.user_name}!</h1>
        <p>Member since {new Date(stats.member_since).toLocaleDateString()}</p>
      </div>

      {/* Quick Stats */}
      <div className="quick-stats">
        <StatCard title="Total Bookings" value={stats.total_bookings} />
        <StatCard title="Upcoming" value={stats.upcoming_bookings} color="blue" />
        <StatCard title="Total Spent" value={`$${stats.total_spent}`} color="green" />
        <StatCard title="Avg. Cost" value={`$${stats.average_booking_cost}`} />
      </div>

      {/* Favorite Academies */}
      <div className="favorite-academies">
        <h2>Your Favorite Academies</h2>
        <div className="academy-grid">
          {stats.favorite_academies.map((academy, index) => (
            <div key={index} className="academy-card">
              <h3>{academy.academy_name}</h3>
              <p>{academy.bookings_count} bookings</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Bookings */}
      <div className="recent-bookings">
        <h2>Recent Bookings</h2>
        <div className="booking-list">
          {stats.recent_bookings.map((booking) => (
            <BookingCard key={booking.id} booking={booking} />
          ))}
        </div>
      </div>

      {/* Status Distribution */}
      <div className="status-chart">
        <h2>Booking Status Overview</h2>
        <div className="status-bars">
          {Object.entries(stats.booking_status_distribution).map(([status, count]) => (
            <div key={status} className="status-bar">
              <span className="status-label">{status}</span>
              <div className="status-bar-fill" style={{width: `${(count/stats.total_bookings)*100}%`}} />
              <span className="status-count">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
```

## ✨ Benefits

1. **Personalized Experience**: Shows relevant statistics for external clients
2. **Comprehensive Overview**: Provides complete booking history and patterns
3. **Financial Tracking**: Helps clients track their spending
4. **Academy Preferences**: Shows favorite academies for quick access
5. **Recent Activity**: Displays recent bookings for quick reference
6. **Status Tracking**: Shows booking status distribution
7. **Auto-Detection**: No need to manually specify user type
8. **Secure**: Only shows data for the authenticated user

## 🔄 Future Enhancements

Potential future improvements:
- **Time Range Filters**: Add date range parameters for historical analysis
- **Export Functionality**: Allow clients to export their booking history
- **Notifications**: Show upcoming booking reminders
- **Recommendations**: Suggest academies based on preferences
- **Analytics**: Add booking patterns and trends analysis
- **Real-time Updates**: Add WebSocket support for live updates
- **Mobile Optimization**: Optimize for mobile dashboard viewing

## 📱 Mobile Considerations

### Responsive Design
```css
.external-client-dashboard {
  padding: 1rem;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }

  .academy-list {
    flex-direction: column;
  }

  .booking-list {
    grid-template-columns: 1fr;
  }
}
```

### Touch-Friendly Interface
- Large touch targets for mobile users
- Swipe gestures for booking history
- Collapsible sections for better mobile experience
- Optimized loading states for slower connections

This comprehensive dashboard provides external clients with all the information they need to track their booking activity, spending patterns, and preferences in an easy-to-understand format.

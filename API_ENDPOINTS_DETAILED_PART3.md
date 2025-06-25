# AI Football Platform API - Field & Booking Management (Part 3)

## 🏟️ Field Management Endpoints

**Academy Admin permissions required - scoped to their academy only**

### 1. **List Academy Fields**
```http
GET /api/v1/field/
Authorization: Bearer <academy_admin_token>
```

**Query Parameters:**
- `search`: Search by field name, type, or academy name
- `field_type`: Filter by field type (football, basketball, volleyball, tennis)
- `is_available`: Filter by availability status
- `is_active`: Filter by active status
- `page`: Page number
- `page_size`: Items per page

**Success Response (200):**
```json
{
  "count": 5,
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
        "email": "info@elite.com",
        "phone": "+1234567890"
      },
      "name": "Main Football Field",
      "field_type": "football",
      "capacity": 500,
      "hourly_rate": "150.00",
      "facilities": {
        "lights": true,
        "changing_rooms": true,
        "parking": true,
        "seating": true,
        "scoreboard": true
      },
      "is_available": true,
      "is_active": true,
      "booking_count": 45,
      "next_available_slot": "2024-01-25T15:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "academy": 1,
      "academy_name": "Elite Football Academy",
      "academy_details": {
        "id": 1,
        "name": "Elite Football Academy",
        "email": "info@elite.com",
        "phone": "+1234567890"
      },
      "name": "Training Field A",
      "field_type": "football",
      "capacity": 200,
      "hourly_rate": "100.00",
      "facilities": {
        "lights": true,
        "changing_rooms": false,
        "parking": true,
        "seating": false,
        "scoreboard": false
      },
      "is_available": true,
      "is_active": true,
      "booking_count": 28,
      "next_available_slot": "2024-01-25T14:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-10T08:15:00Z"
    }
  ]
}
```

### 2. **Create New Field**
```http
POST /api/v1/field/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "academy": 1,
  "name": "Training Field B",
  "field_type": "football",
  "capacity": 150,
  "hourly_rate": "80.00",
  "facilities": {
    "lights": true,
    "changing_rooms": false,
    "parking": true,
    "seating": false,
    "scoreboard": false,
    "artificial_grass": true,
    "water_fountain": true
  },
  "is_available": true
}
```

**Success Response (201):**
```json
{
  "id": 6,
  "academy": 1,
  "academy_name": "Elite Football Academy",
  "academy_details": {
    "id": 1,
    "name": "Elite Football Academy",
    "email": "info@elite.com",
    "phone": "+1234567890"
  },
  "name": "Training Field B",
  "field_type": "football",
  "capacity": 150,
  "hourly_rate": "80.00",
  "facilities": {
    "lights": true,
    "changing_rooms": false,
    "parking": true,
    "seating": false,
    "scoreboard": false,
    "artificial_grass": true,
    "water_fountain": true
  },
  "is_available": true,
  "is_active": true,
  "booking_count": 0,
  "next_available_slot": null,
  "created_at": "2024-01-20T10:00:00Z",
  "updated_at": "2024-01-20T10:00:00Z"
}
```

### 3. **Get Field Details**
```http
GET /api/v1/field/{id}/
Authorization: Bearer <academy_admin_token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "academy": 1,
  "academy_name": "Elite Football Academy",
  "academy_details": {
    "id": 1,
    "name": "Elite Football Academy",
    "name_ar": "أكاديمية النخبة لكرة القدم",
    "description": "Premier football training academy",
    "address": "123 Sports St, City",
    "phone": "+1234567890",
    "email": "info@elite.com",
    "website": "https://elite.com"
  },
  "name": "Main Football Field",
  "field_type": "football",
  "capacity": 500,
  "hourly_rate": "150.00",
  "facilities": {
    "lights": true,
    "changing_rooms": true,
    "parking": true,
    "seating": true,
    "scoreboard": true,
    "artificial_grass": false,
    "water_fountain": true,
    "first_aid": true
  },
  "is_available": true,
  "is_active": true,
  "booking_count": 45,
  "next_available_slot": "2024-01-25T15:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "upcoming_bookings": [
    {
      "id": 23,
      "start_time": "2024-01-25T15:00:00Z",
      "end_time": "2024-01-25T17:00:00Z",
      "booked_by": "Ahmed Player",
      "status": "confirmed",
      "total_cost": "300.00"
    },
    {
      "id": 24,
      "start_time": "2024-01-25T18:00:00Z",
      "end_time": "2024-01-25T20:00:00Z",
      "booked_by": "John Coach",
      "status": "pending",
      "total_cost": "300.00"
    }
  ],
  "monthly_utilization": {
    "total_hours_available": 744,
    "total_hours_booked": 320,
    "utilization_rate": 43.0,
    "revenue_generated": "48000.00"
  }
}
```

### 4. **Update Field**
```http
PUT /api/v1/field/{id}/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "name": "Main Football Stadium",
  "field_type": "football",
  "capacity": 600,
  "hourly_rate": "180.00",
  "facilities": {
    "lights": true,
    "changing_rooms": true,
    "parking": true,
    "seating": true,
    "scoreboard": true,
    "artificial_grass": true,
    "water_fountain": true,
    "first_aid": true,
    "vip_section": true
  },
  "is_available": true
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "academy": 1,
  "name": "Main Football Stadium",
  "field_type": "football",
  "capacity": 600,
  "hourly_rate": "180.00",
  "facilities": {
    "lights": true,
    "changing_rooms": true,
    "parking": true,
    "seating": true,
    "scoreboard": true,
    "artificial_grass": true,
    "water_fountain": true,
    "first_aid": true,
    "vip_section": true
  },
  "is_available": true,
  "is_active": true,
  "updated_at": "2024-01-20T10:00:00Z"
}
```

### 5. **Delete Field**
```http
DELETE /api/v1/field/{id}/
Authorization: Bearer <academy_admin_token>
```

**Success Response (204):** No Content

### 6. **Check Field Availability**
```http
GET /api/v1/field/{id}/availability/
Authorization: Bearer <academy_admin_token>
```

**Query Parameters:**
- `start_date`: Start date for availability check (YYYY-MM-DD)
- `end_date`: End date for availability check (YYYY-MM-DD)
- `start_time`: Start time for specific day (HH:MM)
- `end_time`: End time for specific day (HH:MM)

**Example:**
```http
GET /api/v1/field/1/availability/?start_date=2024-01-25&end_date=2024-01-27&start_time=15:00&end_time=17:00
```

**Success Response (200):**
```json
{
  "field_id": 1,
  "field_name": "Main Football Field",
  "availability_check": {
    "start_date": "2024-01-25",
    "end_date": "2024-01-27",
    "requested_time": "15:00-17:00"
  },
  "availability": [
    {
      "date": "2024-01-25",
      "is_available": false,
      "reason": "Already booked",
      "conflicting_booking": {
        "id": 23,
        "start_time": "15:00:00",
        "end_time": "17:00:00",
        "booked_by": "Ahmed Player"
      }
    },
    {
      "date": "2024-01-26",
      "is_available": true,
      "reason": "Available for booking"
    },
    {
      "date": "2024-01-27",
      "is_available": true,
      "reason": "Available for booking"
    }
  ],
  "next_available_slots": [
    {
      "date": "2024-01-25",
      "available_times": [
        "09:00-11:00",
        "11:00-13:00",
        "13:00-15:00",
        "17:00-19:00",
        "19:00-21:00"
      ]
    },
    {
      "date": "2024-01-26",
      "available_times": [
        "09:00-11:00",
        "11:00-13:00",
        "13:00-15:00",
        "15:00-17:00",
        "17:00-19:00",
        "19:00-21:00"
      ]
    }
  ]
}
```

### 7. **Get Field Schedule**
```http
GET /api/v1/field/{id}/schedule/
Authorization: Bearer <academy_admin_token>
```

**Query Parameters:**
- `date`: Specific date (YYYY-MM-DD)
- `week`: Week number
- `month`: Month number (1-12)
- `year`: Year (YYYY)

**Example:**
```http
GET /api/v1/field/1/schedule/?date=2024-01-25
```

**Success Response (200):**
```json
{
  "field_id": 1,
  "field_name": "Main Football Field",
  "schedule_date": "2024-01-25",
  "daily_schedule": [
    {
      "time_slot": "09:00-11:00",
      "status": "available",
      "booking": null
    },
    {
      "time_slot": "11:00-13:00",
      "status": "available",
      "booking": null
    },
    {
      "time_slot": "13:00-15:00",
      "status": "available",
      "booking": null
    },
    {
      "time_slot": "15:00-17:00",
      "status": "booked",
      "booking": {
        "id": 23,
        "booked_by": "Ahmed Player",
        "booked_by_email": "player@academy.com",
        "status": "confirmed",
        "total_cost": "300.00",
        "notes": "Team training session"
      }
    },
    {
      "time_slot": "17:00-19:00",
      "status": "available",
      "booking": null
    },
    {
      "time_slot": "18:00-20:00",
      "status": "booked",
      "booking": {
        "id": 24,
        "booked_by": "John Coach",
        "booked_by_email": "coach@academy.com",
        "status": "pending",
        "total_cost": "300.00",
        "notes": "Private coaching session"
      }
    },
    {
      "time_slot": "20:00-22:00",
      "status": "available",
      "booking": null
    }
  ],
  "summary": {
    "total_slots": 7,
    "booked_slots": 2,
    "available_slots": 5,
    "utilization_rate": 28.6,
    "daily_revenue": "600.00"
  }
}
```

### 8. **Get Field Utilization Statistics**
```http
GET /api/v1/field/{id}/utilization/
Authorization: Bearer <academy_admin_token>
```

**Query Parameters:**
- `period`: Time period (daily, weekly, monthly, yearly)
- `start_date`: Start date for statistics
- `end_date`: End date for statistics

**Example:**
```http
GET /api/v1/field/1/utilization/?period=monthly&start_date=2024-01-01&end_date=2024-01-31
```

**Success Response (200):**
```json
{
  "field_id": 1,
  "field_name": "Main Football Field",
  "period": "monthly",
  "date_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "utilization_stats": {
    "total_hours_available": 744,
    "total_hours_booked": 320,
    "total_bookings": 45,
    "utilization_rate": 43.0,
    "average_booking_duration": 7.1,
    "peak_hours": ["15:00-17:00", "18:00-20:00"],
    "least_busy_hours": ["09:00-11:00", "21:00-23:00"]
  },
  "revenue_stats": {
    "total_revenue": "48000.00",
    "average_revenue_per_booking": "1066.67",
    "average_revenue_per_hour": "150.00",
    "projected_monthly_revenue": "52000.00"
  },
  "booking_trends": [
    {
      "week": 1,
      "bookings": 8,
      "revenue": "8400.00",
      "utilization": 32.0
    },
    {
      "week": 2,
      "bookings": 12,
      "revenue": "13200.00",
      "utilization": 48.0
    },
    {
      "week": 3,
      "bookings": 15,
      "revenue": "16800.00",
      "utilization": 56.0
    },
    {
      "week": 4,
      "bookings": 10,
      "revenue": "9600.00",
      "utilization": 38.0
    }
  ],
  "user_distribution": {
    "internal_bookings": {
      "count": 28,
      "percentage": 62.2,
      "revenue": "29600.00"
    },
    "external_bookings": {
      "count": 17,
      "percentage": 37.8,
      "revenue": "18400.00"
    }
  }
}
```

---

## 📅 Booking Management Endpoints

**Academy Admin permissions - can manage bookings for their academy's fields**

### 1. **List Academy Bookings**
```http
GET /api/v1/fieldbooking/
Authorization: Bearer <academy_admin_token>
```

**Query Parameters:**
- `search`: Search by field name, booked by name/email
- `status`: Filter by booking status (pending, confirmed, cancelled, completed)
- `field`: Filter by specific field ID
- `start_date`: Filter bookings from this date
- `end_date`: Filter bookings until this date
- `booked_by_type`: Filter by user type (coach, player, parent, external_client)
- `page`: Page number
- `page_size`: Items per page

**Success Response (200):**
```json
{
  "count": 35,
  "next": "http://api/v1/fieldbooking/?page=2",
  "previous": null,
  "results": [
    {
      "id": 23,
      "field": 1,
      "field_name": "Main Football Field",
      "field_details": {
        "id": 1,
        "name": "Main Football Field",
        "field_type": "football",
        "capacity": 500,
        "hourly_rate": "150.00"
      },
      "booked_by": 4,
      "booked_by_name": "Ahmed Player",
      "booked_by_email": "player@academy.com",
      "booked_by_details": {
        "id": 4,
        "email": "player@academy.com",
        "first_name": "Ahmed",
        "last_name": "Player",
        "user_type": "player",
        "phone": "+1234567890"
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
      "created_at": "2024-01-20T10:00:00Z",
      "updated_at": "2024-01-20T10:30:00Z"
    },
    {
      "id": 24,
      "field": 1,
      "field_name": "Main Football Field",
      "field_details": {
        "id": 1,
        "name": "Main Football Field",
        "field_type": "football",
        "capacity": 500,
        "hourly_rate": "150.00"
      },
      "booked_by": 5,
      "booked_by_name": "John Coach",
      "booked_by_email": "coach@academy.com",
      "booked_by_details": {
        "id": 5,
        "email": "coach@academy.com",
        "first_name": "John",
        "last_name": "Coach",
        "user_type": "coach",
        "phone": "+1234567891"
      },
      "academy_name": "Elite Football Academy",
      "start_time": "2024-01-25T18:00:00Z",
      "end_time": "2024-01-25T20:00:00Z",
      "duration_hours": 2.0,
      "total_cost": "300.00",
      "status": "pending",
      "notes": "Private coaching session",
      "match": null,
      "can_cancel": true,
      "can_modify": true,
      "created_at": "2024-01-20T11:00:00Z",
      "updated_at": "2024-01-20T11:00:00Z"
    }
  ]
}
```

### 2. **Get Booking Details**
```http
GET /api/v1/fieldbooking/{id}/
Authorization: Bearer <academy_admin_token>
```

**Success Response (200):**
```json
{
  "id": 23,
  "field": 1,
  "field_name": "Main Football Field",
  "field_details": {
    "id": 1,
    "name": "Main Football Field",
    "academy": 1,
    "academy_name": "Elite Football Academy",
    "field_type": "football",
    "capacity": 500,
    "hourly_rate": "150.00",
    "facilities": {
      "lights": true,
      "changing_rooms": true,
      "parking": true,
      "seating": true,
      "scoreboard": true
    }
  },
  "booked_by": 4,
  "booked_by_name": "Ahmed Player",
  "booked_by_email": "player@academy.com",
  "booked_by_details": {
    "id": 4,
    "email": "player@academy.com",
    "first_name": "Ahmed",
    "last_name": "Player",
    "full_name": "Ahmed Player",
    "user_type": "player",
    "phone": "+1234567890",
    "is_active": true
  },
  "academy_name": "Elite Football Academy",
  "start_time": "2024-01-25T15:00:00Z",
  "end_time": "2024-01-25T17:00:00Z",
  "duration_hours": 2.0,
  "total_cost": "300.00",
  "status": "confirmed",
  "notes": "Team training session - U17 squad",
  "match": null,
  "can_cancel": true,
  "can_modify": true,
  "created_at": "2024-01-20T10:00:00Z",
  "updated_at": "2024-01-20T10:30:00Z",
  "payment_details": {
    "payment_method": "internal",
    "payment_status": "paid",
    "invoice_number": "INV-2024-001-023"
  },
  "booking_history": [
    {
      "action": "created",
      "timestamp": "2024-01-20T10:00:00Z",
      "performed_by": "Ahmed Player",
      "details": "Booking created for team training"
    },
    {
      "action": "confirmed",
      "timestamp": "2024-01-20T10:30:00Z",
      "performed_by": "Academy Admin",
      "details": "Booking confirmed by academy admin"
    }
  ]
}
```

### 3. **Update Booking**
```http
PUT /api/v1/fieldbooking/{id}/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "start_time": "2024-01-25T16:00:00Z",
  "end_time": "2024-01-25T18:00:00Z",
  "total_cost": "300.00",
  "status": "confirmed",
  "notes": "Team training session - Updated time"
}
```

**Success Response (200):**
```json
{
  "id": 23,
  "field": 1,
  "start_time": "2024-01-25T16:00:00Z",
  "end_time": "2024-01-25T18:00:00Z",
  "duration_hours": 2.0,
  "total_cost": "300.00",
  "status": "confirmed",
  "notes": "Team training session - Updated time",
  "updated_at": "2024-01-20T12:00:00Z"
}
```

### 4. **Confirm Booking**
```http
POST /api/v1/fieldbooking/{id}/confirm/
Authorization: Bearer <academy_admin_token>
```

**Request (Optional):**
```json
{
  "confirmation_notes": "Booking confirmed - payment received",
  "send_confirmation_email": true
}
```

**Success Response (200):**
```json
{
  "message": "Booking confirmed successfully",
  "booking_id": 23,
  "status": "confirmed",
  "confirmation_time": "2024-01-20T12:00:00Z",
  "email_sent": true
}
```

### 5. **Cancel Booking**
```http
POST /api/v1/fieldbooking/{id}/cancel/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "cancellation_reason": "Academy event - field needed for tournament",
  "refund_amount": "300.00",
  "send_cancellation_email": true
}
```

**Success Response (200):**
```json
{
  "message": "Booking cancelled successfully",
  "booking_id": 23,
  "status": "cancelled",
  "cancellation_time": "2024-01-20T12:00:00Z",
  "refund_amount": "300.00",
  "email_sent": true
}
```

### 6. **Complete Booking**
```http
POST /api/v1/fieldbooking/{id}/complete/
Authorization: Bearer <academy_admin_token>
```

**Request (Optional):**
```json
{
  "completion_notes": "Session completed successfully",
  "actual_end_time": "2024-01-25T17:00:00Z",
  "send_completion_email": true
}
```

**Success Response (200):**
```json
{
  "message": "Booking completed successfully",
  "booking_id": 23,
  "status": "completed",
  "completion_time": "2024-01-25T17:00:00Z",
  "email_sent": true
}
```

### 7. **Send Booking Reminder**
```http
POST /api/v1/fieldbooking/{id}/send_reminder/
Authorization: Bearer <academy_admin_token>
```

**Request (Optional):**
```json
{
  "reminder_message": "Reminder: Your training session is tomorrow at 3 PM",
  "reminder_hours_before": 24
}
```

**Success Response (200):**
```json
{
  "message": "Reminder sent successfully",
  "booking_id": 23,
  "recipient": "player@academy.com",
  "reminder_sent_at": "2024-01-24T15:00:00Z"
}
```

### 8. **Check Booking Availability**
```http
POST /api/v1/fieldbooking/check_availability/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "field": 1,
  "start_time": "2024-01-26T15:00:00Z",
  "end_time": "2024-01-26T17:00:00Z"
}
```

**Success Response (200):**
```json
{
  "available": true,
  "field_id": 1,
  "field_name": "Main Football Field",
  "requested_time": {
    "start_time": "2024-01-26T15:00:00Z",
    "end_time": "2024-01-26T17:00:00Z",
    "duration_hours": 2.0
  },
  "estimated_cost": "300.00",
  "conflicts": [],
  "alternative_slots": []
}
```

**Conflict Response (200):**
```json
{
  "available": false,
  "field_id": 1,
  "field_name": "Main Football Field",
  "requested_time": {
    "start_time": "2024-01-25T15:00:00Z",
    "end_time": "2024-01-25T17:00:00Z",
    "duration_hours": 2.0
  },
  "estimated_cost": "300.00",
  "conflicts": [
    {
      "booking_id": 23,
      "booked_by": "Ahmed Player",
      "start_time": "2024-01-25T15:00:00Z",
      "end_time": "2024-01-25T17:00:00Z",
      "status": "confirmed"
    }
  ],
  "alternative_slots": [
    {
      "start_time": "2024-01-25T13:00:00Z",
      "end_time": "2024-01-25T15:00:00Z",
      "estimated_cost": "300.00"
    },
    {
      "start_time": "2024-01-25T17:00:00Z",
      "end_time": "2024-01-25T19:00:00Z",
      "estimated_cost": "300.00"
    },
    {
      "start_time": "2024-01-26T15:00:00Z",
      "end_time": "2024-01-26T17:00:00Z",
      "estimated_cost": "300.00"
    }
  ]
}
```

### 9. **Academy Booking Statistics**
```http
GET /api/v1/fieldbooking/statistics/
Authorization: Bearer <academy_admin_token>
```

**Query Parameters:**
- `start_date`: Start date for statistics (YYYY-MM-DD)
- `end_date`: End date for statistics (YYYY-MM-DD)
- `field`: Specific field ID (optional)
- `period`: Grouping period (daily, weekly, monthly)

**Example:**
```http
GET /api/v1/fieldbooking/statistics/?start_date=2024-01-01&end_date=2024-01-31&period=weekly
```

**Success Response (200):**
```json
{
  "academy_id": 1,
  "academy_name": "Elite Football Academy",
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "grouping": "weekly"
  },
  "overall_statistics": {
    "total_bookings": 145,
    "confirmed_bookings": 120,
    "pending_bookings": 15,
    "cancelled_bookings": 8,
    "completed_bookings": 102,
    "total_revenue": "125600.00",
    "average_booking_value": "866.21",
    "total_hours_booked": 837,
    "average_booking_duration": 5.77
  },
  "field_statistics": [
    {
      "field_id": 1,
      "field_name": "Main Football Field",
      "bookings": 85,
      "revenue": "75200.00",
      "hours_booked": 501,
      "utilization_rate": 67.3
    },
    {
      "field_id": 2,
      "field_name": "Training Field A",
      "bookings": 45,
      "revenue": "35400.00",
      "hours_booked": 236,
      "utilization_rate": 31.7
    },
    {
      "field_id": 3,
      "field_name": "Training Field B",
      "bookings": 15,
      "revenue": "15000.00",
      "hours_booked": 100,
      "utilization_rate": 13.4
    }
  ],
  "weekly_trends": [
    {
      "week": 1,
      "week_start": "2024-01-01",
      "bookings": 32,
      "revenue": "28800.00",
      "utilization": 45.2
    },
    {
      "week": 2,
      "week_start": "2024-01-08",
      "bookings": 38,
      "revenue": "33600.00",
      "utilization": 53.6
    },
    {
      "week": 3,
      "week_start": "2024-01-15",
      "bookings": 45,
      "revenue": "38400.00",
      "utilization": 61.2
    },
    {
      "week": 4,
      "week_start": "2024-01-22",
      "bookings": 30,
      "revenue": "24800.00",
      "utilization": 42.8
    }
  ],
  "user_type_breakdown": {
    "internal_users": {
      "coach": {
        "bookings": 45,
        "revenue": "38200.00",
        "percentage": 31.0
      },
      "player": {
        "bookings": 35,
        "revenue": "28600.00",
        "percentage": 24.1
      },
      "parent": {
        "bookings": 20,
        "revenue": "18400.00",
        "percentage": 13.8
      }
    },
    "external_clients": {
      "bookings": 45,
      "revenue": "40400.00",
      "percentage": 31.0
    }
  },
  "peak_hours": [
    {
      "hour": "15:00-16:00",
      "bookings": 25,
      "percentage": 17.2
    },
    {
      "hour": "16:00-17:00",
      "bookings": 28,
      "percentage": 19.3
    },
    {
      "hour": "17:00-18:00",
      "bookings": 23,
      "percentage": 15.9
    }
  ],
  "payment_statistics": {
    "total_paid": "118200.00",
    "total_pending": "7400.00",
    "payment_methods": {
      "internal": "78800.00",
      "credit_card": "32400.00",
      "cash": "14400.00"
    }
  }
}
```

---

## 🚀 Advanced Features

### **Bulk Operations**

#### 1. **Bulk Update Field Availability**
```http
POST /api/v1/field/bulk_update_availability/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "field_ids": [1, 2, 3],
  "is_available": false,
  "reason": "Maintenance period",
  "start_date": "2024-02-01",
  "end_date": "2024-02-03"
}
```

#### 2. **Bulk Booking Confirmation**
```http
POST /api/v1/fieldbooking/bulk_confirm/
Authorization: Bearer <academy_admin_token>
```

**Request:**
```json
{
  "booking_ids": [23, 24, 25, 26],
  "confirmation_notes": "Monthly bookings confirmed",
  "send_emails": true
}
```

### **Export & Reporting**

#### 1. **Export Booking Data**
```http
GET /api/v1/fieldbooking/export/
Authorization: Bearer <academy_admin_token>
```

**Query Parameters:**
- `format`: Export format (csv, excel, pdf)
- `start_date`: Start date
- `end_date`: End date
- `fields`: Comma-separated field IDs

#### 2. **Generate Revenue Report**
```http
GET /api/v1/fieldbooking/revenue_report/
Authorization: Bearer <academy_admin_token>
```

**Query Parameters:**
- `period`: Report period (monthly, quarterly, yearly)
- `year`: Report year
- `format`: Report format (json, pdf)

---

## 🔔 Notification & Email Features

### **Automated Notifications:**
- ✅ **Booking Confirmation** - Email sent when booking is confirmed
- ✅ **Booking Reminder** - Automatic reminders before booking time
- ✅ **Cancellation Notice** - Email sent when booking is cancelled
- ✅ **Completion Confirmation** - Email sent when session is completed
- ✅ **Payment Reminders** - For external clients with pending payments

### **Admin Notifications:**
- ✅ **New Booking Alert** - Academy admin notified of new external bookings
- ✅ **Cancellation Alert** - Admin notified of cancelled bookings
- ✅ **Revenue Milestone** - Alerts when revenue targets are reached
- ✅ **Field Utilization** - Alerts for low/high utilization rates

---

## ⚠️ Error Responses

### **Common Error Scenarios:**

#### **Field Not Found (404):**
```json
{
  "detail": "Not found.",
  "error_code": "FIELD_NOT_FOUND"
}
```

#### **Booking Conflict (400):**
```json
{
  "error": "Booking conflict detected",
  "error_code": "BOOKING_CONFLICT",
  "details": {
    "conflicting_booking": {
      "id": 23,
      "start_time": "2024-01-25T15:00:00Z",
      "end_time": "2024-01-25T17:00:00Z"
    }
  }
}
```

#### **Insufficient Permissions (403):**
```json
{
  "detail": "You do not have permission to perform this action.",
  "error_code": "PERMISSION_DENIED"
}
```

#### **Validation Error (400):**
```json
{
  "start_time": ["This field is required."],
  "end_time": ["End time must be after start time."],
  "field": ["Field must belong to your academy."]
}
```

---

This comprehensive documentation covers all Field Management and Booking Management endpoints for Academy Admins, providing complete control over their academy's facilities and booking operations while maintaining proper access control and academy scope isolation.

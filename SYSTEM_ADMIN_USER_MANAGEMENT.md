# 🔧 System Admin User Management - Complete Guide

## Overview
System administrators have **full system access** and can manage all users across all academies in the platform. They use dedicated endpoints with comprehensive CRUD operations and advanced filtering capabilities.

## 🚀 User Management Endpoints

### Base URL
```
/api/v1/users/
```

### Authentication
- **Type**: JWT Bearer Token
- **Header**: `Authorization: Bearer <system_admin_token>`
- **Required Permission**: `system_admin` user type

---

## 📋 1. LIST ALL USERS

### Endpoint
```http
GET /api/v1/users/
```

### Query Parameters
- `search`: Search by email, first name, or last name
- `user_type`: Filter by user type (system_admin, academy_admin, coach, player, parent, external_client)
- `is_active`: Filter by active status (true/false)
- `page`: Page number for pagination
- `page_size`: Items per page (default: 20)

### Response Fields
- `id`: Unique user identifier
- `email`: User's email address
- `first_name`: User's first name
- `last_name`: User's last name
- `full_name`: Computed full name (first_name + last_name)
- `user_type`: User role in the system
- `is_active`: Whether the user account is active
- `date_joined`: When the user account was created
- `last_login`: Last time the user logged in (null if never logged in)

### Request Example
```http
GET /api/v1/users/?search=john&user_type=coach&is_active=true&page=1&page_size=10
Authorization: Bearer <system_admin_token>
```

### Response Example (200)
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
      "last_login": "2024-01-20T10:30:00Z",
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

---

## 🔍 2. GET USER DETAILS

### Endpoint
```http
GET /api/v1/users/{id}/
```

### Request Example
```http
GET /api/v1/users/1/
Authorization: Bearer <system_admin_token>
```

### Response Example (200)
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

## ➕ 3. CREATE NEW USER

### Endpoint
```http
POST /api/v1/users/
```

### Request Body
```json
{
  "email": "newuser@example.com",
  "password": "secure_password123",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "coach"
}
```

### Request Example
```http
POST /api/v1/users/
Authorization: Bearer <system_admin_token>
Content-Type: application/json

{
  "email": "coach@newacademy.com",
  "password": "secure_password123",
  "first_name": "Jane",
  "last_name": "Coach",
  "user_type": "coach"
}
```

### Response Example (201)
```json
{
  "id": 25,
  "email": "coach@newacademy.com",
  "first_name": "Jane",
  "last_name": "Coach",
  "full_name": "Jane Coach",
  "user_type": "coach",
  "is_active": true,
  "date_joined": "2024-01-20T10:00:00Z",
  "last_login": null
}
```

---

## ✏️ 4. UPDATE USER

### Endpoint
```http
PUT /api/v1/users/{id}/
```

### Request Body
```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "is_active": true
}
```

### Request Example
```http
PUT /api/v1/users/25/
Authorization: Bearer <system_admin_token>
Content-Type: application/json

{
  "first_name": "Updated",
  "last_name": "Name",
  "phone": "+1987654321",
  "is_active": true
}
```

### Response Example (200)
```json
{
  "id": 25,
  "email": "coach@newacademy.com",
  "first_name": "Updated",
  "last_name": "Name",
  "full_name": "Updated Name",
  "user_type": "coach",
  "is_active": true,
  "date_joined": "2024-01-20T10:00:00Z",
  "last_login": null
}
```

---

## 🔄 5. PARTIAL UPDATE USER

### Endpoint
```http
PATCH /api/v1/users/{id}/
```

### Request Body
```json
{
  "is_active": false
}
```

### Request Example
```http
PATCH /api/v1/users/25/
Authorization: Bearer <system_admin_token>
Content-Type: application/json

{
  "phone": "+1122334455"
}
```

### Response Example (200)
```json
{
  "id": 25,
  "email": "coach@newacademy.com",
  "first_name": "Updated",
  "last_name": "Name",
  "full_name": "Updated Name",
  "user_type": "coach",
  "is_active": true,
  "date_joined": "2024-01-20T10:00:00Z",
  "last_login": null
}
```

---

## 🗑️ 6. DELETE USER

### Endpoint
```http
DELETE /api/v1/users/{id}/
```

### Request Example
```http
DELETE /api/v1/users/25/
Authorization: Bearer <system_admin_token>
```

### Response Example (204)
```
No Content
```

---

## ✅ 7. ACTIVATE USER

### Endpoint
```http
POST /api/v1/users/{id}/activate/
```

### Request Example
```http
POST /api/v1/users/25/activate/
Authorization: Bearer <system_admin_token>
```

### Response Example (200)
```json
{
  "status": "User activated"
}
```

---

## ❌ 8. DEACTIVATE USER

### Endpoint
```http
POST /api/v1/users/{id}/deactivate/
```

### Request Example
```http
POST /api/v1/users/25/deactivate/
Authorization: Bearer <system_admin_token>
```

### Response Example (200)
```json
{
  "status": "User deactivated"
}
```

---

## 🔐 9. RESET USER PASSWORD

### Endpoint
```http
POST /api/v1/users/{id}/reset_password/
```

### Request Body
```json
{
  "new_password": "new_secure_password123"
}
```

### Request Example
```http
POST /api/v1/users/25/reset_password/
Authorization: Bearer <system_admin_token>
Content-Type: application/json

{
  "new_password": "new_secure_password123"
}
```

### Response Example (200)
```json
{
  "status": "Password reset successful"
}
```

---

## 🛡️ Security & Permissions

### Permission Classes
- **`IsSystemAdmin`**: Only system administrators can access these endpoints
- **`IsAuthenticated`**: User must be authenticated with valid JWT token

### User Type Restrictions
- System admins can manage **ALL user types**:
  - `system_admin`
  - `academy_admin`
  - `coach`
  - `player`
  - `parent`
  - `external_client`

### Data Validation
- Email uniqueness validation
- Password complexity requirements
- User type validation against predefined choices
- Required field validation

---

## 📊 Advanced Features

### Search & Filtering
- **Text Search**: Search across email, first name, and last name
- **Type Filtering**: Filter by specific user types
- **Status Filtering**: Filter by active/inactive status
- **Pagination**: Configurable page size and navigation

### Error Handling
- **400 Bad Request**: Validation errors, missing required fields
- **401 Unauthorized**: Invalid or missing authentication token
- **403 Forbidden**: User lacks system admin permissions
- **404 Not Found**: User ID doesn't exist
- **500 Internal Server Error**: Server-side errors

### Logging & Audit
- All user management actions are logged
- Audit trail for compliance and security
- User activity tracking

---

## 🔄 User Lifecycle Management

### 1. **User Creation**
- System admin creates user with initial credentials
- User profile is automatically created based on user type
- User receives welcome email with login credentials

### 2. **User Activation/Deactivation**
- System admin can activate/deactivate users without deletion
- Deactivated users cannot log in but data is preserved
- Useful for temporary suspensions or account management

### 3. **User Updates**
- System admin can update any user field except user_type
- Changes are immediately reflected across the system
- Profile relationships are maintained

### 4. **User Deletion**
- Permanent removal of user and associated data
- Cannot be undone
- Use deactivation for temporary removal instead

---

## 💡 Best Practices

### 1. **User Creation**
- Always set strong initial passwords
- Verify email addresses before activation
- Assign appropriate user types based on role

### 2. **User Management**
- Use deactivation instead of deletion for temporary suspensions
- Regularly review user permissions and access levels
- Monitor user activity and login patterns

### 3. **Security**
- Regularly rotate system admin credentials
- Use strong authentication tokens
- Monitor for suspicious user management activities

### 4. **Data Integrity**
- Validate all user data before creation/updates
- Maintain referential integrity across related models
- Use atomic transactions for complex operations

---

## 🔗 Related Endpoints

### Academy Management
- **List Academies**: `GET /api/v1/academies/`
- **Create Academy**: `POST /api/v1/academies/`
- **Academy Details**: `GET /api/v1/academies/{id}/`
- **Update Academy**: `PUT /api/v1/academies/{id}/`
- **Delete Academy**: `DELETE /api/v1/academies/{id}/`

### Global Analytics
- **System Overview**: `GET /api/v1/analytics/academy_overview/`
- **Player Performance**: `GET /api/v1/analytics/player_performance/`
- **Team Performance**: `GET /api/v1/analytics/team_performance/`
- **Field Utilization**: `GET /api/v1/analytics/field_utilization/`

---

## 📝 Implementation Notes

### Technology Stack
- **Framework**: Django REST Framework
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: PostgreSQL with polymorphic models
- **Permissions**: Custom permission classes
- **Serialization**: Nested serializers for profile data

### Code Structure
- **Views**: `UserViewSet` in `apps/accounts/views.py`
- **Serializers**: `BaseUserSerializer` in `apps/core/serializers.py`
- **Permissions**: `IsSystemAdmin` in `apps/core/permissions.py`
- **Models**: `User` model in `apps/core/models.py`
- **URLs**: Routed in `apps/accounts/urls.py`

### Key Features
- **Polymorphic Profiles**: Different profile types for different user types
- **Atomic Transactions**: Database operations are atomic
- **Comprehensive Logging**: All actions are logged for audit
- **Flexible Filtering**: Advanced search and filter capabilities
- **Role-Based Access**: Strict permission controls

---

## 🚨 Important Notes

### ⚠️ Warnings
- **User Deletion**: Cannot be undone - use deactivation instead
- **Password Management**: System admins can reset any user's password
- **Profile Relationships**: Deleting users affects related data
- **Permission Escalation**: Only system admins can create other system admins

### 🔒 Security Considerations
- **Token Security**: JWT tokens should be stored securely
- **Password Policy**: Enforce strong password requirements
- **Access Logging**: Monitor all administrative actions
- **Session Management**: Implement proper token expiration

### 📊 Performance Considerations
- **Pagination**: Use pagination for large user lists
- **Database Indexing**: Ensure proper indexing on search fields
- **Caching**: Consider caching for frequently accessed user data
- **Query Optimization**: Use select_related for profile data

---

## 📞 Support & Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure user has system_admin role
2. **User Not Found**: Verify user ID exists in database
3. **Validation Errors**: Check required fields and data format
4. **Token Expired**: Refresh JWT token if expired

### Debug Information
- Check Django logs for detailed error messages
- Verify user permissions in admin interface
- Test endpoints with Postman or similar tools
- Review database constraints and relationships

---

This comprehensive user management system provides system administrators with full control over all users in the platform while maintaining security, audit trails, and data integrity.

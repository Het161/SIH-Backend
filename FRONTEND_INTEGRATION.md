# Backend API Integration Guide

## Base URL
- **Local Development:** `http://127.0.0.1:8000`
- **Production:** `https://your-deployed-url.com` (update when deployed)

## API Documentation
- **Swagger UI:** http://127.0.0.1:8000/docs (interactive testing)
- **OpenAPI Spec:** `openapi.json` (attached)

## Authentication Flow

### 1. Register User
**POST** `/api/v1/auth/register`

Request:
{
"email": "user@example.com",
"name": "John Doe",
"role": "employee",
"password": "Password123"
}

text

Response:
{
"id": "uuid-here",
"email": "user@example.com",
"name": "John Doe",
"role": "employee"
}

text

### 2. Login
**POST** `/api/v1/auth/login`

Request:
{
"email": "user@example.com",
"password": "Password123"
}

text

Response:
{
"access_token": "eyJhbGciOiJIUzI1...",
"token_type": "bearer",
"user": {
"id": "uuid",
"email": "user@example.com",
"name": "John Doe"
}
}

text

### 3. Using Token in Requests
For all authenticated endpoints, include the token in headers:

Authorization: Bearer eyJhbGciOiJIUzI1...

text

Example with JavaScript fetch:
fetch('http://localhost:8000/api/v1/tasks', {
method: 'GET',
headers: {
'Authorization': Bearer ${token},
'Content-Type': 'application/json'
}
})

text

## Key Endpoints

### Tasks
- `POST /api/v1/tasks` - Create task
- `POST /api/v1/tasks/bulk` - Create bulk tasks
- `POST /api/v1/tasks/{task_id}/start` - Start task with GPS
- `POST /api/v1/tasks/{task_id}/evidence` - Upload evidence (multipart/form-data)
- `POST /api/v1/tasks/{task_id}/submit` - Submit task
- `POST /api/v1/tasks/{task_id}/review` - Review task
- `GET /api/v1/tasks/{task_id}/lifecycle` - Get task history
- `GET /api/v1/tasks/search` - Search tasks with filters

### Analytics
- `GET /api/v1/analytics/user/{user_id}` - User productivity
- `GET /api/v1/analytics/team/{department}` - Team productivity
- `GET /api/v1/analytics/organization` - Organization metrics
- `GET /api/v1/analytics/sla-breaches` - Overdue tasks

### Audit Logs
- `GET /api/v1/audit-logs` - All audit logs (with filters)
- `GET /api/v1/audit-logs/user/{user_id}` - User audit logs
- `GET /api/v1/audit-logs/task/{task_id}` - Task audit logs

### Reports
- `GET /api/v1/reports/user/{user_id}/pdf` - Download PDF report
- `GET /api/v1/reports/user/{user_id}/excel` - Download Excel report
- `GET /api/v1/reports/team/{department}/excel` - Download team Excel

### Dashboard
- `GET /api/v1/dashboard/summary` - Organization summary
- `GET /api/v1/dashboard/user/{user_id}` - User dashboard

## Test Credentials
(Create test users and provide credentials here)

Example:
- **Manager:** manager@test.com / Password123
- **Employee:** employee@test.com / Password123

## Error Handling
All errors return this format:
{
"detail": "Error message here"
}

text

Common HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `404` - Not Found
- `500` - Server Error

## Notes
- All datetime fields use ISO 8601 format: `2025-10-08T14:30:00Z`
- UUIDs are used for all IDs
- File uploads use `multipart/form-data`
- All other requests use `application/json`

## Support
Contact: your-email@example.com

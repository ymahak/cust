# 📚 API Documentation

Complete API reference for the AI Customer Support System.

---

## Base URL

- **Development:** `http://localhost:8000/api`
- **Production:** `{YOUR_DOMAIN}/api`

---

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

Tokens expire after 24 hours.

---

## Endpoints

### 🔐 Authentication Endpoints

#### 1. Sign Up
**POST** `/api/auth/signup`

Create a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123",
  "role": "user"  // optional: "user", "agent", or "admin"
}
```

**Response (200 OK):**
```json
{
  "message": "User created successfully",
  "username": "john_doe",
  "role": "user"
}
```

**Error Responses:**
- `400 Bad Request`: Username already exists, invalid role, validation errors
- `500 Internal Server Error`: Database error

**Validation Rules:**
- Username: Minimum 3 characters
- Password: Minimum 6 characters
- Role: Must be "user", "agent", or "admin"

---

#### 2. Login
**POST** `/api/auth/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid username or password

---

#### 3. Get Current User
**GET** `/api/auth/me`

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "username": "john_doe",
  "role": "user"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token

---

### 💬 Chat Endpoints

#### 4. Send Message
**POST** `/api/chat`

Send a message to the AI support system. This is a public endpoint (no authentication required).

**Request Body:**
```json
{
  "message": "I need help with my order"
}
```

**Response (200 OK):**
```json
{
  "response": "I'd be happy to help you with your order. Could you provide your order number?",
  "intent": "question",
  "agent_type": "support_agent",
  "escalated": false,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Response Fields:**
- `response`: AI-generated response text
- `intent`: Classified intent (greeting, question, complaint, refund, technical, billing, other)
- `agent_type`: Agent that handled the request (support_agent, escalation_agent, guardrail)
- `escalated`: Boolean indicating if request was escalated
- `timestamp`: ISO 8601 timestamp

**Error Responses:**
- `400 Bad Request`: Message violates guardrails
- `500 Internal Server Error`: Internal error

**Note:** Messages are saved to database and can be retrieved via history endpoint.

---

### 👥 HITL Endpoints

All HITL endpoints require **Admin** or **Agent** role.

#### 5. List Pending Escalations
**GET** `/api/hitl/escalations/pending`

Get all pending escalations for human review.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "escalations": [
    {
      "_id": "65a1b2c3d4e5f6g7h8i9j0k1",
      "user_id": "guest_user",
      "reason": "Support agent unable to handle: complaint",
      "agent_type": "support_agent",
      "status": "pending",
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  ],
  "count": 1
}
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Insufficient permissions (not admin/agent)

---

#### 6. Get Escalation Details
**GET** `/api/hitl/escalations/{escalation_id}`

Get detailed information about a specific escalation.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `escalation_id` (string): MongoDB ObjectId of the escalation

**Response (200 OK):**
```json
{
  "_id": "65a1b2c3d4e5f6g7h8i9j0k1",
  "user_id": "guest_user",
  "reason": "Support agent unable to handle: complaint",
  "agent_type": "support_agent",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00.000Z",
  "original_response": "I understand your concern..."
}
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Escalation not found

---

#### 7. Approve Escalation
**POST** `/api/hitl/escalations/{escalation_id}/approve`

Approve an escalated response and send it to the user.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `escalation_id` (string): MongoDB ObjectId of the escalation

**Request Body:**
```json
{
  "response": "We apologize for the issue. Here's how we can help...",
  "notes": "Approved as is"  // optional
}
```

**Response (200 OK):**
```json
{
  "status": "approved",
  "message": "Escalation approved and resolved."
}
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Escalation not found

---

#### 8. Reject Escalation
**POST** `/api/hitl/escalations/{escalation_id}/reject`

Reject an escalated response and provide an alternative.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `escalation_id` (string): MongoDB ObjectId of the escalation

**Request Body:**
```json
{
  "response": "Alternative response text...",
  "notes": "Rejected, new response provided"  // optional
}
```

**Response (200 OK):**
```json
{
  "status": "rejected",
  "message": "Escalation rejected and resolved with new response."
}
```

---

#### 9. Edit Escalation Response
**POST** `/api/hitl/escalations/{escalation_id}/edit`

Edit the AI-generated response and resolve the escalation.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `escalation_id` (string): MongoDB ObjectId of the escalation

**Request Body:**
```json
{
  "original_response": "Original response text",
  "edited_response": "Edited response text",
  "reason": "Tone adjustment needed"
}
```

**Response (200 OK):**
```json
{
  "status": "edited",
  "message": "Response edited and escalation resolved."
}
```

---

### 📊 Monitoring Endpoints

All monitoring endpoints require **Admin** role.

#### 10. Get Metrics
**GET** `/api/monitoring/metrics`

Get system performance metrics.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "agent_performance": {
    "support_agent": {
      "total_calls": 150,
      "escalations": 12,
      "avg_response_time": 1.23,
      "total_response_time": 184.5
    },
    "intent_agent": {
      "total_calls": 150,
      "escalations": 0,
      "avg_response_time": 0.45,
      "total_response_time": 67.5
    }
  },
  "system_health": {
    "last_check": "2024-01-15T10:30:00.000Z",
    "status": "healthy",
    "uptime_seconds": 86400
  },
  "escalation_stats": {
    "pending": 5,
    "resolved": 120,
    "rejected": 10
  },
  "current_time": "2024-01-15T10:30:00.000Z"
}
```

---

#### 11. Get Dashboard Data
**GET** `/api/monitoring/dashboard`

Get comprehensive dashboard data including metrics, traces, and statistics.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "overview": {
    "total_calls": 150,
    "total_escalations": 12,
    "success_rate": 0.92
  },
  "agent_performance": { /* ... */ },
  "intent_distribution": {
    "greeting": 20,
    "question": 50,
    "complaint": 30,
    "refund": 15,
    "technical": 25,
    "billing": 10
  },
  "trace_summary": {
    "total_traces": 50,
    "successful": 46,
    "failed": 4
  }
}
```

---

#### 12. Get Traces
**GET** `/api/monitoring/traces`

Get recent request traces (last 50).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "span_id": "trace-123",
    "parent_span_id": null,
    "operation_name": "chat_request",
    "start_time": "2024-01-15T10:30:00.000Z",
    "end_time": "2024-01-15T10:30:01.500Z",
    "duration_ms": 1500,
    "status": "completed",
    "logs": [
      {
        "timestamp": "2024-01-15T10:30:00.500Z",
        "level": "info",
        "message": "Intent classified: question"
      }
    ]
  }
]
```

---

#### 13. Get Trace by ID
**GET** `/api/monitoring/traces/{trace_id}`

Get specific trace details.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `trace_id` (string): Trace ID

---

### 🏥 Health Check

#### 14. Health Check
**GET** `/api/health`

Check if the API is running.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "ai-customer-support"
}
```

No authentication required.

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing rate limiting to prevent abuse.

---

## CORS

CORS is enabled for:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative frontend port)

To add more origins, update `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://yourdomain.com"],
    ...
)
```

---

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These interfaces allow you to test API endpoints directly from the browser.

---

**Last Updated:** 2024

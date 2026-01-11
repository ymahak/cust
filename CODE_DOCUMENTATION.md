# 📖 Detailed Code Documentation

Comprehensive code documentation for every file in the AI Customer Support System.

---

## Table of Contents

- [Backend Files](#backend-files)
  - [Core Application](#core-application)
  - [Agents](#agents)
  - [Database](#database)
  - [Authentication](#authentication)
  - [Security](#security)
  - [Monitoring](#monitoring)
  - [Routes](#routes)
- [Frontend Files](#frontend-files)
  - [Components](#components)
  - [API Client](#api-client)
  - [Configuration](#configuration)

---

## Backend Files

### Core Application

#### `backend/app/main.py`

**Purpose:** FastAPI application entry point, middleware configuration, and authentication endpoints.

**Key Components:**

1. **FastAPI App Initialization**
   ```python
   app = FastAPI(title="AI Customer Support", version="1.0.0")
   ```
   - Creates the FastAPI application instance
   - Sets application metadata

2. **CORS Middleware**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173", "http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
   - Enables Cross-Origin Resource Sharing
   - Allows frontend to make API requests
   - Allows credentials (cookies, auth headers)

3. **Router Registration**
   ```python
   app.include_router(chat_router, prefix="/api")
   app.include_router(hitl_router, prefix="/api")
   app.include_router(monitoring_router, prefix="/api")
   ```
   - Registers all API routes
   - All routes prefixed with `/api`

4. **Request Models**
   - `User`: Login request model (username, password)
   - `SignupRequest`: Signup request model (username, password, optional role)
   - `TokenResponse`: Login response model (access_token, token_type)

5. **Endpoints:**

   **`POST /api/auth/signup`**
   - Creates new user account
   - Validates input (username min 3 chars, password min 6 chars)
   - Hashes password with bcrypt
   - Stores user in MongoDB
   - Returns user info (without password)

   **`POST /api/auth/login`**
   - Authenticates user credentials
   - Verifies password hash
   - Creates JWT token
   - Returns token for subsequent requests

   **`GET /api/auth/me`**
   - Returns current user info
   - Requires JWT token in Authorization header
   - Validates token and extracts user data

   **`GET /api/health`**
   - Health check endpoint
   - Returns service status
   - No authentication required

---

### Agents

#### `backend/app/agent/intent_agent.py`

**Purpose:** Classifies user messages into intent categories.

**Key Function:**

```python
def classify_intent(user_message: str) -> str:
```

**Implementation:**
1. Gets OpenAI client using API key from environment
2. Sends classification prompt + user message to GPT-3.5-turbo
3. Uses low temperature (0.3) for consistent classification
4. Validates response against known intents
5. Returns intent category or "other" as fallback

**Intents:**
- `greeting`: Simple greetings
- `question`: General questions
- `complaint`: Issues or problems
- `refund`: Refund requests
- `technical`: Technical support
- `billing`: Billing or payment issues
- `other`: Anything else

**Error Handling:**
- Returns "other" if classification fails
- Logs errors without crashing

---

#### `backend/app/agent/support_agent.py`

**Purpose:** Generates AI responses to user queries.

**Key Function:**

```python
def generate_response(
    user_message: str,
    intent: str,
    conversation_history: Optional[List[Dict]] = None
) -> Dict[str, any]:
```

**Implementation:**
1. Builds context from conversation history (last 5 messages)
2. Creates system prompt with role definition
3. Adds intent information to context
4. Sends to GPT-3.5-turbo with user message
5. Checks response for "ESCALATE" keyword
6. Returns response dict with escalation flag

**Returns:**
```python
{
    "response": str,           # Generated response text
    "needs_escalation": bool,  # True if escalation needed
    "agent_type": str          # "support_agent"
}
```

**Features:**
- Includes conversation context for continuity
- Detects when escalation is needed
- Handles errors gracefully with fallback response

---

#### `backend/app/agent/escalation_agent.py`

**Purpose:** Manages human-in-the-loop escalation workflow.

**Class:** `EscalationAgent`

**Key Methods:**

1. **`create_escalation(user_id, reason, agent_type, original_response)`**
   - Creates escalation record in MongoDB
   - Sets status to "pending"
   - Stores original AI response
   - Returns escalation info with message

2. **`get_pending_escalations()`**
   - Retrieves all escalations with status "pending"
   - Sorted by creation date
   - Returns list of escalations

3. **`get_escalation_details(escalation_id)`**
   - Gets full details of specific escalation
   - Includes original response
   - Raises error if not found

4. **`resolve_escalation(escalation_id, resolution, resolved_by)`**
   - Marks escalation as resolved
   - Stores resolution text
   - Records who resolved it
   - Updates timestamp

5. **`update_escalation_response(escalation_id, new_response, resolved_by, reason)`**
   - Updates AI response with human-edited version
   - Stores reason for edit
   - Saves human feedback
   - Marks as resolved

6. **`provide_feedback(escalation_id, feedback_type, notes, submitted_by)`**
   - Saves human feedback
   - Links to escalation
   - Used for system improvement

---

### Database

#### `backend/app/database/mongo.py`

**Purpose:** MongoDB connection management and database operations.

**Key Components:**

1. **Global Variables**
   - `client`: AsyncIOMotorClient instance
   - `db`: Database instance
   - `messages_collection`: Chat messages collection
   - `escalations_collection`: Escalations collection
   - `users_collection`: Users collection

2. **Connection Management**

   **`connect_db()`**
   - Establishes MongoDB connection
   - Uses MONGO_URI from environment
   - Initializes collections
   - Idempotent (safe to call multiple times)

3. **User Management**

   **`create_user(username, password, role="user")`**
   - Checks if username exists
   - Hashes password with bcrypt
   - Creates user document
   - Returns user dict (without password)

   **`verify_user(username, password)`**
   - Finds user by username
   - Verifies password hash
   - Returns user data if valid
   - Returns None if invalid

   **`get_user_by_username(username)`**
   - Retrieves user by username
   - Removes password from response
   - Formats timestamps

4. **Message Management**

   **`save_message(user_id, message, response, agent_type, metadata)`**
   - Saves chat message to database
   - Includes metadata (intent, escalation status)
   - Stores timestamp

   **`get_conversation_history(user_id, limit=10)`**
   - Retrieves recent messages for user
   - Sorted by timestamp (newest first)
   - Limits results
   - Formats for API response

5. **Escalation Management**

   **`create_escalation(user_id, reason, agent_type)`**
   - Creates escalation document
   - Status: "pending"
   - Stores creation timestamp

   **`get_pending_escalations()`**
   - Finds all pending escalations
   - Sorted by creation date
   - Formats for API response

   **`get_escalation(escalation_id)`**
   - Retrieves single escalation
   - Converts ObjectId to string
   - Formats timestamps

   **`resolve_escalation(escalation_id, resolution)`**
   - Updates escalation status to "resolved"
   - Stores resolution text
   - Records resolution timestamp

   **`update_escalation_response(escalation_id, response, reviewed_by, notes, status)`**
   - Updates escalation with human response
   - Stores reviewer info
   - Records review timestamp
   - Adds optional notes

   **`save_human_feedback(escalation_id, reviewer, action, response, original_response, notes)`**
   - Saves feedback to separate collection
   - Links to escalation
   - Stores action type (approved, rejected, edited)
   - Used for analytics and improvement

---

### Authentication

#### `backend/app/auth/jwt.py`

**Purpose:** JWT token creation and verification.

**Configuration:**
- Algorithm: HS256
- Expiration: 24 hours
- Secret: From environment variable (JWT_SECRET)

**Key Functions:**

1. **`create_token(data: Dict) -> str`**
   - Creates JWT token
   - Adds expiration time (24 hours from now)
   - Adds issued-at time
   - Encodes with secret key
   - Returns token string

2. **`verify_token(token: str) -> Dict`**
   - Decodes JWT token
   - Verifies signature
   - Checks expiration
   - Returns payload (user data)
   - Raises ValueError if invalid/expired

**Token Payload:**
```python
{
    "username": str,
    "role": str,
    "exp": int,  # Expiration timestamp
    "iat": int   # Issued-at timestamp
}
```

---

### Security

#### `backend/app/security/guardrails.py`

**Purpose:** Input validation and security guardrails.

**Key Function:**

```python
def check_guardrails(message: str) -> Dict[str, any]:
```

**Validation Checks:**

1. **Blocked Keywords**
   - Checks for malicious keywords: hack, exploit, bypass, unauthorized access, illegal, harmful, dangerous
   - Case-insensitive matching

2. **Pattern Matching**
   - Detects sensitive data patterns:
     - `password = ...`
     - `api_key = ...`
     - `secret = ...`
   - Uses regex matching

3. **Message Length**
   - Maximum 2000 characters
   - Prevents oversized payloads

**Returns:**
```python
{
    "allowed": bool,    # True if passed all checks
    "reason": str       # Reason if blocked
}
```

**Integration:**
- Called before processing chat messages
- Blocks harmful or malicious input
- Returns generic error message to user

---

### Monitoring

#### `backend/app/monitoring/logger.py`

**Purpose:** Centralized logging configuration.

**Key Function:**

```python
def setup_logger() -> logging.Logger:
```

**Configuration:**
- Log level: INFO (configurable)
- Format: Timestamp, Level, Module, Message
- Output: Both file and console
- File: `logs/app_{date}.log`
- Console: Standard output

**Features:**
- Creates logs directory if needed
- Rotates log files daily
- Includes file and line number

---

#### `backend/app/monitoring/metrics.py`

**Purpose:** Metrics tracking system.

**Key Components:**

1. **Metrics Storage**
   - In-memory dictionary storage
   - Agent performance metrics
   - System health metrics
   - Escalation statistics

2. **Agent Performance Tracking**
   - Total calls per agent
   - Escalation count
   - Average response time
   - Total response time

3. **System Health**
   - Status (healthy, unhealthy)
   - Uptime in seconds
   - Last check timestamp

4. **Key Functions:**
   - `record_agent_call(agent_type, response_time, escalated)`
   - `update_system_health(status)`
   - `get_all_metrics()`
   - `get_agent_performance(agent_type)`
   - `get_escalation_stats()`

---

#### `backend/app/monitoring/tracer.py`

**Purpose:** Distributed tracing system.

**Key Components:**

1. **Trace Storage**
   - In-memory list (last 50 traces)
   - Span-based tracing
   - Parent-child relationships

2. **Span Structure**
   ```python
   {
       "span_id": str,
       "parent_span_id": str | None,
       "operation_name": str,
       "start_time": str,
       "end_time": str | None,
       "duration_ms": float | None,
       "status": str,
       "logs": List[Dict]
   }
   ```

3. **Key Functions:**
   - `start_span(operation_name, parent_span_id)`
   - `end_span(span_id, status)`
   - `add_log(span_id, message, level)`
   - `get_recent_traces(limit=50)`
   - `get_trace(trace_id)`
   - `clear_traces()`

---

### Routes

#### `backend/app/routes/chat.py`

**Purpose:** Chat API endpoints.

**Key Endpoint:**

**`POST /api/chat`**

**Flow:**
1. Validates input (guardrails)
2. Classifies intent (Intent Agent)
3. Retrieves conversation history
4. Generates response (Support Agent)
5. Checks for escalation
6. Creates escalation if needed (Escalation Agent)
7. Saves message to database
8. Returns response

**Request Model:**
```python
class ChatMessage(BaseModel):
    message: str
```

**Response Model:**
```python
class ChatResponse(BaseModel):
    response: str
    intent: str
    agent_type: str
    escalated: bool
    timestamp: str
```

**Error Handling:**
- Graceful fallbacks at each step
- Continues even if one step fails
- Returns helpful error messages

---

#### `backend/app/routes/hitl.py`

**Purpose:** HITL dashboard API endpoints.

**Authentication:** Requires Admin or Agent role

**Key Endpoints:**

1. **`GET /api/hitl/escalations/pending`**
   - Lists all pending escalations
   - Returns count and list

2. **`GET /api/hitl/escalations/{id}`**
   - Gets escalation details
   - Includes original response

3. **`POST /api/hitl/escalations/{id}/approve`**
   - Approves escalation
   - Stores response
   - Marks as resolved
   - Saves feedback

4. **`POST /api/hitl/escalations/{id}/reject`**
   - Rejects escalation
   - Stores alternative response
   - Marks as resolved

5. **`POST /api/hitl/escalations/{id}/edit`**
   - Edits AI response
   - Stores edited version
   - Records reason
   - Marks as resolved

**Request Models:**
- `EscalationResponse`: Response and optional notes
- `EditResponse`: Original, edited, and reason

---

#### `backend/app/routes/monitoring.py`

**Purpose:** Monitoring API endpoints.

**Authentication:** Requires Admin role

**Key Endpoints:**

1. **`GET /api/monitoring/metrics`**
   - Returns all metrics
   - Agent performance
   - System health
   - Escalation stats

2. **`GET /api/monitoring/dashboard`**
   - Comprehensive dashboard data
   - Includes overview, metrics, distributions, traces

3. **`GET /api/monitoring/traces`**
   - Returns recent traces (last 50)
   - Includes span details

4. **`GET /api/monitoring/traces/{id}`**
   - Gets specific trace
   - Includes all spans and logs

---

## Frontend Files

### Components

#### `frontend/src/App.tsx`

**Purpose:** Main application component with routing and authentication.

**Key Features:**

1. **State Management**
   - `user`: Current user info (null if not logged in)
   - `view`: Current view (chat, hitl, monitoring)
   - `authView`: Authentication view (login, signup)
   - `loading`: Loading state

2. **Authentication Flow**
   - Checks for token in localStorage
   - Fetches user info on mount
   - Shows login/signup if not authenticated
   - Shows main app if authenticated

3. **View Switching**
   - Chat: Available to all users
   - HITL: Admin/Agent only
   - Monitoring: Admin only
   - Role-based navigation

4. **Functions**
   - `handleLogin(token)`: Stores token, fetches user
   - `handleLogout()`: Removes token, clears user
   - `setView(view)`: Changes current view

---

#### `frontend/src/components/Chat.tsx`

**Purpose:** Chat interface component.

**Key Features:**

1. **State**
   - `messages`: Array of message objects
   - `input`: Current input text
   - `loading`: Loading state

2. **Functions**
   - `handleSend()`: Sends message to API
   - `loadHistory()`: Loads conversation history
   - `scrollToBottom()`: Auto-scrolls to latest message

3. **Message Display**
   - Shows user and assistant messages
   - Displays intent and agent type
   - Shows escalation badge if escalated
   - Displays timestamps

4. **UI Elements**
   - Message list
   - Input field
   - Send button
   - Loading indicator
   - Error messages

---

#### `frontend/src/components/HITL.tsx`

**Purpose:** HITL dashboard for agents/admins.

**Key Features:**

1. **State**
   - `escalations`: List of pending escalations
   - `selectedEscalation`: Currently selected escalation
   - `loading`: Loading state
   - `error`: Error messages

2. **Functions**
   - `fetchEscalations()`: Loads pending escalations
   - `viewEscalationDetails(id)`: Loads escalation details
   - `handleApprove()`: Approves escalation
   - `handleReject()`: Rejects escalation
   - `handleEdit()`: Edits response

3. **UI Elements**
   - Escalation list
   - Escalation details view
   - Action buttons (Approve, Reject, Edit)
   - Notes field
   - Auto-refresh (5 seconds)

---

#### `frontend/src/components/MonitoringDashboard.tsx`

**Purpose:** Monitoring dashboard for admins.

**Key Features:**

1. **State**
   - `metrics`: System metrics
   - `traces`: Request traces
   - `loading`: Loading states
   - `error`: Error messages

2. **Functions**
   - `fetchMetrics()`: Loads metrics
   - `fetchTraces()`: Loads traces
   - `handleClearTraces()`: Clears trace history

3. **Display**
   - Agent performance cards
   - Intent distribution charts
   - Escalation statistics
   - Trace summaries
   - Auto-refresh (10 seconds)

---

#### `frontend/src/components/Login.tsx`

**Purpose:** User login component.

**Key Features:**

1. **State**
   - `username`: Username input
   - `password`: Password input
   - `error`: Error message
   - `loading`: Loading state

2. **Functions**
   - `handleSubmit()`: Submits login form
   - Calls API login function
   - Stores token
   - Triggers parent callback

3. **UI Elements**
   - Username input
   - Password input
   - Login button
   - Error display
   - Link to signup

---

#### `frontend/src/components/Signup.tsx`

**Purpose:** User signup component.

**Key Features:**

1. **State**
   - `username`: Username input
   - `password`: Password input
   - `confirmPassword`: Confirm password input
   - `role`: Selected role
   - `error`: Error message
   - `loading`: Loading state

2. **Validation**
   - Username min 3 characters
   - Password min 6 characters
   - Passwords must match

3. **Functions**
   - `handleSubmit()`: Submits signup form
   - Validates input
   - Calls API signup function
   - Redirects to login

4. **UI Elements**
   - Username input
   - Password input
   - Confirm password input
   - Role selector
   - Signup button
   - Link to login

---

### API Client

#### `frontend/src/api.ts`

**Purpose:** Centralized API client with axios.

**Key Features:**

1. **Configuration**
   - Base URL: `http://localhost:8000/api`
   - Default headers: Content-Type: application/json
   - Request interceptor: Adds JWT token
   - Response interceptor: Handles 401 errors

2. **Type Definitions**
   - `ChatResponse`: Chat API response
   - `LoginResponse`: Login API response
   - `User`: User information
   - `Escalation`: Escalation data
   - `Metrics`: Metrics data
   - `Trace`: Trace data

3. **API Functions**

   **Authentication:**
   - `signup(username, password, role)`
   - `login(username, password)`
   - `getCurrentUser()`

   **Chat:**
   - `sendMessage(message)`

   **HITL:**
   - `getPendingEscalations()`
   - `getEscalation(id)`
   - `approveEscalation(id, response, notes)`
   - `rejectEscalation(id, response, notes)`
   - `editEscalation(id, original, edited, reason)`

   **Monitoring:**
   - `getMetrics()`
   - `getDashboard()`
   - `getTraces()`

4. **Error Handling**
   - Automatic token injection
   - 401 error handling (redirects to login)
   - Error message extraction
   - Promise rejection with errors

---

## Configuration Files

### Backend

#### `backend/requirements.txt`

Python dependencies:
- `fastapi>=0.104.0`: Web framework
- `uvicorn[standard]>=0.24.0`: ASGI server
- `python-dotenv>=1.0.0`: Environment variables
- `motor>=3.3.0`: Async MongoDB driver
- `pymongo>=4.6.0`: MongoDB driver
- `pyjwt>=2.8.0`: JWT tokens
- `openai>=1.3.0`: OpenAI API client
- `pydantic>=2.5.0`: Data validation
- `python-multipart>=0.0.6`: Form data support
- `bcrypt>=4.0.0`: Password hashing

---

### Frontend

#### `frontend/package.json`

Node.js dependencies:
- `react^19.2.0`: UI library
- `react-dom^19.2.0`: React DOM
- `axios^1.13.2`: HTTP client
- `typescript~5.9.3`: TypeScript compiler
- `vite^7.4.4`: Build tool
- `@vitejs/plugin-react^5.1.1`: Vite React plugin

---

**Last Updated:** 2024

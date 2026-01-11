# 🤖 AI Customer Support System

A production-ready multi-agent AI customer support system with Human-in-the-Loop (HITL), comprehensive monitoring, and enterprise-grade security features.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Code Documentation](#code-documentation)
- [Usage Guide](#usage-guide)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This project implements a complete multi-agent AI customer support system that:

- **Classifies user intents** using an Intent Classification Agent
- **Generates intelligent responses** using a Support Agent powered by OpenAI GPT
- **Escalates complex issues** to human agents via HITL workflow
- **Monitors system performance** with real-time metrics and tracing
- **Ensures security** through JWT authentication, role-based access, and input guardrails
- **Provides dashboards** for human agents to review and manage escalations

---

## ✨ Features

### 1. Multi-Agent System
- **Intent Agent**: Classifies user messages into categories (greeting, question, complaint, refund, technical, billing, other)
- **Support Agent**: Generates contextual responses using OpenAI GPT-3.5-turbo
- **Escalation Agent**: Manages human-in-the-loop workflow for complex issues

### 2. Human-in-the-Loop (HITL)
- Dashboard for agents/admins to review escalated requests
- Approve, reject, or edit AI-generated responses
- Store human feedback for system improvement
- Role-based access control (Admin/Agent only)

### 3. Monitoring & Observability
- Real-time agent performance metrics
- Intent distribution tracking
- Escalation statistics
- Distributed tracing across agents
- Comprehensive monitoring dashboard

### 4. Security
- JWT-based authentication
- Role-based access control (Admin, Agent, User)
- Input validation and guardrails
- Password hashing with bcrypt
- Protected API endpoints

### 5. User Management
- User signup and authentication
- MongoDB-based user storage
- Secure password hashing
- Role assignment (user, agent, admin)

---

## 🏗️ Architecture

```
┌─────────────────┐
│   React.js      │  Frontend (TypeScript)
│   Frontend      │  - Chat Interface
└────────┬────────┘  - HITL Dashboard
         │           - Monitoring Dashboard
         │ HTTP/REST
         │
┌────────▼────────┐
│   FastAPI       │  Backend (Python)
│   Backend       │  - REST API
└────────┬────────┘  - Multi-Agent Orchestration
         │
    ┌────┴────┬──────────────┐
    │         │              │
┌───▼───┐ ┌──▼──┐    ┌──────▼──────┐
│MongoDB│ │OpenAI│    │   Monitoring│
│       │ │ API  │    │   & Metrics │
└───────┘ └──────┘    └─────────────┘
```

### System Flow

1. **User sends message** → Frontend (React)
2. **API Request** → Backend (FastAPI)
3. **Security Check** → Guardrails validation
4. **Intent Classification** → Intent Agent (OpenAI)
5. **Response Generation** → Support Agent (OpenAI)
6. **Escalation Check** → Escalation Agent
7. **Storage** → MongoDB
8. **Metrics** → Monitoring System
9. **Response** → Frontend

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** (v0.104.0+): High-performance async web framework
- **Python** (3.8+): Programming language
- **MongoDB**: NoSQL database (via Motor async driver)
- **OpenAI API**: GPT-3.5-turbo for AI responses
- **JWT**: Authentication tokens
- **bcrypt**: Password hashing
- **Uvicorn**: ASGI server

### Frontend
- **React** (18+): UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **Axios**: HTTP client
- **CSS3**: Styling

---

## 📁 Project Structure

```
cust/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── agent/                  # Multi-agent system
│   │   │   ├── __init__.py
│   │   │   ├── intent_agent.py     # Intent classification agent
│   │   │   ├── support_agent.py    # Response generation agent
│   │   │   └── escalation_agent.py # Escalation management agent
│   │   ├── auth/                   # Authentication
│   │   │   ├── __init__.py
│   │   │   └── jwt.py              # JWT token creation/verification
│   │   ├── database/               # Database layer
│   │   │   ├── __init__.py
│   │   │   └── mongo.py            # MongoDB operations
│   │   ├── monitoring/             # Monitoring system
│   │   │   ├── __init__.py
│   │   │   ├── logger.py           # Logging configuration
│   │   │   ├── metrics.py          # Metrics tracking
│   │   │   └── tracer.py           # Distributed tracing
│   │   ├── routes/                 # API routes
│   │   │   ├── __init__.py
│   │   │   ├── chat.py             # Chat endpoints
│   │   │   ├── hitl.py             # HITL endpoints
│   │   │   └── monitoring.py       # Monitoring endpoints
│   │   └── security/               # Security features
│   │       ├── __init__.py
│   │       └── guardrails.py       # Input validation & guardrails
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # Environment variables (create this)
│
├── frontend/
│   ├── src/
│   │   ├── components/             # React components
│   │   │   ├── Chat.tsx            # Chat interface
│   │   │   ├── Chat.css
│   │   │   ├── Login.tsx           # Login page
│   │   │   ├── Login.css
│   │   │   ├── Signup.tsx          # Signup page
│   │   │   ├── Signup.css
│   │   │   ├── HITL.tsx            # HITL dashboard
│   │   │   ├── HITL.css
│   │   │   ├── MonitoringDashboard.tsx
│   │   │   └── MonitoringDashboard.css
│   │   ├── App.tsx                 # Main app component
│   │   ├── App.css                 # Main app styles
│   │   ├── api.ts                  # API client
│   │   └── main.tsx                # Entry point
│   ├── package.json                # Node.js dependencies
│   ├── vite.config.ts              # Vite configuration
│   └── tsconfig.json               # TypeScript configuration
│
└── README.md                       # This file
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python** 3.8 or higher
- **Node.js** 16 or higher and npm
- **MongoDB** (local or MongoDB Atlas account)
- **OpenAI API Key** (from https://platform.openai.com/api-keys)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd cust
```

### Step 2: Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   # Create .env file in backend/ directory
   ```
   
   Add the following content:
   ```env
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.zldx5.mongodb.net/
   OPENAI_API_KEY=sk-your-openai-api-key-here
   JWT_SECRET=your-secret-key-here-change-in-production
   ```

5. **Run the backend server:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`
   API docs at: `http://localhost:8000/docs`

### Step 3: Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

### Step 4: Verify Installation

1. **Check backend:**
   - Visit `http://localhost:8000/api/health`
   - Should return: `{"status": "healthy", "service": "ai-customer-support"}`

2. **Check frontend:**
   - Visit `http://localhost:5173`
   - Should see the login page

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# MongoDB Connection
MONGO_URI=mongodb+srv://username:password@cluster0.zldx5.mongodb.net/

# OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# JWT Secret Key (use a strong random string in production)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
```

### MongoDB Setup

**Option 1: MongoDB Atlas (Cloud - Recommended)**
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string
4. Update `MONGO_URI` in `.env`

**Option 2: Local MongoDB**
1. Install MongoDB locally
2. Start MongoDB service
3. Use: `MONGO_URI=mongodb://localhost:27017/`

### OpenAI API Key

1. Sign up at https://platform.openai.com/
2. Go to API Keys section
3. Create new API key
4. Add to `.env` file

---

## 📚 API Documentation

### Authentication Endpoints

#### POST `/api/auth/signup`
Create a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123",
  "role": "user"  // optional: "user", "agent", or "admin"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "username": "john_doe",
  "role": "user"
}
```

#### POST `/api/auth/login`
Authenticate user and get JWT token.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET `/api/auth/me`
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "username": "john_doe",
  "role": "user"
}
```

### Chat Endpoints

#### POST `/api/chat`
Send a message to the AI support system (public endpoint).

**Request Body:**
```json
{
  "message": "I need help with my order"
}
```

**Response:**
```json
{
  "response": "I'd be happy to help you with your order. Could you provide your order number?",
  "intent": "question",
  "agent_type": "support_agent",
  "escalated": false,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HITL Endpoints (Requires Admin/Agent Role)

#### GET `/api/hitl/escalations/pending`
Get all pending escalations.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "escalations": [
    {
      "_id": "65a1b2c3d4e5f6g7h8i9j0k1",
      "user_id": "guest_user",
      "reason": "Support agent unable to handle: complaint",
      "agent_type": "support_agent",
      "status": "pending",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

#### GET `/api/hitl/escalations/{escalation_id}`
Get details of a specific escalation.

#### POST `/api/hitl/escalations/{escalation_id}/approve`
Approve an escalation and send response.

**Request Body:**
```json
{
  "response": "We apologize for the issue. Here's how we can help...",
  "notes": "Approved as is"
}
```

#### POST `/api/hitl/escalations/{escalation_id}/reject`
Reject escalation and provide alternative response.

#### POST `/api/hitl/escalations/{escalation_id}/edit`
Edit the AI-generated response.

**Request Body:**
```json
{
  "original_response": "Original response text",
  "edited_response": "Edited response text",
  "reason": "Tone adjustment needed"
}
```

### Monitoring Endpoints (Requires Admin Role)

#### GET `/api/monitoring/metrics`
Get system metrics.

**Response:**
```json
{
  "agent_performance": {
    "support_agent": {
      "total_calls": 150,
      "escalations": 12,
      "avg_response_time": 1.23
    }
  },
  "system_health": {
    "status": "healthy",
    "uptime_seconds": 86400
  }
}
```

#### GET `/api/monitoring/dashboard`
Get comprehensive dashboard data.

#### GET `/api/monitoring/traces`
Get recent request traces.

---

## 📖 Code Documentation

### Backend Files

#### `backend/app/main.py`
**Purpose:** FastAPI application entry point and main configuration.

**Key Components:**
- FastAPI app initialization
- CORS middleware configuration
- Router registration (chat, HITL, monitoring)
- Authentication endpoints (signup, login, /me)
- User models and request schemas

**Important Functions:**
- `signup()`: Creates new user account with password hashing
- `login()`: Authenticates user and returns JWT token
- `get_current_user()`: Validates JWT and returns user info

#### `backend/app/database/mongo.py`
**Purpose:** MongoDB database operations and connection management.

**Key Functions:**
- `connect_db()`: Establishes MongoDB connection
- `create_user()`: Creates new user with hashed password
- `verify_user()`: Verifies user credentials
- `save_message()`: Saves chat messages to database
- `get_conversation_history()`: Retrieves chat history
- `create_escalation()`: Creates HITL escalation
- `get_pending_escalations()`: Gets pending escalations
- `resolve_escalation()`: Resolves escalation with human response
- `save_human_feedback()`: Stores human feedback

**Collections:**
- `users`: User accounts with hashed passwords
- `messages`: Chat messages and responses
- `escalations`: HITL escalations
- `human_feedback`: Human review feedback

#### `backend/app/agent/intent_agent.py`
**Purpose:** Classifies user messages into intent categories.

**Key Function:**
- `classify_intent(user_message: str) -> str`: Returns intent category

**Intents:**
- greeting, question, complaint, refund, technical, billing, other

**Implementation:**
- Uses OpenAI GPT-3.5-turbo with classification prompt
- Temperature: 0.3 (low for consistency)
- Max tokens: 50

#### `backend/app/agent/support_agent.py`
**Purpose:** Generates AI responses to user queries.

**Key Function:**
- `generate_response(user_message, intent, conversation_history) -> Dict`

**Returns:**
- `response`: Generated response text
- `needs_escalation`: Boolean flag
- `agent_type`: "support_agent"

**Implementation:**
- Uses OpenAI GPT-3.5-turbo
- Includes conversation context
- Checks for escalation triggers ("ESCALATE" keyword)

#### `backend/app/agent/escalation_agent.py`
**Purpose:** Manages human-in-the-loop escalation workflow.

**Key Functions:**
- `create_escalation()`: Creates escalation record
- `get_pending_escalations()`: Gets pending escalations
- `resolve_escalation()`: Resolves with human response
- `update_escalation_response()`: Updates AI response

#### `backend/app/auth/jwt.py`
**Purpose:** JWT token creation and verification.

**Key Functions:**
- `create_token(data: Dict) -> str`: Creates JWT token
- `verify_token(token: str) -> Dict`: Verifies and decodes token

**Configuration:**
- Algorithm: HS256
- Expiration: 24 hours
- Secret: From environment variable

#### `backend/app/security/guardrails.py`
**Purpose:** Input validation and security guardrails.

**Key Function:**
- `check_guardrails(message: str) -> Dict`: Validates user input

**Checks:**
- Blocked keywords (hack, exploit, etc.)
- Sensitive data patterns (passwords, API keys)
- Message length limits (max 2000 characters)

#### `backend/app/routes/chat.py`
**Purpose:** Chat API endpoints.

**Key Endpoints:**
- `POST /api/chat`: Main chat endpoint

**Flow:**
1. Guardrails check
2. Intent classification
3. Get conversation history
4. Generate response
5. Check for escalation
6. Save to database
7. Return response

#### `backend/app/routes/hitl.py`
**Purpose:** HITL dashboard API endpoints.

**Key Endpoints:**
- `GET /api/hitl/escalations/pending`: List pending
- `GET /api/hitl/escalations/{id}`: Get details
- `POST /api/hitl/escalations/{id}/approve`: Approve
- `POST /api/hitl/escalations/{id}/reject`: Reject
- `POST /api/hitl/escalations/{id}/edit`: Edit

**Authorization:** Admin/Agent role required

#### `backend/app/routes/monitoring.py`
**Purpose:** Monitoring and metrics API endpoints.

**Key Endpoints:**
- `GET /api/monitoring/metrics`: Get metrics
- `GET /api/monitoring/dashboard`: Get dashboard data
- `GET /api/monitoring/traces`: Get traces

**Authorization:** Admin role required

#### `backend/app/monitoring/metrics.py`
**Purpose:** Metrics tracking system.

**Tracks:**
- Agent performance (calls, latency, escalations)
- Intent distribution
- Error rates
- System health

#### `backend/app/monitoring/tracer.py`
**Purpose:** Distributed tracing system.

**Features:**
- Span tracking across agents
- Duration measurement
- Success rate calculation
- Trace history

### Frontend Files

#### `frontend/src/App.tsx`
**Purpose:** Main application component with routing and authentication.

**Key Features:**
- Authentication state management
- View switching (chat, HITL, monitoring)
- Role-based navigation
- Login/signup handling

**State:**
- `user`: Current user information
- `view`: Current view (chat/hitl/monitoring)
- `authView`: Authentication view (login/signup)
- `loading`: Loading state

#### `frontend/src/components/Chat.tsx`
**Purpose:** Chat interface component.

**Features:**
- Message display
- Input handling
- Message sending
- History loading
- Real-time updates

#### `frontend/src/components/HITL.tsx`
**Purpose:** HITL dashboard for agents/admins.

**Features:**
- List pending escalations
- View escalation details
- Approve/reject/edit actions
- Auto-refresh (5 seconds)

#### `frontend/src/components/MonitoringDashboard.tsx`
**Purpose:** Monitoring dashboard for admins.

**Features:**
- Agent performance metrics
- Intent distribution charts
- Escalation statistics
- Trace summaries
- Auto-refresh (10 seconds)

#### `frontend/src/components/Login.tsx`
**Purpose:** User login component.

**Features:**
- Username/password input
- Form validation
- Error handling
- Link to signup

#### `frontend/src/components/Signup.tsx`
**Purpose:** User signup component.

**Features:**
- Username/password/confirm password
- Role selection
- Form validation
- Link to login

#### `frontend/src/api.ts`
**Purpose:** API client with axios.

**Features:**
- Centralized API configuration
- JWT token injection
- Error handling
- Type definitions

**Key Functions:**
- `signup()`: User registration
- `login()`: User authentication
- `sendMessage()`: Send chat message
- `getPendingEscalations()`: Get HITL escalations
- `getMetrics()`: Get monitoring metrics

---

## 📖 Usage Guide

### For End Users

1. **Sign Up:**
   - Visit the application
   - Click "Sign up here"
   - Enter username, password, confirm password
   - Select role (user/agent/admin)
   - Click "Sign Up"

2. **Login:**
   - Enter username and password
   - Click "Login"

3. **Chat:**
   - Type your message
   - Press Enter or click Send
   - View AI response
   - Continue conversation

### For Agents/Admins

1. **HITL Dashboard:**
   - Login with agent/admin account
   - Click "HITL Dashboard" in navigation
   - View pending escalations
   - Click on escalation to review
   - Choose action: Approve, Reject, or Edit
   - Add notes if needed
   - Submit response

2. **Monitoring Dashboard (Admin Only):**
   - Click "Monitoring" in navigation
   - View system metrics
   - Check agent performance
   - Review traces
   - Monitor system health

---

## 🔧 Development

### Running in Development Mode

**Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

**Backend:**
```bash
# Use production ASGI server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Code Style

**Backend:**
- Follow PEP 8
- Use type hints
- Document functions with docstrings

**Frontend:**
- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks

---

## 🐛 Troubleshooting

### Common Issues

**1. MongoDB Connection Error**
- Check `MONGO_URI` in `.env`
- Verify MongoDB is running
- Check network connectivity
- Verify credentials

**2. OpenAI API Error**
- Verify `OPENAI_API_KEY` in `.env`
- Check API key is valid
- Verify account has credits
- Check rate limits

**3. Import Errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version (3.8+)

**4. Frontend Build Errors**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Check Node.js version (16+)

**5. CORS Errors**
- Verify backend CORS settings in `main.py`
- Check frontend URL matches allowed origins
- Ensure backend is running

**6. JWT Token Errors**
- Verify `JWT_SECRET` in `.env`
- Check token expiration (24 hours)
- Ensure token is sent in Authorization header

**7. bcrypt Installation Issues**
- On Windows: May need Visual C++ Build Tools
- Try: `pip install bcrypt --no-cache-dir`
- Alternative: Use `passlib` with bcrypt backend

---

## 📝 License

This project is for educational/demonstration purposes.

---

## 👥 Contributors

- Project Developer

---

## 🙏 Acknowledgments

- OpenAI for GPT API
- FastAPI team
- React team
- MongoDB team

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review API documentation at `/docs`
3. Check error logs in console

---

**Last Updated:** 2024

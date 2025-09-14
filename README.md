# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
email-validator==2.1.0
pydantic[email]==2.5.0

# setup_instructions.md

# Authentication System Setup Guide

## Backend Setup (FastAPI)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the FastAPI Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. API Endpoints

The server will be available at `http://localhost:8000`

**Available Endpoints:**
- `GET /` - API information and available endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/profile` - Get current user profile (protected)
- `POST /auth/logout` - User logout (protected)
- `GET /auth/stats` - Authentication statistics
- `GET /auth/recent-activity` - Recent login activity
- `GET /health` - Health check

**Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Frontend Setup (React)

The React frontend is already configured to connect to the FastAPI backend at `http://localhost:8000`.

### Features:
- User registration with validation
- User login with JWT token storage
- Form validation and error handling
- Responsive design
- Real-time API integration

## Database

The application uses SQLite database (`auth_system.db`) which will be created automatically when you first run the server.

**Tables:**
- `users` - User information and credentials
- `login_attempts` - Login attempt tracking for security monitoring

## Logging System

The application implements comprehensive logging:

### Log Files:
- `auth_system.log` - Main application log file

### Logger Categories:
1. **auth_system** - General authentication system logs
2. **user_actions** - User action tracking (registration, login, logout, etc.)
3. **security** - Security events (failed logins, suspicious activity)

### Log Types:
- **REQUEST/RESPONSE** - HTTP request and response logging
- **USER_ACTION** - User behavior tracking
- **SECURITY_EVENT** - Security-related events
- **Database operations** - User creation, authentication, etc.

## Security Features

1. **Password Hashing** - Uses bcrypt for secure password storage
2. **JWT Tokens** - Secure authentication with configurable expiration
3. **CORS Protection** - Configurable cross-origin resource sharing
4. **Request Logging** - Complete request/response tracking
5. **Failed Login Tracking** - Monitors and logs failed authentication attempts
6. **IP Address Logging** - Tracks client IP addresses for security analysis
7. **User Agent Tracking** - Logs browser/client information

## Testing the System

### 1. Start the Backend
```bash
python main.py
```

### 2. Test Registration
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "TestPassword123",
       "first_name": "John",
       "last_name": "Doe"
     }'
```

### 3. Test Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "TestPassword123"
     }'
```

### 4. Test Protected Endpoint
```bash
curl -X GET "http://localhost:8000/auth/profile" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Check Logs
Monitor the `auth_system.log` file to see detailed logging information:

```bash
tail -f auth_system.log
```

## Production Considerations

1. **Change SECRET_KEY** - Use a secure, randomly generated secret key
2. **Database** - Consider using PostgreSQL or MySQL for production
3. **CORS Settings** - Restrict allowed origins to your frontend domain
4. **HTTPS** - Always use HTTPS in production
5. **Rate Limiting** - Implement rate limiting for authentication endpoints
6. **Log Rotation** - Configure log rotation to manage file sizes
7. **Environment Variables** - Store sensitive configuration in environment variables

## Monitoring User Activity

The system logs all user activities in structured JSON format. Key activities tracked:

- User registration attempts
- Login/logout events
- Profile access
- Failed authentication attempts
- Security events (weak passwords, suspicious activity)
- API request patterns

All logs include:
- Timestamp
- User email/ID
- IP address
- User agent
- Action details
- Additional metadata

This comprehensive logging system allows you to:
- Monitor user behavior
- Detect security threats
- Analyze usage patterns
- Debug authentication issues
- Maintain audit trails


------------------------------------------------------------------------------------------------------------------------------------------------------
## How to Run the Project
Backend Setup
Navigate to the backend directory:      cd backend
Install Python dependencies:            pip install -r requirements.txt
Start the FastAPI server:               python main.py

The backend will run on http://localhost:8000

## Frontend Setup
Open a new terminal and navigate to the frontend directory:     cd frontend
Install Node.js dependencies:                                   npm install
Start the React development server:                             npm start

The frontend will run on http://localhost:3000

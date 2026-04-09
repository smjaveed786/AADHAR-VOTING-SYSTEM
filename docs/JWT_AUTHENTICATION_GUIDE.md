# JWT Authentication Guide

This guide explains how JWT-based authentication works in the Voting System and how to set it up.

## What is JWT?

**JSON Web Token (JWT)** is a compact, self-contained way to transmit information between parties as a JSON object. It's digitally signed, so it can be verified and trusted.

### Token Structure

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwMzI1MDAwMH0.signature
└──────────── Header ────────────┘└───────────── Payload ──────────────┘└── Signature ──┘
```

| Part | Description |
|------|-------------|
| **Header** | Algorithm (HS256) and token type (JWT) |
| **Payload** | Data claims: `sub` (username), `exp` (expiration) |
| **Signature** | HMAC-SHA256(header + payload, secret_key) |

---

## Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production-make-it-long-and-random
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> [!CAUTION]
> **Never commit `.env` files to version control!**  
> Use `.env.example` as a template and keep actual credentials secure.

### Generating a Secure Secret Key

```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_hex(32))"

# Option 2: OpenSSL
openssl rand -hex 32

# Example output: a3b8f9e2c1d4a7b6e5f8c9d0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8
```

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    
    Note over Client,Auth: 1. Login
    Client->>API: POST /api/auth/login
    Note right of Client: {username, password}
    API->>Auth: authenticate_admin()
    Auth-->>API: True/False
    API-->>Client: {access_token, expires_in}
    
    Note over Client,Auth: 2. Protected Request
    Client->>API: GET /api/admin/voters
    Note right of Client: Header: Authorization: Bearer {token}
    API->>Auth: verify_token()
    Auth-->>API: TokenData(username)
    API-->>Client: Voter data
    
    Note over Client,Auth: 3. Token Expired
    Client->>API: GET /api/admin/voters
    API->>Auth: verify_token()
    Auth-->>API: None (expired)
    API-->>Client: 401 Unauthorized
```

---

## API Usage

### 1. Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "username": "admin"
}
```

### 2. Access Protected Routes

Include the token in the `Authorization` header:

```bash
curl -X GET http://localhost:5000/api/admin/voters \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Verify Token

```bash
curl -X GET http://localhost:5000/api/auth/verify \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "valid": true,
  "username": "admin",
  "message": "Token is valid"
}
```

---

## Frontend Integration

### React/TypeScript Example

```typescript
// Store token after login
const login = async (username: string, password: string) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Store in localStorage (or httpOnly cookie for better security)
    localStorage.setItem('token', data.access_token);
    return true;
  }
  return false;
};

// Include token in API requests
const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('token');
  
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
};

// Example: Fetch voters
const getVoters = async () => {
  const response = await fetchWithAuth('/api/admin/voters');
  return response.json();
};

// Logout
const logout = () => {
  localStorage.removeItem('token');
  window.location.href = '/admin/login';
};
```

---

## Security Best Practices

| Practice | Implementation |
|----------|----------------|
| **Use HTTPS** | Always use HTTPS in production |
| **Short Expiration** | Default 60 minutes, adjust as needed |
| **Secure Storage** | Use httpOnly cookies or secure storage |
| **Secret Key Length** | At least 256 bits (32 bytes hex) |
| **Rotate Keys** | Rotate JWT secret periodically |
| **Don't Store Sensitive Data** | Only store username in token |

> [!IMPORTANT]
> JWTs are stateless - the server cannot invalidate them before expiration.
> For logout, the client must remove the token from storage.

---

## File Structure

```
backend/
├── settings.py         # Configuration from env vars
├── auth.py             # JWT utilities and admin auth
├── app.py              # FastAPI app with get_current_admin dependency
└── api/routes/
    └── auth.py         # Login/logout/verify endpoints
```

---

## Testing Authentication

1. **Start the server:**
   ```bash
   cd backend
   uvicorn app:app --reload --port 5000
   ```

2. **Open API docs:**
   Navigate to `http://localhost:5000/docs`

3. **Test login:**
   Use the `/api/auth/login` endpoint with default credentials

4. **Use the token:**
   Click "Authorize" button, enter `Bearer {your_token}`

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid/expired token | Re-login to get new token |
| `Invalid token` | Malformed JWT | Check token format |
| `Token expired` | Exceeded `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Re-login |
| `Invalid credentials` | Wrong username/password | Check `.env` values |

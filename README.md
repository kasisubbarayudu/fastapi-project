# Memories API

A clean REST API built with **FastAPI** and **PostgreSQL** to manage personal memories and notes.

It supports user signups, logins, token authentication, and full CRUD (Create, Read, Update, Delete) operations for memories with privacy controls.

---

## Features

- **User Accounts & Login**: Register a user and log in to receive an authentication token.
- **Flexible Dual Auth**: Easily switch between local RS256 JWT authentication or AWS Cognito via configuration.
- **Memories CRUD**: Create, read, edit, and delete your memories.
- **Privacy & Security**: Users can only see, modify, or delete their own memories.
- **Search & Pagination**: Search memories by title and page through results.
- **Docker Ready**: Run the app and PostgreSQL database together using Docker Compose.
- **Testing**: Pre-configured test suite using `pytest`.

---

## Authentication Backends

The application supports two pluggable authentication modes, controlled by the `COGNITO_BACKEND` environment variable in `.env`:

### 1. Local JWT Backend (`COGNITO_BACKEND=False`)
- **How it works**: Uses **RS256 asymmetric encryption** with RSA key pairs (`private_key.pem` and `public_key.pem`).
- **Signup & Storage**: Passwords are hashed using bcrypt and stored in your local PostgreSQL database.
- **Login**: Verifies credentials against PostgreSQL, then signs an RS256 JWT token using the private key.
- **Token Verification**: Protected routes verify incoming Bearer tokens using the RSA public key.

### 2. AWS Cognito Backend (`COGNITO_BACKEND=True`)
- **How it works**: Integrates with **AWS Cognito User Pools** via `boto3`.
- **Signup**: Registers users directly in your AWS Cognito User Pool (with optional email confirmation via `POST /users/confirmSignUP`).
- **Login**: Authenticates credentials directly against AWS Cognito via `USER_PASSWORD_AUTH` flow to retrieve access tokens.
- **Account Cleanup**: Deleting a user account removes them from both local PostgreSQL and the AWS Cognito User Pool.

---

## Tech Stack

- **Backend**: Python 3.12, FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: PyJWT (RS256) / AWS Cognito (`boto3`)
- **Testing**: Pytest
- **Containerization**: Docker & Docker Compose

---

## Project Structure

```
.
├── app/
│   ├── auth/           # Login & JWT / Cognito authentication logic
│   ├── certs/          # RSA keys (private_key.pem & public_key.pem)
│   ├── routers/        # API routes (/users, /memories, /auth)
│   ├── config.py       # App configuration & .env loader
│   ├── database.py     # Database connection setup
│   ├── main.py         # Main FastAPI entrypoint
│   ├── models.py       # User & Memory database models
│   ├── oauth2.py       # Authentication middleware/dependencies
│   └── schemas.py      # Request & Response data shapes
├── tests/              # Test files
├── docker-compose.yml  # Local database & app launcher
├── Dockerfile          # Docker image build instructions
└── requirements.txt    # Python packages
```

---

## Setup & Running Locally

### 1. Prerequisites
- Python 3.12+
- PostgreSQL running locally or via Docker

### 2. Environment Variables
Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_USER=postgres
DB_PASSWD=postgres
DB_NAME=fastapi
ACCESS_TOKEN_EXPIRY_PERIOD_IN_MINUTES=60

# Authentication Mode Selection
COGNITO_BACKEND=False

# AWS Cognito Settings (required only if COGNITO_BACKEND=True)
COGNITO_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Install & Run
```bash
# Clone the repository
git clone https://github.com/your-username/fastapi-memories-api.git
cd fastapi-memories-api

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
View interactive docs at `http://localhost:8000/docs`.

---

## Running with Docker Compose

To start both the PostgreSQL database and the API container together:

```bash
docker compose up -d --build
```

To stop containers and clean up data:
```bash
docker compose down -v
```

---

## API Endpoints

### 1. Authentication (`/auth`)
- `POST /auth/login` - Send `username` (email) and `password` to receive an `access_token`.

### 2. Users (`/users`)
- `POST /users/signup` - Create a new user account.
- `POST /users/confirmSignUP` - Confirm signup (Cognito mode only).
- `GET /users/` - List registered users (requires Bearer token).
- `GET /users/{id}` - Get user profile details by ID.
- `DELETE /users/{id}` - Delete user account.

### 3. Memories (`/memories`)
- `POST /memories/` - Create a new memory (`title`, `content`).
- `GET /memories/current` - List your memories (supports `?search=...`, `?page=1`, `?Limit=10`).
- `GET /memories/{id}` - View a specific memory by ID.
- `PUT /memories/{id}` - Update title or content of a memory.
- `DELETE /memories/{id}` - Delete a memory by ID.

---

## Running Tests

To run the automated test suite:

```bash
pytest -s -v
```

---

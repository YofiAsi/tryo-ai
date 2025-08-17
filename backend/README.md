# HR Backend API

A modern, scalable HR management system built with FastAPI, MongoDB, and Celery for background task processing.

## 🚀 Features

- **FastAPI Framework**: Modern, fast web framework for building APIs with Python
- **MongoDB Integration**: Document-based database using Beanie ODM
- **Background Task Processing**: Celery workers for async CV processing
- **JWT Authentication**: Secure user authentication and authorization
- **Role-Based Access Control**: Admin and user role management
- **File Storage**: MinIO integration for document storage
- **Real-time Monitoring**: Flower dashboard for Celery task monitoring
- **Docker Support**: Containerized development environment

## 📁 Project Structure

```
hr-backend-api/
├── app/                          # Main application package
│   ├── api/                     # API route definitions
│   │   ├── admin_api.py         # Administrative endpoints
│   │   ├── candidates_api.py    # Candidate management endpoints
│   │   └── api_response.py      # Standardized API responses
│   ├── conf/                    # Configuration management
│   │   ├── app_settings.py      # Application settings
│   │   ├── celery_config.py     # Celery configuration
│   │   └── env/                 # Environment-specific configs
│   ├── consts/                  # Constants and enums
│   ├── entity/                  # Database entity models
│   ├── errors/                  # Custom exception handling
│   ├── migration/               # Database migrations
│   ├── repository/              # Data access layer
│   ├── schema/                  # Pydantic DTOs and schemas
│   ├── service/                 # Business logic layer
│   ├── utils/                   # Utility functions
│   ├── workers/                 # Celery worker tasks
│   └── main.py                  # FastAPI application entry point
├── configs/                     # Configuration files
├── docker-compose-dev.yml       # Development environment setup
├── main_dev.py                  # Development server entry point
├── celery_worker.py             # Celery worker entry point
├── requirements.txt              # Python dependencies
└── CELERY_README.md             # Celery setup documentation
```

## 🛠️ Prerequisites

- **Python 3.8+**
- **Docker & Docker Compose**
- **MongoDB** (via Docker)
- **Redis** (via Docker)
- **MinIO** (via Docker)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hr-backend-api
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the `configs/` directory:

```bash
# Database Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=hr_backend

# Redis Configuration
REDIS_URL=redis://localhost:6379

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Application Settings
APP_NAME=HR Backend API
APP_DESCRIPTION=Human Resources Management System
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

### 5. Start Infrastructure Services

```bash
docker-compose -f docker-compose-dev.yml up -d
```

This will start:
- **MongoDB** on port 27017
- **Redis** on port 6379
- **MinIO** on ports 9000 (API) and 9001 (Console)
- **Flower** (Celery monitoring) on port 5555

### 6. Start the Application

#### Option A: Using the Development Script
```bash
python main_dev.py
```

#### Option B: Using Uvicorn Directly
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Start Celery Worker (Optional)

For background task processing:

```bash
python celery_worker.py
```

## 🌐 API Endpoints

Once running, access the API at:

- **API Base URL**: `http://localhost:8000/api/v1`
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/v1/health`

### Available Endpoints

- **Authentication**: `/auth/*`
- **User Management**: `/users/*`
- **Candidate Management**: `/candidates/*`
- **Administrative**: `/admin/*`
- **Account Operations**: `/account/*`

## 🔧 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Quality

```bash
# Install development tools
pip install black isort flake8

# Format code
black app/
isort app/

# Lint code
flake8 app/
```

### Database Migrations

The application automatically runs migrations on startup. To manually trigger:

```python
from app.migration.user_migration import init_migration
await init_migration()
```

## 🐳 Docker Development

### Start All Services

```bash
docker-compose -f docker-compose-dev.yml up -d
```

### View Logs

```bash
# All services
docker-compose -f docker-compose-dev.yml logs -f

# Specific service
docker-compose -f docker-compose-dev.yml logs -f mongo
```

### Stop Services

```bash
docker-compose -f docker-compose-dev.yml down
```

### Clean Up Volumes

```bash
docker-compose -f docker-compose-dev.yml down -v
```

## 📊 Monitoring

### Celery Task Monitoring

Access the Flower dashboard at `http://localhost:5555` to monitor:
- Active workers
- Task queues
- Task execution history
- Worker performance

### Application Logs

Check the application logs for debugging information:
- FastAPI logs in the console
- Celery worker logs in the terminal
- Database logs via Docker

## 🔒 Security

- **CORS**: Configured for development and production
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Admin and user role management
- **Input Validation**: Pydantic models for request validation

## 🚀 Production Deployment

### Environment Variables

Set production environment variables:
```bash
export ENVIRONMENT=production
export MONGODB_URL=<production-mongodb-url>
export REDIS_URL=<production-redis-url>
export SECRET_KEY=<secure-secret-key>
```

### Docker Production

```bash
# Build production image
docker build -t hr-backend-api .

# Run production container
docker run -p 8000:8000 hr-backend-api
```

### Scaling

- **Multiple Workers**: Scale Celery workers based on load
- **Load Balancing**: Use nginx or similar for API load balancing
- **Database**: Consider MongoDB Atlas for managed database
- **Caching**: Implement Redis caching for frequently accessed data

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB container is running
   - Check connection string in environment variables

2. **Redis Connection Error**
   - Verify Redis container is running
   - Check Redis URL configuration

3. **Port Already in Use**
   - Change ports in docker-compose file
   - Kill processes using the ports

4. **Celery Worker Not Processing**
   - Check Redis connection
   - Verify worker is running and connected

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --log-level debug
```

## 📚 Additional Documentation

- **Celery Setup**: See `CELERY_README.md` for detailed Celery configuration
- **API Documentation**: Interactive docs available at `/docs` endpoint
- **Code Comments**: Inline documentation throughout the codebase

---

**Happy Coding! 🎉**

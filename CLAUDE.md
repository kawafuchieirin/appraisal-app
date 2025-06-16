# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Real estate appraisal application using Django (UI) + FastAPI (ML API) with single container architecture. Uses multiple regression analysis for property valuation.

## Architecture

### Service Architecture
- **Django (Port 8080)**: Frontend UI service - forms, results display, error handling
- **FastAPI (Port 8000)**: ML prediction API - regression model inference
- **Communication**: Django makes HTTP requests to FastAPI endpoint
- **Local**: Independent Docker containers (no docker-compose)
- **Production**: ECR → Lambda + API Gateway

### Key Architectural Patterns
- **Model Serving**: Models packaged in FastAPI container, loaded at startup
- **Error Handling**: Graceful degradation when API unavailable
- **Environment Config**: Feature toggles via USE_MODEL_API env var
- **Docker Networking**: Uses host.docker.internal for container communication

## Commands

### Development
```bash
# Start both services with health checks (recommended)
./deploy/run_dev.sh

# Start individual services
./deploy/run_fastapi.sh [port] [environment]
./deploy/run_django.sh [port] [environment]

# Model training
cd model_create && python train_model.py

# Run integration tests
cd django_app && python test_integration.py
cd fastapi_app && python test_api.py
```

### Testing
```bash
# Test Django-FastAPI integration flow
python django_app/test_integration.py

# Test API endpoints directly
python fastapi_app/test_api.py

# Manual API test
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]}'
```

### Deployment
```bash
# Deploy to ECR/Lambda
./deploy/push_to_ecr.sh ap-northeast-1 fastapi
./deploy/push_to_ecr.sh ap-northeast-1 django
./deploy/push_to_ecr.sh ap-northeast-1 all

# Build for Lambda (linux/amd64 required)
docker build --platform linux/amd64 -t app-name .
```

## Code Architecture

### Django App Structure
- `valuation/views.py`: Form handling, API calls to FastAPI
- `valuation/forms.py`: Property valuation input form
- `valuation/templates/`: UI templates (base.html, index.html, result.html)
- `settings.py`: Environment-based config, API endpoint settings

### FastAPI Structure
- `main.py`: API endpoints, CORS config, health checks
- `model_loader.py`: ML model lifecycle management
- `predict_schema.py`: Request/response validation schemas
- `lambda_handler.py`: AWS Lambda integration using Mangum

### Model Training
- `train_model.py`: Creates model.joblib, scaler.joblib, feature_info.joblib
- `create_sample_data.py`: Test data generation
- Models stored in `models/` directory

## Environment Configuration

### Key Environment Variables
- `USE_MODEL_API`: Toggle between API and mock predictions
- `API_ENDPOINT`: FastAPI service URL
- `API_TIMEOUT`: Request timeout in seconds
- `ALLOWED_HOSTS`: Django security setting
- `CORS_ORIGINS`: FastAPI CORS configuration

### Environment Files
- `deploy/.env.development`: Local development settings
- `deploy/.env.production`: Production Lambda settings

## Development Workflow

### Adding New Features
1. Update model if needed: `model_create/train_model.py`
2. Add API endpoint: `fastapi_app/main.py`
3. Update Django form/view: `django_app/valuation/`
4. Test integration: `python test_integration.py`

### Model Updates
1. Modify training in `model_create/train_model.py`
2. Retrain and save new model files
3. Restart FastAPI to load new model
4. Test predictions via API

### Docker Development
- Development Dockerfiles use volume mounts for hot-reload
- Production Dockerfiles optimized for Lambda size/performance
- Always specify `--platform linux/amd64` for Lambda builds

## Important Notes

### Security
- CSRF protection enabled in Django
- CORS restrictions configured per environment
- Never commit `.env` files with real credentials

### Performance
- Models loaded once at FastAPI startup
- Feature standardization happens at prediction time
- Lambda cold starts mitigated by container reuse

### Testing Approach
- Integration tests verify full Django→FastAPI flow
- Session-based CSRF handling in tests
- Health check verification before testing

### Cleanup Policy
When making changes:
- Remove unused imports and dead code
- Delete temporary test files
- Clean up old Docker images
- Remove commented code older than current session

Use cleanup commands:
```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
rm -rf .pytest_cache/ .coverage htmlcov/
```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Real estate appraisal application using Django (UI) + FastAPI (ML API) with single container architecture. Uses multiple regression analysis for property valuation.

## Architecture

### Service Architecture
- **Django (Port 8000)**: Frontend UI service - forms, results display, error handling
- **FastAPI (Port 8000)**: ML prediction API - regression model inference
- **Communication**: Django makes HTTP requests to FastAPI endpoint via ALB
- **Local**: Independent Docker containers (no docker-compose)
- **Production**: ECR → ECS Fargate + ALB (CloudFormation managed)

### Key Architectural Patterns
- **Model Serving**: Models packaged in FastAPI container, loaded at startup
- **Error Handling**: Graceful degradation when API unavailable
- **Environment Config**: Feature toggles via USE_MODEL_API env var
- **Production Networking**: ALB routes traffic between Django and FastAPI services
- **Infrastructure as Code**: All AWS resources managed via CloudFormation

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
# Deploy to ECR/ECS
./deploy/push_to_ecr.sh ap-northeast-1 fastapi
./deploy/push_to_ecr.sh ap-northeast-1 django
./deploy/push_to_ecr.sh ap-northeast-1 all

# Deploy AWS infrastructure
aws cloudformation deploy --template-file deploy/cloudformation-template.yaml \
  --stack-name satei-app-v2 --capabilities CAPABILITY_IAM

# Build for ECS (linux/amd64 required)
docker build --platform linux/amd64 -f django_app/Dockerfile.ecs -t app-name .
docker build --platform linux/amd64 -f fastapi_app/Dockerfile.ecs -t app-name .

# Cleanup AWS resources
./deploy/cleanup_aws_resources.sh
python3 deploy/cleanup_individual_resources.py
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
- `Dockerfile.ecs`: ECS Fargate deployment configuration

### Model Training
- `train_model.py`: Creates model.joblib, scaler.joblib, feature_info.joblib
- `create_sample_data.py`: Test data generation
- Models stored in `models/` directory

## Environment Configuration

### Key Environment Variables
- `USE_MODEL_API`: Toggle between API and mock predictions
- `API_ENDPOINT`: FastAPI service URL (ALB DNS for production)
- `API_TIMEOUT`: Request timeout in seconds
- `ALLOWED_HOSTS`: Django security setting (ALB DNS for production)
- `CORS_ORIGINS`: FastAPI CORS configuration
- `SECRET_KEY`: Django secret key for production
- `DEBUG`: Django debug mode toggle
- `ENVIRONMENT`: Environment name (development/production)

### Environment Files
- `deploy/.env.development`: Local development settings
- `deploy/.env.production`: Production ECS settings
- `deploy/django-ecs-task-definition.json`: Django ECS task configuration
- `deploy/fastapi-ecs-task-definition.json`: FastAPI ECS task configuration
- `deploy/cloudformation-template.yaml`: AWS infrastructure definition

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
- Production Dockerfiles optimized for ECS Fargate performance
- Always specify `--platform linux/amd64` for ECS builds
- Separate Dockerfiles: `Dockerfile.dev` (development), `Dockerfile.ecs` (production)

## Important Notes

### Security
- CSRF protection enabled in Django (ALB-compatible settings)
- CORS restrictions configured per environment
- Never commit `.env` files with real credentials
- Security groups restrict access to ECS tasks
- ALB terminates SSL/TLS connections

### Performance
- Models loaded once at FastAPI startup
- Feature standardization happens at prediction time
- ECS Fargate provides consistent performance
- ALB load balancing across multiple tasks

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
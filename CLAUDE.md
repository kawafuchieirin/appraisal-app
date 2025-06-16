# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Real estate appraisal application using Django (UI) + FastAPI (ML API) with single container architecture.

## Architecture

- **Django**: Frontend UI (forms, results display, error handling) - `django_app/`
- **FastAPI**: ML prediction API using regression models - `fastapi_app/`  
- **ML Model**: Multiple regression analysis - `model_create/`
- **Local**: Single Docker containers (no docker-compose)
- **Production**: ECR → Lambda + API Gateway for both services

## Directory Structure

```
appraisal-app/
├── django_app/       # Django application
├── fastapi_app/      # FastAPI prediction API (Lambda-ready)
├── model_create/     # ML model training and storage
└── deploy/           # All deployment and configuration files
    ├── lambda/       # Lambda deployment files
    ├── .env.development  # Development environment variables
    ├── .env.production   # Production environment variables
    ├── run_dev.sh    # Development environment (both services)
    ├── run_django.sh # Django single container
    ├── run_fastapi.sh# FastAPI single container
    └── push_to_ecr.sh# ECR deployment script
```

## Development Commands

### Local Development
```bash
# Start both services (recommended)
./deploy/run_dev.sh

# Start individual services
./deploy/run_fastapi.sh [port] [environment]
./deploy/run_django.sh [port] [environment]

# Access URLs
# Django: http://localhost:8080
# FastAPI: http://localhost:8000
```

### Model Training
```bash
# Train and save regression model
python model_create/train_model.py
```

### API Testing
```bash
# Test FastAPI prediction endpoint
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"features": [...]}'  
```

### Production Deployment
```bash
# Build and push to ECR
./deploy/push_to_ecr.sh [region] [service]

# Deploy specific service
./deploy/push_to_ecr.sh ap-northeast-1 fastapi
./deploy/push_to_ecr.sh ap-northeast-1 django

# Deploy all services
./deploy/push_to_ecr.sh ap-northeast-1 all
```

## Development Priority

1. Model creation (`model_create/train_model.py`, `model.joblib`)
2. FastAPI prediction API (`fastapi_app/main.py`, `model_loader.py`)
3. Django UI (`django_app/valuation/views.py`, `templates/valuation/`)
4. Local single container setup (`deploy/run_*.sh`)
5. Lambda deployment configuration (`deploy/push_to_ecr.sh`)

## Code Cleanup Guidelines

### Cleanup Policy
Always remove unused code, resources, and files when:
- Replacing implementations with new approaches
- Refactoring components or modules
- Switching to different libraries or frameworks
- Completing experimental or temporary solutions

### What to Clean Up
- **Unused imports and dependencies** in requirements.txt, package.json
- **Dead code** - functions, classes, variables that are no longer called
- **Commented-out code blocks** older than current development session
- **Temporary files** - test data, debug outputs, backup files
- **Deprecated configuration** - old environment variables, config files
- **Sample/mock data** when replaced with real data sources
- **Development scripts** that are no longer needed

### Cleanup Commands
```bash
# Remove unused Python packages
pip-autoremove -y

# Clean up temporary files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name ".DS_Store" -delete

# Remove development artifacts
rm -rf .pytest_cache/ .coverage htmlcov/
```

### File Management
- Delete test/sample data files when real data is implemented
- Remove temporary scripts after functionality is integrated
- Clean up old Docker images and containers periodically
- Remove unused configuration files and templates
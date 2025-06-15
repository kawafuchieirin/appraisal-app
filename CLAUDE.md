# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Real estate appraisal application using Django (UI) + FastAPI (ML API) with multi-container architecture.

## Architecture

- **Django**: Frontend UI (forms, results display, error handling) - `main_app/`
- **FastAPI**: ML prediction API using regression models - `ssessment/`  
- **ML Model**: Multiple regression analysis - `model_create/`
- **Local**: docker-compose multi-container setup
- **Production**: FastAPI → ECR → Lambda + API Gateway, Django → S3/CloudFront or Fargate

## Directory Structure

```
app/
├── main_app/         # Django application
├── ssessment/        # FastAPI prediction API (Lambda-ready)
├── model_create/     # ML model training and storage
├── deploy/           
│   ├── local/        # docker-compose setup
│   └── lambda/       # Lambda deployment files
```

## Development Commands

### Local Development
```bash
# Start all services
docker-compose -f deploy/local/docker-compose.yml up

# Rebuild containers
docker-compose -f deploy/local/docker-compose.yml up --build
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

### Lambda Deployment
```bash
# Build and push to ECR
bash deploy/lambda/push.sh
```

## Development Priority

1. Model creation (`model_create/train_model.py`, `model.joblib`)
2. FastAPI prediction API (`ssessment/main.py`, `ml_model_loader.py`)
3. Django UI (`main_app/views.py`, `templates/form.html`)
4. Local docker-compose setup
5. Lambda deployment configuration

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
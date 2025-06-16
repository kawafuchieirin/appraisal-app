#!/bin/bash

# Django Development Container Runner
# Usage: ./run_django.sh [port] [environment]

set -e

# Default values
PORT=${1:-8080}
ENV=${2:-development}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Django Development Container${NC}"
echo "Port: ${PORT}"
echo "Environment: ${ENV}"

# Build Django image
echo -e "${YELLOW}🔨 Building Django image...${NC}"
cd ..
docker build -f django_app/Dockerfile.dev -t satei-django:dev .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Run Django container
echo -e "${BLUE}🐳 Starting Django container...${NC}"
docker run -it --rm \
    --name satei-django-dev \
    -p ${PORT}:8000 \
    -v $(pwd)/django_app:/app/django_app \
    -v $(pwd)/deploy/.env.${ENV}:/app/.env \
    --env-file deploy/.env.${ENV} \
    satei-django:dev

echo -e "${GREEN}✅ Django container stopped${NC}"
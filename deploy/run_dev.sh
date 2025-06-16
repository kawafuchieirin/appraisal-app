#!/bin/bash

# Development Environment Runner
# Starts both Django and FastAPI containers
# Usage: ./run_dev.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Development Environment${NC}"
echo "FastAPI: http://localhost:8000"
echo "Django: http://localhost:8080"

# Function to cleanup containers on exit
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up containers...${NC}"
    docker stop satei-fastapi-dev satei-django-dev 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start FastAPI in background
echo -e "${BLUE}🐳 Starting FastAPI container...${NC}"
cd ..
docker build -f fastapi_app/Dockerfile.dev -t satei-fastapi:dev . > /dev/null 2>&1

docker run -d --rm \
    --name satei-fastapi-dev \
    -p 8000:8000 \
    -v $(pwd)/fastapi_app:/app/fastapi_app \
    -v $(pwd)/model_create/models:/app/models \
    -v $(pwd)/deploy/.env.development:/app/.env \
    --env-file deploy/.env.development \
    satei-fastapi:dev

# Wait for FastAPI to be ready
echo -e "${YELLOW}⏳ Waiting for FastAPI to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ FastAPI is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ FastAPI failed to start${NC}"
        exit 1
    fi
    sleep 1
done

# Start Django in foreground
echo -e "${BLUE}🐳 Starting Django container...${NC}"
docker build -f django_app/Dockerfile.dev -t satei-django:dev . > /dev/null 2>&1

docker run -d --rm \
    --name satei-django-dev \
    -p 8080:8000 \
    -v $(pwd)/django_app:/app/django_app \
    -v $(pwd)/deploy/.env.development:/app/.env \
    --env-file deploy/.env.development \
    satei-django:dev

# Keep script running and show logs
echo -e "${GREEN}✅ Both services started successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Service URLs:${NC}"
echo "  FastAPI: http://localhost:8000"
echo "  Django:  http://localhost:8080"
echo ""
echo -e "${YELLOW}📝 Press Ctrl+C to stop all services${NC}"

# Follow Django logs to keep script alive
docker logs -f satei-django-dev
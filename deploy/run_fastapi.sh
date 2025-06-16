#!/bin/bash

# FastAPI Development Container Runner
# Usage: ./run_fastapi.sh [port] [environment]

set -e

# Default values
PORT=${1:-8000}
ENV=${2:-development}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting FastAPI Development Container${NC}"
echo "Port: ${PORT}"
echo "Environment: ${ENV}"

# Build FastAPI image
echo -e "${YELLOW}🔨 Building FastAPI image...${NC}"
cd ..
docker build -f fastapi_app/Dockerfile.dev -t satei-fastapi:dev .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Run FastAPI container
echo -e "${BLUE}🐳 Starting FastAPI container...${NC}"
docker run -it --rm \
    --name satei-fastapi-dev \
    -p ${PORT}:8000 \
    -v $(pwd)/fastapi_app:/app/fastapi_app \
    -v $(pwd)/model_create/models:/app/models \
    -v $(pwd)/deploy/.env.${ENV}:/app/.env \
    --env-file deploy/.env.${ENV} \
    satei-fastapi:dev

echo -e "${GREEN}✅ FastAPI container stopped${NC}"
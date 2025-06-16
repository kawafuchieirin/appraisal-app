#!/bin/bash

# Unified ECR Push Script for Django + FastAPI Lambda Services
# Usage: ./push_to_ecr.sh [AWS_REGION] [SERVICE_NAME]

set -e

# Default values
AWS_REGION=${1:-"ap-northeast-1"}
SERVICE_NAME=${2:-"all"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Unified ECR Deployment${NC}"
echo "Region: ${AWS_REGION}"
echo "Service: ${SERVICE_NAME}"

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to get AWS Account ID. Check AWS credentials.${NC}"
    exit 1
fi

echo "Account ID: ${AWS_ACCOUNT_ID}"

# Login to ECR
echo -e "${YELLOW}🔐 Logging into ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ECR login failed${NC}"
    exit 1
fi

# Function to build and push service
build_and_push_service() {
    local service=$1
    local repo_name="satei-${service}"
    local ecr_uri="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${repo_name}"
    
    echo -e "${BLUE}📦 Processing ${service} service${NC}"
    
    # Check if ECR repository exists, create if not
    aws ecr describe-repositories --repository-names ${repo_name} --region ${AWS_REGION} > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Creating ECR repository: ${repo_name}${NC}"
        aws ecr create-repository \
            --repository-name ${repo_name} \
            --region ${AWS_REGION} \
            --image-scanning-configuration scanOnPush=true
    else
        echo -e "${GREEN}✅ ECR repository exists: ${repo_name}${NC}"
    fi
    
    # Build Docker image
    echo -e "${YELLOW}🔨 Building ${service} Docker image...${NC}"
    docker build -f ${service}_app/Dockerfile -t ${repo_name}:latest .
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Docker build failed for ${service}${NC}"
        return 1
    fi
    
    # Tag and push image
    echo -e "${YELLOW}🏷️ Tagging and pushing ${service} image...${NC}"
    docker tag ${repo_name}:latest ${ecr_uri}:latest
    
    # Generate timestamp tag
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    docker tag ${repo_name}:latest ${ecr_uri}:${TIMESTAMP}
    
    # Push images
    docker push ${ecr_uri}:latest
    docker push ${ecr_uri}:${TIMESTAMP}
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ ECR push failed for ${service}${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ ${service} service deployed successfully${NC}"
    echo "  Latest: ${ecr_uri}:latest"
    echo "  Tagged: ${ecr_uri}:${TIMESTAMP}"
}

# Deploy based on service parameter
case ${SERVICE_NAME} in
    "django")
        build_and_push_service "django"
        ;;
    "fastapi")
        build_and_push_service "fastapi"
        ;;
    "all")
        echo -e "${BLUE}🚀 Deploying all services${NC}"
        build_and_push_service "fastapi"
        build_and_push_service "django"
        ;;
    *)
        echo -e "${RED}❌ Unknown service: ${SERVICE_NAME}${NC}"
        echo "Available services: django, fastapi, all"
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 ECR deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "  1. Deploy Lambda functions:"
echo "     aws lambda create-function --function-name satei-django --package-type Image --code ImageUri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/satei-django:latest"
echo "     aws lambda create-function --function-name satei-fastapi --package-type Image --code ImageUri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/satei-fastapi:latest"
echo ""
echo "  2. Set up API Gateway integration"
echo "  3. Configure environment variables"
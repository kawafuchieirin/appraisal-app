#!/bin/bash

# AWS Lambda + API Gateway Deployment Script
# Usage: ./deploy/deploy_lambda.sh [AWS_REGION] [FUNCTION_NAME]

set -e

# Default values
AWS_REGION=${1:-"ap-northeast-1"}
FUNCTION_NAME=${2:-"satei-api"}
ECR_REPO_NAME=${FUNCTION_NAME}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Lambda + API Gateway deployment${NC}"

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest"

# IAM Role ARN (assume it exists or create manually)
ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/lambda-execution-role"

echo -e "${YELLOW}📋 Deployment Configuration:${NC}"
echo "  Region: ${AWS_REGION}"
echo "  Function: ${FUNCTION_NAME}"
echo "  ECR Image: ${ECR_URI}"
echo "  IAM Role: ${ROLE_ARN}"

# Check if Lambda function exists
echo -e "${YELLOW}🔍 Checking Lambda function...${NC}"

aws lambda get-function --function-name ${FUNCTION_NAME} --region ${AWS_REGION} > /dev/null 2>&1
FUNCTION_EXISTS=$?

if [ ${FUNCTION_EXISTS} -ne 0 ]; then
    echo -e "${YELLOW}Creating Lambda function: ${FUNCTION_NAME}${NC}"
    
    # Create Lambda function
    aws lambda create-function \
        --function-name ${FUNCTION_NAME} \
        --package-type Image \
        --code ImageUri=${ECR_URI} \
        --role ${ROLE_ARN} \
        --timeout 30 \
        --memory-size 1024 \
        --environment Variables='{USE_MODEL_API=true,AWS_LWA_PORT=8000,AWS_LWA_READINESS_CHECK_PATH=/health}' \
        --region ${AWS_REGION}
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Lambda function created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create Lambda function${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Updating existing Lambda function: ${FUNCTION_NAME}${NC}"
    
    # Update Lambda function code
    aws lambda update-function-code \
        --function-name ${FUNCTION_NAME} \
        --image-uri ${ECR_URI} \
        --region ${AWS_REGION}
    
    # Update Lambda function configuration
    aws lambda update-function-configuration \
        --function-name ${FUNCTION_NAME} \
        --timeout 30 \
        --memory-size 1024 \
        --environment Variables='{USE_MODEL_API=true,AWS_LWA_PORT=8000,AWS_LWA_READINESS_CHECK_PATH=/health}' \
        --region ${AWS_REGION}
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Lambda function updated successfully${NC}"
    else
        echo -e "${RED}❌ Failed to update Lambda function${NC}"
        exit 1
    fi
fi

# Wait for function to be active
echo -e "${YELLOW}⏳ Waiting for function to be active...${NC}"
aws lambda wait function-active --function-name ${FUNCTION_NAME} --region ${AWS_REGION}

# Create or update API Gateway
API_NAME="${FUNCTION_NAME}-api"
echo -e "${YELLOW}🌐 Setting up API Gateway: ${API_NAME}${NC}"

# Check if API Gateway exists
API_ID=$(aws apigatewayv2 get-apis --region ${AWS_REGION} --query "Items[?Name=='${API_NAME}'].ApiId" --output text)

if [ -z "${API_ID}" ] || [ "${API_ID}" == "None" ]; then
    echo -e "${YELLOW}Creating API Gateway: ${API_NAME}${NC}"
    
    # Create API Gateway
    API_RESPONSE=$(aws apigatewayv2 create-api \
        --name ${API_NAME} \
        --protocol-type HTTP \
        --cors-configuration AllowCredentials=false,AllowHeaders="*",AllowMethods="*",AllowOrigins="*" \
        --region ${AWS_REGION})
    
    API_ID=$(echo ${API_RESPONSE} | jq -r '.ApiId')
    echo -e "${GREEN}✅ API Gateway created with ID: ${API_ID}${NC}"
else
    echo -e "${GREEN}✅ Using existing API Gateway: ${API_ID}${NC}"
fi

# Create Lambda integration
echo -e "${YELLOW}🔗 Creating Lambda integration...${NC}"

INTEGRATION_RESPONSE=$(aws apigatewayv2 create-integration \
    --api-id ${API_ID} \
    --integration-type AWS_PROXY \
    --integration-uri "arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:function:${FUNCTION_NAME}" \
    --payload-format-version 2.0 \
    --region ${AWS_REGION})

INTEGRATION_ID=$(echo ${INTEGRATION_RESPONSE} | jq -r '.IntegrationId')

# Create routes
echo -e "${YELLOW}🛣️ Creating API routes...${NC}"

# Create ANY /{proxy+} route
aws apigatewayv2 create-route \
    --api-id ${API_ID} \
    --route-key 'ANY /{proxy+}' \
    --target integrations/${INTEGRATION_ID} \
    --region ${AWS_REGION}

# Create default stage
echo -e "${YELLOW}🎭 Creating default stage...${NC}"

aws apigatewayv2 create-stage \
    --api-id ${API_ID} \
    --stage-name '$default' \
    --auto-deploy \
    --region ${AWS_REGION} > /dev/null 2>&1 || true

# Add Lambda permission for API Gateway
echo -e "${YELLOW}🔑 Adding Lambda permission...${NC}"

aws lambda add-permission \
    --function-name ${FUNCTION_NAME} \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${AWS_REGION}:${AWS_ACCOUNT_ID}:${API_ID}/*/*" \
    --region ${AWS_REGION} > /dev/null 2>&1 || true

# Get API Gateway endpoint
API_ENDPOINT="https://${API_ID}.execute-api.${AWS_REGION}.amazonaws.com"

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Deployment Summary:${NC}"
echo "  Lambda Function: ${FUNCTION_NAME}"
echo "  API Gateway ID: ${API_ID}"
echo "  API Endpoint: ${API_ENDPOINT}"
echo ""
echo -e "${BLUE}🧪 Test Commands:${NC}"
echo "  Health Check:"
echo "    curl ${API_ENDPOINT}/health"
echo ""
echo "  Prediction Test:"
echo "    curl -X POST ${API_ENDPOINT}/predict \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"building_area\":80,\"land_area\":120,\"building_age\":10,\"ward_name\":\"世田谷区\",\"year\":2024,\"quarter\":1}'"
echo ""
echo -e "${BLUE}🔧 Django Configuration:${NC}"
echo "  Update Django .env file:"
echo "    FASTAPI_URL=${API_ENDPOINT}"
echo "    USE_MODEL_API=true"
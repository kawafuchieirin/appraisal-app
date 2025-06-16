# FastAPI Lambda Deployment Dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Install system dependencies
RUN yum update -y && yum install -y gcc gcc-c++ curl

# No Lambda Web Adapter needed - using Mangum for native Lambda integration

# Copy requirements and install dependencies
COPY fastapi_app/requirements.txt .
RUN pip install --upgrade pip && \
    pip install numpy==1.24.3 && \
    pip install -r requirements.txt

# Copy FastAPI application
COPY fastapi_app/ .

# Copy ML models
COPY model_create/models/ ./models/

# Default command - Lambda handler with Mangum
CMD ["main.handler"]
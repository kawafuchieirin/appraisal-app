# FastAPI Lambda Deployment Dockerfile  
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Remove the default lambda-adapter extension
RUN rm -f /opt/extensions/lambda-adapter

# Copy requirements and install dependencies
COPY ../../ssessment/requirements.txt .

# Install build dependencies and system packages
RUN yum update -y && yum install -y gcc gcc-c++

# Install Python packages with specific numpy version for Lambda
RUN pip install --upgrade pip && \
    pip install numpy==1.24.3 && \
    pip install -r requirements.txt

# Copy FastAPI application
COPY ../../ssessment/ .

# Copy ML models
COPY ../../model_create/models/ ./models/

# Default command - use Lambda handler
CMD ["lambda_handler.handler"]
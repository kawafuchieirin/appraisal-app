# Django Lambda Deployment Dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Install system dependencies
RUN yum update -y && yum install -y curl

# Install Lambda Web Adapter v0.7.0 (stable version)
RUN curl -Lo /opt/bootstrap https://github.com/awslabs/aws-lambda-web-adapter/releases/download/v0.7.0/bootstrap-linux-x86_64 && \
    chmod +x /opt/bootstrap

# Copy requirements and install dependencies
COPY django_app/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy Django application
COPY django_app/ .

# Set environment variables for Lambda Web Adapter
ENV AWS_LWA_PORT=8000
ENV AWS_LWA_READINESS_CHECK_PATH=/health/
ENV AWS_LWA_REMOVE_BASE_PATH=/

# Expose port
EXPOSE 8000

# Default command - Django with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "0", "django_app.wsgi:application"]
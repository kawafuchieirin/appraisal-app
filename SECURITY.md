# Security Guidelines

This document outlines the security measures implemented in the Real Estate Appraisal Application.

## Security Improvements

### 1. Secret Management
- **Django SECRET_KEY**: Now loaded from environment variables, not hardcoded
- **Production secrets**: Should be stored in AWS Secrets Manager, not in .env files
- **Environment files**: .env files are git-ignored, use .env.example as template

### 2. Debug Mode Control
- **DEBUG setting**: Controlled by environment variable (defaults to False)
- **Production**: Always set DEBUG=false in production

### 3. CORS Configuration
- **Restricted origins**: CORS now restricts allowed origins based on environment
- **Limited methods**: Only allows GET and POST methods
- **Limited headers**: Only allows necessary headers (Content-Type, Authorization)

### 4. Django Security Headers
- **XSS Protection**: Enabled via SECURE_BROWSER_XSS_FILTER
- **Content Type**: Enabled via SECURE_CONTENT_TYPE_NOSNIFF
- **Frame Options**: Set to DENY to prevent clickjacking
- **HTTPS**: SSL redirect and secure cookies in production

### 5. ALLOWED_HOSTS
- **Development**: Set to localhost and 127.0.0.1
- **Production**: Must be set to specific domain names

## Best Practices

### Environment Variables
```bash
# Development
export DEBUG=true
export SECRET_KEY="dev-only-secret-key"
export ALLOWED_HOSTS="localhost,127.0.0.1"
export CORS_ORIGINS="http://localhost:8080"

# Production (use AWS Secrets Manager)
export DEBUG=false
export SECRET_KEY="$(aws secretsmanager get-secret-value --secret-id satei-app/django-secret-key --query SecretString --output text)"
export ALLOWED_HOSTS="your-domain.com,www.your-domain.com"
export CORS_ORIGINS="https://your-domain.com,https://www.your-domain.com"
```

### Generating a New SECRET_KEY
```bash
# Generate a new Django secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Store in AWS Secrets Manager
aws secretsmanager create-secret \
    --name satei-app/django-secret-key \
    --secret-string "your-generated-secret-key"
```

### Security Checklist for Deployment

- [ ] Generate new SECRET_KEY for production
- [ ] Store secrets in AWS Secrets Manager
- [ ] Set DEBUG=false
- [ ] Configure ALLOWED_HOSTS with actual domains
- [ ] Configure CORS_ORIGINS with actual domains
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Review and remove any test/debug endpoints
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerting

## Reporting Security Issues

If you discover a security vulnerability, please report it to the maintainers privately. Do not create public issues for security vulnerabilities.

## Additional Recommendations

1. **Regular Updates**: Keep all dependencies updated for security patches
2. **Dependency Scanning**: Use tools like `pip-audit` to scan for vulnerabilities
3. **Code Review**: All code changes should be reviewed for security implications
4. **API Authentication**: Consider adding API key or JWT authentication for the prediction API
5. **Rate Limiting**: Implement rate limiting to prevent abuse
6. **WAF**: Consider using AWS WAF for additional protection
7. **Monitoring**: Set up security monitoring and alerting for suspicious activities
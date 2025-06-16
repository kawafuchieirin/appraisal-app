"""
Lambda handler for FastAPI application
"""

import json
import base64
from main import app
from mangum import Mangum

# Create Mangum handler for Lambda
handler = Mangum(app, lifespan="off")
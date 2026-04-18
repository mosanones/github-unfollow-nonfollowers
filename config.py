import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# GitHub configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'your_token_here')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'your_username_here')

# API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.github.com')
REQUEST_TIMEOUT = int(os.getenv('API_TIMEOUT', 10))  # seconds
RATE_LIMIT_SLEEP = float(os.getenv('RATE_LIMIT_SLEEP', 3.0))  # increased to 3s to stay well within rate limits

# Application settings
PREVIEW_MODE_DEFAULT = True  # Preview by default for safety
MAX_RETRIES = 5  # bumped up retries since GitHub API can be flaky sometimes

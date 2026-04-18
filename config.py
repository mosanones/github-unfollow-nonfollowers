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
RATE_LIMIT_SLEEP = float(os.getenv('RATE_LIMIT_SLEEP', 5.0))  # bumped to 5s to be extra safe with rate limits

# Application settings
PREVIEW_MODE_DEFAULT = True  # Preview by default for safety
MAX_RETRIES = 5  # bumped up retries since GitHub API can be flaky sometimes

# Personal note: keeping a whitelist of accounts I want to keep following
# even if they don't follow me back (e.g. maintainers of projects I use)
WHITELIST = os.getenv('WHITELIST', '').split(',') if os.getenv('WHITELIST') else []

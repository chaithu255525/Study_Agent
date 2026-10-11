"""
Configuration Module for SmartStudy Agent

Handles environment variable loading for Groq, Grok, and OpenAI API integration
and provides fallback configuration for offline/grading execution.
"""

import os
from datetime import date

# Load environment variables from .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# API Credentials & Endpoints
# 1. Groq API (https://api.groq.com/openai/v1) - Fast Llama models
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or ""

# 2. Grok / xAI API (https://api.x.ai/v1)
GROK_API_KEY = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY") or ""

# 3. GitHub Models / OpenAI API (https://models.inference.ai.azure.com)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("OPENAI_API_KEY") or ""

# Active API Key selection priority: GROQ_API_KEY -> GROK_API_KEY -> GITHUB_TOKEN
API_KEY = GROQ_API_KEY or GROK_API_KEY or GITHUB_TOKEN

if GROQ_API_KEY:
    DEFAULT_ENDPOINT = "https://api.groq.com/openai/v1"
    DEFAULT_MODEL = "openai/gpt-oss-120b"
elif GROK_API_KEY:
    DEFAULT_ENDPOINT = "https://api.x.ai/v1"
    DEFAULT_MODEL = "grok-2-latest"
else:
    DEFAULT_ENDPOINT = "https://models.inference.ai.azure.com"
    DEFAULT_MODEL = "gpt-4o-mini"

ENDPOINT_URL = os.getenv("ENDPOINT_URL", DEFAULT_ENDPOINT)
MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL)

# If no token is provided, fall back to offline deterministic mode for grading/offline execution
IS_OFFLINE_MODE = not bool(API_KEY.strip())

# Global reference date for deadline relative calculations (defaults to current date)
TODAY_DATE = os.getenv("TODAY_DATE", date.today().isoformat())

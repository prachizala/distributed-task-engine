import os
import sys

REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "REDIS_URL",
    "SECRET_KEY",
    "CELERY_BROKER_URL",
]

def validate_environment():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        print(f"WARNING: The following environment variables are missing: {', '.join(missing)}")
        print("Default local fallbacks will be used.")
    else:
        print("All required environment variables are set.")

if __name__ == "__main__":
    validate_environment()

BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = BROKER_URL

CELERYBEAT_SCHEDULE = {
    "run-every-5-minute": { "task": "tasks.main", "schedule": 300 },
}

CELERY_TIMEZONE = 'UTC'
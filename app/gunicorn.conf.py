import os

# REF: https://docs.gunicorn.org/en/stable/settings.html
bind = os.getenv("BIND", "0.0.0.0:8080")
timeout = int(os.getenv("TIMEOUT", "30"))
workers = int(os.getenv("WORKERS", "1"))
worker_class = os.getenv("WORKER_CLASS", "gevent")
worker_connections = int(os.getenv("WORKER_CONNECTIONS", "1000"))
max_requests = int(os.getenv("MAX_REQUESTS", "0"))
threads = int(os.getenv("THREADS", "1"))

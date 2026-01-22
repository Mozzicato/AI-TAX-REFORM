"""
Gunicorn Configuration for AI Tax Reform API
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '7860')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', min(multiprocessing.cpu_count() * 2 + 1, 4)))
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Request handling
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "ai-tax-reform-api"

# Server mechanics
preload_app = True
daemon = False

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

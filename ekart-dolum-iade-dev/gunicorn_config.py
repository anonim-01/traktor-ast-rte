"""
Gunicorn Configuration File
Production-ready settings for Flask application
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# Logging
accesslog = "/app/logs/gunicorn-access.log"
errorlog = "/app/logs/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "traktor-ast-rte"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (eğer kullanıyorsanız)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Development ayarları (production'da False olmalı)
reload = False
reload_engine = "auto"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# For development (local testing)
if os.getenv("FLASK_ENV") == "development":
    bind = "127.0.0.1:8000"
    reload = True
    loglevel = "debug"
    accesslog = "-"
    errorlog = "-"

"""
Gunicorn configuration file for AI Football Platform.

This file contains production-ready Gunicorn settings optimized for:
- Performance and scalability
- Security
- Monitoring and logging
- Process management
"""

import multiprocessing
import os

# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "football-platform"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment for HTTPS)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
worker_tmp_dir = "/dev/shm"
forwarded_allow_ips = "*"

# Monitoring
statsd_host = None
statsd_prefix = "football-platform"

# Development
reload = False
reload_engine = "auto"


# Custom settings
def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker):
    """Called just after a worker has been initialized."""
    worker.log.info("Worker received INT or QUIT signal")


def pre_fork(server, worker):
    """Called just before a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)


def worker_abort(worker):
    """Called when a worker has received a SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")


def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")


def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting football platform server")


def on_reload(server):
    """Called to reload the server."""
    server.log.info("Reloading football platform server")


def child_exit(server, worker):
    """Called when a worker has been exited."""
    server.log.info("Worker exited (pid: %s)", worker.pid)


def worker_exit(server, worker):
    """Called when a worker has been exited, in callable worker."""
    server.log.info("Worker exited (pid: %s)", worker.pid)


def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    server.log.info("Number of workers changed from %s to %s", old_value, new_value)


def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Shutting down football platform server")

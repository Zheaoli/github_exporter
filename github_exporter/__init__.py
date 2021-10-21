from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from github_exporter.config import METRIC_REGISTRY
from github_exporter.cronjobs.github_metrics import start_github_job

scheduler = BackgroundScheduler()

start_github_job()

scheduler.add_job(
    func=start_github_job, trigger="interval", seconds=600, id="github_job"
)

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app(registry=METRIC_REGISTRY)})

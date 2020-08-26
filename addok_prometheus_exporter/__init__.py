import falcon
import time
from falcon_multipart.middleware import MultipartMiddleware
from prometheus_client import core, exposition, Counter, Histogram

from addok.config import config
from addok.http import View, log_notfound, log_query
from addok.ds import DS
from addok.db import DB

def register_http_middleware(middlewares):
    middlewares.append(MultipartMiddleware())
    middlewares.append(MetricsMiddleware())

def register_http_endpoint(api):
    api.add_route('/metrics', MetricsHandler())

class MetricsMiddleware():
    def __init__(self):
        self.requests = Counter(
            'http_total_request',
            'Counter of total HTTP requests',
            ['method', 'path', 'status'])

        self.request_historygram = Histogram(
            'request_latency_seconds',
            'Histogram of request latency',
            ['method', 'path', 'status'])

    def process_request(self, req, resp):
        req.start_time = time.time()

    def process_response(self, req, resp, resource, req_succeeded):
        resp_time = time.time() - req.start_time

        self.requests.labels(method=req.method, path=req.path, status=resp.status).inc()
        self.request_historygram.labels(method=req.method, path=req.path, status=resp.status).observe(resp_time)

class MetricsHandler():
    def __init__(self):
        pass

    def on_get(self, req, resp):
        resp.set_header('Content-Type', exposition.CONTENT_TYPE_LATEST)
        self._gather_metrics()
        collected_metrics = exposition.generate_latest(core.REGISTRY)
        resp.body = collected_metrics

    def _gather_metrics(self):
        try:
            DS.metrics()
            DB.metrics()
        except AttributeError:
            pass

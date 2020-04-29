import falcon
from falcon_multipart.middleware import MultipartMiddleware
from prometheus_client import core, exposition

from addok.config import config
from addok.http import View, log_notfound, log_query
from addok.ds import DS

def register_http_middleware(middlewares):
    middlewares.append(MultipartMiddleware())

def register_http_endpoint(api):
    api.add_route('/metrics', MetricsHandler())

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
        except AttributeError:
            pass

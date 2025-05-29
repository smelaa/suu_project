from fastapi import FastAPI, Request
import socket
import time

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

resource = Resource(attributes={
    SERVICE_NAME: "echo-app",
})

otlp_exporter = OTLPMetricExporter(
    endpoint="http://default-otel-collector.observability.svc.cluster.local:4318/v1/metrics",
)

reader = PeriodicExportingMetricReader(otlp_exporter)
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter("echo-app-metrics")

request_counter = meter.create_counter(
    name="request_count",
    description="Total number of requests",
    unit="1"
)

request_duration_histogram = meter.create_histogram(
    name="request_duration_ms",
    description="Duration of requests in milliseconds",
    unit="ms"
)

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    request_counter.add(1, {"path": request.url.path, "method": request.method})
    request_duration_histogram.record(duration_ms, {"path": request.url.path, "method": request.method})

    return response

@app.get("/ip")
async def get_ip(request: Request):
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    return {"ip": ip_address}
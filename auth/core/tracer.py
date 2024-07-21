from functools import wraps

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from auth.core.config import settings


def traced(name: str):
    """
    Декоратор для подключения трейсера к запросу
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = name + "." + func.__name__
            with tracer.start_as_current_span(span_name) as span:
                request = kwargs.get("request")
                if request:
                    request_id = request.headers.get("X-Request-Id")
                    span.set_attribute("http.request_id", request_id)
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def configure_tracer():
    # Установка имени сервиса
    resource = Resource(
        attributes={
            SERVICE_NAME: "auth-api",
        },
    )
    # Создаем провайдера трейсера
    trace.set_tracer_provider(TracerProvider(resource=resource))

    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.jaeger_host,
        agent_port=settings.jaeger_port,
    )

    # Добавляем SpanProcessor для отправки данных в Jaeger
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Возвращаем трейсера для использования в приложении
    return trace.get_tracer(__name__)


def init_tracer(app):
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)

import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger(__name__)

def instrument_app(app: FastAPI) -> None:
    """
    Sets up Prometheus monitoring for the FastAPI application.
    Adds a /metrics endpoint that Prometheus can scrape.
    
       Automatically instruments all routes with:
    - Request count by endpoint, method, and status code
    - Request latency histograms (enables p50, p95, p99 calculations)
    - Requests currently in progress
    """
    logger.info("Setting up Prometheus monitoring for the application.")
    Instrumentator().instrument(app).expose(app)
    logger.info("Prometheus monitoring setup complete. /metrics endpoint is ready.")
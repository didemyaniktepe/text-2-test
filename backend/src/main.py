import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .infrastructure.config.settings import get_settings
from .api.router import api_router
from .core.container import Container

logger = logging.getLogger(__name__)

settings = get_settings()
container = Container()
container.wire(modules=["src.api.v1.endpoints.tests"])


def get_container() -> Container:
    return container


app = FastAPI(
    title="Text to Test API",
    description="API for generating and running Playwright tests",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Text to Test API is running",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "api_endpoints": {
            "tests": "/api/tests",
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


logger.info("Application startup complete")

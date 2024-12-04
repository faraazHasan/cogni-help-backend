from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .features.root_router import router as root_router


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "https://localhost", "https://localhost/", "capacitor://localhost",
                       "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:4173", "http://127.0.0.1:4173", "http://cogni-help-admin.s3-website-us-east-1.amazonaws.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _app.include_router(router=root_router, prefix=settings.API_V1_STR)

    return _app


app = get_application()

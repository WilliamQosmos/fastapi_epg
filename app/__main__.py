from contextlib import asynccontextmanager
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.core.ioc import AdaptersProvider
from app.core.config import settings
from app.routers import api_router
from app import __version__


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.state.dishka_container.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=None,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.BASE_PATH_PREFIX)

container = make_async_container(AdaptersProvider())
setup_dishka(container, app)


@app.get("/specs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/specs/openapi.json",
        title=settings.PROJECT_NAME,
    )


@app.get("/specs/openapi.json", include_in_schema=False)
async def openapi(req: Request) -> JSONResponse:
    openapi = get_openapi(
        title=settings.PROJECT_NAME,
        version=__version__,
        routes=app.routes,
    )
    return JSONResponse(openapi)

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session

from src.api.router import api_router
from src.config import settings
from src.db.session import engine
from src.handlers.refresh_handler import refresh_all_stats
from src.logger import logger


def cstm_generate_unique_id(route: APIRoute) -> str:
    return f'{route.tags[0]}-{route.name}'


async def _refresh_loop() -> None:
    """Periodically recomputes and persists all analytics stats in the background."""
    while True:
        try:
            with Session(engine) as session:
                refresh_all_stats(session)
        except Exception as e:
            logger.exception(f'Unexpected error during scheduled stats refresh: {e}')
        await asyncio.sleep(settings.refresh_interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_refresh_loop())
    yield
    task.cancel()


app = FastAPI(
    title='Analytics-Service',
    openapi_url='/api/openapi.json',
    generate_unique_id_function=cstm_generate_unique_id,
    lifespan=lifespan,
)

app.include_router(api_router, prefix='/api')


@app.get('/health', tags=['health'])
async def health_check():
    return {'status': 'ok'}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler to log all HTTPExceptions before returning the response"""
    logger.error(f'HTTP Exception: {exc.status_code} - {exc.detail} for url: {request.url}')

    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.detail},
    )

from fastapi import APIRouter

from .clients import router as clients_router

api_router = APIRouter()

api_router.include_router(clients_router)

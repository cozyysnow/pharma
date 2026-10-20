from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.users import router as users_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.categories import router as categories_router
from backend.app.api.v1.suppliers import router as suppliers_router
from backend.app.api.v1.medicines import router as medicines_router
from backend.app.api.v1.inventory import router as inventory_router
from backend.app.api.v1.transactions import router as transactions_router
from backend.app.api.v1.settings import router as settings_router
from backend.app.api.v1.datasets import router as datasets_router
from backend.app.api.v1.ml import router as ml_router
from backend.app.api.v1.forecasts import router as forecasts_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(health_router)
api_v1_router.include_router(categories_router)
api_v1_router.include_router(suppliers_router)
api_v1_router.include_router(medicines_router)
api_v1_router.include_router(inventory_router)
api_v1_router.include_router(transactions_router)
api_v1_router.include_router(settings_router)
api_v1_router.include_router(datasets_router)
api_v1_router.include_router(ml_router)
api_v1_router.include_router(forecasts_router)

__all__ = ["api_v1_router"]

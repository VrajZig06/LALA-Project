from fastapi import APIRouter

from app.api.user_routes import router as user_router
from app.api.video_routes import router as video_router
from app.api.order_routes import router as order_router
from app.api.subscription_routes import router as subscription_router
app_router = APIRouter()

# Add Routes with Module Wise
app_router.include_router(user_router)
app_router.include_router(video_router)
app_router.include_router(order_router)
app_router.include_router(subscription_router)

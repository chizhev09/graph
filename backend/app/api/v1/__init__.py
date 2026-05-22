from fastapi import APIRouter

from app.api.v1 import auth, categories, listings, notifications, profile, searches, subscriptions

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(searches.router, prefix="/searches", tags=["searches"])
api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])

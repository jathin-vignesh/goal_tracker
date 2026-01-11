from fastapi import APIRouter
from app.routers import auth_routes,sso,goals,completions

router = APIRouter()

router.include_router(auth_routes.router,tags=["Authentication"])
router.include_router(sso.router,tags=["SSO"])
router.include_router(goals.router,tags=["Goals"])
router.include_router(completions.router, tags=["Sub-Goal Completion"])
from fastapi import APIRouter

from app.features.bot.router import router as chat_router
from app.features.questions.router import questions_router
from app.features.form_builder.router import router as form_builder_router

from .auth.router import router as auth_router
from .user.router import userRouter as user_router

router = APIRouter()

# Include all routers here
router.include_router(router=auth_router)
router.include_router(router=user_router)
router.include_router(router=chat_router)
router.include_router(router=questions_router)
router.include_router(router=form_builder_router)

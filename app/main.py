from fastapi import FastAPI
from app.config.database import Base, engine
from app.model.user import User
from app.model.spo2_session import Spo2Session

from app.api.routes.auth_routes import router as auth_router
from app.api.routes.user_routes import router as user_router
from app.api.routes.spo2_session_routes import router as spo2_session_router
from app.api.routes.insights_routes import router as insights_router
from app.api.routes.report_routes import router as report_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Apnea Detector API")

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(spo2_session_router)
app.include_router(insights_router)
app.include_router(report_router)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.trends import router as trends_router

app = FastAPI(title="traffic-signal-optimizer")

app.add_middleware(
    CORSMiddleware,
    allow_origin="http://localhost:5173",
    allow_methods="*",
    allow_headers="*",

)

app.include_router(trends_router, prefix="/api", tags=["trends"])
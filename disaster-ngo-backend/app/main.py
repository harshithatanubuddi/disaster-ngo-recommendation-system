from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.recommendations import router as recommend_router
from app.routers.disasters import router as disaster_router
from app.api.alerts import router as alerts_router

app = FastAPI(title="Disaster–NGO Decision Support System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://animated-palmier-dfd2ce.netlify.app",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ONLY THESE ROUTERS
app.include_router(alerts_router)
app.include_router(recommend_router)
app.include_router(disaster_router)

@app.get("/")
def root():
    return {"status": "Backend running"}

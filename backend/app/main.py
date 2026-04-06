from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, care, dashboard, metrics, patients, reports
from app.db.session import create_all_tables


app = FastAPI(title="RetinalAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_all_tables()


app.include_router(analysis.router, prefix="/api")
app.include_router(care.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

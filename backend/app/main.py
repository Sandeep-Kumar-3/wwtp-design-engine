from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.project import ProjectInput
from app.services.design_service import generate_design


app = FastAPI(
    title="WWTP Design Engine",
    description=(
        "Preliminary municipal and industrial "
        "wastewater treatment plant design engine."
    ),
    version="1.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():

    return {
        "application": "WWTP Design Engine",
        "version": "1.2.0",
        "status": "running",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/api/design")
def create_design(
    project: ProjectInput,
):

    return generate_design(project)
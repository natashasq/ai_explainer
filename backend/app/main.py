from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes.explain import router as explain_router
from app.routes.upload import router as upload_router

app = FastAPI(title=settings.app_name, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(explain_router)
app.include_router(upload_router)


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}


@app.get("/health")
async def health():
    return {"status": "ok"}

# @app.get("/api/explain")

from fastapi import FastAPI
from app.api.routes import router
from app.database.connection import create_tables

app = FastAPI(
    title="Supply Chain Risk Intelligence API",
    description="AI-powered supply chain risk monitoring",
    version="1.0.0"
)

# Create tables on startup
create_tables()

# Include routes
app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "Supply Chain Risk Intelligence API",
        "status": "running"
    }
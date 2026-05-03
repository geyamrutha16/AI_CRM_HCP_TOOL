"""
Main FastAPI application.
Starts the server and configures all routes, middleware, and initialization.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import config
from models.database import init_db
from routes import interactions, agent

# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print("⚡ Initializing database...")
    init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="AI-CRM HCP Module",
    description="Healthcare CRM for logging HCP interactions with AI orchestration",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware BEFORE including routes (order matters!)
# Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# CORS middleware (should be added last so it's processed first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

# Include routes
app.include_router(interactions.router)
app.include_router(agent.router)


# Root endpoint
@app.get("/")
async def root():
    """Welcome endpoint."""
    return {
        "message": "AI-CRM HCP Module API",
        "docs": "/docs",
        "health": "/agent/health"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": "production" if not config.DEBUG else "development"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG
    )

"""
Simple Posts CRUD API using FastAPI and SQLAlchemy.
PostgreSQL is the backend used for this example. Make sure to have a PostgreSQL server running and update the connection string in the code accordingly.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import auth
from .database import create_tables
from .routers import memories, users


def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    Runs once when the app starts, before it begins accepting requests.
    """
    create_tables()  # ensures tables exist before the API starts serving requests
    yield
    # shutdown cleanup would go here, e.g. engine.dispose()


app = FastAPI(lifespan=lifespan)
origins = ["https://www.google.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(memories.router)
app.include_router(users.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"name": "memories API", "version": "1.0.0"}


import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


from app.database import get_db_connection
from app.routes import (
    availability,
    appointments,
    callbacks,
    clinic_info,
    chats,
    vapi_tools,
    current_datetime,
    dashboard,
)

# Basic application logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Register existing routers
app.include_router(availability.router)
app.include_router(appointments.router)
app.include_router(callbacks.router)
app.include_router(clinic_info.router)
app.include_router(chats.router)
app.include_router(vapi_tools.router)
app.include_router(current_datetime.router)
app.include_router(dashboard.router)

# CORS configuration 

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://clinico-call.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["GET", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type"],
)



@app.get("/")
def root():
    return {"message": "ClinicoCall API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/db-test")
def test_database():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT current_database()")
        database_name = cursor.fetchone()[0]

        return {
            "database": database_name,
            "status": "connected",
        }

    except Exception:
        logger.exception("Database connectivity check failed")
        raise HTTPException(
            status_code=503,
            detail="Database connection check failed",
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
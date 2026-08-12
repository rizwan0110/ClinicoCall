from fastapi import FastAPI
from app.database import get_db_connection
from app.routes import availability
from app.routes import appointments
from app.routes import callbacks
from app.routes import clinic_info

app = FastAPI()
app.include_router(availability.router)
app.include_router(appointments.router)
app.include_router(callbacks.router)
app.include_router(clinic_info.router)

@app.get("/")
async def root():
    return {"Hello"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/db-test")
def test_database():
    connection = get_db_connection()

    cursor = connection.cursor()
    cursor.execute("SELECT current_database();")

    database_name = cursor.fetchone()

    cursor.close()
    connection.close()

    return {
        "database": database_name[0],
        "status": "connected"
    }


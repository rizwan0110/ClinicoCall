
from fastapi import APIRouter
from pydantic import BaseModel

from app.database import get_db_connection

router = APIRouter()


class CallbackCreate(BaseModel):
    patient_id: int
    reason: str


@router.post("/callbacks")
def create_callback(callback: CallbackCreate):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO callback_request (
                patient_id,
                reason,
                status
            )
            VALUES (%s, %s, %s)
            RETURNING callback_id
            """,
            (
                callback.patient_id,
                callback.reason,
                "pending",
            ),
        )

        callback_id = cursor.fetchone()[0]
        connection.commit()

        return {
            "message": "Callback request created successfully",
            "callback_id": callback_id,
        }

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

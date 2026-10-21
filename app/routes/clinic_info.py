from fastapi import APIRouter
from app.database import get_db_connection

router = APIRouter()


@router.get("/clinic-info")
def get_clinic_info():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                SELECT
                    clinic_name,
                    phone_number,
                    address,
                    working_hours,
                    additional_information
                FROM clinic_info
                LIMIT 1;
                """
            )
            clinic = cursor.fetchone()
        finally:
            cursor.close()
    finally:
        connection.close()

    if clinic is None:
        return {"message": "Clinic information not available"}

    return {
        "clinic_name": clinic[0],
        "phone_number": clinic[1],
        "address": clinic[2],
        "working_hours": clinic[3],
        "additional_information": clinic[4]
    }
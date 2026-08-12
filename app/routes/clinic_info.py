from fastapi import APIRouter

from app.database import get_db_connection

router = APIRouter()


@router.get("/clinic-info")
def get_clinic_info():

    connection = get_db_connection()
    cursor = connection.cursor()

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

    cursor.close()
    connection.close()

    return {
        "clinic_name": clinic[0],
        "phone_number": clinic[1],
        "address": clinic[2],
        "working_hours": clinic[3],
        "additional_information": clinic[4]
    }
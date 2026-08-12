from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date, time

from app.database import get_db_connection
from app.routes.availability import generate_slots

router = APIRouter()


class AppointmentCreate(BaseModel):
    patient_id: int
    appointment_date: date
    appointment_time: time
    reason_for_visit: str
    affected_area: str
    issue_duration: str


@router.post("/appointments")
def create_appointment(appointment: AppointmentCreate):

    connection = get_db_connection()
    cursor = connection.cursor()

    # 1. Check past date
    if appointment.appointment_date < date.today():
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Appointment date cannot be in the past"
        )

    # 2. Check patient exists
    cursor.execute(
        """
        SELECT patient_id
        FROM patient
        WHERE patient_id = %s
        """,
        (appointment.patient_id,)
    )

    patient = cursor.fetchone()

    if patient is None:
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # 3. Check appointment time is a valid clinic slot
    valid_slots = generate_slots()

    requested_time = appointment.appointment_time.strftime("%H:%M")

    if requested_time not in valid_slots:
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Invalid appointment time"
        )

    # 4. Check slot is not already booked
    cursor.execute(
        """
        SELECT appointment_id
        FROM appointment
        WHERE appointment_date = %s
        AND appointment_time = %s
        AND status = 'booked'
        """,
        (
            appointment.appointment_date,
            appointment.appointment_time
        )
    )

    existing_appointment = cursor.fetchone()

    if existing_appointment is not None:
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=409,
            detail="Appointment slot is already booked"
        )

    # 5. Insert appointment
    cursor.execute(
        """
        INSERT INTO appointment (
            patient_id,
            appointment_date,
            appointment_time,
            reason_for_visit,
            affected_area,
            issue_duration,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING appointment_id;
        """,
        (
            appointment.patient_id,
            appointment.appointment_date,
            appointment.appointment_time,
            appointment.reason_for_visit,
            appointment.affected_area,
            appointment.issue_duration,
            "booked"
        )
    )

    appointment_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Appointment booked successfully",
        "appointment_id": appointment_id
    }
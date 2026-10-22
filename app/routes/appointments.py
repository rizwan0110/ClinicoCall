
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database import get_db_connection
from app.routes.availability import generate_slots

router = APIRouter()

TIMEZONE = ZoneInfo("Asia/Kolkata")


class AppointmentCreate(BaseModel):
    patient_id: int
    appointment_date: date
    appointment_time: time
    reason_for_visit: str
    affected_area: str
    issue_duration: str


@router.post("/appointments")
def create_appointment(appointment: AppointmentCreate):
    connection = None
    cursor = None

    try:
        now = datetime.now(TIMEZONE)
        appointment_date = appointment.appointment_date
        appointment_time = appointment.appointment_time

        # Reject appointments in the past.
        if appointment_date < now.date():
            raise HTTPException(
                status_code=400,
                detail="Appointment date cannot be in the past",
            )

        if appointment_date == now.date() and appointment_time <= now.time():
            raise HTTPException(
                status_code=400,
                detail="Cannot book an appointment for a time that has already passed",
            )

        # Check that the requested time matches the clinic schedule.
        valid_slots = generate_slots()
        requested_time = appointment_time.strftime("%H:%M")

        if requested_time not in valid_slots:
            raise HTTPException(
                status_code=400,
                detail="Invalid appointment time",
            )

        connection = get_db_connection()
        cursor = connection.cursor()

        # Confirm that the patient exists.
        cursor.execute(
            """
            SELECT patient_id
            FROM patient
            WHERE patient_id = %s
            """,
            (appointment.patient_id,),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found",
            )

        # Check whether the requested slot is already booked.
        cursor.execute(
            """
            SELECT appointment_id
            FROM appointment
            WHERE appointment_date = %s
              AND appointment_time = %s
              AND status = 'booked'
            """,
            (appointment_date, appointment_time),
        )

        if cursor.fetchone() is not None:
            raise HTTPException(
                status_code=409,
                detail="Appointment slot is already booked",
            )

        # Create the appointment.
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
            RETURNING appointment_id
            """,
            (
                appointment.patient_id,
                appointment_date,
                appointment_time,
                appointment.reason_for_visit,
                appointment.affected_area,
                appointment.issue_duration,
                "booked",
            ),
        )

        appointment_id = cursor.fetchone()[0]
        connection.commit()

        return {
            "success": True,
            "message": "Appointment booked successfully",
            "appointment_id": appointment_id,
            "patient_id": appointment.patient_id,
            "appointment_date": appointment_date.isoformat(),
            "appointment_time": requested_time,
            "status": "booked",
        }

    except Exception:
        if connection is not None:
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

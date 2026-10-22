
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database import get_db_connection


router = APIRouter()


@router.get("/dashboard/appointments/today")
def get_todays_appointments():
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()

    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                a.appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.reason_for_visit,
                a.affected_area,
                a.issue_duration,
                a.status,
                p.patient_id,
                p.name,
                p.phone_number,
                p.is_returning_patient
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            WHERE a.appointment_date = %s
            ORDER BY a.appointment_time ASC
            """,
            (today,),
        )

        rows = cursor.fetchall()

        appointments = [
            {
                "appointment_id": row[0],
                "appointment_date": row[1].isoformat(),
                "appointment_time": row[2].strftime("%H:%M"),
                "reason_for_visit": row[3],
                "affected_area": row[4],
                "issue_duration": row[5],
                "status": row[6],
                "patient_id": row[7],
                "patient_name": row[8],
                "phone_number": row[9],
                "is_returning_patient": row[10],
            }
            for row in rows
        ]

        return {
            "date": today.isoformat(),
            "total_appointments": len(appointments),
            "appointments": appointments,
        }

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


@router.get("/dashboard/appointments")
def get_all_appointments():
    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                a.appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.reason_for_visit,
                a.affected_area,
                a.issue_duration,
                a.status,
                p.patient_id,
                p.name,
                p.phone_number,
                p.is_returning_patient
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            ORDER BY
                a.appointment_date DESC,
                a.appointment_time ASC
            """
        )

        rows = cursor.fetchall()

        appointments = [
            {
                "appointment_id": row[0],
                "appointment_date": row[1].isoformat(),
                "appointment_time": row[2].strftime("%H:%M"),
                "reason_for_visit": row[3],
                "affected_area": row[4],
                "issue_duration": row[5],
                "status": row[6],
                "patient_id": row[7],
                "patient_name": row[8],
                "phone_number": row[9],
                "is_returning_patient": row[10],
            }
            for row in rows
        ]

        return {
            "total_appointments": len(appointments),
            "appointments": appointments,
        }

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


@router.get("/dashboard/callbacks")
def get_all_callbacks():
    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                c.callback_id,
                c.reason,
                c.status,
                c.created_at,
                p.patient_id,
                p.name,
                p.phone_number
            FROM callback_request c
            JOIN patient p ON c.patient_id = p.patient_id
            ORDER BY c.created_at DESC
            """
        )

        rows = cursor.fetchall()

        callbacks = [
            {
                "callback_id": row[0],
                "reason": row[1],
                "status": row[2],
                "created_at": row[3].isoformat() if row[3] else None,
                "patient_id": row[4],
                "patient_name": row[5],
                "phone_number": row[6],
            }
            for row in rows
        ]

        return {
            "total_callbacks": len(callbacks),
            "callbacks": callbacks,
        }

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


class AppointmentStatusUpdate(BaseModel):
    status: str


@router.patch("/dashboard/appointments/{appointment_id}/status")
def update_appointment_status(
    appointment_id: int,
    update: AppointmentStatusUpdate,
):
    allowed_statuses = {"booked", "completed", "cancelled"}

    if update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Use booked, completed, or cancelled.",
        )

    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE appointment
            SET status = %s
            WHERE appointment_id = %s
            RETURNING appointment_id, status
            """,
            (update.status, appointment_id),
        )

        updated = cursor.fetchone()

        if updated is None:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found",
            )

        connection.commit()

        return {
            "message": "Appointment status updated successfully",
            "appointment_id": updated[0],
            "status": updated[1],
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


class CallbackStatusUpdate(BaseModel):
    status: str


@router.patch("/dashboard/callbacks/{callback_id}/status")
def update_callback_status(
    callback_id: int,
    update: CallbackStatusUpdate,
):
    allowed_statuses = {"pending", "completed"}

    if update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Use pending or completed.",
        )

    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE callback_request
            SET status = %s
            WHERE callback_id = %s
            RETURNING callback_id, status
            """,
            (update.status, callback_id),
        )

        updated = cursor.fetchone()

        if updated is None:
            raise HTTPException(
                status_code=404,
                detail="Callback request not found",
            )

        connection.commit()

        return {
            "message": "Callback status updated successfully",
            "callback_id": updated[0],
            "status": updated[1],
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

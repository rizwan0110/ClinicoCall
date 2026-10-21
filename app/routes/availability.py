from fastapi import APIRouter
from datetime import datetime, timedelta, date
from app.database import get_db_connection
from zoneinfo import ZoneInfo
from fastapi import HTTPException


router = APIRouter()


def generate_slots():

    opening_time = datetime.strptime("08:00", "%H:%M")
    closing_time = datetime.strptime("20:00", "%H:%M")

    breaks = [
        ("09:30", "10:00"),
        ("12:30", "13:30"),
        ("16:30", "17:00")
    ]

    slots = []

    current_time = opening_time

    while current_time < closing_time:

        slot_time = current_time.strftime("%H:%M")

        is_break = False

        for break_start, break_end in breaks:

            if break_start <= slot_time < break_end:
                is_break = True
                break

        if not is_break:
            slots.append(slot_time)

        current_time += timedelta(minutes=30)

    return slots

@router.get("/availability")
def get_availability(date: date):
    
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()

    if date < today:
        raise HTTPException(
            status_code=400,
            detail="Cannot check availability for a past date"
        )

    all_slots = generate_slots()

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT appointment_time
        FROM appointment
        WHERE appointment_date = %s
        AND status = 'booked'
        """,
        (date,)
    )

    booked_appointments = cursor.fetchall()

    cursor.close()
    connection.close()

    booked_slots = [
        appointment[0].strftime("%H:%M")
        for appointment in booked_appointments
    ]
    available_slots = [
    slot
    for slot in all_slots
    if slot not in booked_slots
    ]

    # Exclude elapsed appointment slots when checking today
    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    if date == now.date():
        current_time = now.strftime("%H:%M")

        available_slots = [
            slot
            for slot in available_slots
            if slot > current_time
        ]

    return {
        "date": date,
        "available_slots": available_slots
    }
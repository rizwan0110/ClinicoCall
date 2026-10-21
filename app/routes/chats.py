from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, date

from app.database import get_db_connection

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


# Simple in-memory session storage for MVP
booking_sessions = {}
callback_sessions = {}


# ---------------------------------------------------
# INTENT DETECTION
# ---------------------------------------------------

def detect_intent(message: str):

    message = message.lower()

    if "book" in message or "appointment" in message:
        return "booking"

    if "available" in message or "slot" in message:
        return "availability"

    if (
        "open" in message
        or "working hours" in message
        or "address" in message
        or "phone" in message
        or "contact" in message
    ):
        return "clinic_info"

    if "call back" in message or "callback" in message:
        return "callback"

    return "unknown"


# ---------------------------------------------------
# DATABASE HELPERS
# ---------------------------------------------------

def create_patient(name: str, phone_number: str):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO patient (
            name,
            phone_number,
            is_returning_patient
        )
        VALUES (%s, %s, %s)
        RETURNING patient_id;
        """,
        (
            name,
            phone_number,
            False
        )
    )

    patient_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return patient_id


def find_patient_by_phone(phone_number: str):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT patient_id, name
        FROM patient
        WHERE phone_number = %s
        """,
        (phone_number,)
    )

    patient = cursor.fetchone()

    cursor.close()
    connection.close()

    return patient


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

    return clinic


def create_appointment_from_session(session):

    connection = get_db_connection()
    cursor = connection.cursor()

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
            session["patient_id"],
            session["appointment_date"],
            session["appointment_time"],
            session["reason_for_visit"],
            session["affected_area"],
            session["issue_duration"],
            "booked"
        )
    )

    appointment_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return appointment_id


def create_callback_from_session(session):

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
        RETURNING callback_id;
        """,
        (
            session["patient_id"],
            session["reason"],
            "pending"
        )
    )

    callback_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return callback_id


# ---------------------------------------------------
# CHAT ENDPOINT
# ---------------------------------------------------

@router.post("/chat")
def chat(request: ChatRequest):

    session_id = "demo_user"

    # Detect whether the user is explicitly starting a new flow
    new_intent = detect_intent(request.message)


    # =================================================
    # SWITCH / START CALLBACK
    # =================================================

    if new_intent == "callback":

        # Cancel unfinished booking if one exists
        if session_id in booking_sessions:
            del booking_sessions[session_id]

        callback_sessions[session_id] = {
            "step": "phone_number"
        }

        return {
            "response": "Sure. What is your phone number?"
        }


    # =================================================
    # SWITCH / START BOOKING
    # =================================================

    if new_intent == "booking":

        # Cancel unfinished callback if one exists
        if session_id in callback_sessions:
            del callback_sessions[session_id]

        # Start booking only if one is not already active
        if session_id not in booking_sessions:

            booking_sessions[session_id] = {
                "step": "phone_number"
            }

            return {
                "response": "Sure. What is your phone number?"
            }


    # =================================================
    # ACTIVE BOOKING CONVERSATION
    # =================================================

    if session_id in booking_sessions:

        session = booking_sessions[session_id]

        # Step 1: Phone number
        if session["step"] == "phone_number":

            phone_number = request.message
            patient = find_patient_by_phone(phone_number)

            session["phone_number"] = phone_number

            if patient:

                session["patient_id"] = patient[0]
                session["name"] = patient[1]
                session["step"] = "appointment_date"

                return {
                    "response": (
                        f"Welcome back, {patient[1]}. "
                        "What date would you like your appointment?"
                    )
                }

            else:

                session["step"] = "name"

                return {
                    "response": (
                        "I couldn't find an existing patient with that "
                        "phone number. What is your name?"
                    )
                }


        # Step 2: New patient name
        if session["step"] == "name":

            name = request.message

            patient_id = create_patient(
                name=name,
                phone_number=session["phone_number"]
            )

            session["name"] = name
            session["patient_id"] = patient_id
            session["step"] = "appointment_date"

            return {
                "response": (
                    f"Thanks, {name}. Your patient profile has been created. "
                    "What date would you like your appointment?"
                )
            }


        # Step 3: Appointment date
        if session["step"] == "appointment_date":

            try:
                appointment_date = datetime.strptime(
                    request.message,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                return {
                    "response": "Please enter the date in YYYY-MM-DD format."
                }

            if appointment_date < date.today():

                return {
                    "response": (
                        "The appointment date cannot be in the past. "
                        "Please choose another date."
                    )
                }

            session["appointment_date"] = appointment_date
            session["step"] = "appointment_time"

            return {
                "response": (
                    f"Great. You selected {appointment_date}. "
                    "What time would you prefer?"
                )
            }


        # Step 4: Appointment time
        if session["step"] == "appointment_time":

            session["appointment_time"] = request.message
            session["step"] = "reason_for_visit"

            return {
                "response": "What is the reason for your visit?"
            }


        # Step 5: Reason for visit
        if session["step"] == "reason_for_visit":

            session["reason_for_visit"] = request.message
            session["step"] = "affected_area"

            return {
                "response": "Which area is affected?"
            }


        # Step 6: Affected area
        if session["step"] == "affected_area":

            session["affected_area"] = request.message
            session["step"] = "issue_duration"

            return {
                "response": "How long have you had this issue?"
            }


        # Step 7: Issue duration + create appointment
        if session["step"] == "issue_duration":

            session["issue_duration"] = request.message

            appointment_id = create_appointment_from_session(
                session
            )

            name = session["name"]
            appointment_date = session["appointment_date"]
            appointment_time = session["appointment_time"]

            del booking_sessions[session_id]

            return {
                "response": (
                    f"Thanks, {name}. Your appointment has been booked "
                    f"for {appointment_date} at {appointment_time}. "
                    f"Your appointment ID is {appointment_id}."
                )
            }


    # =================================================
    # ACTIVE CALLBACK CONVERSATION
    # =================================================

    if session_id in callback_sessions:

        session = callback_sessions[session_id]


        # Step 1: Phone number
        if session["step"] == "phone_number":

            phone_number = request.message
            patient = find_patient_by_phone(phone_number)

            session["phone_number"] = phone_number

            if patient:

                session["patient_id"] = patient[0]
                session["name"] = patient[1]
                session["step"] = "reason"

                return {
                    "response": (
                        f"Thanks, {patient[1]}. "
                        "What would you like us to call you about?"
                    )
                }

            else:

                session["step"] = "name"

                return {
                    "response": (
                        "I couldn't find an existing patient with that "
                        "phone number. What is your name?"
                    )
                }


        # Step 2: New patient name
        if session["step"] == "name":

            name = request.message

            patient_id = create_patient(
                name=name,
                phone_number=session["phone_number"]
            )

            session["name"] = name
            session["patient_id"] = patient_id
            session["step"] = "reason"

            return {
                "response": (
                    f"Thanks, {name}. "
                    "What would you like us to call you about?"
                )
            }


        # Step 3: Callback reason
        if session["step"] == "reason":

            session["reason"] = request.message

            callback_id = create_callback_from_session(
                session
            )

            name = session["name"]

            del callback_sessions[session_id]

            return {
                "response": (
                    f"Thanks, {name}. Your callback request has been "
                    f"created successfully. "
                    f"Your callback request ID is {callback_id}."
                )
            }


    # =================================================
    # FAQ / CLINIC INFORMATION
    # =================================================

    if new_intent == "clinic_info":

        clinic = get_clinic_info()
        message = request.message.lower()

        if "open" in message or "working hours" in message:

            return {
                "response": f"Our working hours are {clinic[3]}."
            }

        if "address" in message:

            return {
                "response": f"Our clinic address is {clinic[2]}."
            }

        if "phone" in message or "contact" in message:

            return {
                "response": f"You can contact the clinic at {clinic[1]}."
            }


    # =================================================
    # OTHER / UNKNOWN INTENTS
    # =================================================


    return {
    "response": (
        "I'm sorry, I didn't understand that. "
        "I can help you book an appointment, check clinic information, "
        "or request a callback."
    )
}

import logging
from datetime import date, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError
from psycopg2 import Error as DatabaseError

from app.routes.clinic_info import get_clinic_info
from app.routes.availability import get_availability
from app.routes.chats import find_patient_by_phone, create_patient
from app.routes.appointments import AppointmentCreate, create_appointment
from app.routes.callbacks import CallbackCreate, create_callback
from app.routes.current_datetime import get_current_datetime


router = APIRouter()
logger = logging.getLogger(__name__)


class VapiRequest(BaseModel):
    message: dict


@router.post("/vapi/tools")
async def vapi_tools(request: VapiRequest):

    payload = request.model_dump()
    tool_calls = payload.get("message", {}).get("toolCallList", [])
    results = []

    for tool_call in tool_calls:

        tool_id = tool_call.get("id")

        try:
            tool_name = tool_call.get("function", {}).get("name")
            arguments = tool_call.get("function", {}).get("arguments", {})

            # ----------------------------------
            # 1. GET CLINIC INFORMATION
            # ----------------------------------
            if tool_name == "get_clinic_info":
                result = get_clinic_info()

            # ----------------------------------
            # 2. CHECK APPOINTMENT AVAILABILITY
            # ----------------------------------
            elif tool_name == "check_availability":
                try:
                    appointment_date = date.fromisoformat(
                        arguments["date"]
                    )

                    result = get_availability(
                        date=appointment_date
                    )

                except (KeyError, TypeError, ValueError):
                    result = {
                        "success": False,
                        "error": "Invalid or missing date. Use YYYY-MM-DD format."
                    }

                except HTTPException as error:
                    result = {
                        "success": False,
                        "error": error.detail
                    }

            # ----------------------------------
            # 3. BOOK APPOINTMENT
            # ----------------------------------
            elif tool_name == "book_appointment":
                try:
                    name = arguments["name"].strip()
                    phone_number = arguments["phone_number"].strip()

                    if not name or not phone_number:
                        raise ValueError(
                            "Name and phone number are required"
                        )

                    appointment_date = date.fromisoformat(
                        arguments["appointment_date"]
                    )

                    appointment_time = datetime.strptime(
                        arguments["appointment_time"],
                        "%H:%M"
                    ).time()

                    reason_for_visit = arguments["reason_for_visit"]
                    affected_area = arguments["affected_area"]
                    issue_duration = arguments["issue_duration"]

                    # Find existing patient
                    patient = find_patient_by_phone(phone_number)

                    if patient:
                        patient_id = patient[0]
                    else:
                        patient_id = create_patient(
                            name=name,
                            phone_number=phone_number
                        )

                    # Create appointment using existing logic
                    appointment = AppointmentCreate(
                        patient_id=patient_id,
                        appointment_date=appointment_date,
                        appointment_time=appointment_time,
                        reason_for_visit=reason_for_visit,
                        affected_area=affected_area,
                        issue_duration=issue_duration
                    )

                    result = create_appointment(appointment)

                except (KeyError, TypeError, ValueError, ValidationError) as error:
                    result = {
                        "success": False,
                        "error": f"Invalid booking details: {error}"
                    }

                except HTTPException as error:
                    result = {
                        "success": False,
                        "error": error.detail
                    }

            # ----------------------------------
            # 4. REQUEST CALLBACK
            # ----------------------------------
            elif tool_name == "request_callback":
                try:
                    name = arguments["name"].strip()
                    phone_number = arguments["phone_number"].strip()
                    reason = arguments["reason"].strip()

                    if not name or not phone_number or not reason:
                        raise ValueError(
                            "Name, phone number, and reason are required"
                        )

                    # Find existing patient
                    patient = find_patient_by_phone(phone_number)

                    if patient:
                        patient_id = patient[0]
                    else:
                        patient_id = create_patient(
                            name=name,
                            phone_number=phone_number
                        )

                    callback = CallbackCreate(
                        patient_id=patient_id,
                        reason=reason
                    )

                    result = create_callback(callback)

                except (KeyError, TypeError, ValueError, ValidationError) as error:
                    result = {
                        "success": False,
                        "error": f"Invalid callback details: {error}"
                    }

                except HTTPException as error:
                    result = {
                        "success": False,
                        "error": error.detail
                    }

            # ----------------------------------
            # 5. GET CURRENT DATE AND TIME
            # ----------------------------------
            elif tool_name == "get_current_datetime":
                result = get_current_datetime()

            # ----------------------------------
            # UNKNOWN TOOL
            # ----------------------------------
            else:
                result = {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }

        # ----------------------------------
        # DATABASE ERROR HANDLING
        # ----------------------------------
        except DatabaseError:
            logger.exception(
                "Database error while processing Vapi tool"
            )

            result = {
                "success": False,
                "error": (
                    "The clinic system is temporarily unavailable. "
                    "Please try again later."
                )
            }

        # ----------------------------------
        # UNEXPECTED ERROR HANDLING
        # ----------------------------------
        except Exception:
            logger.exception(
                "Unexpected error while processing Vapi tool"
            )

            result = {
                "success": False,
                "error": (
                    "Unable to complete the request right now. "
                    "Please try again later."
                )
            }

        results.append({
            "toolCallId": tool_id,
            "result": result
        })

    return {"results": results}

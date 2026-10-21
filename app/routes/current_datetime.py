from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter

router = APIRouter()


@router.get("/current-datetime")
def get_current_datetime():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    return {
        "current_date": now.strftime("%Y-%m-%d"),
        "current_time": now.strftime("%H:%M"),
        "current_day": now.strftime("%A"),
        "timezone": "Asia/Kolkata"
    }
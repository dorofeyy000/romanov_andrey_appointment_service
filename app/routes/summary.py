from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.database import get_db
from app.models import Appointment, Specialist, Slot
from app.schemas import SummaryOut

router=APIRouter()

@router.get("/summary",response_model=SummaryOut)
def summary(db: Session=Depends(get_db),user=Depends(get_current_user)):
    total=db.query(Appointment).count()
    booked=db.query(Appointment).filter(Appointment.status=="booked").count()
    cancelled=db.query(Appointment).filter(Appointment.status=="cancelled").count()
    share=round((cancelled/total*100) if total else 0,2)

    rows=(
        db.query(
            Specialist.id,
            Specialist.full_name,
            func.count(Appointment.id).label("appointments")
        )
        .outerjoin(Appointment,Appointment.specialist_id==Specialist.id)
        .group_by(Specialist.id,Specialist.full_name)
        .order_by(Specialist.id)
        .all()
    )

    specialist_load=[
        {"specialist_id":row.id,"full_name":row.full_name,"appointments":row.appointments}
        for row in rows
    ]

    return {
        "total_appointments":total,
        "booked_appointments":booked,
        "cancelled_appointments":cancelled,
        "cancellation_share":share,
        "specialist_load":specialist_load
    }

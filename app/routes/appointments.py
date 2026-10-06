from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.database import get_db
from app.models import Appointment,Specialist,Service,Slot
from app.schemas import AppointmentCreate,AppointmentOut,AppointmentPage
from app.services import book_slot,cancel_appointment

router=APIRouter()

def appointment_dict(item):
    return {
        "id":item.id,
        "user_id":item.user_id,
        "specialist_id":item.specialist_id,
        "specialist_name":item.specialist.full_name,
        "service_id":item.service_id,
        "service_name":item.service.name,
        "slot_id":item.slot_id,
        "slot_start":item.slot.start_at,
        "slot_end":item.slot.end_at,
        "status":item.status,
        "created_at":item.created_at,
        "cancelled_at":item.cancelled_at
    }

@router.get("/appointments",response_model=AppointmentPage)
def list_appointments(
    page:int=Query(1,ge=1),
    size:int=Query(20,ge=1,le=100),
    status:str|None=None,
    db:Session=Depends(get_db),
    user=Depends(get_current_user)
):
    query=db.query(Appointment).filter(Appointment.user_id==user.id)

    if status:
        query=query.filter(Appointment.status==status)

    total=query.count()

    items=(
        query
        .order_by(Appointment.id)
        .offset((page-1)*size)
        .limit(size)
        .all()
    )

    return {
        "items":[appointment_dict(item) for item in items],
        "total":total
    }

@router.get("/appointments/{appointment_id}",response_model=AppointmentOut)
def get_appointment(
    appointment_id:int,
    db:Session=Depends(get_db),
    user=Depends(get_current_user)
):
    item=db.get(Appointment,appointment_id)

    if not item or item.user_id!=user.id:
        raise HTTPException(status_code=404,detail="Запись не найдена")

    return appointment_dict(item)

@router.post("/appointments",response_model=AppointmentOut,status_code=201)
def create_appointment(
    data:AppointmentCreate,
    db:Session=Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        item=book_slot(
            db,
            user.id,
            data.specialist_id,
            data.service_id,
            data.slot_id
        )
        return appointment_dict(item)
    except ValueError as exc:
        raise HTTPException(status_code=409,detail=str(exc))

@router.post("/appointments/{appointment_id}/cancel",response_model=AppointmentOut)
def cancel(
    appointment_id:int,
    db:Session=Depends(get_db),
    user=Depends(get_current_user)
):
    item=db.get(Appointment,appointment_id)

    if not item or item.user_id!=user.id:
        raise HTTPException(status_code=404,detail="Запись не найдена")

    if item.status=="cancelled":
        raise HTTPException(status_code=409,detail="Запись уже отменена")

    item=cancel_appointment(db,item)

    return appointment_dict(item)
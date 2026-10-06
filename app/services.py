from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models import Appointment, Slot

def book_slot(db: Session,user_id: int,specialist_id: int,service_id: int,slot_id: int):
    slot=db.get(Slot,slot_id)
    if not slot:
        raise ValueError("Слот не найден")
    if not slot.is_available:
        raise ValueError("Слот уже занят")
    if slot.specialist_id!=specialist_id or slot.service_id!=service_id:
        raise ValueError("Параметры записи не соответствуют слоту")

    appointment=Appointment(
        user_id=user_id,
        specialist_id=specialist_id,
        service_id=service_id,
        slot_id=slot_id,
        status="booked"
    )
    slot.is_available=False
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment

def cancel_appointment(db: Session,appointment: Appointment):
    appointment.status="cancelled"
    appointment.cancelled_at=func.now()
    appointment.slot.is_available=True
    db.commit()
    db.refresh(appointment)
    return appointment

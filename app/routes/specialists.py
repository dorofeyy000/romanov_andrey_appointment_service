from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Service, Specialist, Slot
from app.schemas import ServiceOut, SlotOut, SpecialistOut
from app.auth import get_current_user

router=APIRouter()

@router.get("/specialists",response_model=list[SpecialistOut])
def specialists(db: Session=Depends(get_db),user=Depends(get_current_user)):
    return db.query(Specialist).order_by(Specialist.id).all()

@router.get("/services",response_model=list[ServiceOut])
def services(db: Session=Depends(get_db),user=Depends(get_current_user)):
    return db.query(Service).order_by(Service.id).all()

@router.get("/slots",response_model=list[SlotOut])
def slots(
    specialist_id: int|None=Query(default=None),
    service_id: int|None=Query(default=None),
    available: bool=True,
    limit: int=50,
    db: Session=Depends(get_db),
    user=Depends(get_current_user)
):
    query=db.query(Slot).filter(Slot.is_available==available)
    if specialist_id is not None:
        query=query.filter(Slot.specialist_id==specialist_id)
    if service_id is not None:
        query=query.filter(Slot.service_id==service_id)
    return query.order_by(Slot.start_at).limit(limit).all()

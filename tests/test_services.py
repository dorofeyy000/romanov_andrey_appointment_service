from datetime import datetime,timedelta
from app.models import Slot
from app.services import book_slot

def test_book_slot_rejects_occupied_slot(db_session):
    slot=Slot(
        specialist_id=1,
        service_id=1,
        start_at=datetime.now(),
        end_at=datetime.now()+timedelta(minutes=30),
        is_available=False
    )
    db_session.add(slot)
    db_session.commit()
    try:
        book_slot(db_session,1,1,1,slot.id)
        assert False
    except ValueError as exc:
        assert "занят" in str(exc)

def test_book_slot_creates_appointment(db_session):
    slot=Slot(
        specialist_id=1,
        service_id=1,
        start_at=datetime.now(),
        end_at=datetime.now()+timedelta(minutes=30),
        is_available=True
    )
    db_session.add(slot)
    db_session.commit()
    appointment=book_slot(db_session,1,1,1,slot.id)
    assert appointment.slot_id==slot.id
    assert appointment.status=="booked"

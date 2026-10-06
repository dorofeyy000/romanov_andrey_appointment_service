from datetime import datetime,timedelta
from app.models import Slot,Appointment
from app.services import book_slot,cancel_appointment

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

def test_book_slot_rejects_overlap(db_session):
    slot1=Slot(
        specialist_id=1,
        service_id=1,
        start_at=datetime(2026,1,1,10,0),
        end_at=datetime(2026,1,1,10,30),
        is_available=False
    )

    slot2=Slot(
        specialist_id=1,
        service_id=1,
        start_at=datetime(2026,1,1,10,15),
        end_at=datetime(2026,1,1,10,45),
        is_available=True
    )

    db_session.add_all([slot1,slot2])
    db_session.commit()

    db_session.add(
        Appointment(
            user_id=1,
            specialist_id=1,
            service_id=1,
            slot_id=slot1.id,
            status="booked"
        )
    )

    db_session.commit()

    try:
        book_slot(db_session,1,1,1,slot2.id)
        assert False
    except ValueError as exc:
        assert "пересекается" in str(exc)

def test_cancel_returns_slot_to_available(db_session):
    slot=Slot(
        specialist_id=1,
        service_id=1,
        start_at=datetime.now(),
        end_at=datetime.now()+timedelta(minutes=30),
        is_available=False
    )

    db_session.add(slot)
    db_session.commit()

    appointment=Appointment(
        user_id=1,
        specialist_id=1,
        service_id=1,
        slot_id=slot.id,
        status="booked"
    )

    db_session.add(appointment)
    db_session.commit()

    cancel_appointment(db_session,appointment)

    assert appointment.status=="cancelled"
    assert slot.is_available is True
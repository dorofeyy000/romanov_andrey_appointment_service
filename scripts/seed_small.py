from datetime import datetime,timedelta
from sqlalchemy import text
from app.database import SessionLocal
from app.models import User, Specialist, Service, Slot

db=SessionLocal()

try:
    db.execute(text("TRUNCATE TABLE appointments, slots, specialists, services RESTART IDENTITY CASCADE"))
    db.commit()

    user=db.query(User).filter(User.username=="demo").first()

    if not user:
        user=User(username="demo",password="demo")
        db.add(user)
        db.commit()

    specialists=[
        Specialist(
            full_name=f"Специалист {i}",
            specialty=f"Направление {i}"
        )
        for i in range(1,11)
    ]

    services=[
        Service(
            name=f"Услуга {i}",
            duration_minutes=30
        )
        for i in range(1,11)
    ]

    db.add_all(specialists)
    db.add_all(services)
    db.commit()

    specialists=db.query(Specialist).order_by(Specialist.id).all()
    services=db.query(Service).order_by(Service.id).all()

    start=datetime(2026,1,1,9,0,0)

    slots=[]

    for i in range(500):
        specialist=specialists[i%len(specialists)]
        service=services[i%len(services)]
        slot_start=start+timedelta(minutes=30*i)

        slots.append(
            Slot(
                specialist_id=specialist.id,
                service_id=service.id,
                start_at=slot_start,
                end_at=slot_start+timedelta(minutes=service.duration_minutes),
                is_available=True
            )
        )

    db.add_all(slots)
    db.commit()

    print(f"Users: {db.query(User).count()}")
    print(f"Specialists: {db.query(Specialist).count()}")
    print(f"Services: {db.query(Service).count()}")
    print(f"Slots: {db.query(Slot).count()}")
    print("Small dataset created successfully")

finally:
    db.close()
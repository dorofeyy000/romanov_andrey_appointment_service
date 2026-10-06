from datetime import datetime,timedelta
from sqlalchemy import text
from app.database import SessionLocal
from app.models import User, Specialist, Service, Slot, Appointment

TARGET_SPECIALISTS=200
TARGET_SERVICES=30
TARGET_SLOTS=200000
TARGET_APPOINTMENTS=50000
CANCELLED_APPOINTMENTS=5000

db=SessionLocal()

try:
    db.execute(text("TRUNCATE TABLE appointments, slots RESTART IDENTITY CASCADE"))
    db.commit()

    if db.query(User).count()==0:
        db.add(User(username="demo",password="demo"))
        db.commit()

    while db.query(Specialist).count()<TARGET_SPECIALISTS:
        current=db.query(Specialist).count()
        batch=[]
        for i in range(current+1,TARGET_SPECIALISTS+1):
            batch.append({
                "full_name":f"Специалист {i}",
                "specialty":f"Направление {(i-1)%10+1}"
            })
        db.bulk_insert_mappings(Specialist,batch)
        db.commit()

    while db.query(Service).count()<TARGET_SERVICES:
        current=db.query(Service).count()
        batch=[]
        for i in range(current+1,TARGET_SERVICES+1):
            batch.append({
                "name":f"Услуга {i}",
                "duration_minutes":30
            })
        db.bulk_insert_mappings(Service,batch)
        db.commit()

    specialists=db.query(Specialist).order_by(Specialist.id).all()
    services=db.query(Service).order_by(Service.id).all()

    start=datetime(2026,1,1,9,0,0)

    for offset in range(0,TARGET_SLOTS,5000):
        end=min(offset+5000,TARGET_SLOTS)
        batch=[]

        for i in range(offset,end):
            specialist=specialists[i%len(specialists)]
            service=services[i%len(services)]
            slot_start=start+timedelta(minutes=30*i)

            batch.append({
                "specialist_id":specialist.id,
                "service_id":service.id,
                "start_at":slot_start,
                "end_at":slot_start+timedelta(minutes=service.duration_minutes),
                "is_available":i>=TARGET_APPOINTMENTS or i<CANCELLED_APPOINTMENTS
            })

        db.bulk_insert_mappings(Slot,batch)
        db.commit()

    appointment_batch=[]

    for i in range(TARGET_APPOINTMENTS):
        appointment_batch.append({
            "user_id":1,
            "specialist_id":specialists[i%len(specialists)].id,
            "service_id":services[i%len(services)].id,
            "slot_id":i+1,
            "status":"cancelled" if i<CANCELLED_APPOINTMENTS else "booked"
        })

        if len(appointment_batch)>=5000:
            db.bulk_insert_mappings(Appointment,appointment_batch)
            db.commit()
            appointment_batch.clear()

    if appointment_batch:
        db.bulk_insert_mappings(Appointment,appointment_batch)
        db.commit()

    print(f"Specialists: {db.query(Specialist).count()}")
    print(f"Services: {db.query(Service).count()}")
    print(f"Slots: {db.query(Slot).count()}")
    print(f"Appointments: {db.query(Appointment).count()}")
    print(f"Cancelled appointments: {db.query(Appointment).filter(Appointment.status=='cancelled').count()}")
    print("Working dataset created successfully")

finally:
    db.close()
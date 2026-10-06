from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__="users"

    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    username: Mapped[str]=mapped_column(String(100),unique=True,index=False)
    password: Mapped[str]=mapped_column(String(255))
    is_active: Mapped[bool]=mapped_column(Boolean,default=True)

class Specialist(Base):
    __tablename__="specialists"

    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    full_name: Mapped[str]=mapped_column(String(200))
    specialty: Mapped[str]=mapped_column(String(200))

    slots=relationship("Slot",back_populates="specialist")
    appointments=relationship("Appointment",back_populates="specialist")

class Service(Base):
    __tablename__="services"

    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    name: Mapped[str]=mapped_column(String(200))
    duration_minutes: Mapped[int]=mapped_column(Integer)

    slots=relationship("Slot",back_populates="service")
    appointments=relationship("Appointment",back_populates="service")

class Slot(Base):
    __tablename__="slots"

    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    specialist_id: Mapped[int]=mapped_column(ForeignKey("specialists.id"))
    service_id: Mapped[int]=mapped_column(ForeignKey("services.id"))
    start_at: Mapped[datetime]=mapped_column(DateTime)
    end_at: Mapped[datetime]=mapped_column(DateTime)
    is_available: Mapped[bool]=mapped_column(Boolean,default=True)

    specialist=relationship("Specialist",back_populates="slots")
    service=relationship("Service",back_populates="slots")
    appointment=relationship("Appointment",back_populates="slot",uselist=False)

class Appointment(Base):
    __tablename__="appointments"

    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id"))
    specialist_id: Mapped[int]=mapped_column(ForeignKey("specialists.id"))
    service_id: Mapped[int]=mapped_column(ForeignKey("services.id"))
    slot_id: Mapped[int]=mapped_column(ForeignKey("slots.id"),unique=True)
    status: Mapped[str]=mapped_column(String(30),default="booked")
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    cancelled_at: Mapped[datetime|None]=mapped_column(DateTime,nullable=True)

    user=relationship("User")
    specialist=relationship("Specialist",back_populates="appointments")
    service=relationship("Service",back_populates="appointments")
    slot=relationship("Slot",back_populates="appointment")

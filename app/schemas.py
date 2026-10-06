from datetime import datetime
from pydantic import BaseModel, ConfigDict

class LoginRequest(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: int
    username: str

class SpecialistOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: int
    full_name: str
    specialty: str

class ServiceOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: int
    name: str
    duration_minutes: int

class SlotOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: int
    specialist_id: int
    service_id: int
    start_at: datetime
    end_at: datetime
    is_available: bool

class AppointmentCreate(BaseModel):
    specialist_id: int
    service_id: int
    slot_id: int

class AppointmentOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: int
    user_id: int
    specialist_id: int
    service_id: int
    slot_id: int
    status: str
    created_at: datetime
    cancelled_at: datetime|None

class AppointmentPage(BaseModel):
    items: list[AppointmentOut]
    total: int

class SummaryOut(BaseModel):
    total_appointments: int
    booked_appointments: int
    cancelled_appointments: int
    cancellation_share: float
    specialist_load: list[dict]

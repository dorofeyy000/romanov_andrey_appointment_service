import statistics
import time
import requests

from app.database import SessionLocal
from app.models import Slot, Appointment

BASE_URL="http://127.0.0.1:8000"

session=requests.Session()

WARMUP=5
REPEATS=20


def percentile(values,p):
    values=sorted(values)
    index=(len(values)-1)*p
    lower=int(index)
    upper=min(lower+1,len(values)-1)
    weight=index-lower

    return values[lower]+(values[upper]-values[lower])*weight


def check(response,name):
    if response.status_code>=400:
        raise RuntimeError(
            f"{name}: HTTP {response.status_code}: {response.text}"
        )


def login():
    response=session.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username":"demo",
            "password":"demo"
        }
    )

    check(response,"POST /api/auth/login")


def get_all_appointments():
    result=[]
    page=1

    while True:
        response=session.get(
            f"{BASE_URL}/api/appointments?page={page}&size=100"
        )

        check(response,"GET /api/appointments")

        data=response.json()
        items=data.get("items",[])
        total=data.get("total",0)

        result.extend(items)

        if len(result)>=total:
            break

        page+=1

    return result


def get_free_slots():
    db=SessionLocal()

    try:
        required=WARMUP+REPEATS+WARMUP+REPEATS

        slots=(
            db.query(Slot)
            .outerjoin(
                Appointment,
                Appointment.slot_id==Slot.id
            )
            .filter(
                Slot.is_available==True,
                Appointment.id==None
            )
            .order_by(Slot.id)
            .limit(required)
            .all()
        )

        if len(slots)<required:
            raise RuntimeError(
                f"Недостаточно реально свободных слотов: "
                f"{len(slots)}, требуется {required}"
            )

        return [
            {
                "id":slot.id,
                "specialist_id":slot.specialist_id,
                "service_id":slot.service_id
            }
            for slot in slots
        ]

    finally:
        db.close()


def get_first_appointment():
    appointments=get_all_appointments()

    if not appointments:
        raise RuntimeError(
            "Не найдена существующая запись для GET detail"
        )

    return appointments[0]["id"]


def measure(name,method,url,**kwargs):
    for _ in range(WARMUP):
        response=session.request(
            method,
            url,
            **kwargs
        )

        check(response,name)

    values=[]

    for _ in range(REPEATS):
        start=time.perf_counter()

        response=session.request(
            method,
            url,
            **kwargs
        )

        elapsed=(time.perf_counter()-start)*1000

        check(response,name)

        values.append(elapsed)

    p50=statistics.median(values)
    p95=percentile(values,0.95)
    maximum=max(values)

    print(
        f"{name}: "
        f"p50={p50:.2f} ms | "
        f"p95={p95:.2f} ms | "
        f"max={maximum:.2f} ms"
    )


def create_appointment(slot):
    response=session.post(
        f"{BASE_URL}/api/appointments",
        json={
            "specialist_id":slot["specialist_id"],
            "service_id":slot["service_id"],
            "slot_id":slot["id"]
        }
    )

    check(
        response,
        "POST /api/appointments"
    )

    return response.json()["id"]


def cancel_appointment(appointment_id):
    response=session.post(
        f"{BASE_URL}/api/appointments/{appointment_id}/cancel"
    )

    check(
        response,
        "POST /api/appointments/{appointment_id}/cancel"
    )


login()

slots=get_free_slots()

appointment_id=get_first_appointment()

measure(
    "POST /api/auth/login",
    "POST",
    f"{BASE_URL}/api/auth/login",
    json={
        "username":"demo",
        "password":"demo"
    }
)

measure(
    "POST /api/auth/logout",
    "POST",
    f"{BASE_URL}/api/auth/logout"
)

login()

measure(
    "GET /api/specialists",
    "GET",
    f"{BASE_URL}/api/specialists"
)

measure(
    "GET /api/services",
    "GET",
    f"{BASE_URL}/api/services"
)

measure(
    "GET /api/slots",
    "GET",
    f"{BASE_URL}/api/slots?available=true&limit=20"
)

measure(
    "GET /api/appointments",
    "GET",
    f"{BASE_URL}/api/appointments?page=1&size=20"
)

measure(
    "GET /api/appointments/{appointment_id}",
    "GET",
    f"{BASE_URL}/api/appointments/{appointment_id}"
)

measure(
    "GET /api/summary",
    "GET",
    f"{BASE_URL}/api/summary"
)

create_warmup_slots=slots[:WARMUP]

create_measure_slots=slots[
    WARMUP:
    WARMUP+REPEATS
]

cancel_warmup_slots=slots[
    WARMUP+REPEATS:
    WARMUP+REPEATS+WARMUP
]

cancel_measure_slots=slots[
    WARMUP+REPEATS+WARMUP:
    WARMUP+REPEATS+WARMUP+REPEATS
]


for slot in create_warmup_slots:
    appointment_id=create_appointment(slot)
    cancel_appointment(appointment_id)


create_values=[]

for slot in create_measure_slots:
    start=time.perf_counter()

    appointment_id=create_appointment(slot)

    elapsed=(time.perf_counter()-start)*1000

    create_values.append(elapsed)

    cancel_appointment(appointment_id)


for slot in cancel_warmup_slots:
    appointment_id=create_appointment(slot)

    cancel_appointment(appointment_id)


cancel_ids=[]

for slot in cancel_measure_slots:
    appointment_id=create_appointment(slot)
    cancel_ids.append(appointment_id)


cancel_values=[]

for appointment_id in cancel_ids:
    start=time.perf_counter()

    response=session.post(
        f"{BASE_URL}/api/appointments/{appointment_id}/cancel"
    )

    elapsed=(time.perf_counter()-start)*1000

    check(
        response,
        "POST /api/appointments/{appointment_id}/cancel"
    )

    cancel_values.append(elapsed)


print(
    f"POST /api/appointments: "
    f"p50={statistics.median(create_values):.2f} ms | "
    f"p95={percentile(create_values,0.95):.2f} ms | "
    f"max={max(create_values):.2f} ms"
)

print(
    f"POST /api/appointments/{{appointment_id}}/cancel: "
    f"p50={statistics.median(cancel_values):.2f} ms | "
    f"p95={percentile(cancel_values,0.95):.2f} ms | "
    f"max={max(cancel_values):.2f} ms"
)

print("Замер завершён.")
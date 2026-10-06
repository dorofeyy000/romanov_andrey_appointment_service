import statistics
import time
import requests

BASE_URL="http://127.0.0.1:8000"
LOGIN_URL=f"{BASE_URL}/api/auth/login"

session=requests.Session()

def percentile(values,p):
    values=sorted(values)
    index=(len(values)-1)*p
    lower=int(index)
    upper=min(lower+1,len(values)-1)
    weight=index-lower
    return values[lower]+(values[upper]-values[lower])*weight

def measure(name,method,url,**kwargs):
    warmup=5
    repeats=20

    for _ in range(warmup):
        session.request(method,url,**kwargs)

    values=[]

    for _ in range(repeats):
        start=time.perf_counter()
        response=session.request(method,url,**kwargs)
        elapsed=(time.perf_counter()-start)*1000

        if response.status_code>=400:
            raise RuntimeError(
                f"{name}: HTTP {response.status_code}: {response.text}"
            )

        values.append(elapsed)

    p50=statistics.median(values)
    p95=percentile(values,0.95)
    maximum=max(values)

    print(
        f"{name}: p50={p50:.2f} ms | "
        f"p95={p95:.2f} ms | "
        f"max={maximum:.2f} ms"
    )

login_response=session.post(
    LOGIN_URL,
    json={
        "username":"demo",
        "password":"demo"
    }
)

if login_response.status_code!=200:
    raise RuntimeError(
        f"Login error: {login_response.status_code} {login_response.text}"
    )

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
    "GET /api/summary",
    "GET",
    f"{BASE_URL}/api/summary"
)
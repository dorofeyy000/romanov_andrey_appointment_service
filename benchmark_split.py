import statistics
import requests
import time

BASE_URL="http://127.0.0.1:8000"

session=requests.Session()

session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username":"demo","password":"demo"}
)

operations=[
    ("GET /api/slots",f"{BASE_URL}/api/slots?available=true&limit=20"),
    ("GET /api/appointments",f"{BASE_URL}/api/appointments?page=1&size=20"),
    ("GET /api/summary",f"{BASE_URL}/api/summary")
]

def percentile(values,p):
    values=sorted(values)
    index=(len(values)-1)*p
    low=int(index)
    high=min(low+1,len(values)-1)
    weight=index-low
    return values[low]+(values[high]-values[low])*weight

for name,url in operations:
    for _ in range(5):
        session.get(url)

    response_times=[]
    db_times=[]
    code_times=[]
    query_counts=[]

    for _ in range(20):
        start=time.perf_counter()
        response=session.get(url)
        total=(time.perf_counter()-start)*1000

        db_time=float(response.headers.get("X-DB-Time-Ms","0"))
        queries=int(response.headers.get("X-DB-Queries","0"))
        code_time=max(0,total-db_time)

        response_times.append(total)
        db_times.append(db_time)
        code_times.append(code_time)
        query_counts.append(queries)

    print(
        f"{name}: "
        f"operation={statistics.median(response_times):.2f} ms | "
        f"db={statistics.median(db_times):.2f} ms | "
        f"code={statistics.median(code_times):.2f} ms | "
        f"queries={statistics.median(query_counts):.0f}"
    )